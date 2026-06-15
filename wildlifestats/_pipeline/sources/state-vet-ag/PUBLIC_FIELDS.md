# Public Field Subset — State Vet/Ag Registry (`agencies.yaml`)

_Wave 1 Step 1 audit — 2026-06-15_

This file documents which fields from `agencies.yaml` are safe to render publicly on the
WildlifeStats website, which are internal-only, and the rationale for each classification.

Audit result: **51 jurisdictions** — all 50 states + District of Columbia.  
Missing `jurisdiction` field: **0** (all records have a 2-letter state code).  
All jurisdictions present: **AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME
MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY**.

---

## DISPLAY — render publicly

| Field | Notes |
|-------|-------|
| `jurisdiction` | 2-letter state/DC code — used for page routing |
| `state_name` | Full state name — display |
| `agency_name` | Official agency name — display |
| `contact_phone` | Agency main phone — public |
| `primary_url` | Agency website — public |
| `wildlife_disease_program_url` | Program-specific page if different from `primary_url` — public |

## INTERNAL — do not render publicly

| Field | Rationale |
|-------|-----------|
| `parent_department` | Org-chart detail; agency_name already conveys the relevant entity |
| `state_veterinarian_name` | Named individual in a role that changes; display on page would require active maintenance to stay current |
| `state_veterinarian_url` | Same rationale; rendered via primary_url instead |
| `contact_email` | State official's government email address — public record but not the right contact for wildlife emergency referrals (use phone or website) |
| `hq_address` | Administrative HQ address; not a wildlife intake address |
| `reportable_diseases_url` | Research/researcher field; not relevant to the public emergency directory |
| `publishes_dashboard` | Research field |
| `dashboard_url` | Research field |
| `notes` | Internal research notes |
| `gaps` | Internal data-quality tracking |
| `sources` | Internal provenance |

## Rationale for state_veterinarian_name as INTERNAL

State veterinarian names are public officials; their names and titles appear on official .gov
sites. However:
1. Names change when administrations or appointments turn over.
2. The wildlife911 directory page is a public emergency reference — it should point to the
   agency and its stable URL, not a named individual whose tenure may change.
3. Displaying a stale name could misdirect callers.

Future maintainers may choose to display this field with an explicit "as of [date]" caveat
and a verified freshness check in the refresh cycle.

## Ambiguous fields

`state_veterinarian_name` and `contact_email` were considered for DISPLAY but classified
INTERNAL for the reasons documented above. This does not require a blockers note since the
classification is unambiguous in the context of the wildlife911 emergency directory.

## Audit conducted by

WO-2026-06-15-wave1-public-spines-wildlife911 (Wave 1 Step 1), Claude Code A.
