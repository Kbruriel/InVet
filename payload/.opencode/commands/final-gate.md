---
description: Ejecuta el gate final de release con el modelo seleccionado.
agent: invet-final-reviewer
subtask: false
---

Ejecuta el gate final del slice indicado por `$ARGUMENTS`.

Instrucciones:
0. Requiere `BE-00X`, `FE-00X` o `QA-00X` y normaliza el mismo indice vertical.
1. Ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage docs`.
   - Si falla, reporta `BLOCKED` y no declares cierre final.
1.1. Regenera y verifica los cinco manifiestos; si alguno falta o esta stale, devuelve el flujo a `/plan-task BE-00X`.
2. Revisa:
   - `docs/opencode/qa/QA-00X-results.md`
   - `docs/opencode/qa/QA-00X-findings.md`
   - `docs/opencode/reviews/BE-00X-review.md`
   - `docs/opencode/reviews/BE-00X-clean-architecture-review.md`
   - `docs/opencode/reviews/BE-00X-security-review.md`
   - `docs/opencode/checks/BE-00X-checks.md`
   - `docs/opencode` actualizado para el slice
   - `git diff` y logs relevantes
3. Si faltan comandos, logs o evidencias mecanicas, ejecutalos directamente en este agente sin iniciar subagentes.
4. Crea siempre `docs/opencode/reviews/BE-00X-final-review.md` usando `docs/opencode/templates/review_findings_template.md` como base.
5. Usa `APPROVED` solo si `QA-00X-results.md` esta `APPROVED`, `QA-00X-findings.md` no existe o esta en estado resuelto, las tres revisiones, checks y docs estan cerrados y no hay findings abiertos.
6. Usa `REJECTED` o `BLOCKED` si hay gaps, inconsistencias o verificaciones imposibles.
7. No modifiques codigo de producto.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
