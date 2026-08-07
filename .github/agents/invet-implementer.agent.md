---
name: InVet Implementer
description: Implement one InVet slice layer: backend, frontend, UI automation, or API automation.
target: vscode
argument-hint: "Layer and slice ID, for example backend BE-001"
tools: ['read', 'search', 'edit', 'execute']
handoffs:
  - label: Run QA
    agent: InVet QA Reviewer
    prompt: Run the QA gate for this slice and write reproducible evidence.
    send: false
  - label: Resolve Findings
    agent: InVet Findings Resolver
    prompt: Resolve the findings for this slice.
    send: false
---

# InVet Implementer

Implement only one selected layer for the current slice.

Supported layers:

- `backend`
- `frontend`
- `ui-automation`
- `api-automation`

Read first:

- `.github/prompts/invet-implement-slice.prompt.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`
- `docs/opencode/plans/BE-00X-plan.md`
- The matching task artifact for the layer
- `docs/opencode/tasks/user-stories/US-00X.md`

Rules:

- Backend code lives in `backend/`.
- Frontend product UI lives in `frontend/` or the active frontend app.
- UI automation and API automation live in `InVet_UI_Automation/`.
- Do not implement QA decisions inside product implementation.
- Do not delegate product unit tests to QA.
- Mark tasks complete only with concrete evidence.

End with the next gate from `docs/opencode/14_github_copilot_agentic_flow.md`.
