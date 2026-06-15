# WildStats top 10 source operationalization plan

**Date:** 2026-06-15
**Author:** Codex
**Status:** Planning note for the next bounded source-implementation wave
**Scope:** Public-safe operationalization planning only. No app code, no schema
fork, no second registry.

## 1. Purpose

This note turns the seeded master source registry into a practical shortlist for
the next engineering wave. It answers a narrower question than the registry
itself:

- which sources should move first
- how each should be fetched
- what each joins on
- where attribution and license traps sit
- which public surface each source should serve first

The goal is to let an engineer start implementation without reopening source
selection.

## 2. Selection rule

These 10 sources are the current operationalization shortlist because together
they cover the strongest near-term WildStats surfaces:

- public center and Wildlife911 routing
- federal-first law watch
- rehab social monitoring
- cross-taxa occurrence and migration context
- wildlife disease and mortality context
- literature and methods support

This is not just the first 10 records in priority order. It is the most useful
cross-surface set drawn from the canonical registry for the next wave.

## 3. Included source_ids

1. `wildstats_rehab_centers_registry`
2. `wildstats_state_vet_ag_registry`
3. `gbif`
4. `inaturalist`
5. `ebird_ebd`
6. `usgs_whispers_nwhc`
7. `federal_register_api`
8. `regulations_gov_api`
9. `flyway_social_roster`
10. `pubmed_pmc`

## 4. Safe-now vs extra-review split

### Safe now with normal implementation discipline

- `wildstats_rehab_centers_registry`
- `wildstats_state_vet_ag_registry`
- `usgs_whispers_nwhc`
- `federal_register_api`
- `regulations_gov_api`
- `pubmed_pmc`

### Safe with tighter source-policy handling before broad public use

- `gbif`
- `inaturalist`
- `ebird_ebd`
- `flyway_social_roster`

The second group is still strategically important. It just carries more
license, attribution, or ToS nuance per record or per surface.

## 5. Per-source operationalization notes

## 5.1 `wildstats_rehab_centers_registry`

- **Why it is in the top 10:** It is the public directory spine and the most
  important join table for `/centers/`, `wildlife911`, funder context, future
  990 joins, and center-level enrichment.
- **Exact fetch posture:** No external fetch required for MVP. Treat
  `wildlifestats/_pipeline/sources/rehab-centers/centers.yaml` as the canonical
  local source and render or normalize from that file.
- **Expected join key / identity spine:** `slug` is the public page spine.
  `ein` is the financial-join spine. `state` and `county_fips` are geography
  joins. `legal_name` and `common_name` are fallback matching aids.
- **Refresh cadence:** Manual periodic review, then scheduled integrity checks
  later once downstream pages depend on it.
- **Attribution requirement:** Render as a WildStats-curated registry with
  source links preserved per row when displayed publicly.
- **Public-safe posture:** Public-safe for display and AI analysis. This is a
  local curated public-reference asset, not a private data source.
- **Known license or ToS trap:** Mixed upstream source provenance by row. Avoid
  overstating verification. Public display is fine; claims like permit status,
  24/7 intake, or species coverage should only reflect the explicit row values
  and linked sources.
- **Recommended first implementation surface:** `/centers/` and `wildlife911`.
- **Blocking dependencies:** None for MVP. Optional later dependencies include
  990 enrichment and center-specific help-content extraction.

## 5.2 `wildstats_state_vet_ag_registry`

- **Why it is in the top 10:** It is the strongest current state-by-state
  public government contact layer for disease and reporting context.
- **Exact fetch posture:** No external fetch required for MVP. Treat
  `wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml` as the canonical
  local source. Normalize to a state-contact lookup table if needed.
- **Expected join key / identity spine:** `jurisdiction` is the primary join
  key. `state_name` is the public label. `agency_name` is the display identity.
- **Refresh cadence:** Manual periodic review, ideally quarterly or when
  disease-program content changes materially.
