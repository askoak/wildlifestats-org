# Wildlife911 architecture — corrections to the 21:20 ET amendment

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 21:30 ET
**Status:** Correction layered on top of `wildlifestats-wren-architecture-spec-amendment-wildlife911-2026-06-10.md`. Where this file disagrees with the 21:20 amendment, this file governs.
**Mike directives:**
- 2026-06-10 21:21 ET: "these documents were virginia calibrated and a virginia-specific version should be retained and then we create a separate national that has its own folders by year [interpreted as state] -- specifics about blue ridge wildlife center and clarke county etc very much belong as places to recommend"
- 2026-06-10 21:23 ET: "keep what you have as national template and I'll reupload the original file you save as State>VA on onedrive and github"
- 2026-06-10 21:23 ET: re-uploaded the unscrubbed `wildlife_rescue_guides_va.yaml`

## §1 — What I got wrong in the 21:20 amendment

I treated the Virginia-calibrated Wildlife911 content as "the seed for national expansion" — implying that Virginia content would be replaced by progressively more national / state-agnostic content. That was incorrect.

The correct model:

- **Virginia content is canonical Virginia content.** Mike's curated YAML includes Blue Ridge Wildlife Center, SW VA Wildlife Center, and Wildlife Center of Virginia as **legitimate referral recommendations** for Virginia triage users. Clarke County in CWD DMA + transport-restricted-county lists is **correct Virginia regulatory information**. These belong in the Virginia edition; they are not §19 violations.
- **National template is a separate abstracted artifact**, derived from the Virginia structure but stripped of all state-specific referrals. It's the *scaffolding* a new state's content gets authored against.
- **Per-state editions** (VA today; 49 others later) each have full state-specific content with their state's legitimate rehab-center referrals.

## §2 — Lane-discipline reasoning (why Blue Ridge in VA isn't §19)

§19 prevents BRWC content from contaminating the WildlifeStats public tier. The intent is to prevent BRWC-as-the-organization from being used as a source, a voice, or a brand that bleeds into WildlifeStats's national-research identity.

§19 does NOT prevent BRWC-as-one-of-many-Virginia-wildlife-rehab-centers from being listed as a referral option for a Virginia user with an injured animal. That's correct public-safety information. The Virginia edition also recommends Wildlife Center of Virginia and SW VA Wildlife Center; BRWC is one of several Virginia options, not the only one or the favored one.

