---
description: Planifica un slice vertical InVet desde un ID BE, FE o QA.
agent: invet-product-planner
---

Planifica el slice indicado por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay contradicciones criticas entre matriz/tareas/plan o se requiere decidir alcance.
1. Acepta exactamente un argumento con formato `BE-00X`, `FE-00X` o `QA-00X`.
   - Extrae el indice y normaliza de forma explicita al slice vertical `BE-00X` / `FE-00X` / `QA-00X`.
   - Informa la normalizacion en el resumen. Esto no es un remapeo a otra tarea: los tres IDs representan el mismo indice vertical.
   - Si el formato no es valido, deten el comando sin crear ni modificar archivos.
2. Usa `BE-00X` como ID canonico y guarda siempre un unico plan compartido en `docs/opencode/plans/BE-00X-plan.md`.
3. Antes de planificar un nuevo slice, ejecuta `python backend/scripts/validate_slice_plan.py $ARGUMENTS --stage previous`.
   - Si el QA del slice anterior no esta `APPROVED` o sus findings siguen abiertos, no generes un plan nuevo.
4. Lee:
   - `docs/opencode/02_be_fe_qa_task_matrix.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/templates/slice_plan_template.md`
   - `docs/opencode/plans/BE-00X-plan.md` si ya existe.
5. Produce un plan de ejecucion vertical con:
   - Objetivo del slice.
   - Alcance MVP.
   - Fuera de alcance.
   - Entidades y reglas de negocio.
   - Endpoints esperados.
   - Contrato de implementacion frontend detallado.
   - Pruebas QA.
   - Riesgos de seguridad/IDOR/BOLA.
   - Definition of Done.
6. El contrato frontend debe definir obligatoriamente:
   - Rutas y acceso publico/privado.
   - Flujos de usuario y estados loading, submitting, error, empty y success.
   - Contrato API por accion: endpoint, metodo, request, response, errores y autenticacion.
   - Formularios, campos y validaciones.
   - Arquitectura de componentes y ubicacion en `app`, `features`, `entities` o `shared`.
   - Responsive, accesibilidad y lineamientos visuales.
   - Pruebas unitarias, de componentes, integracion y E2E aplicables.
7. Genera tareas atomicas para backend, frontend y QA con el formato exacto de la plantilla:
   - `- [ ] BE|FE|QA-00X-TNN - Titulo`
   - `Capa: backend|frontend|qa`
   - `Objetivo: ...`
   - `Depende de: Ninguna|IDs de tarea`
   - `Entregables: ...`
   - `Criterios de aceptacion: ...`
   - `Validacion: ...`
   - `Evidencia: pending`
   - `Paralelismo[P]: Si|No`
8. Cada tarea debe tener un unico objetivo, dependencias explicitas, entregables concretos y criterios verificables.
9. No implementes codigo fuente en este comando.
   - `/plan-task` nunca implementa backend, frontend ni QA; solo crea o corrige `docs/opencode/plans/BE-00X-plan.md`.
10. Si falta informacion critica, existen contradicciones entre matriz/tareas o no se pueden derivar criterios de aceptacion medibles:
   - Deten la planificacion solo cuando el gap sea bloqueante.
   - Haz preguntas concretas al usuario antes de guardar el plan final.
   - No inventes endpoints, permisos, entidades ni reglas de negocio.
   - Si el hueco no bloquea el plan, documenta la suposicion en una seccion `Suposiciones`.
11. Si el plan ya existe, ejecuta una revision de gaps antes de reescribir:
   - Verifica que todo lo indicado en matriz, BE, FE y QA este representado en el plan.
   - Identifica secciones faltantes, criterios incompletos, tareas duplicadas, dependencias no documentadas y riesgos no cubiertos.
   - Corrige gaps no bloqueantes dentro del mismo plan.
   - Preserva tareas `- [x]` solo si sus criterios siguen validos y `Evidencia` contiene archivos o comandos reproducibles.
   - Si una tarea completada carece de evidencia, regresala a `- [ ]`, usa `Evidencia: pending` y registra el motivo en `Revision de gaps`.
   - No dupliques tareas existentes; actualizalas o agrega solo las tareas faltantes.
   - Documenta cambios en una seccion `Revision de gaps`.
12. Agrega un `Checklist tecnico` obligatorio con validaciones de rutas, contratos API, permisos, migraciones/modelos, estados de error, pruebas, run-checks y documentacion.
13. Al terminar, ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage plan`.
   - No declares la planificacion terminada mientras el validador reporte errores.
