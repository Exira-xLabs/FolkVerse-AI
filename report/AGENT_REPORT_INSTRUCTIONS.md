# FolkVerse — instructions for the reporting agent

Give this file to the agent working in your implementation repository. Its task is to produce an evidence-backed report showing whether the implementation follows the exact Markdown instructions in this build kit.

## Task

Inspect the real repository, read the instruction files below, verify the implemented work, and write `report/AGENT_REPORT.md` in the implementation repository. Create `report/` if needed. This file is the reporting brief, not a completed project report.

Report the actual state of the project. Do not assume the build kit itself contains a working application. If only the kit is available, report that limitation and mark implementation checks as unverified. Do not create an application just to fill in this report.

## Read the exact source instructions

Find the build kit at the repository root or under `docs/build-kit/`. Resolve the following paths against that location. Read the full files, including prerequisites, prompts, acceptance gates and handoff requirements; summaries are not substitutes.

1. Read applicable `AGENTS.md` files, inspect Git status, and preserve unrelated changes.
2. Read `README_START_HERE.md` and `00_MASTER_CODEX_PROMPT.md`.
3. Read `01_OPENDESIGN_UI_PROMPTS.md`.
4. Read all three specifications:
   - `specs/ARCHITECTURE_AND_COSTS.md`
   - `specs/DATA_AND_API_CONTRACTS.md`
   - `specs/CONTENT_AND_AI_RULES.md`
5. Read every phase file in numerical order:
   - `phases/00_FOUNDATION.md`
   - `phases/01_VISUAL_UI.md`
   - `phases/02_CONTENT_MAP.md`
   - `phases/03_GROUNDED_GUIDE.md`
   - `phases/04_PERSONAL_JOURNEYS.md`
   - `phases/05_OBJECT_LENS.md`
   - `phases/06_STORIES_VOICE.md`
   - `phases/07_DNA_RECOMMENDATIONS.md`
   - `phases/08_INTEGRATION_RELEASE.md`
6. Read `QA_AND_DEMO.md` and `SOURCES_AND_TRACEABILITY.md`.
7. Inspect `assets/ASSET_MANIFEST.json`, the actual `references/ui/` images, and available `design/opendesign/` exports when evaluating visual work.
8. Read available implementation records: `docs/build-status.md`, `docs/decisions.md`, `docs/design-differences.md`, setup instructions, dependency manifests/locks, tests and evidence files.

List every required file as read or missing in the report. Do not silently skip a missing document. The source documents remain authoritative: this reporting brief does not replace their requirements. Quote or reference the exact file and section for each finding. If instructions conflict, identify the conflict and the applicable instruction hierarchy; do not invent a resolution or claim compliance with both.

## Verification rules

- Check actual code and behavior before accepting previous status notes. Record the repository path, branch, commit, uncommitted changes and report date/time with timezone.
- Follow the phase prerequisites and acceptance gates exactly. A gate passes only when evidence supports it; a checked box or plausible code is insufficient.
- Run relevant, documented local checks when possible. Record exact commands, exit codes, results and evidence paths. Report unavailable services, credentials, tools and environments explicitly. Do not expose secret values in the report or logs.
- Separate **live implementation**, **labelled deterministic demo fixtures**, **untested implementation**, **unavailable capability**, and **planned/deferred work**. A fixture does not prove a live integration.
- Separate target counts and metrics from measured results. Report actual reviewed exhibits, eligible artifacts, sample sizes, versions and failures. Do not invent approval, rights clearance, users, benchmark photos, accuracy, partnerships or provider calls.
- Verify the original museum artwork, guide character, routes and bilingual UI against the visual specification. Capture screenshots only from a running application. Check 1600×900, 390×844, 768×1024, keyboard behavior, 200% zoom and reduced motion where possible. Record visual deviations and unavailable checks.
- Check the relevant API schemas, error states, source/citation boundaries, catalog candidate restrictions, session ownership, consent, reset/deletion, private media cleanup and server-side credentials according to the specs and active phases.
- Keep generated decorative imagery separate from authoritative map geometry, recognition references and benchmarks. Recorded narration is not live speech; a visual shell is not a completed AI feature.
- Recheck official documentation when verifying current provider model IDs, request formats, dependencies, rights or prices. Include verification dates. Documentation access alone does not prove authenticated integration.
- Report generation permits inspection, appropriate local verification and report/evidence output. Preserve the app and supplied assets; do not make unrelated fixes, change system configuration, spend money, deploy publicly or submit competition materials through this task.

## Required report structure

Use the following headings in `report/AGENT_REPORT.md`. Fill every section with actual findings; use explicit missing/unverified entries when evidence is absent.

### 1. Repository and scope

Identify the repository, commit, working tree, environment, build-kit location, active phase and inspected scope. State whether application source and a runnable environment were available.

### 2. Instructions reviewed

| Instruction file | Read / missing | Relevant sections and observations |
|---|---|---|

Include every file listed in the reading order and applicable repository instructions.

### 3. Phase compliance

| Phase | Status | Passed / total acceptance gates | Evidence | Remaining work |
|---|---|---|---|---|

Include phases 00–08. Use **complete**, **partial**, **not started**, **blocked**, or **unverified**. For each phase, reproduce every acceptance gate as written in its source file, then mark it **PASS**, **FAIL**, **UNVERIFIED**, or **DEFERRED** with concrete evidence. Deferred gates do not pass. Explain unmet prerequisites. Do not declare a phase complete while a required gate lacks evidence.

### 4. Feature capability matrix

| Feature / route | Live / fixture / untested / unavailable / planned | Working behavior | Failure states checked | Evidence |
|---|---|---|---|---|

Cover Home, Explore/map, exhibits/sources, Journey, Guide, Stories, Lens, voice, My DNA/recommendations, saved state and Chinese/English. Split mixed capabilities into separate rows when needed.

### 5. Verification results

| Check | Exact command or manual procedure | Exit code / outcome | Environment and sample size | Evidence path |
|---|---|---|---|---|

Include relevant startup, database/API health, contracts, lint/typecheck/build, functional workflows, security/privacy, grounding/unknown behavior and visual checks. Distinguish newly run checks from older recorded evidence. Include failures and skipped checks with reasons.

### 6. Content, rights and AI evidence

State actual corpus counts and review status, rights/provenance records, provider mode/configuration names, retrieval method, citation validation, recognition limitations and voice mode. Report measured metrics separately from the targets in `QA_AND_DEMO.md`; include sample sizes and versions.

### 7. Deviations and blockers

| Requirement: file and section | Actual behavior | Impact | Evidence | Required action |
|---|---|---|---|---|

Include both documented deviations and newly found discrepancies. Identify missing credentials, human reviews, hardware or other prerequisites without fabricating their completion. Do not assign people or roles unless already agreed.

### 8. Handoff and next actions

Give the next unfulfilled phase/gate, ordered concrete actions, reproducible run/check commands and evidence locations. Explain whether the available evidence supports a local demo. Distinguish successful startup, functional completion and pitch readiness. If updating `docs/build-status.md` or `docs/decisions.md` is outside the assigned reporting scope, list the exact updates needed instead of silently editing them.

## Final delivery

Verify that every phase and acceptance gate is represented, every PASS has evidence, links resolve, and the report contains no secrets or fabricated results. End the agent's response with the report path, a concise readiness statement and the most important unresolved gate. Do not replace the report with a conversational summary.
