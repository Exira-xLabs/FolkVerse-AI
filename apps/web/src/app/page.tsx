import { MuseumShell } from "@/components/museum-shell";
import { applicationMode } from "@/lib/app-mode";
import { pageMetadata } from "@/lib/page-metadata";

export function generateMetadata() { return pageMetadata("home"); }

export default function HomePage() { return <MuseumShell page="home" mode={applicationMode()} />; }
