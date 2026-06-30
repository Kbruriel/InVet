---
description: Ejecuta QA funcional y técnico para una tarea QA InVet, por ejemplo QA-001.
agent: invet-qa-validator
---

Valida la tarea QA indicada por `$ARGUMENTS`.

Instrucciones:
1. Normaliza el argumento a `QA-00X`.
2. Lee:
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
3. Valida happy path, negative path, permisos, IDOR/BOLA, regresión y UI responsive.
4. Ejecuta pruebas disponibles si el entorno lo permite.
5. Reporta evidencia y defectos.
6. No apruebes si hay blockers de seguridad, arquitectura o datos privados expuestos.
