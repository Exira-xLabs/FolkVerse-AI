"""Sanitized provider diagnostics; no visitor question or successful generation is needed."""

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx

from folkverse.config import Settings


async def diagnose(
    settings: Settings,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, object]:
    key = settings.provider_key
    result: dict[str, object] = {
        "checked_at": datetime.now(UTC).isoformat(),
        "provider": settings.guide_provider,
        "base_url": settings.provider_base_url,
        "model": settings.provider_model,
        "key_present": bool(key),
        "app_mode": settings.app_mode,
        "daily_request_limit": settings.ollama_daily_request_limit
        if settings.guide_provider == "ollama"
        else None,
        "daily_usd_budget": (
            "unlimited" if settings.daily_ai_budget_unlimited else str(settings.daily_ai_budget_usd)
        )
        if settings.guide_provider == "deepseek"
        else None,
        "authentication": "unverified",
        "generation_verified": False,
    }
    if not key:
        return result
    try:
        async with httpx.AsyncClient(
            transport=transport, trust_env=False, timeout=15, follow_redirects=False
        ) as client:
            headers = {"Authorization": "Bearer " + key.get_secret_value()}
            if settings.guide_provider == "deepseek":
                response = await client.get(settings.provider_base_url + "/models", headers=headers)
                result["http_status"] = response.status_code
                result["authentication"] = "accepted" if response.status_code == 200 else "rejected"
            else:
                catalog = await client.get("https://ollama.com/api/tags")
                result["catalog_http_status"] = catalog.status_code
                names = {m["name"] for m in catalog.json().get("models", [])}
                result["model_in_catalog"] = settings.provider_model in names
                # This model is deliberately absent; auth acceptance reaches model lookup.
                name = "folkverse-auth-" + uuid4().hex
                if name in names:
                    return result
                body = {
                    "model": name,
                    "messages": [{"role": "user", "content": "Auth probe."}],
                    "max_tokens": 1,
                    "stream": False,
                }
                response = await client.post(
                    settings.provider_base_url + "/chat/completions", headers=headers, json=body
                )
                control = await client.post(
                    settings.provider_base_url + "/chat/completions",
                    headers={"Authorization": "Bearer SYNTHETIC_INVALID_CONTROL"},
                    json=body,
                )
                result["http_status"] = response.status_code
                result["invalid_control_http_status"] = control.status_code
                if response.status_code == 404 and control.status_code == 401:
                    result["authentication"] = "accepted"
                elif response.status_code == 401:
                    result["authentication"] = "rejected"
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        result["authentication"] = "unverified"
        result["diagnostic_status"] = "unavailable_or_invalid_response"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = asyncio.run(diagnose(Settings()))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")
    parser.exit(0 if result["authentication"] == "accepted" else 2)


if __name__ == "__main__":
    main()
