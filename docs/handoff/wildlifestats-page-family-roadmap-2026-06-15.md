# WildStats page family roadmap

**Date:** 2026-06-15
**Author:** Codex
**Status:** Decision-ready product roadmap note using the current master source registry as source of truth

## Scope and rule

This note uses only the current canonical registry and the June 15 planning
notes:

- `wildlifestats/_pipeline/sources/master-source-registry.yaml`
- `docs/handoff/wildlifestats-master-source-registry-spec-2026-06-15.md`
- `docs/handoff/wildlifestats-brwc-alignment-work-plan-2026-06-15.md`
- `docs/handoff/wildlifestats-source-registry-and-api-leverage-plan-2026-06-15.md`
- `docs/handoff/wildlifestats-existing-corpus-sweep-2026-06-15.md`

This note does **not** redesign the registry and does **not** assume any source
family that is not already present there.

## Executive read

If the goal is a product roadmap rather than a research wishlist, the cleanest
split is:

- build now where the registry is already operational or API-clean
- delay pages that still need manual curation, editorial judgment, or tighter
  licensing controls

That leads to three "now" candidates:

- wildlife laws and proposed-change tracker
- grants and funders page
- wildlife rehab social monitor

And three "later" candidates:

- center directory enrichment page
- phenology or migration signals page
- wildlife news of the week

## 1. Wildlife rehab / wildlife hospital social monitor

- **Audience:** rehab operators, sector researchers, journalists, and public users who want a national view of what wildlife hospitals are posting right now.
- **User value:** a single surface for public-facing rehab-center signals without asking users to scan dozens of Facebook or Instagram pages themselves.
- **Exact source inputs:** `flyway_social_roster`, `wildstats_rehab_centers_registry`, and `flyway_phrase_search_discovery` for roster expansion only.
- **Stored locally vs linked out:** store normalized metadata only: organization slug, platform, post URL, timestamp, extracted species/topic/event tags, short summary, engagement metrics if captured, and provenance fields. Link out to the original post for full text and media. Do not store raw media or build a permanent raw-post archive for the public lane.
- **Freshness target:** current within 24-72 hours for active monitored pages.
- **Licensing or ToS risks:** highest risk is platform ToS and media rights. The safe posture is metadata-plus-link, not republishing raw post bodies or images. False-positive extraction risk is also real.
- **MVP dataset:** Tier A or top 25-50 organizations from `flyway_social_roster`, joined to org names and states from `wildstats_rehab_centers_registry`.
- **Update cadence:** daily or weekday pull for recent activity; monthly manual review of the monitored roster.
- **Automated now, later, or not at all:** `now`, but only as a metadata-first monitor.
- **Phase 9 dependencies:** Bucket `01 SOCIAL` is the hard dependency. Bucket `06 AGGREGATE` is optional later for sector rollups. Bucket `02 FIRM PROFILE` is optional later for richer org cards.

## 2. Wildlife laws and proposed-change tracker

- **Audience:** policy-aware nonprofits, boards, researchers, educators, and public users tracking regulatory change.
- **User value:** one place to watch federal notices, dockets, comment deadlines, and selected wildlife-relevant bills without pretending to be a legal service.
- **Exact source inputs:** `federal_register_api`, `regulations_gov_api`, `congress_gov_api`, `openstates_api`. `gdelt_doc` can be used later for context or press overlays, but not as the authoritative legal backbone.
- **Stored locally vs linked out:** store normalized metadata only: rule or bill title, agency or chamber, docket or bill ID, dates, comment deadlines, geography, topic tags, and canonical source URL. Link out to the full text and docket pages.
- **Freshness target:** daily for federal sources; state layer can lag modestly if needed.
- **Licensing or ToS risks:** low compared with other page families. Main risk is pretending media coverage or keyword matches are equivalent to formal legal status. Avoid legal advice language.
- **MVP dataset:** federal-only first. Start with Federal Register and Regulations.gov. Add Congress.gov once the federal notice flow is stable. Add Open States only after the schema is proven.
- **Update cadence:** daily automated pull plus weekly sanity review.
- **Automated now, later, or not at all:** `now`, with a federal-first MVP.
- **Phase 9 dependencies:** Bucket `07 REGULATORY` is the primary dependency. Bucket `06 AGGREGATE` can later support trend summaries by agency, state, or topic.

## 3. Wildlife news of the week

- **Audience:** general public, research-adjacent users, and sector readers who want a short weekly roundup.
- **User value:** a digest layer that translates the broader wildlife information stream into a manageable weekly read.
- **Exact source inputs:** `gdelt_doc` and `biorxiv_medrxiv`. That is the current registry-backed source set for the page. The registry does not yet contain a broader curated outlet list.
- **Stored locally vs linked out:** store article or preprint metadata, cluster ID, date, topic tags, and a short summary. Link out to original reporting and original preprint pages. Do not republish article text.
- **Freshness target:** weekly, not real-time.
- **Licensing or ToS risks:** copyright is the core risk. GDELT also has precision and dedupe noise. Preprints add another risk: they are not peer reviewed and should be labeled clearly.
- **MVP dataset:** a weekly digest of 10-15 items, with a human editorial pass before publication.
- **Update cadence:** one weekly run, not daily.
- **Automated now, later, or not at all:** `later`. The current registry is not strong enough yet for a fully automatic public news page without a lot of cleanup.
- **Phase 9 dependencies:** Bucket `08 MEDIA / ACADEMIC` is the main dependency. Bucket `06 AGGREGATE` could later support recurring topic clusters.

