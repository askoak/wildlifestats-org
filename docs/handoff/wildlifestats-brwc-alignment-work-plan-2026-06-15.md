# WildlifeStats work plan: BRWC alignment, public-safe ports, and boundary rules

**Author:** Codex planning note
**Date:** 2026-06-15
**Status:** Expanded working plan for continued implementation in
`askoak/wildlifestats-org`
**Trigger:** Mike directive 2026-06-15: audit BRWC and WildlifeStats together,
identify what is shared, what is different, and what should move from BRWC into
WildlifeStats without pulling BRWC internal data, patient records, or staff-only
corpus into the public lane.

## 1. Decision in one paragraph

WildlifeStats is the canonical public national destination. BRWC is the proving
ground and operations lab. We should reuse BRWC's successful **surface
patterns, interaction models, public-safe workflows, and source-policy
decisions**, but not its private bindings. In practice: copy the shell, not the
memory; the workflow, not the patient database; the public UX, not the internal
corpus.

## 2. What this note now covers

This note is no longer just a boundary reminder. It is the working alignment
plan for:

- what WildlifeStats may learn from BRWC
- what WildlifeStats must never ingest from BRWC
- which BRWC-born tools are worth porting
- what each port should bind to in WildlifeStats
- what order the ports should happen in
- which workstreams can safely run in parallel
- what "done" means for each surface

## 3. Repo anchors and existing specs

This plan should be read alongside these repo-native anchors:

- `docs/handoff/wildlifestats-wren-architecture-spec-2026-06-10.md`
- `docs/handoff/wildlifestats-engineer-order-phase9-multi-source-framework-2026-06-11.md`
- `docs/handoff/wildlifestats-flyway-spec-2026-06-10.md`
- `docs/handoff/wildlifestats-secure-tier-national-research-spec-2026-06-10.md`
- `docs/handoff/wildlifestats-form990-ingestion-spec-2026-06-11.md`
- `docs/handoff/wildlifestats-source-registry-and-api-leverage-plan-2026-06-15.md`
- `docs/handoff/wildlifestats-existing-corpus-sweep-2026-06-15.md`

Those docs already establish:

- the public-vs-secure WREN split
- the Phase 9 bucket taxonomy
- the Flyway legal posture and signal model
- the secure-tier audience and access model
- the 990 ingestion path
- the source-registry-first acquisition strategy

This alignment plan sits above them and decides **which BRWC concepts should
feed which WildlifeStats surfaces**.

## 4. What changed from earlier lane discipline

Earlier WildlifeStats handoff documents were written under a stricter
lane-discipline assumption: WildlifeStats should not read BRWC source directly
and should rebuild from first principles. That rule was directionally right for
contamination control, but it is now too blunt for the current job.

**As of 2026-06-15, the updated rule is narrower and better:**

1. WildlifeStats may audit BRWC directly for product patterns, interaction
   design, public-safe tooling concepts, and architecture lessons.
2. WildlifeStats does **not** import BRWC internal data, patient records, staff
   voice corpus, private social corpus, or center-only operational workflows.
3. Any port from BRWC to WildlifeStats must be rebound to WildlifeStats
   public-clean sources, synthetic cubes, public aggregates, public literature,
   Wildlife911 routing content, or future partner-authorized secure data.
4. The public tier of WildlifeStats remains a national nonprofit/research
   product, not a re-skinned BRWC site.

This note does **not** repeal the existing BRWC contamination guardrails for
public site content. It clarifies that conceptual and structural reuse is
allowed; raw or identifying cross-lane data flow is not.

## 5. Current product reality

### WildlifeStats already has

- A public national frame: homepage, governance, methodology, ingestion notes,
  and a clearer nonprofit/research identity than BRWC.
- A synthetic data explorer under `/data/` and `data/cube/*`.
- A national rehab-center directory under `/centers/`.
- A public Wildlife911 route under `/wildlife911/`.
- Flyway source registries and extraction pipeline under
  `wildlifestats/_pipeline/flyway/`.
