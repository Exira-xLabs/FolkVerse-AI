# Phase 06 — Branching folklore and voice

**Prerequisite:** Guide and source flow working; reviewed story setting available.

**Outcome:** One complete story graph and optional live speech through a truthful state machine.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/06_STORIES_VOICE.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Implement one reviewed setting with a small finite story graph, e.g. 5–7 nodes, two decisions and reachable endings. Creative adaptations are visibly labelled and linked to factual context. Pre-reviewed text is the default. Optional generation uses allowed nodes/characters only and schema validation; no invented branch IDs or factual publication.

Persist story session and choices, reject stale node transitions, support restart and resume. Preserve the puppetry stage, gold buttons and player. Use real audio duration and captions. If no narrator audio exists, text mode works and audio is unavailable rather than fake playing.

Add voice adapter states idle, requesting_permission, recording, transcribing, transcript_ready, generating, speaking, cancelled/error. Users edit transcripts before sending to the existing guide. Implement one Chinese/English ASR and TTS provider only after checking actual documentation, region, credentials and pricing. Do not assume browser speech recognition works on all devices in China. Use a licensed system voice, not an unconsented imitation.

Support stopping narration, sentence replay where available, captions and mute. Do not autoplay. Raw audio cleanup must run. Recorded-demo clips remain labelled and must never pretend to answer a new live question. Guide girl is a visual companion; lip sync is optional post-pitch work, not required for the prototype.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] All story branches reach an ending; restart/resume/stale choices tested.
- [ ] Creative text distinguished from source-backed factual context.
- [ ] Mic denial, noisy/empty audio, cancellation and TTS failure preserve text usability.
- [ ] Live voice tested only if configured; otherwise report recorded/text fallback accurately.
- [ ] Captions and spoken content match approved answer/story text.


## Handoff
Story graph manifest, reviewed text, audio provenance and actual voice capability matrix.
