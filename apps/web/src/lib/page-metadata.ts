import "server-only";
import { cookies } from "next/headers";
import type { Metadata } from "next";
import { dictionaries } from "./i18n";
import type { PageKey } from "./routes";

export async function pageMetadata(page: PageKey): Promise<Metadata> {
  const locale = (await cookies()).get("folkverse_locale")?.value === "zh-CN" ? "zh-CN" : "en";
  return { title: { absolute: `${dictionaries[locale].nav[page]} | FolkVerse China` } };
}
