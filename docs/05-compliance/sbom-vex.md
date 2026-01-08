# SBOM and VEX

Every artifact in Itqahn includes a Software Bill of Materials (SBOM). Vulnerabilities are tracked with VEX statements.

---

## SBOM Overview

A Software Bill of Materials lists all components in an artifact:

| Purpose | Benefit |
|---------|---------|
| **Transparency** | Know what's in your software |
| **Vulnerability tracking** | Match CVEs to components |
| **License compliance** | Identify license obligations |
| **Supply chain security** | Detect compromised packages |

---

## SBOM Format

Itqahn uses CycloneDX format (version 1.5+):

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:abc123...",
  "version": 1,
  "metadata": {
    "timestamp": "2026-01-06T12:00:00Z",
    "tools": [
      {
        "vendor": "Syft",
        "name": "syft",
        "version": "0.100.0"
      }
    ],
    "component": {
      "type": "application",
      "name": "user-service",
      "version": "1.2.3",
      "purl": "pkg:docker/user-service@1.2.3"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "express",
      "version": "4.18.2",
      "purl": "pkg:npm/express@4.18.2",
      "licenses": [
        {
          "license": {
            "id": "MIT"
          }
        }
      ],
      "externalReferences": [
        {
          "type": "website",
          "url": "https://expressjs.com"
        }
      ],
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "abc123..."
        }
      ]
    }
  ],
  "dependencies": [
    {
      "ref": "pkg:npm/express@4.18.2",
      "dependsOn": [
        "pkg:npm/body-parser@1.20.2",
        "pkg:npm/cookie@0.5.0"
      ]
    }
  ]
}
```

---

## SBOM Generation

### Container Images

```bash
# Generate SBOM with Syft
syft registry.io/user-service:1.2.3 \
  --output cyclonedx-json \
  --file sbom.cyclonedx.json
```

### Source Code

```bash
# Generate from source
syft dir:./src \
  --output cyclonedx-json \
  --file sbom.cyclonedx.json
```

### CI Integration

```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE }}
    format: cyclonedx-json
    output-file: sbom.cyclonedx.json

- name: Validate SBOM
  run: |
    python tools/validators/sbom_validator.py sbom.cyclonedx.json
```

---

## Vulnerability Scanning

### Scanning with SBOM

```bash
# Scan SBOM for vulnerabilities
grype sbom:sbom.cyclonedx.json \
  --output json \
  --file sca-results.json
```

### Scan Results Format

```json
{
  "matches": [
    {
      "vulnerability": {
        "id": "CVE-2024-1234",
        "severity": "High",
        "description": "...",
        "fix": {
          "versions": ["4.18.3"],
          "state": "fixed"
        }
      },
      "artifact": {
        "name": "express",
        "version": "4.18.2",
        "type": "npm"
      }
    }
  ],
  "source": {
    "type": "sbom",
    "target": "sbom.cyclonedx.json"
  }
}
```

---

## VEX (Vulnerability Exploitability eXchange)

VEX statements document whether vulnerabilities are actually exploitable:

### VEX Status Values

| Status | Meaning |
|--------|---------|
| **not_affected** | Vulnerability doesn't affect this product |
| **affected** | Vulnerability affects this product |
| **fixed** | Vulnerability was fixed |
| **under_investigation** | Still being assessed |

### VEX Document

```json
{
  "@context": "https://openvex.dev/ns/v0.2.0",
  "@id": "https://itqahn.io/vex/user-service/2026-01-06",
  "author": "security-team@itqahn.io",
  "timestamp": "2026-01-06T12:00:00Z",
  "version": 1,
  "statements": [
    {
      "vulnerability": {
        "@id": "https://nvd.nist.gov/vuln/detail/CVE-2024-1234"
      },
      "products": [
        {
          "@id": "pkg:docker/user-service@1.2.3"
        }
      ],
      "status": "not_affected",
      "justification": "vulnerable_code_not_in_execute_path",
      "impact_statement": "The vulnerable function is not used in our codebase"
    }
  ]
}
```

### VEX Justifications

| Justification | When to Use |
|---------------|-------------|
| `component_not_present` | Component not actually in build |
| `vulnerable_code_not_present` | Vulnerable code not included |
| `vulnerable_code_not_in_execute_path` | Code exists but never runs |
| `vulnerable_code_cannot_be_controlled_by_adversary` | No attack vector |
| `inline_mitigations_already_exist` | Mitigations in place |

---

## Policy Enforcement

### SBOM Required

```rego
# policies/opa/supply-chain/sbom_required.rego
package supplychain

