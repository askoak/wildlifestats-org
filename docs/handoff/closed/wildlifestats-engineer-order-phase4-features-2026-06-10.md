# Engineer order — Phase 4: national features layer

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer
**Date:** 2026-06-10 ~14:39 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Order #4 / Phase 3 merges)
**Authority:** §13 + §14.

## Why one order, multiple sections

Master plan §2 Phase 4 lists five sections (One Health, Parks, Wildlife, Data, Ingest). Each is independently buildable; in normal pacing they would be separate orders. Mike's directive 2026-06-10 14:38 ET ("get the website updated to the best it can be all elements - NO MIKE GATES") authorizes shipping them as a sequence of PRs without re-summoning architect approval between each.

Engineer's choice: ship as five sequential single-concern PRs (preferred — each is self-revertable) OR one combined PR (acceptable if each section is implemented cleanly and CI passes). Default to sequential PRs.

## §1 — `/data/` filtering interface

Build the public-facing query interface against `data/cube/admissions-cube.json`.

### Components

- **Filter controls**: year (multi-select), state (multi-select), class (multi-select), reason (multi-select). All filters default to "all".
- **Aggregate summary**: total records matching filters, by year and by state. Display as a small table.
- **Choropleth map**: US states colored by record count for current filter set. Use a public-domain US states TopoJSON file (commit it under `assets/maps/us-states.topojson`). Render with raw SVG + D3 or `topojson-client` only — no full D3 dataviz framework dependency.
- **CSV download** button. Generates CSV client-side from the filtered cube. Apply k-suppression per spec §10 — any (year, month, state, class, reason) row with n<10 collapses into "Suppressed (n<10)" with the sum of suppressed counts.

### Constraints

- All client-side. No backend. Cube JSON fetched once on page load, filtered in memory.
- No external CDN dependencies. Self-hosted libraries only — commit `topojson-client.min.js` to `assets/js/vendor/`.
- Page loads within 2s on a clean cache (cube file is the largest payload).
- Mobile responsive — filters stack vertically below 768px; map scales to viewport width.

### Voice / framing

Page heading: "Data". Kicker: "RESEARCH SECTION". Below the filters, a small note:

> Synthetic dataset, n=100,000 records distributed across all 50 states and the District of Columbia. Generated from regional distribution models calibrated against published wildlife rehabilitation literature. See [Methodology](/methodology.html) for the generation script and seed.

Below the map, a small caption:

> Counties with fewer than 10 records in the current filter are suppressed in downloads.

## §2 — `/one-health/` hub

Build out the One Health hub as an educational reference page sourcing from the cube + curated narrative.

### Components

- Hero paragraph (already shipped in Phase 2 — keep verbatim).
- Three subsections, each a card on the page:
  - **Cross-species disease patterns** — narrative on HPAI, leptospirosis, rabies, WNV. Plain text, 4–6 sentences each. Cite primary sources (CDC, USDA APHIS, USGS NWHC). Hyperlink to the source.
  - **Zoonotic risk by region** — small map showing infectious_disease admission count per state from the cube, filtered to `reason = infectious_disease`. Same TopoJSON / k-suppression as `/data/`.
  - **Wildlife–domestic animal–human connection** — narrative, 6–8 sentences, citing the One Health concept's institutional adoption (CDC One Health Office, WHO Tripartite, etc.).

### Voice

Earnest, citation-discipline. Brookings/Pew register. No alarmism, no marketing.

## §3 — `/parks/` national parks lens

Page that filters the cube by proximity to NPS units.

### Components

- A small NPS unit JSON file: `assets/data/nps-units.json` — name, type (NP, NM, NHP, etc.), state, lat, lon. Commit a snapshot from NPS data.gov (one-time download).
- For each NPS unit, compute the synthetic admissions count from counties within ~50 mi of the unit. Pre-compute this at build time (extend `generate_synthetic_cube.py` with an optional `--with-parks-overlay` flag that emits `data/cube/parks-overlay.json`). Engineer adds the flag and re-runs in this PR.
- Page UI: searchable list of NPS units; click one → one-page profile showing top 5 species classes admitted from nearby counties, dominant reasons, seasonal pattern (small line chart).

### Caveat copy (mandatory)

> These profiles use synthetic data plausibly shaped by regional species composition. They are not measured against any specific park's actual wildlife activity, and they are not a substitute for NPS interpretive resources or wildlife management reports.

Place this caveat at the top of every park profile page.

## §4 — `/wildlife/` encyclopedia

Taxonomic browse interface.

### Components

- Three-level navigation: class → guild → species archetype.
- Each species archetype gets a page with:
  - Range hint (a US states list or a small filled-state map showing which regions/states the archetype appears in per `species-archetypes.json`).
  - Top 3 synthetic admission reasons (computed from the cube).
  - Seasonal pattern — small 12-point monthly bar chart.
  - "What to do if you find one" — generic guidance routing to https://ahnow.org (AnimalHelpNow) as the institutional national directory. NO triage advice on the page itself.

