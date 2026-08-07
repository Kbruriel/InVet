---
description: Ejecuta el flujo completo y sus gates para un slice InVet.
agent: invet-orchestrator
---

Ejecuta el slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X`, `FE-00X` o `QA-00X` y normaliza explicitamente el mismo indice vertical.
2. Ejecuta el flujo obligatorio definido por `invet-orchestrator`.
3. Antes de cada etapa, ejecuta el stage correspondiente de `backend/scripts/validate_slice_plan.py`.
4. Despues de `/implement-backend-task`, ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage secure-persistence`; si falla, vuelve a backend o findings.
5. Ejecuta `/implement-ui-automation-task FE-00X` y `/implement-api-automation-task BE-00X` antes de QA.
6. Ejecuta `/run-ui-checks FE-00X` antes de `/run-checks BE-00X`.
7. Detente ante cualquier gate fallido y reporta el comando exacto para reanudar.
8. Si `/implement-findings` aplica correcciones, repite QA, UI checks y los reviews afectados.
9. No declares el slice cerrado hasta que QA, UI checks, reviews y checks esten aprobados y la documentacion se actualice.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
