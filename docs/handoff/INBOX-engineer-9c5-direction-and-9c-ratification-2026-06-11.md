# INBOX — Phase 9c.1-9c.4 ratified + 9c.5 direction (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 13:40 ET
**Channel:** Autonomous mode — Mike directed engineer to communicate with architect via this lane, not via session UI prompts.
**Re:** PRs #42, #43, #44, #45 ratification + 9c.5 question routed from your session

## 9c.1-9c.4 ratified

Strong work across four sub-PRs in ~30 minutes. Specifically:

- **PR #42 fetch.py (b751caf)** — robots-aware + rate-limited + cached + dating envelope, all live with monkeypatched HTTP tests proving the gates fire correctly. The "robots cannot be verified → refuse to proceed" path is particularly important; that's the correct interpretation of robots-respect under uncertainty.
- **PR #43 exa_client.py (a5d863d)** — canonical-URL discovery with host-matched ranking + dedupe + validate_candidate doing real content sanity-checking.
- **PR #44 claude_client.py (697c1a9)** — structured extraction with the verbatim-quote discipline gate firing on mission_statement. This was the load-bearing defensive check; you implemented it.
- **PR #45 apify_client.py (7af8de8)** — 5-platform actor support, audit-log discipline preserved from the Flyway POC, no-raw-text drop verified in tests.

Test gates grew from 13 → 29 with each implementation. All 29 pass; live tests properly env-flag-gated behind `WILDLIFESTATS_LIVE_*`. CI green throughout. This is exactly the cadence and discipline the engineer order called for.

## 9c.5 question — direction is option 1, ship the harness no-spend

You asked Mike (in session) how to execute the 9c.5 integration smoke given no vault credentials in your session. Mike routed the question to the autonomous channel. Adjudication:

**Ship the no-spend harness. Defer live execution.** Concretely:

- **9c.5 PR contents:**
  - A runner script `scripts/run-9c5-smoke.sh` (or `wildlifestats/_pipeline/_common/run_smoke.py` — your preference) that invokes one live call per client.
  - Per-client invocation documented in PR body and script comments: the exact `WILDLIFESTATS_LIVE_*` env flag, the credential handle name (`custom-cred:api.exa.ai`, etc.), the per-call expected output shape.
  - Per-client cost estimate (Exa ~$0.50, Claude ~$1, Apify ~$1, Voyage optional ~$0.50) and the **$5 hard cap** total across all four. The script aborts before issuing the next call if cumulative cost would exceed $5.
  - A README section at `wildlifestats/_pipeline/_common/README-smoke.md` documenting how to run it: invoke `bash` with the four credential handles in `api_credentials`, run the script, paste the structured results into a follow-up PR or INBOX.
  - Live execution deferred. NOT spent in this PR.

- **Why this option, not the others:**
  - Option 2 (Mike runs locally): works but introduces a paste-back round-trip that's unnecessary when the script can just be invoked in a credentialed environment.
  - Option 3 (inject creds into your session): violates the 2026-06-11 09:30 credential discipline. Tokens are env-injected via vault handles for the duration of a single bash invocation, never pasted into chat sessions where they live in conversation memory. Don't.
  - Option 4 (skip 9c.5, go to 9d): tempting because 9d live writes are blocked on the PostgREST Exposed-Schemas cross-lane #290 anyway. But skipping the live-validation of the four `_common` clients before they're composed into bucket pipelines hides bugs until 9d, when the bugs are harder to localize. Live-validate the components before composing.

- **Why option 1 wins:** the framework is fully scaffolded by end of day, the discipline is preserved, and live execution slips by hours-not-days to whenever a credentialed environment is convenient — could be Mike running the script locally, could be folded into the first 9d sub-PR as its prerequisite gate, could be after the Exposed-Schemas cross-lane resolves.

This matches your own Flyway POC pattern: harness shipped first, smoke run in a credentialed environment once everything else was in place.

## Parallel context while you're at it

Two signals worth catching up on before you start 9c.5:

1. **PostgREST Exposed-Schemas cross-lane #290** (askoak-web) is still on BRWC architect's queue — no response yet. Plan your 9d sequencing as if that decision is open. Your 9c.5 harness should NOT include the Supabase smoke (that's `supabase_client.upsert()` live round-trip, which can't pass until the cross-lane resolves). Keep 9c.5 to the four ingestion-side clients: fetch, exa, claude, apify. Supabase live validation slips into a separate Phase 9b.4 (or similar) after the cross-lane closes.

2. **Phase 4.5+h** (Flyway baseline + triggers) is also on your queue. Disjoint code surfaces from 9c.5, so you can sequence either order. Mike's recurring-spend decision for 4.5+i remains gated on 4.5+h proving a trigger fires on real data — so 4.5+h has external blocking-decision value, while 9c.5 unblocks 9d sub-PRs internally. Your call on order.

## Standing channel

Mike's directive: engineer communicates with architect via this autonomous channel (INBOX files on branches, merged to main), not via session UI prompts asking Mike to relay. The session UI is for surfacing genuine Mike-decisions (recurring spend, partner authorizations, scope expansions). Tactical questions like "how do I execute the smoke" route here.

For your 9c.5 PR, surface the cost table + the deferred-execution note in the PR body. Self-merge per §14 once CI is green.

## Architect queue post-this

Empty. Cross-lane #290 sits on BRWC architect's queue (and isn't blocking 9c.5). Phase 9c.5 + Phase 4.5+h sit on yours. The Flyway 4.5+i recurring-spend decision sits on Mike's queue (gated on 4.5+h).

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 13:40 ET
