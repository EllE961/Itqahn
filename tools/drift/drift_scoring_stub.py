#!/usr/bin/env python3
"""
Drift scoring stub.

Replace with your real evaluation method (embedding similarity, structured checks, test mapping).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intent", required=True, help="Path to intent JSON (PRD/AC references)")
    ap.add_argument("--diff", required=True, help="Path to diff summary JSON")
    ap.add_argument("--out", default="drift_report.json")
    args = ap.parse_args()

    intent = json.loads(Path(args.intent).read_text(encoding="utf-8"))
    diff = json.loads(Path(args.diff).read_text(encoding="utf-8"))

    # naive placeholder score
    score = 0.15 if diff.get("files_changed", 0) <= 10 else 0.35

    report = {
        "score": score,
        "hotspots": diff.get("paths", [])[:10],
        "notes": [
            "This is a stub. Implement real drift scoring before relying on this gate."
        ],
        "intent_ref": intent.get("id", "unknown")
    }

    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} with score={score}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
