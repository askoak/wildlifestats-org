# WO-2026-06-16-wls-ebird-sampling-denominator-policy-followup

**Date:** 2026-06-16  
**Author:** Codex  
**Status:** Proposed bounded follow-up from architect audit of PR #74  
**Scope:** Lock the denominator policy off the committed aggregate-only pilot
artifact, without rerunning the full eBird archive.

## 1. Why this exists

PR #74 proved the local Virginia denominator pilot and committed an
aggregate-only CSV with hash
`553f847986b3a39145b7308987fe02eb4bcee15fbf68b28a536a36c0525847f2`.

The remaining judgment call is not whether the pilot worked. It did.

The remaining judgment call is denominator policy: whether downstream avian
signals should treat every complete checklist as equally denominator-worthy, or
whether complete-but-zero-effort rows should be segregated from the primary
denominator.

## 2. Architect audit outcome on PR #74

### Schema and governance

- The pilot schema is sane for the stated grain:
  `county_code × iso_year × iso_week × protocol_code`.
- The committed artifact is aggregate-only. No raw eBird rows or extracted raw
  files were committed.
- The source-governance chain is present:
  `DATA_TERMS.md`, `provenance.yml`, pilot handoff note, and results YAML.
- The offline pilot tests pass locally.

### CI state at audit time

- The PR head under audit is `ae9a50570c9eecfea9007f4cc0e44ebc2e7dc5ef`.
- The PR remains **draft** at audit time.
- The PR `validate` run is **unstable** at audit time because two jobs remain
  queued and the repo's existing `HTML validation` lane is failing here just as
  it is already failing on current `main` (`86cc0371fc861c02f8f4810c0c92fd0b8522e6e6`).
- Because the branch is still draft and not in a clean settled state, this
  audit pass stops at the bounded follow-up rather than forcing a merge.

### Storage call on the aggregate CSV

- Keep
  `wildlifestats/_pipeline/sources/ebird-sampling/results/virginia_complete_checklist_effort_by_county_week_protocol.csv`
  in git **for this pilot**.
- Rationale:
  - it is aggregate-only and hash-pinned
  - it is the core reproducibility artifact for the pilot
  - it is below GitHub's per-file ceiling
  - the repo already carries a comparable committed artifact:
    `data/cube/admissions-cube.json` at ~24.5 MB
- Caveat:
  - do **not** let this become a rolling archive pattern
  - if this grows into multi-state outputs or repeated refreshes, move the
    derived CSV artifacts out of git and keep only hashes, provenance, and
    compact summaries in-repo
  - preferred off-repo replacement path if that happens:
    `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\WildStats\artifacts\ebird-sampling\`

## 3. Exact denominator policy choice

Do **not** use "all complete checklists" as one undifferentiated downstream
denominator.

Use this policy instead:

1. Preserve the committed full aggregate CSV as the canonical pilot artifact.
2. Define the **primary denominator** as rows where at least one effort field
   is populated:
   - `duration_minutes_count > 0`, or
   - `effort_distance_km_count > 0`, or
   - `effort_area_ha_count > 0`
3. Define a secondary **low-trust zero-effort stratum** as rows where all
   three effort counts are zero.
4. Do **not** drop `Incidental` and `Historical` wholesale by protocol name.
   Stratify by observed effort metadata instead.

This is a stratify call, not a blanket protocol-drop call.

## 4. Evidence for the policy call

From the committed aggregate CSV:

- retained complete checklists: `2,271,631`
- complete-but-zero-effort checklists: `72,345`
- primary denominator if zero-effort rows are excluded: `2,199,286`

Zero-effort checklist distribution by protocol:

- `Incidental`: `49,289` of `60,745` (`81.14%`)
- `Historical`: `23,035` of `31,649` (`72.78%`)
- `Stationary`: `17` of `786,850`
- `Traveling`: `4` of `1,368,328`
- all other protocols in this pilot: `0`

That is why the right rule is "segregate zero-effort rows" rather than
"blindly drop whole protocols" or "treat everything as equally reliable."

## 5. Exact bounded follow-up

Next session should do this and nothing broader:

1. Read the committed aggregate CSV only. Do **not** rerun the full archive.
2. Emit a derived stratified artifact at:
   `wildlifestats/_pipeline/sources/ebird-sampling/results/virginia_complete_checklist_effort_by_county_week_protocol_stratified.csv`
3. Add one new column:
   - `effort_metadata_class` with values:
     - `effort_present`
     - `zero_effort`
4. Emit a paired compact summary YAML at:
   `wildlifestats/_pipeline/sources/ebird-sampling/results/virginia_complete_checklist_effort_by_county_week_protocol_stratified.summary.yml`
5. Update the source-folder `README.md` and provenance/handoff notes so the
   downstream rule is explicit:
   - full aggregate remains the audit artifact
   - primary denominator uses `effort_present`
   - `zero_effort` remains queryable as a low-trust tail

## 6. Hard rules for the follow-up

- Do not commit raw eBird rows or extracted raw files.
- Do not rerun the full archive pass unless the output schema itself changes.
- Do not delete or rewrite the original pilot CSV in this follow-up.
- If local-only inspection is needed, start from:
  `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\WildStats\ebirdSamplingMay2026`
  rather than re-extracting the tarball.

## 7. Acceptance criteria

- Original pilot CSV remains unchanged and still hashes to
  `553f847986b3a39145b7308987fe02eb4bcee15fbf68b28a536a36c0525847f2`.
- Stratified CSV is derived entirely from the committed aggregate CSV.
- Summary YAML reproduces:
  - total retained complete checklists: `2,271,631`
  - zero-effort complete checklists: `72,345`
  - primary denominator checklists: `2,199,286`
- README/provenance/handoff text makes the denominator policy explicit enough
  that the next architect does not have to rediscover it from chat.
