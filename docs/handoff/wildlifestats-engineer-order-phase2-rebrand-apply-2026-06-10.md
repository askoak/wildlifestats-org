# Engineer order — Phase 2: rebrand apply

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer
**Date:** 2026-06-10 ~14:38 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Order #2 / Phase 1.5 merges)
**Authority:** §13 elevated ship + §14 self-merge.
**Single concern:** apply the Phase 2 rename ledger mechanically.

## Source of truth

`docs/handoff/wildlifestats-rename-ledger-phase2-2026-06-10.md` — every change in this PR is specified there. This order is just the dispatch.

## Scope

Apply, in one PR:

1. §3.1 Section title canonicalization across all section landings + header nav.
2. §3.2 Homepage final copy.
3. §3.3 "What this is / what this isn't" final two-column.
4. §3.4 Section landing final placeholder paragraphs.
5. §3.5 Methodology / Governance / About final placeholder copy.
6. §2 Google Fonts `<link>` for Source Serif Pro on every page (if not already loaded in Phase 1).
7. §4 Logo slot — placeholder `assets/img/logo.svg`, header swap from text wordmark to `<a class="brand">` block, CSS additions in `assets/css/site.css`.

## Out of scope

Palette tokens (UNCHANGED per ledger §1). Real logo file (slot only — Mike's v2.0 Gemini runs are in flight, drop-in later). Section content (Phase 4). Data (Phase 3). SEO / sitemap / OpenGraph (Phase 6).

## Acceptance criteria

1. Every section's `<h1>` matches the ledger §3.1 right column.
2. Header nav labels match the new `<h1>` titles.
3. Each section landing's kicker reads `RESEARCH SECTION` (not the long descriptive name).
4. Homepage paragraph copy is verbatim from ledger §3.2 (two paragraphs).
5. Homepage two-column "What this is / What this isn't" is verbatim from §3.3.
6. Each section landing paragraph is verbatim from §3.4.
7. Methodology / Governance / About paragraphs are verbatim from §3.5.
8. Header renders the `<a class="brand">` block with placeholder `logo.svg` at 40px desktop / 32px mobile; kicker text reads "National Wildlife Rehabilitation Research Framework" in uppercase letter-spaced sans.
9. CI green: BRWC content guard, link check, HTML validate.
10. Manual visual QA on desktop (1280px) and mobile (375px) — no horizontal scroll, no broken layout.
11. Source Serif Pro loads from Google Fonts on every page (`display=swap`).

## Commit and merge

- Branch: `engineer/phase2-rebrand-apply`.
- Commit: `feat(wildlifestats): apply Phase 2 rebrand — final copy, section titles, logo slot`. Body cites the rename ledger.
- Trailer: `Engineer: <your-seat-sig>`.
- Self-merge per §14 once acceptance criteria pass on the Netlify preview.
- After merge, append `## Resolution` to this order file with merge commit hash; move to `docs/handoff/closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:38 ET
