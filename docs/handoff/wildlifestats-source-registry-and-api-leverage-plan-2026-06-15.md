# WildlifeStats planning note: source registry, owned APIs, and staged acquisition

**Author:** Codex planning note
**Date:** 2026-06-15
**Status:** Expanded planning note grounded in the existing WildStats and BRWC
audits
**Trigger:** Mike directive to plan a searchable, filterable master database of
wildlife, nature, environment, and related sites, datasets, APIs, and
repositories, plus a set of public-facing WildlifeStats pages built from that
source universe.

## 1. Core decision

Do **not** begin by scraping the whole web.

Begin by building a **source registry** and treating acquisition as a ranking
problem:

1. Which sources are worth knowing about?
2. Which sources are worth owning locally?
3. Which sources are better left as external references that WildlifeStats
   queries or cites on demand?

The correct sequence is:

`discover -> classify -> score -> decide ingest tier -> only then acquire`

## 2. What changed after the audit

This plan is now more specific than the original "source registry first"
recommendation because the audit showed two important things:

1. WildStats already has a meaningful source corpus in
   `docs/research/data-sources/` and `wildlifestats/_pipeline/sources/`.
2. BRWC already solved several important source-policy problems:
   attribution schema, cache-and-refresh patterns, public-safe extraction
   posture, and source-by-surface license reasoning.

That means this initiative does **not** start from zero. It starts by
consolidating existing work into one canonical registry and then deciding what
to operationalize.

## 3. New constraint from the credentials inventory

The credential catalog at:

`C:\Users\Hello\OneDrive - Michael Oak Advisors\Credentials\Credentials-README.md`

changes the recommended strategy in an important way:

**WildlifeStats should be API-first, scrape-second.**

You already control enough relevant infrastructure and third-party access that
the first version of this effort should lean on:

- owned API keys
- official public APIs
- official bulk exports
- repo metadata APIs
- and structured feeds

before resorting to broad HTML scraping.

This lowers:

- legal risk
- breakage risk
- maintenance burden
- junk-data volume

## 4. Relationship to existing repo specs

This note should align with, not replace, the earlier WildStats framework docs:

- `docs/handoff/wildlifestats-engineer-order-phase4.5-source-registry-2026-06-10.md`
- `docs/handoff/wildlifestats-engineer-order-phase9-multi-source-framework-2026-06-11.md`
- `docs/handoff/wildlifestats-form990-ingestion-spec-2026-06-11.md`
- `docs/handoff/wildlifestats-flyway-spec-2026-06-10.md`
- `docs/handoff/wildlifestats-existing-corpus-sweep-2026-06-15.md`

Practical implication:

- the earlier Phase 4.5 source registry order defined a registry shape for
  source-typed ingestion
- the Phase 9 order defined bucket taxonomy by organization type x bucket
- this note defines the **higher-level source strategy** that should feed both

The registry should therefore serve **both**:

- pipeline orchestration
- public product discovery and filtering

## 5. What this project actually is

This effort is not one database. It is four related layers.

### Layer A - Source Registry

A searchable inventory of wildlife-related sources:

- datasets
- APIs
- bulk downloads
- state portals
- rehab-center sites
- research groups
- literature archives
- GitHub repositories
- trackers
- news sources
- social feeds

This is the control tower.

### Layer B - Acquisition Rules

A decision layer that tells WildlifeStats:

- what may be fully ingested
- what should be selectively ingested
- what should only be indexed
- what must remain reference-only

This is the governance layer.

### Layer C - Owned Knowledge Base

The subset of source content and metadata WildlifeStats actually stores,
normalizes, and analyzes.

This is the research substrate.

### Layer D - Public Products

The user-facing pages built from A, B, and C:

- directory/search pages
- law watch
- social monitor
- news digest
- species/help pages
- source explorer

This is what the public sees.

## 6. Registry design goals

The master source registry should do six jobs at once:

1. act as the canonical inventory of what WildlifeStats knows exists
2. distinguish authoritative sources from commentary, vendors, and media
3. encode licensing and public-safety decisions explicitly
4. tell the pipeline how to access a source
5. tell product pages whether a source is suitable for a given surface
6. make later onboarding of new sources routine instead of ad hoc

