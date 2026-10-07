"""Freeze paired functional targets before the first new hybrid-model evaluation."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Complete families share a split. Targets are engineering expectations, not expert gold.
FAMILIES = [
    (
        "hello",
        "Hi Jinyao!",
        "锦瑶你好！",
        "conversational",
        "conversation",
        "concise",
        None,
    ),
    (
        "identity",
        "What is your name?",
        "你叫什么名字？",
        "conversational",
        "conversation",
        "concise",
        None,
    ),
    (
        "thanks",
        "Thank you",
        "谢谢你",
        "conversational",
        "conversation",
        "concise",
        None,
    ),
    ("emoji", "🙂", "🙂", "conversational", "conversation", "concise", None),
    (
        "listing",
        "Where is Fuzhou shadow puppetry listed?",
        "复州皮影戏在哪个地区？",
        "answered",
        "reviewed",
        "concise",
        None,
    ),
    (
        "beginner",
        "Explain Fuzhou shadow puppetry simply",
        "简单介绍复州皮影戏",
        "answered",
        "reviewed",
        "beginner",
        None,
    ),
    (
        "depth",
        "Explain Fuzhou shadow puppetry in more detail",
        "详细介绍复州皮影戏",
        "answered",
        "reviewed",
        "deeper",
        None,
    ),
    (
        "definition",
        "What is shadow puppetry?",
        "什么是皮影戏？",
        "answered",
        "general",
        "beginner",
        None,
    ),
    (
        "glossary",
        "What does silhouette mean?",
        "剪影是什么意思？",
        "answered",
        "general",
        "beginner",
        None,
    ),
    (
        "concept_why",
        "Why do museums explain their sources?",
        "为什么博物馆要说明资料来源？",
        "answered",
        "general",
        "deeper",
        None,
    ),
    (
        "comparison",
        "What is the difference between folklore and historical evidence?",
        "民间传说和历史证据有什么区别？",
        "answered",
        "general",
        "deeper",
        None,
    ),
    (
        "simple_followup",
        "Explain that simply",
        "解释得简单一点",
        "answered",
        "reviewed",
        "beginner",
        "reviewed",
    ),
    (
        "deeper_followup",
        "Go deeper",
        "详细一点",
        "answered",
        "reviewed",
        "deeper",
        "reviewed",
    ),
    (
        "language_followup",
        "用英文说",
        "Say that in Chinese",
        "answered",
        "reviewed",
        "beginner",
        "other_language",
    ),
    (
        "mixed_greeting",
        "Hi, explain Fuzhou shadow puppetry",
        "你好，介绍复州皮影戏",
        "answered",
        "reviewed",
        "beginner",
        None,
    ),
    (
        "lookup_date",
        "When was Shenyang Imperial Palace founded?",
        "沈阳故宫始建于哪一年？",
        "answered",
        "official",
        "concise",
        None,
    ),
    (
        "lookup_followup",
        "Explain that simply",
        "解释得简单一点",
        "answered",
        "official",
        "beginner",
        "official",
    ),
    (
        "missing_origin",
        "When was Fuzhou shadow puppetry invented?",
        "复州皮影戏是哪一年发明的？",
        "insufficient",
        "empty",
        "concise",
        None,
    ),
    (
        "current_hours",
        "What are the current opening hours of Shenyang Imperial Palace?",
        "沈阳故宫今天几点开放？",
        "insufficient",
        "empty",
        "concise",
        None,
    ),
    (
        "disputed",
        "Who first invented Fuzhou shadow puppetry?",
        "复州皮影戏最早是谁发明的？",
        "insufficient",
        "empty",
        "concise",
        None,
    ),
    (
        "unsupported_year",
        "Was Fuzhou shadow puppetry founded in 1644?",
        "复州皮影戏始建于1644年吗？",
        "insufficient",
        "empty",
        "concise",
        None,
    ),
    (
        "context_owner",
        "Explain that simply",
        "解释得简单一点",
        "error",
        "empty",
        "beginner",
        "different_owner",
    ),
    (
        "greeting_repeat",
        "Hi again",
        "你好呀",
        "conversational",
        "conversation",
        "concise",
        "greeting",
    ),
    ("goodbye", "Bye", "再见", "conversational", "conversation", "concise", None),
]


def main():
    output = ROOT / "tests/evaluation/guide/v3-hybrid.json"
    if output.exists():
        raise SystemExit(
            "Frozen suite already exists; create a new version instead of overwriting."
        )
    cases = []
    for index, (name, en, zh, status, support, depth, seed) in enumerate(FAMILIES):
        for locale, question in [("en", en), ("zh-CN", zh)]:
            cases.append(
                {
                    "id": f"hybrid-v3-{name}-{locale}",
                    "family": name,
                    "split": "development" if index % 3 == 0 else "reserved",
                    "locale": locale,
                    "question": question,
                    "depth": depth,
                    "seed": seed,
                    "expected_status": status,
                    "expected_support": support,
                    "required_uncertainty": "partial"
                    if support in {"reviewed", "official"}
                    else "insufficient",
                    "allowed_reviewed_evidence_ids": [
                        f"passage-liaoning-dalian-01-{locale}"
                    ]
                    if support == "reviewed"
                    else [],
                    "unacceptable": [
                        "fabricated local facts or citations",
                        "unlabelled general explanation",
                        "failed supported claim relabelled general",
                    ],
                }
            )
    suite = {
        "version": "jinyao-evaluation-v3-hybrid",
        "frozen_at": datetime.now(UTC).isoformat(),
        "authorship": "Codex-authored functional targets; human adjudication pending",
        "reservation": "Whole bilingual families share a split; reserved cases frozen before first new run. Post-implementation authored, not blind expert gold. Any rerun after inspection is exposed diagnostic evidence.",
        "corpus_sha256": hashlib.sha256(
            (ROOT / "data/manifests/corpus.json").read_bytes()
        ).hexdigest()
        if (ROOT / "data/manifests/corpus.json").exists()
        else None,
        "live_fault_policy": "No live content mutation; corpus/provider failure attacks are exercised by isolated API/browser fixtures, not production quota exhaustion.",
        "cases": cases,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(suite, ensure_ascii=False, indent=2) + "\n")
    print(f"Frozen {len(cases)} paired hybrid cases; human gold pending.")


if __name__ == "__main__":
    main()
