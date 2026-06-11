#!/usr/bin/env bash
# Fails if any committed file (excluding docs/handoff/ and this script itself)
# contains a forbidden BRWC-identifying string. Per Standing Orders §19, the
# WildlifeStats public tier carries zero BRWC content. This guard enforces
# that by build.

set -euo pipefail

# Forbidden strings — case-insensitive matching.
# Add to this list as new BRWC-specific terms are identified.
#
# NOTE on "clarke county": the original guard blocked the bare string, but
# "Clarke County" is a real US county name in six states (AL, GA, IA, MS, VA,
# WA) and the national county dataset (county-fips.json / the synthetic cube)
# legitimately lists all of them as structured Census rows. The BRWC identifier
# is the *prose frame* "Clarke County, Virginia" plus Boyce / Blue Ridge, not
# the bare census name. We therefore match "clarke county, v" (catches ", VA"
# and ", Virginia" in prose) so a BRWC framing still fails the guard while the
# national Census data passes. Flagged to the architect for ratification.
FORBIDDEN_PATTERNS=(
  "blue ridge wildlife"
  "brwc"
  "jen riley"
  "dr\\. riley"
  "clarke county, v"
  "boyce, va"
  "boyce virginia"
  "askoak\\.michaeloak"
)

# Paths to exclude — these are allowed to mention BRWC for legitimate reasons:
#   - docs/handoff/ : architect/engineer coordination files (BRWC is named in
#     cross-lane handoffs, scope notes, lane-discipline references).
#   - docs/research/ : research appendices may cite published academic work that
#     references real wildlife centers (e.g. McRuer 2017's Wildlife Center of
#     Virginia citation in the cat-impact appendix).
#   - wildlifestats/_wren/wildlife911/states/ : state-specific Wildlife911
#     editions intentionally list local wildlife rehabilitation centers as
#     referral recommendations. Virginia's edition recommends Blue Ridge
#     Wildlife Center, Wildlife Center of Virginia, and SW VA Wildlife Center
#     as legitimate Virginia rehab options for triage users. This is correct
#     Virginia public-safety information, not BRWC content contamination.
#     §19 prevents BRWC-as-source-of-WildlifeStats-content, NOT BRWC-as-a-
#     Virginia-rehabilitation-referral.
#   - The national template at wildlifestats/_wren/wildlife911/templates/
#     national/ is BRWC-scrubbed and IS subject to the guard.
EXCLUDE_PATHS=(
  "./docs/handoff/"
  "./docs/research/"
  "./wildlifestats/_wren/wildlife911/states/"
  "./wildlifestats/_pipeline/sources/README.md"
  "./.github/workflows/"
  "./scripts/check-no-brwc.sh"
  "./.git/"
  "./node_modules/"
  "./README.md"
)

# Build the find exclusion args.
FIND_ARGS=()
for path in "${EXCLUDE_PATHS[@]}"; do
  FIND_ARGS+=(-not -path "${path}*")
done

# Find all text files outside excluded paths.
FILES=$(find . -type f \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.json" -o -name "*.xml" -o -name "*.txt" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" \) "${FIND_ARGS[@]}")

FAIL=0
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  # -i case-insensitive, -E extended regex, -l list files only.
  MATCHES=$(echo "$FILES" | xargs -r grep -i -l -E "$pattern" 2>/dev/null || true)
  if [[ -n "$MATCHES" ]]; then
    echo "FAIL: forbidden pattern '$pattern' found in:"
    echo "$MATCHES" | sed 's/^/  /'
    FAIL=1
  fi
done

if [[ "$FAIL" -eq 1 ]]; then
  echo ""
  echo "Standing Orders §19 prohibits BRWC content on the WildlifeStats public tier."
  echo "If the match is intentional (e.g., in a handoff file), add the path to EXCLUDE_PATHS."
  exit 1
fi

echo "PASS: no BRWC content found in non-handoff files."
