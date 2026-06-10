#!/usr/bin/env python3
"""Validate the synthetic admissions cube against the spec §11 checks.

Exits non-zero (failing CI) if any check fails. Reads the committed
data/cube/admissions-cube.json and the build inputs; runs without numpy so
the CI job stays light.

Spec: docs/handoff/wildlifestats-synthetic-cube-spec-phase3-2026-06-10.md §11
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

CUBE = os.path.join(REPO, "data", "cube", "admissions-cube.json")
ARCHETYPES = os.path.join(HERE, "species-archetypes.json")

LEGEND = ["year_idx", "month", "state_idx", "county_idx", "class_idx",
          "species_idx", "reason_idx", "outcome_idx", "disposition_idx", "n"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    failures = []

    cube = load(CUBE)
    arche = load(ARCHETYPES)["regions"]
    dims = cube["dimensions"]
    cells = cube["cells"]

    # legend sanity
    if cube.get("cells_legend") != LEGEND:
        failures.append(f"cells_legend mismatch: {cube.get('cells_legend')}")

    iy, im, ist, icty, icl, isp, irs, iou, idi, inn = range(10)

    total = sum(c[inn] for c in cells)
    if not (100000 - 500 <= total <= 100000 + 500):
        failures.append(f"total n {total} outside 100000±500")

    # no NaN / negative / unknown index values
    n_states = len(dims["states"])
    n_counties = len(dims["counties"])
    n_species = len(dims["species"])
    for c in cells:
        if len(c) != 10:
            failures.append(f"cell wrong arity: {c}"); break
        if c[inn] <= 0:
            failures.append(f"non-positive n: {c}"); break
        if not (0 <= c[iy] < len(dims["years"])):
            failures.append(f"bad year_idx: {c}"); break
        if not (1 <= c[im] <= 12):
            failures.append(f"bad month: {c}"); break
        if not (0 <= c[ist] < n_states):
            failures.append(f"bad state_idx: {c}"); break
        if not (0 <= c[icty] < n_counties):
            failures.append(f"bad county_idx: {c}"); break
        if not (0 <= c[icl] < len(dims["classes"])):
            failures.append(f"bad class_idx: {c}"); break
        if not (0 <= c[isp] < n_species):
            failures.append(f"bad species_idx: {c}"); break
        if not (0 <= c[irs] < len(dims["reasons"])):
            failures.append(f"bad reason_idx: {c}"); break
        if not (0 <= c[iou] < len(dims["outcomes"])):
            failures.append(f"bad outcome_idx: {c}"); break
        if not (0 <= c[idi] < len(dims["dispositions"])):
            failures.append(f"bad disposition_idx: {c}"); break

    # every state >= 50 records
    state_tot = [0] * n_states
    for c in cells:
        state_tot[c[ist]] += c[inn]
    for si, s in enumerate(dims["states"]):
        if state_tot[si] < 50:
            failures.append(f"state {s} has {state_tot[si]} records (<50)")

    # every year >= 5000 records
    year_tot = [0] * len(dims["years"])
    for c in cells:
        year_tot[c[iy]] += c[inn]
    for yi, y in enumerate(dims["years"]):
        if year_tot[yi] < 5000:
            failures.append(f"year {y} has {year_tot[yi]} records (<5000)")

    # every (region, class) present in archetypes has >= 10 records
    # map county_idx -> region via state-region map
    region_map = load(os.path.join(HERE, "state-region-map.json"))["states"]
    counties = dims["counties"]
    county_region = [region_map[c["state"]]["region"] for c in counties]
    rc_tot = {}
    for c in cells:
        region = county_region[c[icty]]
        cls = dims["classes"][c[icl]]
        rc_tot[(region, cls)] = rc_tot.get((region, cls), 0) + c[inn]
    for region, rdata in arche.items():
        for cls in rdata["species"]:
            got = rc_tot.get((region, cls), 0)
            if got < 10:
                failures.append(f"(region {region}, class {cls}) has {got} records (<10)")

    # species archetype probabilities sum in [0.99, 1.01]
    for region, rdata in arche.items():
        for cls, table in rdata["species"].items():
            s = sum(table.values())
            if not (0.99 <= s <= 1.01):
                failures.append(f"archetype {region}/{cls} probs sum {s:.4f}")

    if failures:
        print("CUBE VALIDATION FAILED:")
        for f in failures:
            print("  -", f)
        sys.exit(1)

    print("CUBE VALIDATION PASSED")
    print(f"  total records: {total}")
    print(f"  cells: {len(cells)}")
    print(f"  states: {n_states}, counties: {n_counties}, species: {n_species}")


if __name__ == "__main__":
    main()
