#!/usr/bin/env python3
"""Thin Apify actor wrapper for Flyway (flyway-spec §2 / actors-config.json).

Reads the API token from the APIFY_TOKEN environment variable — the token is
never read from disk, printed, logged, or committed (per the credential policy).
Stdlib-only (urllib); no external dependency.

Usage (library):
    from apify_client import scrape_facebook, scrape_instagram
    posts = scrape_facebook(["https://www.facebook.com/lindsaywildlife"],
                            limit=15, newer_than="120 days")
"""
import json
import os
import urllib.request
import urllib.error

API = "https://api.apify.com/v2"


def _token():
    tok = os.environ.get("APIFY_TOKEN")
    if not tok:
        raise SystemExit(
            "APIFY_TOKEN is not set in the environment. Set it locally "
            "(e.g. from the Credentials\\apify.env file) and re-run; this "
            "script never reads the secret from disk itself.")
    return tok


def run_actor(actor_id, run_input, timeout=540):
    """Run an actor synchronously and return its dataset items (list)."""
    slug = actor_id.replace("/", "~")
    url = f"{API}/acts/{slug}/run-sync-get-dataset-items?token={_token()}"
    data = json.dumps(run_input).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def scrape_facebook(page_urls, limit=15, newer_than="120 days"):
    run_input = {
        "startUrls": [{"url": u} for u in page_urls],
        "resultsLimit": limit,
        "captionText": False,
    }
    if newer_than:
        run_input["onlyPostsNewerThan"] = newer_than
    return run_actor("apify/facebook-posts-scraper", run_input)


def scrape_instagram(usernames, limit=15):
    run_input = {"username": list(usernames), "resultsLimit": limit}
    return run_actor("apify/instagram-post-scraper", run_input)


def fetch_dataset(dataset_id, limit=1000):
    """Fetch items from an existing Apify dataset by id (e.g. from a prior run)."""
    url = f"{API}/datasets/{dataset_id}/items?token={_token()}&clean=true&limit={limit}"
    with urllib.request.urlopen(url, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--facebook", nargs="*", default=[])
    ap.add_argument("--instagram", nargs="*", default=[])
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--newer-than", default="120 days")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = {"facebook": [], "instagram": []}
    if args.facebook:
        out["facebook"] = scrape_facebook(args.facebook, args.limit, args.newer_than)
    if args.instagram:
        out["instagram"] = scrape_instagram(args.instagram, args.limit)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"facebook posts: {len(out['facebook'])}  instagram posts: {len(out['instagram'])}")
