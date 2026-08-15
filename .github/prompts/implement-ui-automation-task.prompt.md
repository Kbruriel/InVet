# InVet Command: implement-ui-automation-task

Equivalent to OpenCode `/implement-ui-automation-task`.

Input: `FE-00X`.

Use agent: `InVet UI Automation Implementer`.

Before acting, read:

- `.opencode/commands/implement-ui-automation-task.md`
- `.opencode/agents/invet-ui-automation-implementer.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`

Preflight:
- Validate the slice plan through `backend/scripts/validate_slice_plan.py --stage qa` before closing the task.
- Recover missing dependencies first, and use Docker when the slice depends on PostgreSQL or the repo runtime.
- Treat stale evidence as invalid and confirm Docker containers were updated or recreated when Docker applies.

Implement only UI/E2E automation under `InVet_UI_Automation/`.
