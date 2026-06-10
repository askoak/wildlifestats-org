# Slow-pace protocol (architect)

> **CANONICAL SOURCE (2026-06-10 19:25 EDT):** This was elevated into
> askoak/askoak-web Standing Orders **§21** (slow-pace, incl. the per-tick
> floor, goodnight protocol, and mutual checkin-loop end) and **§22**
> (session-end "Mike we need:" line), with **§0** defining auto mode /
> autopilot. Those sections in askoak-web `main` are the single source of
> truth and govern this lane (§19/§20). This file + its §8.5 engineer notes
> are a lane-local quick-card that COMPOSES with §21/§22 — if they ever
> diverge, askoak-web wins. Read engineer-acknowledged §0/§21/§22 in full
> 2026-06-10 (`soar-aspen-beryl-heron`).

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 16:17 ET
**Status:** Active. Governs the architect seat's behavior during owner-authorized slow-pace windows.
**Mike directive 2026-06-10 16:17 ET:** "goodnight protocol slow pace add a slow pace protocol to use fewer credits but stay active and working"
**Lane scope:** Lands in WildlifeStats lane initially. Candidate for elevation to askoak-web Standing Orders if it proves out; that elevation is a Mike-strategic call, not a self-promotion.

## §1 — Purpose

The default §10 architect polling carve-out fires every 30 minutes for ~15-hour overnight windows. That's ~30 wakes. Most wakes are no-ops (the engineer hasn't shipped anything new since the last tick), but each wake still incurs a small fixed cost to fetch, log, and decide-not-to-act.

Slow pace is the "still on duty, but lower idle cost" mode. The architect remains responsive to engineer-shipped work, but the wake cadence stretches and the per-wake scope narrows.

## §2 — Activation

Slow pace activates when Mike says any of:

- "goodnight" / "good night" (the canonical activation)
- "slow pace" / "slow down" / "low credits"
- "auto mode" combined with end-of-day timing
- An explicit cadence override (e.g. "every 2 hours" or "hourly")

Activation is implicit on these phrases; no popup, no confirmation. The architect adjusts the cadence on the next wake and notes the change in the current session's authorization log file.

## §3 — Cadence

| Mode | Cadence | When to use |
|---|---|---|
| **Active** (default §10 carve-out) | 30 minutes | Engineer is shipping fast, real adjudication likely each tick |
| **Slow pace** (this protocol) | **2 hours** | Engineer is autonomous, ratifications are the only expected work |
| **Skeleton** | 4 hours | Long overnight, engineer typically idle, only major events warrant a wake |

Mike can override with explicit cadence ("every hour", "every 3 hours"). Architect honors and notes.

## §4 — Per-wake scope (slow pace)

Every wake follows this routine and exits as fast as possible:

1. **Programmatic gate (bash_script).** Check `git log <checkpoint>..origin/main` — if empty, exit before the LLM wakes. This costs effectively zero.
2. **If new commits exist:** read the commit messages only. Do not diff files unless a commit message indicates a Phase resolution, an INBOX, or a CROSS-LANE event.
3. **For phase resolutions:** spot-verify with one HEAD curl against the live site (200 check + one acceptance-criterion string check). Post a one-line ratification comment on the merged PR. Stop.
4. **For INBOX files:** read the file. If the question is answerable with a one-paragraph adjudication, write it on a short-lived branch and self-merge per §14. If it needs new specs or new engineer orders, **defer to active-mode cadence** — write a brief note acknowledging the INBOX and switch back to active cadence for the next wake to handle properly. Better to defer than to ship rushed architectural decisions at low-cadence cost ceilings.
5. **For CROSS-LANE events:** read and respond if trivial; defer if substantial. Same logic.
6. **Update the checkpoint, log the tick, exit.**

## §5 — What slow-pace wakes do NOT do

- Do not draft new architecture specs. Architecture work happens at active cadence when Mike is engaged.
- Do not draft new engineer orders. Same reasoning.
- Do not refactor existing handoff files. Same.
- Do not message Mike unless §16 fires (genuine block; popup question with concrete options).
- Do not send notifications. Mike is asleep.
- Do not open status PRs. §17 still applies.
- Do not run multi-step research or browser tasks. Defer.
- Do not spawn subagents. Defer.

## §6 — What slow-pace wakes still WILL do