- A multi-source data framework already scaffolded in
  `wildlifestats/_pipeline/_common/` and the Phase 9 engineer order.

### BRWC already has

- A stronger tool layer: `WREN`, `Goose`, `J.E.F.F.`, `MAGpi`, `Mock`,
  `Bramble`, `WildSocial`, `Atlas`, and public `WildData`.
- A live AI worker stack and production-ish interaction patterns.
- Internal corpus + patient-record search over real BRWC data.
- Public education and donor storytelling patterns that are more mature than
  WildlifeStats's current UI shell.

### Shared ambition

Both properties want to:

- route wildlife finders toward the right help
- turn messy wildlife data into usable interfaces
- support educators and citizen scientists
- expose research and methodology transparently
- use AI as a navigation layer rather than a black box

## 6. Non-negotiable boundary rules

These rules govern every port decision:

1. **No BRWC patient data in WildlifeStats public tools.**
2. **No BRWC internal corpus in WildlifeStats public tools.**
3. **No BRWC social voice dataset in WildlifeStats public tools.**
4. **No BRWC staff workflow assumptions in public WildlifeStats UI.**
5. **WildlifeStats public answers must identify when data is synthetic,
   aggregate, or directory-derived.**
6. **Triage flows route to Wildlife911, public directories, and state/federal
   sources, not BRWC operational guidance.**
7. **If a feature needs micro-data or partner records, it belongs in the future
   WildlifeStats secure tier, not the public tier.**
8. **BRWC can appear as one organization in national directories and public
   aggregates, but its raw records remain BRWC-only.**
9. **License-restricted third-party data does not become public-safe merely
   because BRWC already uses it.**
10. **Every ported surface must declare its approved source classes before it
    ships.**

## 7. Surface contract: public vs secure

The easiest way to make bad alignment decisions is to stay vague about which
surface is public and which is secure. The contract below should be treated as
hard scope.

| Surface | Audience | Allowed inputs | Forbidden inputs | Output posture |
|---|---|---|---|---|
| Public `/wren/` | General public, volunteers, students, researchers exploring public data | Synthetic cube, methodology, governance, center directory, public source registry, Wildlife911 routing, public Flyway signals | BRWC corpus, BRWC patient records, partner micro-data | Plain answer, show the data, show the method |
| Public `/data/` and future `/sector/` | Public and research-adjacent users | Synthetic cube, 990 aggregates, public registries, public source metadata | BRWC private metrics, partner raw records | Transparent aggregate exploration |
| Public `/wildlife911/` | Finders and referrers | Center directory, public help content, service flags, public agency contacts | BRWC internal responder flows, clinical instructions | Routing, not medicine |
| Public source and citation layer | Researchers, educators, advanced public users | Authoritative-source YAML, public APIs, literature metadata, public agency pages | BRWC internal judgment masquerading as citation | Linked source cards, evidence-first |
| Public Flyway dashboard | Public and research tier | Extracted public-safe signal records, structured citizen-science feeds, methodology | Raw post text archive, reposted media | Signals and anomalies, not reposting |
| Secure `/secure/wren/` | Approved users only | Partner-authorized anonymized data, secure aggregates, public layers above | BRWC data unless BRWC separately becomes a WildlifeStats partner under a secure agreement | Same shell, deeper data |
| Secure research APIs | Approved researchers and partners | WildlifeStats secure bucket data, anonymized snapshots, audit-controlled downloads | Any data without agreement and lineage | Logged, DOI-aware, role-gated |

## 8. Port matrix: what moves, what does not

