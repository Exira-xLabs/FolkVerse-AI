"""Server-only JSON transport; the guide harness must validate its untrusted output."""

import asyncio
import json
import time
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from folkverse.config import Settings
from folkverse.errors import ApiError
from folkverse.gateway_limits import UsageLedger

GATEWAY_VERSION = "guide-json-v2"
MAX_RESPONSE_BYTES = 131072
TRANSIENT_STATUSES = {429, 500, 502, 503, 504}


class ProviderUsage(BaseModel):
    model_config = ConfigDict(strict=True)
    prompt_tokens: int = Field(ge=1)
    completion_tokens: int = Field(ge=1)
    total_tokens: int = Field(ge=2)


class ProviderResult(BaseModel):
    payload: dict[str, Any] = Field(repr=False)
    usage: ProviderUsage
    model: str
    attempt_id: str
    latency_ms: int
    gateway_version: str = GATEWAY_VERSION


class ProviderMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, repr=False)


def unavailable() -> ApiError:
    return ApiError(503, "provider_unavailable", "The guide is temporarily unavailable.", True)


def parse_json(raw: str | bytes | bytearray) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError("Non-finite JSON value")

    def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON field")
            result[key] = value
        return result

    return json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_keys)


class GuideGateway:
    def __init__(
        self,
        settings: Settings,
        ledger: UsageLedger,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings, self.ledger, self.transport = settings, ledger, transport

    def _ready(self) -> None:
        s = self.settings
        if (
            s.app_mode != "live"
            or not s.provider_key
            or not s.provider_key.get_secret_value().strip()
        ):
            raise unavailable()
        if s.guide_provider == "ollama":
            if s.ollama_daily_request_limit <= 0:
                raise unavailable()
        elif (
            s.daily_ai_budget_usd <= 0
            or s.deepseek_price_model != s.deepseek_model
            or s.deepseek_price_base_url != s.deepseek_base_url
            or s.deepseek_input_usd_per_million is None
            or s.deepseek_output_usd_per_million is None
        ):
            raise unavailable()

    async def complete(
        self,
        messages: list[ProviderMessage],
        actor_id: str,
    ) -> ProviderResult:
        self._ready()
        s = self.settings
        if not actor_id or len(actor_id) > 200 or not 1 <= len(messages) <= 12:
            raise ApiError(422, "invalid_input", "The guide request is invalid.")
        # Byte-level upper bound with generous per-message framing allowance.
        input_bound = sum(len(m.content.encode("utf-8")) + 256 for m in messages) + 256
        if input_bound > s.model_max_input_tokens:
            raise ApiError(413, "context_too_large", "The guide context is too large.")
        if not any("json" in m.content.casefold() for m in messages if m.role == "system"):
            raise ApiError(422, "invalid_input", "A server JSON instruction is required.")
        try:
            async with asyncio.timeout(s.model_timeout_seconds):
                return await self._complete(messages, actor_id)
        except TimeoutError:
            raise ApiError(
                503, "provider_timeout", "The guide timed out. Try again.", True
            ) from None

    async def _complete(
        self,
        messages: list[ProviderMessage],
        actor_id: str,
    ) -> ProviderResult:
        s = self.settings
        key = s.provider_key
        assert key is not None
        request_body = {
            "model": s.provider_model,
            "messages": [m.model_dump() for m in messages],
            "max_tokens": s.model_max_output_tokens,
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        if s.guide_provider == "deepseek":
            request_body["thinking"] = {"type": "disabled"}
        else:
            request_body["reasoning_effort"] = "none"
        # Reserve every attempt separately, including a possibly billed retry.
        reserve = self.ledger.cost(s.model_max_input_tokens, s.model_max_output_tokens)
        async with httpx.AsyncClient(
            transport=self.transport,
            follow_redirects=False,
            trust_env=False,
            timeout=httpx.Timeout(s.model_timeout_seconds),
        ) as client:
            for number in range(2):
                pending = asyncio.create_task(
                    asyncio.to_thread(self.ledger.reserve, actor_id, reserve)
                )
                try:
                    attempt = await asyncio.shield(pending)
                except asyncio.CancelledError:
                    # Admission may already have committed in its worker thread.
                    try:
                        attempt = await pending
                        await asyncio.shield(
                            asyncio.to_thread(
                                self.ledger.finish,
                                attempt,
                                "cancelled",
                                0,
                            )
                        )
                    except ApiError:
                        pass
                    raise
                started = time.monotonic()
                status = "failed"
                usage: ProviderUsage | None = None
                retry = False
                try:
                    async with client.stream(
                        "POST",
                        s.provider_base_url + "/chat/completions",
                        headers={
                            "Authorization": "Bearer " + key.get_secret_value(),
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        },
                        json=request_body,
                    ) as response:
                        if response.status_code in TRANSIENT_STATUSES:
                            retry = number == 0
                            # Do not retry earlier than a provider's requested wait.
                            if response.headers.get("retry-after"):
                                retry = False
                            raise unavailable()
                        if response.status_code != 200:
                            raise unavailable()
                        if "application/json" not in response.headers.get("content-type", ""):
                            raise unavailable()
                        raw = bytearray()
                        async for chunk in response.aiter_bytes():
                            raw.extend(chunk)
                            if len(raw) > MAX_RESPONSE_BYTES:
                                raise unavailable()
                    data = parse_json(raw)
                    if not isinstance(data, dict):
                        raise unavailable()
                    usage = ProviderUsage.model_validate(data.get("usage"))
                    if usage.total_tokens != usage.prompt_tokens + usage.completion_tokens:
                        usage = None
                        raise unavailable()
                    if (
                        usage.prompt_tokens > s.model_max_input_tokens
                        or usage.completion_tokens > s.model_max_output_tokens
                    ):
                        # Reconcile the actual bill, but never publish an out-of-bounds reply.
                        raise unavailable()
                    choices = data.get("choices")
                    if (
                        data.get("model") != s.provider_model
                        or not isinstance(choices, list)
                        or len(choices) != 1
                        or not isinstance(choices[0], dict)
                    ):
                        raise unavailable()
                    choice = choices[0]
                    message = choice.get("message")
                    if (
                        choice.get("finish_reason") != "stop"
                        or not isinstance(message, dict)
                        or message.get("role") != "assistant"
                        or message.get("tool_calls")
                        or not isinstance(message.get("content"), str)
                    ):
                        raise unavailable()
                    payload = parse_json(message["content"])
                    if not isinstance(payload, dict) or not payload:
                        raise unavailable()
                    status = "completed"
                    return ProviderResult(
                        payload=payload,
                        usage=usage,
                        model=s.provider_model,
                        attempt_id=attempt,
                        latency_ms=int((time.monotonic() - started) * 1000),
                    )
                except asyncio.CancelledError:
                    status = "cancelled"
                    raise
                except (httpx.TransportError, OSError):
                    retry = number == 0
                    if not retry:
                        raise unavailable() from None
                except (ValueError, ValidationError, RecursionError):
                    raise unavailable() from None
                except ApiError:
                    if not retry:
                        raise
                finally:
                    cleanup = asyncio.create_task(
                        asyncio.to_thread(
                            self.ledger.finish,
                            attempt,
                            status,
                            int((time.monotonic() - started) * 1000),
                            usage.prompt_tokens if usage else None,
                            usage.completion_tokens if usage else None,
                        )
                    )
                    try:
                        await asyncio.shield(cleanup)
                    except asyncio.CancelledError:
                        await cleanup
                        raise
                if retry:
                    await asyncio.sleep(0.25)  # One bounded backoff within the total deadline.
        raise unavailable()


# Keep existing integrations/imports compatible; production uses the provider-neutral name.
DeepSeekGateway = GuideGateway
