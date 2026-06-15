"""CLI helpers for the law_watch federal + Regulations.gov paths."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from wildlifestats._pipeline.law_watch import cross_source_bridge as bridge
from wildlifestats._pipeline.law_watch import federal_register as fr
from wildlifestats._pipeline.law_watch import regulations_gov as rg


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "wildlifestats/_pipeline/law_watch/_output"
DEFAULT_FR_SNAPSHOT_PATH = REPO_ROOT / "wildlifestats/_pipeline/_work/law_watch/federal_register/latest.json"
DEFAULT_FR_JSONL_PATH = DEFAULT_OUTPUT_ROOT / "federal_register.jsonl"


def _parse_date(raw: str) -> date:
    return date.fromisoformat(raw[:10])


def _emit_federal_from_snapshot(
    *,
    snapshot_path: Path = DEFAULT_FR_SNAPSHOT_PATH,
    output_path: Path = DEFAULT_FR_JSONL_PATH,
) -> int:
    records = bridge.load_records(snapshot_path)
    bridge.write_jsonl(records, output_path)
    summary_path = output_path.with_name("federal_register-summary.json")
    summary = {
        "source_system": "federal_register_api",
        "record_count": len(records),
        "snapshot_path": str(snapshot_path),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(records)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="pull Federal Register snapshot")
    fetch.add_argument("--since", required=True)
    fetch.add_argument("--agency-slug", action="append", default=list(fr.DEFAULT_AGENCY_SLUGS))

    sub.add_parser("normalize", help="emit Federal Register JSONL from the latest snapshot")
    sub.add_parser("emit", help="emit Federal Register JSONL from the latest snapshot")

    regulations_fetch = sub.add_parser("regulations-fetch", help="cache Regulations.gov raw payloads")
    regulations_fetch.add_argument("--since", required=True)
    regulations_fetch.add_argument("--query", default="")
    regulations_fetch.add_argument("--agency-id", action="append", default=list(rg.DEFAULT_AGENCY_IDS))

    regulations_emit = sub.add_parser("regulations-emit", help="emit Regulations.gov normalized JSONL")
    regulations_emit.add_argument("--cache-date", default=None)

    bridge_cmd = sub.add_parser("bridge", help="bridge Federal Register records with Regulations.gov enrichment")
    bridge_cmd.add_argument("--federal", default=str(DEFAULT_FR_JSONL_PATH))
    bridge_cmd.add_argument("--regulations", default=str(rg.DEFAULT_OUTPUT_ROOT / "regulations_gov.jsonl"))

    args = ap.parse_args()

    if args.command == "fetch":
        since = _parse_date(args.since)
        days_back = max(1, (_parse_date(date.today().isoformat()) - since).days)
        summary = fr.pull_federal_register(days_back=days_back, agency_slugs=args.agency_slug)
        print(
            f"Federal Register search hits: {summary.search_hits} | "
            f"records: {summary.detail_records} | snapshot: {summary.snapshot_path}"
        )
        return

    if args.command in {"normalize", "emit"}:
        count = _emit_federal_from_snapshot()
        print(f"Wrote {count} Federal Register records to {DEFAULT_FR_JSONL_PATH}")
        return

    if args.command == "regulations-fetch":
        bundles = rg.fetch_regulations_gov(
            args.query,
            args.since,
            agency_ids=args.agency_id,
        )
        print(f"Cached {len(bundles)} Regulations.gov document bundles")
        return

    if args.command == "regulations-emit":
        count = rg.emit_regulations_gov_records(cache_date=args.cache_date)
        print(f"Wrote {count} Regulations.gov records to {rg.DEFAULT_OUTPUT_ROOT / 'regulations_gov.jsonl'}")
        return

    count = bridge.emit_enriched_records(
        fr_path=Path(args.federal),
        rg_path=Path(args.regulations),
    )
    print(f"Wrote {count} enriched law_watch records to {bridge.DEFAULT_ENRICHED_PATH}")


if __name__ == "__main__":
    main()
