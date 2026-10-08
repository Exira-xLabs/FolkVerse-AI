"""Deterministic, pure route selection over already-published exhibit metadata.

The planner never reads the database, never calls a model and never invents durations. It
receives one ``Candidate`` per strictly published exhibit (id, stored minutes, themes,
regions, available locales) and returns an ordered selection whose total obeys the requested
5-60 minute budget.

Determinism rules (all documented, all covered by tests):

* Candidates are processed in stable exhibit-ID order, so the result depends only on their
  set, never on database or request order.
* Eligibility is strict: requested locale text must exist, the optional region must be listed,
  and every selected stop must share a case-folded theme with ``interests`` when interests are
  given. A requested ``start_exhibit_id`` is included only if it satisfies the same criteria
  and fits the time; otherwise it is left out with an explicit notice.
* Fresh (not in ``novelty_exhibit_ids``) stops outrank previously seen ones only among routes
  that use the same number of minutes. Novelty is explicit request input; nothing is inferred,
  and no novelty claim is ever made when the visitor supplied no such list.
* Ties are broken by interest overlap, theme coverage, stop count and finally exhibit ID, so
  two runs over the same corpus always produce the same route.
* Display order spreads themes: the best-ranked stop that introduces an unused theme goes
  first, and the requested starting exhibit always goes first.

Selection is a bounded deterministic heuristic over exact minute budgets. It always obeys the
time limit and is reproducible, but it is not claimed to be a global optimum.

Reason codes are the frozen vocabulary of ``folkverse.journey_explanations``; the API layer
renders localized text from them.
"""

from dataclasses import dataclass
from typing import Literal

from folkverse.journey_explanations import ALLOWED_REASON_CODES, MAX_STOPS, ReasonCode

MIN_DURATION = 5
MAX_DURATION = 60
MAX_INTERESTS = 8

NoticeCode = Literal[
    "no_candidates",
    "no_fit",
    "partial_fill",
    "start_too_long",
    "start_ineligible",
    "start_filtered",
    "cap",
    "stops_withdrawn",
    "stops_trimmed",
]


@dataclass(frozen=True)
class Candidate:
    """One published exhibit; localized prose stays in the API layer."""

    id: str
    estimated_minutes: int
    themes: tuple[str, ...]
    region_ids: tuple[str, ...]
    locales: tuple[str, ...]


@dataclass(frozen=True)
class Selection:
    candidate: Candidate
    codes: tuple[ReasonCode, ...]


@dataclass(frozen=True)
class Plan:
    selections: tuple[Selection, ...]
    total_minutes: int
    notice: str | None
    notice_codes: tuple[NoticeCode, ...]


def normalise_interests(interests: list[str] | tuple[str, ...]) -> frozenset[str]:
    return frozenset(item.strip().casefold() for item in interests if item.strip())


def matches_interests(
    candidate: Candidate, interests: frozenset[str] | set[str]
) -> bool:
    """Interest eligibility, exactly as selection applies it: case-folded theme overlap."""
    return not interests or bool(interests & _themes(candidate))


def start_notice_code(
    candidate: Candidate | None,
    *,
    interests: frozenset[str] | set[str],
    locale: str,
    region_id: str | None,
    duration_minutes: int,
) -> NoticeCode | None:
    """The single truthful notice code for a declared starting exhibit.

    ``candidate`` is the requested exhibit as it is selectable *right now* (published, usable
    minutes, with an approved source), or ``None`` when it is not selectable at all. ``None`` is
    returned when nothing is wrong with it, so a stale code is dropped as soon as the exhibit
    fits again instead of keeping a claim that is no longer true.
    """
    if candidate is None:
        return "start_ineligible"
    if locale not in candidate.locales or (
        region_id is not None and region_id not in candidate.region_ids
    ):
        return "start_ineligible"
    if candidate.estimated_minutes > duration_minutes:
        return "start_too_long"
    if not matches_interests(candidate, interests):
        return "start_filtered"
    return None


