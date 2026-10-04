import { MuseumShell } from "@/components/museum-shell";
import { applicationMode } from "@/lib/app-mode";

export default function HomePage() { return <MuseumShell page="home" mode={applicationMode()} />; }
