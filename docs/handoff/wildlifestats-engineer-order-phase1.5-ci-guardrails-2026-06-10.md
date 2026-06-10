# Engineer order — Phase 1.5: CI guardrails

**From:** Architect, `measured-fern-jasper-thrush`
**To:** WildlifeStats Engineer
**Date:** 2026-06-10 ~14:35 ET
**Repo:** askoak/wildlifestats-org
**Branch base:** `main` (after Order #1 / Phase 1 merges)
**Authority:** §13 elevated ship + §14 self-merge eligibility.
**Single concern:** add automated guardrails so future PRs can't accidentally regress.

## Why this exists

Phase 1 ships the structural framework. Before Phase 2 starts mechanical search-and-replace work across many files, we want CI that:

1. **Catches BRWC contamination automatically.** Any future PR — Phase 2 rebrand, Phase 4 content, anything — fails CI if BRWC's identifying strings appear in committed files. §19 boundary enforced by the build, not by reviewer attention.
2. **Catches broken internal links.** Section landings cross-link in Phase 4; a Phase 2 rename that breaks a path should fail CI, not 404 in production.
3. **Catches malformed HTML.** Pure static site, no framework — a missing close tag goes unnoticed until someone visits the page. CI catches it.

This order is small, additive, and reversible. Single PR.

## Scope — what ships in this PR

### 1. `.github/workflows/validate.yml`

A GitHub Actions workflow that runs on `pull_request` and on `push` to `main`. Three jobs, all required to pass before merge once branch protection is configured (branch protection is OUT of scope for this PR — engineer ships the workflow; Mike configures protection separately if he wants).

```yaml
name: validate

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  brwc-content-guard:
    name: BRWC content guard
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check for forbidden strings
        run: bash scripts/check-no-brwc.sh

  link-check:
    name: Internal link check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install link checker
        run: npm install -g linkinator@6
      - name: Check internal links
        run: |
          linkinator . \
            --recurse \
            --skip "^https?://" \
            --skip "^mailto:" \
            --skip "node_modules" \
            --skip ".git"

  html-validate:
    name: HTML validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install html-validate
        run: npm install -g html-validate@8
      - name: Validate HTML files
        run: |
          html-validate \
            --config .htmlvalidate.json \
            $(find . -name "*.html" -not -path "./node_modules/*" -not -path "./.git/*")
```

### 2. `scripts/check-no-brwc.sh`

```bash
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
```

Make it executable: `chmod +x scripts/check-no-brwc.sh`. Commit with the executable bit preserved (`git update-index --chmod=+x scripts/check-no-brwc.sh` before commit, or set executable on the file before `git add`).

### 3. `.htmlvalidate.json`

A restrained html-validate config — strict enough to catch real bugs, loose enough that Phase 2 search-and-replace work doesn't trip every rule.

```json
{
  "extends": ["html-validate:recommended"],
  "rules": {
    "no-trailing-whitespace": "off",
    "void-style": "off",
    "no-inline-style": "off",
    "no-implicit-button-type": "warn",
    "wcag/h30": "warn",
    "wcag/h32": "warn",
    "wcag/h36": "warn",
    "wcag/h37": "warn",
    "wcag/h67": "warn",
    "wcag/h71": "warn"
  },
  "elements": [
    "html5"
  ]
}
```

### 4. README footer line

Append to the existing README:

```markdown
## CI

`.github/workflows/validate.yml` runs on every PR. Three jobs:

- **BRWC content guard** — `scripts/check-no-brwc.sh` fails if forbidden BRWC-identifying strings appear outside `docs/handoff/`.
- **Internal link check** — `linkinator` checks all internal links resolve.
- **HTML validation** — `html-validate` checks HTML well-formedness.

All three must pass for §14 self-merge eligibility.
```

## Self-test before opening the PR

Run locally:

```bash
bash scripts/check-no-brwc.sh
npx linkinator . --recurse --skip "^https?://" --skip "^mailto:"
npx html-validate --config .htmlvalidate.json $(find . -name "*.html" -not -path "./node_modules/*" -not -path "./.git/*")
```

All three should pass on the Phase 1 deliverables. If any fail, fix in this PR before merge (e.g., a Phase 1 page has an unclosed tag, or `linkinator` doesn't like the empty sitemap — adjust the config or fix the file).

## Out of scope

- Branch protection rules on `main` (Mike's call; this PR doesn't touch GitHub repo settings).
- Lighthouse / Axe accessibility scans (Phase 6).
- Visual regression testing (deferred indefinitely — pure static site, low value).
- A separate "preview-deploy URL probe" job (Netlify's own preview deploys cover that).

## Acceptance criteria

1. PR is opened and all three CI jobs run.
2. All three CI jobs pass green on the PR.
3. After merge, the same three jobs run on `main` and pass green.
4. `scripts/check-no-brwc.sh` is executable in the committed tree (`git ls-files --stage scripts/check-no-brwc.sh` shows mode `100755`).

## Commit and merge

- Branch: `engineer/phase1.5-ci-guardrails`.
- Commit message: `feat(wildlifestats): add CI guardrails — BRWC content guard, link check, HTML validate`. Body explains what each job catches and why it's worth automating now (before Phase 2's mass search-and-replace).
- Trailer: `Engineer: <your-seat-sig>`.
- Self-merge per §14 once all three jobs pass green. Single concern, additive, reversible by `git revert`.
- After merge, append a `## Resolution` section to this order file citing the merge commit hash. Move the file to `docs/handoff/closed/`.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:35 ET
