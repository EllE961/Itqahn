# INITIAL: Feature Request Template

Use this template to capture feature requests before PRP generation.

---

```markdown
# INITIAL: {Feature Name}

**ID**: initial-{ulid}
**Created**: {YYYY-MM-DDTHH:MM:SSZ}
**Requester**: {user or system}
**Status**: draft | submitted | prp-generated

---

## FEATURE

**One-liner**: {What this feature does in one sentence}

**Description**:
{2-3 sentences describing what the user wants to accomplish.
Focus on the outcome, not the implementation.}

**User Story**:
As a {role},
I want to {action},
So that {benefit}.

---

## EXAMPLES

Concrete examples of expected behavior. At least 2 examples required.

### Example 1: {Happy Path}

**Given**: {Starting state}
**When**: {User action}
**Then**: {Expected outcome}

```json
// Input
{
  "field1": "value1",
  "field2": "value2"
}

// Expected Output
{
  "result": "success",
  "data": {...}
}
```

### Example 2: {Edge Case or Error}

**Given**: {Starting state}
**When**: {User action that should fail or edge case}
**Then**: {Expected behavior}

```json
// Input
{
  "field1": "invalid"
}

// Expected Output
{
  "result": "error",
  "message": "Validation failed: field1 must be..."
}
```

### Example 3: {Optional Additional Example}

{Add more examples as needed}

---

## DOCUMENTATION

What documentation needs updating after implementation?

- [ ] User guide: {section}
- [ ] API documentation: {endpoint}
- [ ] README: {section}
- [ ] Other: {specify}

---

## CONSTRAINTS

### Performance
- Response time: {e.g., < 200ms}
- Throughput: {e.g., 100 requests/second}
- Memory: {e.g., < 50MB per request}

### Security
- Authentication: {required/not required}
- Authorization: {role or permission needed}
- Data sensitivity: {PII/credentials/none}

### Compatibility
- Browsers: {e.g., Safari 15+, Chrome 90+}
- Platforms: {e.g., iOS 14+, Android 10+}
- Dependencies: {existing features this builds on}

### Other Constraints
- {Any other technical or business constraints}

---

## ACCEPTANCE

How do we know this is done? Binary criteria only.

- [ ] {Criterion 1: Specific, testable, yes/no}
- [ ] {Criterion 2: Specific, testable, yes/no}
- [ ] {Criterion 3: Specific, testable, yes/no}
- [ ] All validation gates pass
- [ ] Documentation updated
- [ ] Evidence Pack generated

---

## GOTCHAS

Known edge cases, risks, or things to watch out for.

### Known Edge Cases
- {Edge case 1}: {How to handle}
- {Edge case 2}: {How to handle}

### Risks
- {Risk 1}: {Likelihood (H/M/L), mitigation}
- {Risk 2}: {Likelihood (H/M/L), mitigation}

### Dependencies
- {External system or team dependency}
- {Other feature dependency}

### Anti-Patterns to Avoid
- Do NOT: {Thing to avoid}
- Do NOT: {Thing to avoid}

---

## REFERENCE

Links to related materials (optional).

- Figma: {link if applicable}
- Related issues: {#issue numbers}
- Concept Lock: {version reference}
- Prior art: {links to similar features}

---

## INTERNAL (System Use)

```yaml
# Filled by system, not user
processing:
  submitted_at: null
  prp_generated_at: null
  prp_id: null
  run_id: null
  validation_status: pending
```
```

---

## Usage Notes

1. **Keep it short**: INITIAL should be 1-2 pages max
2. **Be specific**: Vague requests lead to vague PRPs
3. **Include examples**: Concrete examples prevent misunderstanding
4. **State constraints clearly**: Constraints bound the solution space
5. **Binary acceptance**: "Works well" is not testable; "Returns 200 in < 200ms" is

---

## Workflow

```
User fills INITIAL
       │
       ▼
Submit via Dashboard
       │
       ▼
Dashboard validates format
       │
       ├── Invalid → Return with errors
       │
       └── Valid → Queue for PRP generation
              │
              ▼
         /generate-prp
              │
              ▼
         PRP draft for review
```

---

**Template Version**: 1.0.0
