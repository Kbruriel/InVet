# InVet Copilot Instructions

Use these instructions whenever GitHub Copilot works in this repository.

## Operating Model

InVet is developed by vertical slices. A slice uses the same numeric index across:

- `US-00X`
- `BE-00X`
- `FE-00X`
- `QA-00X`
- `UIA-00X`
- `APIA-00X`

There is one canonical plan per slice: `docs/opencode/plans/BE-00X-plan.md`.

OpenCode slash commands are not available inside GitHub Copilot. When a document says `/plan-task`, `/qa-task`, `/run-checks`, or another slash command, translate it into the equivalent Copilot workflow described in `docs/opencode/14_github_copilot_agentic_flow.md`.

VS Code custom agents for this repository live in `.github/agents/*.agent.md`. Prompt files live in `.github/prompts/*.prompt.md`.

## Required Context

Before editing code for a slice, read the relevant files:

- `docs/opencode/14_github_copilot_agentic_flow.md`
- `docs/opencode/13_agents_architecture_and_gate_flow.md`
- `docs/opencode/plans/BE-00X-plan.md`
- `docs/opencode/tasks/backend/BE-00X.md`
- `docs/opencode/tasks/frontend/FE-00X.md`
- `docs/opencode/tasks/qa/QA-00X.md`
- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`

If a required artifact is missing, do not invent its contents. Create or repair the canonical artifact first, using `docs/opencode/templates/slice_plan_template.md` and the rules in `docs/opencode/references/missing_artifact_generation.md` when applicable.

## Gates

Do not skip gates because a file exists. Use decisions and states inside the artifacts.

The normal flow is:

1. Plan the slice.
2. Implement backend.
3. Validate secure persistence with `python backend/scripts/validate_slice_plan.py BE-00X --stage secure-persistence`.
4. Implement frontend.
5. Implement UI automation.
6. Implement API automation.
7. Run QA.
8. Run functional review.
9. Run clean architecture review.
10. Run security review.
11. Run UI checks.
12. Run formal checks.
13. Update docs.
14. Run final gate when a second release opinion is requested.

When a gate fails, stop the forward flow, document the failure, recommend the next exact step, and fix through the findings workflow.

## Findings Workflow

Findings are blocking when they are `OPEN`, `IN_PROGRESS`, or `READY_FOR_REVALIDATION`.

State context:

- `OPEN`: the issue is still reproducible and no fix has been accepted yet.
- `IN_PROGRESS`: the issue is being worked but not ready for revalidation.
- `READY_FOR_REVALIDATION`: the fix is applied and QA must rerun before anything can close.
- `RESOLVED`: QA confirmed the fix with fresh evidence.
- `ACCEPTED_RISK`: QA or a reviewer accepted the risk with explicit justification.

Use these rules:

- QA can create findings and mark corrected findings as `RESOLVED`.
- QA findings files must include `- Estado global: OPEN|IN_PROGRESS|READY_FOR_REVALIDATION|RESOLVED|ACCEPTED_RISK`.
- Implementers can fix findings and move QA findings to `READY_FOR_REVALIDATION`.
- Do not mark a finding `RESOLVED` while implementing the fix.
- After findings are fixed, rerun QA first, then rerun any affected reviews, UI checks, and checks.

## QA And Review Continuity

- After QA, recommend functional review only when `QA-00X-results.md` says `Decision: APPROVED` and `QA-00X-findings.md` is absent or has global state `RESOLVED`/`ACCEPTED_RISK`.
- If QA is `REJECTED` or findings are `OPEN`/`IN_PROGRESS`, recommend the findings workflow for `BE-00X`.
- If findings are `READY_FOR_REVALIDATION`, treat that as a findings state and route through the findings workflow; the resolver hands revalidation back to QA when the corrections are ready.
- Do not treat `READY_FOR_REVALIDATION` as a completed gate, even if an older results file says `APPROVED`.
- After functional review runs and is `APPROVED`, recommend clean architecture review for `BE-00X`; do not send the flow back to QA.
- Recommend QA from functional review only when the review preflight could not start because QA is not approved or needs revalidation.

## Required Closing Output

Every Copilot task must end with:

```text
Estado de ejecucion: <APPROVED|REJECTED|BLOCKED|READY_FOR_REVALIDATION|COMPLETED>
Siguiente paso recomendado: <exact command or prompt name>
Motivo: <why this is the next gate>
```

If there are findings:

```text
Comando recomendado para resolver hallazgos: <exact command or prompt name>
Motivo: <why findings block the next gate>
```

If there is a blocker:

```text
Comando recomendado para desbloquear el gate: <exact command or prompt name>
Motivo: <what evidence or artifact is missing>
```

## Implementation Rules

- Preserve UTF-8 in all Markdown and source files.
- Keep tasks small and tied to one layer: backend, frontend, QA, UI automation, or API automation.
- Do not combine product implementation with QA gate decisions.
- Do not let QA implement missing unit tests for product code.
- Prefer existing architecture, naming, and test patterns.
- Keep product code changes scoped to the current slice.
- Keep UI automation and API automation inside `InVet_UI_Automation/`.
- Use `backend/scripts/validate_slice_plan.py` for deterministic gate checks whenever a stage is available.
