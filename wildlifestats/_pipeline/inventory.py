#!/usr/bin/env python3
"""Pipeline stage 1 — inventory.

Walks an input directory and writes _work/inventory.json: one record per
discovered partner file (path, sha256, size, row estimate, format). No file
content is transformed here; this stage only catalogs what arrived.

Determinism: when WILDLIFESTATS_DETERMINISTIC=1, discovered_at is clamped to a
fixed value so repeated runs are byte-identical (used in CI).

Usage:
    python wildlifestats/_pipeline/inventory.py --input samples/partners/ \
        --out wildlifestats/_pipeline/_work/inventory.json
"""
import argparse
import hashlib
import json
import os

SUPPORTED = {".xlsx": "xlsx", ".csv": "csv", ".json": "json"}
DETERMINISTIC_TS = "2026-01-01T00:00:00Z"


def now_iso():
    if os.environ.get("WILDLIFESTATS_DETERMINISTIC") == "1":
        return DETERMINISTIC_TS
    # Avoid importing datetime.now in deterministic mode; only used live.
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def estimate_rows(path, fmt):
    try:
        if fmt == "csv":
            with open(path, encoding="utf-8", errors="replace") as f:
                return max(0, sum(1 for _ in f) - 1)  # minus header
        if fmt == "json":
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return len(data) if isinstance(data, list) else 1
        if fmt == "xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(path, read_only=True)
            ws = wb.active
            n = ws.max_row or 0
            wb.close()
            return max(0, n - 1)
    except Exception:
        return None
    return None


def inventory(input_dir):
    records = []
    for root, _dirs, files in os.walk(input_dir):
        for name in sorted(files):
            ext = os.path.splitext(name)[1].lower()
            if ext not in SUPPORTED:
                continue
            path = os.path.join(root, name)
            fmt = SUPPORTED[ext]
            records.append({
                "path": path.replace(os.sep, "/"),
                "sha256": sha256_of(path),
                "size_bytes": os.path.getsize(path),
                "rows_estimate": estimate_rows(path, fmt),
                "format": fmt,
                "discovered_at": now_iso(),
            })
    records.sort(key=lambda r: r["path"])
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="wildlifestats/_pipeline/_work/inventory.json")
    args = ap.parse_args()

    records = inventory(args.input)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"input": args.input, "n_files": len(records), "files": records},
                  f, ensure_ascii=False, indent=2, sort_keys=False)
    print(f"inventory: {len(records)} files -> {args.out}")
    return records


if __name__ == "__main__":
    main()
