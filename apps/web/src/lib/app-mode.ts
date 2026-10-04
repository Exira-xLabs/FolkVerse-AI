import "server-only";
import { readFileSync } from "node:fs";
import path from "node:path";

// Read only the mode from the same root file used by FastAPI. Never expose its other values.
export function applicationMode(): "demo" | "live" {
  const explicit = process.env.APP_MODE;
  if (explicit) return explicit === "demo" ? "demo" : "live";
  try {
    const rootEnv = readFileSync(path.resolve(process.cwd(), "../../.env"), "utf8");
    return /^APP_MODE=demo\s*$/m.test(rootEnv) ? "demo" : "live";
  } catch { return "live"; }
}
