#!/usr/bin/env bash
# WildlifeStats html-validate gate (architect precommit hook).
#
# Runs the same html-validate command the CI gate uses. Intended to be
# invoked locally before `git push` to prevent shipping HTML that breaks
# the gate on main. The 2026-06-11 incident (577 errors, 176 files
# blocking the engineer's Flyway POC PR for half a morning) is the
# proximate cause of this hook.
#
# Usage:
#   bash scripts/check-html-validate.sh
#
# Exits non-zero if any error-level findings exist. Warnings are
# tolerated (long-title and wcag warnings do not fail CI).
#
# Architect lane discipline:
#   - Renderers that emit HTML from YAML MUST route every interpolated
#     value through render_directory.py's safe() helper or an equivalent
#     html.escape(quote=True) call. The 2026-06-11 failure was caused by
#     un-escaped prose like "Fish & Wildlife" and "intake <50 animals/year".
#   - Hardcoded labels containing & in source code MUST be written as
#     &amp; (e.g. "Wildlife help &amp; species guides"), not as raw &,
#     so they round-trip through any double-escape-safe renderer.
#   - This hook is the safety net; it is not a substitute for the
#     discipline above.

set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "SKIP: npx not available — html-validate hook requires Node 20+"
  exit 0
fi

# Limit to HTML files we author; exclude vendored, generated-test, and
# git plumbing.
FILES=$(find . -name "*.html" \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./docs/research/*" \
)

if [[ -z "$FILES" ]]; then
  echo "No HTML files found."
  exit 0
fi

echo "Running html-validate against $(echo "$FILES" | wc -l | tr -d ' ') HTML files..."

# Capture output; tolerate warnings, fail on errors.
OUTPUT=$(npx --no-install html-validate --config .htmlvalidate.json $FILES 2>&1 || true)
ERROR_LINE=$(echo "$OUTPUT" | grep -E "^✖ .*problems" || true)

if [[ -z "$ERROR_LINE" ]]; then
  echo "PASS: html-validate found nothing to report."
  exit 0
fi

# Extract error count from line like "✖ 154 problems (151 errors, 3 warnings)"
ERROR_COUNT=$(echo "$ERROR_LINE" | grep -oE "[0-9]+ errors" | grep -oE "[0-9]+" || echo "0")

if [[ "$ERROR_COUNT" -gt 0 ]]; then
  echo "FAIL: html-validate found $ERROR_COUNT errors."
  echo ""
  echo "$OUTPUT" | tail -40
  echo ""
  echo "Renderer discipline (see comment block at top of this script):"
  echo "  - Pipe YAML-sourced strings through safe() / html.escape()"
  echo "  - Write hardcoded labels with &amp; not &"
  echo "  - Run this hook locally before pushing"
  exit 1
fi

echo "PASS: html-validate found $ERROR_LINE (warnings only, no errors)."
exit 0
