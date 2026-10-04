import { randomBytes } from "node:crypto";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const env = path.join(root, ".env");
if (!existsSync(env)) {
  const password = randomBytes(24).toString("hex");
  writeFileSync(env, [
    "APP_MODE=demo",
    "POSTGRES_USER=folkverse",
    `POSTGRES_PASSWORD=${password}`,
    "POSTGRES_DB=folkverse",
    "POSTGRES_PORT=5440",
    `DATABASE_URL=postgresql+psycopg://folkverse:${password}@127.0.0.1:5440/folkverse`,
    `SESSION_SECRET=${randomBytes(48).toString("hex")}`,
    "COOKIE_SECURE=false",
    'ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]',
    "",
  ].join("\n"), { mode: 0o600, flag: "wx" });
  console.log("Created ignored root .env with fresh local secrets.");
} else {
  console.log("Preserved existing root .env.");
}
const webEnv = path.join(root, "apps/web/.env.local");
mkdirSync(path.dirname(webEnv), { recursive: true });
if (!existsSync(webEnv)) {
  writeFileSync(webEnv, "API_BASE_URL=http://127.0.0.1:8000\n", { flag: "wx" });
}
console.log("Local configuration ready. Run pnpm db:up, then pnpm db:migrate.");