def _themes(candidate: Candidate) -> frozenset[str]:
    return frozenset(theme.strip().casefold() for theme in candidate.themes if theme.strip())


def _seen(candidate: Candidate, novelty: frozenset[str] | set[str]) -> bool:
    return candidate.id.casefold() in novelty


def reason_codes(
    candidate: Candidate,
    *,
    interests: frozenset[str] | set[str],
    novelty_exhibit_ids: frozenset[str] | set[str],
    start_exhibit_id: str | None,
) -> tuple[ReasonCode, ...]:
    """Deterministic server-authored reason codes, in the frozen canonical order."""
    novelty = {item.casefold() for item in novelty_exhibit_ids}
    chosen: set[ReasonCode] = {"time_fit"}
    if start_exhibit_id is not None and candidate.id == start_exhibit_id:
        chosen.add("starting_exhibit")
    elif interests & _themes(candidate):
        chosen.add("theme_match")
    elif novelty and not _seen(candidate, novelty):
        chosen.add("new_discovery")
    else:
        chosen.add("collection_discovery")
    return tuple(code for code in ALLOWED_REASON_CODES if code in chosen)


def allowed_codes(
    candidate: Candidate,
    *,
    interests: frozenset[str] | set[str],
    novelty_exhibit_ids: frozenset[str] | set[str],
    start_exhibit_id: str | None,
) -> tuple[ReasonCode, ...]:
    """Codes the exploration model may choose from for this stop; only statements that are true.

    ``new_discovery`` means the stop is not one the visitor listed as already seen, so it is
    never offered when the visitor supplied no such list, and never offered for a repeat.
    ``collection_discovery`` covers a stop that was not selected primarily by a listed
    interest, or one the visitor has already seen.
    """
    novelty = {item.casefold() for item in novelty_exhibit_ids}
    allowed: set[ReasonCode] = {"time_fit"}
    matched = bool(interests & _themes(candidate))
    if start_exhibit_id is not None and candidate.id == start_exhibit_id:
        allowed.add("starting_exhibit")
    if matched:
        allowed.add("theme_match")
    if novelty and not _seen(candidate, novelty):
        allowed.add("new_discovery")
    if not matched or _seen(candidate, novelty):
        allowed.add("collection_discovery")
    return tuple(code for code in ALLOWED_REASON_CODES if code in allowed)


def _rank_key(
    candidate: Candidate, interests: frozenset[str], novelty: frozenset[str]
) -> tuple[int, int, str]:
    return (
        1 if _seen(candidate, novelty) else 0,
        -len(interests & _themes(candidate)),
        candidate.id,
    )


def _key(
    chosen: tuple[Candidate, ...], interests: frozenset[str], novelty: frozenset[str]
) -> tuple[int, int, int, int, int, tuple[str, ...]]:
    used = sum(candidate.estimated_minutes for candidate in chosen)
    fresh = sum(1 for candidate in chosen if not _seen(candidate, novelty))
    overlap = sum(len(interests & _themes(candidate)) for candidate in chosen)
    themes = len({theme for candidate in chosen for theme in _themes(candidate)})
    return (-used, -fresh, -overlap, -themes, -len(chosen), tuple(sorted(c.id for c in chosen)))


