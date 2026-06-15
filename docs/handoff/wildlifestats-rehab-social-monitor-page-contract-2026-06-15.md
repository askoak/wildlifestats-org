# WildStats rehab_social_monitor page contract

**Date:** 2026-06-15
**Author:** Codex
**Status:** Page-level display contract for the metadata-first rehab social monitor
**Scope:** Public page behavior only. No UI code.

## 1. Purpose

This note defines what the first public `rehab_social_monitor` page should show
and how it should filter the normalized records defined in:

- `docs/handoff/wildlifestats-rehab-social-signal-normalized-schema-2026-06-15.md`

The goal is to let implementation move without reopening the public-lane
content policy.

## 2. MVP posture

The first `rehab_social_monitor` page is:

- metadata-first
- source-attributed
- organization-linked
- signal-oriented
- not a scraped-content archive

The page should help a user answer:

- which rehab centers are signaling noteworthy things publicly
- what kinds of signals are appearing
- which species or topics are surfacing
- where the signal is happening

## 3. Record inclusion rule

A `rehab_social_signal` record is eligible for public display only if:

1. `display_status = publish_ready`
2. `takedown_status = active`
3. `source_registry_id = flyway_social_roster`
4. `source_post_url` is present
5. `source_org_slug` joins cleanly to the public center registry
6. the record does not violate a later policy or quality rule

Records marked for review or suppression should not appear publicly.

## 4. Primary page view

The MVP should use a default card list, not a dense archive table.

Why:

- the page is interpretive and signal-first
- platform and organization identity matter
- cards handle short summaries and tags better than dense rows

A compact list view can be added later, but should not block MVP.

## 5. Default sort

Use:

1. `signal_detected_at` descending
2. then `confidence` descending

The page should feel current first, not encyclopedic.

## 6. Required filters

### `signal family`

Backed by:

- `signal_family`

User-facing values:

- `Phenology`
- `Baby season`
- `Disease concern`
- `Mortality event`
- `Weather event`
- `Window strike`
- `Training or education`

### `organization`

Backed by:

- `source_org_slug`
- `source_org_name`

### `state`

Backed by:

- `geo_state`
- fallback to joined center state when the signal-level geography is null

### `platform`

Backed by:

- `source_platform`

User-facing values:

- `Facebook`
- `Instagram`
- `TikTok`
- `YouTube`
- `Web`

### `topic`

Backed by:

- `topic_tags`

Initial useful topics:

- `baby-season`
- `hummingbirds`
- `monarchs`
- `raptors`
- `waterfowl`
- `hpai`
- `window-strikes`
- `storm-response`

### `time window`

Backed by:

- `signal_detected_at`
- optionally `event_date`

User-facing quick filters:

- `Last 7 days`
- `Last 30 days`
- `This season`

## 7. Optional later filters

Do not block MVP on these:

- `species_canonical`
- `event_category`
- `confidence band`
- `engagement_public`

## 8. Card contract

Each default card should show:

- `source_org_name`
- joined state label
- `source_platform`
- `signal_title`
- `summary_short`
- `topic_tags`
- `species_verbatim` if present
- `event_date` if present
- `signal_detected_at`
- outbound `source_post_url`

### What the card should not show

Do not show:

- raw post text
- copied image or video media
- internal prompt or extraction metadata
- take-down or review statuses on public cards

## 9. Compact row contract

If a later compact list is added, each row should show:

- `source_org_name`
- `source_platform`
- `signal_title`
- `signal_family`
- `event_date`
- `signal_detected_at`
- `source_post_url`

## 10. Detail panel or secondary view

If the page later adds an expanded panel, it may reveal:

- `geo_state`
- `geo_county_fips`
- `geo_locality_verbatim`
- `species_canonical`
- `confidence`
- `event_category`
- minimal provenance wording

Still do not expose raw post text or media.

## 11. Suppression rules

The public page must suppress:

1. `display_status != publish_ready`
2. `takedown_status != active`
3. missing `source_post_url`
4. missing org join
5. obvious duplicate records with the same `rehab_social_signal_id`
6. low-trust records flagged by a later quality rule

## 12. Empty-state contract

The page should support three empty states:

### No results after filtering

Message:

- `No current rehab social signals match these filters.`

### Roster active, no publish-ready signals in window

Message:

- `WildStats is monitoring approved public rehab-center sources, but no publish-ready signals appear in this time window.`

### Feed paused or under review

Message:

- `This monitor is temporarily showing limited results while source refresh or quality review is in progress.`

## 13. Page-level guardrails

The page should always communicate:

- monitored public sources only
- metadata plus link back to the original post
- no rehosting of raw content
- signals may be incomplete or later corrected

The page should not:

- become an archive of copied social content
- imply that all posts are equally verified
- expose suppressed or taken-down org content

## 14. Acceptance criteria

This page contract is implementation-ready when:

1. an engineer can render cards from `rehab_social_signal` records without new
   schema debate
2. filters map cleanly to normalized fields
3. the public page can exclude review and takedown records reliably
4. organization pages and the social monitor can share the same org slug
5. the monitor stays metadata-only from the first ship

## 15. Next adjacent task

After this note, the cleanest adjacent implementation-planning slice is a Wave
1 public-spine implementation note for:

- `wildstats_rehab_centers_registry`
- `wildstats_state_vet_ag_registry`
- `federal_register_api`
- `regulations_gov_api`

That would stay safely in the public-spine lane without colliding with the
other engineer's Flyway code work.
