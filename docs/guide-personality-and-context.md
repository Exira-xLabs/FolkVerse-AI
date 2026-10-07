# Jinyao personality, language and consented context

Implemented Part 2 runtime, October 6, 2026. See [verification report](../report/PHASE_03_HYBRID_PART_02.md). This extends the current guide schema; the separate hybrid sections schema remains Part 4.

## Conversation behavior

Jinyao is a fictional AI cultural companion: warm, patient, brief and clear about evidence limits. The shared `jinyao-conversation-v2` policy contains bilingual openings and invitations for greeting, identity, thanks, start, goodbye, help, empathy and clarification. The model composes a reply by selecting permitted phrase IDs; it does not write unrestricted social prose. Both server and browser reconstruct and check the exact displayed text. Greetings/start/help invite a next step; thanks, goodbye and identity do not force a question.

Known social messages take one metered model call. A greeting attached to a supported cultural question keeps the whole factual request. Unknown messages without an identified published topic or scoped follow-up take a bounded model routing/composition call. The model reads the complete message and may propose a social intent or cultural route. A cultural route cannot supply prose, claims or sources and returns to the conservative evidence pipeline. A social route can display only policy phrases. Model routing therefore cannot grant factual authority; a classification can still be imperfect. Known unsupported requests about published topics retain the explicit coverage gap.

With consented recent turns, the last two replies exclude recently used openings/invitations. A returning greeting does not repeat the introductory opening; without history the “again” opening and continuity invitation are excluded. Without consent, option ordering varies without saving hidden visitor history. Repetition is possible across independent messages; no repeat-generation loop is added. Provider failures remain visible errors with recovery, including for greetings.

## Language and explanation preference

The UI offers Automatic, English and Chinese. In Automatic mode, Chinese/English message text guides the reply language; ambiguous emoji/punctuation keeps the current language. Quoted source names/text do not determine the surrounding reply language. An explicit whole-message language instruction overrides the selection for that message. Simpler/deeper follow-up variants change explanation depth. API consumers supply the locale explicitly; the API does not silently reinterpret that field.

Whole-message polite follow-ups normalize to supported commands. They still need an owned exhibit context or explicit exhibit scope for factual reference resolution. A request for meaning, significance or chronology does not become answerable merely because it is a follow-up. Broader cultural understanding, translated topic matching, free explanations and qualified general background belong to Part 4 and the reviewed data program.

## Consent and limits

- Context is off by default. No previous pairs or topic token are sent without consent.
- With consent, the browser sends at most six completed successful user/assistant pairs, at most 8,000 characters. Pending, error, cancelled, blank and oversized pairs are excluded; pairs are kept whole. A further 12,000-byte history bound leaves provider input room for the current question and server instructions.
- Each pair has only `user` (1–2,000 characters) and `assistant` (1–4,000). Extra keys/roles are forbidden. Server validators enforce consent, counts, individual lengths and combined character limits. Raw browser history is untrusted context, never evidence or system instructions.
- BFF and API enforce a 65,536-byte encoded body limit before forwarding/parsing. The current question remains limited to 2,000 characters. The provider also retains its independent input/output budget.
- Turning consent off clears the signed topic token and sends no history on the next request. This does not retract a previous provider request. Consent cannot be changed during a pending request.
- Signed topic/evidence references expire after 30 minutes, retain ownership/version checks, and are not refreshed by social turns. Raw history is not signed or written to the application database/logs.
- Page history retains the latest 100 turns with a truncation notice. Close/reopen preserves it; reload/unmount removes it. Provider processing follows the configured provider's policies; page-only application retention does not promise provider deletion.

The existing 40-second server, 60-second browser and 150-second BFF deadlines are retained. The browser bounds bootstrap and streaming as well as generation, and cancellation propagates upstream. Model routing and retries are inside the same server deadline and admission/budget gates.

## Local provider configuration

Production intent remains Ollama Cloud with its own credential/model/quota. The current owner's ignored `.env` selects direct DeepSeek for test runs. Verified October 6 against the authenticated model catalog: `DEEPSEEK_BASE_URL=https://api.deepseek.com`, `DEEPSEEK_MODEL=deepseek-flash`, which serves V4.1 Flash. The conservative configured rates are peak cache-miss input $0.30/million and output $1.20/million, with a $0.10 daily test budget. These are admission/accounting bounds, not a provider invoice. [Official model and pricing documentation](https://api-docs.deepseek.com/quick_start/pricing).

Keys remain server-only and untracked. No secret is included in reports or browser captures. Changing back to Ollama requires its own credential and a positive bounded request quota; a DeepSeek-issued key is not an Ollama credential.
