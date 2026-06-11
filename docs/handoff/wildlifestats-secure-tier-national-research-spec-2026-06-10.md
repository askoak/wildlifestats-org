# Secure tier architecture — national research access

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 16:14 ET
**Status:** Source of truth for all `/secure/` work. Supersedes the original Phase 5 mechanism note (`wildlifestats-secure-tier-mechanism-note-phase5-2026-06-10.md`); that note's scope was Mike-only basic-auth proxying to BRWC and is now archived. Phase 5 expands into a real multi-tier national research access platform.
**Mike directive 2026-06-10 16:14 ET:** "really start to plan out the /secure site for research direct access or near-direct access (annonomized raw) data like we built for Staff at BRWC but expand capabilities national for a broad audience"
**Lane discipline:** This document defines a WildlifeStats-native secure tier. No code is copied from BRWC's `/brwc/` — §19 prevents that, and the audience and data model are different enough that a clone would be wrong even if §19 didn't exist.

## §1 — One paragraph

The WildlifeStats secure tier serves a national multi-audience research community — credentialed academics, agency biologists, partner wildlife rehabilitators, veterinary practitioners, advanced students, and accountable journalists — across three access tiers. Tier 1 is Mike (full access). Tier 2 is approved researchers and partners (anonymized individual records, k-relaxed aggregates, programmatic API, bulk DOI-cited downloads). Tier 3 is credentialed reference users (richer aggregates than the public tier, no individual records, clinical/educational orientation). Authentication moves from basic-auth (Phase 5 original architect default) to Netlify Identity with role-based access control. Every query is logged with a per-user audit trail. Every download is DOI-stamped and citation-required. The synthetic cube remains the only data source for the first secure-tier ship; real partner data flows in via Phase 4.5's pipeline as partnerships develop.

## §2 — Three access tiers

### §2.1 Tier 1 — Owner (Mike)

- **Population:** 1 (Mike).
- **Access:** everything. Raw partner data when it exists, full audit logs, admin endpoints, the works.
- **Auth:** Netlify Identity admin role.
- **Use case:** methodology validation, ad-hoc exploration, partnership relationship management.

### §2.2 Tier 2 — Research access (approved researchers and partners)

- **Population:** ~50-500 initially over the first year; could grow to thousands at scale.
- **Sub-audiences:**
  - Credentialed academics (PIs, postdocs, biostats grad students with institutional affiliation)
  - State wildlife agency biologists / USGS NWHC / USDA APHIS staff
  - Partner wildlife rehabilitation organization administrators (their own data + anonymized peer comparisons)
  - Veterinary diagnostic lab staff at AAVLD member labs
- **Access:**
  - Anonymized individual records (PII stripped — see §4 anonymization rules)
  - K-relaxed aggregates (k ≥ 5 instead of public k ≥ 10)
  - Programmatic JSON API (`/secure/api/v1/...`)
  - Bulk download of full anonymized cube as Parquet or CSV (DOI-stamped, citation-required)
  - Cite-able query URLs (every UI query produces a stable URL that re-executes the same query)
  - Saved queries, downloadable session log
  - Rate limit: 1000 API requests/day per user
- **Auth:** Netlify Identity authenticated role + approved researcher role.
- **Application flow:** ORCID-linked account, institutional affiliation declared, use-case statement, terms-of-use agreement (citation requirement, no redistribution beyond derived work, attribution to WildlifeStats and the underlying source registry entries).
- **Approval:** automated for verified ORCID + .edu/.gov institutional email; manual for everyone else (Mike or a delegated admin reviews; turnaround target one business day).

### §2.3 Tier 3 — Reference access (credentialed reference users)

- **Population:** larger — thousands to tens of thousands.
- **Sub-audiences:**
  - Wildlife veterinarians and rehab center medical directors who need clinical reference, not micro-data
  - Graduate students doing literature reviews
  - Journalists and policy researchers verifying specific claims
  - Educators teaching wildlife disease ecology or rehab medicine
