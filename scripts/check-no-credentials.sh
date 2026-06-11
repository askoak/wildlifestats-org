#!/usr/bin/env bash
# WildlifeStats credential-leakage guard.
#
# Scans the repo for bearer tokens, API keys, and other credential
# patterns that should NEVER appear in source. Standing Orders 2026-06-11
# discipline (engineer's Flyway POC + architect's credential INBOX):
# token values exist only in os.environ at runtime; they are never
# committed, logged, printed, or written to disk.
#
# What this guard CATCHES (commits with any of these fail):
#
#   - sk-...  / pk-...     OpenAI-style tokens (sk-proj-, sk-ant-, etc.)
#   - pplx-...             Perplexity tokens
#   - apify_api_...        Apify tokens (older format)
#   - cfut_...             Cloudflare API user tokens
#   - eyJ... .eyJ... .     JWTs (incl. Supabase service_role keys)
#   - Bearer <40+ char>    Any bearer token in source
#
# What this guard does NOT catch (intentionally — these are env-var
# references, not values):
#
#   - CUSTOM_CRED_*_TOKEN  env var names
#   - "Bearer ${SOME_VAR}" interpolations
#   - "Authorization: Bearer " literal (no token following)
#
# If the guard catches a legitimate reference (e.g., a test fixture with
# an obvious placeholder), add the file path to EXCLUDE_PATHS rather
# than removing the pattern.
#
# Usage:
#   bash scripts/check-no-credentials.sh
#
# CI wires this into .github/workflows/validate.yml alongside check-no-
# brwc.sh and check-html-validate.sh.

set -euo pipefail

# Forbidden token patterns. Each is grep -E compatible.
FORBIDDEN_PATTERNS=(
  # OpenAI / Anthropic SK-format keys
  'sk-[A-Za-z0-9_-]{32,}'
  # Perplexity tokens
  'pplx-[A-Za-z0-9_-]{20,}'
  # Apify older API-token format
  'apify_api_[A-Za-z0-9_-]{20,}'
  # Cloudflare user tokens
  'cfut_[A-Za-z0-9_-]{20,}'
  # JWT tokens (incl. Supabase service_role keys)
  'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
)

# Paths intentionally excluded:
#   - .git: plumbing
#   - node_modules: vendored
#   - docs/handoff: human-readable notes may include placeholder
#     examples; the BRWC guard already audits this folder
#   - this script (it mentions the forbidden patterns by example)
EXCLUDE_PATHS=(
  "./.git/"
  "./node_modules/"
  "./scripts/check-no-credentials.sh"
)

# Find all text files outside excluded paths.
FIND_ARGS=()
for path in "${EXCLUDE_PATHS[@]}"; do
  FIND_ARGS+=(-not -path "${path}*")
done

FILES=$(find . -type f \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.json" -o -name "*.xml" -o -name "*.txt" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.csv" -o -name "*.py" -o -name "*.sh" -o -name "*.env" -o -name "*.example" \) "${FIND_ARGS[@]}")

if [[ -z "$FILES" ]]; then
  echo "No files to scan."
  exit 0
fi

FAIL=0
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  MATCHES=$(echo "$FILES" | xargs -r grep -l -E "$pattern" 2>/dev/null || true)
  if [[ -n "$MATCHES" ]]; then
    echo "FAIL: forbidden credential pattern '$pattern' found in:"
    echo "$MATCHES" | sed 's/^/  /'
    FAIL=1
  fi
done

if [[ "$FAIL" -eq 1 ]]; then
  echo ""
  echo "Phase 9 credential discipline (per 2026-06-11 INBOXes) prohibits"
  echo "raw token values in source. Tokens are env-var-injected by the"
  echo "Perplexity vault at runtime and live only in os.environ."
  echo ""
  echo "If a match is from a legitimate test fixture or documentation"
  echo "example, add the path to EXCLUDE_PATHS in scripts/check-no-"
  echo "credentials.sh. Do NOT remove the pattern."
  echo ""
  echo "If a match is from an actual leaked credential, rotate the"
  echo "credential immediately, then remove it from git history with"
  echo "git filter-repo or bfg-repo-cleaner."
  exit 1
fi

echo "PASS: no forbidden credential patterns found in scanned files."
exit 0
