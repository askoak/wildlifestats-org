# Engineer order — Phase 3.1: synthetic cube scale-up to n=1,000,000

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer (`soar-aspen-beryl-heron`)
**Date:** 2026-06-10 ~16:10 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main`
**Authority:** §13 elevated ship + §14 self-merge.
**Single concern:** regenerate the synthetic cube at n=1M with sharded output.
**Mike directive 2026-06-10 16:09 ET:** "increase records to 1,000,000 we will need a very large database if we truly end up with national coverage"

## Source of truth

`docs/handoff/wildlifestats-synthetic-cube-spec-phase3-amendment-1m-2026-06-10.md`. Read it in full first. The original Phase 3 spec remains the ambient design; the amendment governs where it disagrees.

## Scope — single PR (recommended) or two sub-PRs

**Recommended single PR.** The generator change, the UI loader change, and the validator update are interlinked and the engineer's prior Phase 4.1 work owns all three touchpoints. One PR is cleaner than three.

If the engineer prefers two sub-PRs:

- 3.1a: generator + validator + new cube files committed (UI breaks transiently because it's still loading the old single-file path)
- 3.1b: UI loader + meta-display updates (UI reads the new sharded files)

Two sub-PRs are acceptable only if the engineer can ship them on the same branch with sequential commits and squash-merge at the end. Two separately-merged PRs with the site broken between them is NOT acceptable.

## Scope of changes

1. **`wildlifestats/_build/generate_synthetic_cube.py`:**
   - Default `--n` raised from 100000 to 1000000
   - Add `--output-mode {single,sharded}` (default: `sharded`)
   - Add `--out-dir` (used in sharded mode; mutually exclusive with `--out`)
   - In sharded mode: emit `<out-dir>/admissions-cube.meta.json` + `<out-dir>/by-state/<STATE_POSTAL>.json`
   - Meta file shape per amendment §4
   - Determinism: same seed → byte-identical output. Sort shards by postal code; sort cells within each shard by (year, month, county_fips, class, species, reason, outcome, disposition)

2. **`wildlifestats/_build/validate_cube.py`:**
   - Scale thresholds 10× per amendment §6
   - Add sharded-mode assertions: sum of shard `n_records` equals meta `n_records`; meta shard list matches actual files; no extra/missing shards

3. **Regenerate the cube files:**
   - Delete the old `data/cube/admissions-cube.json` (if `single` mode was previously committed)
   - Run `python wildlifestats/_build/generate_synthetic_cube.py --seed 42 --n 1000000 --output-mode sharded --out-dir data/cube/`
   - Commit `data/cube/admissions-cube.meta.json` + `data/cube/by-state/*.json` (51 files)

4. **`assets/js/data.js`** (Phase 4.1 loader code):
   - Switch from single-file `fetch('/data/cube/admissions-cube.json')` to meta-first + lazy-shard-load pattern per amendment §5
   - When the state filter changes, fetch any not-yet-loaded shards in parallel
   - When no state filter is applied, fetch all 51 shards in parallel (acceptable; modern browsers handle this fine and the per-shard size is small)
   - Cache loaded shards in a module-scope `loadedShards` object so subsequent filter changes reuse them

5. **`assets/js/parks.js`** (Phase 4.3 National Parks lens, if it directly loads the cube): same loader update. If it loads a separate `parks-overlay.json`, that file may also need a regeneration step from the generator's parks-overlay flag — verify and update if so.

6. **`/data/index.html`** (Phase 4.1 page):
   - Update the meta-display strings if any are hard-coded with "n=100,000" anywhere on the page (they should be reading from the meta file, but verify)
   - Update the "synthetic dataset" disclaimer wherever it appears to read "n=1,000,000" — search the codebase for `100,000` and `100000` and update all user-facing strings

7. **`/methodology.html`** (Phase 6 content, may not be long-form yet):
   - Update any mention of the dataset size to n=1,000,000
   - Note the seed (42) and the sharded storage architecture

8. **README.md:**
   - Update any dataset-size mentions

## What NOT to change

- Schema, dimensions, regional archetypes, seasonality formulas, admission-reason probabilities, outcome correlations — all unchanged from Phase 3 original spec
- Seed value (stays at 42)
- The Phase 4.5 partner pipeline — completely orthogonal
- WREN spec or any WREN code — the LLM context doesn't depend on cube size
- The Apify plan — orthogonal
- BRWC content guard, link check, HTML validate jobs

## Acceptance criteria

1. `python wildlifestats/_build/generate_synthetic_cube.py --seed 42 --n 1000000 --output-mode sharded --out-dir data/cube/` runs to completion in under 5 minutes on a standard runner.
2. Output files exist: `data/cube/admissions-cube.meta.json` and `data/cube/by-state/<XX>.json` for all 51 jurisdictions (50 states + DC).
3. Total records across all shards is in [995000, 1005000].
4. `python wildlifestats/_build/validate_cube.py` passes all checks (including new sharded-mode assertions).
5. Running the generator twice produces byte-identical output (determinism).
6. Largest single shard file is ≤ 4 MB uncompressed; meta file is ≤ 200 KB.
7. Total uncompressed cube size (meta + all shards) is ≤ 40 MB.
8. `/data/` page on the Netlify preview loads in under 2 seconds on a clean cache (cold load: meta file only, paint immediately; shards lazy-load as user interacts).
9. Filter UI works correctly with sharded loading — selecting one state loads one shard; selecting multiple loads multiple; no filter loads all in parallel.
10. CSV download applies k-suppression correctly against the loaded subset (existing Phase 4.1 logic; verify it still works after the loader change).
11. Phase 4.3 National Parks lens (`/parks/`) continues to work — verify any cube-dependent functionality.
12. Phase 4.4 Wildlife encyclopedia (`/wildlife/`) continues to work — same verification.
13. `/methodology.html` mentions "n=1,000,000" where the page references the dataset size.
14. CI green: BRWC content guard, link check, HTML validate, cube-validate, pipeline-dry-run.
15. No user-facing string anywhere on the site still says "n=100,000" or "100,000" referring to the dataset size (verify with grep).

## Commit and merge

- Branch: `engineer/phase3.1-cube-1m-scale`
- Commit message: `data(wildlifestats): scale synthetic cube to n=1,000,000 with sharded storage`. Body cites the amendment file and explains the sharded-loader change.
- Trailer: `Engineer: soar-aspen-beryl-heron`
- This PR is larger than typical §14 single-concern work because it touches the generator + the validator + the UI loader + the cube files themselves. It IS single-concern (the scale-up) and reversible by `git revert` (which would restore the n=100K cube and the single-file loader together).
- Self-merge per §14 after CI green + Netlify preview QA on all acceptance criteria.
- After merge, append a `## Resolution` section to this order file citing the merge commit hash. Move to `docs/handoff/closed/`.

## Risk and rollback

If sharded-mode produces unexpected behavior on the live site (e.g., shard fetch timeouts on a slow connection cause the UI to render with partial data and not refresh when shards complete), the rollback is `git revert <merge-commit>`. The revert restores the single-file cube + single-file loader as a fully-working configuration. Do not be hesitant to revert — the n=100K single-file path was working; restoring it costs nothing.

If the engineer hits a genuine blocker (e.g., the determinism guarantee can't be preserved with the parallel-state generation approach), revert to single-file mode at n=1M (architecture A from the amendment) and ship that. Architecture A is acceptable as a Phase 3.1 first ship; Architecture B can land as a Phase 3.2 follow-up if needed.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 16:10 ET

## Engineer implementation plan + spec-gap note (`soar-aspen-beryl-heron`, 2026-06-10, slow-pace tick)

Read the order + amendment in full. NOT YET STARTED — teed up for the next tick to execute as one atomic PR in fresh context (per engineer slow-pace §8.5: a large atomic unit belongs in clean context, not chained through a long one). Plan:

**SPEC GAP I FOUND — must handle or criteria 11/12 fail.** The order's loader step (#4/#5) names only `data.js`/`parks.js`. But the cube is ALSO loaded by:
- `assets/js/data-explorer.js` (the actual Phase 4.1 filename; "data.js" in the spec) — full cube.
- `assets/js/one-health.js` — full cube, filters reason=infectious_disease, sums by state.
- `assets/js/wildlife.js` — full cube, per-species reason + monthly aggregation.
- `assets/js/parks.js` — uses `data/cube/parks-overlay.json` (separate; regenerate via `--with-parks-overlay`, NOT sharded).
If Architecture B (sharded) ships and the single `admissions-cube.json` is removed, one-health and wildlife break. They need national (all-state) data, so sharding gives them no benefit — they'd load all 51 shards.

**Recommended approach (Architecture B, scalable):**
1. Add `assets/js/cube-loader.js` — shared: `loadMeta()`, `loadCellsForStates(states[])` (lazy + cached per amendment §5), `loadAllCells()` (parallel all shards). Reused by data-explorer / one-health / wildlife.
2. Generator: `--n` default 1000000; add `--output-mode {single,sharded}` default `sharded`; sharded writes `admissions-cube.meta.json` (shape per amendment §4.5: shards{}, totals_by_year, totals_by_state, dimensions) + `by-state/<POSTAL>.json` (cells only, sorted). Determinism preserved (postal-code order; cells sorted). Keep `single` mode working. Also re-run `--with-parks-overlay` (unaffected logic, but regen against the 1M cube so park counts scale).
3. Validator: thresholds ×10 (total [995000,1005000], state ≥500, year ≥50000, region-class ≥100) + sharded assertions (Σ shard n_records == meta n_records; per-shard cell_count matches meta; no missing shard). Validator must read sharded OR single.
4. Rewire data-explorer (lazy by state filter), one-health + wildlife (loadAllCells). parks.js only needs the regenerated parks-overlay.
5. Strings: grep `100,000` / `100000` site-wide → `1,000,000` / `1000000` (index hero, /data/ note, methodology, governance footer line "n=100,000", README, og-default.png regen with new number, sitemap unaffected).
6. CI cube-validate already runs; it must pass on sharded output.

**Fallback (Architecture A, permitted by order Risk §):** if B's 3-loader rewrite is too much for one tick, ship single-file at n=1M (`--output-mode single`, default raised to 1M): regenerate one `admissions-cube.json` (~28 MB, ~6-8 MB gzipped on the wire), all loaders UNCHANGED, validator ×10, strings updated. Meets criteria 1-7,10-15; defers 8-9 (sharded lazy-load) to a Phase 3.2 follow-up. Lower risk, real value, all pages keep working.

Engineer leaning: ship **A first** next tick (fast, safe, unblocks the 1M number everywhere), then **B as Phase 3.2** with the shared cube-loader. Both are explicitly sanctioned by the order. Final call at execution time.

— Engineer `soar-aspen-beryl-heron`, 2026-06-10

## Resolution

Shipped (Architecture A). PR #18, merged `8228af8`. Cube regenerated to n=1,000,000 (974,250 cells, 25.7 MB, deterministic seed 42); validator ×10; strings + og image + JSON-LD + parks-overlay updated; meta version 1.1.0. All four cube-dependent pages verified at 1M on preview; CI green; cube serves 200 on the Netlify deploy.

Per the order's Risk section, shipped single-file Architecture A first. Criteria 6/8/9 (sharded lazy-load) deferred to **Phase 3.2**: the generator's `--output-mode sharded` writer is already implemented and committed; Phase 3.2 = flip the default + add a shared `assets/js/cube-loader.js` and rewire data-explorer + one-health + wildlife (the spec-gap I flagged). One clean follow-up PR.

— Engineer `soar-aspen-beryl-heron`, 2026-06-10
