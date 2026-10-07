"""Stage local OCR as unreviewed observations, never as inventory facts or approvals."""

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx

from folkverse.config import ROOT
from folkverse.liaoning_inventory import AGENT, collections, digest, download, write_json


def stage(folder: Path, source_id: str, private: Path) -> dict[str, Any]:
    capture = next(c for c in collections(folder) if c["source"]["id"] == source_id)
    runtime = json.loads((folder / "ocr-runtime.json").read_text())
    model = private / "ocr/chi_sim.traineddata"
    if hashlib.sha256(model.read_bytes()).hexdigest() != runtime["sha256"]:
        raise ValueError("Pinned OCR language model checksum mismatch")
    raw = (private / "raw" / capture["raw_sha256"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != capture["raw_sha256"]:
        raise ValueError("Private source capture checksum mismatch")
    pages: list[dict[str, Any]] = []
    segmentation_mode = 11 if raw.startswith(b"%PDF") else 6
    private.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        images: list[tuple[str, Path, str]] = []
        if raw.startswith(b"%PDF"):
            pdf = scratch / "input.pdf"
            pdf.write_bytes(raw)
            # Bound render count and resolution; every original page remains locatable.
            subprocess.run(
                [
                    "pdftoppm",
                    "-png",
                    "-r",
                    "140",
                    "-f",
                    "1",
                    "-l",
                    "40",
                    str(pdf),
                    str(scratch / "page"),
                ],
                timeout=120,
                check=True,
                capture_output=True,
            )
            for page in sorted(scratch.glob("page-*.png")):
                images.append(
                    (
                        f"pdf-page:{int(page.stem.split('-')[-1])}",
                        page,
                        hashlib.sha256(page.read_bytes()).hexdigest(),
                    )
                )
        else:
            text = raw.decode("utf-8")
            links = list(
                dict.fromkeys(re.findall(r'(?:src=["\'])([^"\']*imageDir/[^"\']+\.png)', text))
            )
            if not links or len(links) > 40:
                raise ValueError("Expected one to forty official scan images")
            with httpx.Client(
                timeout=25, headers={"User-Agent": AGENT}, follow_redirects=False
            ) as client:
                for number, link in enumerate(links, 1):
                    url = urljoin(capture["source"]["resource_url"], link)
                    image = download(url, client)
                    sha = hashlib.sha256(image).hexdigest()
                    (private / "raw" / sha).write_bytes(image)
                    path = scratch / f"page-{number}.png"
                    path.write_bytes(image)
                    images.append((url, path, sha))
        for locator, path, sha in images:
            result = subprocess.run(
                [
                    "tesseract",
                    str(path),
                    "stdout",
                    "--tessdata-dir",
                    str(model.parent),
                    "-l",
                    "chi_sim",
                    "--psm",
                    str(segmentation_mode),
                    "-c",
                    "tessedit_create_tsv=1",
                ],
                check=True,
                timeout=60,
                capture_output=True,
                text=True,
            )
            if not result.stdout.startswith("level\tpage_num\t"):
                raise ValueError(
                    "OCR did not emit the required TSV; cannot count this as extracted"
                )
            lines: dict[str, list[str]] = {}
            tokens: dict[str, list[dict[str, Any]]] = {}
            low_confidence = 0
            for line in result.stdout.splitlines()[1:]:
                cells = line.split("\t", 11)
                if len(cells) != 12 or not cells[11].strip():
                    continue
                if float(cells[10]) < 80:
                    low_confidence += 1
                key = ":".join(cells[1:5])
                lines.setdefault(key, []).append(cells[11])
                tokens.setdefault(key, []).append(
                    {
                        "text": cells[11],
                        "confidence": float(cells[10]),
                        "box": list(map(int, cells[6:10])),
                    }
                )
            pages.append(
                {
                    "locator": locator,
                    "image_sha256": sha,
                    "low_confidence_tokens": low_confidence,
                    "lines": [
                        {
                            "locator": f"ocr-line:{key}",
                            "text": " ".join(words),
                            "tokens": tokens[key],
                        }
                        for key, words in lines.items()
                    ],
                }
            )
    evidence = {
        "version": "liaoning-ocr-observations-v1",
        "source_id": source_id,
        "source_collection_hash": capture["collection_hash"],
        "source_raw_sha256": capture["raw_sha256"],
        "runtime": runtime,
        "engine_version": subprocess.run(
            ["tesseract", "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0],
        "parameters": {"page_segmentation_mode": segmentation_mode, "pdf_render_dpi": 140},
        "pages": pages,
        "status": "unresolved_requires_visual_row_reconciliation",
        "counts_as_imported_rows": False,
        "counts_as_reviewed_knowledge": False,
    }
    key = digest(evidence)
    destination = folder / "ocr" / f"{source_id}-{key[:16]}.json"
    if not destination.exists():
        write_json(
            destination,
            {**evidence, "observation_hash": key, "created_at": datetime.now(UTC).isoformat()},
        )
    return {
        "source_id": source_id,
        "pages": len(pages),
        "observation_hash": key,
        "file": str(destination),
        "status": evidence["status"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=ROOT / "data/liaoning")
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    print(json.dumps(stage(args.folder, args.source, ROOT / ".local/liaoning"), indent=2))


if __name__ == "__main__":
    main()
