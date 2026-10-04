from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
    request_id: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    mode: Literal["demo", "live"]
    database: Literal["available", "unavailable"]
    pgvector: Literal["available", "unavailable"]
    schema_status: Literal["current", "unavailable"]
    postgres_version: str | None = None
    pgvector_version: str | None = None


class SessionResponse(BaseModel):
    session_id: str
    expires_at: datetime
    behavioral_opt_in: Literal[False] = False


class SessionDeleted(BaseModel):
    deleted: Literal[True] = True
