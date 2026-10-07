import copy
import io
import json
from pathlib import Path

import httpx
import openpyxl
import pytest
from pydantic import ValidationError

from folkverse.liaoning_inventory import (
    SourceSpec,
    collect,
    collections,
    download,
    extract,
    ingest,
    safe_url,
    write_json,
)
from folkverse.liaoning_review import (
    Relation,
    Unit,
    apply_reviews,
    coverage_report,
    draft,
    link,
    review_template,
    reviewed,
)


def source(**changes):
    values = dict(
        id="test-inventory",
        title="Official list",
        institution="Province",
        url="https://www.ln.gov.cn/list",
        resource_url="https://www.ln.gov.cn/list",
        adapter="api_json",
        kind="heritage",
        reference_date="2026-06-30",
        edition="2026",
        expected_count=2,
        counting_unit="project rows",
        rights="metadata_only_pending_excerpts",
    )
    return SourceSpec.model_validate(values | changes)


def raw(name="甲", locality="沈阳市"):
    return json.dumps(
        {
            "items": [
                {"id": "1", "name": name, "category": "传统技艺", "locality": locality},
                {"id": "2", "name": "乙", "category": "民俗", "locality": "铁西区"},
            ]
        },
        ensure_ascii=False,
    ).encode()


@pytest.fixture
def workspace(tmp_path):
    write_json(tmp_path / "registry.json", {"sources": [source().model_dump()]})
    write_json(
        tmp_path / "launch-plan.json",
        {
            "cities": [
                {"id": "shenyang", "names": {"en": "Shenyang", "zh-CN": "沈阳"}},
                {"id": "anshan", "names": {"en": "Anshan", "zh-CN": "鞍山"}},
            ],
            "required_locales": ["en", "zh-CN"],
            "minimum_topics_per_city": 3,
            "minimum_subjects_per_city": 2,
        },
    )
    ingest(tmp_path, source(), raw(), "2026-10-06T00:00:00+00:00", tmp_path / "raw")
    return tmp_path


def unit(folder, identifier="intro-zh", **changes):
    row = collections(folder)[0]["rows"][0]
    return Unit.model_validate(
        dict(
            id=identifier,
            topic_id="topic",
            city_ids=["shenyang"],
            subject="crafts",
            locale="zh-CN",
            kind="introduction",
            text="名录列有甲。",
            supporting_rows=[row["id"]],
            classification="source_statement",
            rights_basis="test permission",
        )
        | changes
    )


def approve(folder):
    packet = review_template(folder)
    for entry in packet["entries"]:
        entry["review"].update(
            decision="approved",
            reviewer="Fixture Human",
            reviewed_at="2026-10-06T00:00:00+00:00",
            notes="fixture review",
            attest_human_review=True,
            rights_cleared=True,
            source_support_checked=True,
            translation_checked=True,
        )
    return packet


def test_workbook_magic_and_merged_category():
    book = openpyxl.Workbook()
    page = book.active
    page.title = "projects"
    page.append(["序号", "类别", "名称"])
    page.append([1, "传统技艺", "甲"])
    page.append([2, None, "乙"])
    page.merge_cells("B2:B3")
    stream = io.BytesIO()
    book.save(stream)
    spec = source(adapter="workbook", sheet="projects", resource_url="https://www.ln.gov.cn/a.xls")
    rows, errors = extract(spec, stream.getvalue())
    assert errors == [] and len(rows) == 2
    assert {r["category_original"] for r in rows} == {"传统技艺"}
    assert rows[1]["locator"] == "sheet:projects;row:3"
    with pytest.raises(ValueError, match="worksheet"):
        extract(spec.model_copy(update={"sheet": "absent"}), stream.getvalue())


def test_missing_and_duplicate_ordinals_do_not_pass_same_count():
    document = json.loads(raw())
    document["items"][1]["id"] = "3"
    rows, errors = extract(source(), json.dumps(document).encode())
    assert len(rows) == 2 and any("missing=['2']" in error for error in errors)
    document["items"][1]["id"] = "1"
    _, errors = extract(source(), json.dumps(document).encode())
    assert any("Duplicate" in error for error in errors)


def test_html_script_is_not_an_inventory_row():
    data = b"<script>01 fake nowhere</script><p>01 name city</p>"
    rows, errors = extract(source(adapter="html_lines", expected_count=1), data)
    assert not errors and [r["name_original"] for r in rows] == ["name"]


@pytest.mark.parametrize(
    "url",
    [
        "http://www.ln.gov.cn/a",
        "https://ln.gov.cn.evil.test/a",
        "https://www.ln.gov.cn:8443/a",
        "https://u:p@ln.gov.cn/a",
    ],
)
def test_inventory_host_boundary(url):
    with pytest.raises(ValueError):
        safe_url(url)