| BRWC tool or pattern | WildlifeStats disposition | What is worth carrying | What must not carry over | WildlifeStats target form | Approved binding | Earliest safe phase |
|---|---|---|---|---|---|---|
| `WREN` shell | Port and adapt first | Query UX, progressive disclosure, "show the data", "how computed", hub feel | BRWC prompt state, BRWC data assumptions, any BRWC-only code paths | Public `/wren/`, later `/secure/wren/` | Synthetic cube, methodology, centers, Wildlife911, public source cards | Phase 1 |
| `Goose` | Do not port as-is | Evidence-first answer style, explicit citations, refusal honesty | Corpus retrieval, patient search, staff context, private chunks | Fold best parts into public WREN and later secure WREN | WildlifeStats public/secure stores only | Phase 2 for style, never as direct port |
| `J.E.F.F.` | Port pattern early | Citation cards, source verification, linked outputs | BRWC educator prompt coupling, any Quill tone bleed | WREN source mode or standalone source finder | Authoritative YAML, Crossref, PubMed, public agencies | Phase 2 |
| `MAGpi` | Port pattern early | Lens-based exploration, honesty about sample size, saved views | BRWC-specific metrics, patient-cube assumptions | `/data/` uplift and later `/sector/` | Synthetic cube first, 990/public aggregates later | Phase 2-3 |
| `Mock` educator shell | Port later | Structured educator outputs, tone control, audience adaptation | BRWC lesson content, ambassador specifics, center voice | `/educators/` or WREN educator mode | Public species pages, source cards, center directory, Wildlife911 | Phase 4 |
| `Bramble` | Do not port publicly | Very little for public use beyond pattern lessons | Single-case viewer, patient timelines, case-history assumptions | Maybe secure partner record detail later | Partner-authorized secure records only | Secure-only, much later |
| `WildSocial` | Partial port only | Monitoring workflow, signal extraction posture, roster logic | Raw archive, engagement obsession, center voice bias | Flyway/public signal dashboard | Typed signals plus source URLs only | Phase 3 |
| `Atlas` / Wildlife Almanac | Pattern-only, selective | Story-led dashboard framing, org dossier feel | Donor/board narrative, BRWC institutional framing | Sector dashboards and enriched center profiles | 990, firm profile, regulatory, source registry | Phase 3-4 |
| Public `WildData` | Selective merge | Analytics affordances, public data framing | BRWC-specific content and copy | `/data/`, `/sector/`, `/centers/financials/` | WildlifeStats public datasets only | Phase 2-3 |
| BRWC `Wildlife911` deployment | Continue migration to WildlifeStats | Public routing concept, species triage framing | BRWC-only service assumptions, center-local routing | WildlifeStats becomes canonical public Wildlife911 home | Bucket 04 help content + center directory + state agencies | Phase 3 |

## 9. Code-reuse rule

This note permits **conceptual and structural reuse**, not careless copy-paste.

Default rule:

- reuse the idea
- reuse the interaction pattern
- reuse the data contract shape where it is generic
- rewrite the implementation in WildlifeStats terms

Direct code transplant is acceptable only when all of the following are true:

1. the code is generic
2. it has no BRWC-only bindings, secrets, prompt assumptions, or corpus
   expectations
3. rewriting it would add risk rather than reduce it
4. the resulting WildlifeStats version is still easier to audit than a fresh
   build

In practice, most ports here should be **adaptations or rewrites**, not lifts.

## 10. WildlifeStats-native bindings by surface

Every ported surface needs a clear source spine. This is the binding map.

### Public WREN

Primary bindings:

- `data/cube/*` synthetic cube
- methodology and governance pages
- `wildlifestats/_pipeline/sources/rehab-centers/centers.yaml`
- public Wildlife911 routing content
- future master source registry
- future public Flyway trigger outputs

### Source and citation helper

Primary bindings:

- `docs/research/authoritative-sources/*.yaml`
- `docs/research/data-sources/*.md`
- public APIs such as Crossref, PubMed, ECOS, GBIF, eBird where license and
  rate limits allow
- public agency links and literature metadata

### Data explorer / sector dashboards

Primary bindings:

- synthetic cube
- 990 aggregates
- firm profile outputs
- regulatory verification outputs
- source registry tags and filters

### Wildlife911 matrix

Primary bindings:

- center directory
- Bucket 04 help-wildlife content
- state-vet-ag and public agency contacts
- service flags and accepted-species routing

