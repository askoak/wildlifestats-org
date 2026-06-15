# WildStats master source registry operational fields note

**Date:** 2026-06-15
**Author:** Codex
**Status:** Support note for attribution and refresh representation

## Purpose

This note explains how the first canonical registry should represent:

- attribution-helper data
- cache posture
- refresh cadence

These fields are included in `master-source-registry.yaml`. This note explains
how to use them without creating a schema fork.

They carry source-governance policy only. They do not authorize copying BRWC
corpus material, patient data, raw comments, or BRWC-specific operational
payloads into WildStats.

## Attribution representation

Each record should carry three minimum attribution fields:

- `attribution_badge`
- `attribution_required`
- `license_type`

Recommended behavior:

- `attribution_badge` is the short render string used on public cards or data
  panels
- `attribution_required` is the policy flag that tells a surface whether the
  badge must travel with displayed output
- `license_type` is not the display string; it is the normalized policy class

This mirrors the BRWC lesson that attribution should be rendered centrally, not
re-authored per surface.

## Refresh representation

Each record should carry three operational refresh fields:

- `cache_posture`
- `refresh_cadence`
- `refresh_mode`

Recommended interpretation:

- `cache_posture` describes how WildlifeStats should hold the source:
  local-curated, cached-reference, derived snapshot, cautious live query, or
  request-only
- `refresh_cadence` describes how often the source reasonably changes
- `refresh_mode` describes how WildlifeStats should refresh it operationally

Examples:

- eBird taxonomy: `cached_reference` + `monthly` + `scheduled_pull`
- GBIF occurrence backbone: `periodic_snapshot` + `weekly_or_on_demand` +
  `scheduled_pull`
- local curated YAML registry: `curated_local_registry` + `manual_periodic` +
  `manual_curated`
- WRMD: `partner_request_only` + `request_based` + `request_driven`

## Why keep these fields in the registry

These fields belong in the registry because they answer questions later sessions
should not have to rediscover:

- how should this source be shown?
- does it need visible attribution?
- should we cache it or query it live?
- how often should it refresh?
- does it require secrets or partner coordination?

That is source-governance data, not page-copy detail.
