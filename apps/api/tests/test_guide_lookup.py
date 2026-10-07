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
