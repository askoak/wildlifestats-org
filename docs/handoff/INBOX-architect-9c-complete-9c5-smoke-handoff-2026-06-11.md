# INBOX — Phase 9c complete; 9c.5 live-smoke execution handoff (engineer → architect)

**From:** Engineer, `soar-aspen-beryl-heron`
**To:** Architect, `measured-fern-jasper-thrush`
**Date:** 2026-06-11
**Re:** 9c.1–9c.4 shipped; 9c.5 smoke runner shipped; live execution needs credentials

## Phase 9c implementations — shipped + self-merged (CI green)

| Sub-PR | Module | PR | Notes |
|---|---|---|---|
| 9c.1 | `fetch.py` | #42 | robots (24h cache; 5xx→disallow / 404→allow / neterr→refuse), per-host rate-limit honoring Crawl-Delay, disk cache TTL, dating envelope |
| 9c.2 | `exa_client.py` | #43 | host-match **always** outranks higher-confidence off-host; `validate_candidate` via `fetch` |
| 9c.3 | `claude_client.py` | #44 | forced tool_use; quote discipline (verbatim-or-reject); cost tracking; lazy `jsonschema` (no hard dep) |
| 9c.4 | `apify_client.py` | #45 | 5 platforms; FB/IG POC-proven POST scrapers; **no raw text on disk**; `creds.get_apify_token()` retires the `APIFY_TOKEN` env-shadow |

Gate suite grew 13 → **29**, all passing. Every client carries a `WILDLIFESTATS_LIVE_*` flag-gated live test so CI never spends. `check-no-credentials.sh` passes on each.

## 9c.5 — integration smoke runner shipped (this PR)

`wildlifestats/_pipeline/_common/smoke_9c5.py` — the single orchestrated entry point for your 9c.5 order ("one live call per client, single test target, cost validated, gated so CI doesn't spend"):

- Safe by default; live calls only with `--run` and only for clients whose credential is present (`creds.is_present`).
- Hard **$5 ceiling**, enforced cumulatively as it runs (aborts before exceeding).
- Per-client: `fetch` (no spend) · `exa` (~$0.01) · `claude` Haiku (~$0.001–0.01) · `apify` 1 FB run / 5 posts (~$0.30) · `supabase` SKIP (DB contract already verified via the Supabase MCP; live REST stays gated on Exposed-Schemas).
- Run: `python -m wildlifestats._pipeline._common.smoke_9c5 --run`

## Blocker — and the decision I need from you (not Mike)

**This engineer session has no vault `CUSTOM_CRED_*` tokens** (only the legacy `APIFY_TOKEN`). Exa, Anthropic, and Supabase all resolve `present=False`, so I cannot execute the live smoke from here — and I will not fake live results or spend on a 1-of-4 partial.

Mike's directive this session: **autonomous mode, follow architect's orders, do not prompt Mike.** So I'm routing the execution decision to you. Options:

- **(A) Defer live execution, ratify the harness as the 9c.5 deliverable.** The runner + the four `WILDLIFESTATS_LIVE_*` flag-gated unit tests are the reproducible smoke; live cost-validation runs in the next credentialed pass. I treat 9c as code-complete and move on.
- **(B) You (or a credentialed session) run `smoke_9c5.py --run`** and paste results; I fold the actual spend + correctness into the 9c.5 record.

**My recommendation: (A)** — and combine the live cost-validation of 9c.5 with the first 9d live pass, because **9d bucket live writes are themselves gated on the PostgREST Exposed-Schemas cross-lane (#290)**. One credentialed run validates both at once instead of two separate spend events.

## Next on engineer queue?

With 9c code-complete and 9d live-writes gated on #290, the unblocked candidates I see are: Flyway 4.5+h (baselines/triggers — on my queue per your INBOX) and Phase 8 / 4.6 hardening. Tell me the priority and I'll proceed autonomously; absent a reply I'll pick up 4.5+h next (it's the oldest item explicitly on my queue and needs no new credentials).

— Engineer, `soar-aspen-beryl-heron`, 2026-06-11
