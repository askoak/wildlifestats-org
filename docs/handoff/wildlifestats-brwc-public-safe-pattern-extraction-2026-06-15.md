# WildStats support memo: BRWC public-safe pattern extraction

**Date:** 2026-06-15
**Author:** Codex
**Status:** Support memo only. This note does **not** redefine the WildStats
registry schema and does **not** modify app code.
**Purpose:** Extract reusable public-safe patterns from BRWC's external-source,
taxonomy-cache, iNaturalist, and public-corpus materials for use in
WildlifeStats planning and implementation.

## 1. Files reviewed

BRWC files reviewed for this memo:

- `_data/external/README.md`
- `_data/external/source-registry.json`
- `_data/ebird/README.md`
- `_planning/decisions/2026-06-15-external-data-sources-tool-matrix.md`
- `_planning/specs/2026-06-14-inaturalist-integration-spec.md`
- `_corpus_public/README.md`

This memo is a pattern extraction, not a new architecture. It should be read as
an input to the existing WildStats planning notes and the future master source
registry build.

## 2. Main conclusion

BRWC already solved five classes of problem that WildStats should reuse:

1. source attribution shape
2. reference-cache and refresh posture
3. source-by-surface license reasoning
4. public-safe corpus discipline
5. taxon-keyed enrichment architecture

WildStats should reuse those **patterns**, but bind them to its own public and
national data spine rather than BRWC's operational data.

## 3. Reusable schema patterns

These are the most useful reusable schema patterns visible in BRWC.

### 3.1 Source attribution record

`BRWC:_data/external/source-registry.json` uses a lean but useful source record
shape:

- `display_name`
- `link_url`
- `badge_label`
- `license_note`
- `requires_revenue_generation_permission`

WildStats should keep its richer registry model, but every operational source
should still have an attribution helper shape equivalent to:

- display name
- canonical link
- badge text
- short license note
- public-display risk flag
- fundraising or revenue-adjacency risk flag

That attribution shape should be centrally rendered, not re-authored in every
surface.

### 3.2 Cached reference-table pattern

Both GBIF and eBird in BRWC are treated as **cached reference sources**, not
live front-end dependencies.

Reusable structure:

- canonical table name
- lookup helper
- info or health helper
- refresh endpoint or script
- refresh cadence
- fallback manual refresh path

WildStats should adopt the same pattern for:

- taxonomy tables
- selected status or species lookup tables
- stable crosswalk tables

### 3.3 Taxon-keyed enrichment pattern

The iNaturalist spec is the strongest reusable data-model pattern.

Key architecture decisions worth lifting:

- use `taxon_id` as the stable join spine
- separate build-time enrichment from live runtime queries
- write one derived artifact with taxonomy, occurrence, conservation, and
  phenology fields
- store per-record license and attribution metadata on surfaced photos or
  observations

WildStats should reuse that pattern for national species and signal products.

### 3.4 Public-corpus build pattern

`_corpus_public/README.md` makes the right design call:

- build a public corpus from explicitly public-safe sources
- do **not** filter a broader staff corpus at runtime

That is directly portable to WildStats for any future public retrieval or public
AI layer.

## 4. Attribution rules to carry into WildStats

BRWC's docs imply a simple but strong attribution policy that WildStats should
adopt consistently.

### 4.1 One attribution helper, not many ad hoc strings

BRWC's source-registry and tool-matrix logic both point to the same answer:

- attribution should be centralized
- the surface should not decide attribution wording ad hoc

WildStats should have one attribution helper for public surfaces so the same
source always renders the same attribution language.

### 4.2 Attribution should be source-type aware

Examples pulled from BRWC:

- GBIF: "Data via GBIF.org"
- eBird taxonomy: Cornell attribution wording
- iNaturalist: attribution plus license filtering
- NOAA and BBL: public-domain federal attribution
- VDWR: attribution plus mixed-dataset caution

WildStats should preserve that difference rather than flatten every source into
generic "Source:" links.

### 4.3 Attribution must follow the displayed derivative

BRWC's pattern is not just "cite the source somewhere." It is closer to:

- if the surface displays derived data from a source, the source must be visible
- if the surface displays a photo or observation, the attribution and license
  must travel with that artifact

WildStats should use the same rule on species pages, source cards, signal
dashboards, and any future educator outputs.

## 5. Cache and refresh patterns to carry over

BRWC's materials suggest a very usable operational pattern for WildStats.

### 5.1 API-first, cache-second, UI-never-direct

Common theme across GBIF, eBird, and iNaturalist planning:

- fetch from the source in a controlled job
- cache or derive normalized artifacts
- keep browser-side code away from direct source APIs when possible

WildStats should follow the same pattern for public data products.

### 5.2 Refresh cadence should be explicit per source family

Patterns visible in BRWC:

- eBird taxonomy: monthly
- GBIF backbone: quarterly
- weather-like covariates: daily
- observation or outbreak data: live or near-live with graceful failure

WildStats should encode cadence at the source level rather than treating all
sources as "refresh when someone remembers."

### 5.3 Manual refresh paths still matter

BRWC keeps both:

- automated production refresh
- manual shell fallback

WildStats should preserve this two-path approach for key source families. It is
good resilience and makes debugging easier.

### 5.4 Derived build artifacts should be deterministic

The iNaturalist spec is especially clear here:

- build from source inputs
- write a derived artifact
- let the site build offline from cached output
- refresh only when explicitly requested or on cadence

WildStats should carry over that deterministic-build posture for:

