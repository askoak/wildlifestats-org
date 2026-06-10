# Engineer order — Phase 4.5: data pipeline

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer (`soar-aspen-beryl-heron`)
**Date:** 2026-06-10 ~15:23 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Phase 4 sub-PRs all complete)
**Authority:** §13 + §14.

## Source of truth

`docs/handoff/wildlifestats-data-pipeline-spec-phase4.5-2026-06-10.md`. Every architectural choice is there.

## Scope (one PR per stage; five PRs total)

| Sub-PR | Stages | Effort |
|---|---|---|
| 4.5a | Inventory + schema inference (`inventory.py`, `schema_inference.py`) + samples committed | ~2 hours |
| 4.5b | Field mapping + value normalization (`field_mapping.py`, `normalize.py`, alias tables) | ~half day |
| 4.5c | Validation + audit log (`validate.py`, `audit.py`) | ~2 hours |
| 4.5d | Aggregation + partner cube emission (`aggregate.py`, runner `run.py`) | ~half day |
| 4.5e | CI dry-run job + `/ingest/` page rewrite to use real pipeline outputs | ~2 hours |

Each sub-PR self-merges per §14 once CI is green.

## Acceptance criteria (cumulative across sub-PRs)

By end of Phase 4.5:

1. `python wildlifestats/_pipeline/run.py --input samples/partners/ --mapping samples/partners/sample-mapping.json --out /tmp/test-cube.json` completes without error.
2. The output cube has the same shape as `data/cube/admissions-cube.json` plus the additional dimensions in spec §2.7.
3. Audit log at `_work/audit-log.jsonl` is populated with at least one entry per record.
4. Validation failures land in `_work/validation-failures.json` rather than silently dropping.
5. The `/ingest/` page on the live site shows the eight pipeline stages, sample inputs, sample outputs, and a downloadable archive.
6. CI's new `pipeline-dry-run` job passes green.
7. BRWC content guard passes — no partner sample, no mapping file, no audit log entry mentions BRWC, Blue Ridge, Clarke County, Jen Riley, etc.
8. The pipeline is deterministic: running twice on the same input + mapping produces byte-identical output (modulo timestamps in the audit log, which are clamped to a deterministic value when `WILDLIFESTATS_DETERMINISTIC=1` env var is set, used in CI).

## Commit and merge

- Five branches: `engineer/phase4.5a-inventory`, `engineer/phase4.5b-normalize`, `engineer/phase4.5c-validate`, `engineer/phase4.5d-aggregate`, `engineer/phase4.5e-ingest-page`.
- Commits: `data(wildlifestats): pipeline stage <N> — <stage name>`. Trailer: `Engineer: soar-aspen-beryl-heron`.
- Self-merge per §14 after CI green.
- After each merge, append a one-line `## Resolution` entry to this file noting the merge commit. When all five sub-PRs are merged, move this file to `closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 15:23 ET

## Resolution log (engineer `soar-aspen-beryl-heron`)
- **4.5a — inventory + schema inference** — SHIPPED. PR #17, merged `b3c467f`. inventory.py + schema_inference.py (csv/json/xlsx), 3 heterogeneous sample partner files, `_work/` gitignored, deterministic under WILDLIFESTATS_DETERMINISTIC=1. NEXT: 4.5b field mapping + normalize.
