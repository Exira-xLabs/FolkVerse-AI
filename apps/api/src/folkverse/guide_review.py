"""Public evaluation review worksheets. No human ratings are fabricated automatically."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from folkverse.guide_embeddings import file_hash
from folkverse.guide_evaluation import metric

HumanDimension = Literal["historical_correctness", "explanatory_clarity", "bilingual_faithfulness"]


class HumanRating(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    dimension: HumanDimension
    unit_id: str
    case_ids: list[str] = Field(min_length=1)
    passed: bool | None = None
    reviewer: str | None = None
    reviewed_at: str | None = None
    rationale: str | None = None
    basis: str | None = None
    attest_human_review: bool = False

    @model_validator(mode="after")
    def complete_rating(self) -> "HumanRating":
        if self.passed is not None:
            if not self.attest_human_review or any(
                not value or not value.strip()
                for value in (self.reviewer, self.reviewed_at, self.rationale, self.basis)
            ):
                raise ValueError("Scored judgments require an actual attributed human review")
            assert self.reviewed_at is not None
            if datetime.fromisoformat(self.reviewed_at).tzinfo is None:
                raise ValueError("Review timestamp must include timezone")
        return self


class HumanReviews(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    version: Literal["guide-human-review-v1"]
    run_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    run_mode: Literal["fixture", "live"]
    instructions: str
    ratings: list[HumanRating]


def template(run_path: Path) -> HumanReviews:
    run = json.loads(run_path.read_text())
    if run.get("run_status") != "completed" or run.get("mode") not in {"fixture", "live"}:
        raise ValueError("Review requires a completed evaluation run")
    answered = [case for case in run["cases"] if case["actual_status"] == "answered"]
    ratings = []
    families: dict[str, list[dict[str, Any]]] = {}
    for case in answered:
        for dimension in ("historical_correctness", "explanatory_clarity"):
            ratings.append(
                HumanRating(dimension=dimension, unit_id=case["id"], case_ids=[case["id"]])
            )
        families.setdefault(case["family"], []).append(case)
    for family, pair in families.items():
        if {case["locale"] for case in pair} == {"en", "zh-CN"}:
            ratings.append(
                HumanRating(
                    dimension="bilingual_faithfulness",
                    unit_id=family,
                    case_ids=sorted(case["id"] for case in pair),
                )
            )
    return HumanReviews(
        version="guide-human-review-v1",
        run_sha256=file_hash(run_path),
        run_mode=run["mode"],
        instructions="Leave passed/reviewer/time/rationale/basis empty until actual human review. "
        "Apply the evaluation rubric, record independent basis, and attest human review. "
        "Reviewing a fixture cannot certify real provider expertise.",
        ratings=ratings,
    )


def grade(run_path: Path, review_path: Path) -> dict[str, Any]:
    expected = template(run_path)
    reviews = HumanReviews.model_validate_json(review_path.read_bytes())
    if reviews.run_sha256 != expected.run_sha256 or reviews.run_mode != expected.run_mode:
        raise ValueError("Reviews belong to a different run")
    units = {(r.dimension, r.unit_id): r.case_ids for r in expected.ratings}
    seen = set()
    values: dict[str, list[bool]] = {
        name: []
        for name in ("historical_correctness", "explanatory_clarity", "bilingual_faithfulness")
    }
    for rating in reviews.ratings:
        key = (rating.dimension, rating.unit_id)
        if key in seen or key not in units or rating.case_ids != units[key]:
            raise ValueError("Unknown, duplicate or mismatched human rating unit")
        seen.add(key)
        if rating.passed is not None:
            values[rating.dimension].append(rating.passed)
    if seen != set(units):
        raise ValueError("Review worksheet dropped expected units")
    scores = {
        name: {
            **metric(items, "Attributed human pass/fail judgments"),
            "pending": sum(r.dimension == name for r in expected.ratings) - len(items),
        }
        for name, items in values.items()
    }
    return {
        "run_sha256": expected.run_sha256,
        "review_sha256": file_hash(review_path),
        "run_mode": expected.run_mode,
        "human_dimensions": scores,
        "expert_quality_verified": False,
        "note": "Recorded judgments remain attributable; this tool cannot verify reviewer identity "
        "or certify independent expertise, production integration or missing phase gates.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["template", "grade"])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.run.resolve():
        parser.error("Review output cannot overwrite its evaluation run")
    if args.reviews and args.output.resolve() == args.reviews.resolve():
        parser.error("Grading output cannot overwrite the attributed review worksheet")
    try:
        if args.command == "template":
            result = template(args.run).model_dump(mode="json")
        else:
            if not args.reviews:
                parser.error("--reviews is required for grading")
            result = grade(args.run, args.reviews)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    except (ValueError, OSError, KeyError):
        parser.exit(2, "Invalid or changed evaluation/review data; no score generated.\n")
    print("Review worksheet/summary written; no expert-quality certification granted.")


if __name__ == "__main__":
    main()
