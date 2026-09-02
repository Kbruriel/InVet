---
description: Ejecuta el flujo completo y sus gates para un slice InVet.
agent: invet-orchestrator
subtask: false
---

Ejecuta el slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X`, `FE-00X` o `QA-00X` y normaliza explicitamente el mismo indice vertical. La cadena orquestada usa `BE-00X` como entrada uniforme, excepto `/qa-task QA-00X`.
2. Ejecuta el flujo obligatorio completo definido por `invet-orchestrator`, incluido `/final-gate`.
2.1. Permanece como `invet-orchestrator` durante todo el flujo y aplica directamente el contrato especializado de cada etapa. No cambies de perfil ni invoques los agentes asociados a los comandos manuales.
3. `/plan-task` crea el plan, los sidecars y los cinco manifiestos; es el unico propietario del alcance semantico.
3.1. Antes de cada etapa de implementacion, regenera solo la vista derivada de la capa con `manifest` y ejecuta `verify` para esa capa. Si falla, vuelve a `/plan-task BE-00X`.
3.2. Antes de QA y de los gates de cierre, ejecuta `python backend/scripts/manage_slice_task.py manifest BE-00X --layer all` y `python backend/scripts/manage_slice_task.py verify BE-00X --layer all`.
3.3. Antes de cada etapa, ejecuta el stage correspondiente de `backend/scripts/validate_slice_plan.py`.
3.4. No lances subagentes para comandos, pruebas o logs: el agente activo los ejecuta directamente con el modelo seleccionado.
3.5. Exige estados visibles y checkpoint por tarea. Cancela llamadas de 30 minutos, inactividad operativa prolongada o tres acciones identicas.
4. Exige que `/implement-backend-task` entregue su validacion interna de persistencia aprobada cuando aplique; si falla, vuelve a backend o findings sin exponer el script interno como fase del usuario.
5. Ejecuta `/implement-ui-automation-task BE-00X` y `/implement-api-automation-task BE-00X` antes de QA.
   - Ambas fases deben aportar evidencia contra `db`, `backend` y `frontend` de Docker Compose. Si Docker no esta disponible, detente en `BLOCKED` y recomienda reanudar el mismo comando de automatizacion; no avances con evidencia host.
6. Ejecuta `/run-ui-checks BE-00X` antes de `/run-checks BE-00X`.
7. Detente ante cualquier gate fallido y reporta el comando exacto para reanudar.
8. Si `/implement-findings` aplica correcciones, repite QA, UI checks y los reviews afectados.
9. No declares el slice cerrado hasta que QA, UI checks, reviews y checks esten aprobados, la documentacion se actualice y `/final-gate BE-00X` quede aprobado.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
