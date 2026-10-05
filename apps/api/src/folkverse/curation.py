"""Local operator CLI; review is never exposed as an unauthenticated web endpoint."""

import argparse
import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from folkverse.config import ROOT, Settings
from folkverse.content import KINDS, counts, review_record
from folkverse.content_models import ArtifactExhibit, ClaimEvidence, ExhibitRegion, Review
from folkverse.database import make_engine
from folkverse.met_import import BASE, ImportFailure, import_object, search


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("counts")
    commands.add_parser("ledger")
    commands.add_parser("seed")
    inspect = commands.add_parser("inspect")
    inspect.add_argument("kind", choices=KINDS)
    inspect.add_argument("id")
    review = commands.add_parser("review")
    review.add_argument("kind", choices=KINDS)
    review.add_argument("id")
    review.add_argument(
        "--decision", required=True, choices=["approved", "draft", "rejected", "withdrawn"]
    )
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", required=True)
    review.add_argument("--attest-human-review", action="store_true")
    review.add_argument("--clear-rights", action="store_true")
    ingest = commands.add_parser("import-met")
    ingest.add_argument("--ids", type=int, nargs="+")
    ingest.add_argument("--query", default="China")
    ingest.add_argument("--offset", type=int, default=0)
    ingest.add_argument("--limit", type=int, default=30)
    ingest.add_argument("--refresh", action="store_true")
    ingest.add_argument("--base-url", default=BASE)
    ingest.add_argument(
        "--report", type=Path, default=ROOT / "report/evidence/phase02/met-import.json"
    )
    commands.add_parser("export")
    restore_parser = commands.add_parser("restore-manifest")
    restore_parser.add_argument("--file", type=Path, default=ROOT / "data/manifests/corpus.json")
    args = parser.parse_args()
    engine = make_engine(Settings())
    with Session(engine) as db:
        result: Any
        if args.command == "seed":
            from folkverse.seed_content import seed

            seed(db)
            db.commit()
            result = counts(db)
        elif args.command == "restore-manifest":
            from folkverse.content_snapshot import restore

            try:
                restore(db, args.file)
                db.commit()
                result = {"restored": str(args.file), "counts": counts(db)}
            except (ValueError, KeyError, OSError) as exc:
                db.rollback()
                parser.error(str(exc))
        elif args.command == "counts":
            result = counts(db)
        elif args.command == "ledger":
            result = [
                {k: v for k, v in vars(r).items() if not k.startswith("_")}
                for r in db.scalars(select(Review).order_by(Review.reviewed_at))
            ]
        elif args.command == "inspect":
            row = db.get(KINDS[args.kind], args.id)
            if row is None:
                parser.error("Record not found")
            result = {k: v for k, v in vars(row).items() if not k.startswith("_")}
        elif args.command == "review":
            try:
                record = review_record(
                    db,
                    args.kind,
                    args.id,
                    args.decision,
                    args.reviewer,
                    args.notes,
                    args.attest_human_review,
                    args.clear_rights,
                )
                db.commit()
                result = {"review_id": record.id, "decision": record.status, "counts": counts(db)}
            except ValueError as exc:
                db.rollback()
                parser.error(str(exc))
        elif args.command == "import-met":
            if not 1 <= args.limit <= 50 or (args.ids and len(args.ids) > 50):
                parser.error("Each batch is limited to 50 objects")
            try:
                ids = args.ids or search(
                    args.query, args.offset, args.limit, args.refresh, args.base_url
                )
            except ImportFailure as exc:
                result = {"search_error": str(exc), "objects": []}
            else:
                outcomes = []
                for identifier in dict.fromkeys(ids):
                    try:
                        item = import_object(db, identifier, args.refresh, args.base_url)
                        db.commit()
                        outcomes.append(item)
                    except ImportFailure as exc:
                        db.rollback()
                        outcomes.append({"id": identifier, "error": str(exc)})
                    print(json.dumps(outcomes[-1], ensure_ascii=False), flush=True)
                result = {"objects": outcomes, "counts": counts(db)}
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n"
            )
        else:
            result = {"counts": counts(db), "sources": [], "artifacts": [], "media": []}
            export_models: list[tuple[str, Any]] = [
                *[(kind, model) for kind, model in KINDS.items()],
                ("review", Review),
                ("exhibit_region", ExhibitRegion),
                ("claim_evidence", ClaimEvidence),
                ("artifact_exhibit", ArtifactExhibit),
            ]
            result = {"version": 1, "scope": "Whole Liaoning", "counts": counts(db)}
            for key, model in export_models:
                exported_rows: list[Any] = list(db.scalars(select(model)))
                result[key] = [
                    {k: v for k, v in vars(exported_row).items() if not k.startswith("_")}
                    for exported_row in exported_rows
                ]
            destination = ROOT / "data/manifests/corpus.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n"
            )
            result = {"manifest": str(destination.relative_to(ROOT)), "counts": result["counts"]}
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    engine.dispose()


if __name__ == "__main__":
    main()
