# WildStats Wave 1 public spine implementation sequence

**Date:** 2026-06-15
**Author:** Codex
**Status:** Ordered implementation-planning note
**Scope:** Public-spine implementation only. No Flyway code, no state-law layer,
no secure-tier work.

## 1. Purpose

This note turns the June 15 planning bundle into a clean first implementation
sequence for the safest public-spine sources:

- `wildstats_rehab_centers_registry`
- `wildstats_state_vet_ag_registry`
- `federal_register_api`
- `regulations_gov_api`

The goal is to let the next engineering session start moving without deciding
again what Wave 1 is.

## 2. Why these four come first

These four sources:

- are already named as the top low-risk operationalization targets
- power immediate public utility
- have the fewest license or ToS complications
- stay out of the other engineer's Flyway-heavy code lane

They also anchor the two clearest public surfaces:

- `wildlife911`
- `law_watch`

## 3. What Wave 1 is

Wave 1 is the minimum useful public spine that makes WildStats feel like a
working nonprofit research utility instead of only a planning corpus.

Wave 1 should produce:

1. a stable center-directory and state-contact backbone for `wildlife911`
2. a federal-first `law_watch` feed backed by normalized metadata
3. clean public-source attribution patterns
4. enough structure that later species, social, and sector layers can attach
   without redefining the spine

## 4. What Wave 1 is not

Wave 1 is not:

- Flyway public monitoring implementation
- social extraction work
- state bill tracking
- Congress bill tracking
- secure-tier research access
- 990 enrichment
- species-page enrichment

Those are later layers.

## 5. Inputs already committed

The next engineer should treat these as the planning baseline:

- `wildlifestats/_pipeline/sources/master-source-registry.yaml`
- `docs/handoff/wildlifestats-top10-source-operationalization-plan-2026-06-15.md`
- `docs/handoff/wildlifestats-law-watch-normalized-schema-2026-06-15.md`
- `docs/handoff/wildlifestats-rehab-social-signal-normalized-schema-2026-06-15.md`
- `docs/handoff/wildlifestats-law-watch-page-contract-2026-06-15.md`
- `docs/handoff/wildlifestats-rehab-social-monitor-page-contract-2026-06-15.md`
- `docs/handoff/wildlifestats-github-watch-protocol-2026-06-15.md`

## 6. Recommended sequence

## Step 1 — Stabilize the local public registries as render-ready source spines

Sources:

- `wildstats_rehab_centers_registry`
- `wildstats_state_vet_ag_registry`

Objective:

- make sure the public pages consume these registries cleanly and consistently
- use existing join keys, not ad hoc page-only identifiers

Expected outputs:

- center records keyed by `slug`
- state-vet contact records keyed by `jurisdiction`
- documented field subset for public page rendering

Why first:

- these are local and already public-safe
- they unlock `wildlife911` without any API dependency

Stop condition:

- if page rendering requires inventing new public data not present in the local
  registries, stop and document the gap rather than faking it

## Step 2 — Implement the federal Register normalization path

Source:

- `federal_register_api`

Objective:

- emit normalized `law_watch` records from Federal Register metadata only

Expected outputs:

- a first pull path that creates document-level normalized records
- required fields from the `law_watch` schema
- page-ready records for the card and filter contract

Why second:

- Federal Register is the cleanest single-source starting point for `law_watch`
- it gives the public page a credible backbone even before docket integration

Stop condition:

- if wildlife relevance filtering is too noisy to trust, emit `review_needed`
  internally and stop before public publish

## Step 3 — Add Regulations.gov as the comment and docket layer

Source:

- `regulations_gov_api`

Objective:

- enrich the federal law-watch feed with docket and comment-deadline metadata

Expected outputs:

- normalized `law_watch` records from docket or document metadata
- comment-open logic
- source-aware dedupe within Regulations.gov

Why third:

- the law-watch page becomes meaningfully useful only when users can see open
  comment windows and docket context

Stop condition:

- if authenticated access or response structure is not stable enough, hold this
  layer and ship Federal Register first rather than stalling the whole page

## Step 4 — Bind the normalized records to the page contracts

Surfaces:

- `wildlife911`
- `law_watch`

Objective:

- ensure the page surfaces consume only the fields defined in the public page
  contracts

Expected outputs:

- `wildlife911` using local directory and agency-contact source spines
- `law_watch` using normalized federal metadata records

Why fourth:

- it prevents implementation from drifting into hidden extra fields or silent
  source assumptions

Stop condition:

- if a page needs fields outside the committed schema and page contract, stop
  and document the needed extension first

## Step 5 — Verify public posture before any second-wave source is added

Objective:

- confirm the public spine is stable before adding noisier or more governed
  sources like Flyway, eBird, or iNaturalist

Checks:

- attribution renders correctly
- federal-only law-watch labels are clear
- `wildlife911` does not imply clinical advice
- no private or BRWC-only data assumptions leaked into the public lane

## 7. Suggested engineering breakdown

If one engineer is executing this wave, the cleanest order is:

1. local registries and page data plumbing
2. Federal Register normalization
3. Regulations.gov normalization
4. public page binding
5. QA and guardrail check

If multiple engineers are working safely in parallel:

- one engineer may own `wildlife911` public-spine binding from local registries
- one engineer may own federal `law_watch` normalization

They should not both own the same page surface or the same normalized record
contract.

## 8. Things not to touch in this wave

To avoid stepping on the other visible code lanes, do not bundle in:

- Flyway extraction or signal code
- Supabase social bucket work
- WREN secure-tier behavior
- 990 ingestion
- state bill tracking
- media or news clustering

## 9. Acceptance criteria

Wave 1 is done enough when:

1. `wildlife911` has a clean public data spine from committed local registries
2. `law_watch` can render a federal-first feed from normalized records
3. the public page contracts are satisfied without ad hoc fields
4. attribution is visible
5. later Wave 2 sources can attach without changing the core contracts

## 10. Best next step after Wave 1

Once Wave 1 is stable, the best next safe public layer is:

- `flyway_social_roster` plus the metadata-only `rehab_social_signal` path

That is the natural public-signal follow-on, but it should not be mixed into
this first implementation wave.
