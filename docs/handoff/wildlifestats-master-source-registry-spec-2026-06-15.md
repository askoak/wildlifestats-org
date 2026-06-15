# WildStats master source registry spec

**Date:** 2026-06-15
**Author:** Codex
**Status:** Canonical schema note for the first seeded WildStats source registry

## Purpose

This note defines the first canonical `master-source-registry.yaml` for
WildlifeStats. It converts the existing repo corpus into a single source index
that can support:

- pipeline orchestration
- public source discovery
- ingest-tier governance
- page-feed routing
- later normalization into JSON or database tables

## Canonical artifacts

The canonical seeded registry for this phase is:

- `wildlifestats/_pipeline/sources/master-source-registry.yaml`

This phase also writes:

- this schema note
- a gap memo
- an operational-fields note for attribution and refresh behavior

GitHub-side architect review and cross-session coordination for this slice are
described in:

- `docs/handoff/wildlifestats-github-watch-protocol-2026-06-15.md`

No second registry file should be created in parallel.

## Top-level shape

The registry file uses one top-level object with these keys:

- `schema_version`
- `registry_id`
- `generated_on`
- `status`
- `canonical_notes`
- `sources`

`sources` is the authoritative array of normalized source records.

## Unit of record

One record equals **one source system, feed, curated registry, or platform**.

Examples:

- one record for GBIF
- one record for WRMD
- one record for the WildStats rehab-center registry
- one record for the Federal Register API

This first registry does **not** create one record per state agency office, one
record per rehab center, or one record per individual endpoint variant.

## Field set

Each record in `master-source-registry.yaml` carries these fields:

- `source_id`
- `name`
- `source_class`
- `source_family`
- `origin_type`
- `canonical_url`
- `access_method`
- `format`
- `geography_scope`
- `taxa_scope`
- `license_type`
- `public_safe_for_display`
- `public_safe_for_ai_analysis`
- `attribution_badge`
- `attribution_required`
- `cache_posture`
- `refresh_cadence`
- `refresh_mode`
- `credential_hint`
- `ingest_tier`
- `intended_use`
- `priority`
- `status`
- `page_targets`
- `seeded_from`
- `notes`

## Controlled vocabularies

### `source_class`

- `official_data`
- `research_data`
- `literature`
- `organization_site`
- `news`
- `social`
- `repository`
- `law_policy`
- `directory`

### `source_family`

- `taxonomy_occurrence`
- `rehab_center`
- `state_agency`
- `federal_agency`
- `association`
- `funder`
- `law_regulation`
- `disease_surveillance`
- `literature_index`
- `news_monitoring`
- `social_monitor`
- `technical_reference`

### `origin_type`

- `wildlifestats_curated`
- `external_public`
- `external_restricted`
- `external_partner`

### `access_method`

- `git_tracked_yaml`
- `git_tracked_json`
- `git_tracked_csv`
- `public_api`
- `authenticated_api`
- `bulk_download`
- `dashboard_export`
- `rss_feed`
- `html_scrape`
- `manual_request`
- `partner_request`

### `license_type`

- `public_domain`
- `cc0`
- `cc_by`
- `cc_by_nc_mixed`
- `custom_noncommercial`
- `mixed_open`
- `mixed_restricted`
- `restricted_partner`
- `not_stated`

### `cache_posture`

- `curated_local_registry`
- `cached_reference`
- `build_time_derived`
- `periodic_snapshot`
- `live_query_cautious`
- `manual_review`
- `partner_request_only`

### `refresh_mode`

- `manual_curated`
- `scheduled_pull`
- `scheduled_rebuild`
- `live_query`
- `on_demand`
- `request_driven`

### `ingest_tier`

- `pull_core`
- `pull_periodic`
- `directory_only`
- `manual_on_demand`
- `do_not_ingest`

### `intended_use`

- `ai_analysis`
- `public_directory`
- `page_feed`
- `reference_only`
- `secure_only`

### `status`

- `operational`
- `reviewed`
- `seeded`
- `parked`
- `blocked`

## Interpretation rules

### Public-safe flags

- `public_safe_for_display` means the source is generally acceptable for public
  display in a WildlifeStats surface when attribution is respected.
- `public_safe_for_ai_analysis` means the source may be processed into
  WildlifeStats analysis or retrieval layers under the current planned posture.

These are not universal legal truths. They are current WildStats policy flags
based on the source corpus reviewed to date.

### `intended_use` is primary, not exhaustive

Each record gets one `intended_use` value as its primary classification. Multi-
surface applicability is handled through `page_targets`.

### Local curated files count as first-class sources

The following kinds of files are valid registry records:

- WildStats-owned YAML registries
- local JSON configuration assets that function as source spines
- curated CSV rosters

This avoids the false split between "external data" and "our own registries."

## What this phase is not doing

This phase is not:

- redefining the Phase 9 bucket system
- creating one JSON file per source
- building ingestion code
- building UI
- performing broad new discovery

It is building the canonical source index first.

## Acceptance criteria for this phase

This registry phase is complete enough when:

1. there is one canonical seeded registry file
2. the file is grounded in existing repo materials
3. every record has `ingest_tier` and `intended_use`
4. the file is readable and easy to extend
5. later sessions can operationalize sources without reopening schema design
