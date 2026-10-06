"""Download the pinned platform image through the current user's proxy, not the daemon."""

import hashlib
import json
import os
import pathlib
import platform
import re
import tarfile

import httpx


def main():
    os.chdir(pathlib.Path(__file__).resolve().parents[1])
    root = pathlib.Path(".local/pgvector-image")
    root.mkdir(parents=True, exist_ok=True)
    base = "https://registry-1.docker.io/v2/pgvector/pgvector/"
    digest = re.search(
        r"image: pgvector/pgvector:pg17@(sha256:[a-f0-9]{64})",
        pathlib.Path("compose.yaml").read_text(),
    ).group(1)
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        token = client.get(
            "https://auth.docker.io/token",
            params={
                "service": "registry.docker.io",
                "scope": "repository:pgvector/pgvector:pull",
            },
        ).json()["token"]
        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json",
        }

        def manifest(identifier):
            r = client.get(base + "manifests/" + identifier, headers=headers)
            r.raise_for_status()
            assert "sha256:" + hashlib.sha256(r.content).hexdigest() == identifier
            return r.json()

        index = manifest(digest)
        machine = platform.machine()
        if machine not in {"x86_64", "aarch64"}:
            raise ValueError("Unsupported local platform")
        selected_platform = next(
            m
            for m in index["manifests"]
            if m["platform"]
            == {
                "architecture": "amd64" if machine == "x86_64" else "arm64",
                "os": "linux",
            }
        )
        image = manifest(selected_platform["digest"])
        paths = []
        for item in [image["config"], *image["layers"]]:
            name = item["digest"].split(":")[1]
            p = root / name
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != name:
                with (
                    client.stream(
                        "GET",
                        base + "blobs/" + item["digest"],
                        headers={"Authorization": "Bearer " + token},
                    ) as r,
                    p.open("wb") as f,
                ):
                    r.raise_for_status()
                    for chunk in r.iter_bytes():
                        f.write(chunk)
            assert hashlib.sha256(p.read_bytes()).hexdigest() == name
            paths.append(name)
            print("Verified blob", name[:12], p.stat().st_size, flush=True)
        tag = "pgvector/pgvector:folkverse-verified-pg17"
        (root / "manifest.json").write_text(
            json.dumps([{"Config": paths[0], "RepoTags": [tag], "Layers": paths[1:]}])
        )
        with tarfile.open(root / "image.tar", "w") as archive:
            for name in [*paths, "manifest.json"]:
                archive.add(root / name, arcname=name)
        pathlib.Path(".local/compose-proxy.yaml").write_text(
            "services:\n  db:\n    image: " + tag + "\n    pull_policy: never\n"
        )
        pathlib.Path(
            "report/evidence/phase03-completion/database-image.json"
        ).write_text(
            json.dumps(
                {
                    "upstream_index": digest,
                    "platform_manifest": selected_platform["digest"],
                    "config_digest": image["config"]["digest"],
                    "local_tag": tag,
                    "transport": "existing user HTTPS proxy",
                    "all_blob_hashes_verified": True,
                },
                indent=2,
            )
            + "\n"
        )
        print("Pinned platform image ready for docker load.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (
        httpx.HTTPError,
        OSError,
        KeyError,
        StopIteration,
        AssertionError,
        ValueError,
        AttributeError,
    ):
        raise SystemExit(
            "Pinned image recovery failed; no successful verification is claimed."
        ) from None
