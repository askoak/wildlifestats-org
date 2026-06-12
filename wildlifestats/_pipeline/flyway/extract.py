#!/usr/bin/env python3
"""Flyway extraction stage (flyway-spec §4).

Reads scraped posts (the apify_client output), runs each post's text through an
extractor, and writes typed signal records + an audit line. **No raw post text
is ever written to disk** — only the extracted fields and the source_url.

Two extractor backends:
  --extractor offline  Deterministic vocabulary matcher against the committed
                       signal definitions. No API, no cost, reproducible. This
                       is the CI/test backend and the smoke-test backend when
                       the Anthropic key is unavailable.
  --extractor llm      Production backend: Claude (Haiku tier) using
                       extraction-prompt.md. Requires ANTHROPIC_API_KEY in the
                       environment (referenced by name; never read from disk).

Usage:
    python extract.py --posts scraped.json --extractor offline \
        --out secure/cube/flyway/signals/smoke.json \
        --audit secure/cube/flyway/audit/smoke.jsonl
"""
import argparse
import glob
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SIGNALS_DIR = os.path.join(REPO, "wildlifestats", "_pipeline", "sources", "flyway", "signals")
PROMPT_PATH = os.path.join(HERE, "extraction-prompt.md")

STATE_ABBR = {"AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL",
  "IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
  "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX",
  "UT","VT","VA","WA","WV","WI","WY","DC"}


def load_signals():
    sigs = []
    for fp in sorted(glob.glob(os.path.join(SIGNALS_DIR, "*.json"))):
        sigs.append(json.load(open(fp, encoding="utf-8")))
    return sigs


def prompt_hash():
    try:
        return hashlib.sha256(open(PROMPT_PATH, "rb").read()).hexdigest()[:16]
    except OSError:
        return None


# ---- post field normalization (Apify FB / IG shapes vary) ----
def post_text(p):
    for k in ("text", "message", "caption", "postText", "content"):
        if p.get(k):
            return str(p[k])
    return ""


def post_url(p):
    for k in ("url", "postUrl", "facebookUrl", "permalink", "topLevelUrl", "link"):
        if p.get(k):
            return str(p[k])
    return ""


def post_date(p):
    for k in ("time", "timestamp", "date", "publishedTime", "taken_at"):
        v = p.get(k)
        if v:
            m = re.match(r"(\d{4}-\d{2}-\d{2})", str(v))
            if m:
                return m.group(1)
    return None


def post_locality(p):
    for k in ("locationName", "location", "place", "city"):
        v = p.get(k)
        if isinstance(v, dict):
            v = v.get("name")
        if v:
            return str(v)
    return None


def infer_state(text, locality):
    blob = " ".join([x for x in (locality, text) if x])
    m = re.search(r",\s*([A-Z]{2})\b", blob)
    if m and m.group(1) in STATE_ABBR:
        return m.group(1)
    return None


# ---- offline extractor ----
def extract_offline(text, signals):
    low = text.lower()
    best, best_score, best_hit = None, 0, None
    for s in signals:
        hits = [v for v in s["vocabulary"] if v.lower() in low]
        if not hits:
            continue
        score = sum(len(v) for v in hits)  # longer phrases weigh more
        if score > best_score:
            best, best_score, best_hit = s, score, max(hits, key=len)
    if not best:
        return None
    conf = min(0.9, 0.45 + 0.12 * len([v for v in best["vocabulary"] if v.lower() in low]))
    return {"signal": best, "species_verbatim": best_hit, "confidence": round(conf, 2)}


# ---- llm extractor (production; needs ANTHROPIC_API_KEY) ----
def extract_llm(text, signals):
    import urllib.request
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY not set; use --extractor offline or "
                         "set the key in the environment (never read from disk here).")
    catalog = [{"signal_id": s["signal_id"], "vocabulary": s["vocabulary"],
                "subject": s["subject_canonical"]} for s in signals]
    system = open(PROMPT_PATH, encoding="utf-8").read()
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "system": system,
        "messages": [{"role": "user", "content":
                      "CATALOG:\n" + json.dumps(catalog) + "\n\nPOST:\n" + text}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read())
    txt = out["content"][0]["text"]
    m = re.search(r"\{.*\}", txt, re.S)
    parsed = json.loads(m.group(0)) if m else {"matched": False}
    if not parsed.get("matched"):
        return None
    sig = next((s for s in signals if s["signal_id"] == parsed.get("signal_id")), None)
    if not sig:
        return None
    return {"signal": sig, "species_verbatim": parsed.get("species_verbatim"),
            "confidence": parsed.get("confidence", 0.5), "_llm": parsed}


