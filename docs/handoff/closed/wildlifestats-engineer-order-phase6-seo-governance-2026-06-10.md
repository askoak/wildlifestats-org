# Engineer order — Phase 6: SEO + governance polish

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer
**Date:** 2026-06-10 ~14:40 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Phase 4 sub-orders all merge)
**Authority:** §13 + §14.

## Scope — single PR

1. **`robots.txt`** — flip from `Disallow: /` to allow-list:

   ```
   User-agent: *
   Allow: /
   Disallow: /secure/
   Sitemap: https://wildlifestats.org/sitemap.xml
   ```

2. **`sitemap.xml`** — uncomment all URLs from the Phase 1 skeleton. Add `<lastmod>`, `<changefreq>`, `<priority>`. Include all section landings, encyclopedia top-level pages, Methodology, Governance, About, and `/data/`. EXCLUDE `/secure/*`. EXCLUDE individual encyclopedia leaf pages (too granular; let crawlers discover via the index).

3. **Open Graph + Twitter card meta tags** on every page. Use a generic OG image (`assets/img/og-default.png`, 1200x630, restrained — wordmark on cream background; engineer creates this with simple PIL or any tool, just needs to exist). Per-page OG title and description.

4. **Schema.org `Dataset` markup** on `/data/index.html` as JSON-LD:

   ```html
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "Dataset",
     "name": "WildlifeStats Synthetic Admissions Cube",
     "description": "Synthetic wildlife rehabilitation admission records, n=100,000, generated from regional distribution models calibrated against published literature.",
     "url": "https://wildlifestats.org/data/",
     "isAccessibleForFree": true,
     "license": "https://creativecommons.org/licenses/by/4.0/",
     "creator": {
       "@type": "Organization",
       "name": "WildlifeStats"
     },
     "distribution": [{
       "@type": "DataDownload",
       "encodingFormat": "application/json",
       "contentUrl": "https://wildlifestats.org/data/cube/admissions-cube.json"
     }]
   }
   </script>
   ```

5. **Governance page final long-form content** at `/governance.html`. Replace the Phase 2 short placeholder with ~800 words:
   - Four-tier data framework (public, partner, research, surveillance).
   - Synthetic-data methodology summary (link to /methodology.html).
   - Why no real centers named.
   - How a real wildlife center could partner.
   - Privacy / k-suppression policy.
   - Citation request — how to cite WildlifeStats in academic work.

6. **Methodology page final long-form content** at `/methodology.html`. Replace the Phase 2 short placeholder with ~1000 words:
   - Generation algorithm summary.
   - Regional archetype definitions table.
   - Calibration sources (published literature — cite specific papers / reports).
   - Reproducibility — seed, build command, hash of output.
   - Validation tests run.
   - Known limitations of the synthetic approach.

7. **Remove `noindex, nofollow`** meta tag from every page EXCEPT `/secure/*` (which doesn't have static pages anyway — placeholder remains noindex).

## Acceptance criteria

1. `curl https://wildlifestats.org/robots.txt` returns the new allow-list version.
2. `curl https://wildlifestats.org/sitemap.xml` returns valid XML with all expected URLs.
3. Every page has unique OG title and description tags.
4. `/data/` page validates as a `Dataset` in Google's Rich Results Test (manual check; not gated by CI).
5. `/governance.html` and `/methodology.html` host the long-form content.
6. No page (except 404) returns `noindex, nofollow`.
7. CI green.

## Out of scope

- Submitting to Google Search Console / Bing Webmaster (Mike's call).
- Backlinks campaign (architect's master-plan §6 leaves this for future).
- Real Twitter/X handle for the brand (none exists yet).

## Commit and merge

- Branch: `engineer/phase6-seo-governance`.
- Commit: `feat(wildlifestats): Phase 6 SEO + governance polish`.
- Trailer: `Engineer: <your-seat-sig>`.
- Self-merge per §14 after CI green + manual checks.
- After merge, append `## Resolution`, move to `closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:40 ET

## Resolution

Shipped. PR [#16](https://github.com/askoak/wildlifestats-org/pull/16) squash-merged to `main` as `c9023c0`. All four CI jobs green; robots.txt + sitemap + OG image + no-noindex verified on the Netlify deploy preview before merge.

Delivered all 7 scope items: robots.txt allow-list, full sitemap.xml, OG/Twitter/canonical on every indexable page + generated `og-default.png`, schema.org Dataset JSON-LD on `/data/`, ~800-word governance + ~1000-word methodology long-form, noindex removed everywhere except 404. One addition flagged in the PR: `rel=canonical` per page → `.org`, to avoid duplicate-content indexing between the `.org` domain and the `netlify.app` subdomain.

**This completes the original master-plan build — Phases 1 → 6 are all live on wildlifestats.netlify.app.**

### Lane queue after Phase 6 (for the next auto-mode tick)
Newer orders on `main`, unstarted, triaged by dependency:
- **Phase 4.5 data-pipeline** (`...phase4.5-data-pipeline...`, 5 sub-PRs) — ready; partner-Excel ingestion pipeline.
- **Phase 4.5+ source-registry** — blocked on 4.5.
- **Phase 5 secure-tier** (`...phase5-secure-tier...` + national-research spec) — read spec; may need a credential (Mike).
- **Phase 3.1 cube 1M-scale** (`...phase3.1-cube-1m-scale...` + amendment) — read amendment for the 8 MB-cap implication of a 10× cube.
- **Phase 7 WREN** — gated on Phase 6 (✓) AND Phase 4.5; 7a needs an Anthropic API key set in Netlify env, which is a §16 owner-only step (surface when reached; Mike asleep tonight).

— Engineer, `soar-aspen-beryl-heron`, 2026-06-10
