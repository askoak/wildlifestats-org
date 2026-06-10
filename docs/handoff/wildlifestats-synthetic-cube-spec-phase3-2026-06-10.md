# Phase 3 synthetic-cube architecture spec

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 14:38 ET
**Status:** Source of truth for the Phase 3 engineer order (cube generation + wiring).

This file is the architect deliverable that unblocks Phase 3 generation. The Phase 3 engineer order references this file by path.

## §1 — Goal

Produce a synthetic, reproducible, auditable dataset of **n=100,000 wildlife rehabilitation patient records** distributed across all 50 states + DC, exposed as a queryable JSON cube on the public site at `/data/`.

The data must be **plausibly shaped** (consistent with published wildlife rehabilitation literature) without being a copy or near-copy of any real wildlife center's records.

## §2 — Output schema

Single output file: `data/cube/admissions-cube.json` (committed to the repo; ~2-5 MB gzipped, acceptable size for static hosting).

Top-level shape:

```json
{
  "meta": {
    "version": "1.0.0",
    "generated_at": "2026-06-10T19:00:00Z",
    "seed": 42,
    "n_records": 100000,
    "license": "CC-BY-4.0",
    "description": "Synthetic wildlife rehabilitation admission records. Not derived from any real center's data."
  },
  "dimensions": {
    "years": [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "states": ["AL", "AK", ..., "WY", "DC"],
    "classes": ["bird", "mammal", "reptile", "amphibian", "marine"],
    "species_archetypes": [...see §4...],
    "admission_reasons": ["vehicle_strike", "window_strike", "predation", "entanglement", "orphan_displacement", "habitat_disruption", "anthropogenic_poisoning", "infectious_disease", "other_trauma", "unknown"],
    "outcomes": ["released", "transferred", "deceased", "in_care", "euthanized"],
    "dispositions": ["wild_release_local", "wild_release_relocated", "permanent_sanctuary", "research_donation", "natural_death", "humane_euthanasia"]
  },
  "cells": [
    {
      "year": 2024,
      "month": 5,
      "state": "VA",
      "county_fips": "51043",
      "class": "bird",
      "species": "passerine_songbird",
      "reason": "window_strike",
      "outcome": "released",
      "disposition": "wild_release_local",
      "n": 14
    },
    ...
  ]
}
```

Cells are aggregated counts, not individual records. Total of `n` across all cells = 100,000 ± a few hundred (per-cell jitter — see §6).

## §3 — Geographic distribution

### §3.1 State-level allocation

Allocate the 100,000 records across the 51 jurisdictions (50 states + DC) weighted by a composite index of:

- 60% US Census 2020 state population
- 30% land area (favors low-population, high-wildlife states like MT, WY, AK)
- 10% federally protected land area (favors NPS/USFS-heavy states)

Result: every state gets a meaningful share; CA / TX / FL / NY are largest but not dominant; WY / MT / VT get plausible shares.

### §3.2 County-level allocation within state

For each state's allocation, distribute across that state's counties weighted by:

- 50% county population
- 50% uniform (every county gets a baseline share)

This produces some records in every county in the US (~3,143 counties + DC + boroughs), even tiny ones, while urban counties get the largest shares.

