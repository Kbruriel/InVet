# InVet Command: run-checks

Equivalent to OpenCode `/run-checks`.

Input: optional diagnostic mode, or `BE-00X`, `FE-00X`, or `QA-00X` for formal slice checks.

Use agent: `InVet Check Runner`.

Before acting, read:

- `.opencode/commands/run-checks.md`
- `.opencode/agents/invet-check-runner.md`
- `docs/opencode/templates/checks_results_template.md`
- `docs/opencode/references/run_checks_matrix.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`

Run applicable backend, frontend, and DevOps checks. Write formal check evidence when a slice ID is provided.

The formal `checks` preflight must block applicable open tasks and `CANCELLED` tasks without verifiable evidence.