- **Access:**
  - Richer aggregates than the public tier (deeper geographic resolution; finer temporal grain; richer cross-tabulations) but still aggregate
  - No individual records
  - K-suppression at public tier's k ≥ 10 still applies
  - Same WREN assistant as the public tier, with the reference-tier data context
  - Same cite-able query URLs
  - Rate limit: 100 API requests/day per user
- **Auth:** Netlify Identity authenticated role.
- **Application flow:** verified email (any institution, including independent researchers); attestation to terms of use; no further approval needed (verification is the gate).

## §3 — Authentication infrastructure

### §3.1 Netlify Identity

Switch from the Phase 5 mechanism note's basic-auth to **Netlify Identity** as the authentication provider. Rationale:

- Already integrated with Netlify hosting; no separate backend.
- Supports JWT tokens that Netlify Edge Functions can validate.
- Supports OAuth providers (Google, GitHub) for low-friction account creation.
- Has built-in invite flow + role assignment.
- Free tier covers up to 1000 active users; the next tier covers up to 5000.

### §3.2 Role mapping

Three roles in Netlify Identity, mapped to the three tiers:

| Role | Tier | Granted by |
|---|---|---|
| `admin` | Tier 1 | Manually by Mike |
| `researcher` | Tier 2 | Automated for ORCID + .edu/.gov, manual otherwise |
| `member` | Tier 3 | Automated on email verification + attestation |

### §3.3 URL routing

| URL pattern | Required role | Notes |
|---|---|---|
| `/` and all public pages | none | Public tier (existing) |
| `/secure/` | `member` or higher | Landing page for any authenticated user |
| `/secure/reference/*` | `member` or higher | Tier 3 dashboards and views |
| `/secure/research/*` | `researcher` or higher | Tier 2 micro-data, bulk downloads |
| `/secure/admin/*` | `admin` | Tier 1 admin views, user management |
| `/secure/api/v1/aggregates/*` | `member` or higher | Tier 3 API |
| `/secure/api/v1/records/*` | `researcher` or higher | Tier 2 API (anonymized individual records) |
| `/secure/api/v1/admin/*` | `admin` | Tier 1 API |
| `/wren/secure/*` | `member` or higher | Secure WREN with tier-appropriate data context |

`_redirects` and `netlify.toml` enforce role gates at the edge. Netlify Edge Functions validate JWT on every request to `/secure/api/*`.

### §3.4 Migration from Phase 5 basic-auth

Phase 5 original spec assumed basic-auth with the BRWC staff passcode reused. The amended secure tier doesn't use basic-auth. The Phase 5 mechanism note is archived; do not implement it. The new Phase 5 starts from scratch with Netlify Identity.

## §4 — Anonymization rules for Tier 2 micro-data

"Anonymized raw" per Mike's framing. Specific anonymization applied at the partner-pipeline output stage (Phase 4.5 aggregator's emit phase) so that anonymization is build-time, not query-time. See §5 governance below — this matches Standing Orders §5 (privacy by build, not by runtime).

### §4.1 What is stripped from individual records

| Field | Public tier (k≥10 aggregates only) | Tier 2 anonymized individual | Tier 1 (Mike) raw |
|---|---|---|---|
| `intake_id` | not exposed | hashed (SHA-256 of partner_id + raw_id + project salt) | hashed |
| `partner_id` | not exposed | replaced with `partner_synthetic_id` (stable random ID assigned per partner) | full partner_id |
| `intake_date` | aggregated to month | month + year only (no day) | full date |
| `intake_lat`, `intake_lon` | not exposed | not exposed (county FIPS only) | county FIPS only (raw lat/lon never stored even at Tier 1 per Phase 4.5 spec) |
| `species_raw` | not exposed | normalized canonical only | normalized canonical only |
| `case_notes_text` | not exposed | not exposed | not exposed (per partner agreement, free-text never leaves the partner) |
| `intake_county_fips` | exposed | exposed | exposed |
| `state` | exposed | exposed | exposed |
| `class`, `species`, `reason`, `outcome`, `disposition` | exposed | exposed | exposed |
| `partner_synthetic_id` | not exposed | exposed | exposed |
| `data_freshness_date` | exposed | exposed | exposed |

