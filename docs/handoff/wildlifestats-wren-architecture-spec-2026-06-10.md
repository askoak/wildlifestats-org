# WREN architecture spec — WildlifeStats edition

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 15:23 ET
**Status:** Source of truth for Phase 7 engineer orders. Carries forward the WREN concept introduced in the BRWC lane; ground-up implementation here because §19 prevents copying BRWC code into this lane.
**Mike directive 2026-06-10 15:23 ET:** "build out our own WREN AI assistant that we started in the BRWC project ... data ingestion, cleaning, auditing, analysis, AI-linkages and cubes ... PhD biostats researcher to 80-year-old volunteer at a wildlife hospital navigate the secure pages."

## §1 — What WREN is, in one paragraph

WREN (Wildlife Research and Education Navigator) is an AI-mediated query and exploration layer over the WildlifeStats data assets. It accepts plain-language questions, returns plain-language answers, and exposes the underlying data and methodology on demand. It serves two audiences from one engine — a research-grade interface for biostatisticians who want the cube and the SQL, and a navigator-grade interface for hospital volunteers who want "what should I do if I find a baby raccoon" — separated by progressive disclosure, not by separate apps.

## §2 — Two surfaces, one engine

| Surface | URL | Auth | Data scope | Audience |
|---|---|---|---|---|
| Public WREN | `/wren/` | None | Synthetic cube + public methodology + Wildlife911 routing | Volunteers, public, finders of injured wildlife, researchers exploring the synthetic data |
| Secure WREN | `/secure/wren/` | Basic-auth (Phase 5) | Real partner records (when seeded), private notes, internal dashboards | Mike (now); future tiered partners |

**One engine, two configurations.** The differences are entirely in the data context the engine is given, not in the UI shell, the model, or the prompt structure.

## §3 — Progressive disclosure UX (the central UX gate)

The interface presents three tiers of detail, navigable from any answer:

1. **Plain answer.** A short, declarative response to the user's question. Two to four sentences. No jargon. No tables. No code. Cites the dataset by name (e.g. "Synthetic cube, n=100,000"). Example: "Window strikes are the second-most common admission reason for songbirds in the Northeast, peaking in September and October. To help a stunned bird, place it in a covered box in a quiet area and contact your nearest wildlife rehabilitator."
2. **The data.** A small table or chart that supports the plain answer. One click away — a "Show the data" affordance under every answer. Filterable. Downloadable as CSV (with k-suppression). Example: a year-by-year window-strike count for songbirds in the Northeast, with seasonal breakdown.
3. **The method.** The exact query that produced the data, plus a short note on what the data is (synthetic, n=100,000, calibrated against published literature, seed=42, generation script committed). One more click — a "How was this computed" affordance. Shows the cube path queried, the filters applied, and a link to the methodology page.

**The 80-year-old volunteer never has to click past tier 1.** The PhD biostatistician clicks straight to tier 3. The same engine produces all three; the user chooses how deep to go.

### §3.1 Affordance design

- "Show the data" — a small text button under every WREN answer. Sans-serif, muted color. No icon. Expands inline; does not navigate away.
- "How was this computed" — appears only after "Show the data" is expanded. Same styling, one level deeper. Expands a code block + methodology paragraph.
- Both affordances are keyboard-accessible. Tab navigation reaches them in document order. ARIA-expanded states are wired.

## §4 — The query layer

WREN's job is to translate a plain-language question into a cube query, run it, and produce a plain-language answer plus the raw data.

### §4.1 Query path

```
User question
  → Intent classification (one of: data_query, methodology_question, triage_question, definition_question, off_topic)
  → For data_query:
      → Cube-query plan (state, year, month, class, species, reason, outcome filters; aggregation)
      → Execute against admissions-cube.json (client-side, no backend)
      → Format result (table + chart)
      → Generate plain-language summary referencing the result
  → For methodology_question:
      → Retrieve relevant paragraph(s) from /methodology.html and /governance.html
      → Quote and cite
  → For triage_question (public WREN only):
      → Hard-coded routing to AnimalHelpNow + state-by-state directory
      → Never invent triage advice; always defer to the institutional directory
  → For definition_question:
      → Use a small curated glossary (committed JSON), not the LLM's general knowledge, for terms with WildlifeStats-specific meaning (e.g. "what is a 'reason'?")
  → For off_topic:
      → Polite redirect: "WREN focuses on the WildlifeStats synthetic dataset and wildlife rehabilitation methodology. For questions outside that scope, the National Wildlife Health Center and your state wildlife agency are better sources."
```

