"""Independent deterministic claim support; never trust model self-assessed entailment."""

import re
from typing import Literal

from folkverse.guide_retrieval import EvidencePassage, Locale

SUPPORT_VERSION = "deterministic-support-v1"
SupportMethod = Literal[
    "complete_reviewed_passage",
    "reviewed_variant_v1",
    "complete_sentence_v1",
    "inventory_projection_v1",
    "official_metadata_projection_v1",
    "machine_source_summary_v1",
]


def variants(passage: EvidencePassage) -> dict[str, SupportMethod]:
    if passage.evidence_origin == "official_lookup":
        method: SupportMethod = (
            "machine_source_summary_v1"
            if passage.review_id == "machine_source_assessed_v1"
            else "official_metadata_projection_v1"
        )
        return {text: method for text in passage.statement_variants}
    result: dict[str, SupportMethod] = {passage.text: "complete_reviewed_passage"}
    result.update({text: "reviewed_variant_v1" for text in passage.statement_variants})
    # Whole sentences preserve dates, negation, qualifying clauses and attribution.
    # Do not split abbreviations, semicolons, or fragments out of sentences.
    sentences = re.split(r"(?<=[。！？])|(?<=[.!?])\s+(?=[A-Z])", passage.text)
    qualified = re.search(
        r"however|although|uncertain|disputed|alleged|possibly|unverified|"
        r"according to|legend|belief|传说|据说|争议|可能|不确定|然而|但|尚未|"
        r"(?:Dr|Mr|Mrs|Ms|Prof|St|No|vs|etc)\.",
        passage.text,
        re.I,
    )
    if len(sentences) > 1 and not qualified:
        for sentence in sentences:
            text = sentence.strip()
            if (
                len(text) >= 15
                and text != passage.text
                and text[-1:] in ".!?。！？"
                and not re.match(r"(?:It|They|This|That|He|She)\b|^(?:它|该|其)", text)
            ):
                result[text] = "complete_sentence_v1"
    if passage.language == "en":
        match = re.fullmatch(r"(.+?) is listed as (.+?) (?:from|in) (.+?)\.", passage.text)
        if match:
            title, category, location = match.groups()
            result[
                f"The inventory records {title} under {category}, "
                f"with {location} as the listed locality."
            ] = "inventory_projection_v1"
            result[f"{title}: category — {category}; listed locality — {location}."] = (
                "inventory_projection_v1"
            )
    else:
        match = re.fullmatch(r"(.+?)在.+?名录中列为(.+?)申报的(.+?)项目。", passage.text)
        if match:
            title, location, category = match.groups()
            result[f"名录把{title}列为{category}，申报地区为{location}。"] = (
                "inventory_projection_v1"
            )
            result[f"{title}：名录类别为{category}；申报地区为{location}。"] = (
                "inventory_projection_v1"
            )
        simple = re.fullmatch(r"(.+?)列入(.+?)，地区为(.+?)。", passage.text)
        if simple:
            title, category, location = simple.groups()
            result[f"{title}：名录类别为{category}；名录所列地区为{location}。"] = (
                "inventory_projection_v1"
            )
    return result


def language_matches(text: str, locale: Locale) -> bool:
    chinese = len(re.findall(r"[\u3400-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return chinese >= 6 if locale == "zh-CN" else latin >= 8 and chinese <= max(20, latin // 2)


def general_safe(text: str, locale: Locale, forbidden_names: list[str]) -> bool:
    """Applicability guard, not a truth score. General sections remain unverified."""
    if not language_matches(text, locale) or len(text) > 2400:
        return False
    if re.search(
        r"https?://|www\.|\]\(|\[claim|\[source|\d|[零〇一二三四五六七八九十百千]+年", text, re.I
    ):
        return False
    if re.search(
        r"originated|founded|dates? back|born in|according to|the source says|cures?|dosage|"
        r"legal advice|guaranteed|verified|officially|named|dollars|人民币|美元|"
        r"起源于|始建于|发源于|最早|据.{0,12}记载|治疗|剂量|保证|已核实|已验证|权威确认",
        text,
        re.I,
    ):
        return False
    # Yuan is also a surname (for example Qu Yuan). Reject price/amount uses, not names.
    if re.search(
        r"\b(?:costs?|priced?|fees?|pay|spend|payment)\b[^.!?]{0,30}\byuan\b|"
        r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
        r"twenty|thirty|forty|fifty|hundred|thousand|million|several|a few)\s+yuan\b",
        text,
        re.I,
    ):
        return False
    normalized = text.casefold()
    return not any(name.casefold() in normalized for name in forbidden_names if len(name) >= 2)
