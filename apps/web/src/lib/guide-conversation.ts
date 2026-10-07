import type { GuideAnswer, GuideRequest } from "@folkverse/contracts";

export type ReplyLanguage = "auto" | "en" | "zh-CN";

export function replyPreferences(text: string, previous: "en" | "zh-CN", depth: "concise" | "beginner" | "deeper", preference: ReplyLanguage) {
  const q = text.normalize("NFKC").toLowerCase().trim().replace(/[?.!。！？]+$/, "");
  const command = q.replace(/^(please |could you |can you )/, "").replace(/ please$/, "");
  const chinese = /^(say that in chinese|reply in chinese|answer in chinese|speak chinese|中文|请?用中文(?:说|回答|解释))$/.test(command);
  const english = /^(say that in english|reply in english|answer in english|speak english|english|请?用(?:英文|英语)(?:说|回答|解释))$/.test(command);
  // Quoted names/source text do not decide the language of an otherwise English request.
  const prose = q.replace(/"[^"\n]*"|“[^”\n]*”|「[^」\n]*」|『[^』\n]*』|`[^`\n]*`/g, "");
  const han = (prose.match(/[\u3400-\u9fff]/g) ?? []).length;
  const latin = (prose.match(/[a-z]+/g) ?? []).length;
  const locale = chinese ? "zh-CN" : english ? "en" : preference !== "auto" ? preference :
    han > 0 && (latin === 0 || han >= latin * 2) ? "zh-CN" : latin > 0 ? "en" : previous;
  const simpler = /^(explain that simply|simplify that|make it simpler|explain more simply|解释得简单一点|请?说简单一点|简单解释一下|i don't understand|i do not understand|我不明白|没看懂|不懂)$/.test(command);
  const deeper = /^(go deeper|explain more|tell me more|explain in more detail|more detail|详细一点|再详细一点|请详细解释)$/.test(command);
  return { locale, depth: simpler ? "beginner" as const : deeper ? "deeper" as const : depth };
}

export function recentConversation(turns: { question: string; status: string; answer?: Pick<GuideAnswer, "answer_text"> }[]): NonNullable<GuideRequest["conversation"]> {
  const result: NonNullable<GuideRequest["conversation"]> = [];
  let characters = 0, bytes = 0;
  for (const turn of [...turns].reverse()) {
    if (turn.status !== "ready" || !turn.answer) continue;
    const pair = { user: turn.question, assistant: turn.answer.answer_text };
    if (!pair.user.trim() || !pair.assistant.trim() || pair.user.length > 2000 || pair.assistant.length > 4000) continue;
    const size = pair.user.length + pair.assistant.length;
    const encoded = new TextEncoder().encode(pair.user + pair.assistant).length;
    // Leave room for this question, server instructions and evidence in the provider bound.
    if (characters + size > 8000 || bytes + encoded > 12000) break;
    result.unshift(pair); characters += size; bytes += encoded;
    if (result.length === 6) break;
  }
  return result;
}