### §4.2 What runs where

- **Client (browser):** the WildlifeStats site. Hosts the cube JSON (already on disk after Phase 3), the WREN UI shell, query result rendering, and CSV downloads. No backend required for cube queries — the entire cube is < 8MB and lives in the browser.
- **LLM (Anthropic / Perplexity API):** intent classification, query plan generation, and plain-language summarization. **Stateless per turn.** No conversation memory beyond the current question + the cube schema + recent in-page results.
- **Cube query execution:** pure JavaScript over the in-memory cube. No SQL engine, no WASM database, no IndexedDB. Filtering + aggregation runs in tens of milliseconds for the full cube.

### §4.3 Cube schema as prompt context

The LLM call carries a compact representation of the cube schema in its system prompt — dimensions, valid values, units, and three example query plans. This is committed at `wildlifestats/_wren/schema-context.md` and updated automatically by a build step whenever the cube regenerates.

## §5 — Public vs. secure WREN configuration

The two surfaces differ in three places, no more:

| Aspect | Public WREN | Secure WREN |
|---|---|---|
| Data context | `data/cube/admissions-cube.json` (synthetic) | `data/cube/admissions-cube.json` + `secure/cube/partner-records.json` (real, when seeded) |
| System prompt | "You answer questions about the WildlifeStats synthetic dataset. You never invent triage advice and always redirect medical/clinical questions to AnimalHelpNow." | "You answer questions about the WildlifeStats partner records and the synthetic comparison dataset. The user is authenticated staff." |
| K-suppression | Enforced on all downloads (n<10 collapsed) | Disabled for authenticated users; small cells are exposed |

All other code, UI, prompt scaffolding, and infrastructure is shared.

## §6 — Audit and transparency

Every WREN interaction produces a transparent record:

- **In-UI:** every answer shows the query plan that produced it. Nothing is black-box.
- **Per-session log (client-side):** the browser keeps a log of `{question, query_plan, result_summary, timestamp}` in `sessionStorage`. Users can download their session log as JSON from a "Download my session" link in the WREN UI. No server-side log on the public tier — privacy by design.
- **Secure tier session log:** authenticated users' logs MAY be persisted server-side for audit when partner accounts arrive. Not in scope for Phase 7 initial build.

## §7 — Safety rails

### §7.1 No invented data

WREN must never produce a number that isn't from the cube query result. The plain-language summary references the result by quoting it, not by paraphrasing in a way that could drift. The prompt explicitly forbids fabricating counts.

### §7.2 No triage advice

For "what should I do if I find an injured animal" questions, WREN routes to AnimalHelpNow (ahnow.org) and the user's state directory. WREN never says "give it water" or "wrap it in a towel" or any specific action. The site's voice is research and methodology, not first-response medicine.

### §7.3 No clinical opinions

For "is this disease dangerous to humans" questions, WREN routes to CDC One Health resources and the user's state public-health agency. WREN summarizes the patterns visible in the cube but does not opine on individual or public risk.

### §7.4 Synthetic-data labeling

Every WREN answer that uses cube data carries an inline label: "Based on the WildlifeStats synthetic dataset (n=100,000, generated from regional distribution models calibrated against published literature)." Not at the bottom of the page. Inline with the answer.

### §7.5 Hallucination defense

WREN's system prompt includes the cube schema and explicit rules. If a query plan references a dimension or value not in the schema, the cube-query JS rejects it before the LLM produces a summary. The LLM cannot answer "show me data for Mars" because the cube has no Mars; the rejection is structural, not stylistic.

## §8 — Data pipeline (Phase 4.5, prerequisite for secure WREN)

WREN's secure tier needs a data pipeline that can:

