# INBOX — Phase 4.5+i recurring cron AUTHORIZED (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 14:10 ET
**Channel:** Autonomous mode.
**Re:** Mike's recurring-spend decision on Flyway 4.5+i

## Decision: APPROVED

Mike authorized the recurring Flyway daily cron at 14:08 ET, 2026-06-11. The decision is grounded in the 4.5+h finding ("the engine is built and proven; the only thing standing between it and live early-warning triggers is multi-week collection") and in the POC's geo-attributed, season-correct, quantitative-volume-bearing record set.

**Spend ceiling:** ~$50-100/month steady-state per the post-mortem estimate. Hard cap below.

## Standing constraints (non-negotiable)

These bound the authorization. Violations require re-authorization from Mike.

1. **Month-1 hard cap: $30.** Cron auto-suspends on hitting $30 cumulative Apify+LLM spend within calendar month 1 (June 2026 partial → July 2026 full). This is the validation window — actual spend must match estimate before the cron runs free. From month 2 onward, the steady-state cap is $100/month with auto-suspend on hit.

2. **Two-tier orchestration per Decision A** (already specced in `_common/apify_client.py`):
   - Tier 1 (~50 priority centers): monthly full refresh
   - Tier 2 (~131 long-tail centers): quarterly trailing-90d refresh
   - Daily cron handles Tier 1 + the trailing-7d delta on Tier 2.

3. **§19 raw-text discipline holds.** The cron path uses the same `apify_client` audit-log contract as the POC: `post_text_NOT_STORED: true` on every record. No raw text on disk outside Apify's cloud dataset. The §19 BRWC EIN CHECK constraint on Supabase enforces server-side; the engineer-side audit log is the file-level defense.

4. **Trigger-engine integration is the deliverable, not just the scrape.** Per cube run: cron pulls → `extract.py` produces signal records → `triggers.py` evaluates → if any trigger fires, an INBOX is auto-generated for Mike with provenance (record_ids, centers, weeks, baseline, threshold). The Wild Bird Fund "+12% YoY at patient #5,000" record is exactly the kind of signal that should produce an alert once 4 weeks of baseline accumulates.

5. **Notification discipline: weekly summary + per-trigger alerts.** A weekly digest INBOX summarizing scrape count + cost + zero-trigger weeks goes to Mike (autonomous channel). Per-trigger alerts when an actual trigger fires. No flood. Quiet weeks generate a one-line "no triggers this week, $X.YZ spent" line in the weekly digest; not a separate notification.

6. **Kill-switch.** A `wildlifestats/_pipeline/flyway/CRON_ENABLED` file gates the cron. Setting its contents to `0` (or deleting the file) suspends the next run; a single PR can flip it. Mike or architect can suspend in 30 seconds without engineer involvement.

## Sub-PR plan

| Sub-PR | Scope | Estimated cost |
|---|---|---|
| 4.5+i.1 | Cron script + scheduled execution wiring (GitHub Actions cron, daily 04:00 UTC) | $0 (build only) |
| 4.5+i.2 | Cumulative-spend tracker + auto-suspend at $30 (month 1) / $100 (month 2+) | $0 (build only) |
| 4.5+i.3 | Trigger-fired auto-INBOX generator + weekly digest INBOX | $0 (build only) |
| 4.5+i.4 | Kill-switch (`CRON_ENABLED` gate) + suspend test | $0 (build only) |
| 4.5+i.5 | First live cron run authorized | actual spend logged in PR |

Self-merge per §13/§14 as each lands. 4.5+i.5 is the "go-live" PR — it flips `CRON_ENABLED` from `0` to `1` and the next scheduled tick runs against real centers.

## Implementation notes

**Where the cron runs:** GitHub Actions on this repo (askoak/wildlifestats-org) is the recommended host — it's where the test_gates already run, the credential injection via `api_credentials=[...]` works inside Actions, and the audit-log artifacts can be uploaded as workflow outputs. Alternative: Cloudflare Workers Cron (we have the Cloudflare token in vault), but it adds a hosting surface for marginal benefit. Architect prefers GitHub Actions; engineer's call if you see a better fit.

**Credential injection in Actions:** the existing `validate.yml` jobs don't need credentials, but the cron job will. Use the same `api_credentials` pattern documented in `_common/creds.py`. The four handles needed: `custom-cred:api.apify.com`, `custom-cred:api.anthropic.com`, and (when cross-lane #290 resolves) `custom-cred:oamqicylpytbldrnybcc.supabase.co`. Until #290 resolves, the cron writes signal records to the existing `secure/cube/flyway/signals/` directory tree and a per-week `triggers/triggers-<iso-week>.json` artifact, both committed to the repo. Once #290 resolves, supabase writes land alongside file writes.

**Time zone:** schedule at **04:00 UTC** (midnight ET) so the cron runs after most US-East orgs have finished posting for the day. Avoids race conditions with same-day posts being missed.

**Tier 1 selection:** the 50 priority centers come from `centers.yaml` ranked by `typical_annual_intake` where populated, falling back to ProPublica revenue for orgs missing intake. Document the selection methodology in the 4.5+i.1 PR description and surface the resulting list as a committed artifact (`wildlifestats/_pipeline/flyway/tier1-roster.txt`) so we can audit it and so Tier 2 is unambiguously "the other 131."

**Weekly digest format** (auto-generated):

```
# Flyway Weekly Digest — 2026-W<N>

- Scrape: <X> posts across <Y> centers, <Z> platforms
- Signals extracted: <count> records
- Triggers fired: <count> (see triggers-2026-W<N>.json)
- Spend this week: $<X.YZ>
- Spend month-to-date: $<X.YZ> / $<cap>
```

Triggers-fired alerts are separate INBOXes with full provenance.

## Architect commitments

- Will ratify each sub-PR within one wake cycle of green CI.
- Will not silently raise the $30/$100 caps. Cap changes route to Mike.
- Will flip the kill-switch if any trigger fires that on inspection looks like extraction noise, until the noise is characterized.

## Mike-decision triggers (re-authorization required)

These are signals that pull the decision back onto Mike's queue:

- Month-1 actual spend exceeds $30 OR steady-state exceeds $100/month
- Two or more weeks of trigger firings that on inspection are false positives
- Apify or Anthropic pricing change >25% upward
- An org explicitly opts out of being scraped (more likely to happen as we scale)
- Cross-lane escalation from BRWC or another lane

## Architect queue post-this

Empty until engineer ships 4.5+i.1 for ratification, or cross-lane #290 resolves, or Mike directs otherwise.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 14:10 ET
