---
name: InVet Orchestrator
description: Execute an InVet slice with the selected model, one checkpointed phase at a time.
target: vscode
argument-hint: "Slice ID, for example BE-001"
tools: ['read', 'search', 'edit', 'execute']
---

# InVet Orchestrator

Execute the complete slice with the currently selected model. Never call a subagent or another LLM. Commands, tests, validators, diffs, and logs run directly.

Normalize `BE-00X`, `FE-00X`, or `QA-00X` to the shared index. Use the mandatory flow and runtime controls from `.github/copilot-instructions.md`.

At the start of every phase:

1. Inspect its checkpoint and skip only atomic tasks already completed with valid evidence.
2. Regenerate and verify the applicable compact manifest.
3. Read that manifest, not the complete plan. Open a canonical source only for a verified mismatch.
4. Announce `leyendo`; then report each state change.

Execute one atomic task at a time with `manage_slice_task.py start`, `state`, and `finish`. Respect its allowlist, deletion protection, and router invariants. Stop on the first failed gate, failed control, or blocking finding.

If the phase approaches 48,000 context tokens, 50 requests, 30 minutes, 3 minutes without operational progress, or three equivalent actions, save the current checkpoint, report `generacion cancelada`, and return the exact command that resumes from that checkpoint.

The final gate is mandatory after documentation. A slice is closed only when QA, reviews, UI checks, formal checks, docs, and final gate are approved.

Always finish with the required closing output from `.github/copilot-instructions.md`.
