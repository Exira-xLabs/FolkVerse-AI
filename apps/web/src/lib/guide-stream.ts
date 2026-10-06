import type { GuideAnswer, GuideEvidence, GuideRequest } from "@folkverse/contracts";
import policy from "@folkverse/contracts/jinyao-policy.json";

export class GuideError extends Error {
  constructor(public code: string) { super(code); }
}

export type GuideReply = { answer: GuideAnswer; firstContentMs: number | null };
export type GuideStage = "connecting" | "retrieving" | "generating" | "validating";
const object = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);
const strings = (v: unknown): v is string[] => Array.isArray(v) && v.every(x => typeof x === "string");

function answerShape(v: unknown): v is GuideAnswer {
  return object(v) && typeof v.answer_id === "string" && typeof v.answer_text === "string" &&
    v.answer_text.length <= 50000 && ["answered", "insufficient", "clarification", "conversational"].includes(String(v.status)) &&
    ["en", "zh-CN"].includes(String(v.locale)) && ["concise", "beginner", "deeper"].includes(String(v.depth)) &&
    v.mode === "live" && ["partial", "insufficient"].includes(String(v.uncertainty)) &&
    typeof v.coverage_limit === "string" && strings(v.evidence_ids) && strings(v.related_exhibit_ids) &&
    strings(v.answer_claim_ids) && strings(v.context_claim_ids) && Array.isArray(v.claims) && v.claims.length <= 3 &&
    v.claims.every(c => object(c) && typeof c.claim_id === "string" && typeof c.text === "string" &&
      c.kind === "source_statement" && c.support_method === "complete_reviewed_passage" &&
      strings(c.passage_ids) && strings(c.source_ids));
}

function sourcesShape(v: unknown): v is GuideEvidence[] {
  return Array.isArray(v) && v.length <= 8 && v.every(p => object(p) &&
    ["passage_id", "source_id", "text", "locator", "canonical_url", "source_title", "institution", "rights_basis", "reviewed_at", "reviewer", "fetched_at"].every(k => typeof p[k] === "string") &&
    ["en", "zh-CN"].includes(String(p.language)) && strings(p.exhibit_ids));
}

