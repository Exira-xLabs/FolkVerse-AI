"""Synthetic support tests; fixture approvals never count as editorial review."""

import copy

import pytest
from sqlalchemy.orm import Session
from test_guide_retrieval import db as db  # noqa: F401

from folkverse.guide_explanations import general_request, validate_hybrid
from folkverse.guide_harness import GuideRequest
from folkverse.guide_retrieval import retrieve
from folkverse.guide_support import general_safe, variants


def proposal(passage, text=None, kind="source_statement"):
    return {
        "locale": passage.language,
        "depth": "beginner",
        "status": "answer",
        "claims": [
            {
                "claim_id": "claim_fact",
                "text": text or passage.text,
                "passage_ids": [passage.passage_id],
                "kind": kind,
            }
        ],
        "sections": [
            {
                "section_id": "section_fact",
                "kind": "evidence",
                "text": "",
                "claim_ids": ["claim_fact"],
            }
        ],
        "related_exhibit_ids": [],
    }


def checked(db, locale="en", payload=None, question=None):
    bundle = retrieve(db, "shadow puppetry" if locale == "en" else "皮影戏", locale)
    request = GuideRequest(
        question=question
        or ("Explain Fuzhou shadow puppetry" if locale == "en" else "介绍复州皮影戏"),
        locale=locale,
        depth="beginner",
    )
    return validate_hybrid(
        payload or proposal(bundle.passages[0]),
        request,
        bundle,
        general_allowed=True,
        names=["Fuzhou", "复州"],
    )


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_supported_variants_are_real_explanations_with_checked_sections(db: Session, locale):
    bundle = retrieve(db, "shadow" if locale == "en" else "皮影", locale)
    p = bundle.passages[0]
    text = next(t for t, method in variants(p).items() if method == "inventory_projection_v1")
    answer = checked(db, locale, proposal(p, text))
    assert answer.status == "answered"
    assert answer.answer_text == text and answer.answer_text != p.text
    assert answer.sections[0].support_label == "sources_checked"
    assert answer.claims[0].support_method == "inventory_projection_v1"


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
@pytest.mark.parametrize(
    "attack",
    [
        "invented_date",
        "classification",
        "mapping",
        "display",
        "locale",
        "duplicate",
        "general_laundering",
        "source_id",
    ],
)
def test_unsupported_claims_cannot_launder_into_general(db, locale, attack):
    bundle = retrieve(db, "shadow" if locale == "en" else "皮影", locale)
    p = bundle.passages[0]
    payload = proposal(p)
    if attack == "invented_date":
        payload["claims"][0]["text"] += " Founded in 1450."
    elif attack == "classification":
        payload["claims"][0]["kind"] = "history"
    elif attack == "mapping":
        payload["sections"][0]["claim_ids"] = ["claim_other"]
    elif attack == "display":
        payload["sections"][0]["text"] = "Extra factual prose."
    elif attack == "locale":
        payload["locale"] = "zh-CN" if locale == "en" else "en"
    elif attack == "duplicate":
        payload["sections"].append(copy.deepcopy(payload["sections"][0]))
    elif attack == "source_id":
        payload["claims"][0]["passage_ids"] = ["invented"]
    else:
        payload["claims"][0]["text"] = "Fuzhou was founded in 1450."
        payload["sections"].append(
            {
                "section_id": "section_extra",
                "kind": "general",
                "text": "Fuzhou was founded in 1450.",
                "claim_ids": [],
            }
        )
    answer = checked(db, locale, payload)
    assert answer.status == "insufficient" and answer.reason == "unsupported_claim"
    assert not answer.claims and not answer.sections


@pytest.mark.parametrize(
    "locale,text",
    [
        (
            "en",
            (
                "Shadow puppetry uses light and silhouettes to tell a story. "
                "Think of a screen as a small stage."
            ),
        ),
        ("zh-CN", "皮影利用灯光和剪影讲故事。可以把幕布想象成一个小舞台。"),
    ],
)
def test_general_explanation_is_labelled_and_borrows_no_sources(db, locale, text):
    payload = {
        "locale": locale,
        "depth": "beginner",
        "status": "answer",
        "claims": [],
        "sections": [
            {"section_id": "section_general", "kind": "general", "text": text, "claim_ids": []}
        ],
        "related_exhibit_ids": [],
    }
    answer = checked(db, locale, payload)
    assert answer.reason == "general_explanation" and not answer.sources
    assert answer.sections[0].support_label == "general_unverified"