If the registry cannot answer those six questions, it is just a link list.

## 7. Recommended logical data model

The project needs more than one table or file shape, even if the first phase is
implemented in flat YAML or CSV.

### 7.1 `source_registry`

One record per source, dataset, site, feed, or repo.

This is the canonical inventory.

### 7.2 `source_assets`

One record per important concrete asset behind a source.

Examples:

- API endpoint
- CSV download
- PDF archive
- RSS feed
- GitHub repo
- state roster page

This is the access layer.

### 7.3 `source_runs`

One record per attempted acquisition or refresh.

Examples:

- when fetched
- what method used
- whether it succeeded
- how many records came back
- what it cost

This is the operational history layer.

### 7.4 `source_relationships`

Optional later layer for relationships such as:

- source supersedes source
- source cites source
- source mirrors source
- source belongs to organization
- source feeds page

This becomes valuable once the registry grows beyond simple filtering.

### 7.5 `page_feeds`

A derived mapping between sources and public pages.

Examples:

- source eligible for law watch
- source eligible for Flyway
- source eligible for species pages
- source eligible for source explorer only

This is the product-routing layer.

## 8. The registry schema

Each source should get one normalized record before any deep ingestion work
happens.

### 8.1 Identity block

- `source_id`
- `name`
- `organization`
- `canonical_url`
- `source_class`
- `source_family`
- `subtype`
- `description_short`

### 8.2 Scope block

- `geography_scope`
- `jurisdictions`
- `taxa_scope`
- `species_specific`
- `audience`
- `coverage_notes`

### 8.3 Access block

- `access_method`
- `format`
- `auth_required`
- `credential_hint`
- `api_docs_url`
- `bulk_url`
- `rss_url`
- `scrape_entry_url`

### 8.4 License and risk block

- `license_summary`
- `license_type`
- `license_allows_storage`
- `license_allows_public_display`
- `license_allows_ai_analysis`
- `attribution_required`
- `public_safety_notes`
- `tos_risk`
- `license_risk`

### 8.5 Operational block

- `update_cadence`
- `freshness_class`
- `stability_score`
- `authority_score`
- `structure_score`
- `join_value_score`
- `analysis_value_score`
- `estimated_maintenance_level`

### 8.6 Product-decision block

- `wildlifestats_use_case`
- `ingest_tier`
- `intended_use`
- `page_targets`
- `priority`
- `status`
- `notes`

### 8.7 Provenance block

- `discovered_from`
- `discovered_date`
- `seed_file`
- `review_status`
- `reviewer`

## 9. Controlled vocabularies

The registry will become messy quickly unless the main axes are controlled.

### `source_class`

- `official_data`
- `research_data`
- `literature`
- `organization_site`
- `news`
- `social`
- `repository`
- `law_policy`
- `tool_platform`
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
- `news_feed`
- `social_monitor`
- `developer_resource`

### `access_method`

- `public_api`
- `authenticated_api`
- `bulk_download`
- `rss_feed`
- `arcgis_open_data`
- `github_api`
- `manual_export`
- `html_scrape`
- `partner_request`
- `email_request`

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

- `seeded`
- `reviewed`
- `operational`
- `parked`
- `blocked`

## 10. Scoring model

The registry should not only describe sources. It should score them.

Recommended 1-5 scale for these fields:

- `authority_score`
- `structure_score`
- `freshness_score`
- `join_value_score`
- `analysis_value_score`
- `legal_clarity_score`
- `maintenance_burden_score`

Simple prioritization logic:

- **High-priority operational candidates**
  authority 4-5, structure 4-5, legal clarity 4-5, join value 4-5

- **Good directory/reference candidates**
  authority 3-5, structure 1-3, analysis value 1-3, legal clarity 3-5

- **Park or delay**
  legal clarity 1-2, maintenance burden 4-5, join value 1-2

This keeps "interesting" from outranking "useful."

## 11. Ingest rule: what to store vs what to leave external

This is the most important practical filter.

### `pull_core`

Store locally when all or most are true:

- structured and machine-readable
- public or clearly licensed for reuse
- high-value for repeated querying
- useful as a join spine across many pages
- likely to be queried frequently

Examples:

- source metadata registry records
- species and taxonomy join tables
- public center directory records
- legal/regulatory metadata
- public observation metadata
- normalized repo metadata
- public disease-event metadata

