"""Content-free persistent provider limits and usage accounting."""

from sqlalchemy import BigInteger, CheckConstraint, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from folkverse.database import Base


class GatewayLock(Base):
    __tablename__ = "gateway_lock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    __table_args__ = (CheckConstraint("id = 1"),)


class GatewayBudget(Base):
    __tablename__ = "gateway_budgets"
    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    charged_nano_usd: Mapped[int] = mapped_column(BigInteger, default=0)
    __table_args__ = (CheckConstraint("charged_nano_usd >= 0"),)


class GatewayAttempt(Base):
    __tablename__ = "gateway_attempts"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), index=True)
    actor_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    started_at: Mapped[float] = mapped_column(Float, index=True)
    lease_until: Mapped[float] = mapped_column(Float)
    model: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(24))
    charged_nano_usd: Mapped[int] = mapped_column(BigInteger)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
