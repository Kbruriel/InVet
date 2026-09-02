---
description: Revisa Clean Architecture de un slice identificado y escribe evidencia.
agent: invet-clean-architecture-reviewer
subtask: false
---

Revisa la arquitectura del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X` o `FE-00X`; si falta el ID, pregunta antes de continuar.
2. Normaliza al mismo indice vertical y ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage review`.
3. En Windows PowerShell 5.1 configura `workdir` directamente en `C:\InVet` y no uses `&&`; ejecuta cada comando por separado o usa `$LASTEXITCODE` para fail-fast.
4. Regenera y verifica los cinco manifiestos; revisa sus allowlists junto con plan, diff y archivos del slice.
5. Valida modelo SQL, registro en `models/__init__.py`, migracion Alembic (upgrade/downgrade/seed) y pruebas dirigidas.
6. Compara el diff final contra la matriz AC del plan canonico (`AC-014` para `FE-014`).
7. Valida capas backend y modularidad frontend.
8. Crea siempre `docs/opencode/reviews/BE-00X-clean-architecture-review.md`.
9. Emite `APPROVED` o `REJECTED` con evidencia.
10. No modifiques codigo fuente.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
