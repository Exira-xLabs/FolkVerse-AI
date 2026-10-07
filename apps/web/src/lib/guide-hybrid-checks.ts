import type { GuideAnswer, GuideEvidence } from "@folkverse/contracts";

const same = (a: string[], b: string[]) => new Set(a).size === a.length &&
  new Set(b).size === b.length && a.length === b.length && a.every(id => b.includes(id));

function variants(p: GuideEvidence): Map<string, string> {
  if (p.evidence_origin === "official_lookup") return new Map((p.statement_variants ?? []).map(t => [t, "official_metadata_projection_v1"]));
  const result = new Map<string, string>([[p.text, "complete_reviewed_passage"]]);
  for (const text of p.statement_variants ?? []) result.set(text, "reviewed_variant_v1");
  const sentences = p.text.split(/(?<=[。！？])|(?<=[.!?])\s+(?=[A-Z])/);
  const qualified = /however|although|uncertain|disputed|alleged|possibly|unverified|according to|legend|belief|传说|据说|争议|可能|不确定|然而|但|尚未|(?:Dr|Mr|Mrs|Ms|Prof|St|No|vs|etc)\./i.test(p.text);
  if (sentences.length > 1 && !qualified) for (const sentence of sentences) {
    const text = sentence.trim();
    if (text !== p.text && text.length >= 15 && /[.!?。！？]$/.test(text) && !/^(?:(?:It|They|This|That|He|She)\b|它|该|其)/.test(text)) result.set(text, "complete_sentence_v1");
  }
  const en = /^(.+?) is listed as (.+?) (?:from|in) (.+?)\.$/.exec(p.text);
  const zh = /^(.+?)在.+?名录中列为(.+?)申报的(.+?)项目。$/.exec(p.text);
  if (p.language === "en" && en) {
    result.set(`The inventory records ${en[1]} under ${en[2]}, with ${en[3]} as the listed locality.`, "inventory_projection_v1");
    result.set(`${en[1]}: category — ${en[2]}; listed locality — ${en[3]}.`, "inventory_projection_v1");
  } else if (p.language === "zh-CN" && zh) {
    result.set(`名录把${zh[1]}列为${zh[3]}，申报地区为${zh[2]}。`, "inventory_projection_v1");
    result.set(`${zh[1]}：名录类别为${zh[3]}；申报地区为${zh[2]}。`, "inventory_projection_v1");
  }
  const simple = /^(.+?)列入(.+?)，地区为(.+?)。$/.exec(p.text);
  if (p.language === "zh-CN" && simple) result.set(`${simple[1]}：名录类别为${simple[2]}；名录所列地区为${simple[3]}。`, "inventory_projection_v1");
  return result;
}

export function checkedHybrid(answer: GuideAnswer, sources: GuideEvidence[]): boolean {
  if (answer.contract_version !== "hybrid_sections_v1" || answer.presentation_version !== "hybrid_sections_v1" ||
    answer.status !== "answered" || !Array.isArray(answer.sections) || !answer.sections.length || answer.sections.length > 4 ||
    !same(answer.evidence_ids ?? [], sources.map(p => p.passage_id)) ||
    !same(answer.answer_claim_ids ?? [], (answer.claims ?? []).map(c => c.claim_id)) || (answer.context_claim_ids ?? []).length) return false;
  const claims = answer.claims ?? [];
  if (claims.length > (answer.depth === "concise" ? 1 : 6)) return false;
  if (sources.some(p => p.language !== answer.locale || !["reviewed_corpus", "reviewed_unit", "official_lookup"].includes(p.evidence_origin ?? "reviewed_corpus"))) return false;
  const used = new Set<string>();
  for (const claim of claims) {
    if (!claim.passage_ids.length || !same(claim.passage_ids, [...new Set(claim.passage_ids)]) || claim.support_version !== "deterministic-support-v1") return false;
    const passages = claim.passage_ids.map(id => sources.find(p => p.passage_id === id));
    if (passages.some(p => !p || (p.classification ?? "source_statement") !== claim.kind ||
      variants(p).get(claim.text) !== claim.support_method || (p.required_support_ids ?? []).some(id => !claim.passage_ids.includes(id)))) return false;
    if (!same(claim.source_ids, [...new Set(passages.map(p => p!.source_id))])) return false;
    claim.passage_ids.forEach(id => used.add(id));
  }
  if (!same([...used], answer.evidence_ids ?? [])) return false;
  const refs: string[] = [], ids = new Set<string>();
  for (const section of answer.sections) {
    if (!section || typeof section.section_id !== "string" || ids.has(section.section_id) || typeof section.text !== "string" || !Array.isArray(section.claim_ids)) return false;
    ids.add(section.section_id);
    if (section.kind === "evidence") {
      if (!section.claim_ids.length || section.claim_ids.some(id => !claims.some(c => c.claim_id === id))) return false;
      const selected = section.claim_ids.map(id => claims.find(c => c.claim_id === id)!);
      const lookup = selected.some(c => c.passage_ids.some(id => sources.find(p => p.passage_id === id)?.evidence_origin === "official_lookup"));
      if (section.support_label !== (lookup ? "official_lookup" : "sources_checked") || section.text !== selected.map(c => c.text).join("\n\n")) return false;
      refs.push(...section.claim_ids);
    } else if (section.kind === "general") {
      if (section.claim_ids.length || section.support_label !== "general_unverified" || !section.text.trim() || section.text.length > 2400 ||
        /https?:\/\/|www\.|\]\(|\[claim|\[source|\d|originated|founded|dates? back|born in|according to|起源于|始建于|发源于|最早/i.test(section.text)) return false;
    } else return false;
  }
  const related = [...new Set(sources.filter(p => (p.evidence_origin ?? "reviewed_corpus") === "reviewed_corpus").flatMap(p => p.exhibit_ids))];
  return same(refs, claims.map(c => c.claim_id)) && answer.answer_text === answer.sections.map(s => s.text).join("\n\n") &&
    (answer.related_exhibit_ids ?? []).every(id => related.includes(id)) &&
    answer.reason === (claims.length ? "supported_explanation" : "general_explanation") &&
    answer.uncertainty === (claims.length ? "partial" : "insufficient");
}