### `pull_periodic`

Store only normalized metadata or selected fields when:

- the source is useful but dynamic, large, or legally delicate
- raw text or media storage adds risk but limited value

Examples:

- social posts: organization, platform, URL, date, extracted tags, engagement,
  short summary
- news: title, outlet, date, URL, entities, summary, topic labels
- papers: citation, abstract, keywords, links, not the full PDF corpus by
  default

### `directory_only`

Keep discovery metadata and link out when:

- the source is useful to know about
- ingestion is not needed for the product
- a user is better served by going to the source

Examples:

- niche university lab pages
- conference pages
- software platforms
- many partner directories

### `manual_on_demand`

Do not maintain recurring pulls, but preserve enough metadata to fetch when
needed.

Examples:

- by-request datasets
- special research collections
- large bulk archives that only matter for specific projects

### `do_not_ingest`

List it only if it matters strategically, but do not harvest it until a later
explicit decision changes the posture.

Examples:

- partner-gated operational systems
- expensive commercial APIs
- systems with unclear use rights
- operational platforms whose data would create privacy risk

## 12. Decision tree for new sources

Every newly proposed source should pass through this order:

1. Is it authoritative, widely used, or uniquely valuable?
2. Is there a structured API, bulk export, or official metadata page?
3. Are storage and public display rights clear?
4. Does the source support a real WildlifeStats page or join?
5. Is the maintenance burden reasonable?
6. Is this best handled as `pull_core`, `pull_periodic`, `directory_only`,
   `manual_on_demand`, or `do_not_ingest`?

If a source fails step 4, it should probably not be acquired yet.

## 13. Existing credentials that materially help this project

The credentials README confirms these existing service files that matter
immediately to WildlifeStats planning:

| Credential file | Why it matters here | Best use in this initiative |
|---|---|---|
| `apify.env` | Social and website extraction automation | Rehab-center social monitoring, site metadata collection, targeted source discovery |
| `ebird.env` | Official bird data access | Species pages, migration signals, bird-specific observation overlays |
| `exa.env` | Targeted semantic search | Canonical-source discovery, finding the real API/docs/archive page |
| `github.env` | GitHub API access | Repository discovery, metadata pulls, topic graphs, repo health metrics |
| `openai.env` | LLM extraction and summarization | Controlled metadata extraction, entity tagging, source classification |
| `perplexity.env` | Research acceleration | On-demand source validation and planning support |
| `supabase.env` | Storage and query layer | Registry tables, joins, filters, analysis, derived views |
| `zenodo.env` | Publication and archiving | Snapshot releases, citable source directories, public datasets |
| `anthropic.env` | Secondary LLM path | Structured extraction, validation, comparison workflows |
| `cloudflare.env` / `netlify.env` | Deployment infrastructure | Publish registry pages, dashboards, APIs, static outputs |

These do **not** mean every source should be ingested. They mean the mechanics
for a clean first phase are already largely in hand.

## 14. Recommended first-wave source families

These are the right first-wave buckets because they create the strongest public
value with the least chaos.

### Bucket 1 - Species, taxonomy, and occurrence

- GBIF
- eBird
- iNaturalist
- NatureServe
- USFWS ECOS
- state wildlife portals

Reason:

This becomes the join spine for species pages, trend pages, help pages, and
source filters.

### Bucket 2 - Rehab and center ecosystem

- existing WildlifeStats rehab-center directory
- center websites
- WILD-ONe public/request information
- WRMD metadata only
- state rehabber and permitting sources

Reason:

This underpins center profiles, service matrices, Wildlife911 routing, and
sector analysis.

### Bucket 3 - Law and regulation

- Federal Register API
- Regulations.gov API
- Congress.gov API
- Open States API
- selected state wildlife-advocacy trackers as secondary overlays

Reason:

This is the cleanest way to build a credible wildlife-law watch page without
manually surfing 50 state sites every week.

### Bucket 4 - Disease, surveillance, and wildlife health

- USGS NWHC / WHISPers
- APHIS NWRC
- FWS and state disease bulletins
- literature and standards around wildlife disease data

Reason:

This supports disease watch, mortality events, and future research surfaces.

