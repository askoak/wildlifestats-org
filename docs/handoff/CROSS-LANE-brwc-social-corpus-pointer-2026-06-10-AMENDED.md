# CROSS-LANE — BRWC social corpus pointer (AMENDED, WildlifeStats architect → BRWC architect)

**From:** WildlifeStats Architect, `measured-fern-jasper-thrush`
**To:** BRWC Architect, `coastal-thistle-bronze-cairn`
**Date:** 2026-06-10 19:45 ET
**Amends:** `CROSS-LANE-brwc-social-corpus-pointer-2026-06-10.md` (committed in PR #20). That pointer was correct in classification but incomplete in scope. This file replaces it with the post-audit picture.
**Trigger:** Mike's 19:38 ET correction ("the WildStats folder, sorry"), which led to a live OneDrive audit via the `files` connector. The audit results forced a re-think.

## Audit findings (run 2026-06-10 19:40 ET via `search_files_v2`)

The directory at `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\BRWC\Social Posts\` is correctly named — its contents ARE BRWC-lane content, despite Mike's brief naming confusion:

| File | Audit finding | Lane |
|---|---|---|
| `wildlife_rehab_social_seed_top100.csv` (67 KB) | National roster of 100 wildlife-rehab orgs. **This is the one WildStats-lane file in the directory** — and it is already correctly committed (BRWC-scrubbed to 99 rows) at `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv`. | WildStats |
| `dataset_instagram-scraper_2026-06-08_17-55-19-191.json` (58 KB) | Sampled: 5 IG posts all from `@blueridgewildlifectr`. BRWC's own posts. | BRWC |
| `dataset_youtube-scraper_2026-06-08_17-59-50-734.json` (46 KB) | Naming pattern + co-location with the IG file strongly suggests BRWC's own YT channel. Architect did not sample. | BRWC |
| `dataset_instagram-scraper_2026-06-08_18-16-39-583.json` (31 MB, Google Drive) | Same naming family, much larger. Likely a full-history dump of BRWC's IG. | BRWC |
| `dataset_facebook-posts-scraper_2026-06-08_19-01-19-876.json` (12 MB, Google Drive) | Same naming family. Likely BRWC's FB Page. | BRWC |
| `dataset_instagram-post-scraper_2026-06-08_17-44-47-232.json` (31 MB, Google Drive) | Same naming family. Likely BRWC IG. | BRWC |
| `dataset_youtube-scraper_2026-06-08_18-34-54-404.json` (485 KB, Google Drive) | Same naming family. Likely BRWC YT. | BRWC |
| `brwc-educational-replies_2026-06-08-2.csv` (660 KB, attached to chat) | Sampled: 413 IG comments authored by `blueridgewildlifectr` on its own posts. BRWC's social-team voice corpus. | BRWC |

**Total BRWC corpus in the folder: ~75 MB across 6+ datasets, all dated 2026-06-08.**

## Mike's forward intent (19:38 ET)

Mike wants to create a parallel `99_Public Folder\WildStats\Social Posts\` directory (it does not exist as of the audit). Future Phase 4.5+g Apify scrape outputs targeting the 100-org WildStats roster will land there, keeping BRWC's own social corpus separate from WildStats's national scrape outputs.

This is **Mike's OneDrive action** — neither architect creates folders in Mike's OneDrive.

## Implications for BRWC lane

1. The whole `99_Public Folder\BRWC\Social Posts\` directory (minus the one CSV that is the WildStats roster) is **BRWC corpus**. The BRWC architect should:
   - Ingest into the BRWC lane's own pipelines.
   - The Apify scrape outputs are gold for BRWC's own social-tone analysis, FAQ extraction from comments, and engagement metrics.
   - The educational-replies CSV is the canonical "BRWC staff voice on social" dataset and should anchor any BRWC AI assistant that generates social-tone responses.

2. The WildlifeStats Flyway pipeline (Phase 4.5+f-j) does NOT consume any of this BRWC content. Flyway will produce its OWN scrape outputs against the 99-org BRWC-scrubbed roster, and those outputs land in WildStats territory.

3. The earlier CROSS-LANE handoff (PR #20) only flagged the educational-replies CSV. This amendment widens it to the full directory.

## Implications for WildlifeStats lane

1. **No code or content changes on `main`.** The Flyway roster is correct. The Flyway spec is correct. The Phase 4.5+f-j engineer order is correct.

2. **Phase 4.5+g sample data does NOT come from this BRWC directory.** When the engineer runs the Apify smoke test, it produces fresh outputs against the 99-org WildStats roster. Those outputs land in the WildStats lane's own storage (per Flyway spec §8: `secure/cube/flyway/`).

3. **Mike's future `WildStats\Social Posts\` directory** is informational only — when Mike creates it and starts depositing files there, those files become WildStats lane data. Until then, the directory does not exist and is not a dependency.

## What I did NOT do (deliberate non-actions)

- Did not download or commit any of the BRWC scrape JSON datasets.
- Did not parse or store the BRWC educational-replies CSV beyond a 5-row sample required to determine the lane.
- Did not create the WildStats parallel folder in OneDrive.
- Did not modify `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv`.
- The IG sample download was scrubbed from this seat's sandbox immediately after lane determination per §19.

## Status

- PR #20's CROSS-LANE pointer file is superseded by this amendment.
- BRWC architect: please pick up the full directory pointer, not just the CSV.
- WildlifeStats engineer: no action; the audit findings are FYI.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:45 ET
