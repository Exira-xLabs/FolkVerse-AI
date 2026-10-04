import { notFound } from "next/navigation";
import { MuseumShell } from "@/components/museum-shell";
import { routes, type PageKey } from "@/lib/routes";
import { applicationMode } from "@/lib/app-mode";

export default async function MuseumPage({ params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const href = `/${slug.join("/")}`;
  const key = (Object.keys(routes) as PageKey[]).find(key => routes[key].href === href);
  if (!key) notFound();
  return <MuseumShell page={key} mode={applicationMode()} />;
}
