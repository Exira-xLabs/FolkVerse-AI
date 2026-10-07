"""Fresh real API evaluation; respects configured admission and never changes provider settings."""

import argparse
import hashlib
import json
import math
import time
from collections import Counter, deque
from datetime import UTC, datetime
from pathlib import Path

import httpx
from folkverse.config import ROOT, Settings
from folkverse.database import make_engine
from folkverse.gateway_models import GatewayAttempt
from folkverse.guide_retrieval import EvidencePassage
from folkverse.guide_support import variants
from sqlalchemy import select
from sqlalchemy.orm import Session


def fraction(values):
    scored = [v for v in values if v is not None]
    return {
        "numerator": sum(scored),
        "denominator": len(scored),
        "rate": sum(scored) / len(scored) if scored else None,
    }


def audit(answer, sources, client):
    if answer["status"] != "answered":
        return {
            "claim_support": None,
            "citation_validity": None,
            "display_integrity": not answer["claims"] and not sources,
        }
    claims = answer["claims"]
    passages = {p["passage_id"]: p for p in sources}
    used = {pid for c in claims for pid in c["passage_ids"]}
    citation = used == set(passages) == set(answer["evidence_ids"])
    support = True
    for p in sources:
        if p["evidence_origin"] == "official_lookup":
            checked = client.get(f"/api/v1/guide/evidence/{p['passage_id']}").json()
            citation &= (
                checked.get("current") is True
                and checked.get("passage", {}).get("content_hash") == p["content_hash"]
            )
        elif p["evidence_origin"] == "reviewed_corpus":
            checked = client.get(f"/api/v1/sources/{p['source_id']}").json()
            citation &= any(
                q["id"] == p["passage_id"] and q["text"] == p["text"]
                for q in checked.get("passages", [])
            )
        else:
            citation = False
    for c in claims:
        evidence = [passages.get(pid) for pid in c["passage_ids"]]
        support &= bool(evidence) and all(
            p
            and variants(EvidencePassage.model_validate(p)).get(c["text"])
            == c["support_method"]
            and p["classification"] == c["kind"]
            for p in evidence
        )
        citation &= set(c["source_ids"]) == {p["source_id"] for p in evidence if p}
    sections = answer.get("sections", [])
    refs = [identifier for s in sections for identifier in s["claim_ids"]]
    display = len(refs) == len(set(refs)) and set(refs) == {
        c["claim_id"] for c in claims
    }
    display &= answer["answer_text"] == "\n\n".join(s["text"] for s in sections)
    by_claim = {c["claim_id"]: c for c in claims}
    for section in sections:
        if section["kind"] == "evidence":
            display &= section["text"] == "\n\n".join(
                by_claim[i]["text"] for i in section["claim_ids"]
            )
        else:
            display &= (
                not section["claim_ids"]
                and section["support_label"] == "general_unverified"
            )
    # A general-only answer has no sourced-fact score; human correctness remains pending.
    return {
        "claim_support": bool(support) if claims else None,
        "citation_validity": bool(citation) if claims else None,
        "display_integrity": bool(display),
    }


