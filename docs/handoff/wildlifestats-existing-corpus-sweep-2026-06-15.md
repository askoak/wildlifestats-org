# Existing Corpus Sweep: WildStats + BRWC

**Date:** 2026-06-15
**Author:** Codex
**Purpose:** Answer the blunt question: did we already pull a meaningful body
of source research and data into git across both repos, and if so, what is
there, what overlaps, and what should move into the WildStats lane?

## 1. Bottom line

Yes. There is already a substantial corpus in git across both repos. The work
is not at the "blank sheet" stage.

WildStats already contains:

- a national research corpus on wildlife, environment, and public-source data
- a national rehab-center registry
- seeded public-source YAML registries for agencies, associations, funders, and
  USFWS offices
- an early-warning social-source seed for Flyway
- working pipeline scaffolding under `wildlifestats/_pipeline/`

BRWC already contains:

- real operational data, public social archives, and center-specific analytics
- source-policy and licensing decisions for eBird, GBIF, iNaturalist, NOAA,
  BBL, VDWR, and NASA
- taxonomy-cache and enrichment patterns that should be adapted, not copied
  blindly
- a clear internal/public corpus boundary that WildStats should imitate

The main correction to earlier planning is simple:

**future WildStats work should start from the existing research and source
registries already in git, not from fresh open-ended discovery.**

## 2. Confidence level and limits

This was a real sweep of the high-value corpus and pipeline layers. It was not a
forensic read of every generated artifact.

What was covered with high confidence:

- WildStats `docs/research/`
- WildStats `wildlifestats/_pipeline/sources/`
- WildStats core `docs/handoff/` planning notes
- BRWC `_planning/`
- BRWC `_data/`
- BRWC `_corpus/` and `_corpus_public/` boundary docs

What was **not** exhaustively reviewed:

- every HTML page in both sites
- every chart PNG and generated analysis artifact
- every raw social extract or log file
- every code path in the BRWC worker

That means this sweep is strong enough for planning and prioritization, not a
claim that every file in both repos was line-reviewed.

## 3. What this sweep actually covered

### WildStats high-density areas

The most crowded WildStats research and planning zones found during inventory:

- `docs/handoff/` - 56 files
- `docs/research/data-sources/` - 7 files
- `docs/research/phase9-sources/` - 7 files
- `docs/research/rehab-registry-sources/` - 5 files
- `docs/research/critique/` - 5 files
- `wildlifestats/_pipeline/sources/flyway/signals/` - 8 files

### BRWC high-density areas

The most crowded BRWC planning and data zones found during inventory:

- `_planning/analyses/` - 78 files
- `_planning/analyses/charts/` - 42 files
- `_planning/work-orders/` - 22 files
- `_data/magpi/templates/` - 22 files
- `_data/social/raw/` - 20 files
- `docs/handoff/` - 18 files
- `_planning/decisions/` - 14 files
- `_data/social/` - 13 files
- `_planning/research/` - 10 files

This is why the conclusion is not speculative. Both repos already have a deep
paper trail and data layer.

## 4. WildStats: what already exists

### 4.1 Source-research corpus already in git

The strongest proof is `docs/research/data-sources/`, especially:

- `01-federal-state.md`
- `03-citizen-science.md`
- `04-rehab-onehealth.md`
- `05-apis-scrapers-literature.md`

Those files already map a large part of the target source universe:

- federal wildlife, disease, and environmental sources
- citizen-science systems
- rehab / One Health / disease surveillance systems
- APIs, literature endpoints, and scraper candidates

This is already the nucleus of the future master source database.

### 4.2 Canonical public-source registries already staged

Under `wildlifestats/_pipeline/sources/`:

- `rehab-centers/centers.yaml`
- `state-vet-ag/agencies.yaml`
- `statewide-associations/associations.yaml`
- `sector-funders/funders.yaml`
- `usfws-offices/offices.yaml`
- `README.md` for Flyway seed sources

Key facts:

- `rehab-centers/centers.yaml` header says **177 organizations** and **161
  EIN-verified**. It is the canonical source for the public centers directory,
  Form 990 joins, help-page indexing, and annual-report extraction.
- a quick top-level `slug` count now returns **181**, so the header and the body
  are out of sync and need reconciliation
