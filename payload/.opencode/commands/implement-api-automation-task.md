---
description: Implementa automatizacion API para un slice InVet.
agent: invet-api-automation-implementer
---

Implementa la automatizacion API del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X` y deriva el mismo indice vertical.
2. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/user-stories/US-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/api-automation/APIA-00X.md`
3. Si falta `APIA-00X`, detente y devuelve el trabajo a `/plan-task BE-00X`.
4. Implementa los specs en `InVet_UI_Automation/tests/api/`.
5. Referencia `US-00X-NN` y `CA-NN` en titulos o anotaciones.
6. Ejecuta `npm run test:api` desde `InVet_UI_Automation` cuando el entorno este listo.
7. Actualiza `APIA-00X` con cobertura, evidencia, casos no automatizados y bloqueos.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
