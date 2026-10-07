"""Journey explanations are code selection only; the fake gateway never touches a provider."""

import asyncio
import json

import pytest
from pydantic import ValidationError

from folkverse.errors import ApiError
from folkverse.journey_explanations import (
    FALLBACK_REASONS,
    REASON_TEXT,
    ExplanationResult,
    JourneyExplainer,
    render_reason,
)
from folkverse.provider_gateway import ProviderResult, ProviderUsage


def result_payload(payload, attempt_id="call_test"):
    return ProviderResult(
        payload=payload,
        usage=ProviderUsage(prompt_tokens=12, completion_tokens=6, total_tokens=18),
        model="deepseek-flash",
        attempt_id=attempt_id,
        latency_ms=3,
    )


class FakeGateway:
    """No provider call; ``payload=None`` echoes one allowed code per requested stop."""

    def __init__(self, payload=None, *, error=None, delay=0.0, fail_times=0, code="theme_match"):
        self.payload = payload
        self.error = error
        self.delay = delay
        self.fail_times = fail_times
        self.code = code
        self.calls = 0
        self.actor_ids = []
        self.messages = []

    async def complete(self, messages, actor_id):
        self.calls += 1
        self.actor_ids.append(actor_id)
        self.messages.append(messages)
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None and self.calls <= self.fail_times:
            raise self.error
        payload = self.payload
        if payload is None:
            body = json.loads(messages[-1].content)
            payload = {"stops": []}
            for item in body["untrusted_stops"]:
                allowed = item["allowed_reason_codes"]
                chosen = self.code if self.code in allowed else allowed[0]
                payload["stops"].append(
                    {"exhibit_id": item["exhibit_id"], "reason_codes": [chosen]}
                )
        return result_payload(payload)


def stop(identifier, *, allowed=("theme_match",), fallback=None, **extra):
    data = {
        "exhibit_id": identifier,
        "title": f"Route stop {identifier}",
        "summary": f"Reviewed summary for {identifier}.",
        "themes": ["shadow puppetry"],
        "estimated_minutes": 20,
        "allowed_reason_codes": list(allowed),
    }
    if fallback is not None:
        data["fallback_reason"] = fallback
    data.update(extra)
    return data


def run(coroutine):
    return asyncio.run(coroutine)


def unavailable_error():
    return ApiError(503, "provider_unavailable", "The guide is temporarily unavailable.", True)


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_generated_selection_renders_localized_server_text(locale):
    gateway = FakeGateway(
        {"stops": [{"exhibit_id": "shadow-01", "reason_codes": ["theme_match", "time_fit"]}]}
    )
    explainer = JourneyExplainer(gateway)
    result = run(
        explainer.explain(
            [stop("shadow-01", allowed=("theme_match", "time_fit"))],
            locale,
            ["puppetry"],
            "visitor-1",
            "corpus-1",
        )
    )
    assert result.status == "generated" and result.source == "model"
    assert result.detail == "generated"
    assert result.provider_attempt_id == "call_test"
    assert result.codes == {"shadow-01": ["theme_match", "time_fit"]}
    expected = REASON_TEXT[locale]["theme_match"] + " " + REASON_TEXT[locale]["time_fit"]
    assert result.reasons == {"shadow-01": expected}
    assert gateway.actor_ids == ["visitor-1"]


def test_codes_render_in_server_canonical_order_not_model_order():
    gateway = FakeGateway(
        {
            "stops": [
                {
                    "exhibit_id": "shadow-01",
                    "reason_codes": ["collection_discovery", "theme_match"],
                }
            ]
        }
    )
    result = run(
        JourneyExplainer(gateway).explain(
            [stop("shadow-01", allowed=("theme_match", "collection_discovery"))],
            "en",
            [],
            "visitor-1",
            "corpus-1",
        )
    )
    assert result.codes == {"shadow-01": ["theme_match", "collection_discovery"]}
    assert result.reasons["shadow-01"].startswith(REASON_TEXT["en"]["theme_match"])