### §4.2 Re-identification risk floor

Per record, the smallest combination that could theoretically re-identify a partner or a case:

- Month + county_fips + species (canonical) + reason + outcome

For each unique combination, if the count of records ≤ 4, the row is suppressed at Tier 2 (so Tier 2 sees only combinations with at least 5 records). Mike (Tier 1) sees all combinations regardless of count.

This is **k=5 cell suppression at Tier 2**, vs. **k=10 at Tier 3 and public**. Aggressive enough to materially protect partner anonymity while still letting researchers see rare cases.

### §4.3 Partner agreement requirement

No real partner data flows to Tier 2 until the partner explicitly opts into "anonymized national research dataset" terms in their data sharing agreement. Default is opt-out — partners contribute to the public aggregates only. Opt-in is per-partner, recorded in the source registry entry, gated by a build-time check.

## §5 — Governance

### §5.1 Terms of use (Tier 2)

Researchers accept on application:

1. Cite WildlifeStats and the underlying source-registry entries in any published work using these data (citation snippet auto-generated per query).
2. Do not attempt to re-identify partners or individual cases. Re-identification attempts result in immediate account suspension and notification to the researcher's institutional research office.
3. Do not redistribute the raw bulk download. Derived datasets (analyses, tables, figures in publications) are encouraged; verbatim redistribution of micro-data is prohibited.
4. Acknowledge that the synthetic cube is synthetic and the partner-data layer is identified as such in metadata.
5. Submit a brief annual use report (one paragraph; what you used the data for, what was published).

### §5.2 Audit log

Every query through Tier 2 endpoints — UI or API — is logged server-side in a Netlify Blobs store:

```json
{
  "user_id": "<netlify-identity-uuid>",
  "user_orcid": "0000-0001-2345-6789",
  "institution": "University of Florida",
  "timestamp": "2026-06-10T20:14:00Z",
  "endpoint": "/secure/api/v1/records",
  "query": {"state": ["FL"], "year": [2023], "species": ["sea_turtle"]},
  "records_returned": 142,
  "ip_address_hash": "<SHA-256 of IP, daily-salted>"
}
```

Tier 1 has read access to the full audit log. Tier 2 users see only their own audit history. Audit logs are retained 7 years.

### §5.3 Data citation

Every bulk download produces a citation snippet at download time:

```
WildlifeStats National Wildlife Rehabilitation Database. Tier 2 anonymized
research extract. Query: state=FL, year=2023, species=sea_turtle. Generated
2026-06-10T20:14:00Z. Snapshot DOI: 10.5281/zenodo.20643065 (concept DOI; version DOIs assigned per quarterly release via the GitHub-Zenodo integration on askoak/wildlifestats-org).
Includes data from sources: usgs-whispers (CC0), gbif (CC-BY), and 7 partner
organizations (anonymized). Cite as: Oak, M. and WildlifeStats Consortium (2026). https://doi.org/10.5281/zenodo.20643065
```

Snapshot DOIs are issued quarterly via the Zenodo GitHub-release integration on `askoak/wildlifestats-org`. Each release tag (e.g. `v1.1.0`, `v1.2.0`) triggers Zenodo's webhook, mints a new version DOI, and links it to the project's concept DOI (`10.5281/zenodo.20643065`) which always resolves to the latest version. Each quarterly snapshot is immutable and citable; if a partner's data is later corrected, a new DOI is issued; the old DOI remains for reproducibility of prior research. Zenodo's GitHub integration is free and operational; the EZID/DataCite alternative path is deprecated for this lane.

### §5.4 Take-down policy

If a partner withdraws their data sharing agreement, their records are removed from the next quarterly snapshot's source. Prior snapshot DOIs are not retroactively edited — research citing those DOIs continues to be reproducible against the snapshot frozen at issuance. The withdrawn partner is removed from new quarterly snapshots and from live API responses within 5 business days of withdrawal notice.

