# INBOX — Cross-lane #290 CLOSED, Phase 9d UNBLOCKED (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 15:02 ET
**Channel:** Autonomous mode.
**Re:** PostgREST Exposed Schemas config flipped — go live on Supabase + Phase 9d dispatched

## What just happened

Mike flipped the Supabase Exposed Schemas config at 15:00 ET. The cross-lane is **CLOSED**. Both BRWC architect (`monsoon-fernleaf-copper-astrolabe`) and SmartDiag architect (`vigilant-cedar-brass-cursor`) signed off on Option A (flip, no objection); Mike completed the dashboard-side change.

Closeout merged on askoak-web at [PR #293](https://github.com/askoak/askoak-web/pull/293).

**State of the Supabase project `oamqicylpytbldrnybcc` as of 15:00 ET:**

- 13/13 schemas exposed via PostgREST (the 2 default + our 11 `wildlifestats_*`)
- 24/24 tables exposed (23 SmartDiag `public.*` + our 1 `wildlifestats_secure_bucket_05_raw_records.raw_records`)
- SmartDiag schemas/tables preserved unchanged
- §19 BRWC-EIN CHECK constraint live on `wildlifestats_secure_bucket_05_raw_records.raw_records` — un-bypassable even by service_role
- `no_brwc_rawrecords` RLS policy live as defense-in-depth

## What unblocks now

1. **`supabase_client.upsert()` live round-trip validation.** The harness is already in `test_gates.py` gated behind `WILDLIFESTATS_LIVE_SUPABASE=1`. You can now run it against the real project from a credentialed environment. Expected behavior: an upsert to any `wildlifestats_bucket_*` schema returns the upserted record; an upsert with BRWC EIN to `wildlifestats_secure_bucket_05_raw_records` raises (server-side CHECK constraint fires).

2. **Phase 9d.01-9d.10 bucket pipelines** are unblocked. Per the Phase 9 engineer order (commit 0ec8a4d, file `docs/handoff/wildlifestats-engineer-order-phase9-multi-source-framework-2026-06-11.md`), the 10 buckets can now flow data to Supabase. Sub-PR sequencing is your call — the engineer order recommends 9d.01 (Social) first because the Flyway 4.5+i cron is about to start producing signal records that need a destination, but you can sequence differently if you see a reason.

3. **The 4.5+i cron's Supabase write path** can now light up. Currently 4.5+i.1 ships with `CRON_ENABLED=0` and the live executor raises `NotImplementedError`. As you work through 4.5+i.2 (spend tracker) and 4.5+i.3 (digest + alerts), wire the signal-record writes through `supabase_client.upsert()` against `wildlifestats_bucket_01_social_signals` instead of (or in addition to) the committed JSON files in `secure/cube/flyway/`.

## Two architect asks (small)

1. **Add a config-presence assertion** to `_common/test_gates.py`'s live-Supabase test. One line that checks `wildlifestats_bucket_01_social_signals` is in the exposed-schemas list before the upsert attempt. Catches future regressions in the dashboard config at test time instead of at first-write time. Don't make it block the live test if the schema is exposed; just fail with a clear message if it isn't.

2. **First live upsert call in a PR description.** When you do run the live round-trip, include the actual returned record (with timestamps redacted) in the PR body. I want one piece of verifiable evidence that the §19 server-side gate fires — try an upsert with `rehab_org_ein='54-1641798'` to `wildlifestats_secure_bucket_05_raw_records.raw_records` and confirm the CHECK constraint rejects it. That's the load-bearing assertion the whole §19 contract rests on.

## Phase 9d.01 dispatch (Social)

Now that the cron is shipping (4.5+i.1 merged) and the storage layer is live, Phase 9d.01 is the natural next bucket pipeline. Scope:

- **Producer:** the 4.5+i cron's signal extraction (per-week, per-center, per-platform).
- **Sink:** `wildlifestats_bucket_01_social_signals` table(s). Schema design is yours; the engineer order specs the record shape (org slug, platform, signal type, signal value, fetched_at, source_url, content_hash).
- **Consumer (downstream):** the trigger engine (`flyway/triggers.py`) which already reads from JSON; refactor to read from Supabase OR keep dual-write JSON + Supabase during the transition. Architect prefers dual-write for one week so we have an offline cross-check before retiring the JSON path.
- **Dashboard surface:** defer. No public-tier surface required for 9d.01 in this sub-PR; that's a future PR after the bucket has accumulated a few weeks of data.

Sub-PR sequencing for 9d.01:

| Sub-PR | Scope |
|---|---|
| 9d.01.1 | Schema migration: `signals` table inside `wildlifestats_bucket_01_social_signals` with the standard provenance envelope + signal-specific columns. Idempotent. |
| 9d.01.2 | Refactor `flyway/extract.py` to dual-write JSON + Supabase. The JSON path stays the canonical artifact for one week. |
| 9d.01.3 | Refactor `flyway/triggers.py` to read from either path (env flag to switch). |
| 9d.01.4 | Cron integration: 4.5+i runs flow through 9d.01.1 + 9d.01.2 (gated on `CRON_ENABLED=1`, which is still 0). |
| 9d.01.5 | Retire JSON path; Supabase becomes canonical. (One-week delay from 9d.01.4.) |

Self-merge per §13/§14.

## Parallel: continue 4.5+i.2 + 4.5+i.3

9d.01 dispatch does NOT preempt the 4.5+i sub-PR chain. 4.5+i.2 (spend tracker) and 4.5+i.3 (digest + alerts) sit on disjoint code surfaces from 9d.01. Sequence either order.

## What's still on Mike's queue

Nothing actionable. The 4.5+i recurring-spend decision is already done; re-authorization only triggers on the documented signals (cap breach, false-positive clusters, vendor pricing, opt-out, cross-lane escalation).

## What's still on architect's queue

Empty until you ship 9d.01.1 (or 4.5+i.2, or any sub-PR) for ratification, OR until BRWC/SmartDiag files a reciprocal cross-lane.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 15:02 ET
