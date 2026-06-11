# Engineer Order — Phase 8: National Rehab-Center Directory + Form 990 Pipeline

**To:** soar-aspen-beryl-heron (engineer seat)
**From:** measured-fern-jasper-thrush (architect seat)
**Date:** 2026-06-11
**Branch convention:** `engineer/phase8-*`
**Self-merge authorization:** §13/§14 standing (no architect ratification needed for typical sub-PRs)
**Mike authorization:** Standing — D1 / D2 / D3 ratified 2026-06-11 ("we can scrape their 990 data for the non profits as well... so yes yes yes"). National 100x scale ratified ("all the info we got for BRWC we need to 100x it").

---

## 0. Scope at a glance

Phase 8 lifts WildlifeStats from a Mike-curated Flyway pilot into a **national reference framework** for US wildlife rehabilitation. It has three independent sub-phases:

- **Phase 8a — Directory + per-org pages (SHIPPED by architect this commit)**
  Static `/centers/` directory rendered from `wildlifestats/_pipeline/sources/rehab-centers/centers.yaml` (177 orgs, 161 EINs, 49 states + DC). National landing, 49 state index pages, 177 org profiles. No engineer action required — included here for context.

- **Phase 8b — Form 990 financial ingestion pipeline**
  Implement the spec at `docs/handoff/wildlifestats-form990-ingestion-spec-2026-06-11.md`. Pulls structured 990 data for the 161 EIN-verified centers from ProPublica primary + IRS S3 XML fallback, normalizes into the canonical schema, surfaces a sector-aggregate Financials page and per-org financial section.

- **Phase 8c — Content harvester for per-org enrichment**
  Per-org structured content extraction from each center's public surface (wildlife-help page, about page, news/blog, social): species coverage, intake protocols, mission, leadership, partner orgs. Output: per-org JSON dossiers that enrich the existing static profile pages and feed the per-species "where to take it" guidance in Wildlife911.

This order dispatches **Phase 8b and 8c in parallel**. Both have clean data inputs (centers.yaml is the join key) and disjoint output surfaces (financials section vs. content section on the org profile).

---

## 1. Inputs you already have

```
wildlifestats/_pipeline/sources/rehab-centers/centers.yaml
  └─ 177 orgs, 161 EINs, 49 states + DC. Sorted by state then slug.

docs/handoff/wildlifestats-form990-ingestion-spec-2026-06-11.md
  └─ 5,017-word implementable spec. Read this before Phase 8b.

docs/research/authoritative-sources/
  ├─ 01-state-agencies.yaml         (all 51 jurisdictions)
  ├─ 02-university-extension.yaml   (29 programs)
  └─ 03-professional-handbooks.yaml (41 entries)

docs/research/rehab-registry-sources/
  └─ 01-05 regional research files (source-of-record for centers.yaml)

assets/css/centers.css              (directory styling — already wired)

centers/                            (227 rendered HTML pages — already live)
```

Each org in `centers.yaml` has a stable `slug` (`{state-lower}-{kebab-name}` per the directory URL contract) and an `ein` (where verified). These are the **join keys** for both downstream pipelines.

---

## 2. Phase 8b — Form 990 financial ingestion

### 2.1 Branch and PR structure

Suggested sub-PR sequencing (each can self-merge per §14):

| Sub-PR | Scope | Output |
|---|---|---|
| 8b.1 | ProPublica fetcher + on-disk cache | `wildlifestats/_pipeline/form990/fetch_propublica.py`, `data/_cache/propublica/*.json` (gitignored) |
| 8b.2 | IRS S3 XML fallback for `filings_without_data` | `wildlifestats/_pipeline/form990/fetch_irs_xml.py` |
| 8b.3 | Schema normalizer (IRS field → canonical field) | `wildlifestats/_pipeline/form990/normalize.py`, `wildlifestats/_pipeline/form990/schema.yaml` |
| 8b.4 | Aggregator: per-org filing series + sector aggregates | `wildlifestats/_build/form990/orgs/<ein>.json` + `wildlifestats/_build/form990/sector_aggregate.json` |
| 8b.5 | Public surface: per-org financial section renderer | Re-render of `/centers/<state>/<slug>/` to fill the `org-financials` block |
| 8b.6 | Public surface: sector Financials page | `/centers/financials/index.html` — sector-level revenue/expense/compensation distributions, with downloadable CSV |