- `state-vet-ag/agencies.yaml` covers **51 jurisdictions**
- `statewide-associations/associations.yaml` contains **20 association rows**
- `sector-funders/funders.yaml` contains **33 funder rows**
- `usfws-offices/offices.yaml` contains **78 office rows**

These are not rough notes. They are already canonical-ish structured assets.

### 4.3 National social-monitoring seed already exists

`wildlifestats/_pipeline/sources/README.md` confirms the Flyway lane already has
a seeded national social roster:

- `flyway-social-seed-top100.csv`
- `flyway-social-pages.json`
- `flyway-phrase-search.json`
- `journey-north.json`

Important lane-discipline rule already captured there: BRWC was removed from
the national Flyway seed so WildStats does not accidentally become a BRWC mirror.

### 4.4 Pipeline scaffolding already exists

WildStats also already has meaningful code scaffolding:

- `_pipeline/_common/` for shared fetch, credentials, API clients, and tests
- `_pipeline/flyway/` for social and signal extraction orchestration
- `_pipeline/firm_profile/` for per-organization website harvesting
- migrations under `_pipeline/_common/migrations/`

This matters because the repo already anticipated:

- typed source ingestion
- shared credential handling
- structured writes
- bucketed data products

### 4.5 Research and methodology notes already exist

WildStats also already carries:

- `docs/research/authoritative-sources/`
- `docs/research/phase9-sources/`
- `docs/research/rehab-registry-sources/`
- `docs/research/critique/`

That means the repo already has source discovery, source verification, and
methodological self-critique in one place.

## 5. BRWC: what already exists

### 5.1 Internal corpus and public-safe corpus are already separated

Boundary docs are clear:

- `_corpus/README.md`
- `_corpus_public/README.md`

The BRWC pattern is good and should be copied conceptually:

- internal corpus is a working extraction/input layer
- public-safe corpus is a separately built dataset, not a runtime filter on the
  staff corpus

That is the right design pattern for WildStats too.

### 5.2 BRWC already has a serious public social corpus

`_data/social/README.md` documents a normalized archive across four platforms:

- Instagram: 2,672 posts
- Facebook: 1,452 posts
- YouTube: 318 posts
- TikTok: 154 posts

The repo also has:

- `posts.jsonl`
- `comments.jsonl`
- `search-index.json`
- raw ingest logs
- image-library artifacts exceeding **6.3k** rows
- national-seed and discovery-stage files used for external visual discovery

This is useful for patterns, schemas, and monitoring workflows. It is **not**
the dataset WildStats should ingest as a direct national source of truth.

### 5.3 BRWC already has source-policy decisions worth reusing

High-signal planning files:

- `_planning/decisions/2026-06-15-external-data-sources-tool-matrix.md`
- `_planning/research/2026-06-14-phase-8-apify-discovery-plan.md`
- `_planning/specs/2026-06-14-inaturalist-integration-spec.md`

Those documents already answer many of the hard questions for WildStats:

- which external sources are worth the trouble
- where license friction exists
- which tools should use live API calls versus cached reference tables
- when scraping is justified versus when an API or bulk export is better

The BRWC external-source priority spine is already visible:

- eBird taxonomy
- GBIF taxonomy / occurrences
- iNaturalist
- NOAA weather
- USGS Bird Banding Lab
- VDWR or state wildlife data
- NASA open environmental data

### 5.4 BRWC already has reusable taxonomy and enrichment patterns

Key files:

- `_data/external/README.md`
- `_data/external/source-registry.json`
- `_data/ebird/README.md`
- `_data/va-wildlife-catalog-README.md`
- `_data/inaturalist/*.json`

What is already solved there:

- source-attribution metadata shape
- display badge / license-note pattern
- cached taxonomy tables
- public-domain and license-filter rules
- taxon-keyed enrichment architecture
- state wildlife catalog schema

WildStats should inherit those patterns, but with national/public-safe data.

## 6. What is common across both repos

There is already a shared conceptual spine:

- taxonomy and species normalization matter
- public-safe source attribution matters
- citizen-science data is valuable but license-sensitive
- official agencies and nonprofits are both important
- social monitoring is useful as a signal layer, not as the whole product
- cached reference data is usually better than live front-end API calls

