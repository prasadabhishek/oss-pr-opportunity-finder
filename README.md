# OSS PR Opportunity Finder

Agent skill and Python 3 stdlib CLI (powered by `gh` CLI) to scout active GitHub repositories for high-impact, mergeable open-source contribution opportunities.

## Install as an Agent Skill

```bash
npx skills add prasadabhishek/oss-pr-opportunity-finder
```

## Standalone CLI Usage

Requires an authenticated GitHub CLI (`gh auth login`).

```bash
uv run scripts/oss_finder.py scan \
  --repos astral-sh/uv cli/cli \
  --limit 15 \
  --output /tmp/oss-opportunities.json
```

## License

MIT
