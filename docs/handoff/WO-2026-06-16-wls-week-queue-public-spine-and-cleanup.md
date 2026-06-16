# WO-2026-06-16-wls-week-queue-public-spine-and-cleanup

**Date:** 2026-06-16  
**Author:** Codex  
**Status:** Proposed one-week execution bundle  
**Scope:** Close the most visible WildlifeStats loose ends, finish the public-spine
wave cleanly, and stop the repo from quietly drifting into Virginia-only or
pilot-only interpretations where the product is national.

## 1. Why this bundle exists

WildlifeStats has real forward motion now:

- Wave 1 spine code landed for `wildlife911`, `law_watch`, and source-status
  upgrades.
- the Virginia eBird denominator pilot landed and the denominator policy follow-up
  is now durable on `main`
- the inherited HTML validation failure is fixed
- there are no open PRs at the moment

But the repo still has several high-signal loose ends:

1. the public `wildlife911` route still reads as Virginia-first even though a
   national directory render now exists under `_wren`
2. `law_watch` has normalized records and no public page
3. the sector-funders registry is strong enough for a public page and is still
   trapped as source data only
4. the eBird work is still easy to misread as "national denominator in progress"
   when it is actually a Virginia pilot plus policy call
5. the site needs one deliberate cleanup pass after the above so the new public
   surfaces are linked, labeled, and not internally contradictory

This bundle is meant to move WildlifeStats forward as a national public utility
without reopening the hardest lanes first.

## 2. What this bundle is and is not

This week bundle **is**:

- public-spine finishing work
- low-risk page shipping off already-committed source assets
- national-posture cleanup
- explicit eBird architecture discipline

This week bundle is **not**:

- a Flyway go-live push
- a rehab social monitor public launch
- a national eBird raw ingest
- a secure-tier expansion
- a multi-source Phase 9 marathon

## 3. Current facts that shaped the sequence

- `wildlifestats/_pipeline/flyway/CRON_ENABLED` is still `0`
- `work-orders/WO-2026-06-14-wls-flyway-4-5-i-5-go-live.yml` and
  `work-orders/WO-2026-06-14-wls-flyway-notifications-cron-wiring.yml` exist,
  but this bundle deliberately does not reopen Flyway unless Mike explicitly
  reprioritizes it
- `wildlifestats/_pipeline/law_watch/` now exists with normalized output artifacts
- `wildlifestats/_wren/wildlife911/states/{STATE}/index.html` now exists for all
  50 states plus DC, but the public route at `wildlife911/state/` still presents
  the old Virginia-complete framing
- the current eBird artifact is a Virginia pilot. WildlifeStats.org is national.
  That mismatch must be made explicit before anyone treats the pilot as a
  product denominator layer

## 4. Ordered week queue

Execute in this order:

1. `work-orders/WO-2026-06-16-wls-wildlife911-national-public-route-cleanup.yml`
2. `work-orders/WO-2026-06-16-wls-law-watch-public-page-mvp.yml`
3. `work-orders/WO-2026-06-16-wls-grants-funders-page-mvp.yml`
4. `work-orders/WO-2026-06-16-wls-ebird-national-architecture-and-pilot-labeling.yml`
5. `work-orders/WO-2026-06-16-wls-public-spine-week-closeout-cleanup.yml`

Why this order:

- `wildlife911` route cleanup closes the most obvious national/product mismatch
- `law_watch` is the strongest already-ready public page after that
- funders is the fastest clean second page from a fully local curated source
- eBird architecture belongs before any further bird-signal enthusiasm
- final cleanup waits until the new surfaces exist so it can wire and reconcile
  the actual shipped routes, labels, and docs

## 5. Deliberate deferrals

These are not forgotten. They are intentionally deferred out of this bundle:

- Flyway cron enablement and notification wiring
- rehab social monitor public page
- migration-signals page
- wildlife news page
- all-states eBird denominator generation
- any raw-eBird storage move that requires touching Mike's local filesystem

## 6. Bundle acceptance test

This week counts as successful if, by the end:

1. the public site has a clearly national `wildlife911` state directory posture
2. `law-watch/` exists as a federal-first metadata page
3. `funders/` exists as a public registry-backed sector page
4. the repo makes the Virginia-only eBird pilot impossible to misread as a
   national denominator layer
5. homepage, nav, and README-level descriptions no longer contradict the new
   public surfaces

## 7. Hard rules for the whole bundle

- Do not commit raw eBird rows or extracted raw eBird files.
- Do not rerun the full `ebd_sampling_relMay-2026.tar` archive unless the
  output schema itself changes.
- Do not reopen Flyway cron/go-live work in this bundle.
- Do not turn `law_watch` into a legal-advice tool or full-text mirror.
- Do not let national public routes quietly inherit Virginia-only copy.
- Keep public pages metadata-first and attribution-visible.

## 8. Bottom line

This is the cleanest one-week WildlifeStats push I see from current repo state:
finish the national public spine, ship the two safest public pages, lock the
eBird posture, then do one disciplined cleanup pass instead of another pile of
orphaned planning notes.
