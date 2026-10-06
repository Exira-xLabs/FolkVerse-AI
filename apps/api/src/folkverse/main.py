import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from starlette.middleware.base import RequestResponseEndpoint

from folkverse.config import Settings
from folkverse.content_api import router as content_router
from folkverse.contracts import (
    ErrorDetail,
    ErrorEnvelope,
    HealthResponse,
    SessionDeleted,
    SessionResponse,
)
from folkverse.database import AnonymousSession, make_engine
from folkverse.errors import ApiError
from folkverse.gateway_limits import UsageLedger
from folkverse.guide_api import GuideRequestLimits
from folkverse.guide_api import router as guide_router
from folkverse.guide_embeddings import LocalBGEEncoder
from folkverse.guide_harness import GuideHarness
from folkverse.guide_hybrid import HybridEvidenceRepository
from folkverse.provider_gateway import GuideGateway
from folkverse.sessions import COOKIE_NAME, SessionService

REVISION = "0003_gateway"


def error_response(
    request: Request, status: int, code: str, message: str, retryable: bool = False
) -> JSONResponse:
    body = ErrorEnvelope(
        error=ErrorDetail(code=code, message=message, retryable=retryable),
        request_id=getattr(request.state, "request_id", f"req_{uuid4().hex}"),
    )
    return JSONResponse(
        body.model_dump(),
        status_code=status,
        headers={"Cache-Control": "no-store", "X-Request-ID": body.request_id},
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = make_engine(settings)
    sessions = SessionService(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async def maintain() -> None:
            while True:
                await asyncio.sleep(60)
                pending = asyncio.create_task(asyncio.to_thread(app.state.guide_ledger.prune))
                try:
                    await asyncio.shield(pending)
                    app.state.guide_maintenance = "ok"
                except asyncio.CancelledError:
                    try:
                        await pending
                    except (SQLAlchemyError, ApiError):
                        pass
                    raise
                except (SQLAlchemyError, ApiError):
                    app.state.guide_maintenance = "unavailable"

        maintenance = asyncio.create_task(maintain())
        try:
            yield
        finally:
            maintenance.cancel()
            try:
                await maintenance
            except asyncio.CancelledError:
                pass
            engine.dispose()

    app = FastAPI(title="FolkVerse API", version="0.1.0", lifespan=lifespan)
    app.include_router(content_router)
    app.include_router(guide_router)
    app.state.engine = engine
    app.state.settings = settings
    app.state.guide_ledger = UsageLedger(engine, settings)
    app.state.guide_gateway = GuideGateway(settings, app.state.guide_ledger)
    app.state.guide_request_limits = GuideRequestLimits(
        settings.session_secret.get_secret_value(),
        settings.model_rate_limit_per_minute,
        settings.model_global_rate_limit_per_minute,
    )
    app.state.guide_harness = GuideHarness(
        HybridEvidenceRepository(
            engine,
            LocalBGEEncoder(settings.embedding_model_dir),
            settings.embedding_index_path,
            settings.embedding_enabled,
            settings.embedding_query_timeout_seconds,
            settings.embedding_min_cosine,
        ),
        app.state.guide_gateway,
        settings.session_secret.get_secret_value(),
        timeout_seconds=settings.model_timeout_seconds + 10,
        max_output_tokens=settings.model_max_output_tokens,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "PATCH"],
        allow_headers=["Content-Type"],
    )

    @app.middleware("http")
    async def boundary(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.guide_started_at = time.monotonic()
        request.state.request_id = f"req_{uuid4().hex}"
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("origin") not in settings.allowed_origins:
                return error_response(
                    request, 403, "origin_denied", "Request origin is not allowed."
                )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(ApiError)
    async def api_error(request: Request, exc: ApiError) -> JSONResponse:
        return error_response(request, exc.status, exc.code, exc.message, exc.retryable)

    @app.exception_handler(SQLAlchemyError)
    async def db_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return error_response(
            request,
            503,
            "database_unavailable",
            "The museum service is temporarily unavailable.",
            True,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(
            request, 422, "invalid_input", "The request did not match the schema."
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(
            request, exc.status_code, "request_failed", "The request could not be completed."
        )

    @app.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception) -> JSONResponse:
        return error_response(
            request, 500, "internal_error", "The museum service encountered an error."
        )

    errors: dict[int | str, dict[str, Any]] = {503: {"model": HealthResponse | ErrorEnvelope}}

    @app.get("/health", response_model=HealthResponse, responses=errors, operation_id="root_health")
    @app.get(
        "/api/v1/health", response_model=HealthResponse, responses=errors, operation_id="health"
    )
    def health(response: Response) -> HealthResponse:
        result = HealthResponse(
            status="degraded",
            mode=settings.app_mode,
            database="unavailable",
            pgvector="unavailable",
            schema_status="unavailable",
        )
        try:
            with engine.connect() as connection:
                result.postgres_version = str(
                    connection.execute(text("SHOW server_version")).scalar()
                )
                result.database = "available"
                vector = connection.execute(
                    text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                ).scalar()
                if vector:
                    result.pgvector = "available"
                    result.pgvector_version = str(vector)
                has_schema = connection.execute(
                    text("SELECT to_regclass('public.alembic_version')")
                ).scalar()
                if (
                    has_schema
                    and connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
                    == REVISION
                ):
                    result.schema_status = "current"
        except SQLAlchemyError:
            pass
        if (
            result.database == "available"
            and result.pgvector == "available"
            and result.schema_status == "current"
        ):
            result.status = "ok"
        else:
            response.status_code = 503
        return result

    session_errors: dict[int | str, dict[str, Any]] = {
        code: {"model": ErrorEnvelope} for code in (401, 403, 422, 503)
    }

    def session_response(session: AnonymousSession) -> SessionResponse:
        return SessionResponse(session_id=session.id, expires_at=session.expires_at)

    @app.post(
        "/api/v1/session",
        response_model=SessionResponse,
        responses=session_errors,
        operation_id="start_session",
    )
    def start_session(request: Request, response: Response) -> SessionResponse:
        with Session(engine) as db:
            try:
                session = sessions.require(request.cookies.get(COOKIE_NAME), db)
            except ApiError:
                session = sessions.create(db)
            response.set_cookie(
                COOKIE_NAME,
                sessions.encode(session.id),
                httponly=True,
                secure=settings.cookie_secure,
                samesite="lax",
                path="/",
                max_age=max(1, int((session.expires_at - datetime.now(UTC)).total_seconds())),
            )
            return session_response(session)

    @app.get(
        "/api/v1/session",
        response_model=SessionResponse,
        responses=session_errors,
        operation_id="get_session",
    )
    def get_session(request: Request) -> SessionResponse:
        with Session(engine) as db:
            return session_response(sessions.require(request.cookies.get(COOKIE_NAME), db))

    @app.delete(
        "/api/v1/session",
        response_model=SessionDeleted,
        responses=session_errors,
        operation_id="delete_session",
    )
    def delete_session(request: Request, response: Response) -> SessionDeleted:
        with Session(engine) as db:
            session = sessions.require(request.cookies.get(COOKIE_NAME), db)
            db.delete(session)
            db.commit()
        response.delete_cookie(
            COOKIE_NAME, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax"
        )
        return SessionDeleted()

    return app
