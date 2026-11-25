#!/usr/bin/env python3
"""High-impact open-source PR opportunity finder using gh CLI (Python 3 stdlib only)."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def gh_json(args: list[str], timeout: int = 30):
    proc = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        return None, proc.stderr.strip()
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as e:
        return None, str(e)


def cmd_scan(repos: list[str], limit: int, output: Path) -> None:
    results = []
    for idx, repo in enumerate(repos):
        if idx > 0:
            time.sleep(0.5)
        meta, err = gh_json(["repo", "view", repo, "--json", "nameWithOwner,stargazerCount,primaryLanguage,isArchived,pushedAt,url"])
        if err or not meta:
            results.append({"repo": repo, "error": err or "repo lookup failed"})
            continue

        merged_prs, _ = gh_json(["pr", "list", "--repo", repo, "--state", "merged", "--limit", "20", "--json", "number,mergedAt"])
        issues, i_err = gh_json([
            "issue", "list", "--repo", repo, "--state", "open", "--limit", str(limit),
            "--json", "number,title,url,labels,assignees,comments,createdAt,updatedAt"
        ])
        if i_err or issues is None:
            results.append({"repo": repo, "meta": meta, "error": i_err or "issue lookup failed"})
            continue

        scored = []
        for iss in issues:
            if iss.get("assignees"):
                continue
            labels = [l.get("name", "").lower() for l in iss.get("labels", [])]
            score = 0
            if any(k in labels for k in ["good first issue", "help wanted", "contributions welcome"]):
                score += 40
            if any(k in labels for k in ["bug", "documentation", "enhancement"]):
                score += 20
            comment_cnt = len(iss.get("comments", []))
            if comment_cnt <= 5:
                score += 15
            if merged_prs and len(merged_prs) >= 5:
                score += 25
            scored.append({
                "number": iss["number"],
                "title": iss["title"],
                "url": iss["url"],
                "labels": labels,
                "comments": comment_cnt,
                "mergeability_score": score,
            })

        scored.sort(key=lambda x: x["mergeability_score"], reverse=True)
        results.append({
            "repo": meta.get("nameWithOwner", repo),
            "stars": meta.get("stargazerCount"),
            "language": (meta.get("primaryLanguage") or {}).get("name"),
            "archived": meta.get("isArchived"),
            "recent_merged_prs_sample": len(merged_prs or []),
            "top_opportunities": scored[:limit],
        })

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repos_scanned": len(repos),
        "results": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    print(f"Success! Scanned {len(repos)} repo(s) -> {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub OSS PR Opportunity Finder")
    sub = parser.add_subparsers(dest="command", required=True)
    p_s = sub.add_parser("scan", help="Scan GitHub repos for mergeable open issues")
    p_s.add_argument("--repos", required=True, nargs="+", help="owner/repo list")
    p_s.add_argument("--limit", required=True, type=int, help="Max open issues per repo")
    p_s.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args.repos, args.limit, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