- **Attribution requirement:** Preserve government-source provenance links per
  state when displayed or summarized.
- **Public-safe posture:** Public-safe for display and AI analysis as a public
  contact and program registry.
- **Known license or ToS trap:** Main risk is staleness, not license. Avoid
  presenting these contacts as emergency clinical advice.
- **Recommended first implementation surface:** `wildlife911` and later
  disease-reporting or methods pages.
- **Blocking dependencies:** None for MVP. Later state-specific law or permit
  surfaces can join on the same `jurisdiction` key.

## 5.3 `gbif`

- **Why it is in the top 10:** It is the strongest open cross-taxa occurrence
  backbone in the current public-source set.
- **Exact fetch posture:** Start with filtered API or download-based pulls for
  bounded taxa, geography, and date windows relevant to WildStats pages rather
  than attempting a giant general ingest. Cache normalized snapshots locally.
- **Expected join key / identity spine:** `gbifID` or occurrence identifier at
  record level; `taxonKey` as the taxonomic spine; date and geography
  normalization for downstream joins to state, county, or page geography.
- **Refresh cadence:** Scheduled pull at a bounded cadence, likely weekly for
  narrow operational slices and on-demand for exploratory use.
- **Attribution requirement:** GBIF attribution is required and downstream
  per-record license handling must be preserved.
- **Public-safe posture:** Public-safe if WildStats filters or aggregates by
  record license and avoids laundering mixed-license records into a generic
  public output.
- **Known license or ToS trap:** Mixed per-record licensing is the main trap.
  Do not treat GBIF as uniformly open. Derived public outputs must respect
  record-level license classes and attribution.
- **Recommended first implementation surface:** `source_explorer`,
  `species_pages`, and later Flyway anchor enrichment.
- **Blocking dependencies:** Taxonomy crosswalk strategy, likely via `itis`
  later; geography normalization policy; explicit per-record license filter.

## 5.4 `inaturalist`

- **Why it is in the top 10:** It is a high-value citizen-science source with
  strong observation and image-rich context, especially for public-facing
  species and seasonal pages.
- **Exact fetch posture:** Use the public API for bounded observation searches
  by taxon, place, and date. Start with metadata-first pulls and avoid broad
  image harvesting.
- **Expected join key / identity spine:** `observation_id` at record level,
  `taxon_id` for species joins, `place_id` or normalized state/county geography
  for page joins.
- **Refresh cadence:** Weekly or on-demand for bounded species and geography
  windows.
- **Attribution requirement:** Preserve iNaturalist attribution and creator or
  record-license handling where records are displayed directly.
- **Public-safe posture:** Safe when used as metadata, aggregated signals, or
  licensed record subsets. Risk rises if media is republished casually.
- **Known license or ToS trap:** Per-record license variation and media rights.
  Do not assume observation photos are safe to republish merely because the
  observation metadata is public.
- **Recommended first implementation surface:** `species_pages` and Flyway
  anchor feeds.
- **Blocking dependencies:** Per-record license filter, taxonomy normalization,
  and a clear no-raw-media public posture.

## 5.5 `ebird_ebd`

- **Why it is in the top 10:** It is the strongest avian migration and
  occurrence backbone in the current registry and is especially valuable for
  Flyway and bird-specific species pages.
- **Exact fetch posture:** Use an approved access path to pull bounded avian
  extracts by geography, taxon, and date window. Start with narrow bird-only
  slices rather than a full national historical load.
- **Expected join key / identity spine:** `species_code` or canonical bird
  taxonomy key for species joins; `checklist_id` or observation row identity
  for audit; normalized geography for regional surfaces.
- **Refresh cadence:** Monthly or other bounded batch cadence, aligned to the
  data-distribution posture already noted in the registry.
- **Attribution requirement:** Strong attribution required. Treat eBird as a
  heavily governed source, not a generic open observation feed.
