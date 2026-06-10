# INBOX — OneDrive audit results (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-10 19:45 ET

## What I did

Mike corrected at 19:38 ET: the OneDrive directory he meant to point at is `99_Public Folder\WildStats\`, not `99_Public Folder\BRWC\`, and granted full authority to continue without him. I ran a live audit via the `files` connector against the OneDrive tree.

## What I found

1. **`99_Public Folder\WildStats\` does not exist yet.** Mike intends to create it; this is his OneDrive action, not ours.
2. **`99_Public Folder\BRWC\Social Posts\` exists** and contains ~75 MB of BRWC-lane content (BRWC's own IG, YT, FB scrape outputs, plus the educational-replies CSV) PLUS the one WildStats-lane file: `wildlife_rehab_social_seed_top100.csv` (the 100-org roster, already on `main` BRWC-scrubbed to 99 rows).
3. The earlier `brwc-educational-replies_*.csv` is BRWC content (sampled: 413 IG comments authored by `@blueridgewildlifectr` on its own posts).

## Implications for your Flyway work

**None that change scope.** Specifically:

- The Flyway roster in `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv` is correct (99 rows, BRWC scrubbed).
- The Phase 4.5+f → 4.5+j engineer order stands unchanged.
- The Phase 4.5+g Apify smoke test does NOT use any of the BRWC pre-scraped JSONs as input. When you run 4.5+g, it scrapes fresh against the 99-org WildStats roster.
- The Phase 4.5+g output lands in `secure/cube/flyway/`, NOT in any OneDrive directory. The future `99_Public Folder\WildStats\Social Posts\` directory Mike will create is for HIS reference and parallel manual exploration — not the canonical Flyway storage path. Canonical storage is in the repo (committed) or under `secure/cube/flyway/` (research-tier).

## What I did NOT do

- Did not download any BRWC scrape JSONs into the WildStats lane.
- Did not parse the BRWC educational-replies CSV beyond a 5-row sample needed for lane determination.
- Did not modify the Flyway roster.
- Did not create the `WildStats\Social Posts\` OneDrive folder (Mike's action).

## What changed in the handoff folder

- `CROSS-LANE-brwc-social-corpus-pointer-2026-06-10.md` is now marked SUPERSEDED. It was correct on classification but didn't cover the full BRWC directory.
- `CROSS-LANE-brwc-social-corpus-pointer-2026-06-10-AMENDED.md` is the new authoritative cross-lane pointer. The BRWC architect picks up the full directory, not just the educational-replies CSV.
- This INBOX is the engineer-facing audit summary.

## You can proceed

Phase 4.5+f is the next pickup per your slow-pace cadence. Nothing in the audit blocks it.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:45 ET
