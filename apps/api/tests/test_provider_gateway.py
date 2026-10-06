"""Mock HTTP transport and persistent portable ledger tests; no provider requests."""

import asyncio
import json
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from folkverse.config import Settings
from folkverse.database import Base
from folkverse.errors import ApiError
from folkverse.gateway_limits import UsageLedger
from folkverse.gateway_models import GatewayAttempt, GatewayBudget, GatewayLock
from folkverse.provider_gateway import DeepSeekGateway, ProviderMessage


def configuration(**changes: Any) -> Settings:
    options: dict[str, Any] = dict(
        _env_file=None,
        app_mode="live",
        database_url="postgresql+psycopg://test:test@localhost/test",
        session_secret="s" * 40,
        deepseek_api_key="SYNTHETIC_TEST_KEY",
        daily_ai_budget_usd="1",
        deepseek_price_model="deepseek-flash",
        deepseek_price_base_url="https://api.deepseek.com",
        deepseek_input_usd_per_million="0.3",
        deepseek_output_usd_per_million="1.2",
    )
    options.update(changes)
    return Settings(**options)


@pytest.fixture
def engine(tmp_path: Any) -> Iterator[Engine]:
    engine = create_engine(f"sqlite:///{tmp_path / 'usage.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(GatewayLock(id=1))
        db.commit()
    yield engine
    engine.dispose()


def messages() -> list[ProviderMessage]:
    return [
        ProviderMessage(role="system", content='Return JSON, for example {"text":"..."}.'),
        ProviderMessage(role="user", content="PRIVATE_TEST_QUESTION"),
    ]


def reply(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "model": "deepseek-flash",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": '{"text":"UNVALIDATED_TEST_REPLY"}',
                },
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }
    data.update(changes)
    return data


def complete(engine: Engine, handler: Any, **changes: Any) -> Any:
    settings = configuration(**changes)
    gateway = DeepSeekGateway(settings, UsageLedger(engine, settings), httpx.MockTransport(handler))
    return asyncio.run(gateway.complete(messages(), "synthetic-session"))


def attempts(engine: Engine) -> list[GatewayAttempt]:
    with Session(engine) as db:
        return list(db.scalars(select(GatewayAttempt).order_by(GatewayAttempt.started_at)))


def ollama_configuration(**changes: Any) -> Settings:
    options = dict(
        guide_provider="ollama",
        ollama_api_key="SYNTHETIC_OLLAMA_KEY",
        ollama_daily_request_limit=3,
        daily_ai_budget_usd="0",
    )
    options.update(changes)
    return configuration(**options)


def test_ollama_cloud_request_uses_its_key_endpoint_and_model(engine: Engine) -> None:
    settings = ollama_configuration()

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url == "https://ollama.com/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer SYNTHETIC_OLLAMA_KEY"
        assert body["model"] == "deepseek-v4.1-flash"
        assert body["reasoning_effort"] == "none" and "thinking" not in body
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(200, json=reply(model=settings.provider_model))

    gateway = DeepSeekGateway(settings, UsageLedger(engine, settings), httpx.MockTransport(handler))
    result = asyncio.run(gateway.complete(messages(), "visit"))
    assert result.model == settings.provider_model
    stored = attempts(engine)[0]
    assert stored.charged_nano_usd == 0 and stored.prompt_tokens == 20
    assert stored.model == settings.provider_model


@pytest.mark.parametrize(
    "changes",
    [
        {"ollama_api_key": None},
        {"ollama_daily_request_limit": 0},
        {"app_mode": "demo"},
    ],
)
def test_ollama_missing_key_cap_or_live_mode_cannot_call(engine: Engine, changes: Any) -> None:
    settings = ollama_configuration(**changes)

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("Disabled provider must not receive a request")

    gateway = DeepSeekGateway(settings, UsageLedger(engine, settings), httpx.MockTransport(handler))
    with pytest.raises(ApiError, match="provider_unavailable"):
        asyncio.run(gateway.complete(messages(), "visit"))
    assert not attempts(engine)


def test_ollama_daily_cap_is_shared_and_counts_failed_attempts(engine: Engine) -> None:
    settings = ollama_configuration()
    ledger = UsageLedger(engine, settings)
    for i in range(3):
        attempt = ledger.reserve(f"visit-{i}", 0, now=1000 + i)
        ledger.finish(attempt, "failed", 1)
    another_worker = UsageLedger(engine, settings)
    with pytest.raises(ApiError) as error:
        another_worker.reserve("other-visit", 0, now=1004)
    assert error.value.code == "budget_exhausted"
    assert another_worker.reserve("other-visit", 0, now=87400)


