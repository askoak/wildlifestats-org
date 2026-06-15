#!/usr/bin/env python3
"""
check_national.py
Verify the wildlife911 national directory render is complete and consistent.

Checks:
  1. Every state in ALL_STATES has a rendered index.html
  2. national/index.html exists and links to all 51 state pages
  3. Every state page contains the clinical-advice disclaimer
  4. Centers in centers.yaml appear on the correct state's rendered page
  5. Every state page has agency information (from agencies.yaml)
  6. States with 0 centers still have a page (no-listing fallback rendered)

Exit code 0 = all checks pass; non-zero = one or more failures.
Run from repo root: python wildlifestats/_wren/wildlife911/scripts/check_national.py
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]
CENTERS_YAML = REPO_ROOT / "wildlifestats/_pipeline/sources/rehab-centers/centers.yaml"
AGENCIES_YAML = REPO_ROOT / "wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml"
OUT_ROOT = REPO_ROOT / "wildlifestats/_wren/wildlife911/states"

DISCLAIMER_SENTINEL = "does not provide medical advice"

ALL_STATES = [
    ("AK", "Alaska"), ("AL", "Alabama"), ("AR", "Arkansas"), ("AZ", "Arizona"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DC", "District of Columbia"),
    ("DE", "Delaware"), ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"),
    ("IA", "Iowa"), ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"),
    ("KS", "Kansas"), ("KY", "Kentucky"), ("LA", "Louisiana"), ("MA", "Massachusetts"),
    ("MD", "Maryland"), ("ME", "Maine"), ("MI", "Michigan"), ("MN", "Minnesota"),
    ("MO", "Missouri"), ("MS", "Mississippi"), ("MT", "Montana"), ("NC", "North Carolina"),
    ("ND", "North Dakota"), ("NE", "Nebraska"), ("NH", "New Hampshire"), ("NJ", "New Jersey"),
    ("NM", "New Mexico"), ("NV", "Nevada"), ("NY", "New York"), ("OH", "Ohio"),
    ("OK", "Oklahoma"), ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"),
    ("SC", "South Carolina"), ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"),
    ("UT", "Utah"), ("VA", "Virginia"), ("VT", "Vermont"), ("WA", "Washington"),
    ("WI", "Wisconsin"), ("WV", "West Virginia"), ("WY", "Wyoming"),
]


def check():
    failures = []
    passes = []

    centers = yaml.safe_load(CENTERS_YAML.read_text(encoding="utf-8")) or []
    agencies = yaml.safe_load(AGENCIES_YAML.read_text(encoding="utf-8")) or []
    active_centers = [c for c in centers if c.get("status", "active") == "active"]
    by_state = {}
    for c in active_centers:
        by_state.setdefault(c["state"], []).append(c)

    # Check 1: every state has an index.html
    for code, _ in ALL_STATES:
        page_path = OUT_ROOT / code / "index.html"
        if page_path.exists():
            passes.append(f"[PASS] {code}/index.html exists")
        else:
            failures.append(f"[FAIL] {code}/index.html missing — run render_static_national.py")

    # Check 2: national/index.html exists and links to all 51 states
    national = OUT_ROOT / "national" / "index.html"
    if national.exists():
        passes.append("[PASS] national/index.html exists")
        national_text = national.read_text(encoding="utf-8")
        missing_links = [code for code, _ in ALL_STATES if f"../{code}/" not in national_text]
        if missing_links:
            failures.append(
                f"[FAIL] national/index.html missing links to: {', '.join(missing_links)}"
            )
        else:
            passes.append(f"[PASS] national/index.html links to all {len(ALL_STATES)} states")
    else:
        failures.append("[FAIL] national/index.html missing — run render_static_national.py")

    # Check 3: every state page has the disclaimer
    for code, _ in ALL_STATES:
        page_path = OUT_ROOT / code / "index.html"
        if page_path.exists():
            text = page_path.read_text(encoding="utf-8")
            if DISCLAIMER_SENTINEL in text:
                passes.append(f"[PASS] {code} has disclaimer")
            else:
                failures.append(f"[FAIL] {code}/index.html missing clinical-advice disclaimer")

    # Check 4: centers render to the correct state page
    center_fails = 0
    for code, state_centers in by_state.items():
        page_path = OUT_ROOT / code / "index.html"
        if not page_path.exists():
            continue
        text = page_path.read_text(encoding="utf-8")
        for c in state_centers:
            if c["common_name"] not in text:
                failures.append(
                    f"[FAIL] {code}: '{c['common_name']}' not found on state page"
                )
                center_fails += 1
    if center_fails == 0:
        passes.append(f"[PASS] All {len(active_centers)} centers render on their state page")

    # Check 5: agency info on every state page
    agency_fails = 0
    for a in agencies:
        code = a["jurisdiction"]
        page_path = OUT_ROOT / code / "index.html"
        if page_path.exists():
            text = page_path.read_text(encoding="utf-8")
            sentinel = a["agency_name"][:40]
            if sentinel not in text:
                failures.append(f"[FAIL] {code} agency info missing from state page")
                agency_fails += 1
    if agency_fails == 0:
        passes.append(f"[PASS] All {len(agencies)} agencies render on their state page")

    # Check 6: states with 0 centers still have a page
    zero_center_states = [code for code, _ in ALL_STATES if code not in by_state]
    zero_ok = all((OUT_ROOT / code / "index.html").exists() for code in zero_center_states)
    if zero_ok:
        passes.append(
            f"[PASS] {len(zero_center_states)} zero-center states have fallback pages"
        )
    else:
        failures.append("[FAIL] Some zero-center states are missing fallback pages")

    # Summary
    print(f"\nChecks passed: {len(passes)}")
    print(f"Checks failed: {len(failures)}")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  {f}")
        return 1
    else:
        print("\nAll checks passed.")
        return 0


if __name__ == "__main__":
    sys.exit(check())