- **Public-safe posture:** Safe for derived analysis and tightly scoped public
  outputs if WildStats stays inside the approved license and redistribution
  posture.
- **Known license or ToS trap:** Noncommercial and redistribution limits are
  the primary trap. Avoid broad raw-record public mirrors or casual export of
  redistributed observation tables.
- **Recommended first implementation surface:** Flyway anchor history, bird
  species pages, and later migration-signal methods notes.
- **Blocking dependencies:** Credentialed access, avian taxonomy crosswalk, and
  explicit public-output rules for derived vs. direct record exposure.

## 5.6 `usgs_whispers_nwhc`

- **Why it is in the top 10:** It is the highest-value open U.S. wildlife
  disease and mortality event backbone in the current registry.
- **Exact fetch posture:** Pull periodic public exports or downloadable event
  tables into a normalized event store. Start with recent years plus a bounded
  backfill, not an open-ended ingest.
- **Expected join key / identity spine:** Wildlife-event identifier from the
  export if available, plus species/taxon, state, county, diagnosis, and event
  date as the durable join envelope.
- **Refresh cadence:** Scheduled pull on a periodic snapshot basis, likely
  weekly or monthly depending on actual public release cadence.
- **Attribution requirement:** USGS attribution required on display and methods
  surfaces.
- **Public-safe posture:** Public-safe for display and AI analysis. Strong fit
  for research and species context.
- **Known license or ToS trap:** Main risk is over-interpreting event data as
  clinical truth in real time. Treat it as authoritative surveillance context,
  not a live hotline feed.
- **Recommended first implementation surface:** `research_methods`,
  `species_pages`, and later sector disease context.
- **Blocking dependencies:** Taxonomy normalization and a disease-event schema
  for the WildStats side of the ingest.

## 5.7 `federal_register_api`

- **Why it is in the top 10:** It is the cleanest federal law-watch backbone
  and the most implementation-ready source for a credible policy tracker.
- **Exact fetch posture:** Daily metadata pull for wildlife-relevant notices,
  rules, proposed rules, and agency actions using topic and agency filters.
  Cache normalized metadata locally.
- **Expected join key / identity spine:** Federal Register document identifier,
  citation, publication date, agency, and canonical document URL.
- **Refresh cadence:** Daily.
- **Attribution requirement:** Federal Register attribution should travel with
  links and source cards.
- **Public-safe posture:** Public-safe for display and AI analysis. Strong
  source for a federal-first `law_watch` MVP.
- **Known license or ToS trap:** Low legal risk. The real trap is false topic
  matching. Do not equate any environmental or veterinary notice with
  wildlife-sector relevance without a filtering layer.
- **Recommended first implementation surface:** `law_watch`.
- **Blocking dependencies:** A normalized `law_watch` record schema and a first
  keyword or agency filter policy.

## 5.8 `regulations_gov_api`

- **Why it is in the top 10:** It complements the Federal Register by adding
  docket and comment-period metadata, which is what makes a law-watch page
  useful rather than merely archival.
- **Exact fetch posture:** Authenticated daily pull for wildlife-relevant
  dockets, supporting documents, and comment deadlines. Cache normalized docket
  metadata, not full text.
- **Expected join key / identity spine:** Docket identifier, document
  identifier, comment deadline, agency, and canonical docket URL.
- **Refresh cadence:** Daily.
- **Attribution requirement:** Preserve Regulations.gov attribution and source
  links at the docket or document level.
- **Public-safe posture:** Public-safe for display and AI analysis as metadata.
- **Known license or ToS trap:** Low license risk. Main trap is scope creep
  into full-text document replication or overstating what a docket means.
- **Recommended first implementation surface:** `law_watch`.
- **Blocking dependencies:** API credential handling and the same normalized
  `law_watch` schema used by `federal_register_api`.

## 5.9 `flyway_social_roster`

