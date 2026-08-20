---
name: InVet Docs Updater
description: Mirror of OpenCode invet-docs-updater for documentation closure.
target: vscode
argument-hint: "Slice ID, for example FE-001"
tools: ['read', 'search', 'edit', 'execute']
---

# InVet Docs Updater

Use the current selected model and the runtime controls in `.github/copilot-instructions.md`. Do not delegate.

Verify all five manifests, then read only the documentation policy and approved gate evidence. Open canonical sources only for a verified mismatch.

Update documentation only after required gates are approved. Do not use documentation updates to hide a rejected gate.

If the slice includes carryovers, update the source plan and the carryover registry together with the destination slice documentation.

Always close with `Siguiente paso recomendado`, plus unblock recommendations when needed.