deny[msg] {
  not input.evidence_pack.artifacts.sbom
  msg := "SBOM is required for deployment"
}

deny[msg] {
  input.evidence_pack.artifacts.sbom.format != "CycloneDX"
  msg := "SBOM must be in CycloneDX format"
}
```

### Vulnerability Thresholds

```rego
# policies/opa/supply-chain/vulnerability_thresholds.rego
package supplychain

default allow = false

# Block on critical vulnerabilities without VEX
deny[msg] {
  vuln := input.sca_results.matches[_]
  vuln.vulnerability.severity == "Critical"
  not has_vex_statement(vuln.vulnerability.id)
  msg := sprintf("Critical vulnerability %v without VEX statement", [vuln.vulnerability.id])
}

# Allow if VEX says not_affected
allow {
  not any_blocking_vulns
}

any_blocking_vulns {
  vuln := input.sca_results.matches[_]
  vuln.vulnerability.severity in ["Critical", "High"]
  vex := get_vex(vuln.vulnerability.id)
  vex.status == "affected"
}
```

---

## License Compliance

### License Policy

```yaml
# Allowed licenses
licenses:
  allowed:
    - MIT
    - Apache-2.0
    - BSD-2-Clause
    - BSD-3-Clause
    - ISC

  review_required:
    - LGPL-2.1
    - LGPL-3.0
    - MPL-2.0

  disallowed:
    - GPL-2.0
    - GPL-3.0
    - AGPL-3.0
    - SSPL-1.0
```

### License Check

```rego
# policies/opa/supply-chain/license_check.rego
package supplychain

disallowed_licenses := {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL-1.0"}

deny[msg] {
  component := input.sbom.components[_]
  license := component.licenses[_].license.id
  disallowed_licenses[license]
  msg := sprintf("Disallowed license %v in component %v", [license, component.name])
}
```

---

## Dependency Controls

### Allowlist

```yaml
# Approved registries
registries:
  npm:
    - registry.npmjs.org
  docker:
    - ghcr.io/itqahn
    - registry.io
  python:
    - pypi.org
```

### Typosquatting Prevention

```python
def check_typosquat(package_name: str, ecosystem: str) -> bool:
    """Check if package might be typosquatting a popular package"""
    popular = get_popular_packages(ecosystem)

    for p in popular:
        distance = levenshtein_distance(package_name, p)
        if distance == 1 and package_name != p:
            return True  # Possible typosquat

    return False
```

---

## SBOM Storage

| Storage | Purpose |
|---------|---------|
| Evidence Pack | Per-build SBOM |
| Dependency Track | Continuous monitoring |
| S3/GCS | Long-term archive |

### Dependency Track Integration

```bash
# Upload SBOM to Dependency Track
curl -X POST \
  -H "X-API-Key: ${DT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @sbom.cyclonedx.json \
  "https://dependency-track.example.com/api/v1/bom"
```

---

## Related Documents

- `docs/05-compliance/evidence-pack.md` — Evidence Pack structure
- `docs/05-compliance/slsa-provenance.md` — Build provenance
- `tools/validators/sbom_validator.py` — SBOM validation

---

**Version**: 2.0.0 | **Date**: 2026-01-06
