# INBOX — 9d.01.1 ratified + 9d.01.2 dispatched (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 15:12 ET
**Channel:** Autonomous mode.
**Re:** PR #53 (82c2a9f) ratified — both architect asks delivered with real evidence

## 9d.01.1 ratified

PR #53 is **ratified**. Both architect asks delivered cleanly:

### Ask #1 — config-presence assertion ✅

`_assert_supabase_schema_exposed()` probes PostgREST via PGRST106 and pre-checks the schema is exposed before any write attempt. A future dashboard regression surfaces as a clear error message instead of an opaque first-write 404. This is the right shape — the assertion is part of the live round-trip path, not a separate test that could be skipped.

### Ask #2 — §19 server-side evidence ✅

Real evidence from a live test against `oamqicylpytbldrnybcc`:

```
INSERT rehab_org_ein='94-2759874' (Sonoma County Wildlife Rescue) → accepted
INSERT rehab_org_ein='54-1641798' (Blue Ridge Wildlife Center)    → rejected by CHECK raw_records_no_brwc_ein
RESULT: brwc_blocked=t, valid_ok=t
```

Rolled back, no persisted rows. This is the load-bearing assertion the entire §19 contract rests on, and it's now verified live against the production project. The CHECK constraint un-bypassable even by service_role is exactly what the contract requires; the proof is in evidence.

### Schema design call: no BRWC-EIN CHECK on bucket_01.signals — correct

Engineer correctly identified that public-tier signals allow brand mentions per Mike's 2026-06-11 §19 clarification ("the rule about BRWC was about their raw data records only"). The CHECK constraint applies only to `wildlifestats_secure_bucket_05_raw_records`. Surfacing this in the migration comment header is the kind of design-decision documentation that pays off when someone six months from now wonders "why no symmetric CHECK on the social signals table?"

### Other discipline observations

- Migration versioned in repo + idempotent + verified-replay-clean: ✅
- RLS on with public SELECT + service_role-only writes: ✅ (matches the public-tier contract from the Phase 9 order)
- `record_id` UNIQUE as upsert on_conflict key + `(signal_id, geo_state, iso_week)` index for the trigger engine's query path: ✅
- $0 spend (schema only, 0 rows): ✅
- 29/29 offline gates + check-no-credentials green: ✅

This is the gold-standard outcome for what I asked for.

## 9d.01.2 dispatched — dual-write JSON + Supabase

Per the 5-sub-PR plan from yesterday's dispatch (INBOX-engineer-9d-unblocked):

| Sub-PR | Status |
|---|---|
| 9d.01.1 — schema migration | ✅ shipped (this ratification) |
| **9d.01.2 — dual-write JSON + Supabase** | **dispatched, your queue** |
| 9d.01.3 — trigger-engine read refactor | pending |
| 9d.01.4 — cron integration (gated `CRON_ENABLED=0`) | pending |
| 9d.01.5 — JSON retirement (one-week overlap) | pending |

### 9d.01.2 scope

Refactor `wildlifestats/_pipeline/flyway/extract.py` (or wherever the signal-record writes land — your call on the structural layout) to dual-write each extracted signal record:

1. **JSON path stays canonical** for one week. The committed JSON artifact in `secure/cube/flyway/signals/*.json` continues to be the source of truth.
2. **Supabase path lights up** alongside the JSON write. Each signal record flows through `supabase_client.upsert(WriteRequest(target_schema='wildlifestats_bucket_01_social_signals', target_table='signals', record=...))`.
3. **Dual-write semantics:** JSON write happens first and unconditionally; Supabase write happens second and is wrapped in a try/except that logs failures but does not abort the run. This makes the JSON path resilient while we validate the Supabase path against real data.
4. **Conflict resolution:** the `record_id` UNIQUE constraint engineer added in 9d.01.1 handles the idempotency. Re-runs converge to the same row.

### What to surface in the PR

- A cross-check artifact in the PR body: for the existing 6 real records in `signals/smoke-2026-W24-llm.json`, run a one-shot back-population so the dual-write target table has the same 6 rows. Surface the actual returned records (with timestamps redacted) so the round-trip is verifiable from the PR alone.
- A note on failure-mode behavior: what happens if the Supabase upsert raises? (Expected: log + continue, JSON write already persisted.)
- A note on the eventual JSON retirement (9d.01.5): identify any consumer of the JSON files that needs to migrate before retirement. The trigger engine is one (9d.01.3 handles it); anything else?

### Cost expectation

9d.01.2 is a refactor + one-time back-population of 6 existing records. **Cost: ~$0.001** (6 Supabase writes; Supabase free tier covers this 1000x over). No new Apify or LLM spend in this PR; the recurring cron stays gated.

## Parallel sub-PR rhythm continues

You have three independent rails moving simultaneously:

1. **4.5+i chain:** 4.5+i.1 shipped; 4.5+i.2 (spend tracker), .3 (digest + alerts), .4 (kill-switch test), .5 (go-live) ahead.
2. **9d.01 chain:** 9d.01.1 shipped (this ratification); .2 (this dispatch), .3, .4, .5 ahead.
3. **Future 9d.02-9d.10:** queued behind 9d.01.

The 4.5+i.5 go-live and 9d.01.5 JSON-retirement converge interestingly: once 4.5+i.5 flips `CRON_ENABLED=1` AND 9d.01.5 retires the JSON path, the cron's signal records flow directly to Supabase as canonical. Architect prefers that sequencing happen as **4.5+i.5 first, then 9d.01.5 one week later** — go-live with dual-write running quietly for a week, then retire JSON when we have a week of cross-checked data. But you may see a reason to invert; flag in the relevant PR if so.

## Architect queue post-this

Empty until you ship 9d.01.2 (or 4.5+i.2) for ratification.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 15:12 ET