- species enrichment
- law and regulation snapshots
- structured public signal layers

## 6. Public-safe corpus rules to carry into WildStats

The BRWC public-corpus memo contains one of the most important rules in the
whole corpus:

**public-safe corpora should be built from default-public-safe sources, not from
staff-only corpora with filters layered on top.**

WildStats should adopt the same rule for any future:

- public AI assistant retrieval layer
- public source-card embeddings
- public educator corpus
- public Wildlife911 answer support

Additional BRWC rules worth carrying over:

- no private or third-party commenter text by default
- no IP-sensitive newsletters or proprietary prose without explicit review
- no case-level narratives if consent or privacy is unclear
- stricter audits for public corpora than for staff corpora

## 7. License traps BRWC already surfaced

These are the most important traps BRWC already identified. WildStats should not
relearn them the hard way.

### 7.1 eBird is not "public means free to use everywhere"

BRWC's matrix and README both flag Cornell's terms.

Implications for WildStats:

- taxonomy reference use is comparatively safe
- display uses need attribution
- anything public and sponsor or fundraising adjacent needs extra care
- do not assume non-profit status alone solves commercial-use questions

### 7.2 iNaturalist is not one license

BRWC treats iNaturalist as per-observation licensed.

Implications for WildStats:

- filter at the record level
- default to CC0 and CC-BY where possible
- treat CC-BY-NC as a separate decision path
- always carry attribution fields forward

### 7.3 GBIF is cleaner, but still not frictionless

GBIF is the easiest of the three, but BRWC still treats attribution as
mandatory and occurrence-level licensing as variable.

Implications for WildStats:

- GBIF is a strong default cross-taxa backbone
- attribution still needs to render
- occurrence-level provenance should not be discarded

### 7.4 Surface context matters, not just source context

BRWC's most useful legal insight is that the same source can be acceptable on
one surface and wrong on another.

Examples:

- acceptable in an internal evidence tool
- risky in a fundraising-adjacent storytelling tool
- useful in a terse routing card only under hard caps

WildStats should adopt the same source-by-surface reasoning for:

- public WREN
- source explorer
- law watch
- Flyway
- Wildlife911
- future educator outputs

### 7.5 "Helpful" can still be out of register

BRWC's matrix also shows a non-legal trap:

- some data may be factual but still wrong for the surface

Example:

- NOAA weather in a social-caption drafting tool

WildStats should keep asking both questions:

1. Is the source legally usable here?
2. Does this source belong on this surface at all?

## 8. What WildStats should adapt directly

These BRWC patterns are strong candidates for direct adaptation.

### 8.1 Attribution helper layer

Create a WildStats-owned helper that can render:

- source badge label
- canonical link
- short license note
- display-risk note if needed

This should likely sit beside the future registry outputs, not inside app-page
copy.

### 8.2 Source-policy fields in the master registry

Without redefining the existing WildStats planning schema, the BRWC materials
make a few registry-level fields especially valuable:

- attribution badge text
- license note
- public-display allowed
- AI-analysis allowed
- fundraising or revenue-adjacency sensitivity
- recommended refresh cadence
- recommended access posture: cached vs live vs derived

### 8.3 Cached taxonomy services

WildStats should strongly consider BRWC's pattern of:

- cached eBird taxonomy for birds
- cached GBIF backbone or equivalent for non-birds

This is especially relevant to:

- source explorer filters
- species pages
- Wildlife911 routing
- Flyway signal labeling

### 8.4 iNaturalist build-time enrichment

The BRWC iNaturalist memo is good enough to act as the basis for a WildStats
species-enrichment workstream later:

- build-time artifact
- national or region-scoped occurrence baselines
- taxon-keyed joins
- photo license capture
- no browser-side iNat calls by default

### 8.5 Public corpus audit discipline

If WildStats later builds any public retrieval layer, copy BRWC's explicit audit
mindset:

- public-safe flag on every output chunk
- stricter audit than the internal build
- no runtime trust in "probably public"

## 9. What must stay BRWC-only

These are the strongest red lines from the reviewed material.

- BRWC patient species scope choices used to trim GBIF scope
- BRWC patient cube as a source of occurrence or treatment truth
- Goose's live citation paths into BRWC corpus
- band-number lookup workflows tied to staff operations
- any direct use of BRWC's staff-only or quasi-staff-only corpus content
- any patient-story or responder-story material with consent ambiguity
- any public corpus that includes non-BRWC commenter text
- any WildStats assumption that BRWC's Virginia-only geographic logic is
  nationally reusable without redesign

In short:

- keep the policy, not the payload
- keep the architecture, not the private data

## 10. How this memo should inform WildStats next

This memo is most useful if it is applied narrowly.

### Immediate use

Use it while building:

- the master source registry
- attribution helper rules
- source scoring and ingest decisions

### Near-term use

Use it while planning:

- public WREN source cards
- species-page data bindings
- Wildlife911 routing cards
- Flyway public signal surfaces

### Later use

Use it when designing:

- any public retrieval layer
- any secure research layer that needs public-safe fallbacks

## 11. Bottom line

BRWC's reviewed files do not give WildStats a dataset to import.

They give WildStats a **policy and architecture starter kit**:

- how to describe a source
- how to attribute a source
- how to cache a source
- how to refresh a source
- how to filter a source by license and surface
- how to build a public-safe corpus without trusting runtime filters
- how to use taxon-keyed enrichment to connect species, signals, and help pages

That is exactly the kind of support material WildStats should inherit from BRWC.
