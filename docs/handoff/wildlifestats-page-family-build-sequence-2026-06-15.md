# WildStats recommended page-family build sequence

**Date:** 2026-06-15
**Author:** Codex
**Status:** One-page recommended sequence based on current registry readiness, product value, and operating risk

## Recommended order

### 1. Wildlife laws and proposed-change tracker

Build this first.

Why:

- cleanest API-backed source set in the current registry
- lowest licensing and ToS risk of the six
- narrow federal MVP is obvious and useful
- maps directly to Phase 9 Bucket `07 REGULATORY`

Start with:

- `federal_register_api`
- `regulations_gov_api`

Add later:

- `congress_gov_api`
- `openstates_api`

### 2. Grants / funders page

Build this second.

Why:

- fully local curated source base already exists
- low engineering risk and low legal risk
- quick product win that does not depend on any new ingestion work
- not blocked on Phase 9

Start with:

- `wildstats_sector_funders_registry`

### 3. Wildlife rehab / wildlife hospital social monitor

Build this third.

Why:

- strong product differentiation
- current registry already has an operational roster
- reuses Flyway work already seeded in-repo
- manageable if kept metadata-first

Guardrails:

- metadata only
- link out to originals
- no raw-media archive

Phase 9:

- Bucket `01 SOCIAL` required

### 4. Center directory enrichment page family

Build this fourth.

Why:

- compounds the value of the current center directory
- uses multiple repo-owned registries already in hand
- becomes much stronger after the first operational social and regulatory joins are working

Do not overpromise:

- no permit-verification claims without explicit public roster support
- no financial enrichment dependency unless the registry later adds that source family cleanly

Phase 9:

- Buckets `02`, `04`, and `07`

### 5. Phenology / migration signals page

Build this fifth.

Why:

- high upside, but quality depends on the social monitor and Flyway signal logic being credible first
- mixes the most licensing and false-positive risk
- should ship as a narrow seasonal page, not a sprawling dashboard

Start with:

- hummingbird spring
- monarch spring

Phase 9:

- Bucket `01` first
- Bucket `06` later for baselines

### 6. Wildlife news of the week

Build this last.

Why:

- weakest current source base in the registry
- highest editorial and copyright noise
- easiest page to make feel busy but low-trust

If built before the registry grows, keep it manual-assisted.

Phase 9:

- Bucket `08 MEDIA / ACADEMIC`

## Simple decision rule

If the goal is **lowest-risk public utility**, start with:

1. laws tracker
2. grants/funders

If the goal is **most distinctive public signal surface**, start with:

1. rehab social monitor
2. migration signals later

My bias would be:

1. laws tracker
2. grants/funders
3. rehab social monitor

That order gives WildStats one clean policy page, one clean sector page, and
then one differentiated live-signal page without forcing the hardest licensing
or editorial problems onto the first public launch.
