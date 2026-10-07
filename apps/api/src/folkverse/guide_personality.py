"""Non-factual conversation and lossless inventory explanations, never free-form claims."""

import json
import re
import secrets
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from folkverse.config import ROOT

POLICY: dict[str, Any] = json.loads(
    (ROOT / "packages/contracts/src/jinyao-policy.json").read_text()
)
PERSONALITY_VERSION: str = POLICY["version"]
SocialIntent = Literal[
    "greeting", "identity", "thanks", "start", "goodbye", "help", "empathy", "clarification"
]


class ConversationPair(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    user: str = Field(min_length=1, max_length=2000, repr=False)
    assistant: str = Field(min_length=1, max_length=4000, repr=False)


class ConversationChoice(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    locale: Literal["en", "zh-CN"]
    intent: SocialIntent
    opening_id: int = Field(ge=0)
    invitation_id: int | None = Field(default=None, ge=0)


class ConversationRoute(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    locale: Literal["en", "zh-CN"]
    intent: SocialIntent | Literal["cultural"]
    opening_id: int | None = Field(ge=0)
    invitation_id: int | None = Field(ge=0)


def policy_options(intent: str, locale: str) -> dict[str, Any]:
    return {
        "openings": {str(i): text for i, text in enumerate(POLICY["conversation"][intent][locale])},
        "invitations": {str(i): text for i, text in enumerate(POLICY["invitations"][locale])},
    }


def conversation_options(
    intent: str, locale: str, history: list[ConversationPair]
) -> dict[str, Any]:
    """Exclude recently used wording; history is context, never factual evidence."""
    recent = "\n".join(pair.assistant for pair in history[-2:])
    options = policy_options(intent, locale)
    openings = options["openings"]
    invitations = options["invitations"]
    if intent == "greeting":
        openings.pop("0" if history else "3", None)
    available = {key: text for key, text in openings.items() if text not in recent}
    questions = {key: text for key, text in invitations.items() if text not in recent}
    if not history:
        questions.pop("5", None)
    ordered = list((available or openings).items())
    secrets.SystemRandom().shuffle(ordered)
    question_order = list(questions.items())
    secrets.SystemRandom().shuffle(question_order)
    return {"openings": dict(ordered), "invitations": dict(question_order)}


def render_conversation(choice: ConversationChoice, options: dict[str, Any]) -> str:
    opening = options["openings"].get(str(choice.opening_id))
    question = options["invitations"].get(str(choice.invitation_id))
    requires_question = choice.intent in {"greeting", "start", "help", "empathy", "clarification"}
    if not opening or (requires_question and question is None):
        raise ValueError("Invalid conversation selection")
    if choice.intent in {"thanks", "goodbye", "identity"} and choice.invitation_id is not None:
        raise ValueError("This turn should not require a follow-up question")
    return str(opening) + (" " + str(question) if question else "")


def social_intent(question: str) -> SocialIntent | None:
    # Full-match only: a greeting followed by a cultural question still needs evidence.
    q = unicodedata.normalize("NFKC", question).casefold().strip().rstrip(".!?。！？ ")
    patterns: dict[SocialIntent, str] = {
        "greeting": (
            r"(?:h+i+|h+e+y+|he+l+o+|hello there|hi there|good (?:morning|afternoon|evening)|"
            r"你好(?:呀|啊|锦瑶)?|您好|嗨|哈喽|👋)(?:[ ,，]+jinyao|[ ,，]*锦瑶)?(?:[ !！]*👋)?"
        ),
        "goodbye": r"(?:bye(?: bye)?|goodbye|see you(?: later)?|再见|拜拜|下次见)",
        "help": r"(?:i (?:do not|don't|dont) understand|i'?m confused|我不明白|没看懂|不懂)",
        "empathy": r"(?:i'?m (?:bored|tired)|i am (?:bored|tired)|好无聊|我累了|无聊)",
        "clarification": r"(?:what|huh|嗯|什么意思)",
    }
    for intent, pattern in patterns.items():
        if re.fullmatch(pattern, q):
            return intent
    phrases: dict[SocialIntent, set[str]] = {
        "greeting": {"hi", "hello", "hey", "hi jinyao", "hello jinyao", "你好", "您好", "锦瑶你好"},
        "identity": {"who are you", "what is your name", "你是谁", "你叫什么名字"},
        "thanks": {"thanks", "thank you", "thanks jinyao", "谢谢", "谢谢你", "谢谢锦瑶"},
        "start": {"where do i begin", "how do i start", "从哪里开始", "怎么开始"},
    }
    for intent, values in phrases.items():
        if q in values:
            return intent
    return None


def strip_social_prefix(question: str) -> str:
    """Remove only a greeting prefix; keep the entire factual request for validation."""
    return (
        re.sub(
            r"^(?:hi|hello|hey|你好|您好|嗨)(?:[ ,]+jinyao|[， ]*锦瑶)?[!！,，.。 ]+",
            "",
            question.strip(),
            count=1,
            flags=re.IGNORECASE,
        )
        or question
    )


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


def canonical_followup(question: str) -> str:
    """Only whole-message follow-ups; never discard an attached factual request."""
    q = unicodedata.normalize("NFKC", question).casefold().strip().rstrip(".!?。！？ ")
    q = re.sub(r"^(?:please |could you |can you )", "", q)
    q = re.sub(r"(?: please|，?谢谢)$", "", q)
    variants = {
        "explain that simply": {
            "make it simpler",
            "simplify that",
            "explain more simply",
            "i don't understand",
            "i do not understand",
        },
        "say that in chinese": {
            "reply in chinese",
            "answer in chinese",
            "speak chinese",
            "中文",
            "请用中文回答",
            "用中文回答",
            "用中文解释",
        },
        "say that in english": {
            "reply in english",
            "answer in english",
            "speak english",
            "english",
            "请用英文回答",
            "用英文回答",
            "用英语回答",
            "用英文解释",
        },
        "go deeper": {
            "tell me more",
            "explain in more detail",
            "more detail",
            "再详细一点",
            "请详细解释",
        },
        "解释得简单一点": {"我不明白", "没看懂", "不懂", "请说简单一点", "简单解释一下"},
    }
    for canonical, phrases in variants.items():
        if q == canonical or q in phrases:
            return canonical
    return q
