# Data pipeline architecture spec — Phase 4.5

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 15:23 ET
**Status:** Source of truth for the Phase 4.5 engineer order.
**Replaces:** the Phase 4 "ingestion sandbox" sub-PR is elevated to a full phase per Mike's 2026-06-10 15:23 ET directive.

## §1 — Goal

Build a real data pipeline that ingests heterogeneous wildlife rehabilitation records from partner centers, cleans them, validates them, audits the transformations, and emits a partner cube that uses the same schema as the synthetic cube.

This is the infrastructure that makes the "10,000 Excel files" story credible. It is also the prerequisite for secure WREN (Phase 7f).

## §2 — Pipeline stages

```
[Source files: .xlsx, .csv, .json] 
  → 1. Inventory
  → 2. Schema inference
  → 3. Field mapping
  → 4. Value normalization (species, dates, outcomes)
  → 5. Validation
  → 6. Audit log
  → 7. Aggregation
  → 8. Partner cube emission
```

Each stage is a Python module under `wildlifestats/_pipeline/`. Each stage produces a versioned artifact under `wildlifestats/_pipeline/_work/` (gitignored). The final emission (the partner cube) lands under `secure/cube/partner-records.json` (committed to a secure-only branch or stored outside the repo — see §9 below).

### §2.1 Inventory

`inventory.py` walks an input directory and produces `_work/inventory.json` — one record per file:

```json
{
  "path": "samples/center-a/2024-admissions.xlsx",
  "sha256": "abc123...",
  "size_bytes": 124680,
  "rows_estimate": 312,
  "format": "xlsx",
  "discovered_at": "2026-06-10T19:23:00Z"
}
```

### §2.2 Schema inference

`schema_inference.py` opens each file, reads the header row, and infers column types. Produces `_work/schemas/<file-hash>.json` — one schema per file. Includes column name, inferred dtype, fraction non-null, sample values.

### §2.3 Field mapping

`field_mapping.py` maps source columns to canonical WildlifeStats columns. The mapping is **declared, not inferred** for the first pass — partner files have varied enough headers that a configuration file is the right model:

```json
// wildlifestats/_pipeline/mappings/center-a.json
{
  "partner_id": "center-a",
  "source_format": "xlsx",
  "field_map": {
    "Patient ID": "intake_id",
    "Date In": "intake_date",
    "Animal": "species_raw",
    "Reason for Admission": "reason_raw",
    "Outcome": "outcome_raw",
    "Disposition": "disposition_raw"
  },
  "row_skip": 1,
  "sheet_name": null
}
```

Architect default: each partner gets a mapping file. The pipeline supports an `--infer-mapping` flag for the schema-inference run, which proposes a mapping for human review — but doesn't apply it without commit.

### §2.4 Value normalization

`normalize.py` applies four transformations:

1. **Species normalization.** `species_raw` (free-text common name) → `species_canonical` (a stable identifier from `wildlifestats/_build/species-archetypes.json`). Uses a fuzzy-match table at `wildlifestats/_pipeline/species-aliases.json`. Unmatched species land as `species_canonical = "unknown"` with `species_raw` preserved in the audit log.
2. **Date normalization.** `intake_date` parsed via multiple format attempts (US: MM/DD/YYYY, EU: DD/MM/YYYY, ISO: YYYY-MM-DD, Excel serial). Year, month extracted. Out-of-range dates (before 2000 or after current year + 1) land as `intake_date = null` with the raw value preserved.
3. **Reason / outcome normalization.** Maps partner free-text values to the canonical enumeration in `wildlifestats-synthetic-cube-spec-phase3-2026-06-10.md` §2. Mapping table at `wildlifestats/_pipeline/value-aliases.json`. Unmapped values default to `unknown` with the raw value preserved.
4. **County resolution.** If the source has city or zip, look up county via a committed lookup table at `wildlifestats/_pipeline/zip-to-fips.json`. If no geographic info, county defaults to `unknown_in_state` for the partner's home state.

### §2.5 Validation

`validate.py` runs checks against the normalized records:

- Intake date is not in the future
- Outcome is one of the canonical values
- Species canonical is in the archetypes file OR is `unknown`
- For each record, count appears exactly once (no duplicate intake_ids per partner)

Failed records are NOT dropped silently — they're written to `_work/validation-failures.json` with the row index and the failure reason. The pipeline continues. The audit log captures the count.

### §2.6 Audit log

`audit.py` writes `_work/audit-log.jsonl` — one JSON line per record:

```json
{"record_id": "center-a:1234", "stage": "normalize", "field": "species", "raw": "RT Hawk", "canonical": "raptor_diurnal", "match_method": "alias_table", "timestamp": "..."}
```

