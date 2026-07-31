---
description: Actualiza documentacion Markdown despues de cerrar los gates del slice.
agent: invet-docs-updater
---

Actualiza la documentacion del slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Requiere `BE-00X`, `FE-00X` o `QA-00X` y normaliza el mismo indice vertical.
2. Ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage docs`.
3. Si el preflight falla, no documentes el slice como cerrado.
4. Revisa implementacion, QA, reviews y checks.
5. Actualiza `docs/opencode` segun aplique.
6. Documenta endpoints, componentes, decisiones, riesgos y pendientes.
7. Manten separados MVP, Stage 1, Stage 2 y fuera de alcance.
8. No modifiques codigo fuente.
9. Resume los Markdown actualizados.
