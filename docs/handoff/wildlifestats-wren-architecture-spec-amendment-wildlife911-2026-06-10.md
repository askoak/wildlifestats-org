# WREN architecture spec — Wildlife911 pill amendment

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 21:20 ET
**Status:** Amendment to `wildlifestats-wren-architecture-spec-2026-06-10.md`. Adds Phase 7g (Wildlife911 pill integration) to the WREN build phasing. Read alongside the original WREN spec.
**Mike directive 2026-06-10 21:15 ET:** "an be integrated into WREN? as a Wildlife911 pill? it is corrently hosted on blue ridge wildlife center homepage I created it"

## §1 — What changes

A new sub-phase `7g` is added to WREN's build plan, after `7e` (accessibility) and parallel-or-before `7f` (secure WREN). Wildlife911 pill is a public-tier addition that does not depend on Phase 5 secure tier.

| Phase | Original | Amended |
|---|---|---|
| 7a | Function shell | unchanged |
| 7b | UI shell | unchanged |
| 7c | Engine wiring | unchanged |
| 7d | Triage routing + safety rails | **amended** — Wildlife911 is the canonical triage layer (was: deferral to AnimalHelpNow only) |
| 7e | Accessibility | unchanged |
| 7f | Secure WREN | unchanged (still gated on Phase 5) |
| **7g (new)** | — | **Wildlife911 pill integration + public Wildlife911 surface at `/wildlife911/`** |

## §2 — What Wildlife911 is

Mike-authored institutional triage assistant. Currently deployed as a CustomGPT on BRWC's homepage. The artifact bundle (committed to the repo in this batch, BRWC-scrubbed):

- `wildlifestats/_wren/wildlife911/guides/wildlife_rescue_guides_va.yaml` — master structured guide, Virginia-scoped, ~16 KB. Single source of truth for Wildlife911 behavior.
- `wildlifestats/_wren/wildlife911/guides/*.docx` — 12 species reference docs (BIRD, BAT, DEER, FOX, GROUNDHOG, OPOSSUM, RABBIT, RACCOON, REPTILES, SKUNK, SQUIRREL, RABIES FOX SKUNK RACCOON BAT).
- `wildlifestats/_wren/wildlife911/assets/*.{jpg,webp,png}` — flow charts, infographics, Wildlife911 logo (the `Wildlife911VAbw.png` is Wildlife911's own brand mark, not BRWC's).

Sourcing & lane check:

- **Authored by Mike.** Mike's own IP, hosted on BRWC's homepage as one deployment choice. Per Mike 19:38 ET, the canonical OneDrive location is now `99_Public Folder\WildStats\Wildlife911\Backup Files\` — under the WildStats parent, not BRWC.
- **One §19 scrub applied:** the YAML's regional-hospitals example list mentioned "Blue Ridge Wildlife Center" by name. Replaced with a generic "Wildlife Center of Virginia and other regional wildlife hospitals" reference. No other BRWC strings present in any artifact.
- **Clarke County mentions in YAML + 3 species docs are legitimate** — public Virginia CWD DMA and deer-transport-restricted-county lists. The BRWC content guard's pattern (`clarke county, v`) was narrowed by the engineer earlier today to avoid false positives on this exact case. CI passes.

## §3 — Pill architecture

A WREN "pill" is a specialized sub-mode that handles a class of intents with a dedicated system prompt and reference corpus. The user never sees mode-switching language; they ask WREN a question; WREN's intent classifier routes; the response is generated with the pill's context.

### §3.1 Routing

WREN's intent classification (Phase 7d) gains a `triage` intent. Routing decision:

```
User question
  → Intent classifier (Phase 7c)
  → If intent == "triage" OR vocabulary matches Wildlife911 triggers
      ("found a bird", "what should I do", "injured", "baby", "orphan",
       "hit a window", "cat caught", "rescued", "fell from nest", etc.):
    → Wildlife911 pill mode
      → Load YAML guide as primary context
      → Apply Wildlife911 system prompt (the .docx instructions, structurally encoded)
      → Resolve user's state (default Virginia; ask if ambiguous)
      → Route through Wildlife911's two-step menu (animal → life stage) if user says "Start Wildlife 911"
      → Or answer narratively with safety-first guidance + state directory link