## §6 — Surfaces (`/secure/*` URL map)

### §6.1 Tier 3 (member) surfaces

- `/secure/` — landing page. Welcome, tier explanation, application path to upgrade to researcher.
- `/secure/reference/data/` — like the public `/data/` but with deeper aggregates: by-week instead of by-month, full county granularity instead of state-rolled, cross-tabulations not available on the public tier.
- `/secure/reference/clinical/` — clinical reference views: filter by species → list of intake reasons with case counts and outcome distributions; filter by reason → list of species most affected. Built around the questions a wildlife vet would actually ask.
- `/secure/reference/parks/` — National Parks lens with deeper geographic detail.
- `/secure/reference/wildlife/` — Wildlife encyclopedia with more detailed disease ecology per species.
- `/secure/api/v1/aggregates/...` — read-only aggregate API for Tier 3.
- `/secure/wren/` — secure WREN with the Tier 3 data context (aggregates, no individual records).

### §6.2 Tier 2 (researcher) surfaces (additive over Tier 3)

- `/secure/research/` — landing page for the research tier. Documents the API, links to bulk downloads, shows researcher's saved queries and recent downloads.
- `/secure/research/records/` — anonymized individual records explorer. Filter UI with k=5 cell suppression. Each query produces a cite-able URL.
- `/secure/research/downloads/` — bulk downloads. Pre-built quarterly snapshots in Parquet and CSV; on-demand filtered extracts. Each download is DOI-stamped and citation-required.
- `/secure/api/v1/records/...` — micro-data API. JSON responses. Pagination + cursor-based for large queries.
- `/secure/api/v1/snapshots/...` — list and retrieve quarterly snapshot metadata + download URLs.
- `/secure/wren/` — secure WREN at researcher tier sees individual records in its query results.

### §6.3 Tier 1 (admin) surfaces

- `/secure/admin/` — admin landing.
- `/secure/admin/users/` — user list, role assignment, suspension.
- `/secure/admin/partners/` — partner list, data sharing agreement status, opt-in/opt-out toggles.
- `/secure/admin/audit/` — full audit log search.
- `/secure/admin/snapshots/` — snapshot management, DOI issuance, take-down execution.

### §6.4 API standards

- JSON responses by default; `?format=csv` for CSV; `?format=parquet` for Parquet (Parquet is researcher-tier only).
- Cursor-based pagination for any endpoint returning >1000 records. `next_cursor` field in response; pass as `?cursor=...`.
- Rate limits enforced via an Edge Function counter in Netlify Blobs (per user per day). 429 response with `Retry-After` header.
- Stable URL contract: query parameters define the resource. Same query → byte-identical response (until next snapshot regeneration). This is what makes the cite-able URLs durable.

## §7 — Implementation phases (replaces Phase 5 original)

| Phase | Deliverable | Effort |
|---|---|---|
| **5a** | Netlify Identity setup + three roles + `/secure/` landing page (member-only, says "Coming soon" for now) | ~half day |
| **5b** | Tier 3 reference surfaces — deeper aggregates, clinical view, parks/wildlife extended | ~full day |
| **5c** | Audit log infrastructure (Netlify Blobs + Edge Function for write) + researcher application flow + ORCID OAuth | ~full day |
| **5d** | Tier 2 records explorer UI + k=5 suppression in aggregator + anonymization in Phase 4.5 emit stage | ~full day |
| **5e** | Tier 2 micro-data API (`/secure/api/v1/records/...`) + rate limiting | ~half day |
| **5f** | Bulk download infrastructure + quarterly snapshots + DOI integration | ~full day |
| **5g** | Admin tools (`/secure/admin/*`) | ~half day |
| **5h** | Secure WREN at `/secure/wren/` (was Phase 7f) with tier-aware data context | ~half day |
| **5i** | Terms of use page + governance documentation + citation snippet generation | ~half day |
| **5j** | End-to-end testing — three test users (member, researcher, admin) executing representative workflows | ~half day |

