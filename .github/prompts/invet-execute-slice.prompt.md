# InVet: Execute Slice

Use this prompt when asking GitHub Copilot to run the full agentic flow for one slice.

## Input

Slice ID: `BE-00X`, `FE-00X`, or `QA-00X`.

## Task

Execute the slice gate by gate. Stop at the first failed gate. Do not skip ahead.

## Flow

1. Plan slice.
2. Implement backend.
3. Run `python backend/scripts/validate_slice_plan.py BE-00X --stage secure-persistence`.
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
14. Run final gate only when requested.

## Required Behavior

- Before each gate, read the canonical plan and relevant artifacts.
- If the stage validator exists for the gate, run it.
- If a gate fails, create or update the expected evidence artifact.
- If findings exist, stop and recommend the findings workflow.
- Do not declare the slice closed until all required gates are approved.

## Output

Report:

- Current gate.
- Decision: `APPROVED`, `REJECTED`, or `BLOCKED`.
- Evidence files created or updated.
- Commands executed.
- Findings and blockers.

Always end with:

```text
Siguiente paso recomendado: <next Copilot prompt or exact command>
Motivo: <why this is the next gate>
```

If findings exist:

```text
Comando recomendado para resolver hallazgos: Resolve Findings for BE-00X
Motivo: Los findings bloquean el siguiente gate.
```
