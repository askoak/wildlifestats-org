# Engineer order — Phase 4.5+f through 4.5+j: Flyway social/phenology pipeline

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer (`soar-aspen-beryl-heron`)
**Date:** 2026-06-10 ~19:30 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main`
**Authority:** §13 + §14.
**Source of truth:** `docs/handoff/wildlifestats-flyway-spec-2026-06-10.md`.

This order extends the Phase 4.5+ source-registry engineer order. Five new sub-PRs (`f` through `j`) for the Flyway pipeline. The previously-dispatched Phase 4.5+a through 4.5+e for the ten Tier 1 open-API sources continues independently; Flyway is additive, not blocking.

## Resolution of the engineer's INBOX ask

`INBOX-engineer-social-early-warning-2026-06-10.md` is hereby resolved by the Flyway spec. Engineer may close the INBOX file with a `## Architect Resolution` section citing the spec file path. The engineer's POC offer (3-5 pages × hummingbird phrase search) IS the smoke test inside sub-PR 4.5+g — not a separate pre-spec deliverable.

## The five sub-PRs

| Sub-PR | Deliverable | Gate to next |
|---|---|---|
| **4.5+f** | Source registry entries (`flyway-social-pages`, `flyway-phrase-search`, `journey-north`), storage layout under `wildlifestats/_pipeline/sources/flyway/`, `signal-schema.json`, first 8 signal-definition JSON files, public `/methodology/flyway/` page. **No scraping.** | Merged + CI green |
| **4.5+g** | Apify client + extraction pipeline (`extract.py`) + LLM extraction prompt at `wildlifestats/_pipeline/flyway/extraction-prompt.md`. Manual smoke test on 3-5 Pages × hummingbird signal (the engineer's offered POC). Run logged in the PR description; cost noted. | Merged + smoke-test results documented in PR |
| **4.5+h** | Baseline computation (`baseline.py`) + anomaly trigger logic (`triggers.py`). Bootstrap baselines from synthetic cube seasonality (since real Flyway history doesn't exist yet). Validation: rerun the 4.5+g smoke-test data through baseline+trigger and confirm at least one trigger fires correctly for a manually-injected anomaly. | Merged + validation run shown |
| **4.5+i** | Daily GH Actions cron at `.github/workflows/flyway-daily.yml`. Full 99-Page roster active. **Cron is committed but DISABLED by default** — the workflow's `on:` block uses `workflow_dispatch` only until Mike authorizes recurring cost. Documented in the PR body. | Merged. Cron stays manual-only until Mike authorizes. |
| **4.5+j** | Research-tier dashboard at `/secure/research/flyway/` (gated behind Phase 5 researcher role when 5c lands; until then, a static placeholder page) + WREN context integration (Flyway signals available in WREN's data context for both research and reference tiers, with appropriate aggregation). | Merged + manual demo confirmed |

## Acceptance criteria

Per sub-PR, the standard CI requirements (BRWC content guard, link check, HTML validate, pipeline-dry-run) all pass. In addition:

### Sub-PR 4.5+f

1. Three source registry entries committed under `wildlifestats/_pipeline/sources/`.
2. `wildlifestats/_pipeline/sources/flyway/signal-schema.json` exists and validates as JSON Schema draft 2020-12.
3. Eight signal-definition files exist under `wildlifestats/_pipeline/sources/flyway/signals/`, each conforming to the schema.
4. `/methodology/flyway/index.html` is live on the Netlify preview, accessible without auth, and explains the pipeline + legal posture.
5. Public homepage and `/methodology.html` link to the new methodology page.

### Sub-PR 4.5+g

1. `wildlifestats/_pipeline/flyway/extract.py` runs against a sample post JSON and produces a typed signal record.
2. Apify client wrapper at `wildlifestats/_pipeline/flyway/apify_client.py` uses the existing `APIFY_TOKEN` env var (no new credential setup).
3. **No raw post text is written to disk.** Verify by reviewing `secure/cube/flyway/audit/` after the smoke test — `post_text_NOT_STORED: true` on every record.
4. Smoke-test results are documented in the PR description with: posts scraped, records extracted, total Apify cost, total LLM cost.
5. The smoke test exercises both Facebook and Instagram via Apify's official actors.

### Sub-PR 4.5+h

1. `baseline.py` produces a baseline JSON per signal at `secure/cube/flyway/baselines/<signal-id>.json`.
2. Bootstrap from synthetic-cube seasonality is documented (which cube fields, which formula).
3. `triggers.py` evaluates current observations against baseline and emits `secure/cube/flyway/triggers/<YYYY-WW>.json`.
4. Validation: an artificially-injected spike (e.g. 100 records in one week for a signal that normally sees ~5) fires the spike trigger correctly.

### Sub-PR 4.5+i

1. `.github/workflows/flyway-daily.yml` exists with `on: workflow_dispatch` only.
2. A manual workflow run against the full 99-Page roster completes successfully (Apify cost documented in the PR).
3. Workflow handles per-Page failures gracefully (failed Pages logged, run continues for the rest).
4. PR body explicitly notes: "Daily schedule is COMMENTED OUT until Mike authorizes recurring spend. To activate, uncomment the `schedule:` block in flyway-daily.yml."

### Sub-PR 4.5+j

1. `/secure/research/flyway/` returns 200 on the Netlify preview when authenticated as `researcher` role (or returns 401 if Phase 5 isn't yet in place).
2. The page renders a placeholder dashboard (map stub, signal list stub) if no Flyway data exists yet, OR a real dashboard if 4.5+g/h/i populated data.
3. WREN's system prompt is updated to include Flyway context. Confirm by asking WREN "what hummingbird signals have come in this week" and verifying it consults the Flyway signal store.

## Out of scope

- TikTok / YouTube scraping for the first ship (the roster CSV includes those columns; ingest them in a follow-on sub-PR after the FB+IG baseline proves out).
- Re-syndication of scraped content (explicitly prohibited per spec §6).
- Phrase-search discovery loop UI for Mike to review candidate Pages — defer to a Phase 4.5+k once the monitored-roster path is stable.
- Multilingual extraction (English only for first ship).
- A separate Flyway-only iOS/Android app.

## Mike-only decisions (surfaced; do not block)

The Flyway spec §11 lists four decisions. The engineer ships 4.5+f without any of them resolved. As later sub-PRs approach the decision points, surface them via INBOX if Mike hasn't volunteered an answer:

- Before 4.5+g's manual smoke test: Mike's go for spending ~$5-10 of Apify credit on the POC.
- Before 4.5+i activates the daily cron: Mike authorizes the ~$50-100/month recurring spend.
- Before integrating Journey North as a real source (sub-PR 4.5+f or 4.5+j depending on access path): Mike's input on Journey North's license/API status.

Architect default if Mike is silent: stop at the cost-authorization gate; do not activate the daily cron without authorization. The pipeline ships as `workflow_dispatch`-only and waits.

## Commit and merge

- Five branches: `engineer/phase4.5+f-flyway-registry` through `engineer/phase4.5+j-flyway-dashboard`.
- Commit format: `feat(wildlifestats): Phase 4.5+<letter> — <short description>`.
- Trailer: `Engineer: soar-aspen-beryl-heron`.
- Self-merge per §14 after CI green + the sub-PR's acceptance criteria.
- After each merge, append a `## Resolution 4.5+<letter>` entry to this order file. After 4.5+j merges, move this file to `docs/handoff/closed/`.

## Engineer-lane slow-pace note (per §8.5 of SLOW-PACE-PROTOCOL)

These five sub-PRs are perfect §8.5 units — one focused PR per turn, clean checkpoints, reuse shipped helpers. The engineer's existing slow-pace operating mode applies unchanged.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:30 ET
