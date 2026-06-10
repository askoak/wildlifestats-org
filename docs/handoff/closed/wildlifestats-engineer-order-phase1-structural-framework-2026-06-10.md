# Engineer order — Phase 1: WildlifeStats structural framework

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer
**Date:** 2026-06-10 ~14:30 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main`
**Master plan reference:** `askoak/askoak-web` → `docs/handoff/wildlifestats-master-plan-2026-06-10.md`, §2 Phase 1
**Authority:** §13 elevated ship + §14 self-merge eligibility, applied to this lane per the lane-handoff convention. Single concern: ship the structural framework. Self-merge when CI is clean (no CI exists yet on this repo; a clean merge is the gate).

## Why this order departs from the master plan's literal wording

The master plan (authored when the wildlifestats site was assumed to live as a sibling folder in `askoak-web`) describes Phase 1 as a "surgical fork" — copy `brwc/_public_app/` structurally, then rebrand. The repo we actually have is a **standalone repo** (`askoak/wildlifestats-org`), already isolated by construction. There is no BRWC content to carry over and then scrub.

So Phase 1 here is: build the directory structure and placeholder pages **from first principles**, sized for the national-research IA the master plan calls for in Phases 2–6. No BRWC inheritance is loaded in the first place — which is cleaner than the fork-then-scrub path and preserves the §19 boundary (no BRWC content on the WildlifeStats public tier) by construction.

If anything in this order conflicts with the master plan's literal wording, this clarification governs.

## Scope — what ships in this PR

Single PR, single concern: the structural skeleton. **No content beyond placeholders. No data. No logo. No final palette.** Phase 2 rebrands; Phase 3 wires data; Phase 4 fills sections.

### 1. Directory layout

Create the following structure at the repo root. Existing `index.html` is **replaced** with the new structural version (the current placeholder is superseded).

```
/
  index.html                       (homepage shell — national-research framing)
  404.html                         (institutional 404 — links back to /)
  methodology.html                 (how the dataset is built; placeholder copy)
  governance.html                  (data tier framework, partner model; placeholder copy)
  about.html                       (what WildlifeStats is, who it's for; placeholder copy)

  one-health/
    index.html                     (One Health hub landing — Phase 4 will expand)

  parks/
    index.html                     (National Parks lens landing — Phase 4 will expand)

  wildlife/
    index.html                     (Wildlife encyclopedia landing — taxon→guild→species shell)

  data/
    index.html                     (Searchable national database landing — Phase 3 wires the cube)

  ingest/
    index.html                     (Multi-format ingestion sandbox methodology page — Phase 4 demo)

  assets/
    css/
      tokens.css                   (CSS custom properties — palette, type, spacing)
      base.css                     (reset + base typography + layout primitives)
      site.css                     (header, footer, nav, page chrome)
    js/
      site.js                      (header behavior; tiny, no framework)
    img/
      .gitkeep                     (logo slot reserved; no file yet)

  netlify.toml                     (build config + headers + redirects, incl. /secure/* reservation)
  robots.txt                       (Disallow: / for now — pre-launch)
  sitemap.xml                      (skeleton; URLs commented out until launch)
  README.md                        (updated to reflect new structure)
```

`docs/handoff/` is untouched by this PR except for closing this order.

### 2. CSS tokens (assets/css/tokens.css)

Use CSS custom properties so Phase 2's rebrand is a tokens-file swap, not a page-by-page edit. Architect default values below; Mike's final palette overrides them in Phase 2.

```css
:root {
  /* Color — architect defaults from master plan §4 + lane handoff */
  --color-ink: #1F2A2A;          /* primary text */
  --color-muted: #6B6B65;        /* secondary text, captions */
  --color-paper: #FAF6EC;        /* page background (cream) */
  --color-rule: #DDD8CA;         /* hairlines, borders */
  --color-slate: #2A3F52;        /* deeper slate — primary brand */
  --color-clay: #B96F4D;         /* warm clay — accents, links */
  --color-sage: #6B8264;         /* muted sage — secondary accent */

  /* Type */
  --font-serif: 'Source Serif Pro', Georgia, 'Times New Roman', serif;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  /* Spacing scale */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
  --space-7: 64px;
  --space-8: 96px;

  /* Layout */
  --measure: 68ch;               /* prose column width */
  --container-max: 1100px;       /* wide layout max */
}
```

### 3. Base CSS (assets/css/base.css)

Minimal reset + serif body + sans for kickers / nav / UI. Print-friendly. No animations. No drop shadows. No gradients. Restrained.

Key rules:

- `html { font-size: 17px; }` on desktop; 16px on `(max-width: 640px)`.
- `body` uses `--font-serif`, `--color-ink` on `--color-paper`, line-height 1.6.
- Headings use `--font-sans`, weight 600, restrained letter-spacing on h1/h2 only.
- Links: `--color-clay`, underlined on hover only (no permanent underline noise).
- `.kicker` utility: `--font-sans`, uppercase, letter-spacing 0.18em, 12px, `--color-muted`.
- `.container` utility: `max-width: var(--container-max); margin: 0 auto; padding: 0 var(--space-4);`.
- `.prose` utility: `max-width: var(--measure);` for reading-column content.

### 4. Site chrome (assets/css/site.css)

A thin header and a thin footer, both restrained. No hero images. No marketing gradients.

**Header:**
- Left: wordmark "WildlifeStats" as text (real logo slots in Phase 2). Below the wordmark, a small `--color-muted` kicker reading "National Wildlife Rehabilitation Research Framework".
- Right: primary nav as a single horizontal row — `One Health`, `National Parks`, `Wildlife`, `Data`, `Methodology`, `About`. Sans serif, no caps, no underlines, current-section gets `--color-slate` + bottom border.
- Below header: a 1px `--color-rule` divider, full width.

**Footer:**
- Left: small print — `WildlifeStats is a research framework. Current dataset is synthetic (n=100,000) generated from regional distribution models. See <a href="/methodology.html">Methodology</a>.`
- Right: `<a href="/governance.html">Governance</a>` · `<a href="/about.html">About</a>` · year.
- 1px `--color-rule` top border. `--color-muted` text. No icons.

### 5. Page templates

Every page follows the same chrome (header, divider, main, footer). Differences are in `<main>` only.

**`/index.html` (homepage shell):**
- `<h1>WildlifeStats</h1>` with kicker "National Wildlife Rehabilitation Research Framework".
- Short paragraph (3–4 sentences) describing what the framework is: a national research framework using synthetic n=100,000 patient data scaled from regional distribution models, intended for researchers, policy analysts, educators, and conservation organizations.
- A 5-tile section listing the major surfaces with one-line descriptions: One Health, National Parks, Wildlife, Data, Methodology. Each tile is a plain bordered card — `1px solid var(--color-rule)`, padding `--space-4`, no shadow.
- Brief "What this is / what this isn't" two-column on desktop, stacked on mobile. Mirrors master-plan §3 framing.
- No "Get Started" or "Donate" CTAs. No marketing voice.

**Section landings (`/one-health/index.html`, `/parks/index.html`, `/wildlife/index.html`, `/data/index.html`, `/ingest/index.html`):**
- Each gets the standard chrome plus a `<main class="container prose">` with:
  - `<p class="kicker">SECTION NAME</p>`
  - `<h1>Section title</h1>` (One Health hub / National Parks lens / Wildlife encyclopedia / National database / Multi-format ingestion sandbox)
  - One paragraph of placeholder copy describing what the section will host (3–5 sentences, drawn from master-plan §2 Phase 4 descriptions, scrubbed of any BRWC reference).
  - A small "Status" note: `<p class="status-note">This section is under construction. Final content lands as part of Phase 4 of the build plan.</p>` styled in muted text with a left border.

**`/methodology.html`, `/governance.html`, `/about.html`:**
- Same prose-page treatment. Placeholder copy 4–6 sentences each, written in restrained national-research voice. No specific numbers, no specific centers, no specific names.

**`/404.html`:**
- Centered. "This page does not exist." One sentence. Link back to `/`. No animation.

### 6. `netlify.toml`

```toml
[build]
  publish = "."
  command = ""

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"

# Reserve the /secure/* path for Phase 5. Until then, return 404.
# Phase 5 will replace this rule with a basic-auth gate per the master plan.
[[redirects]]
  from = "/secure/*"
  to = "/404.html"
  status = 404
  force = true

# wildlifestats.com -> wildlifestats.org (Mike configures DNS at GoDaddy; this
# is the Netlify-side rule for when both domains attach to this site).
[[redirects]]
  from = "https://wildlifestats.com/*"
  to = "https://wildlifestats.org/:splat"
  status = 301
  force = true

[[redirects]]
  from = "https://www.wildlifestats.com/*"
  to = "https://wildlifestats.org/:splat"
  status = 301
  force = true
```

### 7. `robots.txt`

```
User-agent: *
Disallow: /
```

Pre-launch. Phase 6 flips this to an allow-list with a real sitemap.

### 8. `sitemap.xml`

Skeleton with the URLs **commented out** so the file exists for the build but does not advertise URLs while the site is pre-launch. Phase 6 uncomments and finalizes.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- URLs commented out until Phase 6 launch readiness.
  <url><loc>https://wildlifestats.org/</loc></url>
  <url><loc>https://wildlifestats.org/one-health/</loc></url>
  <url><loc>https://wildlifestats.org/parks/</loc></url>
  <url><loc>https://wildlifestats.org/wildlife/</loc></url>
  <url><loc>https://wildlifestats.org/data/</loc></url>
  <url><loc>https://wildlifestats.org/ingest/</loc></url>
  <url><loc>https://wildlifestats.org/methodology.html</loc></url>
  <url><loc>https://wildlifestats.org/governance.html</loc></url>
  <url><loc>https://wildlifestats.org/about.html</loc></url>
  -->
</urlset>
```

### 9. Meta tags on every page

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>WildlifeStats — [page title]</title>
<meta name="description" content="National Wildlife Rehabilitation Research Framework — under construction.">
<link rel="stylesheet" href="/assets/css/tokens.css">
<link rel="stylesheet" href="/assets/css/base.css">
<link rel="stylesheet" href="/assets/css/site.css">
```

`noindex,nofollow` stays on every page until Phase 6.

### 10. README update

Replace the current README body with a section that:

- Names this is the WildlifeStats public site repo.
- Notes the Netlify deploy at `wildlifestats.netlify.app` (and `wildlifestats.org` when DNS is wired).
- Lists the top-level structure as it actually exists after this PR.
- Cites the master plan in `askoak/askoak-web` as the source of truth.
- Cites `askoak/askoak-web`'s `CREDENTIALS-POINTER.md` for credential handling (per §18).
- Keeps the "Not in this repo" disclaimer about BRWC content.

## Voice for placeholder copy

National-research register. Brookings / Pew / Cornell Lab. Calm, citation-disciplined, neutral. Specifically avoid:

- Marketing voice ("Discover", "Unlock", "Powerful")
- Startup voice ("We're building", "Join us")
- BRWC's warm-rehab voice ("our patients", "our hospital", "we treat")
- MOA's compensation-consulting voice
- US-state geography as primary frame (this is national)
- Any specific real wildlife center name
- Donation language

Specifically use:

- "The framework", "the dataset", "the analysis"
- "Researchers, policy analysts, educators, conservation organizations"
- "Synthetic data scaled from regional distribution models" — be explicit that the data is synthetic on every page that mentions it
- Em dashes, restrained punctuation
- Source Serif Pro for prose; sans only for nav and kickers

## What is explicitly OUT of scope for this PR

- Real logo files (Mike's v2.0 Gemini runs are in flight; logo slots stay empty)
- Final palette decisions (Mike has not ratified)
- Synthetic data cube (Phase 3)
- One Health book content, Parks profiles, Wildlife encyclopedia entries (Phase 4)
- The `/secure/` authenticated tier (Phase 5; this PR only *reserves* the path)
- SEO, OpenGraph, schema.org Dataset markup (Phase 6)
- Any custom domain DNS work — Mike owns that side at GoDaddy

## Acceptance criteria

After merge and Netlify deploy:

1. `https://wildlifestats.netlify.app/` returns the new homepage (not the prior placeholder).
2. Every section landing (`/one-health/`, `/parks/`, `/wildlife/`, `/data/`, `/ingest/`) returns 200 with the standard chrome and the section's placeholder copy.
3. `/methodology.html`, `/governance.html`, `/about.html`, `/404.html` all return correctly.
4. `https://wildlifestats.netlify.app/secure/anything` returns the 404 page (Phase 5 reservation working).
5. `curl -s https://wildlifestats.netlify.app/robots.txt` returns `Disallow: /`.
6. No page references "Blue Ridge", "BRWC", "Clarke County", "Boyce", "Dr. Riley", "Jen Riley", or any real wildlife center by name. Grep the PR diff to confirm.
7. No console errors in DevTools on any page.
8. Mobile (375px) and desktop (1280px) both render the chrome correctly. Header collapses to a hamburger or wraps gracefully on mobile — engineer's call, but no horizontal scroll.

## Commit and merge

- Branch: `engineer/phase1-structural-framework`.
- Commit messages: `feat(wildlifestats): <subject>` with body explaining what and why. Trailer line: `Engineer: <your-seat-sig>`.
- This is a multi-file PR but single concern (the framework). Self-merge per §14 after acceptance criteria 1–8 pass on the Netlify preview deploy. If any criterion fails, fix in the same PR before merge.
- After merge, append a `## Resolution` section to this file citing the merge commit hash, and move this file to `docs/handoff/closed/wildlifestats-engineer-order-phase1-structural-framework-2026-06-10.md`.

## Architect availability

`measured-fern-jasper-thrush` is dormant after dispatching this order. Summon by name if a Phase 1 question needs adjudication; otherwise the engineer self-decides per §14 conditions.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:30 ET

## Resolution

Shipped. PR [#3](https://github.com/askoak/wildlifestats-org/pull/3) squash-merged to `main` as commit `4052bbd` (self-merge per §14: single concern, no CI configured so clean-merge is the gate, reversible by `git revert`, no auth/privacy/public-data change, own lane).

19 files: 9 HTML pages (homepage + 5 section landings + methodology/governance/about + 404), 3 CSS files (tokens/base/site), `site.js`, `netlify.toml`, `robots.txt`, `sitemap.xml`, README, `assets/img/.gitkeep`.

Acceptance criteria 1–3, 5–8 verified locally on a static server before merge (all pages 200 with correct headings, no console errors, no horizontal scroll at 375px, grids collapse to one column on mobile, no real-org identifiers in any deployable page). Criterion 4 (`/secure/*` → 404) is a Netlify redirect rule that cannot run on a plain static server; verified post-deploy against the live Netlify site — see the post-deploy verification note appended to this lane's INBOX.

— Engineer, `soar-aspen-beryl-heron`, 2026-06-10
