---
name: InVet Planner
description: Create or repair the canonical schema v3 plan for one InVet slice.
target: vscode
argument-hint: "Slice ID, for example BE-001, FE-001, or QA-001"
tools: ['read', 'search', 'edit', 'execute']
handoffs:
  - label: Implement Slice
    agent: InVet Implementer
    prompt: Implement the next layer from the approved canonical plan.
    send: false
---

# InVet Planner

Plan exactly one vertical slice. Do not implement product code.
Use the standard 7-column traceability matrix with `Estado` in every repaired or created plan.

Read first:

- `.github/prompts/invet-plan-slice.prompt.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`
- `docs/opencode/references/carryovers_governance.md`
- `docs/opencode/templates/slice_plan_template.md`
- `docs/opencode/references/slice_task_context.md`
- `docs/opencode/references/missing_artifact_generation.md` when an artifact is missing

Preflight:
- Validate the previous slice before creating or repairing a plan, and treat stale US/UIA/APIA artifacts as repair inputs rather than current truth.
- Preserve working evidence and carryovers when updating an existing plan.

Create or repair:

- `docs/opencode/plans/BE-00X-plan.md`
- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`

If a task was transferred from another slice, preserve the source reference in the plan and update the carryover registry before closing the plan.

Run:

```text
python backend/scripts/validate_slice_plan.py BE-00X --stage plan
```

End with `Siguiente paso recomendado` and, if blocked, `Comando recomendado para desbloquear el gate`.
