# Public Field Subset — Sector Funders Registry (`funders.yaml`)

_Public page audit — 2026-06-16_

This file documents which fields from `funders.yaml` are safe to render on the
public WildlifeStats funders page.

---

## DISPLAY — render publicly

| Field | Notes |
|-------|-------|
| `common_name` | Public-facing short label |
| `legal_name` | Useful when the public-facing label is abbreviated |
| `type` | Public-safe classification for filtering |
| `ein` | Public record where already verified and present in the registry |
| `primary_url` | Organization website |
| `grants_program_url` | Primary program page |
| `annual_grants_total_usd_approx` | Approximate disclosed annual grants total |
| `focus_areas` | Public-safe tags for filtering and scanning |
| `eligibility_summary` | Short prose summary already curated for public reading |
| `application_deadlines_url` | Program or deadline page |
| `contact_email` | Only if already intentionally listed in the registry |

## INTERNAL — do not render publicly by default

| Field | Rationale |
|-------|-----------|
| `sources` | Provenance is important, but the public MVP page links to the official program surface rather than every research source used to curate the row |

## Notes

- This registry is a local curated directory, not a live scrape.
- Public pages should carry a freshness warning because deadlines and
  invitation-only posture can change.
- Adding new fields to the page should be an explicit contract decision rather
  than an accidental spillover from the YAML source.
