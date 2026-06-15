# WildStats law_watch federal field mapping

**Date:** 2026-06-15
**Author:** Codex
**Status:** Field-to-field normalization map for the federal-first `law_watch`
MVP
**Scope:** `federal_register_api` and `regulations_gov_api` only. No Congress or
state layer.

## 1. Purpose

The normalized `law_watch` schema now exists. The page contract now exists.

The next implementation blocker is narrower: how the two first federal sources
map into that schema field by field.

This note locks that mapping so the next engineer does not have to infer field
names or invent transforms while coding.

## 2. Verification basis

This mapping is grounded in official source materials verified on June 15,
2026:

- Federal Register API docs entry point:
  [federalregister.gov/developers/documentation/api/v1](https://www.federalregister.gov/developers/documentation/api/v1)
- Regulations.gov API docs:
  [open.gsa.gov/api/regulationsgov](https://open.gsa.gov/api/regulationsgov/)

Because the Federal Register docs page was CAPTCHA-gated from this environment,
the field list below was confirmed from live official API payloads instead of
from the docs page text alone.

Verified live payload examples used here:

- Federal Register document `2026-11634`, published June 10, 2026
- Regulations.gov document `FWS-R4-ES-2025-0210-0225`, posted June 10, 2026
- Regulations.gov docket `FWS-R4-ES-2025-0210`

## 3. Target normalized schema

This note maps into:

- `docs/handoff/wildlifestats-law-watch-normalized-schema-2026-06-15.md`

The target normalized fields are:

- `law_watch_id`
- `source_system`
- `source_native_id`
- `thread_key`
- `source_url`
- `source_document_url`
- `retrieved_at`
- `last_seen_at`
- `title`
- `short_summary`
- `action_type`
- `policy_stage`
- `source_authority`
- `agency_names`
- `government_level`
- `jurisdiction_scope`
- `topic_tags`
- `taxa_tags`
- `publication_date`
- `effective_date`
- `comment_deadline`
- `comment_open`
- `status_label`
- `docket_id`
- `document_number`
- `citation`
- `related_ids`
- `comment_url`
- `public_safe_for_display`
- `attribution_badge`
- `attribution_required`
- `license_type`
- `notes`

## 4. Shared normalization rules

1. Use the source detail endpoint when available, not only the search-result
   subset.
2. `source_url` should be the human-readable public page, not the API endpoint.
3. `retrieved_at` and `last_seen_at` are ingest timestamps, not source fields.
4. `topic_tags` and `taxa_tags` do not come directly from either API. They are
   a second-pass WildStats tagging layer.
5. `short_summary` should use the source-provided summary field when one exists.
   Do not generate LLM summaries in the first mapping pass.
6. `government_level` is always `federal` for this note.
7. `jurisdiction_scope` should default to `national_us` unless a later explicit
   tagging rule narrows it.

## 5. `federal_register_api` mapping

### 5.1 Confirmed useful live fields

From a live Federal Register document payload, the following fields are present
and useful for WildStats:

- `document_number`
- `title`
- `abstract`
- `type`
- `action`
- `publication_date`
- `effective_on`
- `comments_close_on`
- `comment_url`
- `html_url`
- `pdf_url`
- `citation`
- `agencies[]`
- `docket_ids[]`
- `regulation_id_numbers[]`
- `regulations_dot_gov_info`

### 5.2 Field map

| Normalized field | Federal Register field | Rule |
|---|---|---|
| `law_watch_id` | `document_number` | `lawwatch.federal_register_api.<document_number>` |
| `source_system` | literal | `federal_register_api` |
| `source_native_id` | `document_number` | direct copy |
| `thread_key` | `regulation_id_numbers[0]` else `regulations_dot_gov_info.docket_id` else first `docket_ids[]` | first durable grouping key available |
| `source_url` | `html_url` | direct copy |
| `source_document_url` | `pdf_url` | use PDF as deeper document link |
| `retrieved_at` | ingest timestamp | set at pull time |
| `last_seen_at` | ingest timestamp | set at pull time |
| `title` | `title` | direct copy |
| `short_summary` | `abstract` | direct copy, nullable |
| `action_type` | `type` plus `action` | map `Proposed Rule -> proposed_rule`, `Rule -> final_rule`, `Notice -> notice`, else `policy_update` |
| `policy_stage` | `type` plus `comments_close_on` | `Proposed Rule` with future deadline -> `proposal_open`; `Proposed Rule` with past or null deadline -> `proposal_closed`; `Rule` -> `finalized`; `Notice` -> `notice_only` |
| `source_authority` | literal | `Federal Register` |
| `agency_names` | `agencies[].name` else `agencies[].raw_name` | keep as array |
| `government_level` | literal | `federal` |
| `jurisdiction_scope` | derived constant | `national_us` for MVP |
| `topic_tags` | none | WildStats tagging layer |
| `taxa_tags` | none | WildStats tagging layer |
| `publication_date` | `publication_date` | direct copy |
| `effective_date` | `effective_on` | direct copy |
| `comment_deadline` | `comments_close_on` | direct copy |
| `comment_open` | `comments_close_on` | `true` when deadline exists and is on or after current date; else `false` |
| `status_label` | derived | `active_comment_period`, `newly_posted`, `comment_closed`, or `historical_reference` from stage and dates |
| `docket_id` | `regulations_dot_gov_info.docket_id` else first `dockets[].id` else first `docket_ids[]` | prefer Regulations.gov-style docket id |
| `document_number` | `document_number` | direct copy |
| `citation` | `citation` | direct copy |
| `related_ids` | `regulation_id_numbers[]`, `docket_ids[]`, `regulations_dot_gov_info.document_id` | flatten into array, omit nulls |
| `comment_url` | `comment_url` else first `dockets[].documents[].comment_url` | prefer explicit top-level value, else nested docket doc link |
| `public_safe_for_display` | constant | `true` |
| `attribution_badge` | constant | `Data via the Federal Register` |
| `attribution_required` | constant | `true` |
| `license_type` | constant | `public_domain` |
| `notes` | derived | note if item is a correction, reopening, or has no direct comment link |

### 5.3 Important implementation note

Federal Register is the best source for:

- title
- abstract
- action wording
- citation
- direct publication date

It may also expose downstream Regulations.gov linkage through
`regulations_dot_gov_info`, which is the safest bridge for cross-source
threading in the federal MVP.

## 6. `regulations_gov_api` mapping

### 6.1 Confirmed useful live fields

From a live Regulations.gov document payload, the following fields are present
and useful for WildStats:

- top-level `id`
- `attributes.title`
- `attributes.docAbstract`
- `attributes.documentType`
- `attributes.postedDate`
- `attributes.modifyDate`
- `attributes.commentEndDate`
- `attributes.commentStartDate`
- `attributes.effectiveDate`
- `attributes.openForComment`
- `attributes.withinCommentPeriod`
- `attributes.docketId`
- `attributes.frDocNum`
- `attributes.frVolNum`
- `attributes.agencyId`
- `attributes.originalDocumentId`
- `attributes.fileFormats[]`
- `attributes.withdrawn`

From a live docket payload, the following fields are additionally useful:

- top-level docket `id`
- `attributes.title`
- `attributes.dkAbstract`
- `attributes.docketType`
- `attributes.rin`

### 6.2 Field map

| Normalized field | Regulations.gov field | Rule |
|---|---|---|
| `law_watch_id` | top-level `id` | `lawwatch.regulations_gov_api.<id>` |
| `source_system` | literal | `regulations_gov_api` |
| `source_native_id` | top-level `id` | direct copy |
| `thread_key` | `attributes.docketId` | direct copy |
| `source_url` | derived from top-level `id` | `https://www.regulations.gov/document/<id>` |
| `source_document_url` | first `attributes.fileFormats[].fileUrl` where available | prefer PDF if present |
| `retrieved_at` | ingest timestamp | set at pull time |
| `last_seen_at` | ingest timestamp | set at pull time |
| `title` | `attributes.title` | direct copy |
| `short_summary` | `attributes.docAbstract` else docket `attributes.dkAbstract` | prefer document abstract, then docket abstract |
| `action_type` | `attributes.documentType` | `Proposed Rule -> proposed_rule`, `Rule -> final_rule`, `Supporting & Related -> supporting_document`, `Other -> policy_update` |
| `policy_stage` | `attributes.documentType`, `attributes.openForComment`, `attributes.withinCommentPeriod`, `attributes.withdrawn` | open proposed rule -> `proposal_open`; closed proposed rule -> `proposal_closed`; final rule -> `finalized`; open supporting document -> `docket_open`; withdrawn -> `historical_reference`; else `under_review` |
| `source_authority` | literal | `Regulations.gov` |
| `agency_names` | `attributes.agencyId` | store as one-element array until a federal agency-label crosswalk is added |
| `government_level` | literal | `federal` |
| `jurisdiction_scope` | derived constant | `national_us` for MVP |
| `topic_tags` | none | WildStats tagging layer |
| `taxa_tags` | none | WildStats tagging layer |
| `publication_date` | `attributes.postedDate` | normalize to date |
| `effective_date` | `attributes.effectiveDate` | direct copy |
| `comment_deadline` | `attributes.commentEndDate` | direct copy |
| `comment_open` | `attributes.openForComment` or `attributes.withinCommentPeriod` | boolean OR |
| `status_label` | derived | `active_comment_period`, `newly_posted`, `comment_closed`, or `historical_reference` from stage and dates |
| `docket_id` | `attributes.docketId` | direct copy |
| `document_number` | `attributes.frDocNum` | direct copy, nullable |
| `citation` | `attributes.frVolNum` else `attributes.sourceCitation` | prefer FR volume citation when present |
| `related_ids` | `attributes.originalDocumentId`, docket `attributes.rin` | flatten into array, omit nulls |
| `comment_url` | derived or null | use `null` in MVP unless a stable public comment URL is explicitly available from the payload or trusted source bridge |
| `public_safe_for_display` | constant | `true` |
| `attribution_badge` | constant | `Data via Regulations.gov` |
| `attribution_required` | constant | `true` |
| `license_type` | constant | `public_domain` |
| `notes` | derived | note when agency label is still an ID, when item is withdrawn, or when comment URL is not explicit |

### 6.3 Important implementation note

Regulations.gov is the best source for:

- docket identity
- document type
- posted and modified timestamps
- explicit comment-period booleans
- downloadable document file URLs

It is weaker than Federal Register for human-friendly agency labels unless a
crosswalk is added.

## 7. Cross-source bridge rules

These two sources should not be forced into perfect entity resolution in the
first implementation. Use the smallest safe bridge rules first:

1. If Regulations.gov `attributes.frDocNum` equals Federal Register
   `document_number`, treat them as related.
2. If Federal Register `regulations_dot_gov_info.docket_id` equals
   Regulations.gov `attributes.docketId`, treat them as related.
3. Use `thread_key` for grouping, not for hard dedupe in the first pass.

The federal MVP should tolerate seeing both a Federal Register record and a
Regulations.gov record for the same matter as long as each is clearly labeled
and same-source duplicates are suppressed.

## 8. What not to do in the first mapping pass

Do not:

- scrape HTML pages first when the API already supplies the field
- generate summaries when `abstract` or `docAbstract` is null
- invent topic tags directly from title text without a separate relevance layer
- treat `objectId` as a public-facing durable identifier
- block the whole feed on a missing explicit `comment_url` from Regulations.gov

## 9. Acceptance criteria

This mapping note is implementation-ready when:

1. an engineer can normalize Federal Register documents into the committed
   `law_watch` schema without guessing field names
2. an engineer can normalize Regulations.gov documents into the same schema
   without guessing field names
3. cross-source relationships are explicit but do not force brittle dedupe
4. page-contract fields can be satisfied from normalized output
