# Reference Links

This appendix provides external references to standards, frameworks, and tools used by Itqahn.

---

## Security Standards

### NIST

| Resource | URL | Used For |
|----------|-----|----------|
| NIST SSDF (SP 800-218) | https://csrc.nist.gov/publications/detail/sp/800-218/final | Secure SDLC framework |
| NIST CSF | https://www.nist.gov/cyberframework | Cybersecurity framework |
| NIST SP 800-53 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final | Security controls |

### OWASP

| Resource | URL | Used For |
|----------|-----|----------|
| OWASP ASVS | https://owasp.org/www-project-application-security-verification-standard/ | Application security verification |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ | Web application risks |
| OWASP LLM Top 10 | https://genai.owasp.org/llm-top-10/ | LLM-specific risks |
| OWASP Cheat Sheets | https://cheatsheetseries.owasp.org/ | Security best practices |
| OWASP Testing Guide | https://owasp.org/www-project-web-security-testing-guide/ | Security testing methodology |

### Supply Chain Security

| Resource | URL | Used For |
|----------|-----|----------|
| SLSA | https://slsa.dev/ | Supply chain levels |
| SLSA Requirements | https://slsa.dev/spec/v1.0/requirements | SLSA implementation |
| in-toto | https://in-toto.io/ | Supply chain attestation |
| Sigstore | https://www.sigstore.dev/ | Keyless signing |
| Cosign | https://docs.sigstore.dev/cosign/overview/ | Container signing |

---

## Infrastructure & Platform

### Identity & Secrets

| Resource | URL | Used For |
|----------|-----|----------|
| SPIFFE | https://spiffe.io/ | Workload identity standard |
| SPIRE | https://spiffe.io/spire/ | SPIFFE implementation |
| HashiCorp Vault | https://developer.hashicorp.com/vault | Secrets management |
| Vault Tutorials | https://developer.hashicorp.com/vault/tutorials | Vault implementation guides |

### Policy Enforcement

| Resource | URL | Used For |
|----------|-----|----------|
| Open Policy Agent (OPA) | https://www.openpolicyagent.org/ | General policy engine |
| Rego Language | https://www.openpolicyagent.org/docs/latest/policy-language/ | Policy language |
| Kyverno | https://kyverno.io/ | Kubernetes policies |
| Kyverno Policies | https://kyverno.io/policies/ | Policy examples |

### Kubernetes & GitOps

| Resource | URL | Used For |
|----------|-----|----------|
| Kubernetes Docs | https://kubernetes.io/docs/ | Container orchestration |
| ArgoCD | https://argo-cd.readthedocs.io/ | GitOps deployment |
| Flux | https://fluxcd.io/ | GitOps toolkit |
| Helm | https://helm.sh/ | Package management |

### Workflow Orchestration

| Resource | URL | Used For |
|----------|-----|----------|
| Temporal | https://temporal.io/ | Workflow orchestration |
| Temporal Docs | https://docs.temporal.io/ | Implementation guide |
| Temporal Go SDK | https://docs.temporal.io/dev-guide/go | Go SDK reference |

---

## Observability

### Monitoring & Telemetry

| Resource | URL | Used For |
|----------|-----|----------|
| OpenTelemetry | https://opentelemetry.io/ | Observability framework |
| OTel Specification | https://opentelemetry.io/docs/specs/ | Standard specification |
| Prometheus | https://prometheus.io/ | Metrics collection |
| Grafana | https://grafana.com/ | Visualization |
| Loki | https://grafana.com/oss/loki/ | Log aggregation |
| Tempo | https://grafana.com/oss/tempo/ | Distributed tracing |

### SRE Practices

| Resource | URL | Used For |
|----------|-----|----------|
| Google SRE Book | https://sre.google/sre-book/table-of-contents/ | SRE principles |
| SRE Workbook | https://sre.google/workbook/table-of-contents/ | SRE implementation |
| Sloth | https://sloth.dev/ | SLO generation |

---

## Software Composition

### SBOM Standards

| Resource | URL | Used For |
|----------|-----|----------|
| CycloneDX | https://cyclonedx.org/ | SBOM format |
| CycloneDX Spec | https://cyclonedx.org/specification/overview/ | SBOM specification |
| SPDX | https://spdx.dev/ | Alternative SBOM format |
| VEX | https://cyclonedx.org/capabilities/vex/ | Vulnerability exploitability |

### Dependency Scanning

| Resource | URL | Used For |
|----------|-----|----------|
| Trivy | https://aquasecurity.github.io/trivy/ | Vulnerability scanning |
| Grype | https://github.com/anchore/grype | Vulnerability scanner |
| Syft | https://github.com/anchore/syft | SBOM generation |
| OSV | https://osv.dev/ | Vulnerability database |

---

## Security Scanning

### Static Analysis (SAST)