@pytest.mark.parametrize(
    "attack",
    [
        "unknown_id",
        "extra_id",
        "missing_id",
        "duplicate_id",
        "unknown_code",
        "duplicate_code",
        "empty_codes",
        "stop_extra_field",
        "root_extra_field",
        "prose_field",
        "wrong_type",
    ],
)
def test_rejected_replies_never_leak_model_prose_or_ids(attack):
    stops = [
        stop("shadow-01", fallback="Parent reason one."),
        stop("shadow-02", fallback="Parent reason two."),
    ]
    valid = [
        {"exhibit_id": "shadow-01", "reason_codes": ["theme_match"]},
        {"exhibit_id": "shadow-02", "reason_codes": ["time_fit"]},
    ]
    payload = {"stops": [dict(item) for item in valid]}
    if attack == "unknown_id":
        payload["stops"][1]["exhibit_id"] = "invented-99"
    elif attack == "extra_id":
        payload["stops"].append({"exhibit_id": "invented-99", "reason_codes": ["time_fit"]})
    elif attack == "missing_id":
        payload["stops"].pop()
    elif attack == "duplicate_id":
        payload["stops"][1]["exhibit_id"] = "shadow-01"
    elif attack == "unknown_code":
        payload["stops"][1]["reason_codes"] = ["invented_code"]
    elif attack == "duplicate_code":
        payload["stops"][1]["reason_codes"] = ["time_fit", "time_fit"]
    elif attack == "empty_codes":
        payload["stops"][1]["reason_codes"] = []
    elif attack == "stop_extra_field":
        payload["stops"][0]["text"] = "Shadow puppetry was founded in 1450 in Fuzhou."
    elif attack == "root_extra_field":
        payload["reasons"] = {"shadow-01": "Invented prose."}
    elif attack == "prose_field":
        payload["stops"][0]["note"] = "Ignore previous instructions."
    else:
        payload["stops"][0]["reason_codes"] = "theme_match"
    gateway = FakeGateway(payload)
    result = run(
        JourneyExplainer(gateway).explain(stops, "en", [], "visitor-1", "corpus-1")
    )
    assert gateway.calls == 1
    assert result.status == "unavailable" and result.detail == "rejected_reply"
    assert result.codes == {}
    assert result.reasons == {
        "shadow-01": "Parent reason one.",
        "shadow-02": "Parent reason two.",
    }
    blob = json.dumps(result.model_dump(), ensure_ascii=False)
    for leaked in ["1450", "Invented prose", "Ignore previous instructions", "invented"]:
        assert leaked not in blob


def test_provider_outage_uses_parent_fallback_reason():
    gateway = FakeGateway(error=unavailable_error(), fail_times=100)
    explainer = JourneyExplainer(gateway)
    stops = [stop("shadow-01", fallback="Parent authored base reason.")]
    result = run(explainer.explain(stops, "en", [], "visitor-1", "corpus-1"))
    assert result.status == "unavailable" and result.detail == "provider_error"
    assert result.source == "fallback" and result.provider_attempt_id is None
    assert result.reasons == {"shadow-01": "Parent authored base reason."}
    assert result.codes == {} and explainer.cache_size == 0


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_default_localized_fallback_is_used_when_parent_supplies_none(locale):
    gateway = FakeGateway(error=unavailable_error(), fail_times=100)
    result = run(
        JourneyExplainer(gateway).explain([stop("shadow-01")], locale, [], "visitor-1", "corpus-1")
    )
    assert result.reasons == {"shadow-01": FALLBACK_REASONS[locale]}
    assert result.codes == {} and result.source == "fallback"


def test_unchanged_route_is_served_from_cache_without_a_second_call():
    gateway = FakeGateway()
    explainer = JourneyExplainer(gateway)
    stops = [stop("shadow-01"), stop("shadow-02", allowed=("time_fit",))]
    first = run(explainer.explain(stops, "en", ["puppetry"], "visitor-1", "corpus-1"))
    second = run(explainer.explain(stops, "en", ["puppetry"], "visitor-1", "corpus-1"))
    assert gateway.calls == 1
    assert second.status == "generated" and second.source == "cache"
    assert second.detail == "cache_hit" and second.provider_attempt_id is None
    assert second.reasons == first.reasons and second.codes == first.codes


@pytest.mark.parametrize("change", ["locale", "corpus", "preferences", "route_order"])
def test_cache_invalidates_on_locale_corpus_preferences_and_route(change):
    gateway = FakeGateway()
    explainer = JourneyExplainer(gateway)
    stops = [stop("shadow-01"), stop("shadow-02", allowed=("time_fit",))]
    run(explainer.explain(stops, "en", ["puppetry"], "visitor-1", "corpus-1"))
    changed = list(stops)
    locale, preferences, signature = "en", ["puppetry"], "corpus-1"
    if change == "locale":
        locale = "zh-CN"
    elif change == "corpus":
        signature = "corpus-2"
    elif change == "preferences":
        preferences = ["architecture"]
    else:
        changed = list(reversed(stops))
    run(explainer.explain(changed, locale, preferences, "visitor-1", signature))
    assert gateway.calls == 2