def build_record(p, source_type, hit, method):
    s = hit["signal"]
    text = post_text(p)
    url = post_url(p)
    locality = post_locality(p)
    date = post_date(p)
    llm = hit.get("_llm", {})
    state = llm.get("geo_state") or infer_state(text, locality)
    rid = hashlib.sha256((url + s["signal_id"] + (date or "")).encode()).hexdigest()
    return {
        "record_id": rid,
        "extracted_at": "2026-06-11T00:00:00Z",
        "source_type": source_type,
        "source_url": url,
        "source_org_id": p.get("_org_id"),
        "signal_id": s["signal_id"],
        "extracted_fields": {
            "event_type": s["signal_type"].split(".")[-1],
            "species_canonical": s["subject_canonical"],
            "species_verbatim": hit.get("species_verbatim"),
            "geo_county_fips": None,
            "geo_state": state,
            "geo_locality_verbatim": llm.get("geo_locality_verbatim") or locality,
            "event_date": llm.get("event_date") or date,
            "event_date_precision": llm.get("event_date_precision") or ("day" if date else None),
            "confidence": hit["confidence"],
        },
        "extraction_method": method,
        "extraction_prompt_hash": prompt_hash() if method.startswith("llm") else None,
        "post_text_NOT_STORED": True,
        "license_compliance_notes": "Extract only; original post content not retained per ToS.",
    }


def to_signal_row(rec):
    """Map a §4 extraction record to a bucket_01.signals row (9d.01.2)."""
    ef = rec.get("extracted_fields", {}) or {}
    iso = None
    ev = ef.get("event_date")
    if ev:
        try:
            from datetime import date
            y, m, d = (int(x) for x in str(ev)[:10].split("-"))
            c = date(y, m, d).isocalendar()
            iso = f"{c[0]:04d}-W{c[1]:02d}"
        except (ValueError, TypeError):
            iso = None
    return {
        "record_id": rec.get("record_id"), "signal_id": rec.get("signal_id"),
        "org_slug": rec.get("org_slug"), "source_org_id": rec.get("source_org_id"),
        "platform": rec.get("source_type"), "event_type": ef.get("event_type"),
        "species_canonical": ef.get("species_canonical"),
        "species_verbatim": ef.get("species_verbatim"), "geo_state": ef.get("geo_state"),
        "geo_county_fips": ef.get("geo_county_fips"),
        "geo_locality_verbatim": ef.get("geo_locality_verbatim"),
        "event_date": ef.get("event_date"), "event_date_precision": ef.get("event_date_precision"),
        "confidence": ef.get("confidence"), "iso_week": iso,
        "extraction_method": rec.get("extraction_method"),
        "extraction_prompt_hash": rec.get("extraction_prompt_hash"),
        # provenance envelope: record_id IS a sha → doubles as content_hash
        "fetched_at": rec.get("extracted_at"), "source_url": rec.get("source_url"),
        "content_hash": rec.get("record_id"),
    }


def dual_write_supabase(records):
    """Second leg of the dual-write (JSON already persisted). Each signal flows
    through supabase_client.upsert(); failures are logged, NEVER fatal — the
    JSON path stays canonical. Returns (ok, failed)."""
    try:
        from wildlifestats._pipeline._common import supabase_client
    except ImportError as exc:
        print(f"  supabase dual-write skipped (import: {exc})")
        return (0, 0)
    ok = failed = 0
    for rec in records:
        try:
            supabase_client.upsert(supabase_client.WriteRequest(
                target_schema="wildlifestats_bucket_01_social_signals",
                target_table="signals", on_conflict="record_id",
                record=to_signal_row(rec)))
            ok += 1
        except Exception as exc:  # noqa: BLE001 — Supabase down must not abort the run
            failed += 1
            print(f"  supabase upsert failed ({str(rec.get('record_id'))[:8]}): {type(exc).__name__}")
    print(f"  supabase dual-write: {ok} ok, {failed} failed (JSON already canonical)")
    return (ok, failed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", required=True, help="apify_client output JSON")
    ap.add_argument("--extractor", choices=["offline", "llm"], default="offline")
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--no-supabase", action="store_true",
                    help="skip the Supabase leg of the dual-write (JSON only)")
    args = ap.parse_args()

    signals = load_signals()
    data = json.load(open(args.posts, encoding="utf-8"))
    method = "offline-vocab-matcher-v1" if args.extractor == "offline" \
        else "claude-haiku-flyway-extractor-v1"

    records, audit, scanned, matched = [], [], 0, 0
    for source_type in ("facebook", "instagram"):
        for p in data.get(source_type, []):
            scanned += 1
            text = post_text(p)
            if not text:
                continue
            hit = (extract_offline(text, signals) if args.extractor == "offline"
                   else extract_llm(text, signals))
            audit.append({"source_url": post_url(p), "source_type": source_type,
                          "matched": bool(hit),
                          "signal_id": hit["signal"]["signal_id"] if hit else None,
                          "method": method, "post_text_NOT_STORED": True})
            if hit:
                matched += 1
                records.append(build_record(p, source_type, hit, method))

    for d in (os.path.dirname(args.out), os.path.dirname(args.audit)):
        if d:
            os.makedirs(d, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"generated_with": method, "n_records": len(records),
                   "records": records}, f, ensure_ascii=False, indent=2)
    with open(args.audit, "w", encoding="utf-8", newline="\n") as f:
        for a in audit:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    print(f"scanned {scanned} posts -> {matched} signal records ({method})")
    print(f"records: {args.out}")
    print(f"audit:   {args.audit}")
    # Dual-write leg: JSON above is canonical; Supabase second + non-fatal.
    if not args.no_supabase:
        dual_write_supabase(records)


if __name__ == "__main__":
    main()
