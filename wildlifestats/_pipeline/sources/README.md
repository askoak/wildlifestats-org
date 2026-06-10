# Flyway source registry

Seed sources for **Flyway** — the WildlifeStats social / phenology early-warning
system (working name, Mike-approved 2026-06-10). See
`docs/handoff/INBOX-engineer-social-early-warning-2026-06-10.md` for the concept,
architecture, and the architect spec request.

## flyway-social-seed-top100.csv

Roster of US wildlife-rehabilitation organizations and their public social
handles (Facebook / Instagram / TikTok / YouTube), ranked + tiered (A/B/C), with
an `Apify Search Query` column ready for the scrape stage.

- **Provenance:** Mike-provided seed (`wildlife_rehab_social_seed_top100.csv`),
  2026-06-10.
- **99 of 100 rows.** One row — a Virginia center that is the BRWC lane's own
  organization — was removed to preserve lane separation (Standing Orders §19:
  no BRWC identifiers in the WildlifeStats lane). Flyway monitors the national
  field; BRWC's own data flows through its separate auth-gated tier, never the
  public Flyway registry.
- **Status:** seed only. The architect specs the scrape cadence, the
  per-source registry shape (`<source-id>.json`), the signal-extraction schema,
  and the baseline/anomaly method before any recurring job runs.

These are public Pages. Flyway extracts *signals* and links to source; it does
not republish post content (copyright / platform ToS).