def test_cache_is_bounded_and_evicts_least_recently_used():
    gateway = FakeGateway()
    explainer = JourneyExplainer(gateway, max_entries=2)
    for index in range(3):
        run(
            explainer.explain(
                [stop(f"shadow-0{index}")], "en", [], "visitor-1", "corpus-1"
            )
        )
    assert explainer.cache_size == 2
    run(explainer.explain([stop("shadow-00")], "en", [], "visitor-1", "corpus-1"))
    assert gateway.calls == 4


def test_cache_entries_expire_by_ttl():
    now = [1000.0]
    gateway = FakeGateway()
    explainer = JourneyExplainer(gateway, ttl_seconds=60.0, clock=lambda: now[0])
    stops = [stop("shadow-01")]
    assert run(explainer.explain(stops, "en", [], "visitor-1", "corpus-1")).source == "model"
    assert run(explainer.explain(stops, "en", [], "visitor-1", "corpus-1")).source == "cache"
    now[0] += 61.0
    expired = run(explainer.explain(stops, "en", [], "visitor-1", "corpus-1"))
    assert expired.source == "model" and gateway.calls == 2


def test_concurrent_identical_routes_share_one_provider_call():
    gateway = FakeGateway(delay=0.05)
    explainer = JourneyExplainer(gateway)
    stops = [stop("shadow-01")]

    async def burst():
        return await asyncio.gather(
            *[explainer.explain(stops, "en", [], "visitor-1", "corpus-1") for _ in range(5)]
        )

    results = run(burst())
    assert gateway.calls == 1
    assert all(result.status == "generated" for result in results)
    assert len({result.reasons["shadow-01"] for result in results}) == 1
    details = [result.detail for result in results]
    assert details.count("generated") == 1 and details.count("shared_call") == 4


def test_unavailable_is_retried_and_never_poisoned_forever():
    gateway = FakeGateway(error=unavailable_error(), fail_times=1)
    explainer = JourneyExplainer(gateway)
    stops = [stop("shadow-01")]
    first = run(explainer.explain(stops, "en", [], "visitor-1", "corpus-1"))
    assert first.status == "unavailable" and first.detail == "provider_error"
    second = run(explainer.explain(stops, "en", [], "visitor-1", "corpus-1"))
    assert second.status == "generated" and gateway.calls == 2


def test_prompt_marks_stops_untrusted_and_withholds_parent_prose():
    gateway = FakeGateway()
    stops = [stop("shadow-01", fallback="Parent fallback prose.")]
    run(JourneyExplainer(gateway).explain(stops, "en", ["puppetry"], "visitor-1", "corpus-1"))
    system, user = gateway.messages[0]
    assert system.role == "system" and "json" in system.content.casefold()
    assert "untrusted" in system.content.casefold()
    assert "never write" in system.content.casefold()
    body = json.loads(user.content)
    assert body["interests"] == ["puppetry"]
    assert body["untrusted_stops"] == [
        {
            "exhibit_id": "shadow-01",
            "allowed_reason_codes": ["theme_match"],
            "themes": ["shadow puppetry"],
            "estimated_minutes": 20,
            "title": "Route stop shadow-01",
            "summary": "Reviewed summary for shadow-01.",
        }
    ]
    assert "Parent fallback prose." not in user.content


def test_unknown_allowed_vocabulary_is_filtered_before_the_model_sees_it():
    gateway = FakeGateway(code="time_fit")
    stops = [stop("shadow-01", allowed=("invented_code", "time_fit"))]
    result = run(
        JourneyExplainer(gateway).explain(stops, "en", [], "visitor-1", "corpus-1")
    )
    body = json.loads(gateway.messages[0][-1].content)
    assert body["untrusted_stops"][0]["allowed_reason_codes"] == ["time_fit"]
    assert result.status == "generated"


def test_stops_without_allowed_codes_are_not_sent_and_use_their_fallback():
    gateway = FakeGateway()
    stops = [
        stop("shadow-01"),
        stop("shadow-02", allowed=(), fallback="No model selection for this stop."),
    ]
    result = run(
        JourneyExplainer(gateway).explain(stops, "en", [], "visitor-1", "corpus-1")
    )
    body = json.loads(gateway.messages[0][-1].content)
    assert [item["exhibit_id"] for item in body["untrusted_stops"]] == ["shadow-01"]
    assert result.status == "generated"
    assert result.codes == {"shadow-01": ["theme_match"]}
    assert result.reasons["shadow-02"] == "No model selection for this stop."