@pytest.mark.parametrize(
    "base",
    [
        "https://api.deepseek.com",
        "http://ollama.com/v1",
        "https://ollama.com.evil.example/v1",
        "https://ollama.com/v1?secret=1",
    ],
)
def test_ollama_key_cannot_be_routed_to_a_different_provider(base: str) -> None:
    with pytest.raises(ValueError):
        ollama_configuration(ollama_base_url=base)


def test_request_contract_usage_and_no_private_content_in_ledger(engine: Engine) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url == "https://api.deepseek.com/chat/completions"
        assert request.headers["authorization"] == "Bearer SYNTHETIC_TEST_KEY"
        assert body["thinking"] == {"type": "disabled"}
        assert body["response_format"] == {"type": "json_object"}
        assert body["stream"] is False
        assert body["max_tokens"] == 800
        assert "tools" not in body and "user_id" not in body
        return httpx.Response(200, json=reply())

    result = complete(engine, handler)
    assert result.payload == {"text": "UNVALIDATED_TEST_REPLY"}
    assert "UNVALIDATED_TEST_REPLY" not in repr(result)
    row = attempts(engine)[0]
    assert row.status == "completed" and row.prompt_tokens == 20
    assert row.charged_nano_usd == 18000
    assert row.actor_hash != "synthetic-session"
    with engine.connect() as connection:
        assert "PRIVATE_TEST_QUESTION" not in str(
            connection.exec_driver_sql("SELECT * FROM gateway_attempts").all()
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"app_mode": "demo"},
        {"deepseek_api_key": None},
        {"daily_ai_budget_usd": "0"},
        {"deepseek_price_model": "unknown"},
        {"deepseek_price_base_url": "https://other.example"},
        {"deepseek_input_usd_per_million": None},
        {"deepseek_output_usd_per_million": None},
    ],
)
def test_unconfigured_calls_never_reach_transport(engine: Engine, changes: dict[str, Any]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("Unconfigured call reached provider")

    with pytest.raises(ApiError) as error:
        complete(engine, handler, **changes)
    assert error.value.code == "provider_unavailable"
    assert not attempts(engine)


@pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
def test_one_retry_and_two_separate_reserves(engine: Engine, code: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(code, text="SECRET_PROVIDER_INTERNALS")

    with pytest.raises(ApiError) as error:
        complete(engine, handler)
    assert calls == 2
    assert "SECRET_PROVIDER_INTERNALS" not in str(error.value)
    assert len(attempts(engine)) == 2
    assert all(r.charged_nano_usd == 8160000 for r in attempts(engine))


@pytest.mark.parametrize("code", [400, 401, 402, 403, 422, 301])
def test_permanent_failure_is_not_retried(engine: Engine, code: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            code,
            text="SECRET_PROVIDER_INTERNALS",
            headers={"location": "https://untrusted.example"},
        )

    with pytest.raises(ApiError):
        complete(engine, handler)
    assert calls == 1


def test_retry_can_succeed_and_keeps_uncertain_first_charge(engine: Engine) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("SYNTHETIC_TEST_KEY", request=request)
        return httpx.Response(200, json=reply())

    assert complete(engine, handler).payload
    assert [r.status for r in attempts(engine)] == ["failed", "completed"]
    assert attempts(engine)[0].charged_nano_usd == 8160000


@pytest.mark.parametrize("content", ["", "{}", "[]", "not json", '{"text":'])
def test_invalid_output_is_rejected_without_retry(engine: Engine, content: str) -> None:
    data = reply()
    data["choices"][0]["message"]["content"] = content
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(200, json=data))
    assert len(attempts(engine)) == 1
    assert attempts(engine)[0].status == "failed"
    assert attempts(engine)[0].charged_nano_usd == 18000  # Valid usage still reconciles.


@pytest.mark.parametrize("reason", ["length", "tool_calls", "content_filter", "aborted"])
def test_incomplete_or_tool_reply_is_rejected(engine: Engine, reason: str) -> None:
    data = reply()
    data["choices"][0]["finish_reason"] = reason
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(200, json=data))


@pytest.mark.parametrize(
    "usage",
    [
        None,
        {},
        {"prompt_tokens": -1},
        {"prompt_tokens": True, "completion_tokens": 1, "total_tokens": 2},
        {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 99},
    ],
)
def test_invalid_usage_never_refunds_reserve(engine: Engine, usage: Any) -> None:
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(200, json=reply(usage=usage)))
    assert attempts(engine)[0].charged_nano_usd == 8160000


def test_budget_persists_across_gateway_instances_and_blocks_retry(engine: Engine) -> None:
    settings = configuration(daily_ai_budget_usd="0.01")
    ledger = UsageLedger(engine, settings)
    ledger.reserve("first", 8160000)
    with pytest.raises(ApiError) as error:
        UsageLedger(engine, settings).reserve("second", 8160000)
    assert error.value.code == "budget_exhausted"
    assert len(attempts(engine)) == 1