- Ratify clean phase resolutions with one-line PR comments.
- Self-merge trivial INBOX answers (single-paragraph adjudications on small operational questions).
- Spot-verify live-site endpoints on phase completions.
- Update the architect checkpoint file so the next wake's gate is accurate.
- Escalate genuine blocks via §16 (popup) if the engineer's INBOX raises something only Mike can answer (credentials, partner relationships, scope expansions).
- Terminate the window early per §10 if the engineer reports the build done.

## §7 — Cost discipline

Target per-wake cost in slow pace:

- **Gate-skip wake (no new commits):** ~$0.00 (bash check only, no LLM turn)
- **Routine ratification wake (1-3 new merged PRs):** ≤ $0.05
- **INBOX adjudication wake (real architectural decision):** up to $0.30 (but the architect should defer to active mode for these; see §4.4)

If the architect notices three consecutive wakes exceeding the routine-ratification budget, write a one-line log entry and consider whether the cadence should temporarily revert to active mode — but do NOT message Mike unless §16 fires.

## §8 — Window end

The slow-pace window ends when ANY of:

1. The authorization window's end timestamp arrives (per the active authorization file, e.g. 06:00 ET tomorrow).
2. Mike sends a wake message that supersedes the slow-pace directive.
3. The engineer reports a major phase complete (e.g. Phase 5 secure tier shipped), at which point the architect terminates the window early per §10's self-shrinking rule.
4. The architect detects a §16 block that has been deferred more than 2 cycles — escalate to popup and terminate slow pace.

On window end, the architect logs a closing summary to the authorization file (the original `ARCHITECT-POLL-AUTHORIZATION-<DATE>.md`), deletes the recurring cron, and stands down until summoned.

## §8.5 — Engineer-lane slow pace (added by engineer `soar-aspen-beryl-heron`, 2026-06-10)

Mike directed the engineer seat with the same words ("continue in auto mode,
goodnight protocol, slow pace, fewer credits, stay active and working"). §1–§9
govern the *architect's* polling; this section is the engineer analog.

**Principle.** Stay active and keep shipping the queue, but minimize wasted
cost. The biggest engineer cost sink in a long autonomous run is reprocessing a
large accumulated context on every step — so slow pace favors *focused,
self-contained units of work with clean checkpoints* over one ever-growing
marathon turn.

**In slow pace the engineer:**

1. **Works one order (or one sub-PR) per turn, then lets the turn close.** Each
   merged PR is a durable checkpoint on `main`; the auto-mode wake picks up the
   next unit with fresh, cheaper context. This is more credit-efficient than
   chaining many sub-PRs through a single bloated context.
2. **Trims QA ceremony to what de-risks the change.** Keep the BRWC guard, CI,
   and a single targeted preview/structured check per page. Skip redundant
   screenshots and repeated re-verification once a pattern is proven.
3. **Prefers reusing shipped helpers** (`choropleth.js`, the inline-SVG chart
   pattern, the page chrome) over re-deriving them.
4. **Self-merges per §14** on CI green; does not wait on the architect.
5. **Does not message Mike while he is asleep** unless §16 fires (a genuine
   owner-only block — e.g. the Anthropic key for Phase 7 WREN, a partner
   credential, an irreversible scope decision). Surface those as a single
   concrete popup when the blocking item is actually reached, not preemptively.
6. **Keeps GitHub as the record.** Resolution logs + commit messages are the
   status; no status-report PRs (§17), no notifications (§5).

**Window end** is the same as §8: the authorization end (06:00 ET), a
superseding Mike message, or the build being complete.

## §9 — Cross-references

- §10 (Standing Orders) — architect polling carve-out; this protocol is a refinement of that authority.
- §16 (Standing Orders) — block-on-owner escalation; unaffected by slow pace.
- §17 (Standing Orders) — light the ceremony; the spirit of this protocol.
- §20 — standing-order changes; this protocol stays a WildlifeStats-local convention until Mike elevates it.

## §10 — Tonight's instance

Activated 2026-06-10 16:17 ET (Mike: "continue in auto mode goodnight protocol slow pace").

- Cadence: 2 hours
- Window: until 2026-06-11 06:00 ET (existing authorization end)
- Last active-cadence tick was at 15:30 ET (handled Phase 1-4 ratifications). The 16:00 ET tick will be the last active-cadence wake; the 18:00 ET tick begins slow pace.
- The recurring task is updated from `*/30 * * * *` to `0 */2 * * *` (every two hours on the hour).

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 16:17 ET
