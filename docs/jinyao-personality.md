# Jinyao conversation policy v1

**Hybrid revision approved; implementation in progress.** This document describes the delivered restricted runtime below. The new behavior and migration gates are in [the execution plan](phase-03-hybrid-execution-parts.md) and [output contract](guide-hybrid-output-contract.md). Do not infer that planned generated social/general output is live.

Jinyao is a fictional FolkVerse museum companion. She answers directly, remains patient,
and invites exploration without attaching a repetitive question to every response. English
and Chinese use natural wording with equivalent meaning. She claims no personal history,
institutional authority or expertise beyond the current reviewed sources.

The versioned policy is `packages/contracts/src/jinyao-policy.json`. Server and browser use
the same allowlist. Greetings, identity, thanks and getting-started turns use this non-factual
policy without cultural retrieval or provider calls. They have `status=conversational`, no
claims/citations/provider attempt and no factual-answer latency. They are application policy
responses, not evidence of model generation. Full-match recognition prevents a social prefix
from bypassing cultural validation. Ownership and context expiry still apply.

Cultural answers require real approved evidence and a successful configured provider call.
The provider selects complete statements; the server validates their text, language, mappings,
published links and current eligibility before publication. Browser validation repeats the
claim/evidence/display checks. Provider failures never become policy success.

Beginner/deeper modes can reorder a recognized complete inventory statement into a constrained
explanation of its category and recorded locality. `presentation_version=inventory_projection_v1`
identifies that rendering. The original attributed statement and claim mappings remain visible.
Both boundaries independently reconstruct the explanation; extra prose fails publication.
The grammar retains the listing qualifier and introduces no date, origin, technique, definition,
historical importance or independent classification. Unrecognized statements remain excerpts.
Deeper mode explains the limits of the listing rather than inventing additional history.
This support method is deliberately bounded and still needs independent bilingual assessment.

Follow-ups resolve the consented topic without using previous answer prose as evidence. “Why?”
and glossary/importance requests resolve the reference but return a coverage gap when the
inventory cannot support them. Simplification/depth and language-switch commands adjust the
visitor's selected controls. Social turns and coverage gaps retain the existing client token;
they do not refresh its expiry. Withdrawal, expiry and ownership checks prevent later cultural
publication from reusing invalid context. Turning consent off discards it immediately.

Turns stay in page memory, up to 20, and survive popup close/reopen. Closing cancels a pending
request. Reload/unmount discards turns; no durable server chat history is added. Signed topic
and evidence context lasts 30 minutes and contains no raw questions or generated answers.
The provider receives cultural questions and bounded source text, not local social turns.

Independent human review is pending. The corpus currently supports one Liaoning heritage
listing, not a general Chinese-history expert. New content, glossary, chronology and attributed
interpretations require real editorial review before publication.
