# WildStats rehab_social_signal normalized schema

**Date:** 2026-06-15
**Author:** Codex
**Status:** Public-safe metadata schema note
**Scope:** Normalized public-facing record for the rehab social monitor. No raw
post text. No media rehosting. No app code.

## 1. Purpose

This note defines the first normalized `rehab_social_signal` record for the
planned WildlifeStats rehab or wildlife-hospital social monitor.

It is deliberately **not** the same thing as the secure Flyway extraction
record.

The secure Flyway extraction record exists to capture typed signal evidence with
provenance for internal or research-tier use. The public
`rehab_social_signal` record is the narrower, metadata-only derivative that can
safely back:

- `rehab_social_monitor`
- selected `flyway` public summaries
- later WREN public summaries about recent public-facing rehab signals

## 2. Product posture

The public social-monitor page is:

- metadata-plus-link
- source-attributed
- signal-oriented
- not a scraped-content archive

That means the normalized public record should store:

- who posted
- where it was posted
- what type of signal was detected
- what species or topic was involved
- where and when the event appears to have happened
- a short normalized summary

It should **not** store:

- raw post text
- image or video assets
- large verbatim quotes
- private or semi-private platform content

## 3. Unit of record

One `rehab_social_signal` record equals **one public-facing monitored post or
post-derived signal item** that WildStats chooses to surface in the public lane.

This is post-level and signal-level, not weekly cluster-level.

Examples:

- one center's public baby-songbird intake update
- one public oiled-bird event post
- one public HPAI concern post by a monitored wildlife hospital

If one post implies multiple independent signals, the first implementation
should still prefer one normalized record per surfaced signal item rather than a
single overloaded record.

## 4. Relationship to Flyway extraction records

The relationship should be:

1. raw scrape content stays outside WildStats public storage
2. Flyway extraction emits a secure typed record with `post_text_NOT_STORED:
   true`
3. WildStats derives a narrower `rehab_social_signal` record from that typed
   record for public display

So the public record is a downstream view, not a replacement for the extraction
pipeline.

## 5. Canonical normalized field set

### Identity and provenance

- `rehab_social_signal_id`
- `source_record_id`
- `source_registry_id`
- `source_org_slug`
- `source_org_name`
- `source_platform`
- `source_post_url`
- `source_posted_at`
- `signal_detected_at`

### Signal semantics

- `signal_family`
- `signal_id`
- `signal_title`
- `topic_tags`
- `species_canonical`
- `species_verbatim`
- `event_category`
- `confidence`

### Geography and timing

- `geo_state`
- `geo_county_fips`
- `geo_locality_verbatim`
- `event_date`
- `event_date_precision`

### Public display

- `summary_short`
- `attribution_badge`
- `attribution_required`
- `public_safe_for_display`
- `takedown_status`

### Optional operational metadata

- `engagement_public`
- `notes`

## 6. Required vs optional fields

### Required for the public MVP

- `rehab_social_signal_id`
- `source_registry_id`
- `source_org_slug`
- `source_org_name`
- `source_platform`
- `source_post_url`
- `signal_detected_at`
- `signal_family`
- `signal_title`
- `topic_tags`
- `confidence`
- `summary_short`
- `attribution_badge`
- `attribution_required`
- `public_safe_for_display`
- `takedown_status`

### Strongly preferred when available

- `source_record_id`
- `source_posted_at`
- `species_canonical`
- `species_verbatim`
- `geo_state`
- `geo_county_fips`
- `event_date`
- `event_date_precision`

### Optional in the first pass

- `signal_id`
- `geo_locality_verbatim`
- `event_category`
- `engagement_public`
- `notes`

## 7. Controlled vocabularies

### `source_registry_id`

- `flyway_social_roster`

Later extensions may introduce more monitored-source registries, but the first
public monitor should bind only to the existing Flyway roster.

### `source_platform`

- `facebook`
- `instagram`
- `tiktok`
- `youtube`
- `web`

### `signal_family`

- `phenology`
- `baby_season`
- `disease_concern`
- `mortality_event`
- `rescue_volume`
- `weather_event`
- `oiled_wildlife`
- `window_strike`
- `training_or_education`
- `other_monitored_update`

### `event_category`

- `first_of_season`
- `spike`
- `early_signal`
- `late_signal`
- `ongoing_update`
- `single_incident`

### `takedown_status`