This log is the provenance trail. Every transformation on every field is logged. The audit log is the artifact a researcher cites when asking "where did this number come from."

### §2.7 Aggregation

`aggregate.py` rolls up the normalized records into a partner cube with the same schema as the synthetic cube (per Phase 3 spec §2), plus three additional dimensions:

- `partner_id` (the source center)
- `record_count_redacted_under_k` (number of source records collapsed into this cell when k-suppression applies)
- `data_freshness_date` (latest intake_date in the cell)

### §2.8 Partner cube emission

Writes `secure/cube/partner-records.json` — same shape as `data/cube/admissions-cube.json` but with the additional dimensions. This file is the input to secure WREN.

## §3 — Pipeline runner

`wildlifestats/_pipeline/run.py` is the single entry point:

```bash
python wildlifestats/_pipeline/run.py \
  --input partner-data/center-a/ \
  --mapping wildlifestats/_pipeline/mappings/center-a.json \
  --out secure/cube/partner-records.json
```

Runs all eight stages in order. Each stage is idempotent given the same input. Same input + same mapping = byte-identical output.

The runner accepts `--stages` to run a subset (e.g., `--stages inventory,schema_inference` for the dry-run pass).

## §4 — Sample partner files

For the public ingestion methodology demo (Phase 4 `/ingest/`), the engineer creates 3–5 sample partner files under `samples/partners/` — fictional center names, fictional records, deliberately heterogeneous schemas. The pipeline runs against these samples for the demo.

The samples are committed. They contain only synthetic records derived from the regional archetypes — no real partner data.

## §5 — k-suppression at aggregation time

The partner cube applies k-suppression at aggregation, not at query time. Any (year, month, county, species, reason) cell with fewer than 10 source records is collapsed to a "<k" placeholder cell with `n = "<k"` and `record_count_redacted_under_k = <actual count>`.

This is privacy-by-build per §5 of Standing Orders. The pipeline does not produce a partner cube with raw small-cell counts; it produces a privacy-safe partner cube that is the only artifact secure WREN ever reads.

Authenticated users with a "partner admin" role may eventually be granted access to a separate un-suppressed view via a future engineer order. Not in Phase 4.5 scope.

## §6 — CI integration

`.github/workflows/validate.yml` gains a fifth job: `pipeline-dry-run`.

- Runs `python wildlifestats/_pipeline/run.py --input samples/partners/ --mapping samples/partners/sample-mapping.json --stages inventory,schema_inference,validate`
- Asserts the inventory file is produced
- Asserts no validation errors above a threshold (e.g., < 5% records failing validation on the samples)
- Does NOT emit the partner cube in CI — partner cube emission happens manually with real data on a workstation, not in CI.

## §7 — What is NOT in Phase 4.5

- Live partner data ingestion (we don't have any yet). Phase 4.5 ships the pipeline + the samples + the methodology demo on `/ingest/`. Real partner data arrives later.
- A web UI for ingestion (deferred — Mike or an engineer runs the CLI when real data arrives).
- Versioning of partner mappings beyond git (deferred — git is enough until partners exist).
- Differential privacy beyond k-suppression (deferred — k-suppression matches BRWC privacy discipline; stronger tools when partner accounts arrive).
- Database storage (deferred — JSON files are sufficient for the cube sizes WildlifeStats will see in the foreseeable future).

## §8 — Relationship to Phase 4 `/ingest/` page

The Phase 4 `/ingest/` engineer order was originally a methodology-demo page only. Now it becomes the **public face of the Phase 4.5 pipeline**. The page:

- Explains the eight pipeline stages in plain English
- Shows the sample input files (raw)
- Shows the canonical mappings applied
- Shows the partner cube output (suppressed)
- Provides a downloadable archive of the sample input + outputs so a researcher can audit the methodology

The page is *not* a live ingestion tool. It is a transparent walkthrough of the pipeline's behavior on committed samples.

## §9 — Storage of the partner cube (`secure/cube/partner-records.json`)

Open question: where does the partner cube file live?

**Option A:** Committed to the repo at `secure/cube/`. Convenient; works with Netlify's basic-auth at `/secure/*`. Risk: if a partner ever delivers a non-synthetic file with sensitive records, that file's residue lives in git history.

**Option B:** Stored outside the repo (Mike's OneDrive or an S3 bucket). Engineer fetches it at deploy time via a Netlify build hook with a credential. Cleaner separation; more moving parts.

**Architect default:** Option A for the samples + the Phase 4.5 demo (the records are synthetic). Switch to Option B when a real partner delivers real data. The pipeline's emission target (`--out`) is a CLI flag, so both options work with the same code; the deploy plumbing differs only.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 15:23 ET