def _select(
    pool: list[Candidate],
    capacity: int,
    interests: frozenset[str],
    novelty: frozenset[str],
    max_items: int = MAX_STOPS,
) -> tuple[Candidate, ...]:
    """Bounded knapsack over exact minutes: one best state per capacity, stable ID order."""
    if capacity < 1 or max_items < 1:
        return ()
    best: dict[int, tuple[tuple[int, int, int, int, int, tuple[str, ...]], tuple[Candidate, ...]]]
    best = {0: (_key((), interests, novelty), ())}
    for candidate in sorted(pool, key=lambda item: item.id):
        if candidate.estimated_minutes < 1:
            continue
        additions: dict[int, list[tuple[Candidate, ...]]] = {}
        for used, (_, chosen) in list(best.items()):
            if len(chosen) >= max_items:
                continue
            grown = used + candidate.estimated_minutes
            if grown > capacity:
                continue
            additions.setdefault(grown, []).append((*chosen, candidate))
        for grown, options in additions.items():
            for chosen in options:
                key = _key(chosen, interests, novelty)
                current = best.get(grown)
                if current is None or key < current[0]:
                    best[grown] = (key, chosen)
    return min(best.values(), key=lambda entry: entry[0])[1]


def _order(
    chosen: tuple[Candidate, ...],
    start: Candidate | None,
    interests: frozenset[str],
    novelty: frozenset[str],
) -> tuple[Candidate, ...]:
    if not chosen:
        return ()
    ranked = sorted(chosen, key=lambda item: _rank_key(item, interests, novelty))
    ordered: list[Candidate] = []
    used: set[str] = set()
    if start is not None and start in chosen:
        ordered.append(start)
        used.update(_themes(start))
    remaining = [candidate for candidate in ranked if candidate != start]
    while remaining:
        diverse = [c for c in remaining if _themes(c) - used] or remaining
        pick = diverse[0]
        ordered.append(pick)
        used.update(_themes(pick))
        remaining.remove(pick)
    return tuple(ordered)


def render_notice(
    codes: tuple[NoticeCode, ...] | list[NoticeCode],
    locale: str,
    *,
    duration_minutes: int,
    total_minutes: int = 0,
    withdrawn: int = 0,
    trimmed: int = 0,
    start_minutes: int = 0,
    max_stops: int = MAX_STOPS,
) -> str | None:
    """Render machine notice codes as localized text; unknown codes are ignored."""
    language = "zh-CN" if locale == "zh-CN" else "en"
    texts: list[str] = []
    for code in codes:
        if code == "no_candidates":
            texts.append(
                "目前没有已发布展品符合这些兴趣或地区。"
                if language == "zh-CN"
                else "No published exhibit matches these interests in this region yet."
            )
        elif code == "no_fit":
            texts.append(
                f"没有已发布展品的时长能放入你要求的 {duration_minutes} 分钟路线。"
                if language == "zh-CN"
                else f"No published exhibit fits the {duration_minutes}-minute route you requested."
            )
        elif code == "partial_fill":
            texts.append(
                f"已发布展品的总时长为你要求的 {duration_minutes} 分钟中的 {total_minutes} 分钟。"
                if language == "zh-CN"
                else (
                    f"Published exhibits cover {total_minutes} of the {duration_minutes} minutes "
                    "you requested."
                )
            )
        elif code == "start_too_long":
            texts.append(
                (
                    f"你选择的起点展品需要 {start_minutes} 分钟，"
                    f"超过 {duration_minutes} 分钟的路线，因此未包含。"
                )
                if language == "zh-CN"
                else (
                    f"Your starting exhibit needs {start_minutes} minutes, longer than the "
                    f"{duration_minutes}-minute route, so it was left out."
                )
            )
        elif code == "start_ineligible":
            texts.append(
                "你选择的起点展品在该语言和地区下未发布，因此未包含。"
                if language == "zh-CN"
                else (
                    "Your starting exhibit is not published for this language and region, so it "
                    "was left out."
                )
            )
        elif code == "start_filtered":
            texts.append(
                "你选择的起点展品不符合你所选的兴趣，因此未包含。"
                if language == "zh-CN"
                else (
                    "Your starting exhibit does not match the interests you selected, so it was "
                    "left out."
                )
            )
        elif code == "cap":
            texts.append(
                f"路线最多包含 {max_stops} 个停靠点。"
                if language == "zh-CN"
                else f"The route is limited to {max_stops} stops."
            )
        elif code == "stops_withdrawn":
            texts.append(
                f"{withdrawn} 个已保存站点不再发布或在该语言下不可用，已移除。"
                if language == "zh-CN"
                else (
                    f"{withdrawn} saved stop(s) are no longer published or not available in this "
                    "language and were removed."
                )
            )
        elif code == "stops_trimmed":
            texts.append(
                f"为将路线控制在 {duration_minutes} 分钟内，已移除 {trimmed} 个站点。"
                if language == "zh-CN"
                else (
                    f"{trimmed} stop(s) were removed to keep the route within your "
                    f"{duration_minutes}-minute limit."
                )
            )
    return " ".join(texts) if texts else None


