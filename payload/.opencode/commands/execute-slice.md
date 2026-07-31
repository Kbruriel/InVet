---
description: Ejecuta el flujo completo y sus gates para un slice InVet.
agent: invet-orchestrator
---

Ejecuta el slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Acepta `BE-00X`, `FE-00X` o `QA-00X` y normaliza explicitamente el mismo indice vertical.
2. Ejecuta el flujo obligatorio definido por `invet-orchestrator`.
3. Antes de cada etapa, ejecuta el stage correspondiente de `backend/scripts/validate_slice_plan.py`.
4. Detente ante cualquier gate fallido y reporta el comando exacto para reanudar.
5. Si `/implement-findings` aplica correcciones, repite QA y los reviews afectados.
6. No declares el slice cerrado hasta que QA, reviews y checks esten aprobados y la documentacion se actualice.
