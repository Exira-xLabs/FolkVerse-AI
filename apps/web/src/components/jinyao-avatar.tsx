"use client";

import Image from "next/image";
import { useGraphics } from "./graphics-provider";

export function JinyaoAvatar({ size = 48 }: { size?: number }) {
  const { lowData } = useGraphics();
  return <span className="jinyao-avatar" style={{ width: size, height: size }} aria-hidden="true">
    {lowData ? "J" : <Image src="/folkverse/jinyao/portrait.webp" alt="" fill sizes={`${size}px`} />}
  </span>;
}