### 2.2 Implementation notes (non-negotiable)

- **Pipeline isolation.** Phase 8b lives at `wildlifestats/_pipeline/form990/`. It does **not** import, copy, or fork anything from `askoak/moa-pipeline`. MOA's pipeline is reference architecture, not a code dependency. The 990 spec §10 lists the architectural primitives that may be informed by MOA — read it before writing the normalizer.
- **No PII surface.** ProPublica returns names of officers; those are public-record per Schedule J Part II. Surface them per the spec §6 (compensation benchmarking). Do not collect, store, or surface anything beyond what is in the source 990.
- **Caching is mandatory.** ProPublica JSON responses MUST be cached to `data/_cache/propublica/<ein>.json` keyed by EIN, with a 7-day TTL and an `If-Modified-Since`-style etag header captured in the cache envelope. We will not re-hit ProPublica every CI run.
- **Request spacing 250ms.** Per spec §1.1.1. Backoff to 5s + retry on any non-200.
- **EIN gaps are first-class.** 16 of 177 orgs are not EIN-verified. The renderer must show a "Form 990 financial data: not available — small-filer (likely 990-N e-Postcard)" badge on those org profiles. Do not silently omit.
- **Sector aggregate honors the EIN-verified subset only.** Footnote: "Sector aggregates reflect 161 EIN-verified orgs. 16 small-filer organizations excluded from financial aggregation."

### 2.3 Compensation benchmarking — surface design

Per Mike's D3 ratification ("compensation surfaced as benchmarking tool for centers"):

- Per-org page: ED, CEO, and Medical Director compensation (Schedule J Part II line 1 columns B(i)/B(ii)/B(iii) summed) when reported.
- Sector page: percentile distributions (p25/p50/p75/p90) of (a) total ED compensation, (b) total ED comp as % of total expenses, (c) total functional expenses, (d) revenue per intake (only for orgs where intake counts are independently available — do not invent intake counts from financials).
- **Downloadable CSV** at `/centers/financials/sector-aggregate.csv` — the actual reason centers will use the framework. Columns documented in `/centers/financials/schema.html`.

### 2.4 Tests

- `wildlifestats/_pipeline/form990/test_normalize.py` — golden-record test: feed a known ProPublica response (committed to `tests/fixtures/`), assert canonical output matches checked-in expected JSON.
- `wildlifestats/_pipeline/form990/test_fallback.py` — 410 / 404 from ProPublica triggers S3 XML fallback path.
- CI gate: `make form990-build` must be deterministic — same inputs in, byte-identical outputs out.

### 2.5 Out of scope for Phase 8b

