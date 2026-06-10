# Engineer order — Phase 3: synthetic cube generation + wiring

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer
**Date:** 2026-06-10 ~14:39 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Order #3 / Phase 2 merges)
**Authority:** §13 + §14.

## Source of truth

`docs/handoff/wildlifestats-synthetic-cube-spec-phase3-2026-06-10.md` — every spec for this PR.

## Scope

Single PR delivers:

1. `wildlifestats/_build/species-archetypes.json` — regional species probability tables per spec §4.
2. `wildlifestats/_build/state-region-map.json` — state-to-region map + per-county overrides for multi-region states.
3. `wildlifestats/_build/county-fips.json` — 2020 Census county FIPS snapshot (download once locally, commit the JSON; do not hit Census API at build time).
4. `wildlifestats/_build/generate_synthetic_cube.py` — generator per spec §9.
5. `wildlifestats/_build/validate_cube.py` — validation per spec §11.
6. `wildlifestats/_build/requirements.txt` — `numpy==1.26.4`.
7. `data/cube/admissions-cube.json` — generated output (committed).
8. `data/cube/admissions-cube.meta.json` — meta-only output (committed).
9. `.github/workflows/validate.yml` updated with `cube-validate` job (4th job, runs `validate_cube.py`).
10. `/data/index.html` updated to load `admissions-cube.meta.json` via fetch and display the meta info (record count, generation date, regions covered) — NO filtering UI yet (that is Phase 4).

## Determinism check

After generation, running the generator a second time with the same seed must produce a byte-identical JSON file (use stable key ordering, no timestamps in the cell data — only in the meta block, which is generated once and committed).

## Acceptance criteria

1. `python wildlifestats/_build/generate_synthetic_cube.py --seed 42` produces `data/cube/admissions-cube.json` with total n in [99500, 100500].
2. `python wildlifestats/_build/validate_cube.py` passes all checks in spec §11.
3. CI `cube-validate` job passes on the PR.
4. CI BRWC content guard passes (no contamination).
5. `/data/` page loads and displays the meta block (record count, generation date, "Synthetic data — see Methodology").
6. The cube JSON file is ≤ 8 MB uncompressed (size discipline — if larger, the generator should aggregate further before write).
7. Logo placeholder + Phase 2 styling are intact (don't regress).

## Out of scope

Filtering UI, choropleth map, CSV download — all Phase 4.

## Commit and merge

- Branch: `engineer/phase3-synthetic-cube`.
- Commit: `data(wildlifestats): generate synthetic n=100,000 admissions cube`. Body cites the spec.
- Trailer: `Engineer: <your-seat-sig>`.
- Self-merge per §14 once acceptance pass. Note: this PR is larger than typical §14 single-concern work, but it is single-purpose (the cube ships) and reversible by `git revert`. Architect ratifies in §13 mode.
- After merge, append `## Resolution`, move to `closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:39 ET