### Bucket 5 - Literature and method sources

- Biodiversity Heritage Library
- EDI
- Crossref
- PubMed
- authoritative-source YAMLs already in repo

Reason:

This is the core of a serious source/citation product and research mode.

### Bucket 6 - Repositories and technical tools

- GitHub topics and repo metadata
- open conservation and biodiversity repos
- APIs and developer docs

Reason:

This is the right way to build a wildlife-tech directory without conflating code
with datasets.

## 15. Current source examples by ingest tier

### Pull core now

- GBIF occurrence and species metadata
- ECOS species and status metadata
- rehab-center public profile metadata
- state-vet-ag and USFWS office registries already in repo
- Open States bill metadata
- Federal Register metadata
- Regulations.gov docket and document metadata
- GitHub repository metadata

### Pull periodic now

- wildlife rehab social posts as extracted metadata only
- wildlife news stories as metadata + summary only
- paper abstracts and citation metadata
- Wildlife Insights public metadata
- Movebank public-study metadata

### Directory only now

- vendor and tool platforms
- conference and training pages
- niche project pages without structured access
- access-by-request datasets without immediate page use

### Manual on demand now

- large PDF archives
- special state rosters requiring ad hoc extraction
- partner or nonprofit datasets available only by request

### Do not ingest now

- Species360 operational data
- WILD-ONe operational records
- WRMD patient or operational content
- commercial detection APIs beyond exploratory testing
- anything that would pull private operational records into public lanes

## 16. How this maps to the Phase 9 bucket framework

The registry and the Phase 9 buckets are complementary.

| Registry concern | Phase 9 bucket most affected |
|---|---|
| social and public post sources | Bucket 01 SOCIAL |
| firm sites, annual reports, 990s | Bucket 02 FIRM PROFILE |
| publications and PDFs | Bucket 03 PUBLICATIONS |
| species/help pages and routing content | Bucket 04 HELP-WILDLIFE CONTENT |
| secure partner micro-data | Bucket 05 RAW RECORDS |
| public derived dashboards | Bucket 06 AGGREGATE |
| licensing and state rosters | Bucket 07 REGULATORY |
| media and literature monitoring | Bucket 08 MEDIA / ACADEMIC |
| relationship graphing | Bucket 09 NETWORK |
| training and events | Bucket 10 EVENTS |

This means the registry should not be designed in a vacuum. It should carry
enough metadata to tell the later Phase 9 pipelines where a source belongs.

## 17. Public page plan: what to build first

You mentioned 4-6 wildlife-specific pages. The right first set is:

### Page 1 - Source Explorer

The public-facing searchable source registry:

- filter by topic, source type, geography, taxa, audience, data format, access
  method
- distinguish official data from commentary, news, and tools

This should be built first because it becomes the organizing layer for
everything else.

### Page 2 - Wildlife Law Watch

Track:

- federal rules
- proposed rules
- notices
- comment periods
- key state wildlife bills

Primary data sources:

- Federal Register API
- Regulations.gov API
- Congress.gov API
- Open States API

Secondary editorial overlays:

- nonprofit trackers
- advocacy summaries

### Page 3 - Rehab Social Monitor

Track public posts from wildlife rehab and hospital organizations.

Store:

- organization
- platform
- post URL
- timestamp
- media type
- species and topics detected
- event tags
- engagement
- short extracted summary

Do **not** default to storing raw post text or media locally.

### Page 4 - Wildlife News Digest

Rank and cluster the best stories of the week.

Primary acquisition:

- curated outlet lists
- topic search APIs
- public feeds and news discovery tools

Store:

- metadata
- summary
- topic cluster
- species and geography tags
- link out

### Page 5 - Species and Signal Pages

Species or topic pages that combine:

- occurrence and taxonomy
- law and protection status
- recent news
- center/help links
- public literature

### Page 6 - Research and Methods Hub

A more serious page for:

- standards
- methodology docs
- literature collections
- APIs and public datasets

This is where WildlifeStats can serve PhD users without making the main public
experience feel academic and cold.

## 18. The practical discovery strategy

Do not use one discovery method. Use four.

### Method A - API and portal harvesting

Best for:

- official datasets
- legislative feeds
- repo metadata
- structured biodiversity systems