- **Why it is in the top 10:** It is the operational spine for the rehab social
  monitor and a distinctive WildStats surface not easily replicated by generic
  wildlife sites.
- **Exact fetch posture:** Start with the existing curated CSV roster and treat
  it as the monitored-source registry. The roster itself is local; downstream
  post discovery or extraction happens through controlled Flyway pipelines.
- **Expected join key / identity spine:** `org slug` or equivalent roster org
  identifier joined back to the rehab-center registry. Platform plus source URL
  identify the monitored surface.
- **Refresh cadence:** Manual periodic roster review; downstream signal pulls on
  the Flyway cadence rather than on the CSV cadence.
- **Attribution requirement:** Public outputs should link back to the source
  organization and original post URL, not rehost content.
- **Public-safe posture:** The roster is safe as a registry. Extracted public
  outputs must remain metadata-plus-link only.
- **Known license or ToS trap:** Highest risk item in the top 10. Do not store
  or republish raw post text, images, or platform-native media outside the
  controlled extraction posture already documented.
- **Recommended first implementation surface:** `rehab_social_monitor` and
  `flyway`.
- **Blocking dependencies:** Metadata-only `rehab_social_signal` schema,
  extraction policy, take-down procedure, and join discipline with the center
  registry.

## 5.10 `pubmed_pmc`

- **Why it is in the top 10:** It is the strongest current biomedical and
  veterinary literature backbone for WildStats methods, source cards, and
  research support.
- **Exact fetch posture:** Use NCBI E-utilities for metadata search and bounded
  result retrieval. Treat PubMed metadata as the primary public artifact and
  only use PMC full text where it is actually open and needed.
- **Expected join key / identity spine:** `PMID` as the main article identifier,
  `PMCID` when open full text exists, and DOI as the cross-source bridge to
  Crossref or other literature metadata layers.
- **Refresh cadence:** Daily or on-demand metadata refresh for narrow topic
  queries.
- **Attribution requirement:** Preserve PubMed or PMC links and article-level
  metadata provenance.
- **Public-safe posture:** Strongly public-safe for metadata and summaries.
  Full-text posture varies and should not be treated as uniform.
- **Known license or ToS trap:** Do not assume all PubMed-linked articles are
  open for full-text reuse. Metadata is safe; full text varies by journal and
  PMC status.
- **Recommended first implementation surface:** `research_methods` and
  `source_cards`.
- **Blocking dependencies:** A literature-card schema and topic-query policy so
  WildStats does not become an indiscriminate search mirror.

## 6. Execution waves

## Wave 1 — Public spine and federal utility

- `wildstats_rehab_centers_registry`
- `wildstats_state_vet_ag_registry`
- `federal_register_api`
- `regulations_gov_api`

**Why first:** This wave creates the cleanest immediate public value with the
lowest policy and license risk. It powers `wildlife911`, the center directory,
and a federal-first `law_watch` MVP.

## Wave 2 — Public-safe live signal and surveillance layer

- `flyway_social_roster`
- `usgs_whispers_nwhc`
- `gbif`

**Why second:** This wave adds differentiated signal and disease context, but
requires stronger source-policy discipline than Wave 1. It should follow the
public spine, not precede it.

## Wave 3 — Taxonomy-heavy and literature-heavy enrichment

- `inaturalist`
- `ebird_ebd`
- `pubmed_pmc`

**Why third:** This wave is strategically strong but needs more careful license
and taxonomy handling. It enriches species pages, migration work, and research
support after the public backbone is stable.

## 7. Recommendation

If the next engineering session wants the highest-leverage low-collision
implementation sequence, it should start with:

1. `wildstats_rehab_centers_registry`
2. `wildstats_state_vet_ag_registry`
3. `federal_register_api`
4. `regulations_gov_api`

Then it should stop and ratify the first public surfaces before moving into the
license-heavier citizen-science and social-monitoring stack.
