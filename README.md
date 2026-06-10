# wildlifestats-org

Repository for **wildlifestats.org** — a national wildlife rehabilitation research framework.

## Status

In development. Deployed at https://wildlifestats.netlify.app/ (and at
`wildlifestats.org` once DNS is wired). Every page carries `noindex,nofollow`
and `robots.txt` disallows all crawling until launch readiness (Phase 6).

## Architecture

Master plan: see `docs/handoff/wildlifestats-master-plan-2026-06-10.md` in the
[askoak/askoak-web](https://github.com/askoak/askoak-web) repo (the source of
truth — the plan was authored there during the initial scoping pass).

Summary:

- **Public site (wildlifestats.org):** national-research framing, synthetic
  n=100,000 dataset, new tools for One Health / National Parks / wildlife
  encyclopedia / searchable database. NO references to specific real centers
  in the public tier.
- **Authenticated tier (wildlifestats.org/secure):** future phase (Phase 5).
  The `/secure/*` path is reserved now and returns 404 until then.
- **Domain config:** wildlifestats.org canonical; wildlifestats.com redirects
  to .org.

## What lives here

Pure static HTML/CSS/JS — no build pipeline. Netlify serves the repo root
directly on every push to `main`.

```
index.html            Homepage shell — national-research framing
404.html              Institutional 404
methodology.html      How the dataset is built (placeholder)
governance.html       Data tier framework, partner model (placeholder)
about.html            What WildlifeStats is, who it's for (placeholder)

one-health/index.html National One Health hub landing
parks/index.html      National Parks lens landing
wildlife/index.html   Wildlife encyclopedia landing
data/index.html       Searchable national database landing
ingest/index.html     Multi-format ingestion sandbox (methodology page)

assets/css/tokens.css CSS custom properties — palette, type, spacing
assets/css/base.css   Reset + base typography + layout primitives
assets/css/site.css   Header, footer, nav, page chrome
assets/js/site.js     Header behavior (current-section highlight)
assets/img/           Logo slot reserved (Phase 2)

netlify.toml          Build config + security headers + redirects
robots.txt            Disallow: / (pre-launch)
sitemap.xml           Skeleton; URLs commented out until Phase 6
docs/handoff/         Architect/engineer coordination
```

The palette and typography are token-driven (`assets/css/tokens.css`) so the
Phase 2 rebrand is a single-file swap, not a page-by-page edit.

## Not in this repo

- The real BRWC patient records and any BRWC-specific content
- The AskOak compensation product
- The BRWC public site source

All of those continue to live in [askoak/askoak-web](https://github.com/askoak/askoak-web).

## Credentials

This repo does not store credentials. See
[askoak-web's CREDENTIALS-POINTER.md](https://github.com/askoak/askoak-web/blob/main/CREDENTIALS-POINTER.md)
for the canonical credential-handling pattern across all Mike-Oak ventures
(Standing Orders §18).

## CI

`.github/workflows/validate.yml` runs on every PR. Three jobs:

- **BRWC content guard** — `scripts/check-no-brwc.sh` fails if forbidden BRWC-identifying strings appear outside `docs/handoff/`.
- **Internal link check** — `linkinator` checks all internal links resolve.
- **HTML validation** — `html-validate` checks HTML well-formedness.

All three must pass for §14 self-merge eligibility.
