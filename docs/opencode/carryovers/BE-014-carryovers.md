# Carryovers BE-014

Registros de tareas postergadas o transferidas del slice BE-014 (Soporte básico, tickets + categorías), según `docs/opencode/references/carryovers_governance.md`.

- `status` usa `OPEN` / `TRANSFERRED` / `CLOSED` / `CANCELLED`.
- `closure_evidence` permanece `pending` solo mientras el carryover siga `OPEN` o `TRANSFERRED`; al cerrar, reemplazar por evidencia reproducible y sincronizar ambos planes.
- El validador `backend/scripts/validate_slice_plan.py` bloquea `qa`, `review`, `checks` y `docs` mientras exista un carryover `OPEN` o `TRANSFERRED` para el slice.

## Registros

| source_plan | source_task | destination_plan | destination_task | reason_postponed | status | owner | updated_at | closure_evidence | source_reference | destination_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| docs/opencode/plans/BE-014-plan.md | BE-014-T03 | docs/opencode/plans/BE-014-plan.md | BE-014-T03 | El manifiesto inicial de T03 sólo permitía pruebas y no incluía las capas de aplicación y datos necesarias para implementar la deduplicación. Se corrigieron los entregables canónicos sin crear IDs no válidos como T03a/T03b. | CLOSED | invet-backend-implementer | 2026-09-01 | `python -m pytest app/tests/usecases/test_support_ticket_rules.py app/tests/data/test_support_ticket_repo.py -q`: 37 passed; checkpoint BE-014-T03 en estado completed. | docs/opencode/plans/BE-014-plan.md (BE-014-T03) | docs/opencode/checkpoints/BE-014-backend.json (BE-014-T03) |

## Bloqueantes latentes resueltos

- `backend/app/infrastructure/database/models/__init__.py` registra los modelos de soporte; `Base.metadata.create_all` crea ambas tablas sin importar el submódulo explícitamente.
- `backend/alembic/versions/a014_support.py` ya no silencia excepciones del seed, por lo que un fallo de datos mínimos bloquea visiblemente la migración.
- Se eliminó el duplicado huérfano bajo `backend/app/infraestructure/...`.

Evidencia: `python -m pytest tests/api/test_support_ticket_migration.py app/tests/api/test_support_ticket_api.py -q` aprobó 17 pruebas durante BE-014-T01.