## 4. Phenology or migration signals page

- **Recommended page:** `Spring Migration Signals`
- **Audience:** naturalists, educators, rehab staff, and public users who want a seasonal signal surface rather than a static species encyclopedia.
- **User value:** a public-facing "what is happening now" page for migration and first-of-season patterns, grounded in public feeds rather than generic prose.
- **Exact source inputs:** `journey_north`, `flyway_social_roster`, `flyway_phrase_search_discovery`, `ebird_ebd`, `inaturalist`, `gbif`, and `usda_aphis_hpai_wild_birds` as a hazard overlay when relevant.
- **Stored locally vs linked out:** store derived signal records, first-seen dates, anomaly flags, geography, and source URLs. Link out to original Journey North pages, original observations where license allows, and original social posts. Do not republish raw social content.
- **Freshness target:** daily during active migration season, weekly outside the window.
- **Licensing or ToS risks:** this page combines the thorniest surface mix: social ToS, eBird license constraints, iNaturalist per-record license handling, and general false-positive risk in seasonal signal extraction.
- **MVP dataset:** keep it narrow. Start with two signal families only: hummingbird spring and monarch spring. Do not try to launch a full migration atlas on day one.
- **Update cadence:** daily in season, with explicit season windows.
- **Automated now, later, or not at all:** `later`. It should follow the rehab social monitor, not precede it, because it reuses the same Flyway capture logic but adds harder baseline and signal-quality work.
- **Phase 9 dependencies:** Bucket `01 SOCIAL` is the hard prerequisite for public signal capture. Bucket `06 AGGREGATE` becomes useful once the page wants trend baselines, anomaly thresholds, or regional rollups.

## 5. Grants / funders page

- **Audience:** rehab leaders, grant writers, researchers, and boards looking for the funding landscape around wildlife rehabilitation.
- **User value:** the fastest page in this set for answering "who funds this field, what do they fund, and where do I start?"
- **Exact source inputs:** `wildstats_sector_funders_registry` as the core source. Optional context joins later from `wildstats_statewide_associations_registry` and `wildstats_rehab_centers_registry`.
- **Stored locally vs linked out:** store the local curated funder directory as-is: name, type, approximate annual grants, focus areas, eligibility summary, deadline URL, and source references. Link out to the actual grant program pages.
- **Freshness target:** monthly for deadlines and quarterly for the broader profile.
- **Licensing or ToS risks:** low. The main risk is stale deadlines or stale eligibility language, not legal redistribution risk.
- **MVP dataset:** the existing 33-row curated funders registry.
- **Update cadence:** monthly link and deadline check; quarterly full review.
- **Automated now, later, or not at all:** `now`, but only as a render of the local curated registry, not a new scraping program.
- **Phase 9 dependencies:** no hard Phase 9 dependency for MVP. Later enrichment can draw on Bucket `02 FIRM PROFILE` and Bucket `09 NETWORK`.

## 6. Center directory enrichment page family

- **Audience:** wildlife finders, rehab operators, researchers, and partner organizations using the center directory as an actual working reference.
- **User value:** turns the current center directory from "who exists" into "who exists plus what public context we can verify."
- **Exact source inputs:** `wildstats_rehab_centers_registry`, `wildstats_state_vet_ag_registry`, `wildstats_statewide_associations_registry`, `wildstats_usfws_offices_registry`, `usfws_ecos`, `state_rehab_annual_reports`, and `state_wildlife_open_data_portals`.
- **Stored locally vs linked out:** store verified enrichment fields only: agency links, association context, public service tags already in the local registry, regional office context, and derived badges where the source is explicit. Link out to state reports, state agency pages, and other external references. Do not imply a license or permit is verified unless that came from an explicit public roster.
- **Freshness target:** quarterly is good enough for MVP.
- **Licensing or ToS risks:** main risk is not license, it is false authority. State sources are heterogeneous and some public rosters are incomplete or stale.
- **MVP dataset:** the current center registry plus joins to state-vet-ag, statewide associations, and USFWS offices. Do not block on 990 or partner data. The registry does not currently give this page a 990 source family to use as a hard dependency.
- **Update cadence:** quarterly manual review plus rolling corrections whenever the local YAML registries change.
- **Automated now, later, or not at all:** `later` for the full enrichment concept. A lightweight pass is possible now, but the meaningful version depends on more verified state-level roster work.
- **Phase 9 dependencies:** Buckets `02 FIRM PROFILE`, `04 HELP-WILDLIFE CONTENT`, and `07 REGULATORY` are the core dependencies. Bucket `06 AGGREGATE` can later support center comparison summaries.

## Bottom-line recommendations

- **Best "ship now" page families:** wildlife laws tracker, grants/funders, rehab social monitor.
- **Best "ship later" page families:** center directory enrichment, migration signals, wildlife news of the week.
- **Page not to overbuild early:** wildlife news. The current registry-backed source set is too thin for a fully automatic high-trust weekly page.
