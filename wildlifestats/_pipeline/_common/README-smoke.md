# Phase 9c.5 — integration smoke (how to run)

One live call per `_common` ingestion client, single test target each, behind a
hard **$5 total** cap. This validates the four clients end-to-end before they're
composed into the Phase 9d bucket pipelines (live-validate components before
composing — bugs are far harder to localize once buckets are stacked on top).

Scope is the **four ingestion-side clients only** — `fetch`, `exa`, `claude`,
`apify`. The Supabase live round-trip is **out of scope here**: its DB-side §19
contract is already verified via the Supabase MCP, and the live REST `upsert()`
can't pass until the PostgREST Exposed-Schemas cross-lane (#290) resolves. It
runs separately (Phase 9b.4) once that closes.

## Prerequisites — credentials

The runner reads each token from its vault handle via `creds.py` (never a
module-level constant, never pasted into a chat session). Run it in an
environment where these handles are injected for the duration of the process:

| Client | Env var (`creds.py`) | Vault handle |
|---|---|---|
| exa | `CUSTOM_CRED_API_EXA_AI_TOKEN` | `custom-cred:api.exa.ai` |
| claude | `CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN` | `custom-cred:api.anthropic.com` |
| apify | `CUSTOM_CRED_API_APIFY_COM_TOKEN` | `custom-cred:api.apify.com` |
| fetch | — (no credential) | — |

A client whose handle is absent is reported `SKIP` (not `FAIL`) — the runner
validates whatever it can reach.

## Run

```bash
# dry-run plan only (no spend, no network)
python -m wildlifestats._pipeline._common.smoke_9c5

# live — issue the billable calls (only in a credentialed environment)
python -m wildlifestats._pipeline._common.smoke_9c5 --run
```

In an environment that injects credentials per-invocation (the standing pattern),
supply the three handles to the bash call's `api_credentials`
(`custom-cred:api.exa.ai`, `custom-cred:api.anthropic.com`,
`custom-cred:api.apify.com`) and run the `--run` form above.

## Per-client calls + expected output

| Client | Call | Expected | Est. cost |
|---|---|---|---|
| `fetch` | GET `https://example.com/` | `200` + non-empty body; robots cached | $0 |
| `exa` | `find_canonical_url("National Audubon Society", "annual_report_landing", domain_hint="audubon.org")` | ≥0 ranked candidates, each a valid URL + score ∈ [0,1] | ~$0.50 |
| `claude` | one Haiku structured extraction (topic) | record with `topic`; `estimated_usd` ≥ 0 | ~$1.00 |
| `apify` | 1 FB posts run, `lindsaywildlife`, 5 posts, 120-day window | `succeeded`; audit log carries **no** post text | ~$1.00 |
| `supabase` | — | `SKIP` (MCP-verified; REST gated on #290) | $0 |
| **Total** | | | **≤ $5 (hard cap)** |

The runner enforces the cap **cumulatively** — it aborts before issuing the next
call if running spend would exceed $5. (Voyage embeddings are an optional ~$0.50
add if embedding wiring lands in 9c; not included by default.)

## After running

Paste the runner's result table into a follow-up INBOX or PR comment so the
actual spend + correctness are recorded against the 9c.5 deliverable. Until then,
9c.5 is "harness shipped, live execution deferred" per the architect's
2026-06-11 direction.
