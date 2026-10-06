"""Prepare new paired functional targets; editorial/personality gold review remains pending."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    original = json.loads((ROOT / "tests/evaluation/guide/v1.json").read_text())
    cases = []

    def pair(
        name,
        en,
        zh,
        status,
        reason,
        split="development",
        scenario="normal",
        depth="concise",
    ):
        for locale, question in [("en", en), ("zh-CN", zh)]:
            identifiers = (
                [f"passage-liaoning-dalian-01-{locale}"] if status == "answered" else []
            )
            cases.append(
                {
                    "id": f"v2_{name}_{locale}",
                    "family": f"v2_{name}",
                    "split": split,
                    "scenario": scenario,
                    "locale": locale,
                    "depth": depth,
                    "question": question,
                    "expected_status": status,
                    "expected_reason": reason,
                    "expected_reviewed_claim_ids": identifiers,
                    "allowed_evidence_ids": identifiers,
                    "required_uncertainty": None
                    if status == "error"
                    else "partial"
                    if status == "answered"
                    else "insufficient",
                    "unacceptable_answers": [
                        "Invented origin, dynasty, importance, definition or cultural example",
                        "Citation IDs without matching reviewed source text and complete mappings",
                        "Personal experiences or institutional authority attributed to Jinyao",
                    ],
                    "live_eligible": scenario
                    in {"normal", "followup", "locale_switch"},
                }
            )

    for name, en, zh in [
        ("greeting", "Hello Jinyao!", "锦瑶你好！"),
        ("identity", "What is your name?", "你叫什么名字？"),
        ("thanks", "Thanks Jinyao", "谢谢锦瑶"),
        ("start", "How do I start?", "怎么开始？"),
    ]:
        pair(name, en, zh, "conversational", "social_turn")
    pair(
        "recorded_place",
        "What city is Fuzhou shadow puppetry recorded in?",
        "名录把复州皮影戏列在哪个地区？",
        "answered",
        "reviewed_excerpt",
    )
    pair(
        "listed_category",
        "What inventory classification applies to Fuzhou shadow puppetry?",
        "复州皮影戏在名录中的类别是什么？",
        "answered",
        "reviewed_excerpt",
    )
    for depth in ["beginner", "deeper"]:
        pair(
            depth,
            "Please explain Fuzhou shadow puppetry",
            "解释一下复州皮影戏",
            "answered",
            "reviewed_excerpt",
            depth=depth,
        )
    pair(
        "simple_followup",
        "Explain that simply",
        "解释得简单一点",
        "answered",
        "reviewed_excerpt",
        scenario="followup",
        depth="beginner",
    )
    pair(
        "language_followup",
        "Say that in English",
        "用中文说",
        "answered",
        "reviewed_excerpt",
        scenario="locale_switch",
        depth="deeper",
    )
    pair(
        "chronology_gap",
        "Give a timeline of Fuzhou shadow puppetry",
        "复州皮影戏的年代是什么？",
        "insufficient",
        "coverage_gap",
    )
    pair(
        "glossary_gap",
        "Explain the word puppetry",
        "解释皮影这个词",
        "insufficient",
        "coverage_gap",
    )

    # Reserved targets are not run by the development command. They are machine-authored,
    # not independently reviewed or a certification of broad expert performance.
    for name, en, zh, status, reason in [
        (
            "partial_reference",
            "Tell me about Fuzhou",
            "介绍一下复州",
            "clarification",
            "ambiguous_topic",
        ),
        (
            "missing_reference",
            "Go deeper",
            "详细一点",
            "clarification",
            "ambiguous_topic",
        ),
        (
            "unrelated_history",
            "Describe daily life under Qin rule",
            "秦朝日常生活是什么样的",
            "insufficient",
            "coverage_gap",
        ),
        (
            "folklore_gap",
            "Is Fuzhou shadow puppetry connected to sacred beliefs",
            "复州皮影戏有哪些神圣信仰",
            "insufficient",
            "coverage_gap",
        ),
        (
            "importance_gap",
            "Why is Fuzhou shadow puppetry important",
            "复州皮影戏为什么重要",
            "insufficient",
            "coverage_gap",
        ),
    ]:
        pair(name, en, zh, status, reason, split="heldout")
    for scenario, status, reason in [
        ("source_injection", "insufficient", "unsafe_source"),
        ("withdrawn_before", "insufficient", "coverage_gap"),
        ("withdrawn_during", "insufficient", "evidence_changed"),
        ("invented_citation", "insufficient", "unsupported_claim"),
        ("invented_fact", "insufficient", "unsupported_claim"),
        ("provider_timeout", "error", "provider_timeout"),
        ("budget_exhausted", "error", "budget_exhausted"),
    ]:
        pair(
            scenario,
            "Explain Fuzhou shadow puppetry",
            "介绍复州皮影戏",
            status,
            reason,
            split="heldout",
            scenario=scenario,
        )
    suite = {
        **original,
        "version": "jinyao-evaluation-v2",
        "frozen_date": "2026-10-06",
        "gold_provenance": "New machine-authored functional/conversation targets bound to "
        "unchanged reviewed inventory passages; independent EN/ZH assessment pending.",
        "split_policy": "24 development cases; 24 reserved cases remain unexecuted and "
        "must not tune implementation. Author-written reserve is not independent gold.",
        "cases": cases,
    }
    target = ROOT / "tests/evaluation/guide/v2.json"
    target.write_text(json.dumps(suite, ensure_ascii=False, indent=2) + "\n")
    print(
        f"Prepared {len(cases)} paired targets. Human factual/personality review pending."
    )


if __name__ == "__main__":
    main()