### Voice

Encyclopedic, neutral. Avoid anthropomorphizing. No "majestic" / "beautiful" / similar.

## §5 — `/ingest/` multi-format ingestion methodology

NOT a live tool — a methodology page.

### Components

- Narrative explanation of how heterogeneous Excel files from wildlife centers would be normalized:
  1. Schema inference per file
  2. Field mapping to canonical WildlifeStats columns
  3. Species name normalization (common name → scientific name → archetype)
  4. Date / outcome standardization
  5. K-suppression on aggregation
- 3–5 sample CSV files committed under `samples/ingest/`, each showing a different made-up schema (column names like `Patient ID, Animal, Found Date` vs `case_no, species, intake`).
- A static "before/after" view for each sample — left column shows raw CSV, right column shows normalized JSON.
- No upload widget. No live file processing. Pure documentation.

### Voice

Methodological. The reader should leave understanding the conceptual pipeline, not believing they can upload files today.

## Acceptance criteria

For each sub-PR:

1. Section's section landing now hosts the full feature, not the Phase 2 placeholder paragraph.
2. CI green: BRWC content guard, link check, HTML validate, cube-validate.
3. Page loads in <3s on cold cache.
4. Mobile (375px) and desktop (1280px) render correctly.
5. No console errors.
6. No external CDN dependencies introduced.

## Out of scope

- Search across the encyclopedia by free text (defer — small dataset, browse is sufficient).
- Real species photographs (defer — text-forward site, photos add weight + licensing complexity).
- Real-time NPS data integration (defer — static snapshot).
- An ingestion upload widget (explicitly NOT shipping — methodology demo only).

## Commit and merge

- Five branches, five PRs, in this order: `engineer/phase4-data`, `engineer/phase4-one-health`, `engineer/phase4-parks`, `engineer/phase4-wildlife`, `engineer/phase4-ingest`.
- Each PR self-merges per §14 after CI green + Netlify preview QA.
- After each merge, append a `## Resolution` line to this file (one line per sub-phase). When all five are done, move this file to `closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:39 ET

## Resolution log (engineer `soar-aspen-beryl-heron`)

- **§1 /data/ filtering interface** — SHIPPED. PR #7, merged `42cec52`. Filters (year/class/reason/state, empty=all), aggregate tables, albersUsa choropleth (committed `us-states.topojson` = us-atlas states-albers-10m, pre-projected), k-suppressed client-side CSV. Vendored `topojson-client.min.js` (no CDN). All four CI jobs green; verified on Netlify preview.
- **§2 /one-health/ hub** — SHIPPED. PR #8, merged `78d3f70`. Three cards (cross-species disease patterns w/ USDA APHIS + CDC + USGS NWHC links; zoonotic choropleth filtered to infectious_disease; One Health institutional connection). Extracted shared `assets/js/choropleth.js`. All CI green; verified on preview.

- **§3 /parks/ National Parks lens** — SHIPPED. PR #10, merged `b2a2526`. `assets/data/nps-units.json` (61 National Parks within the 50 states). County centroids added to `county-fips.json` from the 2023 Census Gazetteer (cube verified byte-identical). `generate_synthetic_cube.py --with-parks-overlay` → `data/cube/parks-overlay.json` (per-park rollup, counties within 50 mi via haversine). Searchable list + profile (caveat, class/reason breakdown, inline-SVG seasonal chart); 0-county parks show an honest message. All CI green; verified on preview.

- **§4 /wildlife/ encyclopedia** — SHIPPED. PR #11, merged `fc7ece0`. Class → species-archetype browse from `species-archetypes.json`; per-archetype profile with modeled range map, top-3 reasons, seasonal chart, AHNow routing.
- **§5 /ingest/ methodology demo** — SHIPPED. PR #13, merged `04542c8`. 4 sample CSVs (incompatible schemas) under `samples/ingest/`; in-browser normalization pipeline with before/after views; no upload widget.

## Phase 4 COMPLETE

All five sections shipped (#7 data, #8 one-health, #10 parks, #11 wildlife, #13 ingest), all live on wildlifestats.netlify.app, all CI-green self-merges. This file moved to `closed/`.

### NEXT for the lane (unstarted)
- **Phase 6** (original master-plan, not yet dispatched as a separate engineer order): SEO + governance polish — flip `robots.txt` to allow + real `sitemap.xml`, OpenGraph/Twitter meta, schema.org `Dataset` markup, long-form methodology + governance pages.
- **New orders that arrived mid-run** (on `main`, unread): `wildlifestats-engineer-order-phase4.5-data-pipeline-2026-06-10.md`, `wildlifestats-engineer-order-phase4.5-source-registry-2026-06-10.md`, `wildlifestats-engineer-order-phase7-wren-2026-06-10.md`, plus `wildlifestats-data-sources-master-plan` and a `docs/research/data-sources/` corpus. Triage by stated dependencies on the next tick.
