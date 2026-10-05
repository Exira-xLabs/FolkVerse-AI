import { notFound } from "next/navigation";
import { MuseumShell } from "@/components/museum-shell";
import { routes, type PageKey } from "@/lib/routes";
import { applicationMode } from "@/lib/app-mode";

export default async function MuseumPage({ params, searchParams }: { params: Promise<{ slug: string[] }>; searchParams: Promise<{ exhibit?: string | string[] }> }) {
  const { slug } = await params;
  const href = `/${slug.join("/")}`;
  const key = (Object.keys(routes) as PageKey[]).find(key => routes[key].href === href);
  if (!key) notFound();
  const { exhibit } = await searchParams;
  const initialExhibitId = key === "explore" && typeof exhibit === "string" && exhibit.length <= 200 ? exhibit : undefined;
  return <MuseumShell page={key} mode={applicationMode()} initialExhibitId={initialExhibitId} />;
}
