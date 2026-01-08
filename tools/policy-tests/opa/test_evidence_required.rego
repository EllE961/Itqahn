# OPA tests for evidence pack required policies
package deploy_test

import data.deploy

# Test: Deployment with complete evidence pack passes
test_complete_evidence_passes {
    deploy.allow with input as {
        "deployment": {
            "service": "user-service",
            "version": "1.2.3"
        },
        "evidence_pack": {
            "present": true,
            "sbom": {"present": true},
            "provenance": {"present": true, "signed": true},
            "scans": {
                "sast": {"passed": true},
                "sca": {"passed": true, "critical": 0, "high": 0}
            },
            "tests": {"passed": true, "coverage": 85}
        }
    }
}

# Test: Deployment without evidence pack fails
test_missing_evidence_fails {
    not deploy.allow with input as {
        "deployment": {
            "service": "user-service",
            "version": "1.2.3"
        },
        "evidence_pack": {
            "present": false
        }
    }
}

# Test: Deployment without SBOM fails
test_missing_sbom_fails {
    not deploy.allow with input as {
        "deployment": {
            "service": "user-service",
            "version": "1.2.3"
        },
        "evidence_pack": {
            "present": true,
            "sbom": {"present": false},
            "provenance": {"present": true, "signed": true},
            "scans": {"sast": {"passed": true}, "sca": {"passed": true}},
            "tests": {"passed": true}
        }
    }
}

# Test: Deployment with critical vulnerabilities fails
test_critical_vulnerabilities_fails {
    not deploy.allow with input as {
        "deployment": {
            "service": "user-service",
            "version": "1.2.3"
        },
        "evidence_pack": {
            "present": true,
            "sbom": {"present": true},
            "provenance": {"present": true, "signed": true},
            "scans": {
                "sast": {"passed": true},
                "sca": {"passed": false, "critical": 2, "high": 5}
            },
            "tests": {"passed": true}
        }
    }
}

# Test: Deployment with failed tests fails
test_failed_tests_fails {
    not deploy.allow with input as {
        "deployment": {
            "service": "user-service",
            "version": "1.2.3"
        },
        "evidence_pack": {
            "present": true,
            "sbom": {"present": true},
            "provenance": {"present": true, "signed": true},
            "scans": {"sast": {"passed": true}, "sca": {"passed": true}},
            "tests": {"passed": false}
        }
    }
}

# Test: Regulated tier requires signed provenance
test_regulated_requires_signed_provenance {
    not deploy.allow with input as {
        "deployment": {
            "service": "payment-service",
            "version": "1.0.0",
            "compliance_tier": "regulated"
        },
        "evidence_pack": {
            "present": true,
            "sbom": {"present": true},
            "provenance": {"present": true, "signed": false},
            "scans": {"sast": {"passed": true}, "sca": {"passed": true}},
            "tests": {"passed": true}
        }
    }
}
