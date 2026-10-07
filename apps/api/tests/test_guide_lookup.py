"""Bounded original-page lookup, original-language relations and fresh-source checks."""

import asyncio
import socket

import httpx
import pytest

from folkverse.guide_lookup import OfficialLookup, checked_url, fetch_official, public_ip


@pytest.mark.parametrize(
    "url",
    [
        "http://www.ln.gov.cn/x",
        "https://www.ln.gov.cn.evil.test/x",
        "https://whly.ln.gov.cn@evil.test/x",
        "https://www.ln.gov.cn:444/x",
        "https://127.0.0.1/x",
        "https://whly.ln.gov.cn/x#secret",
    ],
)
def test_only_exact_registered_https_hosts(url):
    with pytest.raises(ValueError):
        checked_url(url)


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "::1", "fd00::1"])
def test_dns_rebinding_to_nonpublic_addresses_is_rejected(monkeypatch, ip):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))],
    )
    with pytest.raises(ValueError):
        asyncio.run(public_ip("www.ln.gov.cn"))


@pytest.mark.parametrize("attack", ["redirect", "robots", "compressed", "oversize"])
def test_access_policy_and_network_bounds_cannot_be_bypassed(monkeypatch, attack):
    import folkverse.guide_lookup as module

    original = httpx.AsyncClient

    async def resolved(host):
        return "93.184.216.34"

    monkeypatch.setattr(module, "public_ip", resolved)

    def handler(request):
        assert request.url.host == "93.184.216.34"
        assert request.headers["host"] == "www.ln.gov.cn"
        assert request.extensions["sni_hostname"] == "www.ln.gov.cn"
        if request.url.path == "/robots.txt":
            return httpx.Response(
                200,
                stream=httpx.ByteStream(
                    b"User-agent: *\nDisallow: /"
                    if attack == "robots"
                    else b"User-agent: *\nAllow: /"
                ),
            )
        if attack == "redirect":
            return httpx.Response(
                302, headers={"location": "http://127.0.0.1/private"}, stream=httpx.ByteStream(b"")
            )
        if attack == "compressed":
            return httpx.Response(
                200, headers={"content-encoding": "br"}, stream=httpx.ByteStream(b"bad")
            )
        return httpx.Response(200, stream=httpx.ByteStream(b"x" * (module.MAX_LOOKUP_BYTES + 1)))

    monkeypatch.setattr(
        module.httpx,
        "AsyncClient",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )
    with pytest.raises((ValueError, httpx.HTTPError)):
        asyncio.run(fetch_official("https://www.ln.gov.cn/profile"))


def test_lookup_relations_are_subject_specific_and_never_fabricate_review(tmp_path):
    lookup = OfficialLookup(tmp_path)
    source = {
        "id": "palace",
        "title": "沈阳市·沈阳故宫",
        "url": "https://www.ln.gov.cn/profile",
        "institution": "Official institution",
        "locality": "沈阳市",
    }
    raw = (
        '<div class="pages_content"><p>沈阳故宫始建于1625年，是一处历史建筑。'
        "其建筑体现了不同阶段的营造方式。</p></div>"
    ).encode()
    passage = lookup.render(source, raw, "en")
    assert any("1625" in fact for fact in passage.statement_variants)
    assert passage.reviewed_at is None and passage.reviewer == ""
    assert passage.evidence_origin == "official_lookup"
    wrong_subject = raw.replace("沈阳故宫始建".encode(), "沈阳故宫的大政殿始建".encode())
    assert not any(
        "1625" in fact for fact in lookup.render(source, wrong_subject, "en").statement_variants
    )


def test_machine_summary_keeps_classification_and_excludes_changed_original(tmp_path):
    import hashlib
    import json

    from folkverse.guide_support import variants
    from folkverse.liaoning_inventory import Article

    raw = (
        '<div class="pages_content"><p>望儿山的名称与慈母盼儿归的民间传说有关。</p></div>'.encode()
    )
    article = Article()
    article.feed(raw.decode())
    payload = {
        "version": "liaoning-machine-source-audit-v1",
        "human_review_performed": False,
        "records": [
            {
                "source_id": "hill",
                "classification": "folklore",
                "source_raw_sha256": hashlib.sha256(raw).hexdigest(),
                "source_paragraph_sha256": hashlib.sha256(
                    "\n".join(article.paragraphs).encode()
                ).hexdigest(),
                "facts": {
                    "en": [
                        "The profile recounts a traditional story about a mother awaiting her son.",
                        "This is folklore, rather than a verified historical event.",
                    ]
                },
                "rights_basis": "Original short attributed summary; machine assessment only.",
            }
        ],
    }
    path = tmp_path / "machine-source-audit.json"
    path.write_text(json.dumps(payload))
    lookup = OfficialLookup(tmp_path)
    source = {
        "id": "hill",
        "title": "营口市·望儿山",
        "url": "https://whly.ln.gov.cn/profile",
        "institution": "Official institution",
    }
    passage = lookup.render(source, raw, "en")
    assert passage.classification == "folklore"
    assert passage.review_id == "machine_source_assessed_v1"
    assert passage.reviewer == "" and passage.reviewed_at is None
    assert set(variants(passage).values()) == {"machine_source_summary_v1"}
    assert lookup.audited_summary("hill", raw + b"changed", "en") is None
    payload["human_review_performed"] = True
    path.write_text(json.dumps(payload))
    assert lookup.audited_summary("hill", raw, "en") is None


def test_machine_assessment_withdrawal_invalidates_cached_evidence(tmp_path, monkeypatch):
    import json

    import folkverse.guide_lookup as module

    (tmp_path / "registry.json").write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "palace",
                        "title": "沈阳市·沈阳故宫",
                        "kind": "explanation",
                        "url": "https://whly.ln.gov.cn/profile",
                        "institution": "Official institution",
                    }
                ]
            }
        )
    )
    raw = '<div class="pages_content"><p>沈阳故宫始建于1625年，是历史建筑。</p></div>'.encode()

    async def fetched(url):
        return raw

    monkeypatch.setattr(module, "fetch_official", fetched)
    lookup = OfficialLookup(tmp_path)
    passages, _ = asyncio.run(lookup.lookup("沈阳故宫", "zh-CN"))
    assert asyncio.run(lookup.current(passages[0]))
    (tmp_path / "machine-source-audit.json").write_text("{}")
    assert not asyncio.run(lookup.current(passages[0]))


def test_all_city_machine_launch_floor_has_bilingual_unique_search():
    import json

    from folkverse.config import ROOT

    folder = ROOT / "data/liaoning"
    manifest = json.loads((folder / "machine-launch-manifest.json").read_text())
    lookup = OfficialLookup(folder)
    assert manifest["ready_cities"] == manifest["total_cities"] == 14
    assert manifest["topics"] == 42
    for city in manifest["cities"]:
        assert city["ready"] and not city["human_approved"]
        assert len({t["subject"] for t in city["topics"]}) >= 2
        for topic in city["topics"]:
            for locale, name in topic["names"].items():
                matches = lookup.search(name, locale)
                assert [m["id"] for m in matches] == [topic["source_id"]]
        assert len(lookup.city_sources("Explain " + city["names"]["en"])) == 3
    assert not lookup.city_sources("Compare Shenyang and Dalian")