| Resource | URL | Used For |
|----------|-----|----------|
| Semgrep | https://semgrep.dev/ | SAST scanning |
| Semgrep Rules | https://semgrep.dev/r | Rule repository |
| CodeQL | https://codeql.github.com/ | GitHub SAST |
| Bandit | https://bandit.readthedocs.io/ | Python security |

### Dynamic Analysis (DAST)

| Resource | URL | Used For |
|----------|-----|----------|
| OWASP ZAP | https://www.zaproxy.org/ | Web app testing |
| Nuclei | https://nuclei.projectdiscovery.io/ | Vulnerability scanning |
| Burp Suite | https://portswigger.net/burp | Web security testing |

### Secret Scanning

| Resource | URL | Used For |
|----------|-----|----------|
| Gitleaks | https://gitleaks.io/ | Secret detection |
| TruffleHog | https://trufflesecurity.com/trufflehog | Credential scanning |
| detect-secrets | https://github.com/Yelp/detect-secrets | Pre-commit scanning |

---

## Testing

### Contract Testing

| Resource | URL | Used For |
|----------|-----|----------|
| Pact | https://pact.io/ | Consumer-driven contracts |
| Pact Docs | https://docs.pact.io/ | Implementation guide |
| Schemathesis | https://schemathesis.readthedocs.io/ | API testing |

### Performance Testing

| Resource | URL | Used For |
|----------|-----|----------|
| k6 | https://k6.io/ | Load testing |
| Locust | https://locust.io/ | Load testing |
| Artillery | https://www.artillery.io/ | Performance testing |

### Chaos Engineering

| Resource | URL | Used For |
|----------|-----|----------|
| Chaos Mesh | https://chaos-mesh.org/ | Kubernetes chaos |
| Litmus | https://litmuschaos.io/ | Chaos experiments |
| Gremlin | https://www.gremlin.com/ | Failure injection |

---

## Developer Platform

### Service Catalog

| Resource | URL | Used For |
|----------|-----|----------|
| Backstage | https://backstage.io/ | Developer portal |
| Backstage Plugins | https://backstage.io/plugins | Plugin ecosystem |
| TechDocs | https://backstage.io/docs/features/techdocs/ | Documentation |

### CI/CD

| Resource | URL | Used For |
|----------|-----|----------|
| GitHub Actions | https://docs.github.com/en/actions | CI/CD workflows |
| GitLab CI | https://docs.gitlab.com/ee/ci/ | CI/CD pipelines |
| Tekton | https://tekton.dev/ | Kubernetes-native CI/CD |
| Dagger | https://dagger.io/ | Portable CI/CD |

---

## Design Systems

### Token Management

| Resource | URL | Used For |
|----------|-----|----------|
| Style Dictionary | https://amzn.github.io/style-dictionary/ | Token transformation |
| Figma Tokens | https://www.figma.com/community/plugin/843461159747178978 | Figma integration |
| Design Tokens W3C | https://www.w3.org/community/design-tokens/ | Standard specification |

### Component Libraries

| Resource | URL | Used For |
|----------|-----|----------|
| Storybook | https://storybook.js.org/ | Component documentation |
| Chromatic | https://www.chromatic.com/ | Visual testing |

---

## AI/ML Security

### LLM Security

| Resource | URL | Used For |
|----------|-----|----------|
| OWASP LLM Top 10 | https://genai.owasp.org/llm-top-10/ | LLM risks |
| NIST AI RMF | https://www.nist.gov/itl/ai-risk-management-framework | AI risk management |
| Anthropic Claude Docs | https://docs.anthropic.com/ | Claude API reference |

### Prompt Security

| Resource | URL | Used For |
|----------|-----|----------|
| Prompt Injection Attacks | https://simonwillison.net/2022/Sep/12/prompt-injection/ | Background reading |
| AI Village | https://aivillage.org/ | AI security community |

---

## Track Assurance & Drift Detection

### Semantic Similarity

| Resource | URL | Used For |
|----------|-----|----------|
| Sentence Transformers | https://www.sbert.net/ | Semantic embeddings |
| OpenAI Embeddings | https://platform.openai.com/docs/guides/embeddings | Text embeddings |
| Anthropic Embeddings | https://docs.anthropic.com/en/docs/build-with-claude/embeddings | Claude embeddings |
| Cosine Similarity | https://en.wikipedia.org/wiki/Cosine_similarity | Similarity measurement |

### Requirements Traceability

| Resource | URL | Used For |
|----------|-----|----------|
| IEEE 830 | https://standards.ieee.org/standard/830-1998.html | Requirements specification |
| DOORS | https://www.ibm.com/products/doors | Requirements management |
| Traceability Matrix | https://en.wikipedia.org/wiki/Traceability_matrix | Requirement tracking |

### Checkpoint & Recovery

| Resource | URL | Used For |
|----------|-----|----------|
| Temporal Sagas | https://docs.temporal.io/encyclopedia/sagas | Compensating transactions |
| Event Sourcing | https://martinfowler.com/eaaDev/EventSourcing.html | State reconstruction |
| CQRS | https://martinfowler.com/bliki/CQRS.html | Command query separation |