Use county FIPS codes as the canonical identifier. The build script downloads the 2020 Census county FIPS list from a committed snapshot (don't hit the API at build time).

## §4 — Species archetypes

Define **regional species archetypes** — small banks of species mixes for each biogeographic region. Each county is assigned to one region; the species mix for records in that county is drawn from that region's archetype.

Regions (simplified for tractability):

| Region | States | Archetype species mix (probabilities sum to 1.0 within class) |
|---|---|---|
| Pacific Northwest | WA, OR, ID (north), MT (west) | Higher: passerines, raptors (bald eagle, red-tailed hawk), black bear. Lower: reptiles. |
| Pacific Southwest | CA, NV (south) | Higher: passerines, raptors, deer mule. Mid: reptiles (gopher snake, fence lizard). |
| Mountain West | ID (south), UT, NV (north), WY, CO, MT (east), AZ (north), NM (north) | Higher: raptors, pronghorn, mule deer. Mid: passerines. |
| Desert Southwest | AZ (south), NM (south), TX (west) | Higher: reptiles (tortoise, lizard, snake), raptors (hawk, falcon). Lower: amphibians. |
| Great Plains | ND, SD, NE, KS, OK, TX (panhandle) | Higher: passerines, prairie raptors, prairie dog. Lower: marine. |
| Upper Midwest | MN, WI, MI, IA | Higher: passerines, raptors (bald eagle), white-tailed deer. |
| Lower Midwest | IL, IN, OH, MO | Higher: passerines, raptors, white-tailed deer, opossum. |
| Northeast | ME, NH, VT, MA, RI, CT, NY, PA, NJ | Higher: passerines, raptors, white-tailed deer, harbor seal (coastal counties). |
| Mid-Atlantic | MD, DE, VA, WV, DC | Higher: passerines, raptors, white-tailed deer. Coastal: shorebirds, terrapin. |
| Southeast | KY, TN, NC, SC, GA, AL, MS, LA, AR | Higher: passerines, raptors, white-tailed deer, opossum. Coastal: pelican, sea turtle. |
| Florida | FL | Higher: pelican, sea turtle, manatee (coastal), raptors, reptiles year-round. |
| Texas Plains | TX (central, east, south) | Higher: passerines, raptors, white-tailed deer, armadillo. Coastal: pelican, sea turtle. |
| Alaska | AK | Higher: raptors (bald eagle), waterfowl, bear (black, brown), seal. |
| Hawaii | HI | Higher: seabirds, native passerines (`apapane`, `iiwi` — taxa only, no individual species rarity calling). Marine. |

Each region defines a class-stratified species probability table. The generation script picks species for each record by drawing from the region's table conditional on the record's class.

Species archetypes file: `wildlifestats/_build/species-archetypes.json`. Committed.

## §5 — Temporal distribution

### §5.1 Year-over-year trend

Slight upward trend from 2017 → 2025 to reflect documented increases in wildlife rehabilitation case loads:

```
year_weights = {
  2017: 0.95,
  2018: 0.97,
  2019: 1.00,
  2020: 0.92,  // pandemic dip (real centers documented this)
  2021: 1.05,  // post-pandemic rebound
  2022: 1.08,
  2023: 1.10,
  2024: 1.12,
  2025: 1.14
}
```

Normalize so weights sum to 9 (number of years).

### §5.2 Seasonality

Strong baby-season peak in May-July (orphan / displacement reasons spike); secondary fall peak (window strikes during migration). Modulated by latitude:

- Northern counties (lat ≥ 42°): peak month = June, amplitude = 2.5× off-season baseline
- Mid-latitude (30–42°): peak month = May, amplitude = 2.0×
- Southern counties (lat < 30°): peak month = April, amplitude = 1.5×; secondary winter bump for migrants
- AK: peak month = July, amplitude = 3.0× (very compressed season)
- FL / HI: no strong peak; year-round amplitude 1.2–1.4×

## §6 — Admission reasons distribution

Base probabilities (apply class-stratified adjustments — birds skew window-strike, mammals skew vehicle-strike, etc.):

```
reason_base = {
  "vehicle_strike": 0.18,
  "window_strike": 0.14,
  "predation": 0.09,
  "entanglement": 0.05,
  "orphan_displacement": 0.22,  // largest single category, dominant in baby season
  "habitat_disruption": 0.08,
  "anthropogenic_poisoning": 0.04,
  "infectious_disease": 0.06,
  "other_trauma": 0.10,
  "unknown": 0.04
}
```

Class-stratified deltas:

- birds: +0.06 window_strike, -0.04 vehicle_strike, +0.02 entanglement
- mammals: +0.08 vehicle_strike, +0.04 orphan_displacement, -0.06 window_strike
- reptiles: +0.10 vehicle_strike (road crossings), -0.08 window_strike
- amphibians: +0.04 habitat_disruption, +0.02 unknown
- marine: +0.10 entanglement, +0.06 anthropogenic_poisoning, -0.12 window_strike

Renormalize per record so probabilities sum to 1.0 after deltas.

Orphan_displacement amplifies further during baby season per the seasonality multiplier in §5.2.

## §7 — Outcomes & dispositions

Outcomes are deliberately weighted toward realistic distributions:

```
outcome_base = {
  "released": 0.45,
  "transferred": 0.08,
  "deceased": 0.28,  // includes died-in-care
  "in_care": 0.04,
  "euthanized": 0.15
}
```

Outcome correlates with admission reason — vehicle_strike has higher deceased + euthanized; orphan_displacement has higher released; predation has higher deceased.

Disposition is determined by outcome:
- released → wild_release_local (0.85) or wild_release_relocated (0.15)
- transferred → wild_release_local (0.50, after transfer) or permanent_sanctuary (0.50)
- deceased → natural_death (1.0)
- in_care → still pending (handled as a residual)
- euthanized → humane_euthanasia (1.0)

## §8 — Jitter and seed strategy

- Master seed: `42`. Hard-coded in the generator.
- Per-cell jitter: ±5–10% on the final `n` count, drawn from a deterministic seeded RNG. Ensures no two cells are exactly the proportional value, and small cells get more variance than large ones.
- Cells with `n < 1` after jitter are dropped (no fractional records).
- Cells with `n < 10` are aggregated for the public-facing `/data/` interface (k-suppression, see §10) but remain in the underlying JSON.

## §9 — Generator script

File: `wildlifestats/_build/generate_synthetic_cube.py`

Single-command rebuild:

```bash
python wildlifestats/_build/generate_synthetic_cube.py \
  --seed 42 \
  --n 100000 \
  --out data/cube/admissions-cube.json
```

Deterministic. Same seed → byte-identical output.

The script is ~400 lines of Python, no external dependencies beyond `numpy` and the Python standard library. `numpy` is the only pip install. Committed `requirements.txt`:

```
numpy==1.26.4
```

Generator reads:

- `wildlifestats/_build/species-archetypes.json` (regional species probability tables)
- `wildlifestats/_build/state-region-map.json` (which region each state belongs to; for multi-region states like TX or MT, defines per-county overrides)
- `wildlifestats/_build/county-fips.json` (committed snapshot of 2020 Census FIPS codes + name + state + population)

Generator writes:

- `data/cube/admissions-cube.json`
- `data/cube/admissions-cube.meta.json` (just the meta block, for fast page-load on `/data/` without parsing the whole cube)

## §10 — Public interface (Phase 4 hand-off)

The `/data/` page (Phase 4 work) consumes `admissions-cube.json` and presents:

- Filter dropdowns: year, month, state, class, reason
- Aggregate counts displayed
- A small choropleth map (counties colored by `n`)
- CSV download of filtered subset

**k-suppression rule:** any CSV row with `n < 10` after filtering is collapsed into a single "Suppressed (n<10)" row. The public-tier CSV does not expose granular small-cell counts. This matches the BRWC privacy discipline by build, not by runtime — the cube JSON does contain small cells, but the public interface's download path filters them.

The interface is Phase 4 work, not Phase 3. Phase 3 ends when the cube file is committed and the `/data/` page can load its meta.

## §11 — Validation tests

A second script, `wildlifestats/_build/validate_cube.py`, runs as part of CI:

- Total `n` is within 100,000 ± 500
- Every state has ≥ 50 records
- Every year has ≥ 5,000 records
- Every (region, class) combination present in archetypes has ≥ 10 records
- Sum of probabilities in every species archetype is ≥ 0.99 and ≤ 1.01
- No NaN, no negative `n`, no unknown reason / outcome / disposition values

CI workflow adds a fourth job (`cube-validate`) that runs `python validate_cube.py` and fails the build if any check fails. This protects against accidental cube regressions.

## §12 — What is NOT in Phase 3

- Individual patient records. Cube is aggregate counts only. No per-individual data exists, synthetic or otherwise.
- Outcomes by week or by day. Month is the finest temporal grain.
- Real species names beyond the archetype level for sensitive taxa (e.g. "raptor" in some regions, not "northern goshawk specifically").
- Any data attribution. The cube is synthetic; methodology page describes its origin (regional distribution models calibrated against published literature), not a specific source organization.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:38 ET