def plan(
    candidates: list[Candidate] | tuple[Candidate, ...],
    *,
    interests: list[str] | tuple[str, ...],
    locale: str,
    duration_minutes: int,
    region_id: str | None = None,
    novelty_exhibit_ids: list[str] | tuple[str, ...] = (),
    start_exhibit_id: str | None = None,
) -> Plan:
    """Select an ordered, time-bounded route; fewer honest stops beat invented ones."""
    duration = max(MIN_DURATION, min(MAX_DURATION, int(duration_minutes)))
    interest_set = normalise_interests(interests)
    novelty = frozenset(item.strip().casefold() for item in novelty_exhibit_ids if item.strip())
    codes: list[NoticeCode] = []

    # Duplicate or malformed caller input never becomes duplicate stops: sorting by the whole
    # value before de-duplication keeps the result a pure function of the candidate multiset.
    unique: dict[str, Candidate] = {}
    for candidate in sorted(
        candidates,
        key=lambda item: (
            item.id,
            item.estimated_minutes,
            item.themes,
            item.region_ids,
            item.locales,
        ),
    ):
        if not isinstance(candidate.id, str) or not candidate.id.strip():
            continue
        if candidate.estimated_minutes < 1:
            continue
        unique.setdefault(candidate.id, candidate)
    base = [
        candidate
        for candidate in unique.values()
        if locale in candidate.locales
        and (region_id is None or region_id in candidate.region_ids)
    ]
    eligible = [
        candidate for candidate in base if matches_interests(candidate, interest_set)
    ]
    start = None
    if start_exhibit_id is not None:
        requested = unique.get(start_exhibit_id)
        code = start_notice_code(
            requested,
            interests=interest_set,
            locale=locale,
            region_id=region_id,
            duration_minutes=duration,
        )
        if code is not None:
            codes.append(code)
        elif requested is not None:
            start = requested

    capacity = duration - start.estimated_minutes if start is not None else duration
    max_items = MAX_STOPS - (1 if start is not None else 0)
    pool = [candidate for candidate in eligible if candidate != start]
    chosen = _select(pool, capacity, interest_set, novelty, max_items)
    all_chosen = (start, *chosen) if start is not None else chosen
    total = sum(candidate.estimated_minutes for candidate in all_chosen)

    if not all_chosen:
        codes.append("no_candidates" if not eligible else "no_fit")
    else:
        if total < duration:
            codes.append("partial_fill")
        if len(all_chosen) >= MAX_STOPS and len(eligible) > MAX_STOPS:
            codes.append("cap")

    ordered = _order(all_chosen, start, interest_set, novelty)
    selections = tuple(
        Selection(
            candidate=candidate,
            codes=reason_codes(
                candidate,
                interests=interest_set,
                novelty_exhibit_ids=novelty,
                start_exhibit_id=start_exhibit_id,
            ),
        )
        for candidate in ordered
    )
    notice_codes = tuple(dict.fromkeys(codes))
    notice = render_notice(
        notice_codes,
        locale,
        duration_minutes=duration,
        total_minutes=total,
        start_minutes=start.estimated_minutes if start is not None else 0,
    )
    return Plan(
        selections=selections, total_minutes=total, notice=notice, notice_codes=notice_codes
    )
