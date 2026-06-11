# Form 990 Ingestion Pipeline — Architecture Specification
**WildlifeStats Research Framework · PR 8b**
**Status:** Draft v1.0 · 2026-06-11
**Author:** WildlifeStats Architecture
**Separation notice:** This specification describes a wholly independent pipeline at `wildlifestats/_pipeline/form990/`. It is architecturally informed by, but does not copy, the MOA 990 pipeline. MOA IP stays in MOA's repo. See §10 (Reference Architecture Notes).

---

## Table of Contents

1. Data Source Architecture
2. Pipeline Architecture
3. Output Schema
4. Public Surface Design
5. Sector Aggregate Metrics
6. Compensation Benchmarking Spec
7. Data Freshness and Update Cadence
8. Audit Trail
9. License + ToS Posture
10. Phasing (Sub-PRs)
11. Reference Architecture Notes

---

## 1. Data Source Architecture

### 1.1 The Three Sources

IRS Form 990 data is publicly available via three primary distribution channels, each with distinct tradeoffs.

#### 1.1.1 ProPublica Nonprofit Explorer API

**Base URL:** `https://projects.propublica.org/nonprofits/api/v2`

ProPublica's API exposes normalized JSON records keyed by EIN. Two endpoints are relevant:

- `GET /organizations/:ein.json` — Returns the full organization profile plus an array of `filings_with_data` (structured financial data) and `filings_without_data` (PDF-only references where machine-readable data is unavailable). This is the primary fetch target for the WildlifeStats pipeline.
- `GET /search.json` — Keyword/state/NTEE search for organization discovery. Useful for EIN registry augmentation, not the main pipeline path.

Key characteristics:
- **Authentication:** None required. Public, unauthenticated GET requests.
- **Rate limits:** Only PDF download links are rate-limited. JSON endpoints appear unthrottled in practice, but courteous request spacing (200–500ms) is recommended for bulk pulls.
- **Fields returned:** ~40–120 financial fields per filing depending on form type (990, 990-EZ, 990-PF), using IRS "element name" conventions. Includes totrevenue, totfuncexpns, totassetsend, totliabend, pct_compnsatncurrofcr, and dozens of Part-level line items.
- **Coverage:** Summary data processed by the IRS during 2012–2019 calendar years (predominantly FY2011–FY2018 in structured form). Full Form 990 documents (PDF + XML) are linked for electronically filed documents; electronic data prior to October 2021 is also available via AWS S3.
- **Limitation:** Does not include organizations filing Form 990-N (e-Postcard; receipts <$50K). Many very small rehab centers will fall into this gap.
- **Limitation:** `filings_without_data` records contain only tax period, form type, and a PDF URL — no structured financial fields. These must be routed to the IRS S3 XML fallback path.

#### 1.1.2 IRS AWS S3 XML Filings

**Bucket:** `irs-form-990` (AWS US East — N. Virginia region)
**Index:** Available as a per-year CSV index from `https://apps.irs.gov/pub/epostcard/990/xml/<YEAR>/` listing EIN, form type, filing date, and object key for each XML file. Monthly ZIP releases are also available at the same path.

