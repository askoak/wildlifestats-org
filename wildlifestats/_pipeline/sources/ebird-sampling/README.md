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

Scope and posture:

- Current committed artifacts are a Virginia-only pilot.
- This is a method proof and denominator-policy proof, not yet a national
  production denominator for WildlifeStats.org.
- The committed repo artifacts remain aggregate-only. No raw eBird rows are
  committed here.

How the local 8 GB archive is used:

- The archive is verified locally from
  `C:\Users\Hello\Downloads\ebd_sampling_relMay-2026.tar`.
- A local extracted working copy may exist at
  `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\WildStats\ebirdSamplingMay2026`
  for inspection and bounded follow-up work.
- WildlifeStats does not "connect to a PC" in any autonomous sense. The local
  Python pilot reads Mike's local archive or extracted working copy when an
  operator runs it, then emits aggregate-only derived artifacts back into this
  repo.

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
- Do not treat this folder as a rolling multi-state archive.

National architecture note:

- WildlifeStats does not need all 50 states just to validate the pilot method.
- WildlifeStats will need a broader off-repo derived-output plan before it can
  claim a national production denominator.
- See
  `docs/handoff/wildlifestats-ebird-national-architecture-2026-06-16.md`
  for the storage, scope, and rollout posture.

