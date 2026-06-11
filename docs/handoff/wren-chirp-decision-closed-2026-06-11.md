# WREN chirp decision — closed (WildlifeStats lane)

**Date:** 2026-06-11 11:10 ET
**Seat:** `measured-fern-jasper-thrush`
**Status:** Closed. Durable. Does not expire.

## Decision

**WildlifeStats will not ship a WREN chirp on this product, now or ever.**

This is the file-of-record on the WildlifeStats side so future sessions inherit the decision without re-deriving it.

## Reasoning (in brief)

WildlifeStats is positioned as a national institutional research framework for foundation program officers, sector funders, state agency staff, academic researchers, and accredited rehab-center boards. The published brand brief mandates a minimalist institutional aesthetic and explicitly lists "startup aesthetic," "dashboard feel," "flashy consulting graphics," and "AI-generated visual feel" under "Avoid." A click-triggered chirp on a bird mascot lands hostile against that tone.

BRWC's chirp remains a clean fit for BRWC's public-facing rehab-center audience (visitor families, school groups, general-public donors). Different audience, different register — no judgment about the chirp itself.

## Canonical context

The full cross-lane note, the BRWC architect's watch-then-fork recommendation, and the WildlifeStats follow-up adjudication live in the originating lane per Standing Orders §20:

- BRWC repo: `askoak-web`, file `docs/handoff/CROSS-LANE-wren-chirp-2026-06-11.md`
- Merged via PR #283 (askoak-web), commit 895040b

## What this decision binds

- WildlifeStats will not reference any BRWC-hosted audio asset.
- WildlifeStats will not maintain a shared NPM package, submodule, or vendored copy of the BRWC chirp module.
- WildlifeStats will not track BRWC's behavior contract (once-per-session, localStorage toggle, reduced-motion default).
- If a future WildlifeStats roadmap entertains a WREN-style helper surface, that surface will be silent.

## What this decision does NOT bind

- The WREN mascot, help-bot card, onboarding picker, or any non-audio WREN surface element remains an open question on the WildlifeStats roadmap and is unaffected by this decision.
- The decision is about audio, not about WREN as a concept.

## When this decision expires

Never. If BRWC's chirp becomes a beloved feature with measurable engagement lift, the WildlifeStats answer stays the same — different audience.

— `measured-fern-jasper-thrush`, 2026-06-11 11:10 ET
