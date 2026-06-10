# INBOX — BRWC corpus pointer noted; no WildlifeStats action (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-10 19:34 ET

## What Mike sent

Mike attached two files at 19:34 ET and pointed at a BRWC OneDrive directory. Summary for engineer awareness:

| File | Lane | Action |
|---|---|---|
| `wildlife_rehab_social_seed_top100.csv` (100 rows) | WildlifeStats | **None.** Current roster on main (99 rows, BRWC scrubbed) already matches this minus the BRWC row. Schema is identical. No engineer work. |
| `brwc-educational-replies_2026-06-08-2.csv` (3923 rows) | BRWC | Cross-lane handoff posted at `docs/handoff/CROSS-LANE-brwc-social-corpus-pointer-2026-06-10.md`. BRWC architect picks it up; do not ingest on this lane. |
| `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\BRWC\Social Posts\` (directory) | BRWC | Same — pointer in the CROSS-LANE file. BRWC architect's job to verify contents and spec ingestion. |

## What this changes in WildlifeStats

Nothing. The Flyway roster is correct. The Flyway spec stands. The Phase 4.5+f–j engineer order stands. §19 BRWC scrub is intact.

If you encounter BRWC-attributable content anywhere in scrape outputs (e.g. an Apify run on a hashtag that surfaces a BRWC post), filter it at extract time the same way the roster is scrubbed — drop the record, log to audit. The Flyway extractor (`extract.py` in 4.5+g) should already do this if the source-org match check is wired correctly; add it explicitly if not.

## Why I'm posting this

So that you don't waste cycles wondering whether Mike's attachment changes the Flyway roster or the Phase 4.5+f scope. It does not. Proceed as queued.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:34 ET
