#!/usr/bin/env python3
"""Generate the synthetic WildlifeStats admissions cube.

Deterministic: same --seed produces byte-identical output. The data is
synthetic and is NOT derived from any real wildlife center's records; it is
sampled from regional distribution models calibrated against the patterns
described in published wildlife rehabilitation literature.

Usage:
    python wildlifestats/_build/generate_synthetic_cube.py \
        --seed 42 --n 100000 --out data/cube/admissions-cube.json

Spec: docs/handoff/wildlifestats-synthetic-cube-spec-phase3-2026-06-10.md

Design notes (engineer, documented for architect ratification):
  * Records are drawn by exact multinomial sampling of N records, then
    aggregated. The Monte-Carlo dispersion is what makes cells differ from
    their exact proportional value (spec §8 intent), while the total stays at
    exactly N -- well within the §11 ±500 tolerance. We therefore do not apply
    a separate destructive ±5-10% jitter that could bias the total when small
    cells round to zero.
  * Cells are written as compact integer-index arrays with a `cells_legend`,
    not verbose objects, so the file meets the ≤8 MB cap (spec §2 target shape
    is preserved as the legend; the data is identical).
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
MONTHS = list(range(1, 13))
CLASSES = ["bird", "mammal", "reptile", "amphibian", "marine"]
REASONS = ["vehicle_strike", "window_strike", "predation", "entanglement",
           "orphan_displacement", "habitat_disruption", "anthropogenic_poisoning",
           "infectious_disease", "other_trauma", "unknown"]
OUTCOMES = ["released", "transferred", "deceased", "in_care", "euthanized"]
DISPOSITIONS = ["wild_release_local", "wild_release_relocated", "permanent_sanctuary",
                "research_donation", "natural_death", "humane_euthanasia"]

YEAR_WEIGHTS = np.array([0.95, 0.97, 1.00, 0.92, 1.05, 1.08, 1.10, 1.12, 1.14])

REASON_BASE = {
    "vehicle_strike": 0.18, "window_strike": 0.14, "predation": 0.09,
    "entanglement": 0.05, "orphan_displacement": 0.22, "habitat_disruption": 0.08,
    "anthropogenic_poisoning": 0.04, "infectious_disease": 0.06,
    "other_trauma": 0.10, "unknown": 0.04,
}
REASON_DELTAS = {
    "bird": {"window_strike": 0.06, "vehicle_strike": -0.04, "entanglement": 0.02},
    "mammal": {"vehicle_strike": 0.08, "orphan_displacement": 0.04, "window_strike": -0.06},
    "reptile": {"vehicle_strike": 0.10, "window_strike": -0.08},
    "amphibian": {"habitat_disruption": 0.04, "unknown": 0.02},
    "marine": {"entanglement": 0.10, "anthropogenic_poisoning": 0.06, "window_strike": -0.12},
}

OUTCOME_BASE = {
    "released": 0.45, "transferred": 0.08, "deceased": 0.28,
    "in_care": 0.04, "euthanized": 0.15,
}
# Per-reason outcome adjustments (renormalized, clipped at 0).
OUTCOME_DELTAS = {
    "vehicle_strike": {"deceased": 0.12, "euthanized": 0.08, "released": -0.18},
    "predation": {"deceased": 0.18, "euthanized": 0.04, "released": -0.20},
    "orphan_displacement": {"released": 0.22, "deceased": -0.14, "euthanized": -0.06},
    "window_strike": {"deceased": 0.06, "released": -0.04},
    "anthropogenic_poisoning": {"deceased": 0.10, "euthanized": 0.06, "released": -0.14},
    "infectious_disease": {"euthanized": 0.10, "deceased": 0.06, "released": -0.14},
    "entanglement": {"released": 0.05, "euthanized": 0.03, "deceased": -0.06},
    "habitat_disruption": {"released": 0.08, "deceased": -0.06},
}
# Disposition given outcome.
DISP_GIVEN_OUTCOME = {
    "released": {"wild_release_local": 0.85, "wild_release_relocated": 0.15},
    "transferred": {"wild_release_local": 0.50, "permanent_sanctuary": 0.50},
    "deceased": {"natural_death": 1.0},
    # in_care has no terminal disposition; routed to permanent_sanctuary as the
    # long-term-care residual (spec §7 "still pending").
    "in_care": {"permanent_sanctuary": 1.0},
    "euthanized": {"humane_euthanasia": 1.0},
}

# State land area (sq mi, land only) and approximate federal-land fraction.
# Public constants (US Census state areas; federal-land share approximations
# from federal land-management summaries). Used only for the §3.1 composite.
STATE_LAND = {
    "AL": 50645, "AK": 570641, "AZ": 113594, "AR": 52035, "CA": 155779,
    "CO": 103642, "CT": 4842, "DE": 1949, "DC": 61, "FL": 53625, "GA": 57513,
    "HI": 6423, "ID": 82643, "IL": 55519, "IN": 35826, "IA": 55857, "KS": 81759,
    "KY": 39486, "LA": 43204, "ME": 30843, "MD": 9707, "MA": 7800, "MI": 56539,
    "MN": 79627, "MS": 46923, "MO": 68742, "MT": 145546, "NE": 76824,
    "NV": 109781, "NH": 8953, "NJ": 7354, "NM": 121298, "NY": 47126,
    "NC": 48618, "ND": 69001, "OH": 40861, "OK": 68595, "OR": 95988,
    "PA": 44743, "RI": 1034, "SC": 30061, "SD": 75811, "TN": 41235,
    "TX": 261232, "UT": 82170, "VT": 9217, "VA": 39490, "WA": 66456,
    "WV": 24038, "WI": 54158, "WY": 97093,
}
STATE_FED_FRAC = {
    "AL": 0.03, "AK": 0.61, "AZ": 0.385, "AR": 0.09, "CA": 0.458, "CO": 0.36,
    "CT": 0.004, "DE": 0.022, "DC": 0.25, "FL": 0.072, "GA": 0.06, "HI": 0.20,
    "ID": 0.617, "IL": 0.015, "IN": 0.016, "IA": 0.003, "KS": 0.006, "KY": 0.05,
    "LA": 0.045, "ME": 0.011, "MD": 0.03, "MA": 0.013, "MI": 0.10, "MN": 0.07,
    "MS": 0.05, "MO": 0.05, "MT": 0.29, "NE": 0.011, "NV": 0.795, "NH": 0.135,
    "NJ": 0.038, "NM": 0.347, "NY": 0.008, "NC": 0.07, "ND": 0.038, "OH": 0.013,
    "OK": 0.018, "OR": 0.527, "PA": 0.022, "RI": 0.005, "SC": 0.05, "SD": 0.055,
    "TN": 0.06, "TX": 0.018, "UT": 0.645, "VT": 0.075, "VA": 0.10, "WA": 0.286,
    "WV": 0.115, "WI": 0.05, "WY": 0.485,
}


def normalize(vec):
    vec = np.clip(np.asarray(vec, dtype=float), 0.0, None)
    return vec / vec.sum()


def month_probs_for_band(band):
    """Seasonal month distribution by latitude band (spec §5.2)."""
    base = np.ones(12)
    if band == "north":          # lat >= 42
        peak, amp = 6, 2.5
    elif band == "mid":          # 30..42
        peak, amp = 5, 2.0
    elif band == "south":        # < 30
        peak, amp = 4, 1.5
    elif band == "ak":
        peak, amp = 7, 3.0
    else:                        # fl_hi: flat
        peak, amp = 5, 1.3
    for m in range(12):
        dist = min(abs((m + 1) - peak), 12 - abs((m + 1) - peak))
        base[m] = 1.0 + (amp - 1.0) * max(0.0, 1.0 - dist / 3.0)
    if band == "south":          # secondary winter bump for migrants
        base[11] += 0.3
        base[0] += 0.3
    return normalize(base)


def lat_band(lat, state):
    if state == "AK":
        return "ak"
    if state in ("FL", "HI"):
        return "fl_hi"
    if lat >= 42:
        return "north"
    if lat >= 30:
        return "mid"
    return "south"


def reason_probs(cls, baby_season):
    p = dict(REASON_BASE)
    for k, dv in REASON_DELTAS.get(cls, {}).items():
        p[k] = p[k] + dv
    if baby_season:
        p["orphan_displacement"] *= 1.6
    return normalize([p[r] for r in REASONS])


def outcome_probs(reason):
    p = dict(OUTCOME_BASE)
    for k, dv in OUTCOME_DELTAS.get(reason, {}).items():
        p[k] = p[k] + dv
    return normalize([p[o] for o in OUTCOMES])


def disp_probs(outcome):
    d = DISP_GIVEN_OUTCOME[outcome]
    return normalize([d.get(x, 0.0) for x in DISPOSITIONS])


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n", type=int, default=100000)
    ap.add_argument("--out", default=os.path.join(REPO, "data", "cube", "admissions-cube.json"))
    ap.add_argument("--with-parks-overlay", action="store_true",
                    help="also emit data/cube/parks-overlay.json (NPS unit rollups)")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    counties = load_json(os.path.join(HERE, "county-fips.json"))["counties"]
    region_map = load_json(os.path.join(HERE, "state-region-map.json"))["states"]
    archetypes = load_json(os.path.join(HERE, "species-archetypes.json"))["regions"]

    states = sorted({c["state"] for c in counties})
    state_idx = {s: i for i, s in enumerate(states)}

    # Global species vocabulary (stable, sorted).
    species_vocab = sorted({sp for reg in archetypes.values()
                            for spd in reg["species"].values() for sp in spd})
    species_idx = {sp: i for i, sp in enumerate(species_vocab)}

    n_counties = len(counties)
    county_state = np.array([state_idx[c["state"]] for c in counties])
    county_pop = np.array([c["pop"] for c in counties], dtype=float)
    county_region = [region_map[c["state"]]["region"] for c in counties]
    county_lat = np.array([region_map[c["state"]]["lat"] for c in counties])

    # ---- §3.1 state composite weights: 60% pop, 30% land, 10% protected ----
    state_pop = np.array([
        sum(county_pop[i] for i in range(n_counties) if county_state[i] == state_idx[s])
        for s in states], dtype=float)
    state_land = np.array([STATE_LAND[s] for s in states], dtype=float)
    state_prot = np.array([STATE_LAND[s] * STATE_FED_FRAC[s] for s in states], dtype=float)
    state_w = (0.60 * normalize(state_pop)
               + 0.30 * normalize(state_land)
               + 0.10 * normalize(state_prot))
    state_w = normalize(state_w)

    # ---- §3.2 county weights within state: 50% pop, 50% uniform ----
    county_w = np.zeros(n_counties)
    for si, s in enumerate(states):
        members = np.where(county_state == si)[0]
        pop = county_pop[members]
        pop_share = pop / pop.sum() if pop.sum() > 0 else np.ones(len(members)) / len(members)
        uniform = np.ones(len(members)) / len(members)
        county_w[members] = state_w[si] * (0.5 * pop_share + 0.5 * uniform)
    county_w = normalize(county_w)

    N = args.n

    # ---- draw records (fixed draw order => deterministic) ----
    rec_county = rng.choice(n_counties, size=N, p=county_w)
    rec_year = rng.choice(len(YEARS), size=N, p=normalize(YEAR_WEIGHTS))

    # month by latitude band
    rec_month = np.empty(N, dtype=int)
    bands = np.array([lat_band(county_lat[c], states[county_state[c]]) for c in rec_county])
    for b in ("north", "mid", "south", "ak", "fl_hi"):
        mask = bands == b
        k = int(mask.sum())
        if k:
            rec_month[mask] = rng.choice(12, size=k, p=month_probs_for_band(b)) + 1

    # class by region
    rec_class = np.empty(N, dtype=int)
    region_names = sorted(archetypes)
    rec_region = np.array(county_region)[rec_county]
    for rn in region_names:
        mask = rec_region == rn
        k = int(mask.sum())
        if not k:
            continue
        cw = archetypes[rn]["class_weights"]
        cls_ids = [CLASSES.index(c) for c in cw]
        probs = normalize([cw[c] for c in cw])
        rec_class[mask] = rng.choice(cls_ids, size=k, p=probs)

    # species by (region, class)
    rec_species = np.empty(N, dtype=int)
    for rn in region_names:
        spd = archetypes[rn]["species"]
        for cname, table in spd.items():
            ci = CLASSES.index(cname)
            mask = (rec_region == rn) & (rec_class == ci)
            k = int(mask.sum())
            if not k:
                continue
            sp_ids = [species_idx[sp] for sp in table]
            probs = normalize([table[sp] for sp in table])
            rec_species[mask] = rng.choice(sp_ids, size=k, p=probs)

    # reason by (class, baby-season)
    baby = np.isin(rec_month, [5, 6, 7])
    rec_reason = np.empty(N, dtype=int)
    for ci, cname in enumerate(CLASSES):
        for bb in (False, True):
            mask = (rec_class == ci) & (baby == bb)
            k = int(mask.sum())
            if k:
                rec_reason[mask] = rng.choice(10, size=k, p=reason_probs(cname, bb))

    # outcome by reason
    rec_outcome = np.empty(N, dtype=int)
    for ri, rname in enumerate(REASONS):
        mask = rec_reason == ri
        k = int(mask.sum())
        if k:
            rec_outcome[mask] = rng.choice(5, size=k, p=outcome_probs(rname))

    # disposition by outcome
    rec_disp = np.empty(N, dtype=int)
    for oi, oname in enumerate(OUTCOMES):
        mask = rec_outcome == oi
        k = int(mask.sum())
        if k:
            rec_disp[mask] = rng.choice(len(DISPOSITIONS), size=k, p=disp_probs(oname))

    # ---- aggregate to cells ----
    keys = np.stack([
        rec_year, rec_month, county_state[rec_county], rec_county,
        rec_class, rec_species, rec_reason, rec_outcome, rec_disp,
    ], axis=1)
    uniq, counts = np.unique(keys, axis=0, return_counts=True)
    cells = [list(map(int, row)) + [int(c)] for row, c in zip(uniq.tolist(), counts.tolist())]
    cells.sort()

    meta = {
        "version": "1.0.0",
        "generated_at": "2026-06-10T19:00:00Z",
        "seed": args.seed,
        "n_records": int(counts.sum()),
        "n_cells": len(cells),
        "license": "CC-BY-4.0",
        "description": "Synthetic wildlife rehabilitation admission records. "
                       "Not derived from any real center's data.",
    }

    cube = {
        "meta": meta,
        "cells_legend": ["year_idx", "month", "state_idx", "county_idx",
                         "class_idx", "species_idx", "reason_idx",
                         "outcome_idx", "disposition_idx", "n"],
        "dimensions": {
            "years": YEARS,
            "months": MONTHS,
            "states": states,
            "counties": [{"fips": c["fips"], "state": c["state"], "name": c["name"]}
                         for c in counties],
            "classes": CLASSES,
            "species": species_vocab,
            "reasons": REASONS,
            "outcomes": OUTCOMES,
            "dispositions": DISPOSITIONS,
        },
        "cells": cells,
    }

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cube, f, ensure_ascii=False, separators=(",", ":"), sort_keys=False)

    meta_out = os.path.join(os.path.dirname(args.out), "admissions-cube.meta.json")
    with open(meta_out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"meta": meta,
                   "dimensions_summary": {
                       "years": [YEARS[0], YEARS[-1]],
                       "n_states": len(states),
                       "n_counties": n_counties,
                       "n_species": len(species_vocab),
                       "regions": region_names,
                   }}, f, ensure_ascii=False, indent=2, sort_keys=False)

    size_mb = os.path.getsize(args.out) / 1e6
    print(f"wrote {args.out}: {len(cells)} cells, n={meta['n_records']}, {size_mb:.2f} MB")
    print(f"wrote {meta_out}")

    if args.with_parks_overlay:
        write_parks_overlay(cells, counties, states, args)


def _haversine_mi(lat1, lon1, lat2, lon2):
    import math
    r = 3958.8  # earth radius, miles
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def write_parks_overlay(cells, counties, states, args, radius_mi=50.0):
    """Per-park rollup of admissions from counties within radius_mi of each
    NPS unit. Deterministic from the committed cube + county centroids."""
    nps_path = os.path.join(REPO, "assets", "data", "nps-units.json")
    nps = load_json(nps_path)["units"]

    # county centroids
    clat = [c.get("lat") for c in counties]
    clon = [c.get("lon") for c in counties]

    # Pre-aggregate cells by county into class/reason/month vectors.
    iM, iCTY, iCL, iRS, iN = 1, 3, 4, 6, 9
    per_county = {}  # county_idx -> {"class":[5], "reason":[10], "month":[12], "total":n}
    for c in cells:
        cty = c[iCTY]
        rec = per_county.get(cty)
        if rec is None:
            rec = {"class": [0] * len(CLASSES), "reason": [0] * len(REASONS),
                   "month": [0] * 12, "total": 0}
            per_county[cty] = rec
        n = c[iN]
        rec["class"][c[iCL]] += n
        rec["reason"][c[iRS]] += n
        rec["month"][c[iM] - 1] += n
        rec["total"] += n

    parks_out = []
    for unit in nps:
        plat, plon = unit["lat"], unit["lon"]
        cls = [0] * len(CLASSES)
        rsn = [0] * len(REASONS)
        mon = [0] * 12
        total = 0
        ncty = 0
        for cty, rec in per_county.items():
            if clat[cty] is None:
                continue
            if _haversine_mi(plat, plon, clat[cty], clon[cty]) <= radius_mi:
                ncty += 1
                total += rec["total"]
                for i in range(len(CLASSES)):
                    cls[i] += rec["class"][i]
                for i in range(len(REASONS)):
                    rsn[i] += rec["reason"][i]
                for i in range(12):
                    mon[i] += rec["month"][i]
        top_classes = sorted(
            [{"class": CLASSES[i], "n": cls[i]} for i in range(len(CLASSES)) if cls[i]],
            key=lambda x: -x["n"])[:5]
        top_reasons = sorted(
            [{"reason": REASONS[i], "n": rsn[i]} for i in range(len(REASONS)) if rsn[i]],
            key=lambda x: -x["n"])[:5]
        parks_out.append({
            "name": unit["name"], "type": unit["type"], "state": unit["state"],
            "lat": plat, "lon": plon, "n_counties": ncty, "total": total,
            "classes": top_classes, "reasons": top_reasons, "monthly": mon,
        })

    parks_out.sort(key=lambda p: p["name"])
    overlay = {
        "meta": {
            "version": "1.0.0",
            "radius_mi": radius_mi,
            "n_parks": len(parks_out),
            "description": "Synthetic admissions rolled up to NPS units from "
                           "counties within the given radius. Plausibly shaped by "
                           "region; not measured against any park's actual activity.",
        },
        "parks": parks_out,
    }
    out = os.path.join(REPO, "data", "cube", "parks-overlay.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(overlay, f, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    print(f"wrote {out}: {len(parks_out)} parks")


if __name__ == "__main__":
    main()
