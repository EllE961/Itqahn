#!/usr/bin/env python3
"""
Evidence Pack Validator

Validates:
- manifest JSON conforms to schema (draft-07)
- referenced artifact paths exist
- computes a simple signature hash (sha256 of canonical JSON)

This is not a cryptographic signing system; it is a CI guardrail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import jsonschema
except ImportError:
    jsonschema = None

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def validate_schema(manifest: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    if jsonschema is None:
        return ["jsonschema not installed; cannot validate schema"]
    v = jsonschema.Draft7Validator(schema)
    errors = sorted(v.iter_errors(manifest), key=lambda e: e.path)
    return [f"{list(e.path)}: {e.message}" for e in errors]

def path_exists(repo_root: Path, rel_path: str) -> bool:
    if not rel_path:
        return False
    p = (repo_root / rel_path).resolve()
    try:
        p.relative_to(repo_root.resolve())
    except Exception:
        # prevent path traversal
        return False
    return p.exists()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Repo root")
    ap.add_argument("--manifest", required=True, help="Path to evidence pack manifest JSON")
    ap.add_argument("--schema", default="templates/compliance/evidence-pack-manifest.schema.json")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = (repo_root / args.manifest).resolve()
    schema_path = (repo_root / args.schema).resolve()

    manifest = load_json(manifest_path)
    schema = load_json(schema_path)

    errs = validate_schema(manifest, schema)
    if errs:
        print("Schema validation errors:")
        for e in errs:
            print(f"- {e}")
        return 1

    missing: List[str] = []

    # Validate known artifact paths
    artifacts = manifest.get("artifacts", {})
    sbom_path = artifacts.get("sbom", {}).get("path", "")
    prov_path = artifacts.get("provenance", {}).get("path", "")
    if not path_exists(repo_root, sbom_path):
        missing.append(f"SBOM path missing: {sbom_path}")
    if not path_exists(repo_root, prov_path):
        missing.append(f"Provenance path missing: {prov_path}")

    for scan in artifacts.get("scans", []):
        if not path_exists(repo_root, scan.get("path", "")):
            missing.append(f"Scan path missing: {scan.get('path','')}")
    for t in artifacts.get("tests", []):
        if not path_exists(repo_root, t.get("path", "")):
            missing.append(f"Test artifact path missing: {t.get('path','')}")
    for a in artifacts.get("approvals", []):
        if not path_exists(repo_root, a.get("path", "")):
            missing.append(f"Approval artifact path missing: {a.get('path','')}")

    if missing:
        print("Missing referenced artifacts:")
        for m in missing:
            print(f"- {m}")
        return 1

    computed_sig = sha256(canonical_json(manifest))
    provided_sig = manifest.get("signature_hash", "")

    print("Evidence Pack: schema OK, artifacts present.")
    print(f"Computed signature_hash: {computed_sig}")
    if provided_sig and provided_sig != computed_sig:
        print(f"WARNING: provided signature_hash differs from computed ({provided_sig})")
        # treat as failure to be strict
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
