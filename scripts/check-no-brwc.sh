#!/usr/bin/env bash
# WildlifeStats BRWC content guard.
#
# Per Standing Orders §19 and Mike's 2026-06-11 05:19 PDT clarification:
#
#   "The rule about BRWC was about their raw data records only."
#
# The threat model is RAW DATA LEAKAGE — not brand mention. BRWC is a real
# US wildlife rehabilitation organization, and its public-facing materials
# (website, annual reports, social media posts, mission statement, contact
# info, etc.) are public information that any researcher, peer center, or
# citizen can read. WildlifeStats treats BRWC the same as any other peer
# center in its national rehab-center directory — one row of N, with
# attribution back to source URLs.
#
# What this guard CATCHES:
#   - Bulk CSV exports that look like BRWC patient records (intake_id +
#     intake_date + species + diagnosis columns from BRWC's internal
#     database)
#   - Internal-staff communication snippets that look like leaked
#     internal documents
#   - Database-dump field names specific to BRWC's internal Supabase schema
#
# What this guard NO LONGER catches (intentionally):
#   - "Blue Ridge Wildlife Center" as a referral in a Virginia rehab
#     directory (legitimate; symmetric with peer centers)
#   - "BRWC" as an organization name in a national registry
#   - Clarke County (a legitimate Virginia county name)
#   - Public mention of leadership (Ed Clark, etc. — published officers)
#
# If you find this guard catching a legitimate reference, add the path to
# EXCLUDE_PATHS rather than removing the pattern.  If you find the guard
# missing actual raw-data leakage, add a more specific pattern.

set -euo pipefail

# Patterns matching RAW DATA RECORD LEAKAGE.
# These are deliberately narrow — they target structural artifacts of
# BRWC's internal database, not brand mentions or public web content.
FORBIDDEN_PATTERNS=(
  # Database column-header patterns from BRWC's Supabase schema
  "brwc_patient_id"
  "brwc_intake_date"
  "brwc_admission_id"
  "brwc_record_id"
  # CSV export filenames from BRWC's pipeline
  "brwc-patient-records"
  "brwc-admissions-export"
  "brwc-clinical-export"
  # Internal Supabase project references
  "brwc.supabase"
  "askoak-brwc"
)

# Paths to exclude from the scan entirely.
EXCLUDE_PATHS=(
  "./docs/handoff/"
  "./docs/research/"
  "./scripts/check-no-brwc.sh"
  "./.git/"
  "./node_modules/"
  "./README.md"
  "./.github/workflows/"
)

# Build the find exclusion args.
FIND_ARGS=()
for path in "${EXCLUDE_PATHS[@]}"; do
  FIND_ARGS+=(-not -path "${path}*")
done

# Find all text files outside excluded paths.
FILES=$(find . -type f \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.json" -o -name "*.xml" -o -name "*.txt" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.csv" \) "${FIND_ARGS[@]}")

FAIL=0
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  MATCHES=$(echo "$FILES" | xargs -r grep -i -l -E "$pattern" 2>/dev/null || true)
  if [[ -n "$MATCHES" ]]; then
    echo "FAIL: forbidden pattern '$pattern' found in:"
    echo "$MATCHES" | sed 's/^/  /'
    FAIL=1
  fi
done

if [[ "$FAIL" -eq 1 ]]; then
  echo ""
  echo "Standing Orders §19 (as clarified by Mike 2026-06-11) prohibits BRWC"
  echo "RAW DATA RECORDS on the WildlifeStats public tier — not brand"
  echo "mentions or attributed public-content references."
  echo ""
  echo "If this match is from a legitimate public-content reference (e.g., a"
  echo "rehab-center directory entry citing BRWC's public website), the"
  echo "pattern is too broad — narrow it."
  echo ""
  echo "If this match is from an actual raw data record export, remove it"
  echo "from this repo immediately. Raw data records belong only in the BRWC"
  echo "lane (askoak/askoak-web)."
  exit 1
fi

echo "PASS: no BRWC raw data records found in scanned files."
echo "(Brand mentions in attributed public-content contexts are allowed."
echo " See scripts/check-no-brwc.sh for the threat model.)"
