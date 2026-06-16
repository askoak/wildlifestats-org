# eBird Sampling Pilot

Local-only source folder for the eBird sampling denominator pilot.

Contents:

- `DATA_TERMS.md` — redistribution and use constraints for this source
- `provenance.yml` — archive verification, pilot provenance, and denominator policy
- `results/virginia_complete_checklist_effort_by_county_week_protocol.csv`
  — canonical aggregate-only pilot artifact
- `results/virginia_complete_checklist_effort_by_county_week_protocol_stratified.csv`
  — derived stratified artifact from the committed aggregate CSV only
- `results/virginia_complete_checklist_effort_by_county_week_protocol_stratified.summary.yml`
  — compact summary of the denominator policy split

Downstream denominator policy:

- Keep the full aggregate CSV as the canonical pilot artifact.
- Primary downstream denominator uses rows with `effort_metadata_class = effort_present`.
- `effort_present` means at least one of `duration_minutes_count`,
  `effort_distance_km_count`, or `effort_area_ha_count` is greater than zero.
- `zero_effort` remains queryable as a low-trust secondary stratum.
- Do not blanket-drop `Incidental` or `Historical` by protocol name; stratify by
  observed effort metadata instead.

Guardrail:

- No raw eBird rows are committed here.
- `raw/` and `_scratch/` are git-ignored on purpose.

