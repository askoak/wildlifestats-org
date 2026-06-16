# WO-2026-06-16-wls-ebird-sampling-denominator-pilot

**Date:** 2026-06-16  
**Author:** Codex  
**Status:** Completed local-only pilot  
**Scope:** Verify the local `ebd_sampling_relMay-2026.tar` archive, stream it
into a Virginia complete-checklist denominator layer, commit aggregate-only
outputs, and carry the source terms forward.

## 1. Why this exists

WildlifeStats already has a documented critique that Flyway's baseline cannot
rest on the synthetic cube alone. For avian signals, the first missing
ingredient is a real effort denominator: how much complete birding effort
occurred in a place and week, not just whether a species or event was seen.

This pilot does the narrowest honest first step:

- one local archive
- one state
- one aggregate grain
- no raw-row redistribution

## 2. Archive verification

Verified on `Hello` at:

- `C:\Users\Hello\Downloads\ebd_sampling_relMay-2026.tar`
- size: `8,460,072,960` bytes
- sha256:
  `ca69755b63f82f91d994be5021c11ca65b0affbca24e2747af1e03e772537678`

Archive members present:

- `ebd_sampling_relMay-2026.txt.gz`
- `BCRCodes.txt`
- `BirdLifeKBACodes.txt`
- `IBACodes.txt`
- `Protocols.txt`
- `USFWSCodes.txt`
- `eBird_Basic_Dataset_Metadata_v1.16.pdf`
- `recommended_citation.txt`
- `terms_of_use.txt`

Bundled citation:

> eBird Basic Dataset. Version: EBD_relMay-2026. Cornell Lab of Ornithology,
> Ithaca, New York. May 2026.

## 3. Pilot contract

### Filter

- `STATE CODE = US-VA`
- `ALL SPECIES REPORTED = 1`

### Grain

`county_code × iso_year × iso_week × protocol_code`

This grain is deliberate. The Flyway spec's anomaly logic is week-shaped and
county-shaped. A month-grain denominator would be easier, but less useful for
the stated baseline problem.

### Raw-row policy

- raw archive stays outside the repo
- no extracted raw rows written into git-tracked paths
- committed artifact is aggregate-only

## 4. Output schema

The pilot emits one CSV row per county-week-protocol cell at:

[`wildlifestats/_pipeline/sources/ebird-sampling/results/virginia_complete_checklist_effort_by_county_week_protocol.csv`](C:/Users/Hello/repos/wildlifestats-org/wildlifestats/_pipeline/sources/ebird-sampling/results/virginia_complete_checklist_effort_by_county_week_protocol.csv)

Columns:

- `state_name`, `state_code`
- `county_name`, `county_code`
- `iso_year`, `iso_week`, `week_start_date`, `week_end_date`
- `observation_type`, `protocol_name`, `protocol_code`
- `complete_checklist_count`, `sampling_event_count`
- `number_observers_total`
- `duration_minutes_count`, `duration_minutes_total`
- `effort_distance_km_count`, `effort_distance_km_total`
- `effort_area_ha_count`, `effort_area_ha_total`
- `first_observation_date`, `last_observation_date`

The counts of non-null effort fields are intentionally carried alongside the
totals. That lets downstream logic distinguish:

- effort-bearing complete checklists
- complete checklists with weak or zero effort metadata

without having to revisit raw rows.

## 5. Governance files added

- [`wildlifestats/_pipeline/sources/ebird-sampling/DATA_TERMS.md`](C:/Users/Hello/repos/wildlifestats-org/wildlifestats/_pipeline/sources/ebird-sampling/DATA_TERMS.md)
- [`wildlifestats/_pipeline/sources/ebird-sampling/provenance.yml`](C:/Users/Hello/repos/wildlifestats-org/wildlifestats/_pipeline/sources/ebird-sampling/provenance.yml)
- [`docs/handoff/WO-2026-06-16-wls-ebird-sampling-denominator-pilot-results.yml`](C:/Users/Hello/repos/wildlifestats-org/docs/handoff/WO-2026-06-16-wls-ebird-sampling-denominator-pilot-results.yml)

## 6. Run result

Full streaming pass results:

- rows scanned: `169,201,908`
- retained Virginia complete checklists: `2,271,631`
- aggregate output rows: `201,582`
- observation date range: `1934-06-05` through `2026-05-31`
- output csv sha256:
  `553f847986b3a39145b7308987fe02eb4bcee15fbf68b28a536a36c0525847f2`

Top protocols by retained checklist count:

1. `Traveling` — `1,368,328`
2. `Stationary` — `786,850`
3. `Incidental` — `60,745`
4. `Historical` — `31,649`
5. `Area` — `19,139`

Top counties by retained checklist count:

1. `US-VA-059` / Fairfax — `296,917`
2. `US-VA-810` / Virginia Beach — `116,430`
3. `US-VA-001` / Accomack — `89,686`
4. `US-VA-153` / Prince William — `84,464`
5. `US-VA-107` / Loudoun — `79,085`

## 7. What the pilot surfaced

Two tails matter:

1. **County-blank records exist, but barely.** Only `30` retained checklists
   land in a blank-county bucket (`23` aggregate rows). I kept them rather than
   silently dropping them.
2. **Complete does not always mean effort-bearing.** `72,345` retained
   checklists have zero populated duration, distance, and area fields. That
   tail is driven mostly by:
   - `Incidental` (`60,745`)
   - `Historical` (`31,649`)

That is not a bug in the pilot. It is a real denominator decision for the next
step:

- use all complete checklists as a broad sampling denominator, or
- restrict the denominator to effort-bearing protocols for a stricter signal
  model

## 8. Verification

- Offline test:
  `$env:PYTHONPATH='.'; python wildlifestats/_pipeline/ebird_sampling/test_pilot.py`
- Full archive pass:
  `$env:PYTHONPATH='.'; python wildlifestats/_pipeline/ebird_sampling/pilot.py --archive 'C:/Users/Hello/Downloads/ebd_sampling_relMay-2026.tar'`

## 9. Recommended next step

Do not jump straight from this pilot into multi-state production ingest.

The next bounded decision should be one of:

1. lock the denominator policy to `Traveling + Stationary + Area` only
2. keep all complete checklists but flag `Incidental/Historical` as low-trust
   denominator strata
3. add a Virginia-only species-level numerator pilot on top of this weekly
   denominator layer

My view: option `2` is the better first follow-on because it preserves the
full record of what eBird says while still making the low-effort tail explicit.

