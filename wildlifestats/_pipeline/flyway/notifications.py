#!/usr/bin/env python3
"""Flyway 4.5+i.3 — weekly digest INBOX + per-trigger alert emitter.

Pure local-artifact code. No credentials, no API calls.

Today the module reads committed file artifacts:
  - `wildlifestats/_pipeline/flyway/spend-log.json`
  - `secure/cube/flyway/triggers/triggers-<iso-week>.json`
  - a caller-specified signal-record JSON file

The split is deliberate:
  - `load_*` helpers are file-backed for the current lane.
  - `render_*` helpers consume plain dict/list payloads so a future signal-store
    reader (for example Supabase) can swap in without rewriting the markdown.

Run:
    python -m wildlifestats._pipeline.flyway.notifications \
        --week 2026-W24 \
        --triggers secure/cube/flyway/triggers/triggers-2026-W24.json \
        --signals secure/cube/flyway/signals/smoke-2026-W24-llm.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from wildlifestats._pipeline.flyway import spend_tracker, triggers

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_HANDOFF_DIR = os.path.join(REPO, "docs", "handoff")
DEFAULT_TRIGGERS_DIR = os.path.join(REPO, "secure", "cube", "flyway", "triggers")


@dataclass(frozen=True)
class InboxDraft:
    filename: str
    body: str


def load_trigger_payload(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_signal_records(path: Optional[str]) -> list[dict]:
    if not path:
        return []
    return triggers.load_records(path)


def week_id_from_text(text: str) -> Optional[str]:
    match = re.search(r"(\d{4}-W\d{2})", text or "")
    return match.group(1) if match else None


def week_sort_key(week_id: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})-W(\d{2})", week_id or "")
    if not match:
        raise ValueError(f"Invalid ISO week: {week_id!r}")
    return int(match.group(1)), int(match.group(2))


def week_bounds(week_id: str) -> tuple[date, date]:
    year, week = week_sort_key(week_id)
    start = date.fromisocalendar(year, week, 1)
    return start, start + timedelta(days=6)


def _parse_dt(value: str) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _money(value: float) -> str:
    return f"${float(value):.2f}"


def _plural(count: int, singular: str, plural: Optional[str] = None) -> str:
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"


def _slug(text: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", (text or "").lower())).strip("-")


def _display_timestamp(value: Optional[str] = None) -> str:
    dt = _parse_dt(value) if value else datetime.now(timezone.utc)
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _week_of_timestamp(value: str) -> Optional[str]:
    dt = _parse_dt(value)
    if dt is None:
        return None
    iso = dt.date().isocalendar()
    return f"{iso[0]:04d}-W{iso[1]:02d}"


def _week_of_record(record: dict) -> Optional[str]:
    if record.get("iso_week"):
        return str(record["iso_week"])
    event_date = (record.get("extracted_fields") or {}).get("event_date") or record.get("event_date")
    if not event_date:
        return None
    try:
        iso = date.fromisoformat(str(event_date)[:10]).isocalendar()
    except ValueError:
        return None
    return f"{iso[0]:04d}-W{iso[1]:02d}"


def filter_runs_for_week(runs: list[dict], week_id: str) -> list[dict]:
    return [run for run in runs if _week_of_timestamp(run.get("timestamp", "")) == week_id]


def filter_records_for_week(records: list[dict], week_id: str) -> list[dict]:
    return [record for record in records if _week_of_record(record) == week_id]


def _distinct(values: list[Optional[str]]) -> list[str]:
    return sorted({value for value in values if value})


def _count_from_runs(runs: list[dict], *, numeric_keys: tuple[str, ...], list_keys: tuple[str, ...]) -> int:
    members: set[str] = set()
    numeric_total = 0
    saw_numeric = False
    for run in runs:
        for key in list_keys:
            value = run.get(key)
            if isinstance(value, (list, tuple, set)):
                members.update(str(item) for item in value if item)
            elif value:
                members.add(str(value))
        if members:
            continue
        for key in numeric_keys:
            value = run.get(key)
            if isinstance(value, (int, float)):
                numeric_total += int(value)
                saw_numeric = True
                break
    if members:
        return len(members)
    return numeric_total if saw_numeric else 0


def _center_count(week_runs: list[dict], week_records: list[dict]) -> int:
    count = _count_from_runs(
        week_runs,
        numeric_keys=("centers_scraped",),
        list_keys=("center_slugs", "centers_scraped", "center_urls"),
    )
    if count:
        return count
    return len(_distinct([
        record.get("source_org_id") or record.get("source_url") for record in week_records
    ]))


def _platform_count(week_runs: list[dict], week_records: list[dict]) -> int:
    count = _count_from_runs(
        week_runs,
        numeric_keys=("platforms_scraped",),
        list_keys=("platforms",),
    )
    if count:
        return count
    return len(_distinct([
        record.get("source_type") or record.get("platform") for record in week_records
    ]))


def weekly_summary(
    *,
    week_id: str,
    trigger_payload: dict,
    signal_records: list[dict],
    spend_runs: list[dict],
    trigger_history: list[tuple[str, dict]],
) -> dict:
    week_runs = filter_runs_for_week(spend_runs, week_id)
    week_records = filter_records_for_week(signal_records, week_id)
    week_start, week_end = week_bounds(week_id)

    weekly_spend = round(sum(float(run.get("total_usd", 0.0)) for run in week_runs), 6)
    actor_runs = sum(int(run.get("actor_runs", 0) or 0) for run in week_runs)
    posts_scanned = sum(int(run.get("posts_scanned", run.get("posts", 0)) or 0) for run in week_runs)
    center_count = _center_count(week_runs, week_records)
    platform_count = _platform_count(week_runs, week_records)

    latest_run = max(
        (dt for dt in (_parse_dt(run.get("timestamp", "")) for run in week_runs) if dt is not None),
        default=None,
    )
    month = latest_run.strftime("%Y-%m") if latest_run else week_end.strftime("%Y-%m")
    month_to_date = spend_tracker.month_to_date(spend_runs, month)
    month_cap = spend_tracker.cap_for(spend_runs, month)

    if latest_run is None:
        rolling_7d = weekly_spend
    else:
        floor = latest_run - timedelta(days=6)
        rolling_7d = round(sum(
            float(run.get("total_usd", 0.0))
            for run in spend_runs
            if (dt := _parse_dt(run.get("timestamp", ""))) is not None and floor <= dt <= latest_run
        ), 6)

    history = {week: payload for week, payload in trigger_history}
    history.setdefault(week_id, trigger_payload)
    ordered_history = sorted(history.items(), key=lambda item: week_sort_key(item[0]))
    zero_trigger_total = sum(1 for _, payload in ordered_history if int(payload.get("n_fired", 0)) == 0)
    zero_trigger_streak = 0
    for _, payload in reversed(ordered_history):
        if int(payload.get("n_fired", 0)) == 0:
            zero_trigger_streak += 1
            continue
        break

    return {
        "week_id": week_id,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "actor_runs": actor_runs,
        "posts_scanned": posts_scanned,
        "center_count": center_count,
        "platform_count": platform_count,
        "signal_records": len(week_records),
        "triggers_fired": int(trigger_payload.get("n_fired", 0)),
        "weekly_spend_usd": weekly_spend,
        "rolling_7d_usd": rolling_7d,
        "month": month,
        "month_to_date_usd": round(month_to_date, 6),
        "month_cap_usd": float(month_cap),
        "zero_trigger_total": zero_trigger_total,
        "zero_trigger_streak": zero_trigger_streak,
    }


def discover_trigger_history(triggers_dir: str = DEFAULT_TRIGGERS_DIR) -> list[tuple[str, dict]]:
    history = []
    for path in sorted(glob.glob(os.path.join(triggers_dir, "triggers-*.json"))):
        week_id = week_id_from_text(os.path.basename(path))
        if not week_id:
            continue
        history.append((week_id, load_trigger_payload(path)))
    return history


def _render_scrape_line(summary: dict) -> str:
    actor_runs = int(summary["actor_runs"])
    posts_scanned = int(summary["posts_scanned"])
    center_count = int(summary["center_count"])
    platform_count = int(summary["platform_count"])
    if posts_scanned > 0:
        bits = [f"{posts_scanned} posts"]
        dimensions = []
        if center_count > 0:
            dimensions.append(_plural(center_count, "center"))
        if platform_count > 0:
            dimensions.append(_plural(platform_count, "platform"))
        if dimensions:
            bits.append("across " + ", ".join(dimensions))
        if actor_runs > 0:
            bits.append(f"({_plural(actor_runs, 'actor-run')})")
        return " ".join(bits)
    if actor_runs > 0:
        bits = [_plural(actor_runs, "actor-run")]
        if center_count > 0 or platform_count > 0:
            tail = []
            if center_count > 0:
                tail.append(_plural(center_count, "center"))
            if platform_count > 0:
                tail.append(_plural(platform_count, "platform"))
            bits.append("across " + ", ".join(tail))
        return " ".join(bits)
    if center_count > 0 or platform_count > 0:
        tail = []
        if center_count > 0:
            tail.append(_plural(center_count, "center"))
        if platform_count > 0:
            tail.append(_plural(platform_count, "platform"))
        return ", ".join(tail)
    return "0 actor-runs"


def render_weekly_digest(
    *,
    summary: dict,
    trigger_payload: dict,
    generated_at: Optional[str] = None,
    trigger_artifact: Optional[str] = None,
) -> str:
    quiet_line = (
        f"- Quiet week: no triggers this week, {_money(summary['weekly_spend_usd'])} spent"
        if summary["triggers_fired"] == 0
        else f"- Trigger alerts emitted: {_plural(summary['triggers_fired'], 'alert')}"
    )
    lines = [
        f"# INBOX — Flyway weekly digest ({summary['week_id']})",
        "",
        "**From:** Flyway cron, `wildlifestats._pipeline.flyway.notifications`",
        "**To:** Mike Oak",
        f"**Date:** {_display_timestamp(generated_at)}",
        "**Channel:** Autonomous mode.",
        f"**Re:** Weekly scrape + trigger summary for {summary['week_id']}",
        "",
        f"- Scrape: {_render_scrape_line(summary)}",
        f"- Signals extracted: {_plural(summary['signal_records'], 'record')}",
        f"- Triggers fired: {summary['triggers_fired']}",
        f"- Spend this week: {_money(summary['weekly_spend_usd'])}",
        f"- Spend month-to-date: {_money(summary['month_to_date_usd'])} / {_money(summary['month_cap_usd'])}",
        f"- Rolling 7-day spend: {_money(summary['rolling_7d_usd'])}",
        f"- Zero-trigger weeks observed: {summary['zero_trigger_total']} total (quiet streak: {summary['zero_trigger_streak']})",
        quiet_line,
    ]
    if trigger_artifact:
        lines.append(f"- Trigger artifact: `{trigger_artifact}`")
    if trigger_payload.get("n_fired", 0):
        fired_titles = [
            f"{item.get('signal_id')} [{item.get('trigger_type')}] {item.get('scope')}"
            for item in trigger_payload.get("fired", [])
        ]
        if fired_titles:
            lines.extend([
                "",
                "## Fired this week",
                "",
                *[f"- {title}" for title in fired_titles],
            ])
    return "\n".join(lines).rstrip() + "\n"


def render_trigger_alert(
    *,
    week_id: str,
    fired: dict,
    generated_at: Optional[str] = None,
    trigger_artifact: Optional[str] = None,
) -> str:
    baseline_bits = []
    if fired.get("baseline_mean") is not None:
        baseline_bits.append(f"mean={fired['baseline_mean']}")
    if fired.get("baseline_stddev") is not None:
        baseline_bits.append(f"stddev={fired['baseline_stddev']}")
    baseline = ", ".join(baseline_bits) if baseline_bits else "n/a"
    provenance = fired.get("provenance") or {}
    centers = provenance.get("centers") or []
    record_ids = provenance.get("record_ids") or []

    lines = [
        f"# INBOX — Flyway trigger fired ({week_id})",
        "",
        "**From:** Flyway cron, `wildlifestats._pipeline.flyway.notifications`",
        "**To:** Mike Oak",
        f"**Date:** {_display_timestamp(generated_at)}",
        "**Channel:** Autonomous mode.",
        f"**Re:** {fired.get('signal_id')} [{fired.get('trigger_type')}] fired for {fired.get('scope')}",
        "",
        f"- Signal: `{fired.get('signal_id')}`",
        f"- Trigger: `{fired.get('trigger_type')}`",
        f"- Scope: `{fired.get('scope')}`",
        f"- Window: `{fired.get('window')}`",
        f"- Observed: {fired.get('observed')}",
        f"- Threshold: {fired.get('threshold')}",
        f"- Baseline: {baseline}",
    ]
    if trigger_artifact:
        lines.append(f"- Trigger artifact: `{trigger_artifact}`")
    if fired.get("reason"):
        lines.append(f"- Reason: {fired['reason']}")
    lines.extend([
        "",
        "## Provenance",
        "",
        f"- Centers: {', '.join(f'`{center}`' for center in centers) if centers else 'none surfaced'}",
        f"- Record IDs: {', '.join(f'`{record_id}`' for record_id in record_ids) if record_ids else 'none surfaced'}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def weekly_digest_filename(week_id: str) -> str:
    return f"INBOX-flyway-weekly-digest-{week_id}.md"


def trigger_alert_filename(week_id: str, fired: dict) -> str:
    stem = "-".join(part for part in (
        _slug(str(fired.get("signal_id", ""))),
        _slug(str(fired.get("trigger_type", ""))),
        _slug(str(fired.get("scope", ""))),
    ) if part)
    return f"INBOX-flyway-trigger-{week_id}-{stem}.md"


def build_weekly_digest_draft(
    *,
    week_id: str,
    trigger_payload: dict,
    signal_records: list[dict],
    spend_runs: list[dict],
    trigger_history: list[tuple[str, dict]],
    generated_at: Optional[str] = None,
    trigger_artifact: Optional[str] = None,
) -> InboxDraft:
    summary = weekly_summary(
        week_id=week_id,
        trigger_payload=trigger_payload,
        signal_records=signal_records,
        spend_runs=spend_runs,
        trigger_history=trigger_history,
    )
    return InboxDraft(
        filename=weekly_digest_filename(week_id),
        body=render_weekly_digest(
            summary=summary,
            trigger_payload=trigger_payload,
            generated_at=generated_at,
            trigger_artifact=trigger_artifact,
        ),
    )


def build_trigger_alert_drafts(
    *,
    week_id: str,
    trigger_payload: dict,
    generated_at: Optional[str] = None,
    trigger_artifact: Optional[str] = None,
) -> list[InboxDraft]:
    drafts = []
    for fired in trigger_payload.get("fired", []):
        drafts.append(InboxDraft(
            filename=trigger_alert_filename(week_id, fired),
            body=render_trigger_alert(
                week_id=week_id,
                fired=fired,
                generated_at=generated_at,
                trigger_artifact=trigger_artifact,
            ),
        ))
    return drafts


def write_drafts(drafts: list[InboxDraft], out_dir: str = DEFAULT_HANDOFF_DIR) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for draft in drafts:
        path = os.path.join(out_dir, draft.filename)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(draft.body)
        written.append(path)
    return written


def emit_notifications(
    *,
    week_id: str,
    trigger_payload: dict,
    signal_records: list[dict],
    spend_runs: list[dict],
    out_dir: str = DEFAULT_HANDOFF_DIR,
    triggers_dir: str = DEFAULT_TRIGGERS_DIR,
    generated_at: Optional[str] = None,
    trigger_artifact: Optional[str] = None,
) -> list[str]:
    history = discover_trigger_history(triggers_dir)
    drafts = [build_weekly_digest_draft(
        week_id=week_id,
        trigger_payload=trigger_payload,
        signal_records=signal_records,
        spend_runs=spend_runs,
        trigger_history=history,
        generated_at=generated_at,
        trigger_artifact=trigger_artifact,
    )]
    drafts.extend(build_trigger_alert_drafts(
        week_id=week_id,
        trigger_payload=trigger_payload,
        generated_at=generated_at,
        trigger_artifact=trigger_artifact,
    ))
    return write_drafts(drafts, out_dir=out_dir)


def main() -> int:
    ap = argparse.ArgumentParser(description="Flyway weekly digest + trigger alert emitter")
    ap.add_argument("--week", default=None, help="ISO week, e.g. 2026-W24")
    ap.add_argument("--triggers", required=True, help="triggers-<iso-week>.json path")
    ap.add_argument("--signals", default=None, help="signal-record JSON path for this week")
    ap.add_argument("--spend-log", default=spend_tracker.SPEND_LOG)
    ap.add_argument("--triggers-dir", default=DEFAULT_TRIGGERS_DIR)
    ap.add_argument("--out-dir", default=DEFAULT_HANDOFF_DIR)
    ap.add_argument("--generated-at", default=None,
                    help="optional ISO timestamp for deterministic test output")
    args = ap.parse_args()

    payload = load_trigger_payload(args.triggers)
    week_id = args.week or week_id_from_text(args.triggers) or week_id_from_text(payload.get("run_id", ""))
    if not week_id:
        raise SystemExit("Could not infer ISO week. Pass --week explicitly.")

    written = emit_notifications(
        week_id=week_id,
        trigger_payload=payload,
        signal_records=load_signal_records(args.signals),
        spend_runs=spend_tracker.load_log(args.spend_log),
        out_dir=args.out_dir,
        triggers_dir=args.triggers_dir,
        generated_at=args.generated_at,
        trigger_artifact=os.path.relpath(args.triggers, REPO),
    )
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