- `active`
- `suppressed_org_request`
- `suppressed_policy`
- `suppressed_quality`

## 8. Field definitions

### `rehab_social_signal_id`

Stable WildStats id for the public-facing record.

Recommended pattern:

`rehabsocial.<org-slug>.<platform>.<fingerprint>`

The fingerprint can be derived from source URL plus signal type or event date.

### `source_record_id`

Optional link back to the secure Flyway extraction record id. Keep nullable so
the public schema does not require public exposure of the secure storage model.

### `source_registry_id`

The monitored-source registry that authorized this signal to exist. For the
first pass this is `flyway_social_roster`.

### `source_org_slug`

Primary join key back to `wildstats_rehab_centers_registry`.

### `source_org_name`

Public display label for the organization.

### `source_platform`

Public platform label.

### `source_post_url`

Canonical outbound link back to the original post or public source page.

### `source_posted_at`

Platform-post timestamp when recoverable. Keep nullable because some source
surfaces may not expose exact timestamps cleanly.

### `signal_detected_at`

When WildStats identified the signal. This is not the same thing as the event
date.

### `signal_family`

The primary signal class used for filter chips and public grouping.

### `signal_id`

Optional detailed mapping to an existing Flyway signal definition, for example:

- `phenology.first_of_season.hummingbird_spring`
- `hazard.hpai_outbreak`

Keep nullable because some public monitor items may be narrower page-safe
signals without a strict Flyway definition file behind them yet.

### `signal_title`

Short plain-language label for the card or list item.

Examples:

- `Baby songbirds arriving early`
- `Possible oiling event reported`
- `Public HPAI concern update`

### `topic_tags`

Array of flat filter tags. Initial examples:

- `baby-season`
- `hummingbirds`
- `monarchs`
- `raptors`
- `waterfowl`
- `hpai`
- `window-strikes`
- `storm-response`
- `marine-wildlife`
- `volunteer-training`

### `species_canonical`

Normalized species or taxon key when the post clearly maps to one.

### `species_verbatim`

The public-facing species phrase used by the source, kept short and normalized.
This is not a license to store long copied text.

### `summary_short`

One- to two-sentence normalized summary for public display.

Rules:

- no long direct quotes
- no copied raw post body
- no image description lifted verbatim from source text
- enough information for a user to understand why the item matters before
  clicking out

### `engagement_public`

Optional small metadata object for public counts if the source actor returns
them and policy permits their display. This should remain strictly optional.

Recommended subfields if used:

- `likes`
- `comments`
- `views`

Do not block the public monitor on this field.

## 9. Transformation rules from the secure extraction record

When deriving a public `rehab_social_signal` from a Flyway extraction record:

1. carry over `source_url`
2. carry over `source_org_id` only after mapping it to the public center slug
3. carry over signal semantics and geography
4. derive a short public summary
5. discard anything not needed for public display

Specifically, the public record should **not** expose:

- `extraction_prompt_hash`
- internal prompt versioning
- internal compliance notes except as folded into policy labels
- any raw scraped text

## 10. Join strategy

The intended join order is:

1. `flyway_social_roster` provides the monitored social source
2. `source_org_slug` joins to `wildstats_rehab_centers_registry`
3. center metadata adds organization name, state, and directory context
4. optional later joins add sector or firm-profile context

This is why `source_org_slug` is the key field in the public schema.

## 11. Public display subset

The first public card or table row needs only:

- `source_org_name`
- `source_platform`
- `signal_title`
- `summary_short`
- `topic_tags`
- `species_verbatim`
- `geo_state`
- `event_date`
- `confidence`
- `source_post_url`

Everything else can remain in the normalized backing record.

## 12. Red lines

1. No raw post text in the public record.
2. No image or video rehosting.
3. No public record created from a source that is not on the approved monitored
   roster.
4. No silent surface drift from metadata-plus-link into content republishing.
5. No public display of a record after an org-level take-down request.
6. No BRWC-only internal or private social material in this schema.

## 13. First implementation recommendation

The first engineer pass should:

1. derive this record only from `flyway_social_roster` monitored items
2. join on `source_org_slug` back to the center registry
3. keep `signal_id` optional
4. require `summary_short`, `source_post_url`, `signal_family`, and
   `takedown_status`
5. reject any attempt to persist raw post text locally

That gives WildlifeStats a public-safe rehab social monitor that is useful,
auditable, and cleanly separated from the secure Flyway extraction layer.
