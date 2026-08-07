---
description: Ejecuta checks de UI automation y regresion para un slice InVet.
agent: invet-check-runner
---

Ejecuta los checks de UI automation del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `FE-00X` y deriva el mismo indice vertical.
2. Verifica que exista `docs/opencode/tasks/ui-automation/UIA-00X.md`.
3. Ejecuta desde `InVet_UI_Automation`:
   - `npm run test:e2e`
   - `npm run test:regression`
4. Resume evidencia, fallos, skips validos y bloqueos.
5. Si los checks UI fallan, no permitas avanzar a `/run-checks BE-00X`.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
