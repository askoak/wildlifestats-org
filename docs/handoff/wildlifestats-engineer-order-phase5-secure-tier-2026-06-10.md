# Engineer order — Phase 5: secure tier national research access

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer (`soar-aspen-beryl-heron`)
**Date:** 2026-06-10 ~16:14 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main`
**Authority:** §13 elevated ship + §14 self-merge.
**Source of truth:** `docs/handoff/wildlifestats-secure-tier-national-research-spec-2026-06-10.md` — read in full.

This order supersedes the original Phase 5 mechanism note (`wildlifestats-secure-tier-mechanism-note-phase5-2026-06-10.md`). That basic-auth-with-BRWC-passcode design is dropped. Move that note to `docs/handoff/closed/` as part of this order's first sub-PR.

## Scope — ten sequential sub-PRs

Per spec §7. Each self-merges per §14 once CI green + manual smoke test on the Netlify preview. The first three deliver an intermediate ship that's worth running on its own.

| Sub-PR | Deliverable | Effort | Acceptance — key checks |
|---|---|---|---|
| **5a** | Netlify Identity setup + three roles (`admin`, `researcher`, `member`) + `/secure/` landing page + role-gated redirects | ~half day | Unauthenticated user hitting `/secure/` gets the login flow. Verified-email user with `member` role lands on `/secure/`. Tier 2 / Tier 1 surfaces return 403 to `member`-only users. |
| **5b** | Tier 3 reference surfaces — `/secure/reference/data/`, `/secure/reference/clinical/`, `/secure/reference/parks/`, `/secure/reference/wildlife/` | ~full day | Each page loads with the standard chrome, deeper-aggregate views (by-week instead of by-month; full county granularity) backed by the same n=1M sharded cube. |
| **5c** | Audit log infrastructure (Netlify Blobs write on every `/secure/*` request via Edge Function) + researcher application flow + ORCID OAuth | ~full day | Every `/secure/*` request writes an audit entry. Researcher application form submits, automated approval fires for `.edu`/`.gov` + verified ORCID. Manual queue visible to admin (Mike). |
| **5d** | Tier 2 records explorer UI (`/secure/research/records/`) + k=5 cell suppression in aggregator + anonymization rules applied at Phase 4.5 emit stage | ~full day | Researcher role can browse anonymized individual records with k≥5 cells visible. Per spec §4 anonymization rules applied at emit. Tier 3 still sees only k≥10 aggregates. |
| **5e** | Tier 2 micro-data API (`/secure/api/v1/records/...`) + cursor pagination + rate limiting (1000/day for researchers, 100/day for members) | ~half day | API returns JSON for researchers, 403 for members on `/records/`, 429 with `Retry-After` past rate limit. Cursor pagination works for >1000-record queries. |
| **5f** | Bulk download infrastructure + quarterly snapshot generator + DOI integration (EZID/DataCite free tier) | ~full day | Researcher can download Parquet or CSV of current quarterly snapshot. Each download produces a citation snippet with snapshot DOI. DOIs resolve. |
| **5g** | Admin tools (`/secure/admin/users/`, `/secure/admin/partners/`, `/secure/admin/audit/`, `/secure/admin/snapshots/`) | ~half day | Admin (Mike) can list users, change roles, view audit log, toggle partner opt-in/opt-out, issue/withdraw snapshot DOIs. |
| **5h** | Secure WREN at `/secure/wren/` with tier-aware data context | ~half day | Same WREN UI shell. System prompt swaps data context: members see aggregate-only context; researchers see micro-data context. Same engine, different config per spec §5.1. |
| **5i** | Terms of use page + governance documentation + citation snippet generator | ~half day | `/secure/terms/` shows ToU; application flow requires checkbox acceptance; every record-query response includes a `citation` field; download dialogs show the citation snippet. |
| **5j** | End-to-end testing with three test users (member, researcher, admin) executing representative workflows | ~half day | Three test accounts walk through their canonical workflows; bug list filed and closed in this PR; CI test suite (if any added) green. |

## Critical engineering notes

### Netlify Identity integration

Netlify Identity is configured via the Netlify dashboard (engineer asks Mike to enable it on the site once). Once enabled, the `netlify-identity-widget` JS library handles the login UI on the client; JWT tokens are sent in the `Authorization` header to Edge Functions. Edge Functions read `req.headers.get('authorization')` and validate the JWT against the Netlify Identity JWKS endpoint.

If Netlify Identity is being deprecated by Netlify (verify on first 5a touch), switch to **Netlify Auth** (the successor) or to **Auth0** (free tier covers 7500 active users). The auth-provider abstraction in the engineer's code should be thin enough that a swap is a one-file change.

### Anonymization at emit, not at query

Per Standing Orders §5 (privacy by build, not by runtime), anonymization is applied at the Phase 4.5 partner-pipeline emit stage, not at the secure-tier query stage. The `aggregate.py` / emit code from Phase 4.5+ gains a `--anonymization-tier {tier1,tier2,tier3}` flag and writes three cube variants:

- `secure/cube/tier1/admissions-cube.meta.json` + shards — full data, Mike only
- `secure/cube/tier2/admissions-cube.meta.json` + shards — anonymized per §4.1, k=5 suppression
- `data/cube/admissions-cube.meta.json` + shards — public, k=10 suppression (existing)

The serving infrastructure picks the right variant based on the user's role. No runtime anonymization logic; just file selection.

For the **initial 5a-5c ship** before partner data exists, all three tiers' content is generated from the synthetic n=1M cube with the appropriate anonymization rules applied. The synthetic cube already has no PII so anonymization is functionally a re-aggregation with different k thresholds and deeper grain at Tier 2/3.

### Audit log via Netlify Blobs

Each `/secure/*` request, regardless of tier, writes one JSON line to a Netlify Blobs store named `audit-log-<YYYY-MM>` (monthly partitioning for retention rotation). Per spec §5.2 shape. The write is fire-and-forget from the Edge Function; if it fails the request still succeeds (we don't gate user requests on audit infrastructure).

### Cite-able query URLs

Every UI query in Tier 2 surfaces produces a URL like:

```
https://wildlifestats.org/secure/research/records/?state=FL&year=2023&species=sea_turtle&snapshot=2026Q2
```

The `snapshot` parameter pins the query to a quarterly snapshot DOI; without it, the query is "live" against the current data. Researchers cite the pinned form for reproducibility; UI defaults to live for exploration.

## What is OUT of scope for Phase 5 entirely

- Payment infrastructure (free for all approved users)
- IRB review of any use case (separate governance phase if/when needed)
- Federated identity (Shibboleth, InCommon)
- Real partner records (those flow in via Phase 4.5 partnerships when DSAs are signed; secure tier ships at 5a-5j with the synthetic cube as the only data, anonymized per tier rules)
- Mobile app (web only)
- Multi-language UI (English only)
- Replication of BRWC's `/brwc/` for BRWC users (BRWC continues at askoak.michaeloak.com; this is a national platform, not a BRWC replacement)

## Out of scope until later phases

- API versioning beyond v1 (defer)
- GraphQL endpoints (REST only for now)
- Real-time data freshness indicators on every page (defer to Phase 6)
- A research-output catalog (papers published using WildlifeStats data) — future community-driven feature

## CI / safety

- Add a new CI job `secure-tier-auth-smoke` that hits `/secure/` unauthenticated and asserts 401, hits `/secure/api/v1/admin/users` unauthenticated and asserts 401. Cheap. Catches accidental gate removals.
- BRWC content guard continues to apply to the secure-tier source files. The guard is path-based; new `secure/` directories inherit the same scan rules.
- Anonymization rules in the aggregator have unit tests verifying that no Tier 2 record contains `partner_id` (only `partner_synthetic_id`), no raw dates, no raw lat/lon, no case_notes_text.

## Mike-facing application approval workflow

For the manual researcher-application queue (Tier 2 applicants who aren't auto-approved), the admin surface (`/secure/admin/users/`) shows pending applications. Mike clicks Approve or Decline. Approval triggers a Netlify Identity role assignment + a templated welcome email with the ToU and a getting-started guide. Decline sends a templated decline email with reason.

Architect default policy for manual review: approve if applicant has institutional affiliation + plausible use case + agrees to ToU. Decline if institution is unverifiable or use case is commercial-resale-oriented. Mike can adjust.

## Commit and merge

- Ten branches, ten sub-PRs, sequential.
- Branch naming: `engineer/phase5a-netlify-identity`, `engineer/phase5b-tier3-reference`, etc.
- Commit format: `feat(wildlifestats): Phase 5<letter> — <short description>`.
- Trailer: `Engineer: soar-aspen-beryl-heron`.
- Self-merge per §14 after CI green + Netlify preview smoke test.
- After each merge, append `## Resolution 5<letter>` entry to this order file. After 5j merges, move this file to `docs/handoff/closed/`.

## Open question Mike should answer when convenient (do not block)

The architect default DOI provider is EZID + DataCite (free up to 100 DOIs/year). The alternative is Zenodo (also free, simpler integration). Both are credible institutional choices. Architect ships against EZID + DataCite default. Mike can override during sub-PR 5f review if he has a preference.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 16:14 ET