### Flyway

Primary bindings:

- public Page roster
- typed signal records only
- Journey North / eBird / iNaturalist anchor feeds
- methodology and audit trail

### Secure tier

Primary bindings:

- partner-authorized secure buckets only
- anonymized snapshots
- audit logs and role-based access rules

## 11. Recommended build order

The trap to avoid is trying to "bring over BRWC" in one sweep. The right
sequence is to harden the public national spine first, then attach the nicest
BRWC-born surfaces to that spine.

### Phase 1 - Lock the data spine and public hub

**Goal:** make the public/private boundary explicit and revive the core public
surface that later tools plug into.

Deliverables:

1. Master source registry spec and seeded registry
2. Public WREN shell aligned to the existing WREN architecture spec
3. Explicit per-surface source declarations
4. Updated methodology notes that say what is synthetic, public, and secure

Depends on:

- existing source research corpus
- current synthetic cube
- current center directory

Acceptance criteria:

- future PRs can point to one registry and one alignment note
- `/wren/` exists as the obvious product hub
- no public surface depends on BRWC internals

### Phase 2 - Add evidence and exploration layers

**Goal:** make WildlifeStats feel research-grade, not demo-grade.

Deliverables:

1. J.E.F.F.-style citation helper or source mode
2. MAGpi-style `/data/` uplift with saved lenses
3. clearer query-to-method affordances in WREN

Depends on:

- Phase 1 registry and WREN shell
- authoritative-source YAML
- public source APIs

Acceptance criteria:

- a user can ask for sources and get linked cards
- a user can explore data without guessing what is behind it
- synthetic/public labels remain visible at all times

### Phase 3 - Build the help and live-signal layers

**Goal:** turn WildlifeStats into something operationally useful to finders and
sector observers.

Deliverables:

1. Wildlife911 species-by-center routing matrix
2. Flyway public signal dashboard
3. center profile enrichments using firm profile, regulatory, and 990 outputs

Depends on:

- Phase 9 Bucket 02, 04, and 07 outputs
- Flyway signal records
- center directory

Acceptance criteria:

- a user can route by species and geography
- Flyway exposes signals, not scraped content
- center pages become meaningfully richer than a static directory row

### Phase 4 - Add educator and story-led sector surfaces

**Goal:** broaden the audience without diluting research rigor.

Deliverables:

1. educator mode or `/educators/`
2. selected Atlas-style story dashboards
3. grants/funders and sector landscape views

Depends on:

- stronger source registry
- species pages and signal data
- center and funder registries

Acceptance criteria:

- educator outputs are grounded in public facts, not free-form invention
- the sector story views remain evidence-first

### Phase 5 - Secure tier expansion

**Goal:** add national research access without muddying the public product.

Deliverables:

1. `/secure/wren/`
2. secure research APIs and downloads
3. partner data onboarding path

Depends on:

- secure-tier spec
- partner-authorized data
- Bucket 05 scaffolding and later actual agreements

Acceptance criteria:

- public and secure stay clearly separated
- secure value is real, not aspirational
- no secure requirement blocks public progress

## 12. Safe parallel workstreams

These streams can run in parallel **if they write to separate files or
surfaces** and one session owns final integration.

### Track A - Registry and source governance

Scope:

- master source registry spec
- seeded registry records
- source scoring and ingest classification

Why safe in parallel:

- mostly planning and normalized metadata work
- low collision with front-end shell work

### Track B - Public WREN shell and methodology affordances

Scope:

- `/wren/` shell
- show-data and show-method affordances
- public safety/refusal framing

Why safe in parallel:

- UI-first work
- can stub registry-backed features until Track A lands

### Track C - Citation helper / source mode

Scope:

- authoritative-source card layer
- external public-source adapters

Why safe in parallel:

- can use registry schema from Track A without touching WREN shell internals

### Track D - Data explorer uplift

Scope:

- `/data/` saved lenses
- synthetic/public labels
- sector dashboard scaffolding

Why safe in parallel:

