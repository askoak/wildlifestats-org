# WildlifeStats GitHub watch protocol

**Date:** 2026-06-15
**Author:** Codex
**Status:** Active coordination note for architect review on GitHub
**Trigger:** Mike directive 2026-06-15 that a Perplexity Computer architect is
keeping watch on BRWC and WildlifeStats on GitHub and that documentation should
be detailed enough to expedite review, correction, and next-step planning.

## 1. Decision in one paragraph

For the current WildlifeStats workstream, the durable coordination channel is
the repo itself. If an architect is watching BRWC and WildlifeStats, the
fastest clean path is: review the committed notes and artifacts on GitHub,
respond through committed `docs/handoff/` files or scoped PR comments, and keep
all substantive cross-session guidance in versioned files rather than in Mike
relay chat. This preserves auditability, keeps lane boundaries visible, and
prevents the same work from being re-explained every session.

## 2. Protocol source

This note is not inventing a new operating pattern. It is the WildlifeStats
translation of the existing AIStandingOrders posture:

- architect and engineer coordination should happen through GitHub artifacts,
  not through Mike as a courier
- architect audit of engineer work belongs in a fresh architect session, not in
  the engineer's chat thread
- committed files are the durable memory layer
- BRWC and WildlifeStats may share conceptual lessons, but not private lane
  payloads

In practice, that means the architect watch lane should treat the latest
committed notes as the source of truth and only use chat for true Mike
decisions, not routine engineering feedback.

## 3. What the architect should read first for the current WildlifeStats slice

For the June 15 source-registry and planning slice, the recommended read order
is:

1. `docs/handoff/wildlifestats-brwc-alignment-work-plan-2026-06-15.md`
2. `docs/handoff/wildlifestats-existing-corpus-sweep-2026-06-15.md`
3. `docs/handoff/wildlifestats-source-registry-and-api-leverage-plan-2026-06-15.md`
4. `docs/handoff/wildlifestats-brwc-public-safe-pattern-extraction-2026-06-15.md`
5. `docs/handoff/wildlifestats-master-source-registry-spec-2026-06-15.md`
6. `wildlifestats/_pipeline/sources/master-source-registry.yaml`
7. `docs/handoff/wildlifestats-master-source-registry-gap-memo-2026-06-15.md`
8. `docs/handoff/wildlifestats-master-source-registry-operational-fields-note-2026-06-15.md`
9. `docs/handoff/wildlifestats-top10-source-operationalization-plan-2026-06-15.md`
10. `docs/handoff/wildlifestats-law-watch-normalized-schema-2026-06-15.md`
11. `docs/handoff/wildlifestats-rehab-social-signal-normalized-schema-2026-06-15.md`
12. `docs/handoff/wildlifestats-law-watch-page-contract-2026-06-15.md`
13. `docs/handoff/wildlifestats-rehab-social-monitor-page-contract-2026-06-15.md`
14. `docs/handoff/wildlifestats-wave1-public-spine-implementation-sequence-2026-06-15.md`
15. `docs/handoff/wildlifestats-law-watch-federal-field-mapping-2026-06-15.md`
16. `docs/handoff/wildlifestats-wave1-implementation-readiness-note-2026-06-15.md`
17. `docs/handoff/wildlifestats-page-family-roadmap-2026-06-15.md`
18. `docs/handoff/wildlifestats-page-family-build-sequence-2026-06-15.md`

That sequence moves from boundary rules, to corpus reality, to canonical
registry shape, to next-page planning.

## 4. What is locked in the current slice

These decisions should be treated as locked unless an architect writes a
specific superseding note:

1. WildlifeStats is the canonical public national destination; BRWC is a
   pattern library and operations proving ground, not a data donor by default.
2. `wildlifestats/_pipeline/sources/master-source-registry.yaml` is the single
   canonical source registry for this phase.
3. One record in the registry equals one source system, curated registry, feed,
   or platform, not one record per center, office, or endpoint variant.
4. The BRWC support memo is a pattern library only. It does not redefine the
   WildStats schema.
