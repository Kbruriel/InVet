---
description: Planifica un slice InVet a partir de un ID backend, por ejemplo BE-001.
agent: invet-product-planner
---

Planifica el slice indicado por `$ARGUMENTS`.

Instrucciones:
1. Normaliza el argumento a formato `BE-00X`.
2. Identifica el frontend y QA equivalentes: `FE-00X` y `QA-00X`.
3. Lee:
   - `docs/opencode/02_be_fe_qa_task_matrix.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
4. Produce un plan de ejecucion con:
   - Objetivo del slice.
   - Alcance MVP.
   - Fuera de alcance.
   - Entidades y reglas de negocio.
   - Endpoints esperados.
   - Componentes frontend esperados.
   - Pruebas QA.
   - Riesgos de seguridad/IDOR/BOLA.
   - Definition of Done.
5. Guarda el plan en `docs/opencode/plans/BE-00X-plan.md`.
6. El plan debe incluir un checklist numerado de tareas generadas para backend, frontend y QA usando este formato por tarea:
   - `- [ ] Numero de tarea`
   - `Objetivo: ...`
   - `Criterios de aceptacion: ...`
   - `Paralelismo[P]: Si/No`
7. Cada tarea debe tener un unico objetivo y criterios de aceptacion verificables.
8. No implementes codigo fuente en este comando.
