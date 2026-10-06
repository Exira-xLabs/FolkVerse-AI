"""Provider authentication diagnostics never expose credentials or generate with a real model."""

import asyncio
import json

import httpx
import pytest
from test_provider_gateway import configuration, ollama_configuration

from folkverse.guide_doctor import diagnose


@pytest.mark.parametrize(
    "status,control,expected",
    [
        (404, 401, "accepted"),
        (404, 404, "unverified"),
        (401, 401, "rejected"),
    ],
)
def test_ollama_auth_uses_invalid_model_and_negative_control(status, control, expected):
    seen = []
    settings = ollama_configuration(ollama_daily_request_limit=0)

    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"models": [{"name": settings.provider_model}]})
        body = json.loads(request.content)
        assert body["model"].startswith("folkverse-auth-")
        assert body["model"] != settings.provider_model and body["max_tokens"] == 1
        seen.append(request.headers["authorization"])
        return httpx.Response(
            status if len(seen) == 1 else control, json={"error": "sensitive raw upstream content"}
        )

    result = asyncio.run(diagnose(settings, httpx.MockTransport(handler)))
    assert result["authentication"] == expected
    assert result["generation_verified"] is False and result["model_in_catalog"] is True
    assert settings.ollama_daily_request_limit == 0
    assert "SYNTHETIC_OLLAMA_KEY" not in json.dumps(result)
    assert "sensitive raw" not in json.dumps(result)


def test_missing_provider_key_sends_no_request():
    def handler(request):
        raise AssertionError("No credential was configured")

    result = asyncio.run(
        diagnose(ollama_configuration(ollama_api_key=None), httpx.MockTransport(handler))
    )
    assert result["key_present"] is False and result["authentication"] == "unverified"


def test_deepseek_diagnostic_uses_only_the_models_endpoint():
    def handler(request):
        assert request.method == "GET" and request.url == "https://api.deepseek.com/models"
        return httpx.Response(401, json={"error": "SYNTHETIC_TEST_KEY"})

    result = asyncio.run(diagnose(configuration(), httpx.MockTransport(handler)))
    assert result["authentication"] == "rejected"
    assert "SYNTHETIC_TEST_KEY" not in json.dumps(result)


def test_invalid_catalog_leaves_auth_unverified():
    result = asyncio.run(
        diagnose(
            ollama_configuration(),
            httpx.MockTransport(
                lambda request: httpx.Response(502, text="sensitive upstream failure")
            ),
        )
    )
    assert result["authentication"] == "unverified"
    assert "sensitive" not in json.dumps(result)
