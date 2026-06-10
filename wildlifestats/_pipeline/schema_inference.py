#!/usr/bin/env python3
"""Pipeline stage 2 — schema inference.

For each file in the inventory, reads the header row and a sample of values,
infers a coarse dtype per column, and writes one schema document per file to
_work/schemas/<file-hash>.json. This stage proposes structure; it does not map
or transform (that is stage 3 field_mapping).

Inferred dtypes: integer, number, date, string (best-effort, conservative).

Usage:
    python wildlifestats/_pipeline/schema_inference.py \
        --inventory wildlifestats/_pipeline/_work/inventory.json \
        --out-dir wildlifestats/_pipeline/_work/schemas
"""
import argparse
import csv
import json
import os
import re

DATE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-[A-Za-z]{3}-\d{4})$")
INT_RE = re.compile(r"^-?\d+$")
NUM_RE = re.compile(r"^-?\d+\.\d+$")


def infer_dtype(values):
    vals = [v for v in values if v not in (None, "")]
    if not vals:
        return "string"
    def all_match(rx):
        return all(rx.match(str(v).strip()) for v in vals)
    if all_match(INT_RE):
        return "integer"
    if all(INT_RE.match(str(v).strip()) or NUM_RE.match(str(v).strip()) for v in vals):
        return "number"
    if all_match(DATE_RE):
        return "date"
    return "string"


def read_rows(path, fmt, limit=50):
    """Return (headers, list-of-row-dicts up to limit)."""
    if fmt == "csv":
        with open(path, encoding="utf-8", errors="replace", newline="") as f:
            sniff = f.readline()
            delim = "\t" if "\t" in sniff else (";" if ";" in sniff else ",")
            f.seek(0)
            r = csv.DictReader(f, delimiter=delim)
            headers = [h.strip() for h in (r.fieldnames or [])]
            rows = []
            for i, row in enumerate(r):
                if i >= limit:
                    break
                rows.append({k.strip(): (v or "").strip() for k, v in row.items()})
            return headers, rows
    if fmt == "json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = [data]
        headers = list(data[0].keys()) if data else []
        return headers, [{k: ("" if v is None else v) for k, v in d.items()} for d in data[:limit]]
    if fmt == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        headers = [str(h).strip() if h is not None else "" for h in next(it, [])]
        rows = []
        for i, raw in enumerate(it):
            if i >= limit:
                break
            rows.append({headers[j]: ("" if raw[j] is None else raw[j])
                         for j in range(min(len(headers), len(raw)))})
        wb.close()
        return headers, rows
    return [], []


def schema_for(file_rec):
    path, fmt = file_rec["path"], file_rec["format"]
    headers, rows = read_rows(path, fmt)
    n = len(rows) or 1
    columns = []
    for h in headers:
        col_vals = [r.get(h, "") for r in rows]
        non_null = sum(1 for v in col_vals if v not in (None, ""))
        samples = [str(v) for v in col_vals if v not in (None, "")][:3]
        columns.append({
            "name": h,
            "dtype": infer_dtype(col_vals),
            "fraction_non_null": round(non_null / n, 3),
            "sample_values": samples,
        })
    return {
        "path": path,
        "sha256": file_rec["sha256"],
        "format": fmt,
        "n_columns": len(columns),
        "columns": columns,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="wildlifestats/_pipeline/_work/inventory.json")
    ap.add_argument("--out-dir", default="wildlifestats/_pipeline/_work/schemas")
    args = ap.parse_args()

    with open(args.inventory, encoding="utf-8") as f:
        inv = json.load(f)
    os.makedirs(args.out_dir, exist_ok=True)
    count = 0
    for rec in inv["files"]:
        schema = schema_for(rec)
        out = os.path.join(args.out_dir, rec["sha256"][:16] + ".json")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2, sort_keys=False)
        count += 1
        print(f"  {rec['path']}: {schema['n_columns']} columns -> {os.path.basename(out)}")
    print(f"schema_inference: {count} schemas -> {args.out_dir}")


if __name__ == "__main__":
    main()
