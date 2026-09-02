---
description: Implementa automatizacion API para un slice InVet.
agent: invet-api-automation-implementer
subtask: false
---

Implementa la automatizacion API del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X`, `FE-00X` o `QA-00X`; deriva el mismo indice vertical y ejecuta la responsabilidad API automation.
2. Ejecuta `python backend/scripts/manage_slice_task.py manifest BE-00X --layer api-automation` y `python backend/scripts/manage_slice_task.py verify BE-00X --layer api-automation`; lee `docs/opencode/manifests/BE-00X-api-automation.md` y bloquea si el sidecar APIA falta o esta stale.
2.1. Ejecuta comandos, pruebas y logs directamente sin subagentes; muestra estados operativos, respeta la allowlist y cancela a los 30 minutos o tras tres acciones repetidas.
2.2. Inicia la fase con `python backend/scripts/manage_slice_task.py start BE-00X --task APIA-00X`, publica estados con `state` y termina con `finish --task APIA-00X --result pass|failed|blocked --evidence "comando y resultado"`. Solo `pass` guarda la fase como completada.
3. Valida que el plan del slice haya pasado `backend/scripts/validate_slice_plan.py --stage qa`; si el plan o `APIA-00X` estan stale o falta el artefacto, detente y devuelve el trabajo a `/plan-task BE-00X`.
4. Prepara obligatoriamente el sistema bajo prueba con Docker Compose: levanta/reconstruye `db`, `backend` y `frontend`, y confirma en especial que `db` y `backend` estan disponibles. Si Docker no esta disponible, usa `BLOCKED`; no uses un backend host como sustituto.
5. Ejecuta Playwright API contra `http://localhost:8000`, que debe ser el puerto publicado por el contenedor backend, y registra estado y logs del stack como evidencia.
6. Implementa los specs en `InVet_UI_Automation/tests/api/`.
7. Referencia `US-00X-NN` y `CA-NN` en titulos o anotaciones.
8. Cambia el estado a `testing` y ejecuta `npm run test:api` desde `InVet_UI_Automation` exclusivamente contra el stack Docker saludable.
9. Actualiza `APIA-00X` con cobertura, evidencia, casos no automatizados y bloqueos.
Cierre obligatorio:
- Si completa con evidencia Docker y Playwright en PASS, usa `Estado de ejecucion: COMPLETED` y recomienda `/qa-task QA-00X`.
- Si falla un spec o la implementacion, usa `REJECTED` y recomienda `/implement-api-automation-task BE-00X` o `/implement-findings BE-00X` cuando exista un finding formal.
- Si Docker o una dependencia impide correr, usa `BLOCKED`, conserva checkpoint y recomienda reanudar `/implement-api-automation-task BE-00X` despues de restaurar el entorno.
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
