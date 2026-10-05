import { notFound } from "next/navigation";
import { MuseumShell } from "@/components/museum-shell";
import { routes, type PageKey } from "@/lib/routes";
import { applicationMode } from "@/lib/app-mode";
import { pageMetadata } from "@/lib/page-metadata";

export async function generateMetadata({ params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const key = (Object.keys(routes) as PageKey[]).find(key => routes[key].href === `/${slug.join("/")}`);
  if (!key) notFound();
  return pageMetadata(key);
}

export default async function MuseumPage({ params, searchParams }: { params: Promise<{ slug: string[] }>; searchParams: Promise<{ exhibit?: string | string[] }> }) {
  const { slug } = await params;
  const href = `/${slug.join("/")}`;
  const key = (Object.keys(routes) as PageKey[]).find(key => routes[key].href === href);
  if (!key) notFound();
  const { exhibit } = await searchParams;
  const initialExhibitId = typeof exhibit === "string" && exhibit.length <= 200 ? exhibit : undefined;
  return <MuseumShell page={key} mode={applicationMode()} initialExhibitId={initialExhibitId} />;
}