There is also already a shared source universe emerging across both repos:

- eBird
- GBIF
- iNaturalist
- NOAA / NWS
- USFWS
- state wildlife / agriculture / veterinary agencies
- ProPublica Nonprofit Explorer
- annual reports / Form 990s
- rehab center public sites and social handles

## 7. What is different

### WildStats

WildStats is building a **national public infrastructure layer**:

- directories
- research registries
- cross-center comparisons
- public-safe source discovery
- national or multi-state monitoring

### BRWC

BRWC is building a **center-specific operating and storytelling layer**:

- patient and intake analytics
- center voice systems
- internal RAG
- staff workflows
- public social archive
- Virginia-specific species context

The implication is important:

**WildStats should borrow BRWC's schemas, guardrails, and source-policy logic.
WildStats should not absorb BRWC's internal data exhaust.**

## 8. Crosswalk: which existing files should seed which future work

This is the most useful practical output of the sweep.

### 8.1 Source registry seeding

Use these first:

- `docs/research/data-sources/01-federal-state.md`
- `docs/research/data-sources/03-citizen-science.md`
- `docs/research/data-sources/04-rehab-onehealth.md`
- `docs/research/data-sources/05-apis-scrapers-literature.md`
- `wildlifestats/_pipeline/sources/*`

Purpose:

- seed official data, citizen science, disease, literature, and directory
  sources

### 8.2 Attribution and license-policy seeding

Use these first:

- `BRWC:_data/external/source-registry.json`
- `BRWC:_data/external/README.md`
- `BRWC:_data/ebird/README.md`
- `BRWC:_planning/decisions/2026-06-15-external-data-sources-tool-matrix.md`

Purpose:

- port source metadata fields
- port attribution patterns
- port refresh cadence logic
- port source-by-surface license reasoning

### 8.3 Species and enrichment architecture

Use these first:

- `BRWC:_planning/specs/2026-06-14-inaturalist-integration-spec.md`
- `BRWC:_data/va-wildlife-catalog-README.md`
- `BRWC:_data/inaturalist/*.json`

Purpose:

- design species joins
- design taxon-keyed enrichment
- design state or national species catalog schema

### 8.4 Public-routing and help-content work

Use these first:

- current center directory YAML
- WildStats Phase 9 bucket taxonomy
- Wildlife911 planning docs

Purpose:

- build species x center help matrix
- bind public routing to center capabilities and public content

### 8.5 Flyway and public signal work

Use these first:

- `wildlifestats/_pipeline/sources/flyway/*`
- `wildlifestats/_pipeline/flyway/*`
- `BRWC:_planning/research/2026-06-14-phase-8-apify-discovery-plan.md`

Purpose:

- preserve the "signals not raw reposting" posture
- keep scraping bounded and budgeted

## 9. What should be copied or adapted from BRWC into WildStats

### Copy the pattern

1. `source-registry.json` structure
   Use the BRWC attribution fields as the base schema for a WildStats source
   registry: display name, link, license note, auth, use constraints,
   attribution text, refresh cadence, and public-safety notes.

2. External-source decision matrix logic
   Port the source-evaluation method from BRWC's tool matrix into a WildStats
   source scoring system:
   `api_first`, `bulk_export_ok`, `scrape_only_if_needed`, `public_safe`,
   `license_risk`, `analysis_value`, `directory_only`, `on_demand_only`.

3. Taxonomy cache approach
   Reuse BRWC's cached reference-table pattern for eBird and GBIF, but bind it
   to WildStats-owned public datasets and public-facing attribution rules.

4. iNaturalist enrichment architecture
   Reuse the taxon-keyed enrichment design from the BRWC spec. It is one of the
   strongest building blocks for national phenology, species pages, and
   cross-source joins.

5. Public-corpus boundary discipline
   Copy the `_corpus_public/` principle exactly: build public-safe corpora from
   explicitly public-safe sources, not by filtering a broader internal corpus at
   runtime.

6. State wildlife catalog schema
   The Virginia wildlife catalog is a useful schema template for state-by-state
   species catalogs, but the `brwc_treated` semantics should be replaced with a
   national/public field model.

### Copy the work product where it is already public-safe

1. Source research conclusions
   The logic in BRWC's iNaturalist and external-source planning docs should be
   cited directly in WildStats planning notes instead of rediscovered.

