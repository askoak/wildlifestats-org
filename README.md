# wildlifestats-org

Repository for **wildlifestats.org** — a national wildlife rehabilitation research framework.

## Status

In development. Single-file placeholder live at https://wildlifestats.netlify.app/ pending the full build.

## Architecture (in progress)

Master plan: see `docs/handoff/wildlifestats-master-plan-2026-06-10.md` in the [askoak/askoak-web](https://github.com/askoak/askoak-web) repo (where the plan was authored during the initial scoping pass).

Summary:

- **Public site (wildlifestats.org):** national-research framing, synthetic n=100,000 dataset, new tools for One Health / National Parks / wildlife encyclopedia / searchable database. NO references to specific real centers in the public tier.
- **Authenticated tier (wildlifestats.org/secure):** future phase. Mirror of a real wildlife center's staff tools for private testing.
- **Domain config:** wildlifestats.org canonical; wildlifestats.com redirects to .org.

## What lives here

```
index.html       The placeholder
README.md        This file
```

When the framework is built out, structure will expand to mirror the patterns from [askoak/askoak-web](https://github.com/askoak/askoak-web)'s `brwc/_public_app/` — but with new content, new branding, synthetic data, and national-scope features added.

## Not in this repo

- The real BRWC patient records and any BRWC-specific content
- The AskOak compensation product
- The BRWC public site source

All of those continue to live in [askoak/askoak-web](https://github.com/askoak/askoak-web).

## Credentials

This repo does not store credentials. See [askoak-web's CREDENTIALS-POINTER.md](https://github.com/askoak/askoak-web/blob/main/CREDENTIALS-POINTER.md) for the canonical credential-handling pattern across all Mike-Oak ventures.