def evaluate(suite_path, output, run_label):
    suite = json.loads(suite_path.read_text())
    if (
        hashlib.sha256((ROOT / "data/manifests/corpus.json").read_bytes()).hexdigest()
        != suite["corpus_sha256"]
    ):
        raise ValueError("Frozen corpus changed; create a new suite version.")
    settings = Settings()
    if settings.app_mode != "live":
        raise ValueError(
            "Existing live configuration required; evaluation cannot activate billing."
        )
    result = {
        "version": "guide-hybrid-functional-evaluation-v3",
        "run_status": "running",
        "mode": "live",
        "started_at": datetime.now(UTC).isoformat(),
        "suite_sha256": hashlib.sha256(suite_path.read_bytes()).hexdigest(),
        "run_label": run_label,
        "authorship": suite["authorship"],
        "reservation": suite["reservation"],
        "provider": settings.guide_provider,
        "model": settings.provider_model,
        "gateway_admission_changed": False,
        "cases": [],
        "seed_answers": [],
        "attempt_ids": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    requests = deque()
    interval_limit = min(settings.model_global_rate_limit_per_minute, 24)

    def ask(client, question, locale, depth, prior=None, consent=False):
        while requests and requests[0] <= time.monotonic() - 61:
            requests.popleft()
        if len(requests) >= interval_limit:
            time.sleep(max(0, 61 - (time.monotonic() - requests[0])))
            while requests and requests[0] <= time.monotonic() - 61:
                requests.popleft()
        requests.append(time.monotonic())
        start = time.perf_counter()
        response = client.post(
            "/api/v1/guide",
            json={
                "question": question,
                "locale": locale,
                "depth": depth,
                "context_consent": bool(prior) or consent,
                "context_token": prior.get("context_token") if prior else None,
                "conversation": [
                    {
                        "user": prior["_probe_question"],
                        "assistant": prior["answer_text"],
                    }
                ]
                if prior and prior.get("_probe_question") and prior.get("answer_text")
                else [],
            },
            headers={"Origin": "http://127.0.0.1:3000"},
        )
        elapsed = (time.perf_counter() - start) * 1000
        body = response.json()
        if body.get("provider_attempt_id"):
            result["attempt_ids"].append(body["provider_attempt_id"])
        return body, elapsed

    for case in suite["cases"]:
        with httpx.Client(
            base_url="http://127.0.0.1:8000", timeout=65, trust_env=False
        ) as client:
            client.post(
                "/api/v1/session", headers={"Origin": "http://127.0.0.1:3000"}
            ).raise_for_status()
            prior = None
            try:
                if case["seed"]:
                    seed_locale = (
                        ("zh-CN" if case["locale"] == "en" else "en")
                        if case["seed"] == "other_language"
                        else case["locale"]
                    )
                    if case["seed"] == "official":
                        question = (
                            "When was Shenyang Imperial Palace founded?"
                            if seed_locale == "en"
                            else "沈阳故宫始建于哪一年？"
                        )
                    elif case["seed"] == "greeting":
                        question = "Hi" if seed_locale == "en" else "你好"
                    else:
                        question = (
                            "Explain Fuzhou shadow puppetry"
                            if seed_locale == "en"
                            else "介绍复州皮影戏"
                        )
                    prior, _ = ask(
                        client, question, seed_locale, "beginner", consent=True
                    )
                    prior["_probe_question"] = question
                    public_prior = {
                        k: v
                        for k, v in prior.items()
                        if k not in {"context_token", "_probe_question"}
                    }
                    result["seed_answers"].append(
                        {"case_id": case["id"], "answer": public_prior}
                    )
                if case["seed"] == "different_owner":
                    with httpx.Client(
                        base_url="http://127.0.0.1:8000", timeout=65, trust_env=False
                    ) as other:
                        other.post(
                            "/api/v1/session",
                            headers={"Origin": "http://127.0.0.1:3000"},
                        ).raise_for_status()
                        answer, elapsed = ask(
                            other,
                            case["question"],
                            case["locale"],
                            case["depth"],
                            prior,
                        )
                        other.delete(
                            "/api/v1/session",
                            headers={"Origin": "http://127.0.0.1:3000"},
                        )
                else:
                    answer, elapsed = ask(
                        client, case["question"], case["locale"], case["depth"], prior
                    )
                error = answer.get("error", {}).get("code")
                status = "error" if error else answer.get("status", "missing")
                sources = answer.get("sources", [])
                scores = (
                    audit(answer, sources, client)
                    if not error
                    else {
                        k: None
                        for k in [
                            "claim_support",
                            "citation_validity",
                            "display_integrity",
                        ]
                    }
                )
                support = case["expected_support"]
                support_state = (
                    (
                        bool(answer.get("claims"))
                        and all(
                            p["evidence_origin"] == "reviewed_corpus" for p in sources
                        )
                        and set(answer.get("evidence_ids", []))
                        <= set(case["allowed_reviewed_evidence_ids"])
                    )
                    if support == "reviewed"
                    else (
                        bool(sources)
                        and all(
                            p["evidence_origin"] == "official_lookup" for p in sources
                        )
                    )
                    if support == "official"
                    else (
                        not sources
                        and bool(answer.get("sections"))
                        and all(s["kind"] == "general" for s in answer["sections"])
                    )
                    if support == "general"
                    else not sources
                )
                scores["scenario"] = (
                    status == case["expected_status"]
                    and support_state
                    and (
                        error == "invalid_context"
                        if case["seed"] == "different_owner"
                        else True
                    )
                )
                scores["locale_delivery"] = (
                    answer.get("locale") == case["locale"] if not error else None
                )
                scores["uncertainty"] = (
                    answer.get("uncertainty") == case["required_uncertainty"]
                    and bool(answer.get("coverage_limit"))
                    if status in {"answered", "insufficient"}
                    else None
                )
                scores["followup_consistency"] = (
                    scores["scenario"]
                    if case["seed"] in {"reviewed", "official", "other_language"}
                    else None
                )
                scores["personality_structure"] = (
                    not answer.get("claims")
                    and not sources
                    and bool(answer.get("conversation_choice"))
                    if status == "conversational"
                    else None
                )
                row = {
                    **case,
                    "actual_status": status,
                    "actual_reason": error or answer.get("reason"),
                    "elapsed_ms": elapsed,
                    "scores": scores,
                    "answer": {k: v for k, v in answer.items() if k != "context_token"}
                    if not error
                    else None,
                    "error": error,
                    "sources": sources,
                }
                result["cases"].append(row)
                print(
                    f"{case['id']}: {status}; target {'PASS' if scores['scenario'] else 'FAIL'}",
                    flush=True,
                )
            finally:
                client.delete(
                    "/api/v1/session", headers={"Origin": "http://127.0.0.1:3000"}
                )
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    result["run_status"] = "completed"
    result["completed_at"] = datetime.now(UTC).isoformat()
    result["metrics"] = {
        name: fraction([c["scores"][name] for c in result["cases"]])
        for name in result["cases"][0]["scores"]
    }
    result["splits"] = {
        split: fraction(
            [c["scores"]["scenario"] for c in result["cases"] if c["split"] == split]
        )
        for split in ["development", "reserved"]
    }
    durations = sorted(
        c["elapsed_ms"] for c in result["cases"] if c["actual_status"] == "answered"
    )
    result["meaningful_api_latency_ms"] = {
        "sample": len(durations),
        "p50": durations[len(durations) // 2] if durations else None,
        "p95": durations[math.ceil(len(durations) * 0.95) - 1] if durations else None,
        "includes_seed": False,
        "browser_latency": False,
    }
    with Session(make_engine(settings)) as db:
        rows = db.scalars(
            select(GatewayAttempt).where(GatewayAttempt.id.in_(result["attempt_ids"]))
        ).all()
        result["usage"] = {
            "attempts_including_seeds": len(rows),
            "statuses": dict(Counter(r.status for r in rows)),
            "prompt_tokens": sum(r.prompt_tokens or 0 for r in rows),
            "completion_tokens": sum(r.completion_tokens or 0 for r in rows),
            "configured_rate_charge_usd": sum(r.charged_nano_usd for r in rows) / 1e9,
            "provider_invoice": False,
        }
    result["human_dimensions"] = {
        name: {"numerator": None, "denominator": 0, "pending": len(result["cases"])}
        for name in [
            "historical_correctness",
            "explanatory_clarity",
            "bilingual_faithfulness",
            "personality",
        ]
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return all(c["scores"]["scenario"] for c in result["cases"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite", type=Path, default=ROOT / "tests/evaluation/guide/v3-hybrid.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--run-label",
        default="first reserved functional run; post-implementation machine targets",
    )
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Do not overwrite dated evidence; select a new output path.")
    raise SystemExit(0 if evaluate(args.suite, args.output, args.run_label) else 1)