- can bind to existing cube first

### Track E - Wildlife911 matrix and center enrichment

Scope:

- Bucket 04 help content
- service-flag joins
- center profile enrichment

Why safe in parallel:

- mostly data-model and directory work

### Track F - Flyway public surface

Scope:

- signal presentation
- methodology
- dashboard shell

Why safe in parallel:

- signal extraction already lives in its own lane

Unsafe parallel combinations:

- two sessions redefining the registry schema
- two sessions both owning `/wren/`
- one session changing public lane rules while another implements against old
  assumptions

## 13. Definition of done for alignment

Alignment is "done enough" only when these statements are true:

1. WildlifeStats has a public hub that does not feel like a placeholder.
2. At least one BRWC-born interaction pattern has been successfully adapted to
   WildlifeStats with fully public-safe bindings.
3. The source registry, center directory, Wildlife911 content, and data
   explorer point to one coherent public data spine.
4. Every public AI or quasi-AI surface can explain what it used and what it did
   not use.
5. No ported tool requires BRWC raw data to feel useful.
6. The secure tier is treated as an additive layer, not a hidden dependency.

## 14. First execution queue inside this repo

If we keep working in `wildlifestats-org`, the most rational next slices are:

1. **Master source registry**
   - normalize the existing research corpus and YAML registries into one source
     spine
   - classify what is ingestable vs reference-only

2. **Public WREN shell reactivation**
   - reconcile the existing WREN spec with current repo state
   - build or polish `/wren/` as the umbrella public tool surface

3. **Citation helper MVP**
   - turn the existing authoritative-source corpus into a public lookup surface
   - keep the initial version narrow and source-first

4. **Data explorer uplift**
   - improve `/data/` with MAGpi-style exploration patterns and saved lenses

5. **Wildlife911 species-routing matrix**
   - use Phase 9 bucket framing to feed Wildlife911 with actual center/species
     routing

These five steps all strengthen WildlifeStats on its own terms and also prepare
the clean data spine that later public-safe BRWC-inspired tools can attach to.

## 15. Things that are tempting but wrong

1. Port `Goose` directly and "just remove the patient stuff."
   - Wrong because Goose's value is tightly coupled to BRWC corpus and record
     search.

2. Mirror BRWC's staff hub in WildlifeStats before the public products are
   ready.
   - Wrong because WildlifeStats is not primarily a staff-ops site.

3. Import BRWC social corpora because they are already available.
   - Wrong because that would contaminate WildlifeStats with center-specific
     voice and content.

4. Build secure-tier researcher features first.
   - Wrong because the public national case is still the foundation and should
     be stronger before private tiers multiply complexity.

5. Treat license-sensitive sources as automatically OK because BRWC already has
   them in some form.
   - Wrong because display rights, donor adjacency, and public redistribution
     rules differ by surface.

## 16. Open questions, but none are blockers to the first slice

1. Whether the first public citation helper should live inside `/wren/` or ship
   as a standalone `/sources/` or `/research/` utility.
2. Whether `/data/` remains the main public analytics surface or whether a
   separate `/sector/` page should hold organization and 990 aggregates.
3. Whether educator mode should be its own route or a WREN mode with
   downloadable lesson artifacts.
4. Whether a formal `work-orders/` structure should be added to this repo later,
   since it still operates largely through `docs/handoff/` artifacts.
5. Whether BRWC should eventually become a secure-data partner to WildlifeStats.
   That is a separate governance decision, not an implementation default.

## 17. Recommendation for the next working session

If the next session is implementation, it should be narrowly scoped:

**Recommended next target:** build the master source registry and then bring
`/wren/` to life as the clean public hub in WildlifeStats, using BRWC only as a
UX and policy benchmark and keeping every data binding WildlifeStats-native.

That is the highest-leverage move because it creates the product surface that
later absorbs:

- J.E.F.F.-style citations
- MAGpi-style data exploration
- Wildlife911 routing
- Flyway signals
- and eventually secure-tier researcher access