Key characteristics:
- **Format:** One XML file per electronic 990 filing, using IRS TEOS schema (2,000+ available fields across Form 990 parts and all schedules).
- **Coverage:** Electronic filings only, going back to approximately 2011. Paper filers are not in this dataset. Updated monthly by the IRS (latest posting as of April 2026).
- **Schema complexity:** The IRS XML uses element names defined in TEOS schemas (available at `https://www.irs.gov/charities-non-profits/form-990-series-downloads`). The schema version changed in 2013 and has had minor revisions annually. XPath extraction requires version-aware parsing.
- **Access cost:** Free. Data is a public data set; no AWS Data Exchange subscription fee. Egress costs apply if pulling at scale from outside AWS us-east-1.
- **Richness:** Canonical source. Contains every field on the form — Schedule J (compensation detail), Schedule I (grants made), Schedule B (contributions; note: contributor names are redacted per IRS policy), Schedule O (narrative supplements), and all other schedules. ProPublica's structured data is derived from this source.
- **Deduplication note:** The index is not exhaustive of all available XML files. The [Nonprofit Open Data Collective](https://nonprofit-open-data-collective.github.io/irs-990-efile-index/) maintains an extended master index that is more complete than the official IRS index.

#### 1.1.3 Candid (formerly GuideStar)

Candid provides highly enriched nonprofit profiles including 990 data, leadership data, and foundation grantmaking history. The basic 990 PDF access is free; programmatic API access to structured financial data and advanced fields requires a paid subscription tier.

**Decision:** Candid is **out of scope for the primary pipeline** due to cost and ToS restrictions on derivative datasets. It is noted here as a potential supplementary enrichment layer for a future phase (e.g., board member disambiguation, foundation grant cross-references).

---

### 1.2 Recommended Architecture: ProPublica Primary, IRS S3 Fallback

**Decision: ProPublica API is the primary pipeline source. IRS S3 XML is the fallback for orgs and fields not covered by ProPublica.**

| Dimension | ProPublica API | IRS S3 XML |
|---|---|---|
| Format | Clean normalized JSON | Raw XML (2,000+ fields, schema-versioned) |
| EIN lookup | Native | Via index CSV lookup → object key |
| Authentication | None | None (public bucket) |
| Financial fields | ~40–120 per filing | Complete (all Parts + Schedules) |
| Schedule J (compensation) | Partial summary | Complete detail per person |
| Schedule I (grants made) | Not surfaced | Complete per-grantee rows |
| Schedule O (narrative) | Not surfaced | Present in XML |
| 990-EZ / 990-PF | Supported (mixed field sets) | Supported |
| 990-N (e-Postcard) | Not included | Not included (no full filing exists) |
| Small org coverage gap | Yes (990-N gap) | Yes (same gap) |
| Setup complexity | Low | Medium (XPath extraction, schema versioning) |
| Update latency | Reflects IRS releases; irregular | Monthly IRS posting |
| Attribution required | Yes (see §9) | Public domain |

**Rationale:** For the WildlifeStats use case — pulling financial summaries for a bounded universe of ~1,000–3,000 EINs drawn from the rehab-center registry — ProPublica's clean JSON eliminates the XML parsing complexity for the common case. The IRS S3 path is reserved for:

1. Organizations where ProPublica returns only `filings_without_data` (PDF-only; no structured data)
2. Fields ProPublica does not surface: Schedule J per-person compensation rows, Schedule I per-grantee rows, Schedule O narrative text, and any Part IX line items beyond ProPublica's subset
3. Historical filings predating ProPublica's structured data coverage
4. Quality-assurance spot-checks against ProPublica figures

The hybrid approach gives WildlifeStats the best of both: low-friction bulk pulls for the common case, with field-complete fallback for the detailed analytics that define the research value proposition.

---

## 2. Pipeline Architecture

All code lives at `wildlifestats/_pipeline/form990/`. This is a WildlifeStats-native implementation. No MOA code is copied or redistributed.

```
wildlifestats/_pipeline/form990/
  fetch_propublica.py        # ProPublica API client; pulls by EIN
  fetch_irs_xml.py           # IRS S3 fallback; XML → normalized JSON
  normalize.py               # Common schema across sources
  extract_compensation.py    # Schedule J extraction (officers, key employees)
  extract_program_service.py # Part III program service accomplishments
  extract_financials.py      # Parts I, IV, VIII (revenue), IX (expenses), X (balance sheet)
  extract_governance.py      # Part VI (governance, policies)
  extract_grants.py          # Schedule I (grants received and made)
  audit.py                   # Per-record provenance
  run.py                     # Orchestrator; takes EIN list, outputs normalized JSON
```

### Module Responsibilities

**`fetch_propublica.py`**
- Wraps `GET /organizations/:ein.json`
- Writes raw API response to `cache/propublica/<EIN>_<ISO_DATE>.json`
- Returns `(filings_with_data: list, filings_without_data: list, org_profile: dict)`
- Handles HTTP 404 (org not in ProPublica), 429/5xx with exponential backoff
- Detects when a `filings_without_data` entry exists without a corresponding `filings_with_data` entry for the same tax period, flagging those for IRS S3 fallback

**`fetch_irs_xml.py`**
- Downloads the per-year index CSV from IRS TEOS (`apps.irs.gov/pub/epostcard/990/xml/<YEAR>/`) and caches locally
- Resolves EIN + tax year to an S3 object key
- Downloads the XML file; caches at `cache/irs_xml/<EIN>_<TAX_PERIOD>.xml`
- Uses the Nonprofit Open Data Collective extended index as a supplementary lookup when the IRS official index is incomplete
- Parses using `lxml` with schema-version detection (pre-2013 vs. 2013+ TEOS schema variants)
- Returns a normalized dict matching the output of `normalize.py`'s target schema

**`normalize.py`**
- Defines the canonical `Filing990` dataclass (see §3 for full schema)
- Accepts either a ProPublica filing dict or a parsed IRS XML dict
- Maps source-specific field names to canonical names
- Applies type coercion: all monetary amounts as `int` (cents) or `float` (dollars), all percentages as `float` 0.0–1.0, booleans for yes/no questions
- Handles null/missing gracefully: all fields nullable, with `_source` annotation per field group indicating which source populated it

**`extract_compensation.py`**
- Parses Schedule J rows: per-person officer/director/key-employee compensation detail
- Fields: person name, title, base compensation, bonus/incentive comp, other reportable comp, deferred compensation, non-taxable benefits, total comp, hours/week, related org comp flag
- Falls back to Part VII, Section A when Schedule J is not filed (org below compensation threshold)
- Outputs a list of `CompensationRecord` objects attached to the filing

**`extract_program_service.py`**
- Parses Part III, lines 4a–4e: up to four named program service descriptions plus "other"
- Extracts free-text description, total expenses, grants component of expenses, and program service revenue per activity
- Also parses Part III, line 2 (primary mission statement)
- Falls through to Schedule O if Part III narrative is truncated on the main form

**`extract_financials.py`**
- Part VIII (Revenue): contributions/grants, program service revenue, investment income, bond proceeds, royalties, rental income, net gain/loss on asset sales, fundraising events, gaming, sales of inventory, miscellaneous revenue; computes totals per column (Total, Related/Exempt, Unrelated, Excluded)
- Part IX (Expenses): grants and similar amounts, member benefits, salaries/comp/benefits (lines 5–10), professional fees, advertising, office expenses, IT, royalties, occupancy, travel, conferences, interest, depreciation, insurance, other
- Part IX columns: program services, management/general, fundraising, total — captures the functional expense allocation split
- Part X (Balance Sheet): cash, savings, pledges, grants receivable, accounts receivable, inventories, prepaid, loans, investments (securities, program-related), land/buildings/equipment (net), other assets; total assets; accounts payable, grants payable, deferred revenue, tax-exempt bond liabilities, loans from officers, other liabilities; total liabilities; net assets by class (unrestricted, temporarily restricted, permanently restricted / ASC 958 reclassified equivalents for post-2018 filers)

**`extract_governance.py`**
- Part VI, Section A: voting board members (total, independent), governance body meetings
- Part VI, Section B: policies — conflict-of-interest policy, COI annual disclosure, COI monitoring/enforcement, whistleblower policy, document retention/destruction policy, Chapter 11 public availability method
- Part VI, Section C: compensation review process for top officer, compensation review for other officers, contemporaneous documentation of process
- Part I summary: number of voting members, number of independent voting members, total employees, total volunteers

**`extract_grants.py`**
- Schedule I (grants made by the organization): per-grantee rows with grantee EIN, name, address, IRC section, amount of cash grant, amount of non-cash assistance, valuation method, description, purpose
- Aggregates: total grants made (count + dollar amount), domestic vs. foreign split
- Schedule B (contributions received) is redacted by IRS for contributor identities; captures only aggregate totals available from Part VIII

**`audit.py`**
- Attaches `_provenance` block to every `Filing990` object:
  - `source`: `"propublica_api"` | `"irs_s3_xml"` | `"irs_s3_xml_via_nodc_index"`
  - `fetch_timestamp`: ISO 8601 UTC
  - `api_url` or `s3_object_key`: the exact URL or key used
  - `raw_cache_path`: local path to cached raw file
  - `propublica_page_url`: `https://projects.propublica.org/nonprofits/organizations/<EIN>` (always attached even for IRS S3 pulls, if org exists in ProPublica)
  - `irs_pdf_url`: direct PDF URL if available from ProPublica `pdf_url` field
  - `schema_version`: for XML pulls, the detected TEOS schema version year
  - `pipeline_run_id`: UUID of the `run.py` invocation that produced the record

**`run.py`**
- Accepts: path to EIN list (JSON array or CSV column), optional `--tax-years` range, optional `--force-refresh` flag
- Per EIN: calls `fetch_propublica.py`, checks for gaps, calls `fetch_irs_xml.py` for missing tax years or flagged records
- Calls all `extract_*.py` modules, assembles into `Filing990` objects, validates against schema
- Outputs: one `<EIN>_<TAX_YEAR>.json` per filing in `output/990_normalized/`
- Outputs: `run_manifest.json` summarizing counts, gap flags, errors, coverage by source
- Logs per-EIN status (found, partial, not_found, error) for operator review

---

## 3. Output Schema

Each file in `output/990_normalized/` is a single JSON object conforming to the `Filing990` schema. All monetary values are in whole US dollars (integer). Percentages are floats in [0.0, 1.0]. All fields are nullable.

```json
{
  "// ── IDENTIFIER BLOCK ──────────────────────────────": null,
  "ein": "XX-XXXXXXX",
  "ein_int": 123456789,
  "org_name": "Blue Ridge Wildlife Center",
  "org_name_aliases": ["BRWC"],
  "address": "...", "city": "...", "state": "VA", "zipcode": "...",
  "tax_year": 2023,
  "tax_period_end": "2023-12-31",
  "accounting_period_end_month": 12,
  "form_type": "990",
  "fiscal_year_end_month": 12,
  "ntee_code": "D20",
  "subsection_code": 3,

  "// ── MISSION / PROGRAM ────────────────────────────": null,
  "mission_statement": "...",
  "program_services": [
    {
      "sequence": "4a",
      "code": "...",
      "description": "Wildlife intake and rehabilitation...",
      "expenses_total": 345000,
      "expenses_grants": 0,
      "revenue": 12000
    }
  ],
  "total_program_service_expenses": 345000,

  "// ── FINANCIALS SUMMARY ────────────────────────────": null,
  "total_revenue": 512000,
  "total_expenses": 489000,
  "net_assets_eoy": 210000,
  "net_assets_boy": 187000,
  "revenue_less_expenses": 23000,
  "pct_program_expenses": 0.706,
  "pct_admin_expenses": 0.201,
  "pct_fundraising_expenses": 0.093,
  "total_assets_eoy": 310000,
  "total_liabilities_eoy": 100000,

  "// ── DETAILED REVENUE (Part VIII) ─────────────────": null,
  "rev_contributions_grants": 380000,
  "rev_program_service": 12000,
  "rev_investment_income": 8000,
  "rev_bond_proceeds": 0,
  "rev_royalties": 0,
  "rev_rental_net": 0,
  "rev_net_asset_sales": 5000,
  "rev_fundraising_events_gross": 90000,
  "rev_fundraising_events_direct_expenses": 15000,
  "rev_fundraising_events_net": 75000,
  "rev_gaming_net": 0,
  "rev_inventory_sales_net": 0,
  "rev_other_misc": 32000,
  "rev_total": 512000,

  "// ── DETAILED EXPENSES (Part IX) ─────────────────": null,
  "exp_grants_domestic": 0,
  "exp_grants_foreign": 0,
  "exp_member_benefits": 0,
  "exp_salaries_comp_benefits": 198000,
  "exp_officer_comp": 72000,
  "exp_disqualified_person_comp": 0,
  "exp_other_salaries": 126000,
  "exp_pension_plan_contributions": 9800,
  "exp_other_employee_benefits": 14200,
  "exp_payroll_taxes": 16000,
  "exp_fees_professional_services": 22000,
  "exp_legal_fees": 5000,
  "exp_accounting_fees": 8500,
  "exp_lobbying_fees": 0,
  "exp_professional_fundraising_fees": 0,
  "exp_investment_management_fees": 0,
  "exp_advertising_promotion": 7000,
  "exp_office": 12000,
  "exp_information_technology": 8000,
  "exp_royalties": 0,
  "exp_occupancy": 34000,
  "exp_travel": 6500,
  "exp_conferences": 3200,
  "exp_interest": 4100,
  "exp_depreciation_depletion": 18000,
  "exp_insurance": 11000,
  "exp_other_total": 38400,
  "exp_total_functional": 489000,
  "exp_total_program_services": 345534,
  "exp_total_mgmt_general": 98334,
  "exp_total_fundraising": 45132,

  "// ── COMPENSATION (Schedule J / Part VII) ────────": null,
  "compensation_records": [
    {
      "person_name": "Jane Smith",
      "title": "Executive Director",
      "avg_hours_per_week": 40.0,
      "avg_hours_per_week_related_orgs": 0.0,
      "reportable_comp_from_org": 72000,
      "reportable_comp_related_orgs": 0,
      "other_comp": 8800,
      "base_compensation": 72000,
      "bonus_incentive_comp": 0,
      "other_reportable_comp": 0,
      "deferred_compensation": 0,
      "nontaxable_benefits": 8800,
      "total_comp_from_all_sources": 80800,
      "former_officer": false,
      "key_employee": false,
      "highest_compensated": false,
      "officer_director": true,
      "source": "schedule_j"
    }
  ],
  "total_officers_directors_trustees_count": 9,
  "schedule_j_filed": true,

  "// ── GOVERNANCE (Part VI) ─────────────────────────": null,
  "governance_board_size": 9,
  "governance_independent_board_members": 8,
  "governance_coi_policy": true,
  "governance_coi_annual_disclosure": true,
  "governance_coi_monitoring": true,
  "governance_whistleblower_policy": true,
  "governance_document_retention_policy": true,
  "governance_public_availability_method": "website",
  "governance_compensation_review_ceo": true,
  "governance_compensation_review_others": true,
  "governance_compensation_documented": true,
  "total_employees": 14,
  "total_volunteers": 220,

  "// ── GRANTS MADE (Schedule I) ─────────────────────": null,
  "grants_made": [
    {
      "grantee_name": "...",
      "grantee_ein": "...",
      "grantee_state": "VA",
      "irc_section": "501(c)(3)",
      "cash_grant_amount": 5000,
      "non_cash_amount": 0,
      "purpose": "Wildlife education programs"
    }
  ],
  "grants_made_total_cash": 5000,
  "grants_made_count": 1,

  "// ── AUDIT / FLAGS ────────────────────────────────": null,
  "form_990t_filed": false,
  "schedule_b_public": false,
  "single_audit_required": false,
  "unrelated_business_revenue": 0,
  "amended_return": false,

  "// ── PROVENANCE ───────────────────────────────────": null,
  "_provenance": {
    "source": "propublica_api",
    "fetch_timestamp": "2026-06-11T12:00:00Z",
    "api_url": "https://projects.propublica.org/nonprofits/api/v2/organizations/123456789.json",
    "raw_cache_path": "cache/propublica/123456789_2026-06-11.json",
    "propublica_page_url": "https://projects.propublica.org/nonprofits/organizations/123456789",
    "irs_pdf_url": "https://projects.propublica.org/nonprofits/download-filing?path=...",
    "schema_version": null,
    "pipeline_run_id": "abc123"
  }
}
```

---

## 4. Public Surface Design

### 4.1 Per-Org Financials Page

**URL pattern:** `wildlifestats.org/centers/<slug>/financials/`

This page renders a full normalized 990 view for a single organization. Layout:

- **Header:** Org name, EIN, most recent tax year, form type
- **Year selector:** Dropdown of all available tax years in descending order; defaults to most recent
- **Summary card:** Total revenue, total expenses, net assets EOY, program / admin / fundraising expense percentages displayed as a horizontal stacked bar
- **Revenue breakdown:** Horizontal bar chart — contributions, program service, investment, fundraising events, other
- **Expense breakdown:** Horizontal bar chart — salaries, occupancy, professional fees, other program, admin, fundraising
- **Compensation table:** All Schedule J / Part VII records for the selected year, sortable by total comp
- **Governance checklist:** COI policy, whistleblower, document retention — yes/no badges
- **Program services:** Accordion showing Part III program descriptions with expense amounts
- **Grants made:** Table of Schedule I grantees (if any)
- **Source links:** "View on ProPublica" (linked to `propublica_page_url`) and "Download IRS PDF" (linked to `irs_pdf_url`) displayed prominently per Mike's D2 directive
- **Data notice:** "990 data is public information. Financial figures reflect the tax year indicated and are sourced from IRS filings via ProPublica Nonprofit Explorer. Data typically lags 12–18 months from fiscal year-end."

### 4.2 Sector Financials Research Page

**URL pattern:** `wildlifestats.org/research/financials/`

Aggregated sector-level analytics view. Sections:

- **Sector overview:** Total sector revenue by year (line chart, 5-year trailing), number of filers, median revenue, total employees
- **Expense composition:** Stacked area chart of sector-wide program / admin / fundraising percentages over time
- **Geographic distribution:** Choropleth map — total sector revenue by state; toggleable to per-org count
- **Revenue concentration:** Herfindahl-Hirschman Index (HHI) display with narrative interpretation; top-10 orgs by revenue with revenue share
- **Compensation overview:** Box-and-whisker chart — CEO total comp by org size quintile; filterable by region
- **Year-over-year trends:** Median revenue growth, median CAGR, net asset growth

### 4.3 Registry Cross-Link

Every rehab center directory page at `wildlifestats.org/centers/<slug>/` includes a "Financials" tab. If the center's EIN is in the registry and a 990 record exists in the pipeline output, the tab renders the most recent year's summary card (total revenue, total expenses, net assets). If no 990 data exists (e.g., 990-N filers, very new orgs), the tab displays "No publicly available 990 filing found. Organization may file Form 990-N (gross receipts <$50,000)."

### 4.4 Compensation Benchmarking Tool

**URL pattern:** `wildlifestats.org/research/compensation-benchmark/`

See §6 for full spec. Entry point from the sector financials page and from the per-org financials page ("How does our CEO comp compare?").

---

## 5. Sector Aggregate Metrics

The following metrics are computed over the full wildlife rehab sector 990 dataset and updated each pipeline refresh cycle.

### 5.1 Revenue Metrics

| Metric | Computation | Grouping |
|---|---|---|
| Median total revenue | Median of `total_revenue` | Sector-wide; by year; by state |
| IQR total revenue | 25th–75th percentile | Sector-wide; by year |
| Mean total revenue | Mean of `total_revenue` | Sector-wide; by year |
| Total sector revenue | Sum of `total_revenue` | Sector-wide; by year |
| Revenue CAGR (5-year) | `(rev_yr_n / rev_yr_n-5)^(1/5) - 1` per org | Distribution: median, P25, P75 |
| Revenue concentration (HHI) | `Σ (rev_i / rev_total)²` across all orgs | Sector-wide; by year |
| Revenue per organization | — | Top-10, bottom-decile lists |

### 5.2 Expense Composition

| Metric | Computation |
|---|---|
| Program expense % | `exp_total_program_services / exp_total_functional` |
| Admin expense % | `exp_total_mgmt_general / exp_total_functional` |
| Fundraising expense % | `exp_total_fundraising / exp_total_functional` |
| Sector-median program % | Median of per-org program %; computed annually |
| Salary % of total expenses | `exp_salaries_comp_benefits / exp_total_functional` |

### 5.3 Compensation Metrics

| Metric | Computation | Segmentation |
|---|---|---|
| Median CEO total comp | Median `total_comp_from_all_sources` for top officer | By revenue quintile; by region; by year |
| P25 / P75 CEO comp | Quartile bounds | Same |
| Highest-paid employee comp | Max of any single compensation record | Per org; sector ranking |
| "Top 25 highest compensated" list | Ranked by CEO total comp | Sector-wide per year; filterable by state |
| Comp as % of revenue | `ceo_comp / total_revenue` | By revenue quintile |

### 5.4 Efficiency Metrics

These require joining 990 data with annual report intake data collected by the WildlifeStats registry pipeline:

| Metric | Computation | Data dependency |
|---|---|---|
| $ per patient intake | `total_expenses / annual_intake_count` | Registry annual report data |
| Revenue per FTE | `total_revenue / total_employees` | Part I employee count |
| Intake per FTE | `annual_intake_count / total_employees` | Registry + Part I |
| Program expense per patient | `exp_total_program_services / annual_intake_count` | Registry annual report data |

Efficiency metrics will display with a data-availability flag: if intake data is not available for an org, per-patient metrics are suppressed and the org is excluded from sector medians for those metrics.

### 5.5 Capacity and Scale

| Metric | Computation |
|---|---|
| Net asset reserve (months) | `(net_assets_eoy / exp_total_functional) * 12` |
| Revenue growth rate YoY | `(rev_yr_n / rev_yr_n-1) - 1` |
| Asset-to-expense ratio | `total_assets_eoy / exp_total_functional` |

### 5.6 Geographic Aggregates

- Total revenue by state (sum, median, count of filers)
- Program expense % by state/region (Northeast, Southeast, Midwest, West, etc.)
- CEO comp by region (4-region + state breakdown)
- Revenue per capita by state (total sector revenue / state population)

---

## 6. Compensation Benchmarking Spec

Per Mike's D3 directive: "Compensation would be great for centers to use as a benchmarking tool." This tool is a genuine benefit to partner organizations and a partnership-acquisition asset.

### 6.1 Tool Design

**Entry modes:**
1. **EIN lookup:** Partner enters their EIN; pipeline resolves to org record, pulls most recent CEO compensation figure, determines org's size quintile and region automatically.
2. **Manual input:** Non-partner (or org without 990 on file) enters: (a) annual budget/revenue range (select), (b) US region (select), (c) CEO total compensation (text input). No account required.

**Peer set definition:**
- Revenue quintile: Q1 (<$250K), Q2 ($250K–$750K), Q3 ($750K–$2M), Q4 ($2M–$5M), Q5 (>$5M). Computed over the current universe of wildlife rehab 990 filers.
- Region: 4-region US Census (Northeast, South, Midwest, West). Filterable to state if peer set size ≥5.
- Tax year: most recent available, with prior-year comparison toggle.

**Output display:**
- **Percentile statement:** "Your CEO compensation of $X places your organization at the Nth percentile among wildlife rehabilitation nonprofits in your size tier and region."
- **Box plot:** Whiskers at P10/P90, box at P25/P75, median line, target org dot highlighted in accent color. X-axis: total CEO compensation in dollars.
- **Peer set table:** All peer orgs in the size/region group listed with name, state, revenue, and CEO comp. Since this is public 990 data, no suppression is applied per Mike's D2 directive.
- **Year-over-year view:** If prior year data exists for the target org, a second panel shows the same chart for the prior year with an arrow indicating movement in percentile.
- **Download:** CSV export of the peer set (name, EIN, state, revenue, CEO comp, tax year).

### 6.2 Privacy and Legal Posture

Per Mike's D1/D2 directives and consistent with the legal posture in §9: this tool surfaces only information that is already mandated to be public under 26 U.S.C. § 6104. Schedule J compensation data is public record. No suppression is applied. A disclosure note reads: "All compensation data is sourced from publicly available IRS Form 990 filings. Data accuracy depends on the information reported by each organization to the IRS."

### 6.3 Strategic Positioning

Frame this tool as a free benefit for WildlifeStats partner centers. Suggested messaging: "WildlifeStats gives every wildlife rehabilitation center access to compensation benchmarking data that previously required expensive consulting engagements or paid database subscriptions. Use this tool to inform your next board compensation review, justify a salary adjustment, or demonstrate to funders that your compensation is appropriate and mission-aligned."

Outreach angle for partnership acquisition: "Free compensation benchmarking" is a concrete, immediate value proposition for a CFO or board chair who faces this question at every annual board meeting.

---

## 7. Data Freshness and Update Cadence

### 7.1 The 12–18 Month Lag

IRS Form 990 data is subject to structural latency that WildlifeStats must communicate honestly. The pipeline and every public surface must be transparent about this:

| Stage | Typical Duration |
|---|---|
| Organization's fiscal year ends | Day 0 |
| 990 filing deadline (15th of 5th month after FY end) | ~5 months |
| Maximum extension period | +6 months (to ~11 months) |
| IRS processing and data release | +1–6 months |
| **Total lag from FY end to public availability** | **12–18 months** |

Per [Candid's guidance](https://learning.candid.org/lag-time/272655): "The total lag time between the end of an organization's fiscal year and the point when its IRS filing is publicly available can be 12 to 18 months."

For a December 31 fiscal year-end organization: the FY2023 filing may not be publicly available until mid-to-late 2025.

### 7.2 Update Schedule

**Recommended cadence: Quarterly pipeline refresh** (January, April, July, October).

Rationale: IRS releases new XML batches monthly. Quarterly pulls balance freshness against pipeline operating costs. Ad-hoc urgent refresh is possible via `run.py --force-refresh --ein <EIN>` for partner orgs requesting updated data.

**Auto-detect new filings:**
- On each refresh, call `fetch_propublica.py` for all registry EINs and compare `updated` timestamps against the local cache manifest
- Pull IRS TEOS index for the current year and prior year; diff against cached index to identify new filings
- Flag any EIN with a new filing for full re-extraction; skip EINs with no change

### 7.3 UI Disclosure

All 990 data displays on WildlifeStats must show: "Financial data as of tax year [YEAR]. IRS filings typically become available 12–18 months after an organization's fiscal year ends. [View on ProPublica]."

---

## 8. Audit Trail

Every record produced by the pipeline carries a `_provenance` block (detailed in §2, `audit.py`). At the public surface level:

- **Per-org financials page:** Each tax year card includes a "Source" footer linking to the ProPublica organization page (`projects.propublica.org/nonprofits/organizations/<EIN>`) and the IRS PDF URL if available.
- **Sector research pages:** A methodology note links to this specification (public, in the WildlifeStats GitHub repo) and states the data sources and refresh date.
- **Compensation benchmarking tool:** Each peer set includes column "Source" = "IRS Form 990 via ProPublica Nonprofit Explorer" with a link.
- **Pipeline run log:** `run_manifest.json` records per-EIN outcome, source, fetch timestamp, cache path, and any error codes. This manifest is archived by run date.
- **Phase 4.5+ source registry integration:** Each `Filing990` object emits a source registry entry consistent with the WildlifeStats source provenance standard: `{ type: "irs_990", ein: "...", tax_year: ..., source_api: "propublica|irs_s3", fetch_date: "...", url: "..." }`.

---

## 9. License + ToS Posture

### 9.1 ProPublica Nonprofit Explorer API

Per the [ProPublica Nonprofit Explorer API documentation](https://projects.propublica.org/nonprofits/api):

> "Usage constitutes agreement to our Data Terms of Use."

The API's `data_source` field in every response explicitly cites: "ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/ | IRS Exempt Organizations Business Master File Extract (EO BMF) | IRS Annual Extract of Tax-Exempt Organization Financial Data."

**WildlifeStats obligations:**
1. **Attribution required:** Every public display of ProPublica-sourced data must credit "ProPublica Nonprofit Explorer" with a link to `https://projects.propublica.org/nonprofits/`. This is satisfied by the source link on every per-org financials card and the methodology note on sector pages.
2. **No resale:** WildlifeStats does not sell 990 data. The pipeline output is used for internal research and free public display only. This is compliant.
3. **Derivative analyses permitted:** Sector aggregates, percentile rankings, and compensation benchmarks are derivative analyses of public data. This is explicitly within the spirit of the API's purpose ("Use this database to find organizations and see details like their executive compensation, revenue and expenses").
4. **Contact for questions:** `[email protected]`

### 9.2 IRS S3 XML Data

IRS Form 990 data is produced by the United States federal government as a function of statutory public disclosure requirements under 26 U.S.C. § 6104. As a work of the U.S. federal government, the underlying 990 filing data is in the public domain under 17 U.S.C. § 105. There are no copyright or attribution restrictions. WildlifeStats should nonetheless cite "IRS Form 990 electronic filing data, available via the IRS Tax Exempt Organization Search" for credibility and source transparency.

### 9.3 Candid / GuideStar

Not used in the primary pipeline. If accessed in a future phase, Candid's API ToS requires a paid agreement and restricts bulk download and redistribution. Any Candid integration must be reviewed against their then-current Terms of Service before implementation.

### 9.4 No Sensitive Data Concerns

Schedule B (contributors to the organization) is redacted by the IRS before public release — contributor identities are not in the pipeline dataset. The pipeline does not handle any non-public data. Schedule J compensation figures and Schedule I grant figures are explicitly mandated to be public by federal law.

---

## 10. Phasing (Sub-PRs)

### PR 8b.1 — ProPublica API Client + EIN-Keyed Fetch + Raw Cache
**Estimated effort:** ~half day
**Deliverables:** `fetch_propublica.py`, cache directory structure, `audit.py` stub, unit tests for HTTP error handling and cache logic. Validates against 10 sample EINs from the registry.

### PR 8b.2 — Normalize.py + Common Schema
**Estimated effort:** ~1 day
**Deliverables:** `normalize.py` with full `Filing990` dataclass, `extract_financials.py`, `extract_compensation.py`, `extract_program_service.py`, `extract_governance.py`, `extract_grants.py`. Integration test: 50 EINs through full normalization, schema validation, no silent null-field failures.

### PR 8b.3 — Per-Org Financials Page + UI
**Estimated effort:** ~half day
**Deliverables:** `wildlifestats.org/centers/<slug>/financials/` page template; year selector; revenue/expense bar charts; compensation table; governance checklist; source links; ProPublica attribution footer. Mobile-responsive.

### PR 8b.4 — Sector Aggregates Page
**Estimated effort:** ~1 day
**Deliverables:** `wildlifestats.org/research/financials/` page; all §5 aggregate metrics computed and cached; choropleth map; compensation box plot; HHI concentration chart; downloadable aggregate CSV.

### PR 8b.5 — Compensation Benchmarking Tool
**Estimated effort:** ~half day
**Deliverables:** `wildlifestats.org/research/compensation-benchmark/` tool; EIN and manual-input modes; peer set computation; box plot with target highlighted; peer set table; CSV export; data disclosure note.

### PR 8b.6 — IRS S3 XML Fallback
**Estimated effort:** ~half day
**Deliverables:** `fetch_irs_xml.py`; TEOS index downloader/cache; EIN → object key resolver (primary IRS index + NODC extended index fallback); XPath extraction for Schedule J, Schedule I, Schedule O, and any Part IX fields not surfaced by ProPublica; integration test on orgs present in S3 but absent from ProPublica structured data.

**Dependency note:** 8b.1 must complete before 8b.2. 8b.2 must complete before 8b.3, 8b.4, 8b.5. 8b.6 can run in parallel with 8b.3–8b.5.

---

## 11. Reference Architecture Notes

Mike's MOA 990 pipeline at `C:\Users\Hello\OneDrive - Michael Oak Advisors\06_Data\03_990\990 Data Pull` is a working reference. We do not copy its code; we read its data-flow patterns and schema choices so we don't repeat its mistakes. Specifically request from Mike:

**(a)** Which fields his pipeline normalizes that aren't obvious from raw 990 data — for example, computed fields like true total compensation (summing W-2 box 1 vs. box 5 discrepancies, deferred comp treatment), or derived program-to-fundraising ratios that required non-obvious Part IX column math.

**(b)** Any IRS schema quirks he's already discovered and worked around — known examples in the community include: the 2013 TEOS schema migration breaking backward-compatible XPaths; fiscal-year vs. calendar-year compensation reporting differences between Part VII and Part IX (compensation for fiscal-year filers is reported on a fiscal-year basis in Part IX but on a calendar-year basis in Part VII and Schedule J); certain Part IX lines that sum differently depending on whether the filer used a joint cost allocation; and `null` vs. `0` semantics in ProPublica fields where a missing value means "not applicable" rather than "zero."

**(c)** His recommended deduplication and match strategy when the same EIN files under slightly different legal names in different years — common issues include: legal name changes after mergers, DBA names appearing in some years but not others, and the IRS BMF lagging behind actual name changes by 6–12 months, causing mismatches between the BMF organization name and the name on the 990 filing itself.

---

*Specification ends. Questions to: WildlifeStats Architecture. Separation notice per Mike's D1: this document and the code it specifies are wholly independent of MOA IP.*
