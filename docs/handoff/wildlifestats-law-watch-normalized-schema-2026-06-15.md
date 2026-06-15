# WildStats law_watch normalized schema

**Date:** 2026-06-15
**Author:** Codex
**Status:** Federal-first schema note
**Scope:** Normalized metadata schema for the first WildlifeStats `law_watch`
record type. No code. No state layer yet.

## 1. Purpose

This note defines the first normalized record shape for the WildlifeStats
wildlife-law and proposed-change tracker.

It is designed for the federal-first MVP already recommended in the page
roadmap:

- `federal_register_api`
- `regulations_gov_api`

`congress_gov_api` and `openstates_api` are deliberately out of the first
schema pass. The point is to lock a stable federal metadata spine first, then
extend carefully.

## 2. Product posture

The `law_watch` surface is a metadata tracker, not a legal research database
and not a law-firm product.

The record model therefore assumes:

- store normalized metadata only
- link out to the canonical government document or docket
- do not store or summarize full legal text as if WildStats were the authority
- do not imply legal advice

## 3. Unit of record

One `law_watch` record equals **one public government document or docket-facing
action item** that WildStats may list on the page.

Examples:

- one Federal Register proposed rule
- one Federal Register notice
- one Regulations.gov docket document
- one comment-period entry that has a discrete public landing page

This first schema does **not** try to collapse all related federal actions into
one perfect master thread. Instead:

- `law_watch_id` identifies the normalized record
- `thread_key` is optional and exists for later clustering

That keeps the MVP simple and avoids brittle dedupe logic.

## 4. Canonical normalized field set

Each `law_watch` record should carry these fields.

### Identity and provenance

- `law_watch_id`
- `source_system`
- `source_native_id`
- `thread_key`
- `source_url`
- `source_document_url`
- `retrieved_at`
- `last_seen_at`

### Core public display

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

### Dates and status

- `publication_date`
- `effective_date`
- `comment_deadline`
- `comment_open`
- `status_label`

### Linking and related ids

- `docket_id`
- `document_number`
- `citation`
- `related_ids`
- `comment_url`

### WildStats governance fields

- `public_safe_for_display`
- `attribution_badge`
- `attribution_required`
- `license_type`
- `notes`

## 5. Required vs optional fields

### Required for the federal MVP

- `law_watch_id`
- `source_system`
- `source_native_id`
- `source_url`
- `title`
- `action_type`
- `policy_stage`
- `source_authority`
- `agency_names`
- `government_level`
- `publication_date`
- `comment_open`
- `public_safe_for_display`
- `attribution_badge`
- `attribution_required`
- `license_type`
- `retrieved_at`

### Strongly preferred when available

- `short_summary`
- `comment_deadline`
- `docket_id`
- `document_number`
- `citation`
- `status_label`
- `topic_tags`
- `taxa_tags`

### Optional in the first pass

- `thread_key`
- `effective_date`
- `related_ids`
- `comment_url`
- `notes`

## 6. Controlled vocabularies

### `source_system`

- `federal_register_api`
- `regulations_gov_api`
- later: `congress_gov_api`
- later: `openstates_api`

### `action_type`

- `notice`
- `proposed_rule`
- `final_rule`
- `rulemaking_docket`
- `supporting_document`
- `comment_request`
- `policy_update`

### `policy_stage`

- `notice_only`
- `proposal_open`
- `proposal_closed`
- `finalized`
- `docket_open`
- `docket_closed`
- `under_review`

### `government_level`

- `federal`
- later: `state`

### `jurisdiction_scope`

- `national_us`
- `selected_states`
- `species_range_specific`
- `program_specific`

### `status_label`

- `active_comment_period`
- `newly_posted`
- `effective_now`
- `comment_closed`
- `historical_reference`

## 7. Field definitions

### `law_watch_id`

Stable WildStats id. Recommended pattern:

`lawwatch.<source_system>.<stable_native_key>`

Examples:

- `lawwatch.federal_register_api.2026-12345`
- `lawwatch.regulations_gov_api.fws-hq-es-2026-0001`

### `source_system`

The exact registry source that produced the record.

