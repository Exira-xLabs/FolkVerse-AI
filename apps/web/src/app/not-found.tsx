"use client";
import Link from "next/link";
import { useLocale } from "@/components/locale-provider";
export default function NotFound() {
  const { locale } = useLocale(); const zh = locale !== "en";
  return <main className="missing-room glass-panel"><p className="eyebrow">404</p><h1>{zh ? "这个展厅尚未开放" : "We couldn’t find this room"}</h1><p>{zh ? "链接可能已更改。您可以返回首页或探索审核后的辽宁馆藏。" : "The link may have changed. Return home or explore the reviewed Liaoning collection."}</p><nav aria-label={zh ? "找回方向" : "Find your way"}><Link className="gold-button" href="/explore">{zh ? "探索辽宁" : "Explore Liaoning"}</Link><Link className="outline-button" href="/">{zh ? "返回首页" : "Return home"}</Link></nav></main>;
}
