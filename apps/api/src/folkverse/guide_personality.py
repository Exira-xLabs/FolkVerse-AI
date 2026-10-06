"""Non-factual conversation and lossless inventory explanations, never free-form claims."""

import json
import re
import unicodedata
from typing import Any

from folkverse.config import ROOT

POLICY: dict[str, Any] = json.loads(
    (ROOT / "packages/contracts/src/jinyao-policy.json").read_text()
)
PERSONALITY_VERSION: str = POLICY["version"]


def social_intent(question: str) -> str | None:
    # Full-match only: a greeting followed by a cultural question still needs evidence.
    q = unicodedata.normalize("NFKC", question).casefold().strip().rstrip(".!?。！？")
    phrases = {
        "greeting": {"hi", "hello", "hey", "hi jinyao", "hello jinyao", "你好", "您好", "锦瑶你好"},
        "identity": {"who are you", "what is your name", "你是谁", "你叫什么名字"},
        "thanks": {"thanks", "thank you", "thanks jinyao", "谢谢", "谢谢你", "谢谢锦瑶"},
        "start": {"where do i begin", "how do i start", "从哪里开始", "怎么开始"},
    }
    return next((intent for intent, values in phrases.items() if q in values), None)


def inventory_projection(text: str, locale: str, depth: str) -> str | None:
    """Reorder only a complete single-sentence listing, retaining its source qualifier.

    This is a bounded grammar, not semantic verification. Other wording stays extractive.
    No glossary, dates, historical importance or origin inference is introduced.
    """
    if depth not in {"beginner", "deeper"}:
        return None
    if locale == "en":
        match = re.fullmatch(
            r"(?P<title>[A-Za-z -]+) is listed as (?P<category>[A-Za-z -]+) "
            r"(?:from|in) (?P<location>[A-Z][a-z]+(?:[ ,'-]+[A-Z][a-z]+)*)\.",
            text,
        )
    else:
        match = re.fullmatch(
            r"(?P<title>[\u3400-\u9fff]+)在[\u3400-\u9fff]+名录中列为"
            r"(?P<location>[\u3400-\u9fff]+)申报的(?P<category>[\u3400-\u9fff]+)项目。",
            text,
        )
    if match is None:
        return None
    template: str = POLICY["projection"][locale][depth]
    return template.format(**match.groupdict())
