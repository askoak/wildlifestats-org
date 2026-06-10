# Architect poll-window authorization (§10 carve-out)

**Architect seat:** `measured-fern-jasper-thrush` (WildlifeStats lane)
**Authorized by:** Mike, 2026-06-10 14:36 ET
**Verbatim:** "you can check in every 30 minutes on automode standing order until 6am eastern tomorrow. use as few credits as possible. Engineer was given full autonomous permission"

## Parameters

| Field | Value |
|---|---|
| Scope | WildlifeStats lane only (askoak/wildlifestats-org) |
| Max cadence | one wake per 30 minutes |
| End condition | 2026-06-11 06:00 ET, OR engineer reports Phase 2 complete with all acceptance criteria met, whichever comes first |
| Mode | automatic — engineer is fully autonomous; no Mike relay required |
| Cost discipline | self-shrink per §10 — skip wakes when nothing needs adjudication; exit early on phase completion |

## What "wake" means in this window

On each scheduled tick the architect:

1. `git fetch origin main && git log --oneline <last-checkpoint>..origin/main`
2. If nothing new on main → log "no-op, nothing to adjudicate", exit immediately (cheapest possible turn).
3. If new commits exist → read the diff for engineer order Resolutions, INBOX files, or any architect-summoned content. Adjudicate where needed (one-line PR comment if useful per §13.2). Otherwise log and exit.
4. If the engineer has reported a phase complete AND acceptance criteria are met → log completion, end the authorization window early, stand down until summoned.

## What this is NOT

- Not a license to draft phase plans, refine specs, or open status PRs (§17).
- Not a license to summon the engineer with new orders unless an acceptance criterion fails (§14 says revert is the default).
- Not a license to message Mike with status — Mike checks in when Mike checks in (§17).

## Termination

This authorization expires automatically at 2026-06-11 06:00 ET or when this file is updated with a `## Closed` section citing the closing turn's commit. Whichever first.