2. License and attribution rules
   eBird, GBIF, and iNaturalist rules should be harmonized across both repos so
   the same source is not treated one way in BRWC and another way in WildStats.

3. Visual/source discovery workflow
   Apify should remain a scoped discovery tool, not the default acquisition
   path. The BRWC phase-8 plan is useful because it treats scraping as a
   budgeted experiment rather than a reflex.

## 10. What should not be copied from BRWC into WildStats

Do **not** move these into the WildStats public lane:

- `_corpus/` raw extracted BRWC text
- patient database artifacts
- `_data/magpi/patient_cube.jsonl`
- Quill audit logs and redaction workflow data
- raw comments or commenter-handle archives
- BRWC-only social performance data
- staff-only banding or case-history workflows
- donor-adjacent use of license-sensitive source data

Also do not point WildStats tools at BRWC internal endpoints or BRWC-auth-gated
tables. WildStats needs its own clean public data spine.

## 11. What this means for the proposed master database

The master database should not begin with "scrape the web and see what happens."
It should begin by formalizing what is already here.

The right first table is a **source registry**, not a giant content dump.

Minimum fields:

- `source_id`
- `source_name`
- `category`
- `geography`
- `taxa_scope`
- `source_type`
- `access_mode`
- `auth_required`
- `license_type`
- `public_safe_for_display`
- `public_safe_for_ai_analysis`
- `update_cadence`
- `structured_data_available`
- `scrape_candidate`
- `ingest_priority`
- `canonical_url`
- `notes`

Recommended ingest buckets:

- `pull_core`
- `pull_periodic`
- `directory_only`
- `manual_on_demand`
- `do_not_ingest`

That registry can be built immediately from the WildStats research files plus
the BRWC source-policy docs already in git.

## 12. What is already researched enough vs what is still thin

### Already researched enough to start implementation

- official data-source families
- citizen-science families
- rehab-center directory scaffolding
- state-vet-ag, association, funder, and USFWS registries
- public routing and center help-content concept
- source-policy and license posture

### Still needs targeted follow-up

- exact registry schema chosen for the canonical implementation
- per-page inclusion rules for news vs law vs social
- legal validation of a few borderline sources
- count and header reconciliation in some YAML registries
- which specific law and news source set should ship first

The key point is that the remaining work is **consolidation and operational
selection**, not broad discovery.

## 13. Recommended reading order for future sessions

If a fresh session needs fast context, read in this order:

1. this corpus sweep note
2. the source-registry planning note
3. the BRWC alignment work plan
4. `docs/research/data-sources/01-federal-state.md`
5. `docs/research/data-sources/03-citizen-science.md`
6. `docs/research/data-sources/04-rehab-onehealth.md`
7. `docs/research/data-sources/05-apis-scrapers-literature.md`
8. `wildlifestats/_pipeline/sources/*`
9. BRWC external-source matrix and iNaturalist spec

That reading order gets a new session to the real work quickly.

## 14. Recommended next bounded sequence

1. Build `master-source-registry` in WildStats from existing files only
   Start with `docs/research/data-sources/*.md`, the YAML registries in
   `wildlifestats/_pipeline/sources/`, and BRWC's external-source matrix.

2. Split sources into two lanes
   `analysis_ingest` versus `external_directory_only`.

3. Create source-family templates
   One schema each for agencies, datasets/APIs, rehab centers, associations,
   funders, laws/regulations, news feeds, and social feeds.

4. Reconcile factual inconsistencies in current registries
   First example: `centers.yaml` header counts versus actual row count.

5. Stand up only 1-2 pilot acquisition flows
   Best candidates: national rehab-center registry enrichment and a public
   wildlife-law/regulation tracker seed.

6. Use scraping only after API, bulk, and public YAML routes are exhausted
   The repo already points toward API-first, cache-second, scrape-third.

## 15. Final read

The important answer is yes: there is already a large body of useful work in git
for both BRWC and WildStats.

WildStats is not missing source research. It is missing consolidation.

WildStats is not missing public-safe product ideas. It is missing a stronger
data spine and execution order.

BRWC is not the database to merge into WildStats. It is the pattern library and
policy lab that WildStats should selectively inherit from.