### `source_native_id`

The source's own durable identifier for the document or docket item. This is
what allows refresh and dedupe without guessing from title text.

### `thread_key`

Optional WildStats clustering key when multiple records clearly belong to the
same policy matter. This should stay nullable in the first implementation.

Recommended use:

- populate only when the relationship is obvious
- do not block ingest if `thread_key` is unknown

### `source_url`

Canonical public landing page WildStats should link users to first.

### `source_document_url`

Optional deeper link when the landing page and the document page are separate.

### `title`

Canonical public title for display. Preserve the government title closely.

### `short_summary`

One- to two-sentence WildStats summary of what the item is. This is an
editorial metadata field, not a replacement for the primary source.

### `action_type`

The document or docket class. Keep this source-normalized, not page-copy-like.

### `policy_stage`

Where the action sits in the public process. This is the most important filter
for users after date.

### `source_authority`

Human-readable authority label, for example:

- `Federal Register`
- `Regulations.gov`

### `agency_names`

Array of agencies or departments tied to the record.

### `topic_tags`

Controlled topical tags used for filtering. Initial examples:

- `endangered_species`
- `migratory_birds`
- `avian_influenza`
- `marine_mammals`
- `habitat`
- `wildlife_rehabilitation`
- `disease_surveillance`
- `transport_or_permitting`

### `taxa_tags`

Optional array for taxon-oriented tagging when the record clearly maps to a
species or group.

### `comment_deadline`

Nullable date. Present when the public source explicitly provides a comment
deadline.

### `comment_open`

Boolean page filter, computed from source metadata and current status. This is
more useful to users than raw dates alone.

### `docket_id`

Nullable but important. Primary discussion-thread key for rulemaking items.

### `document_number`

Nullable source-native identifier for document-level references.

### `citation`

Formal citation string when the source provides one, especially valuable for
Federal Register items.

## 8. Source mapping guidance

## 8.1 Federal Register API

Expected normalized posture:

- one record per Federal Register item
- `source_system = federal_register_api`
- `government_level = federal`
- `source_authority = Federal Register`
- likely high-value fields: title, agencies, publication date, document number,
  citation, abstract-style summary, action class, comment dates when present

Best use:

- new notices
- proposed rules
- final rules
- public-facing regulatory actions that should appear in a wildlife policy feed

## 8.2 Regulations.gov API

Expected normalized posture:

- one record per docket document or public action item
- `source_system = regulations_gov_api`
- `government_level = federal`
- `source_authority = Regulations.gov`
- likely high-value fields: docket id, document id, title, agency, comment
  deadline, comment URL, document type

Best use:

- comment tracking
- docket-level follow-through
- supporting documents for active rulemaking

## 9. Dedupe and clustering rule

The first implementation should follow this rule:

1. Normalize each source item into its own `law_watch` record.
2. Deduplicate only exact same-source duplicates using `source_native_id`.
3. Use `thread_key` later for cross-source clustering when a Federal Register
   item and a Regulations.gov docket obviously describe the same matter.

Do **not** block the federal MVP on perfect cross-source entity resolution.

## 10. Public display subset

The first public `law_watch` card or table row should need only:

- `title`
- `short_summary`
- `source_authority`
- `agency_names`
- `policy_stage`
- `publication_date`
- `comment_deadline`
- `comment_open`
- `topic_tags`
- `source_url`

Everything else can remain in the normalized backing record.

## 11. Red lines

1. No full-text legal mirror.
2. No legal-advice phrasing.
3. No pretending keyword matches equal wildlife relevance without a topic filter
   pass.
4. No state-layer expansion until the federal schema proves stable.
5. No media-source overlays in the canonical law record. News context belongs in
   a separate layer later.

## 12. First implementation recommendation

The first engineer pass should:

1. normalize `federal_register_api` and `regulations_gov_api` only
2. emit one document-level `law_watch` record per item
3. keep `thread_key` nullable
4. filter the first MVP to wildlife-relevant federal items only
5. store metadata plus canonical outbound links, nothing more

That gives WildStats a credible law-watch backbone without overbuilding the
first version.
