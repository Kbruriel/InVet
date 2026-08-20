---
description: Revisa seguridad de un slice identificado y escribe evidencia.
agent: invet-security-reviewer
---

Revisa la seguridad del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X` o `FE-00X`; si falta el ID, pregunta antes de continuar.
2. Normaliza al mismo indice vertical y ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage review`.
3. Regenera y verifica los cinco manifiestos; revisa contratos y superficies declaradas junto con plan, diff y archivos del slice.
4. Valida autenticacion, autorizacion, IDOR/BOLA, aislamiento, tokens, logs y exposicion.
5. Crea siempre `docs/opencode/reviews/BE-00X-security-review.md`.
6. Emite `APPROVED` o `REJECTED` con evidencia.
7. No modifiques codigo fuente.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
