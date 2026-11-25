---
name: oss-pr-opportunity-finder
description: >-
  Scans target GitHub repositories via the gh CLI to identify high-impact,
  actually mergeable open-source contribution opportunities (good first issues,
  bug reports, stalled PR gaps), checks maintainer responsiveness and recent
  merge velocity, and outputs a ranked PR blueprint. Use when looking for open
  source issues to contribute to or scouting high-value PRs.
---

# OSS PR Opportunity Finder

## Overview

Finds high-signal, mergeable open-source issues across any list of GitHub repositories—filtering out dead repos and unmaintained issue trackers by checking recent commit/merge activity via `gh` CLI.

## Dependencies

- **`gh` CLI** (authenticated GitHub CLI): Used to query repo metadata, recent merged PRs, and open issues without hitting unauthenticated API rate limits.

## Quick Start

```bash
uv run scripts/oss_finder.py scan \
  --repos astral-sh/uv cli/cli \
  --limit 15 \
  --output /tmp/oss-opportunities.json
```

## Utility Scripts

`scripts/oss_finder.py` uses Python 3 standard library + `gh` CLI with polite 0.5s pacing between repo calls.

### Subcommands
- **`scan --repos <owner/repo...> --limit <N> --output <path.json>`**:
  - Fetches repo star count, default branch, language, and recent merged PR count (last 30 days) to score **maintainer responsiveness**.
  - Fetches open issues (preferring `good first issue` / `help wanted` / `bug`, excluding already-assigned issues).
  - Ranks opportunities by mergeability (active maintainers + clear labels + low comment noise) and writes structured JSON to `--output`.

## Workflow

1. **Scout Candidate Repos:** Run `oss_finder.py scan` on the user's target repos or domain list.
2. **Filter Out Dead Trackers:** Discard repos with `0` merged PRs in the last 30–60 days unless the user explicitly wants to fork/revive them.
3. **Produce PR Blueprint:** For the top 3–5 issues, inspect the linked repo's `CONTRIBUTING.md`, test command, and target files, then output a concise blueprint: Issue URL, Problem Statement, Target Files, Implementation Plan, and Local Verification Command.

## Common Mistakes

- **Working on issues with an open linked PR:** Always check whether someone already submitted a PR for the issue before writing code.
- **Ignoring repo style/test guidelines:** Read `CONTRIBUTING.md` and run the repo's exact linter/test command before opening a PR.
