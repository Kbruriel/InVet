---
description: Revisa seguridad de un slice identificado y escribe evidencia.
agent: invet-security-reviewer
---

Revisa la seguridad del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X` o `FE-00X`; si falta el ID, pregunta antes de continuar.
2. Normaliza al mismo indice vertical y ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage review`.
3. Revisa plan, diff y archivos del slice.
4. Valida autenticacion, autorizacion, IDOR/BOLA, aislamiento, tokens, logs y exposicion.
5. Crea siempre `docs/opencode/reviews/BE-00X-security-review.md`.
6. Emite `APPROVED` o `REJECTED` con evidencia.
7. No modifiques codigo fuente.
