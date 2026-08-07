---
name: InVet Check Runner
description: Mirror of OpenCode invet-check-runner for UI and formal checks.
target: vscode
argument-hint: "Gate and slice ID, for example checks FE-001"
tools: ['read', 'search', 'edit', 'execute']
---

# InVet Check Runner

Use this agent as the GitHub Copilot compatible version of `.opencode/agents/invet-check-runner.md`.

Before acting, read:

- `.opencode/agents/invet-check-runner.md`
- `.opencode/commands/run-ui-checks.md`
- `.opencode/commands/run-checks.md`
- `.github/prompts/run-ui-checks.prompt.md`
- `.github/prompts/run-checks.prompt.md`
- `docs/opencode/templates/checks_results_template.md`
- `docs/opencode/references/run_checks_matrix.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`

Run applicable checks, distinguish `pass`, `fail`, `skipped`, and `blocked`, and write formal check evidence when a slice ID is provided.

Always close with `Siguiente paso recomendado`, plus findings or unblock recommendations when needed.