function checkedPublication(answer: GuideAnswer, sources: GuideEvidence[]): boolean {
  const claims = answer.claims ?? [];
  const evidence = answer.evidence_ids ?? [];
  const refs = [...(answer.answer_claim_ids ?? []), ...(answer.context_claim_ids ?? [])];
  if (answer.status === "conversational") {
    const intent = answer.social_intent;
    return !!intent && Object.hasOwn(policy.social, intent) && answer.personality_version === policy.version &&
      answer.answer_text === policy.social[intent][answer.locale] && !answer.coverage_limit &&
      !claims.length && !sources.length && !evidence.length && !refs.length &&
      !(answer.related_exhibit_ids ?? []).length && !answer.provider_attempt_id;
  }
  if (answer.status !== "answered") return !claims.length && !sources.length && !evidence.length && !refs.length;
  const sameIds = (a: string[], b: string[]) => new Set(a).size === a.length &&
    new Set(b).size === b.length && a.length === b.length && a.every(id => b.includes(id));
  if (!claims.length || !sameIds(refs, claims.map(c => c.claim_id)) ||
    !sameIds(evidence, sources.map(p => p.passage_id)) ||
    sources.some(p => p.language !== answer.locale)) return false;
  const claimed = new Set<string>();
  for (const claim of claims) {
    if (!claim.passage_ids.length || new Set(claim.passage_ids).size !== claim.passage_ids.length) return false;
    const passages = claim.passage_ids.map(id => sources.find(p => p.passage_id === id));
    if (passages.some(p => !p || p.text !== claim.text)) return false;
    const sourceIds = [...new Set(passages.map(p => p!.source_id))];
    if (!sameIds(claim.source_ids, sourceIds)) return false;
    claim.passage_ids.forEach(id => claimed.add(id));
  }
  if (!sameIds([...claimed], evidence)) return false;
  const sections = refs.map(id => {
    const claim = claims.find(c => c.claim_id === id)!;
    const labels = [...new Set(claim.passage_ids.map(pid => {
      const passage = sources.find(p => p.passage_id === pid)!;
      return `${passage.source_title} (${passage.institution})`;
    }))].sort();
    return `${labels.join("; ")}:\n${claim.text}`;
  });
  const lead = answer.locale === "en" ? "Here is what the reviewed source says:" : "经过审核的来源这样记载：";
  let projection = "";
  if (answer.presentation_version === "inventory_projection_v1") {
    if (answer.depth === "concise") return false;
    const text = claims.find(c => c.claim_id === refs[0])!.text;
    const match = answer.locale === "en"
      ? /^([A-Za-z -]+) is listed as ([A-Za-z -]+) (?:from|in) ([A-Z][a-z]+(?:[ ,'-]+[A-Z][a-z]+)*)\.$/.exec(text)
      : /^([\u3400-\u9fff]+)在[\u3400-\u9fff]+名录中列为([\u3400-\u9fff]+)申报的([\u3400-\u9fff]+)项目。$/.exec(text);
    if (!match) return false;
    const fields: Record<string, string> = { title: match[1], category: match[answer.locale === "en" ? 2 : 3], location: match[answer.locale === "en" ? 3 : 2] };
    projection = policy.projection[answer.locale][answer.depth].replace(/\{(title|category|location)\}/g, (_, name: string) => fields[name]) + "\n\n";
  } else if (answer.presentation_version && answer.presentation_version !== "attributed_excerpt_v1") return false;
  return answer.answer_text === `${projection}${lead}\n\n${sections.join("\n\n")}`;
}

async function receiveGuide(
  payload: GuideRequest, signal: AbortSignal, onStage: (stage: GuideStage) => void,
): Promise<GuideReply> {
  onStage("connecting");
  const session = await fetch("/api/v1/session", { method: "POST", signal, credentials: "same-origin" });
  if (!session.ok) throw new GuideError("session_unavailable");
  const started = performance.now();
  const response = await fetch("/api/v1/guide", {
    method: "POST", credentials: "same-origin", signal,
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    let code = "guide_unavailable";
    try { const body: unknown = await response.json(); if (object(body) && object(body.error) && typeof body.error.code === "string") code = body.error.code; } catch { /* Sanitized generic error. */ }
    throw new GuideError(code);
  }
  if (!response.headers.get("content-type")?.includes("text/event-stream") || !response.body) throw new GuideError("invalid_stream");
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8", { fatal: true });
  let buffer = "", bytes = 0;
  let answer: GuideAnswer | undefined, sources: GuideEvidence[] | undefined;

  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      bytes += chunk.value.length;
      if (bytes > 262144) throw new GuideError("invalid_stream");
      buffer += decoder.decode(chunk.value, { stream: true });
      let separator: RegExpExecArray | null;
      while ((separator = /\r?\n\r?\n/.exec(buffer))) {
        const frame = buffer.slice(0, separator.index).replace(/\r/g, ""); buffer = buffer.slice(separator.index + separator[0].length);
        const lines = frame.split("\n");
        const event = lines.find(line => line.startsWith("event: "))?.slice(7);
        const body = JSON.parse(lines.filter(line => line.startsWith("data: ")).map(line => line.slice(6)).join("\n")) as unknown;
        if (!object(body)) throw new GuideError("invalid_stream");
        if (event === "error") throw new GuideError(object(body.error) && typeof body.error.code === "string" ? body.error.code : "guide_unavailable");
        if (event === "status") {
          if (!["retrieving", "generating", "validating"].includes(String(body.stage))) throw new GuideError("invalid_stream");
          onStage(body.stage as GuideStage);
        } else if (event === "answer") {
          if (answer || !answerShape(body) || body.locale !== payload.locale || body.depth !== payload.depth) throw new GuideError("invalid_stream");
          answer = body;
        } else if (event === "sources") {
          if (!answer || sources || body.answer_id !== answer.answer_id || !sourcesShape(body.items)) throw new GuideError("invalid_stream");
          sources = body.items;
        } else if (event === "done") {
          if (!answer || !sources || body.answer_id !== answer.answer_id) throw new GuideError("invalid_stream");
          if (!checkedPublication(answer, sources)) throw new GuideError("invalid_stream");
          return { answer: { ...answer, sources }, firstContentMs: answer.status === "answered" ? Math.round(performance.now() - started) : null };
        } else if (event !== "meta" && event !== "status") throw new GuideError("invalid_stream");
      }
    }
    throw new GuideError("incomplete_stream");
  } finally {
    await reader.cancel().catch(() => undefined);
    reader.releaseLock();
  }
}


// Covers session bootstrap as well as response streaming: a stalled connection must
// not leave the composer pending indefinitely. Caller cancellation remains distinct.
export async function sendGuide(
  payload: GuideRequest, signal: AbortSignal, onStage: (stage: GuideStage) => void,
): Promise<GuideReply> {
  const deadline = new AbortController();
  const timer = setTimeout(() => deadline.abort(), 60000);
  try {
    return await receiveGuide(payload, AbortSignal.any([signal, deadline.signal]), onStage);
  } catch (error) {
    if (deadline.signal.aborted && !signal.aborted) throw new GuideError("guide_timeout");
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
