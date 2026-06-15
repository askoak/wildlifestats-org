# Public Field Subset — Rehab-Center Registry (`centers.yaml`)

_Wave 1 Step 1 audit — 2026-06-15_

This file documents which fields from `centers.yaml` are safe to render publicly on the
WildlifeStats website, which are internal-only, and the rationale for each classification.

Audit result: **181 centers** across all 50 states + DC.  
Missing slugs: **0**.  Duplicate slugs: **0**.  
Missing phone or intake URL: **0**.  
Note: The WO spec referenced a `primary_taxa` field; this field does not exist in the actual
schema. The equivalent information is encoded in the `services.accepts_*` boolean fields,
which are fully public-safe and documented below.

---

## DISPLAY — render publicly

| Field | Notes |
|-------|-------|
| `common_name` | Organization's public-facing name |
| `city` | City of operations |
| `state` | 2-letter state code |
| `primary_url` | Organization website — public |
| `wildlife_help_url` | Wildlife intake / help page — primary call-to-action |
| `contact_phone` | Main organization phone — public |
| `emergency_hotline` | 24/7 hotline if different from main — public |
| `intake_hours` | Operating hours for intake — public (omit if empty) |
| `mission_excerpt` | Short org description — public |
| `status` | Used for filtering: only render `active` records |
| `services.accepts_birds` | Public-safe boolean for taxa tags |
| `services.accepts_mammals` | Public-safe boolean for taxa tags |
| `services.accepts_reptiles` | Public-safe boolean for taxa tags |
| `services.accepts_amphibians` | Public-safe boolean for taxa tags |
| `services.accepts_marine` | Public-safe boolean for taxa tags |
| `services.accepts_rabies_vector` | Public-safe boolean for taxa tags |

## INTERNAL — do not render publicly

| Field | Rationale |
|-------|-----------|
| `slug` | Internal join key / URL slug (not a display value) |
| `legal_name` | Corporate legal name used for EIN matching; not needed on directory pages |
| `ein` | Tax identifier — publicly available via ProPublica/IRS but not a standard directory display field |
| `county_fips` | Internal geographic code for pipeline joins |
| `contact_email` | May be a personal or shared inbox; use phone/URL for public emergency directory |
| `intake_address` | Physical drop-off address — classified INTERNAL to avoid misuse as a 24/7 arrival address (contact first); renderers may expose this for confirmed drop-off centers in future |
| `leadership.executive_director` | Named individual; not critical for emergency directory |
| `leadership.medical_director` | Named individual; not critical for emergency directory |
| `capacity.*` | Research/analysis fields; not meaningful for public emergency use |
| `notes` | Internal research notes, not publication-ready |
| `source_urls` | Internal provenance tracking |
| `social.*` | Social media URLs — secondary; not needed for emergency directory |
| `news_or_blog_url` | Secondary; not needed for emergency directory |
| `newsletter_signup_url` | Secondary |
| `patient_stories_url` | Secondary |
| `annual_reports_url` | Secondary (transparency link; may be added in future) |
| `most_recent_annual_report_pdf` | Secondary |
| `about_url` | Secondary; primary_url already links to org |
| `accreditations` | Secondary trust signal; may be added in future |

## AMBIGUOUS — classification notes

No fields were classified as ambiguous. The `intake_address` classification as INTERNAL is
a conservative choice: physical addresses are public records, but the directory purpose
(emergency phone/web referral) is served by phone + URL. A future render pass may expose
`intake_address` for centers whose `intake_hours` confirm scheduled drop-offs.

## Join keys

- `slug` is the internal join key for page URLs and analytics.  
- `ein` is the join key for the Form 990 financial ingestion pipeline (Phase 8b).  
  Neither is rendered in public HTML.

## Audit conducted by

WO-2026-06-15-wave1-public-spines-wildlife911 (Wave 1 Step 1), Claude Code A.
