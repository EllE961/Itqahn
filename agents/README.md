# Itqahn Agents (Subagent Library)

This folder defines the **role-based subagent system** for Itqahn.

Agents are not “personalities”. They are **operational roles** with:
- explicit responsibilities,
- constrained tool access,
- defined inputs/outputs,
- stop conditions and escalation rules,
- success metrics.

## How agents are used

- The orchestrator (Temporal workflows) invokes agents at defined phases.
- Each agent produces **artifacts** stored in Git and/or the Evidence Store.
- Policies (OPA/Kyverno) enforce what an agent is allowed to do.

## Start here

- `AGENT-CONTRACT.md` — the rules every agent must obey.
- `PERMISSIONS.md` — the tool/privilege matrix.
- `TRIGGERS.md` — when agents run automatically.
- `_template.md` — how to create new agents.

## Directory layout

Folders are numbered to reflect lifecycle order and governance importance (security/compliance are blocking).

See also: `docs/06-agents-and-governance.md`
