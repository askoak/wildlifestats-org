# Phase 5 secure-tier mechanism note

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 14:39 ET
**Status:** Spec note. Engineer order dispatches when Mike confirms the credential choice OR the architect decides per default.

## What Phase 5 does

Stand up `wildlifestats.org/secure/` as a Netlify basic-auth-gated tier that **mirrors the BRWC staff site** for Mike's private testing. Per master-plan §2 Phase 5: this is the only place real BRWC-derived content appears under the WildlifeStats brand, and it is auth-gated.

## Architectural decision: internal rewrite, not duplication

Per master-plan §2 Phase 5 recommendation: use Netlify `_redirects` with status 200 (rewrite, not 301) to internally serve `askoak.michaeloak.com/brwc/*` content under `wildlifestats.org/secure/*`. One source of truth (BRWC staff site); WildlifeStats secure tier always tracks it automatically.

### Implementation sketch

In `netlify.toml`:

```toml
# Phase 5 — secure tier rewrites
# /secure/* on wildlifestats.org rewrites to /brwc/* on askoak.michaeloak.com.
# Basic-auth gate applies first; only authenticated requests reach the rewrite.

[[redirects]]
  from = "/secure/*"
  to = "https://askoak.michaeloak.com/brwc/:splat"
  status = 200
  force = true
  conditions = { Role = ["staff"] }

[[headers]]
  for = "/secure/*"
  [headers.values]
    Basic-Auth = "<credential>"
```

**Risk:** Netlify proxy rewrites across domains have a 1MB request size limit and may not forward all headers cleanly. If the BRWC staff site has assets > 1MB OR uses cookies / fetch-based auth, the rewrite-only approach breaks.

**Mitigation:** test with `curl -I` against a sample BRWC staff URL after the rewrite is live. If breakage, fall back to **link-out approach** — `/secure/` is a single landing page with a "Continue to BRWC staff site" link that opens `askoak.michaeloak.com/brwc/` in a new tab. Less elegant but unconditionally works.

## Credential decision

Two options (master plan §4 deferred):

1. **Reuse BRWC staff passcode.** One credential to remember; Mike tested. Cleanest in the short term. Downside: when real partner accounts arrive in the future, they get a credential that also unlocks BRWC content.
2. **Separate WildlifeStats credential.** Two passcodes. Cleaner separation. Future-proof for partner accounts.

**Architect default (lane handoff §85):** option 1 — BRWC staff passcode for now. Switch to option 2 when real partner accounts become real.

Engineer reads the BRWC staff passcode from `C:\Users\Hello\OneDrive - Michael Oak Advisors\Credentials\` per §18 (don't paste in chat, don't echo in commits).

## Order dispatch timing

The Phase 5 engineer order does NOT dispatch automatically with the rest of today's queue. It dispatches when:

- Phase 4 is complete and the public tier is stable, OR
- Mike explicitly requests it.

Reason: Phase 5 touches the BRWC site indirectly (rewrites point at it). The architect wants the public tier rock-solid first so that any Phase 5 breakage is isolatable.

When Phase 4 completes, the architect will author `wildlifestats-engineer-order-phase5-secure-tier-YYYY-MM-DD.md` referencing this mechanism note.

## What is NOT in Phase 5

- Real partner accounts (future tier 2 work).
- A separate WildlifeStats auth schema beyond basic-auth (future when partner accounts arrive).
- Any modification to the BRWC staff site — Phase 5 is pure consumer, not producer.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:39 ET