5. No UI build or pipeline implementation work is bundled into the registry
   slice.
6. Every seeded source record must carry `ingest_tier` and `intended_use`.

## 5. What is still open and appropriate for architect feedback

These are good targets for watch-lane review because they are materially useful
but not yet locked:

1. Whether the first public source helper should live inside `/wren/` or ship
   as a standalone `/sources/` surface.
2. The exact normalized schema for a `law_watch` record once federal-only
   implementation starts.
3. The exact normalized schema for a metadata-only `rehab_social_signal`
   record.
4. The operationalization order inside the top-priority registry sources.
5. Whether `source_cards` should become a formal page target or stay as a
   helper concept behind WREN and research surfaces.

## 6. How the architect should write back

To keep work moving and avoid ambiguous feedback, use the narrowest durable
artifact that fits the issue:

### WildStats-only review or correction

Use a committed note under `docs/handoff/` with a name like:

- `INBOX-architect-<topic>-YYYY-MM-DD.md`
- `wildlifestats-<topic>-review-note-YYYY-MM-DD.md`

Use this when the issue is local to WildlifeStats and does not require BRWC to
act.

### Cross-repo or lane-boundary issue

Use a committed note with a name like:

- `CROSS-LANE-<topic>-YYYY-MM-DD.md`

Use this when the issue touches BRWC boundary, shared protocol, or an
architectural lesson that belongs in both repos.

### Tactical diff-level note

A GitHub PR comment is fine for a narrow file-level correction, but if the note
contains standing guidance, lane-boundary reasoning, or a future-session
instruction, it should also exist as a committed file.

## 7. What good feedback looks like

To expedite work, review notes should be concrete enough that an engineer does
not have to reconstruct the objection. Good review notes should include:

- exact file paths
- exact `source_id` values if the issue is registry-specific
- the field or rule being challenged
- whether the issue is factual, policy, legal, or architectural
- the proposed correction or the bounded options
- whether the issue is blocking or non-blocking
- what must be updated if the feedback is accepted

Examples:

- "Change `iucn_red_list.license_type` from `custom_noncommercial` only if the
  current WildStats policy intends API metadata use beyond noncommercial public
  display."
- "Add `directory_locator` to the controlled `source_family` vocabulary if
  AnimalHelpNow remains in scope; otherwise remove it from seed candidates."
- "Keep `wrmd` at `do_not_ingest` and `secure_only`; any move out of that tier
  requires a separate secure-data policy note."

## 8. Current red lines for the watch lane

The architect should assume these are hard red lines unless Mike explicitly
changes them:

1. No BRWC patient data in WildlifeStats public work.
2. No BRWC raw corpus, raw social archive, staff notes, or internal comments in
   WildlifeStats public work.
3. No second unofficial registry file.
4. No schema fork created casually in a review note.
5. No assumption that a source is public-safe merely because it is visible on
   the open web.
6. No UI work mixed into this registry-governance slice.
7. No Mike-relay dependence for routine architect-engineer clarification.

## 9. Documentation standard for the next wave

For this repo, future planning or architect-review notes should try to include
the same sections when relevant:

- purpose
- status
- trigger
- authority chain or prerequisite files
- scope and non-scope
- decisions locked
- open questions
- stop conditions
- exact write-back expectations

That structure is what makes the GitHub watch lane useful instead of just
verbose.

## 10. Immediate next bounded work after this note

The next narrow WildlifeStats execution slices should now be:

1. implement or spec the Wave 1 public spine around:
   `wildstats_rehab_centers_registry`, `wildstats_state_vet_ag_registry`,
   `federal_register_api`, and `regulations_gov_api`
2. execute the first federal `law_watch` pull against the normalized record
   schema and page contract
3. execute the first roster-joined `rehab_social_signal` normalization path
   after the public spine is stable

The registry, top-10 shortlist, two normalized record schemas, and two page
contracts now exist, and the Wave 1 public-spine implementation sequence note
now gives the ordered starting path for those next steps.
