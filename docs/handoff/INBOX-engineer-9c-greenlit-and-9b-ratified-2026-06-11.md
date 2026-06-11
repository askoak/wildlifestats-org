# INBOX — Phase 9b ratified + Phase 9c green-lit (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 12:35 ET
**Re:** Closing Phase 9b, advancing to Phase 9c

## Phase 9b ratified

PR #39 (03e3275) is **ratified**. Strong work on a load-bearing piece:

- **The CHECK-vs-RLS design call was correct, and important enough that I want to call it out.** RLS-only would have been broken on first use because the production write path uses service_role, which bypasses RLS. The CHECK constraint is what actually enforces the §19 BRWC-EIN exclusion. RLS is correctly retained as defense-in-depth for any future authenticated-role write path. The commit message documents this clearly; that documentation is the kind of thing future architects (and future you) will thank current you for.
- **Idempotency confirmed on real apply.** Re-running the migration converges to the same state — the difference between "scaffold complete" and "production-grade" is exactly this kind of verification.
- **88 kB / 880 MB footprint is excellent.** No new plan cost, no resource pressure on SmartDiag, no surprise spend.
- **Test gates updated correctly.** 13/13 passing, with the live round-trip test gated behind `WILDLIFESTATS_LIVE_SUPABASE=1` so CI doesn't accidentally spend.
- **The Exposed-Schemas escalation was the right call.** Project-level API config on a shared project is exactly the kind of thing that needs owner-gating, not engineer initiative.

## PostgREST Exposed Schemas — cross-lane filed

Per your follow-up flag, I've filed a CROSS-LANE note to the BRWC/SmartDiag architect requesting authorization to add `wildlifestats_*` schemas to the PostgREST Exposed Schemas config on `oamqicylpytbldrnybcc`. Filed at askoak-web `docs/handoff/CROSS-LANE-postgrest-exposed-schemas-2026-06-11.md` (PR #290, merged).

The note offers three options (flip, counterpropose, defer) with WildlifeStats's preference being flip. Until that comes back, WildlifeStats lane treats it as an open dependency on the 9d.* PRs but NOT on 9c.

## Phase 9c green-lit — proceed with `_common` implementations

Phase 9c is the implementation layer behind the scaffold gates already in `wildlifestats/_pipeline/_common/`. Five sub-PRs per the engineer order §3, all independent of the Exposed-Schemas decision:

| Sub-PR | Scope | Notes |
|---|---|---|
| 9c.1 | `fetch.py` — robots-aware HTTP with rate-limit + cache + dating envelope | Pure local infra; no API auth needed for the scaffold's contract |
| 9c.2 | `exa_client.py` — canonical-URL discovery against api.exa.ai | Uses `custom-cred:api.exa.ai`; first-use needs `approve_credential` |
| 9c.3 | `claude_client.py` — structured extraction against api.anthropic.com | Uses `custom-cred:api.anthropic.com`; the production replacement for the Flyway POC's env-shadow workaround |
| 9c.4 | `apify_client.py` — refactor the validated Flyway POC into `_common/`, extend FB+IG to all 5 platforms | The Flyway POC client is the proven artifact; preserve its discipline |
| 9c.5 | Integration smoke — one live call per client against a single test target | Cost + correctness validated; gated behind env flags so CI doesn't spend |

### Sequencing within 9c

Recommended order: 9c.1 (fetch — pure local, foundational) → 9c.2 (exa, low spend) → 9c.4 (apify, you already know it) → 9c.3 (claude, highest per-call cost — validate the prompt + schema before bulk runs) → 9c.5 (smoke).

But this is preference, not direction. If you'd rather front-load 9c.3 because you want the production Anthropic path working before any extraction-heavy work lands, that's fine.

### Discipline checks (codify in each sub-PR)

For every `_common` module you implement:

1. **Token by reference only.** `creds.get_*_token()` returns a string; that string lives in a local variable for the duration of a single HTTP request and goes out of scope at function end. No module-level constants, no logging, no return-to-caller of token values.
2. **`scripts/check-no-credentials.sh` passes locally before push.** It's wired into CI; running it pre-push catches surprises.
3. **Each module's `test_gates.py` section grows.** Currently 13 tests; each implementation adds the live-path tests gated behind its own `WILDLIFESTATS_LIVE_*` flag.
4. **PR description surfaces cost.** Per-call estimate + per-bucket steady-state. Mike's authorizations are per-bucket; do not assume a global cap.
5. **Robots respect for `fetch.py`.** Already in the scaffold's contract; the implementation honors it absolutely. One violation surfacing publicly is a permanent reputational tax.

## Cost ceiling for 9c smoke testing

The 9c.5 integration-smoke pass should stay under **$5 total** across all four live clients. That covers:
- Exa: a handful of queries against known orgs (~$0.50)
- Claude: a handful of structured extractions against known content (~$1)
- Apify: one or two actor runs against the Flyway-tested centers (~$1)
- Voyage (if you decide to wire embeddings in 9c — optional): a handful of embed calls (~$0.50)

If your estimate exceeds $5, surface in the PR description before issuing the calls. Mike's standing authorization covers $5-10 single-pass smoke spend; recurring spend is per-bucket and gated separately.

## What 9c is NOT

Not the Phase 9d bucket implementations. Each of those is a separate sub-PR after 9c lands. The intent of 9c is: make the scaffold work; prove the discipline; do NOT yet wire to live data flows.

## Architect queue

After this INBOX:
- Cross-lane #290 (PostgREST Exposed Schemas) is on BRWC architect's queue, not WildlifeStats lane's. Will surface when they reply.
- Phase 9c is on your queue.
- Architect's queue is otherwise empty.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 12:35 ET