def test_reconciliation_is_idempotent(engine: Engine) -> None:
    ledger = UsageLedger(engine, configuration())
    identifier = ledger.reserve("first", 8160000)
    ledger.finish(identifier, "completed", 1, 20, 10)
    ledger.finish(identifier, "completed", 1, 20, 10)
    with Session(engine) as db:
        assert db.scalar(select(GatewayBudget.charged_nano_usd)) == 18000


def test_rate_and_global_concurrency_limits(engine: Engine) -> None:
    settings = configuration(model_max_concurrency=1, model_rate_limit_per_minute=1)
    ledger = UsageLedger(engine, settings)
    identifier = ledger.reserve("first", 100, now=1000)
    with pytest.raises(ApiError) as error:
        ledger.reserve("second", 100, now=1001)
    assert error.value.code == "guide_busy"
    ledger.finish(identifier, "failed", 0)
    with pytest.raises(ApiError) as error:
        ledger.reserve("first", 100, now=1001)
    assert error.value.code == "rate_limited"
    assert ledger.reserve("first", 100, now=1061)


def test_expired_crash_lease_releases_slot_but_not_charge(engine: Engine) -> None:
    ledger = UsageLedger(engine, configuration(model_max_concurrency=1))
    ledger.reserve("first", 100, now=1000)
    ledger.reserve("second", 100, now=1046)
    with Session(engine) as db:
        assert db.scalar(select(GatewayBudget.charged_nano_usd)) == 200


def test_utc_day_rollover_keeps_previous_charge(engine: Engine) -> None:
    ledger = UsageLedger(engine, configuration(daily_ai_budget_usd="0.0000001"))
    first = ledger.reserve("first", 100, now=86399)
    ledger.finish(first, "failed", 0)
    assert ledger.reserve("second", 100, now=86401)
    with Session(engine) as db:
        assert list(db.scalars(select(GatewayBudget.charged_nano_usd))) == [100, 100]


def test_cancellation_releases_slot_and_keeps_unknown_bill(engine: Engine) -> None:
    async def scenario() -> None:
        started = asyncio.Event()

        async def handler(request: httpx.Request) -> httpx.Response:
            started.set()
            await asyncio.Future()
            raise AssertionError("unreachable")

        settings = configuration(model_max_concurrency=1)
        gateway = DeepSeekGateway(
            settings, UsageLedger(engine, settings), httpx.MockTransport(handler)
        )
        task = asyncio.create_task(gateway.complete(messages(), "first"))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert attempts(engine)[0].status == "cancelled"
        assert attempts(engine)[0].charged_nano_usd == 8160000
        UsageLedger(engine, settings).reserve("second", 100)

    asyncio.run(scenario())


def test_total_deadline_handles_provider_that_never_finishes(engine: Engine) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.Future()
        raise AssertionError("unreachable")

    with pytest.raises(ApiError) as error:
        complete(engine, handler, model_timeout_seconds=0.1)
    assert error.value.code == "provider_timeout"
    assert attempts(engine)[0].status == "cancelled"


def test_large_context_is_rejected_before_admission(engine: Engine) -> None:
    settings = configuration(model_max_input_tokens=512)
    gateway = DeepSeekGateway(settings, UsageLedger(engine, settings))
    with pytest.raises(ApiError) as error:
        asyncio.run(gateway.complete(messages(), "first"))
    assert error.value.code == "context_too_large"
    assert not attempts(engine)


def test_oversized_provider_body_is_rejected(engine: Engine) -> None:
    with pytest.raises(ApiError):
        complete(
            engine,
            lambda _: httpx.Response(
                200,
                content=b" " * 131073,
                headers={"content-type": "application/json"},
            ),
        )
    assert attempts(engine)[0].charged_nano_usd == 8160000


def test_pruning_preserves_totals_and_removes_expired_identity(engine: Engine) -> None:
    ledger = UsageLedger(engine, configuration())
    identifier = ledger.reserve("first", 100, now=1000)
    ledger.finish(identifier, "failed", 0)
    ledger.prune(now=1061)
    assert attempts(engine)[0].actor_hash is None
    ledger.prune(now=1000 + 8 * 86400)
    assert not attempts(engine)
    with Session(engine) as db:
        assert db.scalar(select(GatewayBudget.charged_nano_usd)) == 100


def test_pricing_cost_uses_decimal_upward_rounding(engine: Engine) -> None:
    assert UsageLedger(engine, configuration()).cost(1, 1) == 1500
    assert configuration().daily_ai_budget_usd == Decimal("1")