---

## Legacy Modernization

### Modernization Strategies

| Resource | URL | Used For |
|----------|-----|----------|
| Strangler Fig Pattern | https://martinfowler.com/bliki/StranglerFigApplication.html | Incremental migration |
| Modernization Patterns | https://www.oreilly.com/library/view/monolith-to-microservices/9781492047834/ | Migration approaches |
| AWS Modernization | https://aws.amazon.com/application-migration-service/ | Cloud migration |

### Code Analysis

| Resource | URL | Used For |
|----------|-----|----------|
| SonarQube | https://www.sonarsource.com/products/sonarqube/ | Code quality analysis |
| CodeScene | https://codescene.com/ | Code health analysis |
| Understand | https://scitools.com/ | Codebase visualization |
| Sourcegraph | https://sourcegraph.com/ | Code search and intelligence |

### Database Migration

| Resource | URL | Used For |
|----------|-----|----------|
| Flyway | https://flywaydb.org/ | Database migrations |
| Liquibase | https://www.liquibase.com/ | Database change management |
| pgLoader | https://pgloader.io/ | PostgreSQL data loading |
| AWS DMS | https://aws.amazon.com/dms/ | Database migration service |

### Parity Testing

| Resource | URL | Used For |
|----------|-----|----------|
| Contract Testing (Pact) | https://pact.io/ | API compatibility |
| Traffic Mirroring | https://istio.io/latest/docs/tasks/traffic-management/mirroring/ | Shadow traffic |
| Scientist | https://github.com/github/scientist | Experimentation framework |
| Diffy | https://github.com/twitter/diffy | Response comparison |

---

## Continuous Improvement & Experimentation

### DORA Metrics

| Resource | URL | Used For |
|----------|-----|----------|
| DORA Research | https://dora.dev/ | DevOps metrics research |
| DORA Metrics | https://dora.dev/guides/dora-metrics-four-keys/ | Four key metrics |
| Accelerate Book | https://itrevolution.com/product/accelerate/ | DevOps performance |
| SPACE Framework | https://queue.acm.org/detail.cfm?id=3454124 | Developer productivity |

### Feature Flags

| Resource | URL | Used For |
|----------|-----|----------|
| LaunchDarkly | https://launchdarkly.com/ | Feature flag platform |
| Unleash | https://www.getunleash.io/ | Open-source feature flags |
| Split | https://www.split.io/ | Feature delivery |
| OpenFeature | https://openfeature.dev/ | Feature flag standard |

### Canary Deployments

| Resource | URL | Used For |
|----------|-----|----------|
| Flagger | https://flagger.app/ | Progressive delivery |
| Argo Rollouts | https://argo-rollouts.readthedocs.io/ | Kubernetes rollouts |
| Spinnaker | https://spinnaker.io/ | Multi-cloud deployment |
| Istio Traffic Management | https://istio.io/latest/docs/concepts/traffic-management/ | Service mesh canaries |

### A/B Testing & Experimentation

| Resource | URL | Used For |
|----------|-----|----------|
| GrowthBook | https://www.growthbook.io/ | Open-source experimentation |
| Optimizely | https://www.optimizely.com/ | Digital experimentation |
| Statsig | https://statsig.com/ | Feature gates & experiments |
| Statistical Significance | https://en.wikipedia.org/wiki/Statistical_significance | Experiment analysis |

### Automated Rollback

| Resource | URL | Used For |
|----------|-----|----------|
| Kubernetes Rollback | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment | K8s rollback |
| ArgoCD Rollback | https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_rollback/ | GitOps rollback |
| Helm Rollback | https://helm.sh/docs/helm/helm_rollback/ | Chart rollback |

---

## Compliance Frameworks

### General

| Resource | URL | Used For |
|----------|-----|----------|
| SOC 2 | https://www.aicpa.org/soc | Service organization controls |
| ISO 27001 | https://www.iso.org/isoiec-27001-information-security.html | Information security |
| GDPR | https://gdpr.eu/ | Data protection |
| CCPA | https://oag.ca.gov/privacy/ccpa | California privacy |

### Industry-Specific

| Resource | URL | Used For |
|----------|-----|----------|
| PCI DSS | https://www.pcisecuritystandards.org/ | Payment card security |
| HIPAA | https://www.hhs.gov/hipaa/ | Healthcare data |
| FedRAMP | https://www.fedramp.gov/ | Federal cloud |

---

## Additional Resources

### Books

- *Site Reliability Engineering* - Google SRE Team
- *The DevOps Handbook* - Gene Kim et al.
- *Designing Data-Intensive Applications* - Martin Kleppmann
- *Building Secure and Reliable Systems* - Google

### Communities

| Community | URL |
|-----------|-----|
| CNCF | https://www.cncf.io/ |
| OpenSSF | https://openssf.org/ |
| DevSecOps Community | https://www.devsecops.org/ |

---

**Version**: 2.4.0 | **Date**: 2026-01-08