```

### §3.2 The pill's behavior contract

Per the Wildlife911 system prompt's "Golden Rules" (verbatim from Mike's CustomGPT instructions, encoded as Wildlife911 pill rails):

1. Never provide feeding, watering, rearing, or medical treatment instructions.
2. Never improvise or speculate on care.
3. Always direct to a licensed wildlife rehabilitator, veterinarian, or local animal control.
4. Use the YAML file first; use docs/infographics only for clarification.
5. If uncertain, say so explicitly and refer to a professional.

Critical safety reinforcements (verbatim from Wildlife911):

- **Window strikes:** any bird-vs-window event is an emergency, regardless of whether the bird flew away. Always refer.
- **Caught by a cat or dog:** any wild animal that was in a cat's or dog's mouth must be referred immediately, even with no visible injury.

These rails are non-negotiable. The Wildlife911 pill's system prompt encodes them; the WREN safety-test suite (Phase 7d) gains test cases that verify these rails fire correctly.

### §3.3 Persona

The Wildlife911 pill takes on Wildlife911's voice when active: "calm, factual, professional, reassuring, safety-first, never alarmist." This is distinct from WREN's national-research baseline voice. The transition is implicit — the user just sees a more directive, hotline-operator tone when their question is a triage question.

## §4 — Public Wildlife911 surface

Beyond the pill (which lives inside WREN), the public site gets a standalone `/wildlife911/` page that exposes Wildlife911 directly:

- **`/wildlife911/`** — landing page with the iconic "🚨🐾 Start Wildlife 911" entry point. National scope (resolves the user's state from query or geolocation or asks). Defaults to Virginia content while the 49-state expansion is queued.
- **`/wildlife911/start/`** — the dispatcher flow: species menu → life-stage menu → guidance.
- **`/wildlife911/species/<species>/`** — per-species reference pages, rendered from the YAML guide and the species docs.
- **`/wildlife911/state/<XX>/`** — per-state directory page; lists state wildlife agency + AnimalHelpNow as universal fallback. Virginia ships fully populated; other states ship as "AnimalHelpNow is your best starting point" with a placeholder until state-specific content is curated.

The public Wildlife911 surface is accessible without auth. It is part of the public WildlifeStats deployment.

## §5 — Virginia today, national tomorrow

The Wildlife911 corpus is Virginia-scoped. WildlifeStats is a national framework. The reconciliation:

- **Phase 7g ships Virginia-complete.** All Wildlife911 guidance flows correctly for VA users. Non-VA users see a banner: "Wildlife911 currently has full content for Virginia. For your state, we recommend [Animal Help Now](https://animalhelpnow.org) and your state wildlife agency."
- **Phase 7h (queued, future)** — National expansion. The YAML schema gets per-state sections. New YAML fragments authored for the other 49 states + DC, by editorial curation. Architect default: prioritize the 10 highest-population states first (CA, TX, FL, NY, PA, IL, OH, GA, NC, MI), then fill in the rest.
- **The pill architecture supports the expansion structurally** — adding a state is a new YAML fragment, not a code change.

National expansion is an editorial-research project, not an engineer order. Mike or a delegated content lead authors the state-specific content; the engineer ingests it. Out of scope for Phase 7g initial ship.

## §6 — WREN spec original §5 (public/secure config) updates

The original WREN spec §5 specified that public and secure WREN differ only in data context and system prompt. The Wildlife911 pill adds a third axis of difference:

| Aspect | Public WREN | Secure WREN |
|---|---|---|
| Data context | Synthetic cube | Synthetic cube + partner data |
| System prompt | National-research baseline | National-research baseline |
| Wildlife911 pill | **Enabled** | **Enabled** (researchers also get triage if they ask) |
| Triage routing | Wildlife911 pill | Wildlife911 pill |

The pill is available in both surfaces. It is fundamental to WildlifeStats's "anyone from a PhD biostats researcher to an 80-year-old volunteer" promise (lane handoff framing); the volunteer's triage question gets the same Wildlife911 guidance whether they're authenticated or not.

## §7 — Cross-references

- `wildlifestats-wren-architecture-spec-2026-06-10.md` — the original WREN spec. §5 (public/secure config) and §7 (safety rails) are amended by this file.
- `wildlifestats-engineer-order-phase7-wren-2026-06-10.md` — the Phase 7 engineer order. A new sub-PR 7g is added below.
- `wildlifestats-engineer-order-phase7g-wildlife911-pill-2026-06-10.md` — the dispatch for the new sub-PR.
- `wildlifestats/_wren/wildlife911/guides/wildlife_rescue_guides_va.yaml` — the master Wildlife911 guide.

## §8 — License and provenance

- Wildlife911 content is Mike-authored. Per Mike's confirmation 2026-06-10 21:15 ET ("I created it"), the migration into the WildlifeStats repo is authorized.
- License for the migrated corpus: CC-BY 4.0 (matches the WildlifeStats default for documentation per WREN spec §6 governance).
- The CustomGPT instructions file (`Wildlife911-CustomGPT-Instructions.docx`) is NOT committed — it's the system prompt for the OpenAI CustomGPT deployment. The structurally-encoded Wildlife911 system prompt for WREN lives at `wildlifestats/_wren/wildlife911/system-prompt.md` (created by the engineer in Phase 7g sub-PR).

## §9 — What this amendment does NOT do

- Does not deprecate Mike's existing BRWC-homepage Wildlife911 CustomGPT. That deployment continues on BRWC's terms; this amendment establishes a parallel sibling deployment under WildlifeStats branding.
- Does not affect Phase 5 secure tier, Phase 4.5 partner pipeline, or Phase 4.5+ Flyway. Phase 7g is additive to the public WREN.
- Does not commit the national expansion content. Virginia today; 49 states queued for future editorial work.
- Does not deprecate AnimalHelpNow routing. AnimalHelpNow remains the universal fallback for any state where Wildlife911 content isn't yet curated.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 21:20 ET