The lane discipline is preserved because:
- The Virginia edition is one of N state editions. Future Texas edition recommends Texas centers; future California edition recommends California centers. The structure is symmetric.
- The national template (which serves any non-VA state until that state's edition is authored) is BRWC-scrubbed.
- BRWC's own data, voice, tone, clinical records, and case data still never enter WildlifeStats — those remain BRWC-lane-only.
- Listing BRWC by name on a referral page is no different from a public Google search returning BRWC's phone number for "Virginia wildlife rehabilitation Clarke County."

## §3 — Directory structure (final)

```
wildlifestats/_wren/wildlife911/
  templates/
    national/                           # BRWC-scrubbed, state-agnostic scaffolding
      guides/                           # (currently houses the 12 species docs + scrubbed YAML)
        wildlife_rescue_guides_va.yaml  # The BRWC-scrubbed YAML — to be re-cast as a
                                        # generic 'wildlife_rescue_guides_template.yaml'
                                        # by the engineer in 7g.1
        BATS.docx, BIRD.docx, ...       # 12 species reference docs (same files as VA; species
                                        # info is biology, not state-specific)
      assets/                           # 7 infographics + Wildlife911VAbw.png
                                        # (Wildlife911VAbw.png is the brand mark)
  states/
    VA/                                 # Virginia edition (canonical, with full state content)
      guides/
        wildlife_rescue_guides_va.yaml  # UNSCRUBBED original. Includes Blue Ridge Wildlife
                                        # Center + SW VA + Wildlife Center of Virginia as
                                        # legitimate referrals, Clarke County in CWD DMA
                                        # + restricted-transport lists.
        BATS.docx, BIRD.docx, ...       # Same 12 species docs (identical to template;
                                        # symlink-equivalent for now; future per-state
                                        # variants ship as state-specific overrides)
      assets/                           # Same 7 visual assets
    <future: TX, CA, NY, ... once authored>
```

## §4 — Loader behavior (Phase 7g.2 spec amendment)

The loader picks Wildlife911 content in this priority order:

1. If user's resolved state has a state edition at `states/<XX>/`, use that edition.
2. Otherwise, use the national template at `templates/national/`. The non-VA user sees a banner: "Wildlife911 currently has full content for Virginia. For your state, AnimalHelpNow ([animalhelpnow.org](https://animalhelpnow.org)) is your best starting point, plus your state wildlife agency."

A state edition is "complete" if it has a `guides/wildlife_rescue_guides_<XX>.yaml` file with a populated `regional_referrals` block and a `dwr_link` for the state agency. The national template is permanently incomplete-by-design — it's a scaffold, not a destination.

## §5 — BRWC content guard amendment

`scripts/check-no-brwc.sh` updated in this batch:

1. **Scan format coverage expanded** from `.html .css .js .json .xml .txt .toml` to also include `.yaml .yml .md`. This catches future BRWC mentions in handoff and pipeline configuration files that previously went unscanned.
2. **Path exclusions expanded** to add:
   - `./docs/research/` (research appendices may cite real wildlife centers by name as primary-source citations — already a pattern in the cat-impact appendix)
   - `./wildlifestats/_wren/wildlife911/states/` (state editions intentionally list state-specific rehab centers as referrals)
   - `./wildlifestats/_pipeline/sources/README.md` (engineer's documentation of the BRWC scrub policy for the Flyway roster)
   - `./.github/workflows/` (workflow YAMLs mention "brwc-content-guard" as a job name)

The national template (`./wildlifestats/_wren/wildlife911/templates/`) remains subject to the guard. CI verified passing after the changes.

## §6 — National-expansion strategy (revised)

The 21:20 amendment said Virginia ships first and 49 states follow "by editorial work." Corrected:

- **Virginia ships as Virginia.** The VA edition is Mike's deliverable, complete and canonical.
- **The national template is what serves all non-VA users until their state's edition is authored.** The template is a scaffold that already works (just generically) — non-VA users get safe, AnimalHelpNow-routed guidance.
- **Per-state editions are independent author projects.** Each is its own content effort by someone (Mike, a state wildlife agency, a partner organization, or a delegated editor) who curates that state's content using the national template as the structural starting point. There is no "national rollup" version; the structure is federated by state.

This is the right model because each state's wildlife laws, CWD restrictions, primary rehab centers, and DWR-equivalent agency are genuinely different — a single "national" content layer would either be too generic to help or wrong for half the states.

## §7 — Cross-references

- `wildlifestats-wren-architecture-spec-amendment-wildlife911-2026-06-10.md` — the 21:20 amendment this file corrects. Items in §2 ("What Wildlife911 is"), §3 ("Pill architecture"), §5 ("Virginia today, national tomorrow"), §6 (config table) of that file are superseded by §3 and §6 of this correction.
- `wildlifestats-engineer-order-phase7g-wildlife911-pill-2026-06-10.md` — also gets corrections. Specifically:
  - Sub-PR 7g.2 loader now picks `states/<XX>/` first, falls back to `templates/national/`.
  - Sub-PR 7g.3 public surface routes `/wildlife911/state/VA/` to the VA edition; non-VA routes to national template + AnimalHelpNow.
  - Sub-PR 7g.4 per-state pages: VA fully populated from `states/VA/`; other states render the "currently Virginia-complete" landing with AnimalHelpNow.
- `scripts/check-no-brwc.sh` — exclusion list + scan-format coverage updated in this batch.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 21:30 ET
