# Phase 3 amendment — synthetic cube scale-up to n=1,000,000

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 16:10 ET
**Status:** Amendment to `wildlifestats-synthetic-cube-spec-phase3-2026-06-10.md`. Read alongside the original spec. Where this file disagrees with the original, this file governs.
**Mike directive 2026-06-10 16:09 ET:** "increase records to 1,000,000 we will need a very large database if we truly end up with national coverage"

## §1 — What changes

| Property | Original (Phase 3) | Amended (Phase 3.1) |
|---|---|---|
| Total record target | n = 100,000 ± 500 | **n = 1,000,000 ± 5,000** |
| Seed | 42 | 42 (unchanged — determinism preserved) |
| Cube file size cap | ≤ 8 MB uncompressed | ≤ 40 MB uncompressed full-cube, OR sharded |
| State minimum | ≥ 50 records | ≥ 500 records |
| Year minimum | ≥ 5,000 records | ≥ 50,000 records |
| (region, class) cell minimum | ≥ 10 records | ≥ 100 records |
| Per-cell jitter | ±5-10% | ±5-10% (unchanged) |
| Aggregation grain | year × month × county × species × reason × outcome × disposition | unchanged |
| K-suppression rule | n<10 collapses in download | unchanged |
| Public/secure split | unchanged | unchanged |

Everything else in the original Phase 3 spec — schema, dimensions, regional archetypes, seasonality, admission-reason distributions, outcome-disposition correlation, deterministic seed, generator script structure, validation tests — is preserved.

## §2 — Why this number

Mike's framing — "very large database if we truly end up with national coverage" — implies the synthetic baseline should be sized to be a credible representation of the real future state, not just an aesthetically large number.

