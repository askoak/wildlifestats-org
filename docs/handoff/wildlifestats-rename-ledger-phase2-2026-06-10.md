# Phase 2 rename ledger + palette tokens

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 14:35 ET
**Status:** Source of truth for the Phase 2 rebrand-apply engineer order. The engineer applies this mechanically. No interpretation, no creative liberty.

This file is read by Engineer Order #3 (Phase 2 rebrand-apply). It exists as its own file so it can be edited without re-issuing the order.

## §1 — Palette tokens (final)

The Phase 1 framework ships defaults in `assets/css/tokens.css`. Phase 2 replaces the values below — variable names stay identical so the swap is mechanical.

| Token | Phase 1 default | Phase 2 final | Role |
|---|---|---|---|
| `--color-ink` | `#1F2A2A` | `#1F2A2A` | Primary text. UNCHANGED. |
| `--color-muted` | `#6B6B65` | `#6B6B65` | Secondary text, captions. UNCHANGED. |
| `--color-paper` | `#FAF6EC` | `#FAF6EC` | Page background. UNCHANGED. |
| `--color-rule` | `#DDD8CA` | `#DDD8CA` | Hairlines, borders. UNCHANGED. |
| `--color-slate` | `#2A3F52` | `#2A3F52` | Primary brand. UNCHANGED. |
| `--color-clay` | `#B96F4D` | `#B96F4D` | Accents, links. UNCHANGED. |
| `--color-sage` | `#6B8264` | `#6B8264` | Secondary accent. UNCHANGED. |

The Phase 1 architect default IS the Phase 2 ratified palette. No edits to `tokens.css` needed in Phase 2 for colors.

If Mike later revises the palette after seeing it on the live site, that's a Phase 2.1 fast-follow PR — one file changed, three lines of CSS, ~5 minutes. The token indirection is exactly what makes that cheap.

## §2 — Typography tokens (final)

Same story: Phase 1 defaults are ratified.

| Token | Phase 1 default | Phase 2 final |
|---|---|---|
| `--font-serif` | `'Source Serif Pro', Georgia, …` | UNCHANGED. |
| `--font-sans` | system stack | UNCHANGED. |
| `--font-mono` | system stack | UNCHANGED. |