Total: ~5-7 days engineer effort. Sequential, with 5a-5c forming a useful intermediate ship (members can sign up, see "coming soon" research views, and explore the reference tier).

## §8 — What 5a-5c ships (intermediate milestone)

After 5a-5c merge, `/secure/` is a working national reference platform:

- Anyone can sign up with email verification → gets `member` role → sees Tier 3 reference surfaces (richer dashboards than public).
- Researchers can submit an upgrade application (ORCID + institution + use case) → automated approval for verified academics, manual queue for others.
- The clinical-reference and deeper-aggregate views are live.
- The audit log records every Tier 3 query.
- The research/records/api/downloads surfaces all display "Coming soon — application pending" placeholders.

This is the minimum viable secure tier. Phases 5d-5j fill in the research-tier deliverables.

## §9 — What this spec does NOT do

- Does not replicate BRWC's `/brwc/` for any BRWC user. BRWC users continue to use BRWC's site at askoak.michaeloak.com unchanged. The WildlifeStats secure tier serves a national multi-audience research community, not BRWC staff specifically.
- Does not host raw partner records. Only anonymized records (Tier 2) and aggregates (Tier 3) ever appear here. Raw records stay at the partner organization or in Tier 1 admin-only storage.
- Does not implement payment, paid tiers, or any commercial product surface. All tiers are free; the application flow is the gate.
- Does not implement full IRB / human-subjects review. Wildlife research data does not typically fall under human-subjects rules. If a future use case requires IRB review (e.g., research using citizen-finder data with PII), that is a separate governance phase.
- Does not implement federated identity (Shibboleth, InCommon). Netlify Identity's email + OAuth is sufficient for the initial scale.

## §10 — Open governance questions for Mike (low priority; do not block engineer)

These are NOT blockers. Architect defaults are stated; engineer ships against the defaults; Mike adjusts later if desired.

1. **DOI provider.** Architect default: EZID + DataCite. Cost: free for the first 100 DOIs/year, then nominal. Alternative: Zenodo (also free, simpler integration, less institutional gravitas). Architect default holds.
2. **k threshold at Tier 2.** Architect default: k=5. Some researchers will argue k=3 is acceptable for synthetic data; some partners will demand k=10 even for anonymized records. Default holds; per-partner override in source registry permitted.
3. **Audit log retention.** Architect default: 7 years (matches federal records retention norms for research data). Alternative: 5 years or 10 years. Default holds.
4. **Take-down notice period.** Architect default: 5 business days. Some partners may demand 24 hours; some agreements may grant 30 days. Default holds; per-partner override in DSA permitted.
5. **Free-tier user cap.** Netlify Identity's free tier is 1000 active users; next tier ($99/mo) covers 5000. Architect default: ship on free tier; upgrade when we hit 800 active users. No action needed today.

## §11 — Cross-references

- Phase 4.5 source registry (`wildlifestats-engineer-order-phase4.5-source-registry-2026-06-10.md`) emits the cube; this spec adds tier-aware anonymization at the emit stage. Phase 4.5+ becomes a prerequisite for Phase 5d.
- WREN spec (`wildlifestats-wren-architecture-spec-2026-06-10.md`) §5 defines public/secure WREN. This spec updates §5.1 — secure WREN's data context is tier-aware (Tier 2 sees micro-data, Tier 3 sees aggregates). The WREN engine itself is unchanged.
- Phase 3.1 cube (`wildlifestats-synthetic-cube-spec-phase3-amendment-1m-2026-06-10.md`) at n=1M is the data substrate for all tiers' synthetic data context. Real partner data is layered on top via Phase 4.5+ when partnerships develop.
- Phase 5 mechanism note (`wildlifestats-secure-tier-mechanism-note-phase5-2026-06-10.md`) is **superseded by this spec**. The basic-auth-with-BRWC-passcode approach is dropped. Move that note to `closed/` when this spec ships.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 16:14 ET