- Candid / GuideStar API (cost + ToS make it untenable for a public framework; spec §1.2)
- Schedule O narrative parsing (defer to a later phase if there's signal demand)
- IRS Business Master File enrichment (defer; ProPublica + S3 XML cover what we need)

---

## 3. Phase 8c — Content harvester

### 3.1 Branch and PR structure

| Sub-PR | Scope | Output |
|---|---|---|
| 8c.1 | Per-org fetcher: pulls primary_url, about_url, contact_url, news_or_blog_url with polite rate-limiting + robots.txt respect | `wildlifestats/_pipeline/content/fetch_org_pages.py` |
| 8c.2 | LLM-assisted extractor: mission, species list, intake protocols, leadership, partnerships, accreditations | `wildlifestats/_pipeline/content/extract_org_dossier.py` → `wildlifestats/_build/centers/<ein-or-slug>.json` |
| 8c.3 | Re-render org profile pages with enriched content sections | Updates to `wildlifestats/_pipeline/sources/rehab-centers/render_directory.py` |
| 8c.4 | Cross-link from Wildlife911 species pages: per-species "Where to take it in your state" using `accepts_species` flags | Updates to Wildlife911 species page renderer |

### 3.2 Non-negotiables

- **Robots-aware.** Every fetch consults the target site's `robots.txt`. If disallowed, skip and log. Do not bypass.
- **Cite the source URL inline on every extracted claim** in the rendered profile. Surface attribution as `Source: <a href="...">center.org/about</a>` after each enriched section. Per Mike: outputs should reflect "transparent reasoning over black-box conclusions."
- **Mission text quoted, not paraphrased.** If you extract a mission statement, quote it verbatim with a source link. If the source is unavailable, omit. Do not write missions on a center's behalf.
- **Newsletter signup URLs surface as opt-in CTAs**, not lead-gen. This is a research framework, not a partnership funnel.
- **BRWC content guard.** `bash scripts/check-no-brwc.sh` runs on every PR. The narrowed guard catches raw-record artifacts only — brand mentions are fine. If your harvester pulls a BRWC page, treat the extracted public content the same as any peer center's; do not pull from BRWC's internal Supabase or any non-public surface.
- **Snapshot dating.** Every dossier JSON envelope includes `fetched_at` (ISO 8601) and `source_etag` where available. Surface "Last verified: YYYY-MM-DD" on each profile section so stale content is visible.

### 3.3 Model selection

Use the cheapest extraction-grade LLM available via the project's existing AI plumbing. This pipeline is bulk + batchable; latency does not matter. Per Mike's economics: do not burn budget on flagship models for what is, structurally, a structured-extraction task.

### 3.4 Out of scope for Phase 8c

- Social media post bulk-pulls (defer to Phase 4.5+f-j Flyway pipeline, which is already queued)
- Image scraping (text-only for this phase)
- PDF annual report extraction (separate phase — annual reports often run 30-page narratives that warrant their own pipeline)
- Translation / multilingual surfaces

---

## 4. Coordination with already-queued work

Your queue currently includes:

- Phase 4.5+g-j Flyway smoke test + social pipeline (Mike has authorized the smoke test)
- Phase 5a-j secure tier
- Phase 7a-g WREN + Wildlife911 pill
- Phase 4.6c sharded cube regen
- Phase 4.6f schema v1.2

Phase 8b and 8c **do not block** any of the above. They have disjoint code surfaces. Sequence as you see fit per §13.

If priority sequencing is unclear, the architect's preferred order is:

1. Phase 4.5+g (Flyway smoke test — Mike has authorized)
2. Phase 8b.1 + 8b.2 + 8b.3 (the 990 fetcher chain — high signal for institutional credibility)
3. Phase 7a-c (WREN base — unblocks the Wildlife911 chat pill)
4. Phase 8c.1 + 8c.2 (content harvester — depends only on centers.yaml, no blockers)

This is preference, not direction.

---

## 5. Acceptance criteria — what "shipped" looks like

**Phase 8b shipped:**
- `/centers/financials/` page is live with sector-level revenue / expense / compensation distributions
- 161 EIN-verified org profile pages have a populated `org-financials` section with 3+ years of filing summary where available
- Sector aggregate CSV is downloadable
- Compensation percentiles render with footnotes citing IRS Schedule J Part II
- `make form990-build` is deterministic
- 16 non-EIN orgs show the "small-filer" badge

**Phase 8c shipped:**
- 177 org profile pages have an enriched `org-mission`, `org-services`, `org-contact`, `org-resources` block where source pages permitted extraction
- Each enriched section cites its source URL
- Wildlife911 species pages link out to per-state center directories filtered by `accepts_species`
- Every dossier shows a "Last verified" date
- Content guard passes

---

## 6. Escalate to architect if

- ProPublica API materially changes (new auth requirement, breaking schema change)
- IRS S3 XML schema changes for FY2024+ filings in a way the spec didn't anticipate
- A center's robots.txt unexpectedly blocks all content extraction across most of the registry (>20% blocked → architectural decision needed)
- Content guard catches a legitimate reference and you're unsure whether to narrow the pattern or move the file

Open a CROSS-LANE note in `docs/handoff/` for these; the architect will adjudicate within one wake cycle.

---

## 7. Closing line

Phase 8a is shipped this commit. Phase 8b and 8c are dispatched. The architect's queue is empty.

— measured-fern-jasper-thrush, 2026-06-11
