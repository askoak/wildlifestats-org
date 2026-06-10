# Engineer order — Phase 7: WREN AI assistant

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer (`soar-aspen-beryl-heron`)
**Date:** 2026-06-10 ~15:23 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Phase 6 SEO + governance polish completes; Phase 4.5 data pipeline must also be merged for stage 7f gating)
**Authority:** §13 + §14.

## Source of truth

`docs/handoff/wildlifestats-wren-architecture-spec-2026-06-10.md`. Read it in full before starting any stage.

## Scope — six sub-PRs

| Sub-PR | Deliverable | Effort | Gate |
|---|---|---|---|
| 7a | Netlify serverless function shell + Anthropic proxy + per-IP rate limit + daily cost ceiling | ~half day | Phase 6 merged |
| 7b | WREN UI shell at `/wren/` — input box, answer area, "Show the data" + "How was this computed" affordances, no real engine yet (returns canned answer for testing) | ~half day | 7a merged |
| 7c | Intent classification + query-plan generation + cube execution wiring | ~full day | 7b merged |
| 7d | Triage routing + glossary + safety rails (synthetic-data labeling, no-invented-numbers guard, no-clinical-opinion guard) | ~half day | 7c merged |
| 7e | Session log download + WCAG 2.1 AA accessibility audit and fixes | ~half day | 7d merged |
| 7f | Secure WREN at `/secure/wren/` — same UI mounted behind Phase 5 basic-auth, configured against partner cube from Phase 4.5 | ~half day | Phase 5 merged AND Phase 4.5 merged AND 7a–7e merged |

## Acceptance criteria

### 7a — Function shell

1. `POST https://wildlifestats.org/.netlify/functions/wren` accepts `{question: "..."}`, proxies to Anthropic, returns the assistant response.
2. The Anthropic API key is read from a Netlify environment variable, NOT committed.
3. Per-IP rate limit: 10 requests per minute. 11th request returns `{error: "rate_limited", retry_after_seconds: N}`.
4. Daily cost ceiling: if `WREN_DAILY_COST_USD` is exceeded, function returns `{error: "cost_capped"}`. Cost is tracked client-side in a Netlify KV store (use `@netlify/blobs`).
5. CORS configured so only `wildlifestats.org` and the Netlify preview URLs can call the function.

### 7b — UI shell

1. `/wren/` loads with the standard site chrome (Phase 2 header, footer).
2. Input box centered, accepts up to 500 characters. Sans-serif placeholder reads "Ask a question about the data, the methodology, or how to find help for wildlife."
3. Below input: an answer area that initially shows: "Ask a question above. WREN focuses on the WildlifeStats synthetic dataset, the underlying methodology, and routing for wildlife rehabilitation referrals."
4. Submit → POST to the 7a function with a canned question, render whatever comes back as plain text in the answer area.
5. Below each answer, two affordances: "Show the data" (expands a placeholder table) and "How was this computed" (expands a placeholder code block).
6. Both affordances are buttons with `aria-expanded` state, keyboard-navigable, no icon dependencies.

### 7c — Engine wiring

1. The function (7a) now does real work: takes the user question, calls Anthropic for intent classification, generates a cube query plan, and returns `{intent, query_plan, plain_answer}`.
2. The UI (7b) executes the query plan client-side against `data/cube/admissions-cube.json`, formats the result, displays the plain answer + the result table.
3. "Show the data" reveals the actual table from the cube query.
4. "How was this computed" reveals the JSON query plan + a link to `/methodology.html`.
5. End-to-end test: asking "How many window strikes were recorded in the Northeast in 2024?" returns a real number from the cube, with the underlying table shown and the query plan exposed.

### 7d — Safety rails

1. Triage questions (regex on "what should I do", "I found", "injured", "baby", "orphan") trigger the AnimalHelpNow routing response with NO cube data attached.
2. Plain-language answers that include numbers cite the dataset inline ("Based on the WildlifeStats synthetic dataset (n=100,000)...").
3. A test fixture file (`wildlifestats/_wren/test-questions.json`) lists 20 questions with expected intent classifications + safety behaviors. CI runs these through the function and asserts behavior matches.
4. The system prompt is committed at `wildlifestats/_wren/system-prompt.md`. Versioned. Diffs reviewed.

### 7e — Accessibility and session log

1. WREN passes WCAG 2.1 AA on axe-core automated audit.
2. Keyboard navigation: input, submit, both affordances, all reachable in document order. Focus indicators visible.
3. Screen reader: input has a label, submit announces "Send question to WREN", affordances announce their expanded state.
4. "Download my session" link exports `sessionStorage` contents as a `.json` file.

### 7f — Secure WREN

1. `/secure/wren/` is reachable only with Phase 5 credentials. Unauthenticated requests get the standard `/secure/*` 401.
2. The UI shell is identical to public WREN — same code, different config.
3. The serverless function detects the `/secure/` referrer and switches data context to the partner cube from Phase 4.5.
4. K-suppression is disabled for authenticated sessions.

## Out of scope (defer to future orders)

- Multi-turn conversation memory beyond the current question (WREN is stateless per turn for now).
- User accounts (Phase 5 uses basic-auth; per-user accounts are a future tier).
- Image input (text only).
- Voice input/output (text only).
- Background scheduled queries / WREN-authored reports (future).
- Comparing WildlifeStats results to other public wildlife datasets (future).
- A separate "expert mode" UI for biostatisticians beyond the "How was this computed" affordance (the affordance IS expert mode; no separate UI).

## Commit and merge

- Six branches: `engineer/phase7a-function-shell` through `engineer/phase7f-secure-wren`.
- Commits: `feat(wildlifestats): WREN stage <N> — <name>`. Trailer: `Engineer: soar-aspen-beryl-heron`.
- Self-merge per §14 after CI green and the relevant acceptance criteria pass on the Netlify preview.
- After each merge, append a `## Resolution` entry to this file noting the merge commit. When 7f merges (or when WREN is shipped without 7f if Phase 5 hasn't landed), move this file to `closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 15:23 ET