def test_robots_and_redirects_fail_closed():
    def denied(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        pytest.fail("Disallowed resource requested")

    with httpx.Client(transport=httpx.MockTransport(denied)) as client:
        with pytest.raises(ValueError, match="robots_disallowed"):
            download("https://www.ln.gov.cn/list", client)

    def redirect(request):
        return (
            httpx.Response(404)
            if request.url.path == "/robots.txt"
            else httpx.Response(302, headers={"Location": "https://other.test"})
        )

    with httpx.Client(transport=httpx.MockTransport(redirect), follow_redirects=False) as client:
        with pytest.raises(ValueError, match="resource_http_302"):
            download("https://www.ln.gov.cn/list", client)


def test_reimport_preserves_reviews_and_changed_source_invalidates(workspace):
    original = unit(workspace)
    draft(workspace, original)
    packet = approve(workspace)
    assert apply_reviews(workspace, packet) == 1
    assert apply_reviews(workspace, packet) == 0
    assert reviewed(workspace, original)
    before = (workspace / "reviews.json").read_bytes()
    ingest(workspace, source(), raw(), "2026-10-07T00:00:00+00:00", workspace / "raw")
    assert reviewed(workspace, original)
    assert (workspace / "reviews.json").read_bytes() == before
    ingest(workspace, source(), raw(name="甲改"), "2026-10-07T00:00:00+00:00", workspace / "raw")
    assert not reviewed(workspace, original)
    with pytest.raises(ValueError, match="stale"):
        apply_reviews(workspace, packet)
    assert len(list((workspace / "collections").glob("*.json"))) == 2


def test_draft_and_translation_changes_revoke_approval(workspace):
    original = unit(workspace)
    draft(workspace, original)
    translated = unit(
        workspace, "intro-en", locale="en", text="Listed A.", translation_of=original.id
    )
    draft(workspace, translated)
    apply_reviews(workspace, approve(workspace))
    assert reviewed(workspace, translated)
    draft(workspace, original.model_copy(update={"text": "Changed original."}))
    assert not reviewed(workspace, original)
    assert not reviewed(workspace, translated)


@pytest.mark.parametrize(
    "change",
    [
        dict(attest_human_review=False),
        dict(reviewer=""),
        dict(rights_cleared=False),
        dict(source_support_checked=False),
        dict(reviewed_at="2026-10-06T00:00:00"),
    ],
)
def test_approval_requires_actual_attributed_review(workspace, change):
    draft(workspace, unit(workspace))
    packet = approve(workspace)
    packet["entries"][0]["review"].update(change)
    with pytest.raises(ValidationError):
        apply_reviews(workspace, packet)
    assert not (workspace / "reviews.json").exists()


def test_rights_and_translation_cannot_be_skipped(workspace):
    draft(workspace, unit(workspace, rights_basis=""))
    with pytest.raises(ValueError, match="Rights basis"):
        apply_reviews(workspace, approve(workspace))
    draft(workspace, unit(workspace))
    draft(workspace, unit(workspace, "intro-en", locale="en", translation_of="intro-zh"))
    packet = approve(workspace)
    packet["entries"][1]["review"]["translation_checked"] = False
    with pytest.raises(ValueError, match="translation"):
        apply_reviews(workspace, packet)
    assert not (workspace / "reviews.json").exists()


def test_collection_tamper_is_detected(workspace):
    index = json.loads((workspace / "collection-index.json").read_text())
    path = workspace / "collections" / next(iter(index["sources"].values()))["collection"]
    capture = json.loads(path.read_text())
    capture["rows"][0]["name_original"] = "tampered"
    write_json(path, capture)
    with pytest.raises(ValueError, match="hash mismatch"):
        collections(workspace)


def test_unknown_selected_source_fails_before_network(workspace):
    with pytest.raises(ValueError, match="Unknown source"):
        collect(workspace, workspace / "raw", "typo")


def test_catalog_is_not_explanation_or_publication(workspace):
    draft(workspace, unit(workspace))
    apply_reviews(workspace, approve(workspace))
    report = coverage_report(workspace, published={"status": "unavailable", "exhibits": []})
    assert report["summary"]["inventory_rows"] == 2
    assert report["summary"]["reviewed_explanation_units"] == 1
    assert report["summary"]["published_exhibits"] is None
    assert report["summary"]["launch_ready_cities"] == 0
    assert report["summary"]["unknown_unique_topic_total"]
    assert not any(city["reviewed_substantive_topics"] for city in report["launch_manifest"])


def test_missing_rows_and_unknown_total_stay_visible(workspace):
    spec = source(expected_count=3)
    write_json(
        workspace / "registry.json",
        {
            "sources": [
                spec.model_dump(),
                source(id="unknown-total", expected_count=None, adapter="descriptor").model_dump(),
            ]
        },
    )
    ingest(workspace, spec, raw(), "2026-10-06T00:00:00+00:00", workspace / "raw")
    report = coverage_report(workspace, published={"status": "verified", "exhibits": []})
    known, unknown = report["inventories"]
    assert known["missing"] == 1 and known["import_ratio"] == 2 / 3
    assert known["row_accounting"][-1] == {"ordinal": "3", "status": "missing"}
    assert unknown["expected"] is None and unknown["accounted_ratio"] is None


def test_source_bound_identity_relation_never_auto_merges(workspace):
    row_ids = [r["id"] for r in collections(workspace)[0]["rows"]]
    relation = Relation(
        id="shared", row_ids=row_ids, kind="shared_tradition", explanation="Fixture hypothesis only"
    )
    link(workspace, relation)
    link(workspace, relation)
    report = coverage_report(workspace, published={"status": "verified", "exhibits": []})
    assert report["relations"][0]["current"]
    assert report["relations"][0]["relation"]["status"] == "pending"
    assert len(report["relations"]) == 1 and len(report["associations"]) == 2
    ingest(workspace, source(), raw(name="changed"), "2026-10-06T00:00:00+00:00", workspace / "raw")
    report = coverage_report(workspace, published={"status": "verified", "exhibits": []})
    assert not report["relations"][0]["current"]
    with pytest.raises(ValidationError):
        Relation.model_validate(relation.model_dump() | {"status": "confirmed"})


def test_duplicate_review_decisions_rejected_atomically(workspace):
    draft(workspace, unit(workspace))
    packet = approve(workspace)
    packet["entries"].append(copy.deepcopy(packet["entries"][0]))
    with pytest.raises(ValueError, match="Duplicate unit"):
        apply_reviews(workspace, packet)
    assert not (workspace / "reviews.json").exists()


def test_ambiguous_county_names_do_not_create_false_city_coverage(workspace):
    geo = source(id="geography", kind="geography", expected_count=4)
    items = []
    for code, name, level, city_code in [
        ("210100", "沈阳市", "city", "210100"),
        ("210300", "鞍山市", "city", "210300"),
        ("210106", "铁西区", "county", "210100"),
        ("210303", "铁西区", "county", "210300"),
    ]:
        from folkverse.liaoning_inventory import record

        items.append(
            record(
                geo,
                code,
                name,
                level,
                "",
                "fixture:" + code,
                native_code=code,
                level=level,
                city_code=city_code,
            )
        )
    # Fixture geography capture is explicit and integrity-bound; no network/DB writes.
    value = dict(
        version="fixture",
        collection_hash="g",
        source=geo.model_dump(),
        rows=items,
        fetched_at="2026-10-06T00:00:00+00:00",
        errors=[],
        status="imported",
    )
    write_json(workspace / "collections/geography.json", value)
    index = json.loads((workspace / "collection-index.json").read_text())
    from folkverse.liaoning_inventory import digest

    index["sources"][geo.id] = dict(
        collection="geography.json", collection_hash="g", manifest_sha256=digest(value)
    )
    write_json(workspace / "collection-index.json", index)
    report = coverage_report(workspace, published={"status": "verified", "exhibits": []})
    assert report["associations"][0]["city_ids"] == ["shenyang"]
    assert report["associations"][1]["city_ids"] == []
    assert report["associations"][1]["county_codes"] == []
    ingest(
        workspace,
        source(),
        raw(locality="沈阳市铁西区"),
        "2026-10-06T00:00:00+00:00",
        workspace / "raw",
    )
    report = coverage_report(workspace, published={"status": "verified", "exhibits": []})
    assert report["associations"][0]["city_ids"] == ["shenyang"]
    assert report["associations"][0]["county_codes"] == ["210106"]


def test_reimport_cannot_bless_altered_collection(workspace):
    index = json.loads((workspace / "collection-index.json").read_text())
    path = workspace / "collections" / next(iter(index["sources"].values()))["collection"]
    value = json.loads(path.read_text())
    value["rows"][0]["name_original"] = "tampered"
    write_json(path, value)
    with pytest.raises(ValueError, match="cannot bless|hash mismatch"):
        ingest(workspace, source(), raw(), "2026-10-06T00:00:00+00:00", workspace / "raw")


def test_bad_api_values_never_become_stringified_facts():
    payload = json.loads(raw())
    payload["items"][0]["name"] = {"made_up": "data"}
    rows, errors = extract(source(), json.dumps(payload).encode())
    assert len(rows) == 1 and any("Invalid API" in error for error in errors)


def test_translation_cannot_change_topic_or_geographic_scope(workspace):
    original = unit(workspace)
    draft(workspace, original)
    translated = unit(
        workspace, "intro-en", locale="en", topic_id="other-topic", translation_of=original.id
    )
    draft(workspace, translated)
    with pytest.raises(ValueError, match="preserve topic"):
        review_template(workspace)


def test_visual_transcription_is_version_bound_and_idempotent(workspace):
    from folkverse.liaoning_inventory import Reconciliation, digest, reconcile_scan

    base = collections(workspace)[0]
    evidence = {
        "source_id": source().id,
        "source_collection_hash": base["collection_hash"],
        "source_raw_sha256": base["raw_sha256"],
        "pages": [{"locator": "pdf-page:1", "lines": []}],
    }
    observation_hash = digest(evidence)
    write_json(
        workspace / "ocr/fixture.json",
        evidence
        | {"observation_hash": observation_hash, "created_at": "2026-10-06T00:00:00+00:00"},
    )
    packet = Reconciliation.model_validate(
        dict(
            source_id=source().id,
            base_collection_hash=base["collection_hash"],
            observation_hash=observation_hash,
            reviewer="Fixture Human",
            reviewed_at="2026-10-06T00:00:00+00:00",
            attest_visual_row_check=True,
            notes="Visual row verification fixture",
            rows=[
                dict(
                    ordinal=i,
                    name_original=name,
                    category_original="category",
                    locality_original="city",
                    page_locator="pdf-page:1",
                    visual_row_locator=f"table-row:{i}",
                )
                for i, name in [(1, "甲"), (2, "乙")]
            ],
        )
    )
    packet = packet.model_copy(update={"reviewer_kind": "assistant"})
    key = reconcile_scan(workspace, packet)
    assert collections(workspace)[0]["reconciliation"]["reviewer_kind"] == "assistant"
    assert reconcile_scan(workspace, packet) == key
    assert collections(workspace)[0]["errors"] == []
    assert ingest(workspace, source(), raw(), "2026-10-07T00:00:00+00:00", workspace / "raw") == key
    assert not (workspace / "reviews.json").exists()  # Transcription is not content approval.
    changed = packet.model_copy(update={"notes": "Changed review"})
    with pytest.raises(ValueError, match="stale"):
        reconcile_scan(workspace, changed)
    human_packet = packet.model_copy(
        update={"base_collection_hash": key, "reviewer_kind": "human", "reviewer": "Fixture Human"}
    )
    human_key = reconcile_scan(workspace, human_packet)
    assert human_key != key
    assert collections(workspace)[0]["reconciliation"]["reviewer_kind"] == "human"
    assert not (workspace / "reviews.json").exists()
    with pytest.raises(ValidationError):
        Reconciliation.model_validate(packet.model_dump() | {"attest_visual_row_check": False})


def test_ocr_rejects_plain_text_instead_of_recording_empty_success(tmp_path, monkeypatch):
    import hashlib
    import subprocess

    from folkverse.liaoning_ocr import stage

    private = tmp_path / "private"
    model = private / "ocr/chi_sim.traineddata"
    model.parent.mkdir(parents=True)
    model.write_bytes(b"fixture-model")
    write_json(
        tmp_path / "ocr-runtime.json", {"sha256": hashlib.sha256(model.read_bytes()).hexdigest()}
    )
    spec = source(adapter="descriptor")
    ingest(tmp_path, spec, b"%PDF-fixture", "2026-10-06T00:00:00+00:00", private / "raw")

    def run(command, **kwargs):
        if command[0] == "pdftoppm":
            Path(command[-1] + "-1.png").write_bytes(b"fixture-image")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        assert "tessedit_create_tsv=1" in command
        return subprocess.CompletedProcess(command, 0, stdout="plain OCR text", stderr="")

    monkeypatch.setattr("folkverse.liaoning_ocr.subprocess.run", run)
    with pytest.raises(ValueError, match="required TSV"):
        stage(tmp_path, spec.id, private)
    assert not list((tmp_path / "ocr").glob("*.json"))


def test_registry_rights_change_invalidates_review_before_recollection(workspace):
    original = unit(workspace)
    draft(workspace, original)
    apply_reviews(workspace, approve(workspace))
    changed = source(rights="permission withdrawn")
    write_json(workspace / "registry.json", {"sources": [changed.model_dump()]})
    assert not reviewed(workspace, original)
    with pytest.raises(ValueError, match="rights changed"):
        review_template(workspace)


def test_html_codes_preserves_native_categories_and_locality():
    spec = source(adapter="html_codes")
    rows, errors = extract(spec, "<p>1 Ⅱ—31 鼓乐 沈阳市辽中区</p><p>2 Ⅷ—1 雕刻 抚顺市</p>".encode())
    assert not errors
    assert rows[0]["native_code"] == "Ⅱ—31"
    assert rows[0]["category_original"] == "传统音乐"
    assert rows[1]["category_original"] == "传统技艺"
    assert rows[0]["locality_original"] == "沈阳市辽中区"


def test_article_hashes_paragraphs_without_republishing_source_prose():
    text = "某博物馆介绍城市历史及馆藏展品。" * 5
    spec = source(
        adapter="html_article",
        kind="explanation",
        expected_count=None,
        subject_hint="museums",
        locality="沈阳市",
    )
    rows, errors = extract(
        spec, f'<nav>菜单</nav><div class="pages_content"><p>{text}</p></div>'.encode()
    )
    assert not errors
    assert len(rows) == 1
    assert rows[0]["locality_original"] == "沈阳市"
    assert rows[0]["paragraphs"][0]["characters"] == len(text)
    assert len(rows[0]["paragraphs"][0]["text_sha256"]) == 64
    assert text not in json.dumps(rows, ensure_ascii=False)
    assert rows[0]["content_approval"] == "pending_human_review"


def test_launch_preparation_preserves_edits_and_never_approves(workspace, monkeypatch):
    from folkverse import liaoning_review
    from folkverse.liaoning_launch import prepare

    monkeypatch.setattr(
        liaoning_review, "published_snapshot", lambda: {"status": "verified", "exhibits": []}
    )
    specs = [source()]
    materials = []
    for city in ["shenyang", "anshan"]:
        for index in range(3):
            spec = source(
                id=f"explanation-{city}-{index}",
                adapter="html_article",
                kind="explanation",
                expected_count=None,
                subject_hint="sites" if index == 0 else "museums",
            )
            specs.append(spec)
            ingest(
                workspace,
                spec,
                ('<div class="pages_content"><p>' + "历史介绍材料。" * 12 + "</p></div>").encode(),
                "2026-10-06T00:00:00+00:00",
                workspace / "raw",
            )
            capture = next(c for c in collections(workspace) if c["source"]["id"] == spec.id)
            materials.append(
                dict(
                    source_id=spec.id,
                    source_raw_sha256=capture["raw_sha256"],
                    city_id=city,
                    subject=spec.subject_hint,
                    title=spec.title,
                    classification="source_statement",
                    context={"en": "Fixture historical context.", "zh-CN": "测试历史背景。"},
                    example={"en": "Fixture example.", "zh-CN": "测试例子。"},
                    status="assistant_draft_requires_human_review",
                )
            )
    write_json(workspace / "registry.json", {"sources": [s.model_dump() for s in specs]})
    write_json(
        workspace / "launch-material.json",
        {"version": "liaoning-launch-material-v1", "materials": materials},
    )
    result = prepare(workspace)
    assert result["draft_units"] == 48
    assert result["prepared_cities"] == 2
    assert result["approved_units"] == 0
    assert result["automatically_published"] is False
    assert (
        coverage_report(workspace, {"status": "verified", "exhibits": []})["summary"][
            "launch_ready_cities"
        ]
        == 0
    )
    drafts = json.loads((workspace / "units.json").read_text())
    drafts["units"][0]["text"] = "Operator edit to preserve."
    write_json(workspace / "units.json", drafts)
    prepare(workspace)
    assert (
        json.loads((workspace / "units.json").read_text())["units"][0]["text"]
        == "Operator edit to preserve."
    )
    materials[0]["source_raw_sha256"] = "0" * 64
    write_json(
        workspace / "launch-material.json",
        {"version": "liaoning-launch-material-v1", "materials": materials},
    )
    with pytest.raises(ValueError, match="does not match"):
        prepare(workspace)


def test_protected_site_table_keeps_chronology_in_its_own_column():
    spec = source(adapter="html_table", kind="sites", expected_count=1)
    rows, errors = extract(
        spec,
        "<table><tr><td>1</td><td>古城</td><td>沈阳市</td><td>明</td><td>古建筑</td></tr></table>".encode(),
    )
    assert not errors
    assert rows[0]["name_original"] == "古城"
    assert rows[0]["locality_original"] == "沈阳市"
    assert rows[0]["category_original"] == "古建筑"
    assert rows[0]["chronology_original"] == "明"