1. **Ingest** heterogeneous Excel / CSV / JSON files from partner wildlife centers
2. **Clean** — field mapping, species name normalization, date parsing, missing-value handling
3. **Validate** — schema conformance, range checks, internal consistency
4. **Audit** — per-record provenance, transformation log, who/when/source-file
5. **Aggregate into a partner cube** — same schema as the synthetic cube, additional dimensions (partner_id, intake_id_hash)

This pipeline is Phase 4.5 — see `wildlifestats-data-pipeline-spec-phase4.5-2026-06-10.md`. Phase 7 (WREN) depends on Phase 4.5 only for the **secure** WREN surface. The **public** WREN surface depends only on the synthetic cube and ships independently.

## §9 — AI provider and credentials

- **Primary provider:** Anthropic Claude (Sonnet 4.5 or current default) for plain-language generation and intent classification. Reason: low hallucination rate, strong instruction-following, transparent refusal patterns.
- **API key location:** per §18, `C:\Users\Hello\OneDrive - Michael Oak Advisors\Credentials\anthropic.env` (architect default — engineer to confirm path with Mike if absent).
- **Calling pattern for public WREN:** browser calls a **Netlify Serverless Function** (NOT an Edge Function), which proxies to Anthropic with the API key. No API key in client code. **Function-type rationale, per Phase 4.6a hardening:** Netlify Edge Functions enforce a 50ms execution limit; Anthropic API calls have a median time-to-first-token of 200ms–3s. Building the WREN proxy as an Edge Function would time out on every request. Serverless Functions provide a 10-second default execution window (extendable to 26 seconds with background mode), which fits the Anthropic latency envelope. The function lives at `netlify/functions/wren.ts`.
- **Rate limits:** the Netlify function rate-limits per IP to 10 questions per minute. Public WREN is not a free LLM proxy — it's a research assistant for the WildlifeStats dataset specifically.
- **Cost ceiling:** the function refuses requests if a per-day cost ceiling is exceeded. Ceiling is an env var `WREN_DAILY_COST_USD`, default 10. The site continues to work in cube-only mode (filter UI from Phase 4) when WREN is rate-limited or cost-capped.

## §10 — Build phasing

Phase 7 is itself multi-stage. Each stage is its own engineer order.

| Stage | Deliverable | Effort |
|-------|-------------|--------|
| 7a | **Netlify Serverless Function** (not Edge Function — see calling-pattern rationale above) shell + Anthropic proxy + rate limits + cost ceiling | ~half day |
| 7b | WREN UI shell on `/wren/` — input, answer area, "Show the data" + "How was this computed" affordances, no real engine yet | ~half day |
| 7c | Intent classification + query-plan generation + cube execution wiring | ~full day |
| 7d | Triage routing + glossary + safety rails | ~half day |
| 7e | Session log download + accessibility audit (WCAG 2.1 AA) | ~half day |
| 7f | Secure WREN — same UI, mounted at `/secure/wren/`, behind the Phase 5 basic-auth | gated by Phase 5 completion |

Stages 7a–7e are the public WREN. They can ship sequentially after Phase 6 SEO polish. Stage 7f gates on the secure tier (Phase 5) which itself gates on Phase 4 stability.

## §11 — Cross-lane carryover (BRWC's WREN)

The BRWC lane started a WREN. Mike confirmed it on 2026-06-10 15:23 ET. This lane cannot read BRWC code directly (§19 — no BRWC content on the WildlifeStats public tier; the lane handoff explicitly says we don't even READ BRWC source).

**What we do:** build WREN-for-WildlifeStats from this spec, ground up. No code copy. No conceptual contamination beyond the shared name and the shared purpose.

**What we ask of BRWC:** a one-way CROSS-LANE file in this repo's `docs/handoff/CROSS-LANE-wren-conceptual-handoff-2026-06-10.md` describing — in plain English, no code — what BRWC's WREN does well, what didn't work, and any UX patterns that translated badly to volunteers. Architect-to-architect, not engineer-to-engineer. This file is authored by the BRWC architect on their next session, after they see the CROSS-LANE request file we ship in this batch.

The CROSS-LANE request file is the only WREN-related thing that crosses the lane boundary today. The build proceeds with or without BRWC's response.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 15:23 ET
