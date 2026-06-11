# INBOX — Flyway smoke test authorized (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 07:51 ET

## Authorization

Mike confirmed at 2026-06-11 07:50 ET: "1. authorized" — referring to the
~$5-10 one-time Apify smoke test that gates Phase 4.5+g.

You can fire the smoke test when your cadence picks up Phase 4.5+g. Cost
expectation: $5-10 total for the one-off run, well under any meaningful
threshold.

## Scope reminder (from Phase 4.5+g engineer order)

- 3-5 Facebook/Instagram Pages from `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv` (your choice — pick a geographic + size variety)
- Single signal: `phenology.first_of_season.hummingbird_spring`
- Both FB and IG actors run once
- Document in PR description: posts scraped, records extracted, total Apify cost, total LLM cost
- Verify `secure/cube/flyway/audit/` audit log shows `post_text_NOT_STORED: true` on every record
- No raw post text written to disk anywhere

## What this does NOT authorize

- The **recurring** daily 99-Page cron at ~$50-100/month — that's Phase 4.5+i gate and stays disabled until Mike specifically authorizes the recurring spend. Per Phase 4.5+g engineer order: "Daily schedule is COMMENTED OUT until Mike authorizes recurring spend."

## Followup gate

After 4.5+g ships and you've documented cost in the PR, surface a brief INBOX
to Mike-and-architect with: (a) actual cost, (b) extraction quality
observations (false positives, hallucinated geo, missed signals), (c) any
methodological surprises. That's the input for Mike's recurring-spend
authorization at Phase 4.5+i.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 07:51 ET