- **2,200 active US wildlife rehabilitation organizations** (per WRMD's organizational count, see `docs/research/data-sources/04-rehab-onehealth.md`).
- **Median per-org annual case load ≈ 500-1,000 patients** (per published rehab-center annual reports across the long tail).
- **Active years per org ≈ 5-15** (variable; younger orgs have shorter histories).

A credible national real-data cube projects to ~5-15M records. **n = 1,000,000 is the next-checkpoint synthetic baseline**, not the final ceiling. The architecture amended here scales gracefully to 10-20M without further rework — only a re-run of the generator with a larger `--n`.

## §3 — File-size architecture (choose one)

The engineer picks one of two storage architectures at implementation time. Both meet the acceptance criteria. Architect prefers **B** for mobile load times but A is acceptable for the Phase 3.1 first ship if B adds more complexity than budget allows.

### §3.1 Architecture A — single file, larger

- Output: `data/cube/admissions-cube.json` (one file, ~25-40 MB uncompressed)
- Phase 4.1 filter UI (already shipped) loads the full cube on `/data/` page entry, filters in memory
- Risk: 25-40 MB JSON over a cold mobile connection is a 5-10 second first-paint penalty
- Mitigation: serve the cube with `Cache-Control: max-age=86400` + `Vary: Accept-Encoding` (Netlify auto-gzips JSON → ~5-8 MB transfer), and lazy-load only when the user lands on `/data/`

### §3.2 Architecture B — sharded by state (recommended)

- Outputs:
  - `data/cube/admissions-cube.meta.json` (~50 KB) — lightweight index: dimensions, total n per state, total n per year, generation metadata
  - `data/cube/by-state/<STATE_FIPS>.json` (51 files, each 200-800 KB) — one shard per state + DC
- Phase 4.1 filter UI behavior changes:
  - On `/data/` page entry, load only `admissions-cube.meta.json` (fast first paint)
  - When the user selects state filter(s), fetch only the shards for those states
  - When no state is selected, lazy-load shards in parallel as the user explores other dimensions
- Risk: requires changing the cube-loading logic in `assets/js/data.js` (Phase 4.1 deliverable)
- Mitigation: the cube-loading function gains a thin shard-loader. The rest of the filter logic is unchanged because all cells share the same schema regardless of which shard they came from
- Recommended because it scales to 10M+ records without further architectural change — adding scale just means more records per shard or splitting shards finer (e.g., state × year)

## §4 — Generator changes

`wildlifestats/_build/generate_synthetic_cube.py` gets the following modifications (single PR, single concern):

1. **CLI default for `--n` raised from 100000 to 1000000.** The flag itself already exists per Phase 3 spec §9; only the default changes. Pre-existing callers passing `--n 100000` continue to work.
2. **Output mode flag added: `--output-mode {single,sharded}`** (default: `sharded`). Selects between architecture A and B.
3. **Sharded output path:** when `--output-mode sharded`, the script writes `--out-dir data/cube/` containing `admissions-cube.meta.json` + `by-state/<STATE>.json` (51 files). When `--output-mode single`, it writes `--out data/cube/admissions-cube.json` (legacy behavior).
4. **State FIPS in shard filename:** use the 2-letter postal code (`AL.json`, `WY.json`, `DC.json`), not the numeric FIPS, because the UI filters on postal code already.
5. **Meta file shape (sharded mode):**

   ```json
   {
     "version": "1.1.0",
     "generated_at": "2026-06-10T20:10:00Z",
     "seed": 42,
     "n_records": 1000000,
     "license": "CC-BY-4.0",
     "description": "Synthetic wildlife rehabilitation admission records, n=1,000,000. Not derived from any real center's data.",
     "shards": {
       "AL": {"path": "by-state/AL.json", "n_records": 12450, "cell_count": 1820, "size_bytes": 256000},
       "AK": {"path": "by-state/AK.json", "n_records": 4200, "cell_count": 612, "size_bytes": 92000},
       "...": "..."
     },
     "dimensions": { ... same as before ... },
     "totals_by_year": {"2017": 95000, "2018": 97000, "...": "..."},
     "totals_by_state": {"AL": 12450, "AK": 4200, "...": "..."}
   }
   ```

   The shard files contain only the `cells` array for that state, no meta block (the meta lives once at the top level).

6. **Determinism preserved:** running `python generate_synthetic_cube.py --seed 42 --n 1000000 --output-mode sharded --out-dir data/cube/` twice produces byte-identical output. The shard files are written in deterministic state-postal-code order; cells within each shard are sorted by (year, month, county_fips, class, species, reason, outcome).

## §5 — UI changes (`assets/js/data.js`)

The Phase 4.1 filter UI loads the cube on page entry. After this amendment ships, it loads the meta file on page entry and shards on demand.

Pseudocode for the loader:

```javascript
// Old (Phase 4.1):
const cube = await fetch('/data/cube/admissions-cube.json').then(r => r.json());
filterAndRender(cube, filters);

// New (Phase 3.1, sharded mode):
const meta = await fetch('/data/cube/admissions-cube.meta.json').then(r => r.json());
let loadedShards = {};

async function getCells(stateFilter) {
  const wantedStates = stateFilter.length ? stateFilter : Object.keys(meta.shards);
  const newStates = wantedStates.filter(s => !loadedShards[s]);
  const fetched = await Promise.all(
    newStates.map(s =>
      fetch('/data/cube/' + meta.shards[s].path).then(r => r.json())
    )
  );
  newStates.forEach((s, i) => { loadedShards[s] = fetched[i]; });
  return wantedStates.flatMap(s => loadedShards[s].cells);
}

async function onFilterChange(filters) {
  const cells = await getCells(filters.states);
  filterAndRender(cells, filters);
}
```

For users with no state filter applied, the UI fetches all 51 shards in parallel — modern browsers handle 51 small JSON files fine. For state-filtered queries, it fetches only the relevant shards. Either way, the user is rendering filtered results within 1-2 seconds on broadband; the meta file alone paints in <100ms.

## §6 — Validation test updates

`wildlifestats/_build/validate_cube.py` thresholds (Phase 3 spec §11) update proportionally:

| Check | Original | Amended |
|---|---|---|
| Total n within | [99500, 100500] | **[995000, 1005000]** |
| Per-state minimum | ≥ 50 | **≥ 500** |
| Per-year minimum | ≥ 5,000 | **≥ 50,000** |
| (region, class) minimum | ≥ 10 | **≥ 100** |
| Probability sum check | 0.99 ≤ Σ ≤ 1.01 | unchanged |
| No NaN / no negative n / no unknown enum values | — | unchanged |

If the engineer ships sharded mode, the validator must also assert:

- Sum of `n_records` across all shards equals top-level `n_records` in meta
- Cell-count totals match between meta's `cell_count` per state and actual cell count per shard
- No state shard file is missing relative to meta's `shards` dictionary

## §7 — `/data/` page meta-display update

The page already shows the meta block per Phase 3 spec §11. After this amendment, the meta display reads:

```
Synthetic dataset · n = 1,000,000 records · generated 2026-06-10 · seed 42
```

(The Phase 4.1 implementation already drives this from `admissions-cube.meta.json`, so no rewrite is needed beyond pointing at the new meta file.)

## §8 — Out of scope

- The Phase 4.5 partner data pipeline is **unaffected**. Phase 4.5 ingests real partner records into a separate `secure/cube/partner-records.json`. The synthetic-cube scale change does not touch partner-cube logic.
- WREN (Phase 7) is **unaffected** at the LLM layer. The schema-context that goes into the system prompt depends on dimensions and value enumerations, not on counts. WREN's client-side query execution will use whichever shards the UI has loaded; the engineer wires WREN's `getCells()` calls through the same shard-loader as Phase 4.1.
- The CI BRWC content guard, link-check, html-validate, and pipeline-dry-run jobs are unaffected.
- The Apify social-media plan is unaffected.
- Public/secure cube separation per the Phase 4.5+ source registry is unaffected — the source registry's commercial-license routing operates per-cell-source, orthogonal to total record count.

## §9 — Storage and bandwidth note

At n=1M in sharded mode:

- **Disk in repo:** ~20-25 MB total across 51 shard files + meta. Acceptable for Git (large but not problematic; well under the 100MB GitHub file ceiling per file, and the largest single shard is ~800 KB).
- **Netlify bandwidth:** each `/data/` page view fetches the meta (~50 KB) and 0-51 shards depending on filter state. With `Cache-Control: max-age=86400` and Netlify's CDN, repeat visits cost the user near-zero bandwidth.
- **GitHub Actions CI artifact size:** the regenerated cube checks into the repo once per regeneration; CI clones the repo with the cube already present. No impact on CI cycle time beyond a ~2-second extra clone download.

## §10 — Future scale beyond 1M

When the real future state pushes the cube past 5-10M records (e.g., when real WRMD partner data starts flowing through Phase 4.5+):

- **No architecture change required if sharded mode shipped here.** Per-state shards can themselves be split (e.g., `by-state/CA-2024.json`, `by-state/CA-2023.json`) without changing the loader contract — the loader just sees a longer `shards` dictionary in the meta.
- If shard count exceeds ~500, switch the loader from "fetch all shards in parallel when no state filter" to "fetch only shards matching the current filter, with the UI prompting the user to narrow filters before loading the full dataset."
- The 40 MB total-uncompressed budget is the soft limit; past 100 MB total, consider migrating shards to a CDN-served bucket and dropping them from the Git repo (Phase 4.5+'s license-routing logic already supports this for secure-tier data).

## §11 — Acceptance criteria (handed to engineer order)

See `wildlifestats-engineer-order-phase3.1-cube-1m-scale-2026-06-10.md`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 16:10 ET