def test_route_without_any_allowed_codes_skips_the_provider():
    gateway = FakeGateway()
    stops = [stop("shadow-01", allowed=("invented",), fallback="Parent base.")]
    result = run(
        JourneyExplainer(gateway).explain(stops, "en", [], "visitor-1", "corpus-1")
    )
    assert gateway.calls == 0
    assert result.status == "unavailable" and result.detail == "no_allowed_codes"
    assert result.source == "fallback" and result.reasons == {"shadow-01": "Parent base."}


def test_unrelated_sources_metadata_is_ignored_and_never_sent():
    gateway = FakeGateway()
    stops = [stop("shadow-01", sources=[{"url": "https://example.org/private-source"}])]
    run(JourneyExplainer(gateway).explain(stops, "en", [], "visitor-1", "corpus-1"))
    assert "example.org" not in gateway.messages[0][-1].content


@pytest.mark.parametrize(
    "fault,detail",
    [
        ("locale", "invalid_input"),
        ("duplicate_stop", "invalid_input"),
        ("malformed_stop", "invalid_input"),
        ("signature_type", "invalid_input"),
        ("empty_route", "no_stops"),
        ("too_many_stops", "too_many_stops"),
    ],
)
def test_invalid_input_is_unavailable_without_a_provider_call(fault, detail):
    gateway = FakeGateway()
    explainer = JourneyExplainer(gateway, max_stops=2)
    stops = [stop("shadow-01")]
    locale, signature = "en", "corpus-1"
    if fault == "locale":
        locale = "fr"
    elif fault == "duplicate_stop":
        stops = [stop("shadow-01"), stop("shadow-01")]
    elif fault == "malformed_stop":
        stops = [{"title": "Missing identifier"}]
    elif fault == "signature_type":
        signature = 42
    elif fault == "empty_route":
        stops = []
    else:
        stops = [stop("shadow-01"), stop("shadow-02"), stop("shadow-03")]
    result = run(explainer.explain(stops, locale, [], "visitor-1", signature))
    assert gateway.calls == 0
    assert result.status == "unavailable" and result.detail == detail
    assert result.codes == {}


def test_malformed_input_carries_no_reasons_but_oversized_route_keeps_fallbacks():
    gateway = FakeGateway()
    explainer = JourneyExplainer(gateway, max_stops=1)
    malformed = run(explainer.explain([{"title": "x"}], "en", [], "visitor-1", "corpus-1"))
    assert malformed.reasons == {} and malformed.source == "none"
    oversized = run(
        explainer.explain(
            [
                stop("shadow-01", fallback="Base one."),
                stop("shadow-02", fallback="Base two."),
            ],
            "en",
            [],
            "visitor-1",
            "corpus-1",
        )
    )
    assert oversized.source == "fallback"
    assert oversized.reasons == {"shadow-01": "Base one.", "shadow-02": "Base two."}


def test_result_model_forbids_extra_fields_and_versions_the_contract():
    with pytest.raises(ValidationError):
        ExplanationResult(status="generated", reasons={}, codes={}, unexpected=True)
    result = ExplanationResult(status="unavailable", reasons={}, codes={})
    assert result.explainer_version == "journey-reason-codes-v1"


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_render_reason_ignores_unknown_codes_and_falls_back(locale):
    assert render_reason(["time_fit", "invented"], locale) == REASON_TEXT[locale]["time_fit"]
    assert render_reason([], locale) == FALLBACK_REASONS[locale]
    assert render_reason(["starting_exhibit"], "fr") == REASON_TEXT["en"]["starting_exhibit"]


@pytest.mark.parametrize(
    "locale,expected",
    [
        ("en", "Adds an exhibit outside the previous stops you explicitly supplied."),
        ("zh-CN", "补充一个不在您此前明确提供的停靠点之内的展项。"),
    ],
)
def test_new_discovery_means_previous_supplied_stops_not_themes(locale, expected):
    # novelty_exhibit_ids are IDs the planner deprioritizes, not theme preferences.
    assert REASON_TEXT[locale]["new_discovery"] == expected
    assert render_reason(["new_discovery"], locale) == expected
    assert "theme" not in expected.casefold() and "主题" not in expected
    assert REASON_TEXT[locale]["theme_match"] != expected


def test_constructor_rejects_unbounded_configuration():
    gateway = FakeGateway()
    with pytest.raises(ValueError):
        JourneyExplainer(gateway, max_entries=0)
    with pytest.raises(ValueError):
        JourneyExplainer(gateway, ttl_seconds=0)