This should dominate phase 1.

### Method B - Targeted semantic search

Use Exa and curated search prompts to find:

- canonical docs pages
- API references
- dataset landing pages
- state wildlife portals
- official trackers

This is better than brute-force scraping search results.

### Method C - Controlled site crawling

Use Apify or custom crawlers only for:

- specific organizations
- specific recurring pages
- structured lists with no usable API
- social monitoring where the platform pattern is already known

This should be targeted, not open-ended.

### Method D - Human-curated seed lists

Seed the registry from:

- sources already named in repo research docs
- Mike's pasted source lists
- existing WildlifeStats center registry
- GitHub topic lists
- known federal and state agencies

This is the fastest way to make the first version useful.

## 19. Quality gates before a source becomes operational

Before a seeded source becomes `operational`, require:

1. canonical URL confirmed
2. access method confirmed
3. licensing posture recorded
4. intended use assigned
5. ingest tier assigned
6. at least one page or pipeline use case named
7. failure mode documented

That keeps the registry from accumulating half-researched entries that look
finished but are not.

## 20. A three-stage execution plan

### Stage 1 - Build the control tower

Objective:

Create the master source registry before acquiring deep content.

Tasks:

1. define the canonical schema
2. seed from repo material already on disk
3. assign each source an ingest tier
4. assign each source an intended use
5. mark which sources are already reachable with owned credentials

Success condition:

You can search and filter sources even before the downstream content products
are mature.

### Stage 2 - Build three pilot acquisition flows

Objective:

Prove the model with a small number of high-value verticals.

Recommended pilots:

1. law and regulation
2. rehab social monitoring
3. species, taxonomy, and occurrence

Success condition:

WildlifeStats can show that it knows how to discover, normalize, and publish
across three very different source types.

### Stage 3 - Build public pages from normalized outputs

Objective:

Only after the acquisition logic is stable, build the polished public pages.

Success condition:

The pages feel coherent because they share one registry and one vocabulary,
instead of each being a one-off scrape project.

## 21. Practical seeding order for the first real work session

The first real registry build should **not** start from the whole internet. It
should start from the current repo and the already-audited BRWC planning files.

Recommended seed order:

1. `docs/research/data-sources/01-federal-state.md`
2. `docs/research/data-sources/03-citizen-science.md`
3. `docs/research/data-sources/04-rehab-onehealth.md`
4. `docs/research/data-sources/05-apis-scrapers-literature.md`
5. `wildlifestats/_pipeline/sources/rehab-centers/centers.yaml`
6. `wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml`
7. `wildlifestats/_pipeline/sources/statewide-associations/associations.yaml`
8. `wildlifestats/_pipeline/sources/sector-funders/funders.yaml`
9. `wildlifestats/_pipeline/sources/usfws-offices/offices.yaml`
10. BRWC `_data/external/source-registry.json` and the external-source tool
    matrix for attribution and license-pattern reuse

That order gives the registry a strong spine before any new web work begins.

## 22. What not to do

1. Do not scrape everything because you can.
2. Do not store full raw content unless there is a clear research or product
   reason.
3. Do not let social and news ingestion define the whole system. They are only
   two buckets.
4. Do not make the master database a giant blob of unscored links.
5. Do not start with 50 states of wildlife law by hand. Use APIs and start with
   the federal layer plus a limited state set.
6. Do not confuse commercial or vendor access with public publish rights.
7. Do not allow the registry to fork into multiple unofficial spreadsheets or
   JSON lists.

## 23. Immediate next step

The next bounded move should be:

**Create the canonical registry schema and first seeded registry file from
existing repo material only, with an API-leverage column based on the current
credentials inventory.**

That gives WildlifeStats a serious planning artifact and prevents the rest of
the work from dissolving into endless source collection.

## 24. Recommended first implementation slice

If this note becomes a real work slice, the first engineered deliverable should
be:

1. a canonical registry spec note
2. a normalized registry file under `wildlifestats/_pipeline/sources/`
3. controlled vocabularies for `source_class`, `source_family`,
   `access_method`, `ingest_tier`, and `intended_use`
4. a seeded first batch of sources drawn from:
   - the current repo research docs
   - Mike's June 15 source list
   - the credentials-backed services already available

That is the clean start.
