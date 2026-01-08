#!/usr/bin/env python3
"""
Design Jail Validator (lightweight)

Goal: prevent accidental UI style drift by enforcing:
- no new standalone CSS files outside the design system
- no raw hex colors / rgb() values in application code
- no hard-coded px values in app code (prefer tokens/utilities)

This is intentionally conservative. Tune allowlists for your repo.

Exit codes:
  0 = pass
  1 = violations found
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")
RGB_COLOR = re.compile(r"\brgba?\(")
PX_VALUE = re.compile(r"\b\d+px\b")

DEFAULT_ALLOWED_CSS_DIRS = [
    "design-system",
    "styles",
]

DEFAULT_ALLOWED_FILE_GLOBS = [
    "**/*.stories.*",  # storybook can be special-cased
]

@dataclass
class Finding:
    path: str
    line: int
    kind: str
    snippet: str

def iter_files(root: Path, exts: Tuple[str, ...]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in exts:
            yield p

def is_allowed_css(path: Path, allowed_dirs: List[str]) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in allowed_dirs)

def matches_any_glob(path: Path, patterns: List[str], root: Path) -> bool:
    rel = path.relative_to(root)
    s = str(rel)
    for pat in patterns:
        # very small glob matcher; use fnmatch-style patterns
        from fnmatch import fnmatch
        if fnmatch(s, pat):
            return True
    return False

def scan_file(path: Path) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        findings.append(Finding(str(path), 0, "read_error", str(e)))
        return findings

    for i, line in enumerate(text.splitlines(), start=1):
        if HEX_COLOR.search(line):
            findings.append(Finding(str(path), i, "hex_color", line.strip()[:200]))
        if RGB_COLOR.search(line):
            findings.append(Finding(str(path), i, "rgb_color", line.strip()[:200]))
        if PX_VALUE.search(line):
            findings.append(Finding(str(path), i, "px_value", line.strip()[:200]))
    return findings

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--allowed-css-dirs", default=",".join(DEFAULT_ALLOWED_CSS_DIRS))
    ap.add_argument("--allow-globs", default=",".join(DEFAULT_ALLOWED_FILE_GLOBS))
    args = ap.parse_args()

    root = Path(args.root).resolve()
    allowed_css_dirs = [x.strip() for x in args.allowed_css_dirs.split(",") if x.strip()]
    allow_globs = [x.strip() for x in args.allow_globs.split(",") if x.strip()]

    violations: List[Finding] = []

    # 1) Standalone CSS restriction
    for css in iter_files(root, (".css", ".scss")):
        if matches_any_glob(css, allow_globs, root):
            continue
        if not is_allowed_css(css, allowed_css_dirs):
            violations.append(Finding(str(css), 0, "css_outside_design_system", "CSS file not in allowed directories"))

    # 2) Raw styling values in TS/TSX/JS/JSX/CSS
    for p in iter_files(root, (".ts", ".tsx", ".js", ".jsx", ".css", ".scss")):
        if matches_any_glob(p, allow_globs, root):
            continue
        # Skip node_modules and build artifacts
        if "node_modules" in p.parts or ".next" in p.parts or "dist" in p.parts:
            continue
        for f in scan_file(p):
            # Allow px in design-system only
            if f.kind == "px_value" and is_allowed_css(p, allowed_css_dirs):
                continue
            if f.kind in ("hex_color", "rgb_color", "px_value"):
                violations.append(f)

    if violations:
        print("Design Jail violations found:\n")
        for v in violations[:500]:
            loc = f"{v.path}:{v.line}" if v.line else v.path
            print(f"- [{v.kind}] {loc} :: {v.snippet}")
        print(f"\nTotal violations: {len(violations)}")
        return 1

    print("Design Jail: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
