"""Freeze 200 unique bilingual Phase 3 questions before real-provider scoring."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Fresh paraphrases and concept families. These are machine targets, not independent expert gold.
CONCEPTS = [
    (
        "shadow",
        "What is shadow puppetry in plain language?",
        "用简单的话解释什么是皮影戏",
    ),
    (
        "silhouette",
        "Explain what a silhouette is to a beginner",
        "给初学者解释剪影是什么",
    ),
    ("museum", "What is a museum for?", "博物馆有什么作用？"),
    ("artifact", "What is an artifact?", "文物是什么意思？"),
    ("curator", "Explain what a museum curator does", "解释博物馆策展人的工作"),
    ("conservation", "What is museum conservation?", "博物馆里的文物保护是什么意思？"),
    (
        "restoration",
        "Explain the difference between conservation and restoration",
        "解释文物保护与修复的区别",
    ),
    ("archaeology", "What is archaeology?", "什么是考古学？"),
    ("excavation", "Explain an archaeological excavation", "解释考古发掘是什么"),
    ("context", "Why does archaeological context matter?", "为什么考古背景很重要？"),
    (
        "replica",
        "What is the difference between an original object and a replica?",
        "原件和复制品有什么区别？",
    ),
    (
        "provenance",
        "Explain what provenance means in a museum",
        "解释博物馆里的来源信息是什么意思",
    ),
    ("oral", "What is oral history?", "什么是口述历史？"),
    ("folklore", "Explain folklore simply", "简单解释民间传说"),
    (
        "legend",
        "What is the difference between legend and historical evidence?",
        "传说和历史证据有什么区别？",
    ),
    ("primary", "What is a primary source in history?", "历史研究中的一手资料是什么？"),
    (
        "secondary",
        "Explain primary and secondary sources",
        "解释一手资料和二手资料的区别",
    ),
    (
        "uncertainty",
        "Why should a historical explanation mention uncertainty?",
        "为什么历史解释要说明不确定性？",
    ),
    (
        "interpretation",
        "Explain how interpretation differs from evidence",
        "解释观点和证据有什么区别？",
    ),
    ("exhibition", "What does exhibition mean?", "展览是什么意思？"),
    (
        "caption",
        "Why do museum objects have explanatory labels?",
        "为什么博物馆的展品要有说明文字？",
    ),
    ("chronology", "What is a chronology?", "年代顺序是什么意思？"),
    ("craft", "Explain what craftsmanship means", "解释工艺技艺是什么意思"),
    ("calligraphy", "What is calligraphy?", "什么是书法？"),
    ("ceramic", "Explain pottery and porcelain simply", "简单解释陶器和瓷器的区别"),
    ("jade", "What is jade carving?", "什么是玉雕？"),
    ("pagoda", "Explain what a pagoda is", "解释佛塔是什么"),
    (
        "temple",
        "What is the difference between a temple and a museum?",
        "寺庙和博物馆有什么区别？",
    ),
    ("industrial", "Explain industrial heritage", "解释工业遗产是什么"),
    ("fossil", "What is a fossil?", "什么是化石？"),
    ("karst", "Explain a karst cave simply", "简单解释喀斯特洞穴"),
    (
        "stalactite",
        "What is the difference between a stalactite and a stalagmite?",
        "钟乳石和石笋有什么区别？",
    ),
    ("wetland", "What is a wetland?", "什么是湿地？"),
    (
        "tangible",
        "Explain tangible and intangible cultural heritage",
        "解释物质文化遗产和非物质文化遗产的区别",
    ),
    (
        "translation",
        "Why can cultural translation need an explanation?",
        "为什么文化翻译有时需要解释？",
    ),
    ("sources", "Why should a guide show its sources?", "为什么讲解员要展示资料来源？"),
    (
        "belief",
        "Explain the difference between belief and a verified historical claim",
        "解释信仰和核实过的历史说法有什么区别",
    ),
    (
        "adaptation",
        "What is a creative adaptation of history?",
        "历史的创作改编是什么意思？",
    ),
    (
        "comparison",
        "Why compare different historical sources?",
        "为什么要比较不同的历史资料？",
    ),
    (
        "simpler",
        "Could you explain that in simpler words?",
        "能把刚才的内容说得更简单吗？",
    ),
    ("depth", "Please give me more context about that", "请详细解释刚才的内容"),
    ("switch", "Could you explain that in English?", "请用中文再解释一次"),
    ("greeting", "Hello, Jinyao", "您好，锦瑶"),
    ("thanks", "Thanks Jinyao!", "谢谢锦瑶！"),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", type=int, default=5)
    version = parser.parse_args().version
    output = ROOT / f"tests/evaluation/guide/v{version}-phase03-pilot.json"
    if output.exists():
        raise ValueError("Frozen pilot cannot be overwritten.")
    aliases = json.loads((ROOT / "data/liaoning/search-aliases.json").read_text())[
        "aliases"
    ]
    materials = json.loads((ROOT / "data/liaoning/launch-material.json").read_text())[
        "materials"
    ]
    families = []
    for m in materials:
        names = aliases[m["source_id"]]
        families.append(
            (
                m["source_id"],
                f"Explain {names['en']} and give one example",
                f"介绍{names['zh-CN']}并举一个例子",
                "answered",
                "official",
                "beginner",
                None,
            )
        )
    # One unavailable current-information request per city; all 14 cities are represented.
    for m in materials[::3]:
        names = aliases[m["source_id"]]
        families.append(
            (
                "hours-" + m["city_id"],
                f"What time does {names['en']} open today?",
                f"{names['zh-CN']}今天几点开放？",
                "insufficient",
                "empty",
                "concise",
                None,
            )
        )
    for name, en, zh in CONCEPTS:
        seed = (
            "reviewed"
            if name in {"simpler", "depth"}
            else "other_language"
            if name == "switch"
            else None
        )
        support = (
            "reviewed"
            if seed
            else "conversation"
            if name in {"greeting", "thanks"}
            else "general"
        )
        families.append(
            (
                name,
                en,
                zh,
                "conversational" if support == "conversation" else "answered",
                support,
                "beginner",
                seed,
            )
        )
    assert len(families) == 100
    cases = []
    for i, (family, en, zh, status, support, depth, seed) in enumerate(families):
        for locale, q in [("en", en), ("zh-CN", zh)]:
            cases.append(
                {
                    "id": f"pilot-v{version}-{family}-{locale}",
                    "family": family,
                    "split": "development" if i % 4 == 0 else "reserved",
                    "locale": locale,
                    "question": q,
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
                        "unsupported factual assertions",
                        "unlabelled general explanation",
                        "invented citations",
                    ],
                    "expected_source_id": family if support == "official" else None,
                }
            )
    assert len({(c["locale"], c["question"]) for c in cases}) == 200
    payload = {
        "version": f"jinyao-evaluation-v{version}-phase03-pilot",
        "frozen_at": datetime.now(UTC).isoformat(),
        "authorship": "Codex-authored machine source-assessed targets; owner waived human review. No independent expert gold.",
        "reservation": "100 bilingual families share splits (50 development / 150 reserved cases). Revision 5 follows inspection of the incomplete v4 topic subset and source-name correction; shared questions are exposed diagnostics. Post-implementation machine targets, not blind expert gold. Frozen before the first revision-5 run.",
        "corpus_sha256": hashlib.sha256(
            (ROOT / "data/manifests/corpus.json").read_bytes()
        ).hexdigest(),
        "machine_source_audit_sha256": hashlib.sha256(
            (ROOT / "data/liaoning/machine-source-audit.json").read_bytes()
        ).hexdigest(),
        "cases": cases,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(
        "Frozen 200 distinct questions; 14 cities, 42 named topic pairs, 14 current-data refusals, 44 concept/conversation families."
    )


if __name__ == "__main__":
    main()
