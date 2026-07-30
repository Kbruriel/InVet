---
description: Planifica un slice InVet a partir de un ID backend, por ejemplo BE-001.
agent: invet-product-planner
---

Planifica el slice indicado por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay contradicciones criticas entre matriz/tareas/plan o se requiere decidir alcance.
1. Acepta exclusivamente argumentos `BE-00X`.
   - Si recibe `FE-00X`, no normalices ni implementes codigo: explica que `/plan-task` solo genera o actualiza el plan del slice vertical, no debe remapear silenciosamente a backend y redirige a `/implement-frontend-task FE-00X`.
   - Si recibe `QA-00X`, no normalices ni implementes codigo: explica que `/plan-task` no ejecuta QA, no debe remapear silenciosamente a backend y redirige a `/qa-task QA-00X`.
   - Solo si el argumento ya viene como `BE-00X`, continua con la planificacion.
2. Identifica el frontend y QA equivalentes: `FE-00X` y `QA-00X`.
3. Lee:
   - `docs/opencode/02_be_fe_qa_task_matrix.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/plans/BE-00X-plan.md` si ya existe.
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
   - `/plan-task` nunca implementa backend, frontend ni QA; solo crea o corrige `docs/opencode/plans/BE-00X-plan.md`.
9. Si falta informacion critica, existen contradicciones entre matriz/tareas o no se pueden derivar criterios de aceptacion medibles:
   - Deten la planificacion solo cuando el gap sea bloqueante.
   - Haz preguntas concretas al usuario antes de guardar el plan final.
   - No inventes endpoints, permisos, entidades ni reglas de negocio.
   - Si el hueco no bloquea el plan, documenta la suposicion en una seccion `Suposiciones`.
10. Si el plan ya existe, ejecuta una revision de gaps antes de reescribir:
   - Verifica que todo lo indicado en matriz, BE, FE y QA este representado en el plan.
   - Identifica secciones faltantes, criterios incompletos, tareas duplicadas, dependencias no documentadas y riesgos no cubiertos.
   - Corrige gaps no bloqueantes dentro del mismo plan.
   - Preserva tareas marcadas como `- [x]` si su criterio de aceptacion sigue siendo valido.
   - No dupliques tareas existentes; actualizalas o agrega solo las tareas faltantes.
   - Documenta cambios en una seccion `Revision de gaps`.
11. Agrega un `Checklist tecnico` obligatorio con validaciones de rutas, contratos API, permisos, migraciones/modelos, estados de error, pruebas, run-checks y documentacion.
