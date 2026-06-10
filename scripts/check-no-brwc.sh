#!/usr/bin/env bash
# Fails if any committed file (excluding docs/handoff/ and this script itself)
# contains a forbidden BRWC-identifying string. Per Standing Orders §19, the
# WildlifeStats public tier carries zero BRWC content. This guard enforces
# that by build.

set -euo pipefail

# Forbidden strings — case-insensitive matching.
# Add to this list as new BRWC-specific terms are identified.
FORBIDDEN_PATTERNS=(
  "blue ridge wildlife"
  "brwc"
  "jen riley"
  "dr\\. riley"
  "clarke county"
  "boyce, va"
  "boyce virginia"
  "askoak\\.michaeloak"
)

# Paths to exclude — these are allowed to mention BRWC for handoff/coordination
# purposes. Public site content (everything else) is not.
EXCLUDE_PATHS=(
  "./docs/handoff/"
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
FILES=$(find . -type f \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.json" -o -name "*.xml" -o -name "*.txt" -o -name "*.toml" \) "${FIND_ARGS[@]}")

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
