# Policy Tests

This directory contains tests for OPA and Kyverno policies.

---

## Overview

Policy tests verify that security and compliance policies work as intended.

```
policy-tests/
├── opa/
│   ├── test_mcp_allowlist.rego
│   ├── test_evidence_required.rego
│   ├── test_design_jail.rego
│   └── test_budget_caps.rego
├── kyverno/
│   ├── test_require_limits.yaml
│   └── test_disallow_privileged.yaml
└── fixtures/
    └── *.json (test data)
```

---

## Running Tests

### OPA Tests

```bash
# Run all OPA tests
opa test policies/opa/ tools/policy-tests/opa/ -v

# Run specific test file
opa test policies/opa/mcp/ tools/policy-tests/opa/test_mcp_allowlist.rego -v

# Run with coverage
opa test policies/opa/ tools/policy-tests/opa/ --coverage
```

### Kyverno Tests

```bash
# Run Kyverno tests with kyverno CLI
kyverno test tools/policy-tests/kyverno/

# Or use chainsaw for E2E testing
chainsaw test tools/policy-tests/kyverno/
```

---

## Test Structure

### OPA Test Example

```rego
# tools/policy-tests/opa/test_mcp_allowlist.rego
package mcp_test

import data.mcp

# Test: Backend builder can read GitHub
test_backend_builder_github_read {
    mcp.allow with input as {
        "agent_type": "backend-builder",
        "mcp": "github",
        "operation": "repo.read"
    }
}

# Test: Backend builder cannot write to Kubernetes
test_backend_builder_k8s_write_denied {
    not mcp.allow with input as {
        "agent_type": "backend-builder",
        "mcp": "kubernetes",
        "operation": "deployment.scale"
    }
}
```

### Kyverno Test Example

```yaml
# tools/policy-tests/kyverno/test_require_limits.yaml
apiVersion: cli.kyverno.io/v1alpha1
kind: Test
metadata:
  name: test-require-limits
policies:
  - ../../../policies/kyverno/require-resource-limits.yaml
resources:
  - resource_with_limits.yaml
  - resource_without_limits.yaml
results:
  - policy: require-resource-limits
    rule: check-limits
    resources:
      - resource_with_limits.yaml
    result: pass
  - policy: require-resource-limits
    rule: check-limits
    resources:
      - resource_without_limits.yaml
    result: fail
```

---

## CI Integration

```yaml
# .github/workflows/policy-tests.yaml
name: Policy Tests

on:
  push:
    paths:
      - 'policies/**'
  pull_request:
    paths:
      - 'policies/**'

jobs:
  opa-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup OPA
        uses: open-policy-agent/setup-opa@v2
      - name: Run OPA Tests
        run: opa test policies/opa/ tools/policy-tests/opa/ -v

  kyverno-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Kyverno CLI
        uses: kyverno/action-install-cli@v0.2.0
      - name: Run Kyverno Tests
        run: kyverno test tools/policy-tests/kyverno/
```

---

## Related

- `policies/opa/` — OPA policies
- `policies/kyverno/` — Kyverno policies
- `policies/policy-catalog.md` — Policy inventory

---

**Version**: 2.0.0 | **Date**: 2026-01-06
