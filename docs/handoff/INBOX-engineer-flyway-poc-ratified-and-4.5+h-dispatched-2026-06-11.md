# INBOX — Flyway POC ratified + Phase 4.5+h dispatched (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 10:15 ET
**Re:** Closing PR #33, advancing Flyway to 4.5+h baseline + triggers

## Ratification

PR #33 (5936f02, 69887dc) is **ratified**. Excellent work across the board:

- **Token discipline held perfectly.** `APIFY_TOKEN` referenced by env-var name only, never read into your context, never appeared in any commit, never surfaced in a PR description. The pattern transfers cleanly to the rest of Phase 9.
- **Cost discipline held.** ~$0.30 against a $5-10 cap. Two-tier monthly Apify spend remains sustainable.
- **Audit log is correct.** `post_text_NOT_STORED: true` on all 46 lines. Zero raw-text fields. The §19 separation contract is intact under real load.
- **6 real records with proper geographic attribution.** NY (Wild Bird Fund: patient #5,000, +12% YoY volume signal; Brooklyn kestrel nestling; Prospect Park fledgling) and TN (Walden's Puddle baby-season intake). Honest, attributable, and the volume-signal in particular is the kind of finding a baseline can trigger on.
- **The zero-hummingbird-arrival output is correct, not a defect.** June is past the Feb-May arrival window. You inferred this and produced honest baby-season records instead. That's better science than forcing the original signal.
- **The offline-matcher-returns-zero finding is genuinely valuable.** Real wildlife-rehab posts don't use the narrow seed phrases. The vocabulary list is a *prior*, not a matcher. Offline stays as the deterministic CI/test backend; LLM is the production recall path. Documented at architect level.

## My damage acknowledged

The 577-error html-validate gate was architect-caused (PRs #31, #32, #35). You diagnosed it cleanly, asked the right question, separated the fix into its own branch, ran a careful sweep, kept the renderer-fix recommendation visible, and shipped PRs #34 and #36 to unblock the repo. That was the right way to handle architect-lane damage, and it cost you a half-morning that should have been Phase 4.5+h.

This INBOX ships the architect's commitments on that:

1. **`render_directory.py` hardened at source.** `safe()` now html-escapes every interpolated value by default; the few hardcoded labels containing `&` are now written as `&amp;`; all leadership/accreditation/source-URL interpolations are explicitly wrapped. Verified clean (0 errors, 3 long-title warnings only) against the full repo's 260 HTML files. Re-rendering will no longer recreate the gate damage.
2. **`scripts/check-html-validate.sh` added.** Architect precommit hook that runs the same command the CI gate uses. Will catch the next regression before push, not after merge.
3. **Renderer-discipline rules codified** in the script's header comment block. The next time architect adds a renderer (Phase 9 bucket renderers, sector-funders directory, USFWS office maps, etc.), the discipline is enforced at the file level, not by memory.

## Phase 4.5+h authorized

Per your post-mortem recommendation, proceed to **Phase 4.5+h** (baseline + triggers). Scope:

- **Establish per-signal baselines** on the existing 47-post smoke-test corpus + whatever incremental backfill is cheap. For `phenology.baby_season_start.songbird`: per-state, per-week intake-volume baseline. For other signals: weekly mention-count baseline from the seed roster.
- **Trigger logic.** A trigger fires when a current-week signal exceeds the baseline by a documented threshold. Threshold choice is yours; surface the chosen threshold in the PR description with rationale. My prior: 2σ above 8-week rolling baseline for volume signals; ≥3 distinct centers reporting a signal in a 7-day window for presence/absence signals.
- **Output.** A `triggers.json` artifact per cube run, listing fired triggers with provenance (which post, which center, which week, which baseline, which threshold). This is the audit trail that justifies a recurring spend later.
- **No new social spend.** Phase 4.5+h is analytical, not ingestion. Reuse the 47-post corpus + the §22 cube already shipped. If you need more data for the baseline, surface that as a separate authorization request — don't quietly spend.
- **The daily cron stays DISABLED.** Phase 4.5+i remains gated behind Mike's recurring-spend authorization. Per your post-mortem: 4.5+h proving a trigger fires on real data is the input for that decision.

## Production LLM extractor — codify the Anthropic credential

When you scaffold the production extractor (or when you fold the Flyway extract.py into Phase 9 `_common/`), use `custom-cred:api.anthropic.com` via env-injection — same pattern as Apify. The env var name is `CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN`. First use in the thread requires a one-time `approve_credential` consent. This eliminates the env-shadow workaround.

Codify in `wildlifestats/_pipeline/_common/creds.py`:

```python
def get_anthropic_token() -> str:
    """Return the Anthropic API token from env (vault-injected via
    custom-cred:api.anthropic.com). Raises if missing — never falls
    back to disk, never logs the value."""
    tok = os.environ.get("CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN", "").strip()
    if not tok:
        raise RuntimeError(
            "ANTHROPIC token not in env. Invoke bash with "
            "api_credentials=['custom-cred:api.anthropic.com']."
        )
    return tok
```

Same shape for Apify, Exa, OpenAI, Voyage, Perplexity, Supabase, Zenodo. These are the architect-ratified rules from the 2026-06-11 09:30 credential discipline INBOX; nothing new here, just the production codification path.

## Architect queue forward look

After this commit lands:

- Architect: scaffold `wildlifestats/_pipeline/_common/` (creds.py, fetch.py, exa_client.py, claude_client.py, apify_client.py, supabase_client.py) with the discipline rules codified.
- Architect: write full Phase 9 engineer order (10-bucket taxonomy + RLS contract on the askoak Supabase + sub-PR sequencing).
- Engineer: Phase 4.5+h baseline + triggers.

Independent rails. No coordination required. We surface when work lands.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 10:15 ET
