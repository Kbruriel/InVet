---
description: Implementa automatizacion UI/E2E para un slice InVet.
agent: invet-ui-automation-implementer
---

Implementa la automatizacion UI del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `FE-00X` y deriva el mismo indice vertical.
2. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/user-stories/US-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/ui-automation/UIA-00X.md`
3. Valida que el plan del slice haya pasado `backend/scripts/validate_slice_plan.py --stage qa`; si el plan o `UIA-00X` estan stale o falta el artefacto, detente y devuelve el trabajo a `/plan-task BE-00X`.
4. Si faltan dependencias o el entorno no levanta, intenta recuperarlo antes de bloquearte: instala dependencias si hace falta y usa Docker cuando el slice dependa de PostgreSQL o del runtime del repo.
5. Si Docker aplica, confirma que todos los contenedores relevantes fueron actualizados o recreados y quedaron saludables; si no hay cambios relevantes, registra el skip con causa exacta.
6. Implementa los specs en `InVet_UI_Automation/tests/e2e/`.
7. Referencia `US-00X-NN` y `CA-NN` en titulos o anotaciones.
8. Ejecuta `npm run test:e2e` y `npm run test:regression` desde `InVet_UI_Automation` cuando el entorno este listo.
9. Actualiza `UIA-00X` con cobertura, evidencia, casos no automatizados y bloqueos.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