def test_parallel_admission_cannot_overspend(engine: Engine) -> None:
    from concurrent.futures import ThreadPoolExecutor

    settings = configuration(daily_ai_budget_usd="0.01", model_max_concurrency=20)

    def admit(number: int) -> str:
        try:
            UsageLedger(engine, settings).reserve(str(number), 8160000)
            return "admitted"
        except ApiError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=6) as workers:
        outcomes = list(workers.map(admit, range(6)))
    assert outcomes.count("admitted") == 1
    assert outcomes.count("budget_exhausted") == 5
    assert len(attempts(engine)) == 1


def test_parallel_admission_enforces_shared_concurrency(engine: Engine) -> None:
    from concurrent.futures import ThreadPoolExecutor

    settings = configuration(model_max_concurrency=2)

    def admit(number: int) -> str:
        try:
            UsageLedger(engine, settings).reserve(str(number), 100)
            return "admitted"
        except ApiError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=6) as workers:
        outcomes = list(workers.map(admit, range(6)))
    assert outcomes.count("admitted") == 2
    assert outcomes.count("guide_busy") == 4


def test_global_rate_limit_is_shared_across_actors(engine: Engine) -> None:
    ledger = UsageLedger(engine, configuration(model_global_rate_limit_per_minute=1))
    identifier = ledger.reserve("first", 100, now=1000)
    ledger.finish(identifier, "completed", 0)
    with pytest.raises(ApiError) as error:
        ledger.reserve("other", 100, now=1001)
    assert error.value.code == "rate_limited"


@pytest.mark.parametrize(
    "url",
    [
        "http://api.deepseek.com",
        "https://key@api.deepseek.com",
        "https://api.deepseek.com?key=x",
        "https://api.deepseek.com/arbitrary",
        "https://api.deepseek.com#fragment",
    ],
)
def test_invalid_provider_url_is_rejected(url: str) -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        configuration(deepseek_base_url=url)


@pytest.mark.parametrize("content", ['{"n":NaN}', '{"n":Infinity}', '{"a":1,"a":2}'])
def test_nonstandard_or_ambiguous_json_is_rejected(engine: Engine, content: str) -> None:
    data = reply()
    data["choices"][0]["message"]["content"] = content
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(200, json=data))


def test_missing_mode_defaults_to_live_and_glm_stays_off(monkeypatch: Any) -> None:
    monkeypatch.delenv("APP_MODE", raising=False)
    monkeypatch.delenv("GLM_ENABLED", raising=False)
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://test@localhost/test",
        session_secret="s" * 40,
    )
    assert settings.app_mode == "live" and settings.glm_enabled is False
    assert settings.deepseek_api_key is None
    assert settings.daily_ai_budget_usd == 0


def test_unavailable_ledger_never_calls_provider(engine: Engine) -> None:
    with Session(engine) as db:
        lock = db.get(GatewayLock, 1)
        assert lock is not None
        db.delete(lock)
        db.commit()

    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("Unavailable limits allowed a provider call")

    with pytest.raises(ApiError) as error:
        complete(engine, handler)
    assert error.value.code == "gateway_unavailable"


def test_usage_exceeding_reserve_is_recorded_and_output_rejected(engine: Engine) -> None:
    data = reply(usage={"prompt_tokens": 24001, "completion_tokens": 1, "total_tokens": 24002})
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(200, json=data))
    assert attempts(engine)[0].prompt_tokens == 24001
    assert attempts(engine)[0].status == "failed"


def test_retry_after_prevents_immediate_retry(engine: Engine) -> None:
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(429, headers={"retry-after": "60"}))
    assert len(attempts(engine)) == 1


def test_nonempty_answer_with_zero_usage_cannot_erase_charge(engine: Engine) -> None:
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    with pytest.raises(ApiError):
        complete(engine, lambda _: httpx.Response(200, json=reply(usage=usage)))
    assert attempts(engine)[0].charged_nano_usd == 8160000


def test_gateway_migration_upgrade_and_downgrade_preserve_other_tables() -> None:
    import importlib.util
    from pathlib import Path

    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import inspect

    path = Path(__file__).parents[1] / "migrations/versions/0003_gateway.py"
    spec = importlib.util.spec_from_file_location("test_gateway_migration", path)
    assert spec and spec.loader
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE existing_work (id INTEGER)")
        connection.exec_driver_sql("INSERT INTO existing_work VALUES (42)")
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
        assert connection.exec_driver_sql("SELECT id FROM gateway_lock").scalar() == 1
        for model in [GatewayLock, GatewayBudget, GatewayAttempt]:
            assert {c["name"] for c in inspect(connection).get_columns(model.__tablename__)} == {
                c.name for c in model.__table__.columns
            }
        with Operations.context(MigrationContext.configure(connection)):
            migration.downgrade()
        assert "gateway_attempts" not in inspect(connection).get_table_names()
        assert connection.exec_driver_sql("SELECT id FROM existing_work").scalar() == 42
    engine.dispose()
