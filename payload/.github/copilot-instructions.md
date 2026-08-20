# InVet Copilot Instructions

Use these compact rules whenever GitHub Copilot works in this repository.

## Runtime model

- The model selected by the user performs every phase. Do not call `runSubagent`, delegate to another agent, or invoke another LLM.
- Execute commands, tests, validators, status, diff, and log reads directly with the current model.
- Safe read-only checks, tests, lint, and validators may run without confirmation. Require confirmation for applied migrations, commits, pushes, destructive operations, or external side effects.
- Show state changes as `leyendo`, `editando`, `ejecutando pruebas`, `esperando permiso`, or `generacion cancelada`.
- Do not repeat identical text, tool calls, or actions. After one failed retry, inspect new evidence; cancel after three equivalent actions.
- A phase must not run longer than 30 minutes. Cancel after 3 minutes without operational progress or a tool call, preserve the checkpoint, and report the exact resume command.
- Keep one phase below approximately 48,000 context tokens. Near that size, finish the current atomic task, save its checkpoint, and resume in a clean conversation.
- VS Code limits each agent run to 50 requests. Do not consume the limit trying to complete multiple failed phases.

## Slice and context

A slice shares one numeric index across `US`, `BE`, `FE`, `QA`, `UIA`, and `APIA`. Normalize accepted aliases to that index. The canonical plan is `docs/opencode/plans/BE-00X-plan.md`.

`/plan-task` owns the semantic plan, user story, UI automation sidecar, API automation sidecar, and all five derived manifests. Other phases must not redefine scope.

For implementation, use only the matching verified manifest:

- Backend: `docs/opencode/manifests/BE-00X-backend.md`
- Frontend: `docs/opencode/manifests/BE-00X-frontend.md`
- UI automation: `docs/opencode/manifests/BE-00X-ui-automation.md`
- API automation: `docs/opencode/manifests/BE-00X-api-automation.md`
- QA: `docs/opencode/manifests/BE-00X-qa.md`, plus the other four only for cross-layer handoffs

Reviews, checks, docs, and final gate use the five manifests as a compact index, then read only relevant evidence reports, diff, and test output. Open the full plan or sidecar only when manifest verification fails or a concrete contradiction requires the canonical source.

Before a phase, regenerate and verify its manifest. Before QA and closing gates, verify all five with `backend/scripts/manage_slice_task.py`.

## Task controls

- Execute one atomic task at a time with `manage_slice_task.py start`, visible `state` transitions, and `finish --result pass|failed|blocked`. Only `pass` completes its checkpoint.
- The manifest allowlist is derived from `Entregables`. Do not modify files outside it.
- Do not delete existing files or lines without explicit justification recorded by `finish --allow-deletions`.
- Adding a router must preserve every previous `include_router(...)` registration.
- Save a checkpoint after every task. Resume from it; never repeat a completed portion of a slice.
- A manifest limits context but never replaces the canonical plan, sidecars, QA decisions, review reports, diff, or real test results.

## Mandatory flow

1. Plan the slice and generate/verify all manifests.
2. Implement backend; its command performs any applicable persistence validation before returning completion.
3. Implement frontend.
4. Implement UI automation.
5. Implement API automation.
6. Run QA.
7. Run functional review.
8. Run clean architecture review.
9. Run security review.
10. Run UI checks.
11. Run formal checks.
12. Update docs.
13. Run final gate.

Stop at the first `REJECTED` or `BLOCKED` gate. Findings in `OPEN`, `IN_PROGRESS`, or `READY_FOR_REVALIDATION` block forward progress. Implementers move corrected findings only to `READY_FOR_REVALIDATION`; QA or the owning review gate may mark them `RESOLVED` after fresh evidence.

Never skip a gate merely because an artifact exists. Carryovers must be synchronized between source plan, destination plan, and registry. Closure gates reject applicable open tasks and `CANCELLED` tasks without evidence.

## Scope and quality

- Preserve UTF-8.
- Keep backend, frontend, QA, UI automation, and API automation responsibilities separate.
- Product unit tests belong to the implementing layer, not QA.
- UI and API automation remain inside `InVet_UI_Automation/`.
- UI and API automation must run against the Docker Compose `db`, `backend`, and `frontend` services. Docker unavailable is `BLOCKED`; do not replace the stack with host processes.
- Prefer existing architecture, naming, and test patterns.
- QA and reviews document defects; they do not modify product code.

## Required closing output

```text
Estado de ejecucion: <APPROVED|REJECTED|BLOCKED|READY_FOR_REVALIDATION|COMPLETED>
Siguiente paso recomendado: <exact prompt or command>
Motivo: <why this is the next gate>
```

When findings or blockers exist, also provide the exact command that resolves or unblocks the gate.
