---
description: Implementa automatizacion UI/E2E para un slice InVet.
agent: invet-ui-automation-implementer
---

Implementa la automatizacion UI del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X`, `FE-00X` o `QA-00X`; deriva el mismo indice vertical y ejecuta la responsabilidad UI automation.
2. Ejecuta `python backend/scripts/manage_slice_task.py manifest BE-00X --layer ui-automation` y `python backend/scripts/manage_slice_task.py verify BE-00X --layer ui-automation`; lee `docs/opencode/manifests/BE-00X-ui-automation.md` y bloquea si el sidecar UIA falta o esta stale.
2.1. Ejecuta comandos, pruebas y logs directamente sin subagentes; muestra estados operativos, respeta la allowlist y cancela a los 30 minutos o tras tres acciones repetidas.
2.2. Inicia la fase con `python backend/scripts/manage_slice_task.py start BE-00X --task UIA-00X`, publica estados con `state` y termina con `finish --task UIA-00X --evidence "comando y resultado"` para guardar checkpoint.
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
