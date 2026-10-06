"""Serialize admission under a shared PostgreSQL lock; unknown bills retain reserves."""

import hashlib
import hmac
import time
from datetime import UTC, datetime
from decimal import ROUND_CEILING
from uuid import uuid4

from sqlalchemy import delete, func, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from folkverse.config import Settings
from folkverse.errors import ApiError
from folkverse.gateway_models import GatewayAttempt, GatewayBudget, GatewayLock


class UsageLedger:
    def __init__(self, engine: Engine, settings: Settings) -> None:
        self.engine, self.settings = engine, settings

    def _lock(self, db: Session) -> None:
        # SQLite is only a portable test substrate. BEGIN IMMEDIATE serializes its writers.
        if self.engine.dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))
        if db.scalar(select(GatewayLock).where(GatewayLock.id == 1).with_for_update()) is None:
            raise ApiError(503, "gateway_unavailable", "The guide limits are unavailable.", True)

    def reserve(self, actor_id: str, amount: int, now: float | None = None) -> str:
        now = time.time() if now is None else now
        day = datetime.fromtimestamp(now, UTC).date().isoformat()
        actor = hmac.new(
            self.settings.session_secret.get_secret_value().encode(),
            actor_id.encode(),
            hashlib.sha256,
        ).hexdigest()
        try:
            with Session(self.engine) as db, db.begin():
                self._lock(db)
                db.execute(
                    delete(GatewayAttempt).where(
                        GatewayAttempt.started_at < now - 7 * 86400,
                        GatewayAttempt.lease_until < now,
                    )
                )
                # Retain only short-lived pseudonyms for rate checking, not long-term identity.
                for old in db.scalars(
                    select(GatewayAttempt).where(
                        GatewayAttempt.started_at <= now - 60,
                        GatewayAttempt.actor_hash.is_not(None),
                    )
                ):
                    old.actor_hash = None
                active = (
                    db.scalar(
                        select(func.count())
                        .select_from(GatewayAttempt)
                        .where(
                            GatewayAttempt.status == "reserved",
                            GatewayAttempt.lease_until > now,
                        )
                    )
                    or 0
                )
                if active >= self.settings.model_max_concurrency:
                    raise ApiError(429, "guide_busy", "The guide is busy. Try again shortly.", True)
                recent = (
                    select(func.count())
                    .select_from(GatewayAttempt)
                    .where(GatewayAttempt.started_at > now - 60)
                )
                if (db.scalar(recent) or 0) >= self.settings.model_global_rate_limit_per_minute:
                    raise ApiError(
                        429, "rate_limited", "The guide request limit was reached.", True
                    )
                if (
                    db.scalar(recent.where(GatewayAttempt.actor_hash == actor)) or 0
                ) >= self.settings.model_rate_limit_per_minute:
                    raise ApiError(
                        429, "rate_limited", "The guide request limit was reached.", True
                    )
                budget = db.get(GatewayBudget, day)
                if budget is None:
                    budget = GatewayBudget(day=day, charged_nano_usd=0)
                    db.add(budget)
                cap = int(self.settings.daily_ai_budget_usd * 1_000_000_000)
                if self.settings.guide_provider == "ollama":
                    daily_count = (
                        db.scalar(
                            select(func.count())
                            .select_from(GatewayAttempt)
                            .where(GatewayAttempt.day == day)
                        )
                        or 0
                    )
                    if amount != 0 or daily_count >= self.settings.ollama_daily_request_limit:
                        raise ApiError(
                            429, "budget_exhausted", "The daily guide request cap was reached."
                        )
                elif amount <= 0 or budget.charged_nano_usd + amount > cap:
                    raise ApiError(429, "budget_exhausted", "The daily guide budget was reached.")
                budget.charged_nano_usd += amount
                identifier = f"call_{uuid4().hex}"
                db.add(
                    GatewayAttempt(
                        id=identifier,
                        day=day,
                        actor_hash=actor,
                        started_at=now,
                        lease_until=now + self.settings.model_timeout_seconds + 15,
                        model=self.settings.provider_model,
                        status="reserved",
                        charged_nano_usd=amount,
                    )
                )
                return identifier
        except SQLAlchemyError:
            raise ApiError(
                503, "gateway_unavailable", "The guide limits are unavailable.", True
            ) from None

    def finish(
        self,
        identifier: str,
        status: str,
        latency_ms: int,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
    ) -> None:
        try:
            with Session(self.engine) as db, db.begin():
                self._lock(db)
                attempt = db.get(GatewayAttempt, identifier)
                if attempt is None or attempt.status != "reserved":
                    return  # Idempotent reconciliation cannot refund twice.
                budget = db.get(GatewayBudget, attempt.day)
                assert budget is not None
                if prompt_tokens is not None and completion_tokens is not None:
                    actual = self.cost(prompt_tokens, completion_tokens)
                    budget.charged_nano_usd += actual - attempt.charged_nano_usd
                    attempt.charged_nano_usd = actual
                    attempt.prompt_tokens = prompt_tokens
                    attempt.completion_tokens = completion_tokens
                attempt.status, attempt.latency_ms = status, latency_ms
        except SQLAlchemyError:
            # The original committed reserve remains charged; never silently release it.
            raise ApiError(
                503, "gateway_unavailable", "The guide limits are unavailable.", True
            ) from None

    def cost(self, prompt: int, output: int) -> int:
        if self.settings.guide_provider == "ollama":
            return 0  # Subscription/account usage is counted, never assigned invented USD rates.
        incoming = self.settings.deepseek_input_usd_per_million
        outgoing = self.settings.deepseek_output_usd_per_million
        if incoming is None or outgoing is None:
            raise ApiError(503, "provider_unavailable", "Guide pricing is not configured.")
        return int(
            ((prompt * incoming + output * outgoing) * 1000).to_integral_value(
                rounding=ROUND_CEILING
            )
        )

    def prune(self, now: float | None = None) -> None:
        """Drop expired rate pseudonyms and detailed usage after seven days; keep totals."""
        now = time.time() if now is None else now
        with Session(self.engine) as db, db.begin():
            self._lock(db)
            for row in db.scalars(
                select(GatewayAttempt).where(GatewayAttempt.started_at <= now - 60)
            ):
                row.actor_hash = None
            db.execute(
                delete(GatewayAttempt).where(
                    GatewayAttempt.started_at < now - 7 * 86400,
                    GatewayAttempt.lease_until < now,
                )
            )
