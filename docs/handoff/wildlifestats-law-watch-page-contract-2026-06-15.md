# WildStats law_watch page contract

**Date:** 2026-06-15
**Author:** Codex
**Status:** Page-level display contract for the federal-first law watch MVP
**Scope:** Public page behavior only. No UI code.

## 1. Purpose

This note defines what the first public `law_watch` page should show and how it
should filter the normalized records defined in:

- `docs/handoff/wildlifestats-law-watch-normalized-schema-2026-06-15.md`

The goal is to prevent the next implementation step from reopening page scope
or mixing design decisions into the ingest layer.

## 2. MVP posture

The first `law_watch` page is:

- federal-first
- metadata-plus-link
- filterable
- not a legal-advice tool
- not a full-text policy archive

The page should expose the most decision-useful metadata first:

- what the item is
- which agency issued it
- whether comment is open
- when the next important date is
- why WildStats thinks it is in-scope

## 3. Record inclusion rule

A `law_watch` record is eligible for public display only if:

1. `relevance_status = in_scope`
2. `jurisdiction_level = federal` for the MVP
3. `source_id` is one of:
   - `federal_register_api`
   - `regulations_gov_api`
4. `title` and `source_url` are present
5. the item is not blocked by a later editorial or policy flag

Records marked `review_needed` should stay out of the public page until the
filter is proven.

## 4. Primary page views

The first page contract should support two display modes:

### 4.1 Default card list

Best for general users scanning:

- newest or most actionable items
- open comment periods
- topic-tagged notices and dockets

### 4.2 Compact table or list view

Best for heavier users scanning many items:

- title
- agency
- stage
- published date
- comment deadline
- source

The page can ship with cards only, but the data contract should not prevent a
later compact view.

## 5. Default sort

Use this order:

1. open-comment items first
2. among open-comment items, `comment_deadline` ascending
3. otherwise `last_action_at` descending

This keeps the page useful rather than purely chronological.

## 6. Required filters

The MVP page should expose these filters:

### `stage`

Backed by:

- `status_stage`
- or page-normalized labels derived from it

User-facing values:

- `Open for comment`
- `Proposed`
- `Final`
- `Comment closed`
- `Other federal action`

### `source`

Backed by:

- `source_id`

User-facing values:

- `Federal Register`
- `Regulations.gov`

### `topic`

Backed by:

- `topic_tags`

Initial useful tags:

- `Endangered species`
- `Migratory birds`
- `Habitat`
- `Wildlife rehabilitation`
- `Disease surveillance`
- `Marine mammals`

### `agency`

Backed by:

- `agency_names`

MVP should use a small multi-select or single-select list, not free-form
taxonomy.

### `timing`

Backed by:

- `comment_open`
- `publication_date`
- `comment_deadline`

User-facing quick filters:

- `Comment open now`
- `Posted in last 30 days`
- `Deadline this week`

## 7. Optional later filters

Do not block MVP on these:

- `taxa_tags`
- `jurisdiction_scope`
- `source_authority`
- `bill vs rulemaking` once Congress or state layers are added

## 8. Card contract

Each default page card should show:

- `title`
- `short_summary`
- `source_authority`
- `agency_names`
- `status_stage` as a badge
- `publication_date`
- `comment_deadline` if present
- `topic_tags`
- primary outbound `source_url`

### Card labels that matter

The most important badge labels are:

- `Comment open`
- `Proposed rule`
- `Final rule`
- `Notice`
- `Docket`

These should be derived from normalized fields, not hand-authored per card.

## 9. Compact row contract

If a table-like view is added, each row should show:

- `title`
- `agency_names`
- `status_stage`
- `publication_date`
- `comment_deadline`
- `source_authority`

Nothing else is required for MVP scanning.

## 10. Detail panel or secondary view

If the page later adds an expanded panel, it may reveal:

- `docket_id`
- `document_number`
- `citation`
- `effective_date`
- `related_ids`
- `notes`

These should not clutter the default card.

## 11. Suppression rules

The public page must suppress:

1. records with `relevance_status != in_scope`
2. records missing `source_url`
3. records missing `title`
4. duplicate same-source records with the same `source_record_id`
5. obviously stale or placeholder items emitted by a broken fetch

## 12. Empty-state contract

The page should support three empty states:

### No results after filtering

Message:

- `No current law-watch items match these filters.`

### No open comment periods

Message:

- `No federal wildlife-related items currently show an open public comment period in this view.`

### Source unavailable or feed paused

Message:

- `This tracker is temporarily showing limited results while source refresh is in review.`

This is better than silently showing a blank page.

## 13. Page-level guardrails

The page should always state:

- federal-first
- metadata sourced from public government systems
- links out to official documents
- not legal advice

The page should not:

- mirror full legal text
- show media overlays as if they were authoritative law records
- auto-publish borderline keyword matches

## 14. Acceptance criteria

This page contract is implementation-ready when:

1. an engineer can render cards from normalized `law_watch` records without new
   schema debate
2. the filters map cleanly to existing normalized fields
3. the page can suppress `review_needed` items
4. users can find open comment periods quickly
5. the federal-first MVP can ship without waiting for state or bill layers

## 15. Next adjacent task

After this note, the cleanest adjacent page contract is:

- `rehab_social_monitor`

That is the other public page family now structurally ready for display
definition.
