# Responsible Model Use Policy (Internal)

**Effective date:** 2026-01-06

This policy governs how Itqahn uses LLMs and other AI models.

## 1. Risk-based routing
- Security/compliance-critical tasks must use approved high-assurance models.
- Low-risk tasks may use cheaper models only if gates verify output.

## 2. No autonomous unsafe actions
Models must not:
- deploy directly to production,
- access secrets directly,
- perform destructive data operations without human approval.

## 3. Data handling
- Do not include secrets in prompts.
- Prefer hashes or encrypted references for sensitive inputs.
- Avoid storing raw prompts unless configured and approved.

## 4. Logging
Model usage logs must include:
- workflow ID
- agent role
- model identifier
- token usage
- policy verdict reference

## 5. Evaluation
All model changes must pass the evaluator harness.
See `agents/99-meta/evaluator-harness.md` and `tools/eval/` (if implemented).
