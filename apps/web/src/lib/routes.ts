export const routes = {
  home: { href: "/", asset: "01_museum_entrance.png", phase: 0 },
  explore: { href: "/explore", asset: "02_interactive_map.png", phase: 2 },
  journey: { href: "/journey", asset: "03_cultural_journey.png", phase: 4 },
  stories: { href: "/stories/lantern-path", asset: "04_shadow_puppetry.png", phase: 6 },
  lens: { href: "/lens", asset: "05_object_lens.png", phase: 5 },
  guide: { href: "/guide", asset: "06_ai_guide.png", phase: 3 },
  dna: { href: "/dna", asset: "07_folklore_dna.png", phase: 7 },
  sources: { href: "/sources", asset: "08_museum_everywhere.png", phase: 2 },
  status: { href: "/status", asset: "08_museum_everywhere.png", phase: 0 },
} as const;

export type PageKey = keyof typeof routes;
export const navigation: PageKey[] = ["explore", "journey", "stories", "lens", "guide", "dna"];
