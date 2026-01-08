#!/usr/bin/env python3
"""
SBOM Validator (basic)

Checks that an SBOM file:
- exists
- is valid JSON
- contains minimal fields for SPDX or CycloneDX

This is a lightweight guardrail, not a full SBOM compliance engine.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sbom", required=True, help="Path to SBOM JSON")
    args = ap.parse_args()

    p = Path(args.sbom)
    if not p.exists():
        print(f"SBOM not found: {p}")
        return 1

    try:
        data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"SBOM invalid JSON: {e}")
        return 1

    # SPDX JSON often has "spdxVersion"
    if "spdxVersion" in data:
        print("SBOM looks like SPDX JSON.")
        return 0

    # CycloneDX JSON often has "bomFormat": "CycloneDX"
    if data.get("bomFormat") == "CycloneDX":
        print("SBOM looks like CycloneDX JSON.")
        return 0

    print("SBOM format not recognized (expected SPDX or CycloneDX).")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
