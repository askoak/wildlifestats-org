# WildStats Wave 1 implementation readiness note

**Date:** 2026-06-15  
**Author:** Codex  
**Status:** Pre-implementation audit for the Wave 1 public spine only  
**Scope:** `wildlife911` public-spine binding, federal-first `law_watch`
ingest + normalization, and page-contract-to-data-contract alignment. No app
code changes in this session.

## 1. Lane verdict

The Wave 1 lane looks **mostly unclaimed and safe to start**, with two
important cautions:

1. No visible local branch introduces unique in-flight changes to
   `wildlife911`, `law_watch`, `state-vet-ag`, or a dedicated law-watch module.
2. Some shared-core files sit on older common branch ancestry and should be
   treated as **high-collision files even if not actively being changed now**.

That means a next code session can safely start Wave 1 **if it stays inside a
new, narrow ownership lane and avoids canonical shared files unless strictly
necessary**.

## 2. Audit snapshot

- Current branch: `codex/wildstats-source-registry-roadmap-2026-06-15`
- Working tree: clean at audit time
- HEAD during audit: `739001a` `docs(wildlifestats): map federal law-watch fields`
- Visible local branches:
  - `codex/wildstats-source-registry-roadmap-2026-06-15`
  - `codex/9d02-firm-profile-pipeline`
  - `codex/flyway-4-5-i-3-inbox`
  - `codex/flyway-killswitch-e2e-test`
  - `main`

### Branch-overlap read

- `codex/flyway-4-5-i-3-inbox` and `codex/flyway-killswitch-e2e-test` stay in
  Flyway / CI territory and do not show Wave 1 file overlap.
- `codex/9d02-firm-profile-pipeline` is not a Wave 1 lane, but it shares older
  ancestry that already includes `master-source-registry.yaml` and
  `rehab-centers/render_directory.py`.
- No visible local branch shows unique in-flight work against
  `wildlifestats/_wren/wildlife911/` or any existing `law_watch` implementation
  path, because no dedicated `law_watch` implementation path exists yet.

## 3. Repo reality for Wave 1

The repo is not an app-router codebase for these surfaces. It is currently:

- static public pages at repo root
- Python renderers and data modules under `wildlifestats/`
- committed source registries under `wildlifestats/_pipeline/sources/`
- generated public `wildlife911/` HTML already on disk
- planning-complete `law_watch` docs, but **no committed `law_watch` code or
  public page route yet**

That matters for ownership:

- `wildlife911/*.html` is best treated as **generated output**
- the generator and its data inputs are the real ownership boundary
- `law_watch` should start in a new dedicated code lane, not by overloading the
  canonical source-registry subtree

## 4. Exact current files likely involved

## 4.1 `wildlife911` public-spine binding

These are the current files most likely to matter:

- `wildlifestats/_pipeline/sources/rehab-centers/centers.yaml`
- `wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml`
- `wildlifestats/_pipeline/sources/master-source-registry.yaml`
- `wildlifestats/_wren/wildlife911/scripts/render_static_va.py`
- `wildlifestats/_wren/wildlife911/states/VA/guides/wildlife_rescue_guides_va.yaml`
- `wildlifestats/_wren/wildlife911/states/VA/extracted/species_content.json`
- `wildlife911/index.html`
- `wildlife911/start/index.html`
- `wildlife911/state/index.html`
- `wildlife911/state/VA/index.html`
- `wildlife911/species/*/index.html`
- `assets/css/wildlife911.css`

## 4.2 Federal-first `law_watch` ingest + normalization

These are the current files that define the contract and source posture:

- `wildlifestats/_pipeline/sources/master-source-registry.yaml`
- `docs/handoff/wildlifestats-law-watch-normalized-schema-2026-06-15.md`
- `docs/handoff/wildlifestats-law-watch-page-contract-2026-06-15.md`
- `docs/handoff/wildlifestats-law-watch-federal-field-mapping-2026-06-15.md`
- `docs/handoff/wildlifestats-wave1-public-spine-implementation-sequence-2026-06-15.md`
- `docs/handoff/wildlifestats-top10-source-operationalization-plan-2026-06-15.md`

There is **no current committed law-watch module, no normalized output folder,
and no live public `law_watch` page file**.

## 4.3 Page-contract-to-data-contract alignment

These files are the current alignment anchors:

- `docs/handoff/wildlifestats-master-source-registry-spec-2026-06-15.md`
- `wildlifestats/_pipeline/sources/master-source-registry.yaml`
- `docs/handoff/wildlifestats-law-watch-normalized-schema-2026-06-15.md`
- `docs/handoff/wildlifestats-law-watch-page-contract-2026-06-15.md`
- `docs/handoff/wildlifestats-rehab-social-signal-normalized-schema-2026-06-15.md`
- `docs/handoff/wildlifestats-rehab-social-monitor-page-contract-2026-06-15.md`
- `docs/handoff/wildlifestats-wave1-public-spine-implementation-sequence-2026-06-15.md`

The `rehab_social_*` notes matter here mainly as boundary reminders for what
must stay out of Wave 1.

## 5. Likely output paths for a later code session

## 5.1 `wildlife911`

Current public output paths already exist:

- `wildlife911/index.html`
- `wildlife911/start/index.html`
- `wildlife911/state/index.html`
- `wildlife911/state/VA/index.html`
- `wildlife911/species/*/index.html`

The safest next derived-output expansion is likely:

- additional generated `wildlife911/state/<XX>/index.html` pages
- registry-backed contact blocks rendered through the existing
  `render_static_va.py` ownership path, not hand-edited HTML

## 5.2 `law_watch`

Because no implementation path exists yet, the safest likely output boundary is:

