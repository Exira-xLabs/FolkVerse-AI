/** Versioned decorative scenery. Original masters remain unchanged in /assets. */
export function museumArt(asset: string) {
  return asset === "09_ai_guide_character.png"
    ? "/folkverse/enhanced/09_ai_guide_character-lossless.webp"
    : `/folkverse/enhanced/${asset.replace(".png", "-v2.png")}`;
}