@pytest.mark.parametrize(
    "text",
    [
        "Fuzhou dance began long ago.",
        "The craft was invented in 1435.",
        "According to a source, this is true.",
        "Visit https://evil.example.",
        "复州舞蹈始建于明代。",
        "权威确认这些材料能治疗疾病。",
        "A cure uses this dosage.",
    ],
)
def test_general_applicability_guard_rejects_precision_and_false_verification(text):
    assert not general_safe(
        text, "zh-CN" if any(ord(c) > 0x3400 for c in text) else "en", ["Fuzhou", "复州"]
    )


def test_sentence_projection_keeps_uncertainty_and_context(db):
    p = retrieve(db, "shadow", "en").passages[0]
    qualified = p.model_copy(
        update={"text": "A temple was founded in 1625. However, the date is disputed."}
    )
    assert list(variants(qualified)) == [qualified.text]
    plain = p.model_copy(
        update={
            "text": (
                "The museum presents industrial history. "
                "Factory buildings display production machinery."
            )
        }
    )
    assert (
        variants(plain)["Factory buildings display production machinery."] == "complete_sentence_v1"
    )


def test_exact_citation_is_not_enough_to_answer_a_different_date(db):
    assert (
        checked(db, question="When was Fuzhou shadow puppetry founded?").reason
        == "unsupported_claim"
    )


def test_general_request_cannot_override_specific_local_scope():
    assert not general_request(
        GuideRequest(question="When was the Shenyang palace founded?"), ["Shenyang"], False
    )
    assert general_request(GuideRequest(question="What is shadow puppetry?"), ["Shenyang"], False)


def test_single_chinese_sentence_keeps_complete_passage_support_method(db):
    p = retrieve(db, "皮影", "zh-CN").passages[0]
    assert variants(p)[p.text] == "complete_reviewed_passage"


@pytest.mark.parametrize(
    "locale,question", [("en", "What does silhouette mean?"), ("zh-CN", "剪影是什么意思？")]
)
def test_broad_glossary_definition_uses_labelled_general_mode(locale, question):
    assert general_request(
        GuideRequest(question=question, locale=locale), ["Fuzhou shadow puppetry"], False
    )


def test_deeper_chinese_general_section_cannot_invent_local_style(db):
    bundle = retrieve(db, "皮影", "zh-CN")
    payload = proposal(bundle.passages[0])
    payload["sections"].append(
        {
            "section_id": "section_context",
            "kind": "general",
            "text": "复州皮影戏在地方上形成了自己的唱腔和雕刻风格。",
            "claim_ids": [],
        }
    )
    assert checked(db, "zh-CN", payload).reason == "unsupported_claim"


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_statement_reference_preserves_server_text_and_attribution(db, locale):
    bundle = retrieve(db, "shadow" if locale == "en" else "皮影", locale)
    payload = proposal(bundle.passages[0])
    payload["claims"][0].update(text="", statement_id="statement_0")
    answer = checked(db, locale, payload)
    assert answer.status == "answered"
    assert answer.claims[0].text == bundle.passages[0].text


@pytest.mark.parametrize("attack", ["unknown", "wrong_text", "wrong_passage", "wrong_kind"])
def test_statement_reference_cannot_bypass_support(db, attack):
    bundle = retrieve(db, "shadow", "en")
    payload = proposal(bundle.passages[0])
    payload["claims"][0].update(text="", statement_id="statement_0")
    if attack == "unknown":
        payload["claims"][0]["statement_id"] = "statement_999"
    elif attack == "wrong_text":
        payload["claims"][0]["text"] = "Invented local history."
    elif attack == "wrong_passage":
        payload["claims"][0]["passage_ids"] = ["another_passage"]
    else:
        payload["claims"][0]["kind"] = "folklore"
    assert checked(db, payload=payload).reason == "unsupported_claim"


def test_original_objects_are_a_general_concept_not_an_origin_date_request():
    assert general_request(
        GuideRequest(question="What is the difference between an original object and a replica?"),
        [],
        False,
    )
    assert not general_request(GuideRequest(question="Where did this object originate?"), [], False)


@pytest.mark.parametrize(
    "question", ["什么是考古学？", "什么是书法？", "什么是玉雕？", "什么是化石？", "什么是湿地？"]
)
def test_chinese_definition_prefix_accepts_generic_concepts(question):
    assert general_request(
        GuideRequest(question=question, locale="zh-CN", depth="beginner"), ["辽宁", "沈阳"], False
    )


def test_chinese_definition_prefix_preserves_local_and_precise_fact_boundary():
    for question in ["什么是沈阳故宫？", "什么是辽宁最早的书法？", "什么是今天的开放时间？"]:
        assert not general_request(
            GuideRequest(question=question, locale="zh-CN", depth="beginner"),
            ["辽宁", "沈阳"],
            False,
        )