- new dedicated code under `wildlifestats/_pipeline/law_watch/`
- new normalized-record outputs kept **outside**
  `wildlifestats/_pipeline/sources/`
- future public page output only after normalized records satisfy the committed
  page contract

The important readiness point is structural, not filename-perfect:

- `sources/` is the canonical source-registry lane
- `law_watch` normalized records should not be jammed into that lane as a
  second unofficial registry

## 6. Safe files to edit first

For a later Wave 1 code session, the safest ownership order is:

1. **Create new `law_watch` implementation files**
   - safest because the module does not exist yet
   - keeps federal ingest and normalization isolated from shared renderers
2. **Edit `wildlifestats/_wren/wildlife911/scripts/render_static_va.py` only if
   the data binding truly needs the existing public renderer**
   - this is the correct source-of-truth layer for generated `wildlife911`
     pages
   - safer than hand-editing rendered HTML
3. **Touch `wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml` or
   `rehab-centers/centers.yaml` only for genuine source-data corrections**
   - not as a first implementation move
   - not for page-only convenience fields

## 7. Risky files to avoid or defer

These files are higher-risk and should not be the first edit targets:

- `wildlifestats/_pipeline/sources/master-source-registry.yaml`
  - canonical registry file
  - recent planning branch already centers on it
  - hard rule says do not create a schema fork or second registry
- `wildlifestats/_pipeline/sources/rehab-centers/render_directory.py`
  - shared renderer for `/centers/`
  - older common branch ancestry already includes changes here
  - not needed for the first federal `law_watch` lane
- `wildlife911/*.html`
  - generated public output
  - should not be hand-maintained if the renderer is the source of truth
- `wildlifestats/_wren/wildlife911/states/VA/guides/wildlife_rescue_guides_va.yaml`
  - editorial VA source-of-truth
  - not the right first file for public-spine binding work
- anything under `wildlifestats/_pipeline/flyway/`
  - explicitly out of scope
- secure-tier code or social-bucket code
  - explicitly out of scope

## 8. Safest file ownership boundaries

## 8.1 `wildlife911`

- Treat `centers.yaml` and `agencies.yaml` as canonical read-mostly source
  registries.
- Treat `render_static_va.py` as the ownership boundary for generated public
  `wildlife911` pages.
- Treat `wildlife911/*.html` as output artifacts, not primary implementation
  files.

## 8.2 `law_watch`

- Treat the three June 15 notes as the committed contract set:
  normalized schema, federal field mapping, and page contract.
- Start implementation in a new dedicated module boundary.
- Keep normalization, source fetch, and page-binding layers separate.
- Do not repurpose `master-source-registry.yaml` into a working dataset.

## 8.3 Cross-surface alignment

- The source registry owns source posture.
- The normalized schema owns record shape.
- The page contract owns public display fields and filters.
- If a page needs a field the schema does not expose, stop and document the
  gap before coding around it.

## 9. Recommended implementation order

If Mike opens the next exact code lane, the cleanest order is:

1. Create the new `law_watch` module boundary and implement Federal Register
   normalization first.
2. Validate that normalized Federal Register records satisfy the committed
   `law_watch` page contract without extra fields.
3. Add Regulations.gov as the second federal metadata layer.
4. Only then bind `wildlife911` state-contact rendering to the local registries
   through the existing renderer path.
5. Regenerate public outputs from renderer sources, not from manual HTML edits.

Why this order:

- `law_watch` is greenfield and low-collision
- `wildlife911` already has shipped output, so it deserves tighter discipline
- both tracks still remain inside the Wave 1 public-safe spine

## 10. Verification checkpoints

Before any future code session calls itself done, it should verify:

1. `git status` is clean except for the intended Wave 1 files.
2. No local branch introduces new unique edits to the exact files being opened.
3. `law_watch` normalized records map field-for-field to:
   - `wildlifestats-law-watch-normalized-schema-2026-06-15.md`
   - `wildlifestats-law-watch-federal-field-mapping-2026-06-15.md`
   - `wildlifestats-law-watch-page-contract-2026-06-15.md`
4. `wildlife911` uses committed local registries, not ad hoc page-local data.
5. Attribution and refresh posture remain inherited from
   `master-source-registry.yaml`, not restated inconsistently.
6. Generated `wildlife911` outputs are re-rendered from source, not patched by
   hand.
7. No BRWC-only, patient, secure-tier, or raw social payloads enter the public
   lane.

## 11. Stop conditions

Stop and write down the blocker if any of these happens:

1. `wildlife911` binding requires new public fields that do not exist in
   `centers.yaml` or `agencies.yaml`.
2. The next engineer needs to modify `master-source-registry.yaml` structure to
   make Wave 1 work.
3. A `law_watch` implementation needs fields outside the committed normalized
   schema or page contract.
4. Route naming or page behavior for `law_watch` becomes a UI debate rather
   than a data-contract step.
5. Another local branch starts touching the exact same Wave 1 implementation
   files.

## 12. Out of scope

Keep all of this out of the next Wave 1 code session:

- Flyway extraction
- social-monitor implementation
- secure-tier work
- WREN secure behavior
- 990 ingestion
- state bills
- Congress tracking
- media clustering
- BRWC internal corpus
- BRWC patient data
- raw post text or private payloads
- any second registry or schema fork

## 13. Bottom line

Wave 1 is ready for a narrow code session **if the engineer claims a fresh
`law_watch` module lane first and treats existing `wildlife911` HTML as
generated output, not hand-owned page code**.

The first files to edit in a future code session should therefore be new,
dedicated `law_watch` implementation files, with `render_static_va.py` as the
first existing file to touch only when the local-registry binding step is
actually reached.
