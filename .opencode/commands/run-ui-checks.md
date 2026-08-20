---
description: Ejecuta checks de UI automation y regresion para un slice InVet.
agent: invet-check-runner
---

Ejecuta los checks de UI automation del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X`, `FE-00X` o `QA-00X`; deriva el mismo indice vertical.
1.1. Regenera y verifica el manifiesto `ui-automation`; úsalo para seleccionar specs y rutas del slice.
2. Verifica que exista `docs/opencode/tasks/ui-automation/UIA-00X.md`.
   - Levanta/reconstruye obligatoriamente `db`, `backend` y `frontend` con Docker Compose y confirma que los servicios estan disponibles.
   - La UI debe correr sobre `http://localhost:3000` publicado por el contenedor `frontend`; usa `PLAYWRIGHT_START_FRONTEND=false` y no aceptes un frontend host como evidencia.
   - Para el slice 008, las rutas de referencia son `/clinicas`, `/portal/owner/appointments`, `/portal/owner/appointments/new` y `/clinic/appointments`.
3. Ejecuta desde `InVet_UI_Automation`:
   - `npm run test:e2e`
   - `npm run test:regression`
4. Resume estado/logs Docker, comandos Playwright, evidencia, fallos, skips validos y bloqueos. Docker ausente o un servicio no disponible produce `BLOCKED`, nunca `skipped` ni fallback host.
5. Si los checks UI fallan, no permitas avanzar a `/run-checks BE-00X`.
Cierre obligatorio:
- `APPROVED` recomienda `/run-checks BE-00X`.
- `REJECTED` recomienda `/implement-ui-automation-task BE-00X` o `/implement-frontend-task BE-00X` segun el propietario del fallo.
- `BLOCKED` conserva evidencia y recomienda reanudar `/run-ui-checks BE-00X` cuando Docker vuelva a estar disponible.
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
