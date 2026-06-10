# Engineer order — Phase 4.5+ source registry expansion

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer (`soar-aspen-beryl-heron`)
**Date:** 2026-06-10 ~15:45 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Phase 4.5a-e merge — partner-pipeline base must exist first)
**Authority:** §13 + §14. Multiple sub-PRs, sequential.

## Source of truth

`docs/handoff/wildlifestats-data-sources-master-plan-2026-06-10.md` (the master plan) and the seven appendix files under `docs/research/data-sources/`.

## Why this exists

The Phase 4.5 base pipeline (`inventory → schema_inference → field_mapping → normalize → validate → audit → aggregate → emit`) was scoped for **partner Excel files**. The master source plan adds 15 Tier 1 open-API / open-CSV sources that the pipeline must also handle. This order extends Phase 4.5 with a **source registry** + **source-typed ingestion**.

## Scope — five sequential sub-PRs

| Sub-PR | Deliverable | Effort |
|---|---|---|
| 4.5+a | Source registry framework + first source (USGS WHISPers) | ~half day |
| 4.5+b | GBIF + iNaturalist DwC-A handler | ~half day |
| 4.5+c | eBird EBD + CDC ArboNET + USDA APHIS HPAI dashboard | ~half day |
| 4.5+d | NEON + IUCN Red List + EPA ECOTOX + USGS Bird Banding | ~half day |
| 4.5+e | Scheduled-pull workflow (GitHub Actions cron for daily/weekly sources) + provenance layer for the cube | ~half day |

Each sub-PR self-merges per §14 once CI is green AND the new source's smoke-test passes.

## Source registry shape

`wildlifestats/_pipeline/sources/<source-id>.json`:

```json
{
  "source_id": "usgs-whispers",
  "display_name": "USGS WHISPers / National Wildlife Health Center",
  "url": "https://whispers.usgs.gov",
  "license": "public-domain",
  "license_url": "https://www.usgs.gov/copyright",
  "license_allows_commercial": true,
  "license_allows_redistribution": true,
  "access_method": "bulk-download",
  "data_format": "csv",
  "endpoint": "https://www.sciencebase.gov/catalog/item/<item-id>",
  "refresh_cadence": "annual",
  "field_mapping": {
    "Event Date": "intake_date",
    "State": "state",
    "Species": "species_raw",
    "Diagnosis": "diagnosis_raw",
    "Mortality Count": "n"
  },
  "value_mapping_files": {
    "diagnosis_raw → reason_canonical": "wildlifestats/_pipeline/sources/usgs-whispers/diagnosis-aliases.json"
  },
  "smoke_test_record_count_min": 1000,
  "smoke_test_url_returns_200": true,
  "notes": "Public domain federal data. Refresh annually via ScienceBase bulk pull."
}
```

The pipeline runner gains a `--source <source-id>` flag that loads the registry entry and applies the source-specific mapping before running stages 4-8. Sample partner mappings (Phase 4.5 base) keep working unchanged — those use `--mapping <mapping-file>`.

## Provenance layer

Every cube cell gains a `sources` field that lists which source-ids contributed:

```json
{
  "year": 2024,
  "month": 5,
  "state": "VA",
  "county_fips": "51043",
  "class": "bird",
  "species": "passerine_songbird",
  "reason": "window_strike",
  "outcome": "released",
  "disposition": "wild_release_local",
  "n": 14,
  "sources": ["usgs-whispers:2024-annual", "synthetic-baseline:seed-42"]
}
```

This unblocks WREN's "How was this computed" affordance to cite specific upstream sources per query.

## License enforcement

The aggregator (`aggregate.py`) reads each source's `license_allows_commercial` flag. Cells whose contributing sources include ANY commercial-prohibited source land in `secure/cube/` (authenticated tier only). Cells whose contributing sources are all commercial-permitted land in `data/cube/` (public tier). The synthetic baseline is commercial-permitted; CC-BY-NC iNaturalist records that survive filtering are commercial-permitted only if the filter excluded NC records (verify in the iNaturalist source registry entry).

## Scheduled-pull workflow

`.github/workflows/source-refresh.yml`:

```yaml
name: source-refresh

on:
  schedule:
    - cron: '0 6 * * *'   # 06:00 UTC daily for HPAI dashboard
    - cron: '0 6 * * 1'   # 06:00 UTC Mondays for GDELT weekly
  workflow_dispatch:

jobs:
  refresh-daily-sources:
    if: github.event.schedule == '0 6 * * *' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Refresh USDA APHIS HPAI
        run: python wildlifestats/_pipeline/run.py --source usda-aphis-hpai
      - name: Commit if changed
        run: |
          if [ -n "$(git status --porcelain)" ]; then
            git config user.name "github-actions"
            git config user.email "github-actions@github.com"
            git add data/cube/
            git commit -m "data(wildlifestats): scheduled refresh — USDA APHIS HPAI"
            git push
          fi
```

## Acceptance criteria

By end of Phase 4.5+:

1. `python wildlifestats/_pipeline/run.py --source usgs-whispers` ingests, normalizes, validates, and emits a cube fragment with WHISPers data merged in.
2. Same for `gbif`, `inaturalist`, `ebird`, `cdc-arbonet`, `usda-aphis-hpai`, `neon`, `iucn-redlist`, `epa-ecotox`, `usgs-bbl` — ten total Tier 1 sources operational.
3. Each source's registry entry has license metadata; the aggregator routes commercial-restricted data to `secure/cube/` and commercial-permitted to `data/cube/`.
4. The cube's cells carry a `sources` array.
5. Scheduled-pull workflow runs successfully for at least one source on its first scheduled fire (verifiable via Actions log).
6. BRWC content guard passes — citations to specific named wildlife centers in source registries are OK (these are real public-domain academic citations), but no BRWC strings appear.
7. The `/methodology.html` page is updated to list the active sources by name with their licenses.
8. CI green across all stages.

## Out of scope (defer to future orders)

- Tier 2 partnership sources (WRMD, MMHSRP individual records, state FOIAs) — these need outreach work first.
- PDF extraction pipeline for rehab center annual reports — separate engineer order after the API-source pattern is stable.
- The Apify social-media plan — that ingests separately into its own pipeline; integration with the cube is a future cross-pipeline merge order.
- The cat-conflict `/wildlife/cats/` page — see master plan §6; that's a Phase 4 content order, not a pipeline order.

## Commit and merge

- Five branches, five sub-PRs, sequential.
- Commits: `data(wildlifestats): source registry — <source-id>` for the source-handling sub-PRs; `feat(wildlifestats): scheduled-pull workflow` for sub-PR e.
- Trailer: `Engineer: soar-aspen-beryl-heron`.
- Self-merge per §14 after CI green + smoke test.
- After each merge, append a `## Resolution` entry to this file. After all five merge, move to `closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 15:45 ET
