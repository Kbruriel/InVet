# Plantilla de registro de carryovers

Usa este archivo como base para `docs/opencode/carryovers/BE-00X-carryovers.md`.
El registro documenta tareas postergadas o transferidas entre slices y se valida con `backend/scripts/validate_slice_plan.py`.

## Reglas

- No uses archivos anonimos de pendientes.
- Cada fila debe referenciar plan origen, plan destino y evidencia.
- `status` usa `OPEN`, `TRANSFERRED`, `CLOSED` o `CANCELLED`.
- `closure_evidence` puede permanecer `pending` solo mientras el carryover siga abierto.
- Cuando el carryover cierre, reemplaza `pending` con evidencia reproducible y actualiza ambos planes.

| source_plan | source_task | destination_plan | destination_task | reason_postponed | status | owner | updated_at | closure_evidence | source_reference | destination_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BE-XXX-plan.md | BE-XXX-TNN | BE-YYY-plan.md | BE-YYY-TNN | Motivo verificable | OPEN | owner | 2026-08-15 | pending | docs/opencode/plans/BE-XXX-plan.md#L10 | docs/opencode/plans/BE-YYY-plan.md#L20 |
