#!/usr/bin/env python3
"""
Drift scoring tool.

Compares implementation against requirements to detect divergence.
Replace with your real evaluation method (embedding similarity,
structured checks, test mapping).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def calculate_drift_score(intent: dict, diff: dict) -> float:
    """
    Calculate drift score between intent and implementation.

    This is a placeholder implementation. Replace with:
    - Embedding similarity comparison
    - Structured requirement-to-test mapping
    - AST analysis of code changes

    Args:
        intent: Requirements document (PRD/AC references)
        diff: Code change summary

    Returns:
        Drift score between 0.0 (no drift) and 1.0 (complete drift)
    """
    files_changed = diff.get("files_changed", 0)
    lines_changed = diff.get("lines_changed", 0)

    # Naive placeholder scoring
    # TODO: Replace with real drift analysis
    if files_changed <= 5 and lines_changed <= 200:
        return 0.10
    elif files_changed <= 10 and lines_changed <= 500:
        return 0.25
    elif files_changed <= 20:
        return 0.40
    else:
        return 0.60


def identify_hotspots(diff: dict, limit: int = 10) -> list[str]:
    """
    Identify files most likely to have drifted.

    Args:
        diff: Code change summary
        limit: Maximum hotspots to return

    Returns:
        List of file paths that are potential drift hotspots
    """
    paths = diff.get("paths", [])
    # Prioritize certain file patterns
    priority_patterns = ["auth", "security", "payment", "api"]

    hotspots = []
    for path in paths:
        for pattern in priority_patterns:
            if pattern in path.lower():
                hotspots.insert(0, path)
                break
        else:
            hotspots.append(path)

    return hotspots[:limit]


def generate_suggestions(score: float, hotspots: list[str]) -> list[str]:
    """
    Generate remediation suggestions based on drift analysis.

    Args:
        score: Calculated drift score
        hotspots: Identified hotspot files

    Returns:
        List of suggested actions
    """
    suggestions = []

    if score > 0.4:
        suggestions.append(
            "High drift detected. Review requirements alignment."
        )
    if score > 0.2:
        suggestions.append(
            "Consider adding tests to verify requirement coverage."
        )

    auth_hotspots = [h for h in hotspots if "auth" in h.lower()]
    if auth_hotspots:
        suggestions.append(
            f"Security-sensitive files changed: {', '.join(auth_hotspots)}"
        )

    if not suggestions:
        suggestions.append("Drift within acceptable range.")

    return suggestions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate drift score between intent and implementation"
    )
    parser.add_argument(
        "--intent",
        required=True,
        help="Path to intent JSON (PRD/AC references)"
    )
    parser.add_argument(
        "--diff",
        required=True,
        help="Path to diff summary JSON"
    )
    parser.add_argument(
        "--out",
        default="drift_report.json",
        help="Output report path"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.4,
        help="Drift threshold for warnings"
    )
    args = parser.parse_args()

    # Load inputs
    intent = json.loads(Path(args.intent).read_text(encoding="utf-8"))
    diff = json.loads(Path(args.diff).read_text(encoding="utf-8"))

    # Calculate drift
    score = calculate_drift_score(intent, diff)
    hotspots = identify_hotspots(diff)
    suggestions = generate_suggestions(score, hotspots)

    # Build report
    report = {
        "score": score,
        "threshold": args.threshold,
        "status": "pass" if score <= args.threshold else "fail",
        "hotspots": hotspots,
        "suggestions": suggestions,
        "intent_ref": intent.get("id", "unknown"),
        "files_analyzed": diff.get("files_changed", 0),
        "notes": [
            "This is a stub implementation.",
            "Replace with real drift scoring before production use."
        ]
    }

    # Write output
    Path(args.out).write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(f"Drift Report: {args.out}")
    print(f"  Score: {score:.2f}")
    print(f"  Status: {report['status']}")
    print(f"  Hotspots: {len(hotspots)}")

    # Exit with error if above threshold
    return 0 if score <= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
