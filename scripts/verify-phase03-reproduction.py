"""Reproduce the candidate Git-visible tree in a disposable checkout and dedicated temporary DB."""

import argparse
import hashlib
import json
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "pgvector/pgvector:pg17@sha256:d2ef61f42ef767baa5a1475393303cc235bcd92febd9d7014eddb48b41f3bad0"


def main(output):
    result = {
        "started_at": datetime.now(UTC).isoformat(),
        "scope": "Git-visible candidate tree; fresh dependency installs, setup, isolated PostgreSQL/pgvector, migrations, corpus restore, API and production web startup",
        "production_database_modified": False,
        "provider_key_copied": False,
        "provider_calls": 0,
        "steps": [],
    }
    environment = {
        k: v
        for k, v in os.environ.items()
        if k
        in {
            "PATH",
            "HOME",
            "LANG",
            "LC_ALL",
            "TMPDIR",
            "XDG_CACHE_HOME",
            "UV_CACHE_DIR",
            "HTTPS_PROXY",
            "HTTP_PROXY",
            "ALL_PROXY",
            "NO_PROXY",
            "https_proxy",
            "http_proxy",
            "all_proxy",
            "no_proxy",
        }
    }
    environment["NODE_EXTRA_CA_CERTS"] = "/etc/ssl/cert.pem"
    runtime_paths = sorted(
        set(ROOT.glob("apps/api/src/**/*.py"))
        | set(ROOT.glob("apps/web/src/**/*.*"))
        | {
            ROOT / "pnpm-lock.yaml",
            ROOT / "apps/api/uv.lock",
            ROOT / "package.json",
            ROOT / "packages/contracts/openapi.json",
            ROOT / "packages/contracts/src/schema.d.ts",
            ROOT / "packages/contracts/src/jinyao-policy.json",
        }
    )
    result["runtime_file_hashes"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in runtime_paths
        if p.is_file()
    }
    result["git_base_commit"] = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    )
    processes = []
    container = "folkverse-phase3-reproduce-" + secrets.token_hex(6)

    def run(args, cwd, timeout=300, expected_codes=(0,)):
        start = time.monotonic()
        completed = subprocess.run(
            args,
            check=False,
            cwd=cwd,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        result["steps"].append(
            {
                "command": args,
                "exit_code": completed.returncode,
                "elapsed_ms": (time.monotonic() - start) * 1000,
                "expected_codes": list(expected_codes),
            }
        )
        print(
            f"{'PASS' if completed.returncode in expected_codes else 'FAIL'}: {' '.join(args)}",
            flush=True,
        )
        if completed.returncode not in expected_codes:
            # Full output may contain generated database configuration; never publish it.
            raise RuntimeError("Reproduction command failed: " + args[0])
        return completed.stdout

    def read(url):
        with urlopen(url, timeout=5) as response:
            return response.status, json.loads(response.read())

    def wait_ready(url, seconds=45):
        until = time.monotonic() + seconds
        while time.monotonic() < until:
            try:
                return read(url)
            except (URLError, TimeoutError, json.JSONDecodeError):
                time.sleep(0.25)
        raise RuntimeError("Startup did not become available.")

    try:
        with tempfile.TemporaryDirectory(
            prefix="folkverse-phase3-reproduction-"
        ) as temp:
            checkout = Path(temp) / "checkout"
            checkout.mkdir()
            paths = (
                subprocess.check_output(
                    [
                        "git",
                        "ls-files",
                        "--cached",
                        "--others",
                        "--exclude-standard",
                        "-z",
                    ],
                    cwd=ROOT,
                )
                .decode()
                .split("\0")
            )
            fingerprint = hashlib.sha256()
            count = 0
            for name in sorted(set(paths)):
                source = ROOT / name
                if not name or not source.is_file():
                    continue
                target = checkout / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                fingerprint.update(name.encode())
                fingerprint.update(hashlib.sha256(source.read_bytes()).digest())
                count += 1
            result["candidate_tree_sha256"] = fingerprint.hexdigest()
            result["files_copied"] = count
            run(["pnpm", "install", "--frozen-lockfile", "--offline"], checkout)
            run(["uv", "sync", "--project", "apps/api", "--frozen"], checkout)
            run(["pnpm", "setup:local"], checkout)
            first = (checkout / ".env").read_bytes()
            run(["pnpm", "setup:local"], checkout)
            result["setup_preserves_existing_secrets"] = (
                checkout / ".env"
            ).read_bytes() == first
            local = {
                line.split("=", 1)[0]: line.split("=", 1)[1]
                for line in first.decode().splitlines()
                if "=" in line
            }
            db_env = Path(temp) / "database.env"
            db_env.write_text(
                "\n".join(
                    f"{k}={local[k]}"
                    for k in ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
                )
                + "\n"
            )
            db_env.chmod(0o600)
            run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--rm",
                    "--name",
                    container,
                    "--env-file",
                    str(db_env),
                    "-p",
                    "127.0.0.1::5432",
                    IMAGE,
                ],
                checkout,
            )
            port = (
                run(["docker", "port", container, "5432/tcp"], checkout)
                .strip()
                .split(":")[-1]
            )
            config = (
                first.decode()
                .replace(":5440/", f":{port}/")
                .replace("POSTGRES_PORT=5440", f"POSTGRES_PORT={port}")
            )
            config = (
                config.replace("APP_MODE=demo", "APP_MODE=live")
                + "\nTRUSTED_LOOKUP_ENABLED=false\nEMBEDDING_ENABLED=false\n"
            )
            (checkout / ".env").write_text(config)
            deadline = time.monotonic() + 40
            while time.monotonic() < deadline:
                ready = subprocess.run(
                    [
                        "docker",
                        "exec",
                        container,
                        "pg_isready",
                        "-U",
                        "folkverse",
                        "-d",
                        "folkverse",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                if ready.returncode == 0:
                    break
                time.sleep(0.3)
            run(["pnpm", "db:migrate"], checkout)
            run(["pnpm", "db:migrate"], checkout)
            run(
                [
                    "uv",
                    "run",
                    "--project",
                    "apps/api",
                    "python",
                    "-m",
                    "folkverse.curation",
                    "restore-manifest",
                ],
                checkout,
            )
            inspection = [
                "uv",
                "run",
                "--project",
                "apps/api",
                "python",
                "-m",
                "folkverse.curation",
            ]
            before_counts = run(inspection + ["counts"], checkout)
            before_reviews = run(inspection + ["ledger"], checkout)
            run(
                [
                    "uv",
                    "run",
                    "--project",
                    "apps/api",
                    "python",
                    "-m",
                    "folkverse.curation",
                    "restore-manifest",
                ],
                checkout,
                expected_codes=(2,),
            )
            result["restore_refuses_existing_content"] = before_counts == run(
                inspection + ["counts"], checkout
            ) and before_reviews == run(inspection + ["ledger"], checkout)
            run(["pnpm", "assets:sync"], checkout)
            run(["pnpm", "lint"], checkout)
            run(["pnpm", "typecheck"], checkout)
            run(["pnpm", "build"], checkout)
            (checkout / "apps/web/.env.local").write_text(
                "API_BASE_URL=http://127.0.0.1:8004\nAPP_MODE=live\n"
            )
            processes.append(
                subprocess.Popen(
                    [
                        "uv",
                        "run",
                        "--project",
                        "apps/api",
                        "uvicorn",
                        "folkverse.main:create_app",
                        "--factory",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8004",
                    ],
                    cwd=checkout,
                    env=environment,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            )
            _, health = wait_ready("http://127.0.0.1:8004/api/v1/health")
            result["fresh_api_health"] = health
            _, exhibits = read(
                "http://127.0.0.1:8004/api/v1/exhibits?locale=en&limit=5"
            )
            result["fresh_published_exhibits"] = exhibits["total"]
            session_request = Request(
                "http://127.0.0.1:8004/api/v1/session",
                method="POST",
                headers={"Origin": "http://127.0.0.1:3000"},
            )
            with urlopen(session_request, timeout=5) as response:
                cookie = response.headers["Set-Cookie"].split(";")[0]
                result["fresh_owned_session"] = response.status == 200
            guide = Request(
                "http://127.0.0.1:8004/api/v1/guide",
                data=json.dumps(
                    {"question": "Hi", "locale": "en", "depth": "concise"}
                ).encode(),
                headers={
                    "Origin": "http://127.0.0.1:3000",
                    "Cookie": cookie,
                    "Content-Type": "application/json",
                },
            )
            try:
                urlopen(guide, timeout=5)
                result["missing_key_fails_closed"] = False
            except URLError as error:
                result["missing_key_fails_closed"] = getattr(error, "code", None) == 503
            processes.append(
                subprocess.Popen(
                    [
                        "pnpm",
                        "--filter",
                        "@folkverse/web",
                        "exec",
                        "next",
                        "start",
                        "--hostname",
                        "127.0.0.1",
                        "--port",
                        "3004",
                    ],
                    cwd=checkout,
                    env=environment,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            )
            _, web_health = wait_ready("http://127.0.0.1:3004/api/v1/health")
            result["fresh_web_to_api_health"] = web_health
            with urlopen("http://127.0.0.1:3004/guide", timeout=15) as response:
                result["fresh_guide_http_status"] = response.status
            result["passed"] = all(
                [
                    result["setup_preserves_existing_secrets"],
                    result["fresh_owned_session"],
                    result["missing_key_fails_closed"],
                    health["schema_status"] == "current",
                    web_health["database"] == "available",
                    exhibits["total"] == 1,
                ]
            )
    except (
        OSError,
        RuntimeError,
        subprocess.SubprocessError,
        ValueError,
        KeyError,
    ) as error:
        result["passed"] = False
        result["error"] = (
            str(error) if isinstance(error, RuntimeError) else type(error).__name__
        )
    finally:
        for process in reversed(processes):
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        subprocess.run(
            ["docker", "stop", container],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            removed = (
                subprocess.run(
                    ["docker", "inspect", container],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                ).returncode
                != 0
            )
            if removed:
                break
            time.sleep(0.1)
        result["temporary_container_removed"] = removed
        result["completed_at"] = datetime.now(UTC).isoformat()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "passed": result["passed"],
                    "steps": len(result["steps"]),
                    "temporary_container_removed": result[
                        "temporary_container_removed"
                    ],
                },
                indent=2,
            )
        )
    return result["passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(
            "Select a new evidence output; never overwrite a previous run."
        )
    raise SystemExit(0 if main(args.output) else 1)
