/** Versioned decorative scenery. Original masters remain unchanged in /assets. */
export function museumArt(asset: string) {
  return asset === "09_ai_guide_character.png"
    ? "/folkverse/enhanced/09_ai_guide_character-lossless.webp"
    : `/folkverse/enhanced/${asset.replace(".png", "-v2.png")}`;
}

/** Focal crops for small decorative covers; heroes retain their full phone frame. */
export function museumArtFocus(asset: string, usage: "card" | "thumbnail") {
  const focus: Record<string, [string, string]> = {
    "02_interactive_map.png": ["68% 50%", "72% 50%"],
    "03_cultural_journey.png": ["83% 58%", "83% 66%"],
    "04_shadow_puppetry.png": ["78% 46%", "83% 44%"],
    "07_folklore_dna.png": ["76% 50%", "77% 48%"],
    "09_ai_guide_character.png": ["center", "center"],
  };
  return focus[asset]?.[usage === "card" ? 0 : 1] ?? "75% center";
}
