---
name: example-agent
department: example
risk_level: medium
tools:
  - repo_read
  - repo_write_branch
  - issue_tracker
outputs:
  - decision
  - spec
  - change
  - evidence
---

# Example Agent

## Purpose
Explain what this agent does in one sentence.

## When to use
- scenario 1
- scenario 2

## Inputs (required)
- links or artifacts this agent must read

## Outputs (required)
- concrete artifacts created (files, PRs, evidence entries)

## Constraints
- explicit do/don't rules, escalation conditions

## Success metrics
- what “good” looks like for this agent

## System prompt
Write a detailed role instruction here.
