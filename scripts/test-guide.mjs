// Portable guide regressions; full PostgreSQL-backed checks remain pnpm test:api.
import { readdirSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const tests = readdirSync(path.join(root, "apps/api/tests"))
  .filter(name => /^test_guide.*\.py$/.test(name) || name === "test_provider_gateway.py")
  .sort().map(name => `apps/api/tests/${name}`);
tests.push("apps/api/tests/test_foundation.py::test_database_outage_is_not_success");
const result = spawnSync("uv", ["run", "--project", "apps/api", "pytest", ...tests, "-q"], {
  cwd: root, stdio: "inherit",
});
if (result.error) console.error("Could not start uv; follow the local setup instructions.");
process.exit(result.status ?? 1);
