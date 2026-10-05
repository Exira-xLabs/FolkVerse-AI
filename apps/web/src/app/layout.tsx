import type { Metadata } from "next";
import localFont from "next/font/local";
import { cookies } from "next/headers";
import "@fontsource/noto-sans-sc/400.css";
import "@fontsource/noto-serif-sc/400.css";
import "./globals.css";
import { LocaleProvider } from "@/components/locale-provider";
import { VisitProvider } from "@/components/visit-provider";
import { GraphicsProvider } from "@/components/graphics-provider";

const serif = localFont({ src: "./fonts/DejaVuSerif.ttf", variable: "--font-serif", display: "swap" });
const sans = localFont({ src: "./fonts/DejaVuSans.ttf", variable: "--font-sans", display: "swap" });

export const metadata: Metadata = {
  title: { default: "FolkVerse China — 华韵 AI", template: "%s | FolkVerse China" },
  description: "Explore China. Hear its stories. A bilingual cultural museum foundation preview.",
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const preferences = await cookies();
  const locale = preferences.get("folkverse_locale")?.value === "zh-CN" ? "zh-CN" : "en";
  const initialSimple = preferences.get("folkverse_graphics")?.value === "simple";
  return <html lang={locale}><body className={`${serif.variable} ${sans.variable}`}>
    <LocaleProvider initialLocale={locale}><GraphicsProvider initialSimple={initialSimple} initialLowData={preferences.get("folkverse_data")?.value === "low"}><VisitProvider>{children}</VisitProvider></GraphicsProvider></LocaleProvider>
  </body></html>;
}
