# Engineer Order — Phase 9: Multi-Source Ingestion Framework

**To:** soar-aspen-beryl-heron (engineer seat)
**From:** measured-fern-jasper-thrush (architect seat)
**Date:** 2026-06-11 11:30 ET
**Branch convention:** `engineer/phase9-bucket-NN-*`
**Self-merge authorization:** §13/§14 standing per sub-PR
**Mike authorizations standing:**
- Decision A (Apify two-tier strategy) — ratified 2026-06-11
- Decision B (parallel research dispatch) — delivered in PR #35
- Decision C (single Supabase project with RLS) — ratified 2026-06-11
- Decision D (parallel A-E research dispatch) — delivered in PR #35
- D1 / D2 / D3 (firm profile + 990 + compensation surfacing) — ratified 2026-06-11

---

## 0. Scope at a glance

Phase 9 restructures the WildlifeStats data pipeline into a **multi-source ingestion framework** with disciplined bucket taxonomy. Source-of-truth registries are already in place (delivered in PRs #32 and #35); shared infrastructure is scaffolded (this PR). What remains is the per-bucket implementation.

The framework axis is **organization type × data bucket**, not state. The state-by-state slicing is a research method, not a database axis (Mike's framing 2026-06-11). For each of 357 target organization classes (51 jurisdictions × 7 archetypes), the framework maintains 10 data buckets.

### Bucket taxonomy

| # | Bucket | Primary source pattern | Storage schema |
|---|---|---|---|
| 01 | **SOCIAL** | Apify actors (FB, IG, X, TikTok, YouTube) | `wildlifestats_bucket_01_social_signals` |
| 02 | **FIRM PROFILE** | Website + 990 (ProPublica + IRS S3 XML) + annual report PDFs | `wildlifestats_bucket_02_firm_profile` |
| 03 | **PUBLICATIONS** | Exa-discovered canonical URLs → PDF/HTML harvest → text extraction | `wildlifestats_bucket_03_publications` |
| 04 | **HELP-WILDLIFE CONTENT** | Per-species per-center triage pages → Wildlife911 feed | `wildlifestats_bucket_04_help_content` |
| 05 | **RAW RECORDS** | Per-org lane-isolated (BRWC pattern; never crosses lanes) | `wildlifestats_secure_bucket_05_raw_records` |
| 06 | **AGGREGATE** | Computed downstream from 1-5 + 7-10 | `wildlifestats_bucket_06_aggregate` |
| 07 | **REGULATORY** | State agency licensing rosters, USFWS permit holders | `wildlifestats_bucket_07_regulatory` |
| 08 | **MEDIA / ACADEMIC** | Local news + Wiley peer-review (already CONNECTED) | `wildlifestats_bucket_08_media_academic` |
| 09 | **NETWORK** | Derived graph (transfers, board overlap, Apollo enrichment) | `wildlifestats_bucket_09_network` |
| 10 | **EVENTS** | Event pages, Eventbrite, FB Events | `wildlifestats_bucket_10_events` |

---

## 1. Inputs you already have

### Source-of-truth registries (canonical YAML, sorted, validated)

```
wildlifestats/_pipeline/sources/
├── rehab-centers/centers.yaml              181 orgs, 174 EIN-verified
├── state-vet-ag/agencies.yaml              51 jurisdictions
├── statewide-associations/associations.yaml 20 statewide assocs
├── sector-funders/funders.yaml             33 funders
└── usfws-offices/offices.yaml              78 USFWS offices
```

Each entry has a stable `slug` and (where applicable) `ein`. These are the join keys.

### Shared infrastructure (this PR delivers — scaffolded, not implemented)

```
wildlifestats/_pipeline/_common/
├── __init__.py            discipline rules (read first)
├── creds.py               8 typed credential getters
├── fetch.py               robots-aware HTTP with dating envelope
├── exa_client.py          canonical-URL discovery
├── claude_client.py       structured extraction
├── apify_client.py        social orchestration (refactor Flyway POC into here)
├── supabase_client.py     RLS-aware writes
└── test_gates.py          12 discipline-gate smoke tests (12/12 passing)
```

Every scaffold module raises `NotImplementedError` on the actual API call but has live validation gates that fire correctly. Your implementation fills in the TODOs; the gates are non-negotiable and audited by `test_gates.py`.

### CI gates (this PR delivers)

```
.github/workflows/validate.yml adds:
  - credentials-leakage-guard      bash scripts/check-no-credentials.sh
  - common-gates-test              python test_gates.py
```

Plus the existing brwc-content-guard, html-validate (now hardened against regression), link-check, and cube-validate gates.

### Reference specs

- `docs/handoff/wildlifestats-form990-ingestion-spec-2026-06-11.md` — 5,017-word implementable spec for the 990 portion of Bucket 02.
- `wildlifestats/_pipeline/flyway/` — the working Apify POC. Refactor `apify_client.py` into `_common/` per Bucket 01 below.

---

## 2. The §19 RLS contract (non-negotiable)

The Supabase project `oamqicylpytbldrnybcc` is shared between askoak-web (BRWC) and wildlifestats-org (this lane). Per Mike's Decision C (2026-06-11), there is no physical separation; the contract is enforced at schema + RLS level.

### Schema ownership

| Schema prefix | Owner lane | Read access | Write access |
|---|---|---|---|
| `brwc_*` | askoak-web | brwc role | brwc role |
| `wildlifestats_*` | wildlifestats-org | public-tier | wildlifestats role |
| `wildlifestats_secure_*` | wildlifestats-org | wildlifestats role | wildlifestats role |
| `shared_*` | either lane | authenticated (RO from public) | either role |

### Client-side enforcement (already live in scaffold)

`supabase_client.upsert()` raises:
- `CrossLaneViolation` if target_schema starts with `brwc_`, `askoak_`, or `moa_`
- `CrossLaneViolation` if target_schema is not in `WILDLIFESTATS_SCHEMAS`
- `CrossLaneViolation` if a record with `rehab_org_ein == BRWC_EIN` is written to bucket 05
- `MissingProvenance` if a record lacks `fetched_at`, `source_url`, or `content_hash`

### Server-side enforcement (your work in Phase 9b.1)

Apply matching RLS policies via `apply_migration`. Recommended policy shape:

```sql
ALTER TABLE wildlifestats_secure_bucket_05_raw_records.<table>
  ENABLE ROW LEVEL SECURITY;

CREATE POLICY no_brwc_rawrecords ON wildlifestats_secure_bucket_05_raw_records.<table>
  FOR ALL
  TO authenticated
  USING (rehab_org_ein != '54-1641798')
  WITH CHECK (rehab_org_ein != '54-1641798');
```

Both gates required. The client gate alone is not sufficient — a bug or a misconfigured caller must not be able to write a BRWC raw record into the WildlifeStats lane.

---

## 3. Sub-PR sequencing

Recommended order — preserves disjoint code surfaces so multiple buckets can be in flight simultaneously where useful.

### Phase 9a — Foundation (already shipped in this PR)
- 9a.1 Shared `_common/` scaffolding ✅
- 9a.2 CI gates wired (credentials, common-gates-test) ✅
- 9a.3 Engineer order dispatched (this document) ✅

### Phase 9b — Storage layer
- 9b.1 Supabase schemas + RLS policies via `apply_migration` (Supabase MCP)
- 9b.2 `supabase_client.upsert()` implementation against postgrest
- 9b.3 Migration replay test (idempotency)

### Phase 9c — `_common/` implementation
- 9c.1 `fetch.py` — robots + rate-limit + cache + envelope
- 9c.2 `exa_client.py` — Exa Search wrapping
- 9c.3 `claude_client.py` — structured extraction
- 9c.4 `apify_client.py` — refactor Flyway POC into here; add IG/X/TikTok/YouTube
- 9c.5 Integration smoke: each client makes one live call against a single test target; cost + correctness validated

### Phase 9d — Buckets (parallelizable after 9b + 9c)

| Sub-PR | Bucket | Depends on | Notes |
|---|---|---|---|
| 9d.01 | 01 SOCIAL — production | apify_client, claude_client, supabase_client | Inherits Flyway POC validation; gated on Phase 4.5+h trigger validation |
| 9d.02 | 02 FIRM PROFILE — website extract | fetch, claude_client, supabase_client | Per-org dossier with mission, leadership, services, accreditations |
| 9d.02-990 | 02 FIRM PROFILE — 990 ingest | supabase_client | Implements the 990 spec; ProPublica primary + IRS S3 XML fallback |
| 9d.03 | 03 PUBLICATIONS | fetch, exa_client, claude_client, supabase_client | Newsletter + annual report corpus |
| 9d.04 | 04 HELP CONTENT | fetch, claude_client, supabase_client | Per-species per-center matrix; feeds Wildlife911 |
| 9d.05 | 05 RAW RECORDS | supabase_client | Architecturally scaffolded; no per-org records yet (gated on individual org partnerships) |
| 9d.06 | 06 AGGREGATE | all upstream buckets | Sector statistics; Zenodo DOI per release |
| 9d.07 | 07 REGULATORY | fetch, claude_client, supabase_client | Per-jurisdiction licensing rosters |
| 9d.08 | 08 MEDIA / ACADEMIC | fetch, claude_client (Wiley connector already CONNECTED) | Local news + peer-review |
| 9d.09 | 09 NETWORK | bucket 02 + bucket 05 outputs | Apollo.io enrichment for sector funders |
| 9d.10 | 10 EVENTS | fetch, supabase_client | Event/volunteer capacity signals |

### Sub-PR rules

1. **One bucket per PR.** No bundling buckets.
2. **Each PR includes its tests.** Bucket 02 PR includes Bucket 02 tests; not coverage of other buckets.
3. **Each PR documents cost in the description.** Per-org expected $/run + per-month steady-state.
4. **Self-merge per §14 once CI is green** for the standard sub-PR rhythm.
5. **Escalate to architect via CROSS-LANE if** you hit a blocker requiring schema-axis changes (new bucket, lane-discipline edge case, RLS pattern that doesn't fit).

---

## 4. Bucket-specific guidance

### Bucket 01 — SOCIAL (production)

You already validated this in the Flyway POC. Refactor `flyway/apify_client.py` into `_common/apify_client.py` per the scaffold; extend from FB+IG to all 5 platforms; switch the production extraction path from your standin-extractor to `claude_client.extract_structured` via `custom-cred:api.anthropic.com`.

**Two-tier orchestration** per Decision A:
- Tier 1: 50 priority centers (largest by intake/revenue from centers.yaml). Full backfill on first run; monthly refresh.
- Tier 2: 131 long-tail centers. Trailing 90-day window; quarterly refresh.

Identify the 50 priority centers from the `typical_annual_intake` field where available; for orgs with that field empty, fall back to ProPublica revenue (you have ein for 174/181 orgs). Surface the methodology in the PR description.

**Daily cron stays DISABLED until Mike authorizes the recurring spend** — gated on Phase 4.5+h trigger validation, which is currently dispatched.

### Bucket 02 — FIRM PROFILE

Two halves shipping independently:

**Website extract (9d.02):** per-org content harvester. For each of the 181 orgs:
- Fetch `about_url`, `contact_url`, `wildlife_help_url`, `news_or_blog_url`, `annual_reports_url` (already populated in centers.yaml for many orgs).
- Extract via Claude into a structured dossier: mission (quoted, not paraphrased — defensive check in `claude_client`), leadership names + titles, services offered, accreditations, partnerships, contact info.
- Write to `wildlifestats_bucket_02_firm_profile.orgs` keyed by `slug` + `fetched_at`.
- Render the resulting dossier into the existing per-org profile pages at `/centers/<state>/<slug>/`. Re-run `render_directory.py` to refresh.

**990 ingest (9d.02-990):** implements the 990 spec at `docs/handoff/wildlifestats-form990-ingestion-spec-2026-06-11.md`. 161+ EIN-verified orgs; ProPublica API primary, IRS S3 XML fallback. Sector aggregate at `/centers/financials/`. Schedule J compensation surfacing per D3.

### Bucket 03 — PUBLICATIONS

For each org, find canonical URLs for newsletter archive + annual report archive + publications index via `exa_client.find_canonical_url`. Validate each candidate via `fetch.fetch()`. Harvest text content from validated URLs.

Per-doc record includes: source_url, fetched_at, content_hash, doc_type, doc_title, doc_date, full_text (yes — these are public documents that orgs publish to their own websites; full text storage is appropriate). Voyage embeddings populate a vector column for similarity search.

### Bucket 04 — HELP-WILDLIFE CONTENT

Per-species per-center triage content. Input: each org's `wildlife_help_url`. Extract per-species protocols (what to do if you find an injured deer fawn, hummingbird, opossum, etc.) and capture which species each center accepts. Output: a species × center matrix that feeds Wildlife911's per-species "Where to take it in your state" guidance.

Cross-references with `services` flags already in centers.yaml — those flags become the join key.

### Bucket 05 — RAW RECORDS

Architectural scaffolding only in Phase 9. No per-org records are ingested in this phase. Individual orgs that grant data-sharing permission populate this bucket in future phases under per-org data-sharing agreements; the §19 BRWC-EIN guard ensures that lane never crosses into the WildlifeStats raw records bucket.

What ships in 9d.05:
- The table definitions for what a raw-record schema looks like (intake_id, intake_date, species, age_class, presenting_condition, disposition, etc. — modeled after the rehab-sector standard fields).
- The RLS policies enforcing per-org access (which Supabase user can read which org's raw records).
- A `partner_orgs` table tracking which orgs have signed data-sharing agreements and their current data-share status.

No actual records.

### Bucket 06 — AGGREGATE

Computed from buckets 01-05 + 07-10. Sector statistics published as:
- A `/centers/financials/` page (already specced in the 990 spec).
- A `/sector/` page with cross-cutting metrics (intake volume by state, species coverage by state, sector capacity trends).
- A downloadable CSV per major aggregate.
- A Zenodo DOI per quarterly release.

Excludes BRWC raw records from any per-org breakdown. Aggregate-level metrics derived from public 990s include BRWC like every other center.

### Bucket 07 — REGULATORY

Per-jurisdiction licensing rosters. Source: each state's `wildlife_disease_program_url` and rehabber-directory URL (where published) from `state-vet-ag/agencies.yaml`. Many states do not publish a public rehabber directory — flag those as `roster_publicly_available: false`. Where rosters exist, harvest them; join to centers.yaml by org name + state for license verification.

This is the "is this org actually licensed?" join. Surface a `license_verified` badge on each org profile.

### Bucket 08 — MEDIA / ACADEMIC

Two sub-buckets:

**Local news / media mentions:** Per-org search via web search APIs. Mention count + sentiment + recency feed into a per-org "sector visibility" metric.

**Academic / peer-review:** The Wiley connector is already CONNECTED (`search_publications`). Bulk-search per-state and per-species for wildlife rehabilitation research; cross-reference with sector funders (a research grant funded by NFWF citing data from a member center).

### Bucket 09 — NETWORK

Derived graph from buckets 02, 05, and Apollo.io enrichment:
- Org → org transfer edges (from raw records where available + from public news of transfers)
- Org → org board overlap (from 990 Schedule O + Apollo enrichment)
- Org → funder edges (from 990 Schedule I + sector-funders.yaml)

Surfaced as a `/sector/network/` interactive visualization (defer the viz to a separate phase; this PR builds the graph).

### Bucket 10 — EVENTS

Per-org event/volunteer signals. Source: each org's events page, plus Eventbrite + FB Events API search by org name. Volume of events + volunteer training cohorts is a structural capacity signal (a center running 12 volunteer cohorts/year is structurally different from one running zero).

---

## 5. Operational discipline

### Cost surfacing

Every PR description includes a per-bucket cost table:

| Item | Est. $ per run | Est. $ per month steady-state |
|---|---|---|
| Apify (Tier 1, 50 orgs × 5 platforms × monthly) | — | — |
| Apify (Tier 2, 131 orgs × 5 platforms × quarterly) | — | — |
| Claude (extraction per org per refresh) | — | — |
| Exa (canonical URL discovery, one-time per org) | — | — |
| Voyage (embeddings, one-time + per new doc) | — | — |
| Supabase (storage, ~$25/month at small scale) | — | — |

Mike's spend authorizations are per-bucket. Do not assume a global spend cap.

### Robots respect

Every fetch routes through `_common/fetch.py`. The framework's reputation with the orgs we research is non-renewable; one publicly visible violation is a permanent reputational tax on every future partnership conversation.

### Provenance discipline

Every record carries `fetched_at`, `source_url`, `content_hash`. Every rendered surface cites its source URL inline. Records missing the envelope are rejected client-side by `supabase_client.upsert()`.

### LLM source-of-truth discipline

`claude_client.extract_structured` enforces:
- Quote, do not paraphrase, for mission statements and similar identity-statement content.
- Every claim cites its source URL inline.
- Fields are left null when the source doesn't say.

These are codified in the scaffold; do not relax them in implementation.

---

## 6. Acceptance criteria — what "Phase 9 shipped" looks like

- All 10 buckets have a live ingestion pipeline.
- All 181 centers have a Bucket 02 dossier with mission, leadership, services, contact info, all citing sources.
- 161+ EIN-verified centers have Bucket 02-990 financial data with 3+ years of filing summary.
- Bucket 06 publishes a quarterly sector-aggregate dataset with a Zenodo DOI.
- Every bucket's test_gates suite is green in CI.
- BRWC content guard PASSES across the entire repo.
- Credentials leakage guard PASSES.
- html-validate gate stays green.

---

## 7. Escalate to architect via CROSS-LANE if

- A bucket's data shape forces a schema-axis change (new bucket, new owner lane, RLS pattern that doesn't fit)
- A source's robots.txt or ToS makes the bucket unviable at scale (>20% of orgs blocked)
- A credential rotation breaks more than one bucket
- A vendor (Apify, Exa, Anthropic) materially changes pricing or schema
- A new partner org wants raw-record sharing (Bucket 05 — this is a Mike conversation, not engineer's call)

Otherwise: §13/§14 standing. Self-merge per sub-PR.

---

## 8. Closing line

This order dispatches Phase 9. Architect's queue is now empty for the framework. Next architect surface comes from:
- A research output that needs ratification (you ship a sub-PR, architect ratifies)
- A CROSS-LANE escalation (architect adjudicates within one wake cycle)
- A Mike directive (architect routes)

— measured-fern-jasper-thrush, 2026-06-11 11:30 ET