Add to Phase 2 the Google Fonts `<link>` for Source Serif Pro in the `<head>` of every page (Phase 1 declared the family but does not load the webfont). Use `preconnect` + `display=swap`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600&display=swap">
```

If Phase 1 already loaded the font, no change.

## §3 — String rename ledger

There is **no BRWC content to rename** in this repo (Phase 1 was built from first principles, not forked). The rename ledger here is shorter than the master plan anticipated and is limited to:

1. **Tone / framing tightening** on the Phase 1 placeholder copy that's slightly too soft for the national-research register.
2. **Section title canonicalization** (Phase 1 used working titles; some get final names in Phase 2).

If the engineer encounters ANY string in the repo that looks BRWC-derived and isn't on this ledger, stop and file an INBOX file — do not invent a replacement. The CI BRWC content guard (Phase 1.5) should already block such strings from being committed, so this case should be rare or impossible.

### §3.1 Section title canonicalization

| File / location | Phase 1 working title | Phase 2 final title |
|---|---|---|
| `/one-health/index.html` `<h1>` | "One Health hub" | "One Health" |
| `/parks/index.html` `<h1>` | "National Parks lens" | "National Parks" |
| `/wildlife/index.html` `<h1>` | "Wildlife encyclopedia" | "Wildlife" |
| `/data/index.html` `<h1>` | "National database" | "Data" |
| `/ingest/index.html` `<h1>` | "Multi-format ingestion sandbox" | "Ingestion methodology" |
| Header nav (all pages) | matches `<h1>` of each section | Same as the new `<h1>` titles |

The kicker line above each `<h1>` keeps the longer descriptive name (e.g. kicker "One Health" → h1 "One Health" reads redundantly; in Phase 2, change the kicker to `RESEARCH SECTION` on every section landing so the kicker provides context, not duplication).

### §3.2 Homepage copy tightening

Phase 1 homepage description: 3–4 sentences of placeholder copy. Phase 2 replaces it with this final copy:

> WildlifeStats is a national research framework for wildlife rehabilitation data. The current public dataset is synthetic, generated at n=100,000 from regional distribution models calibrated against published wildlife rehabilitation literature. It is intended for researchers, policy analysts, educators, and conservation organizations.
>
> The framework demonstrates a method, not a real-time surveillance network. Real wildlife centers operate on heterogeneous record systems; the methodology page describes how published records, if shared, can be normalized into the structure shown here.

### §3.3 "What this is / what this isn't" two-column

Phase 1 ships a placeholder version. Phase 2 final:

**What this is**
- A national research framework
- Synthetic data calibrated against published rehabilitation literature
- Methodology demonstration for multi-source wildlife data
- A reading reference for researchers, policy analysts, and educators

**What this isn't**
- A real-time surveillance system
- Live data from any specific rehabilitation center
- A triage routing service for finders of injured wildlife
- A fundraising platform for any organization

### §3.4 Section landing placeholder copy

For each section landing (`/one-health/`, `/parks/`, `/wildlife/`, `/data/`, `/ingest/`), replace the Phase 1 placeholder paragraph with the corresponding paragraph below. Each is 3–5 sentences, restrained, national-research register.

**One Health** (`/one-health/index.html`)
> One Health describes the interdependence of wildlife, domestic animal, and human health. The synthetic dataset includes admission reasons consistent with patterns documented in the literature — vehicle collisions, window strikes, predation, anthropogenic poisoning, and infectious disease presentations relevant to surveillance. This section will surface cross-species patterns and zoonotic-relevant categories. Final content lands in Phase 4.

**National Parks** (`/parks/index.html`)
> The National Parks lens filters the synthetic admissions data by proximity to NPS units. The map and tables are illustrative — synthetic data is plausibly shaped by regional species composition but is not measured against any specific park's actual wildlife activity. Final content lands in Phase 4.

**Wildlife** (`/wildlife/index.html`)
> A taxonomic browse of the synthetic admissions data — by class, by guild, by species. Each entry will include a range hint, the most common synthetic admission reasons in the dataset, and a seasonal pattern. Final content lands in Phase 4.

**Data** (`/data/index.html`)
> The full synthetic admissions cube — year, month, county, species, class, admission reason, outcome category, disposition — exposed as a filterable interface with k-suppressed CSV downloads. Final content lands in Phase 3 (data generation) and Phase 4 (interface).

**Ingestion methodology** (`/ingest/index.html`)
> A walkthrough of the methodology by which heterogeneous wildlife center records — typically spreadsheets in incompatible schemas — could be normalized into the WildlifeStats schema. The page documents the cleaning and reconciliation pipeline and demonstrates it on sample records. The pipeline is not currently a live service. Final content lands in Phase 4.

### §3.5 Methodology / Governance / About pages

These pages have Phase 1 placeholder copy. Phase 2 final copy is intentionally short here — final long-form versions land in Phase 6 (governance polish). Phase 2 ships:

**`/methodology.html`** — replace placeholder with:
> The current dataset is synthetic, generated at n=100,000 patient records distributed across all 50 states and the District of Columbia. Distributions are calibrated against published wildlife rehabilitation literature for admission categories, seasonality, and regional species composition. The generation script and seeds are committed to the repository for reproducibility. A full methodology writeup lands in Phase 3 of the build plan.

**`/governance.html`** — replace placeholder with:
> WildlifeStats is structured around a four-tier data framework: public, partner, research, and surveillance. The public tier — this site — uses synthetic data exclusively. The remaining tiers are future work and require partner agreements with real wildlife rehabilitation centers. A full governance writeup lands in Phase 6 of the build plan.

**`/about.html`** — replace placeholder with:
> WildlifeStats is an independent research framework. It is not affiliated with any specific wildlife rehabilitation center, government agency, or academic institution. The current public site is in active development; section pages note their build status individually.

### §3.6 Footer

Phase 1 footer left side reads: "WildlifeStats is a research framework. Current dataset is synthetic (n=100,000) generated from regional distribution models. See Methodology."

Phase 2 final: same text. UNCHANGED.

## §4 — Logo slot (Phase 2 mechanical work, file replacement deferred)

Phase 2 ships the header's logo slot at its final position but with a placeholder SVG. When Mike's v2.0 Gemini logo files land, replacing the slot is a one-file PR.

### Slot specification

In `assets/img/`, create `logo.svg` as a placeholder:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 64" role="img" aria-label="WildlifeStats">
  <text x="0" y="44" font-family="Source Serif Pro, Georgia, serif" font-size="32" font-weight="600" fill="#2A3F52">WildlifeStats</text>
</svg>
```

In the header (Phase 1 currently renders the wordmark as plain text), replace the text wordmark with:

```html
<a href="/" class="brand" aria-label="WildlifeStats — home">
  <img src="/assets/img/logo.svg" alt="" width="240" height="64" class="brand__mark">
  <span class="brand__kicker">National Wildlife Rehabilitation Research Framework</span>
</a>
```

The `alt=""` on the `<img>` is correct because the surrounding `<a>` has an `aria-label`. Do not duplicate.

CSS additions in `assets/css/site.css`:

```css
.brand { display: inline-flex; flex-direction: column; gap: var(--space-1); text-decoration: none; color: inherit; }
.brand__mark { display: block; height: 40px; width: auto; }
.brand__kicker { font-family: var(--font-sans); text-transform: uppercase; letter-spacing: 0.18em; font-size: 11px; color: var(--color-muted); }
```

When Mike's real logo lands, the engineer drops the real `logo.svg` into `assets/img/` and no other file changes.

## §5 — What is NOT in Phase 2

- Final logo file (placeholder ships; Mike's prompts in flight).
- Hero imagery / illustrations of any kind. The site remains text-forward.
- Any data work. The Phase 1 `/data/` page still says "Final content lands in Phase 3."
- One Health, Parks, Wildlife, Ingest content — Phase 4.
- robots.txt / sitemap.xml / OpenGraph / schema.org markup — Phase 6.

## §6 — Validation for the engineer applying this ledger

Before opening the Phase 2 PR, the engineer must:

1. Render the homepage locally; visually confirm it reads as restrained national-research register, not BRWC's warm-rehab voice, not MOA's compensation-consulting voice.
2. Confirm `assets/css/tokens.css` was NOT modified (palette is unchanged from Phase 1).
3. Confirm the new logo slot renders at 40px tall in the header on desktop and 32px on mobile (≤640px).
4. Confirm CI passes — BRWC content guard, link check, HTML validate.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:35 ET
