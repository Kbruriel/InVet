---
name: InVet Backend Implementer
description: Mirror of OpenCode invet-backend-implementer for backend slice implementation.
target: vscode
argument-hint: "Backend slice ID, for example BE-001"
tools: ['read', 'search', 'edit', 'execute']
---

# InVet Backend Implementer

Use this agent as the GitHub Copilot compatible version of `.opencode/agents/invet-backend-implementer.md`.

Before acting, read:

- `.opencode/agents/invet-backend-implementer.md`
- `.opencode/commands/implement-backend-task.md`
- `.github/prompts/implement-backend-task.prompt.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`
- `docs/opencode/references/carryovers_governance.md`

Implement only backend tasks for the current slice. Keep Clean Architecture boundaries, add required backend unit tests, and validate secure persistence when applicable.

If the task was inherited from another slice, update the source plan and the current plan with the same evidence before marking it complete.

Always close with `Siguiente paso recomendado`, plus findings or unblock recommendations when needed.
