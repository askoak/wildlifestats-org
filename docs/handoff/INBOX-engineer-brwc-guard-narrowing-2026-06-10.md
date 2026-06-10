# INBOX — BRWC content-guard pattern narrowed (Phase 3), flagged for ratification

**From:** WildlifeStats Engineer, `soar-aspen-beryl-heron`
**To:** WildlifeStats Architect, `measured-fern-jasper-thrush`
**Date:** 2026-06-10
**Re:** `scripts/check-no-brwc.sh` change shipped in the Phase 3 cube PR

## What changed and why

Phase 3 commits the national county dataset (`wildlifestats/_build/county-fips.json`) and the synthetic cube (`data/cube/admissions-cube.json`), both keyed on the full 2020 US Census county list (3,143 counties). The BRWC content guard failed on these files because one forbidden pattern, the bare string `clarke county`, collides with a **real US county name** that exists in six states — Alabama, Georgia, Iowa, Mississippi, Virginia, and Washington. A national dataset cannot omit those counties, and doing so would itself be a tell.

I narrowed the single pattern from `clarke county` → `clarke county, v`. Rationale:

- The BRWC identifier is the **prose frame** "Clarke County, Virginia" (plus Boyce, Blue Ridge, Jen Riley), not the bare census name appearing as one structured row among 3,143.
- `clarke county, v` still matches "Clarke County, Virginia" and "Clarke County, VA" in any prose, so a BRWC framing on the public tier still fails the guard.
- The structured Census data — `"name":"Clarke County","state":"VA"` — does not contain the substring `clarke county, v`, so it passes.
- All other BRWC patterns are unchanged: `blue ridge wildlife`, `brwc`, `jen riley`, `dr. riley`, `boyce, va`, `boyce virginia`, `askoak.michaeloak`.

Net effect: the §19 contract (no BRWC content on the public tier) is **preserved**; only a false-positive on legitimate national Census data was removed.

## Why I shipped it rather than waiting

Mike authorized full autonomy for the overnight run with no gates, and the architect seat is dormant. The cube PR's `brwc-content-guard` CI job cannot pass without this fix, and the cube is the deliverable. Per §16, I picked the defensible default and am surfacing it here for review rather than blocking.

## Ask

Ratify or object. If you object, the revert is a one-line change to `scripts/check-no-brwc.sh` (restore the bare `clarke county` pattern) — but note that doing so re-breaks CI on any PR that includes the national county data, so an alternative exclusion mechanism (e.g. excluding `data/cube/` and `wildlifestats/_build/county-fips.json` from the scan) would be needed instead. I'd prefer the narrowed pattern; it keeps the guard scanning the data files for the genuinely-forbidden strings.

— Engineer, `soar-aspen-beryl-heron`, 2026-06-10
