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
   - Si el plan, el user story o `UIA/APIA` estan stale o faltan, regeneralos en la misma ejecucion y conserva la evidencia vigente.
4. Lee:
   - `docs/opencode/02_be_fe_qa_task_matrix.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/user-stories/US-00X.md` si ya existe
   - `docs/opencode/tasks/ui-automation/UIA-00X.md` si ya existe
   - `docs/opencode/tasks/api-automation/APIA-00X.md` si ya existe
   - `docs/opencode/references/slice_task_context.md`
   - `docs/opencode/references/spec_kit_reference_improvements.md`
   - `docs/opencode/references/missing_artifact_generation.md` si el plan canonico o los artefactos auxiliares faltan, o si el plan solo existe en `payload/`.
   - `docs/opencode/templates/slice_plan_template.md`
   - `docs/opencode/templates/missing_artifact_generation_template.md` si el gate fallo por artefacto faltante.
   - `docs/opencode/plans/BE-00X-plan.md` si ya existe.
   - `payload/docs/opencode/plans/BE-00X-plan.md` si el plan canonico activo falta.
5. Produce un plan de ejecucion vertical con:
   - Objetivo del slice.
   - Brief operativo con titulo, descripcion, entregables backend, entregables frontend y criterios QA principales.
   - Historias `US-00X-NN` y criterios `CA-NN`.
   - Alcance MVP.
   - Fuera de alcance.
   - Entidades y reglas de negocio.
   - Fuentes y artefactos de contexto.
   - Matriz de trazabilidad criterio -> tarea -> validacion.
   - Endpoints esperados.
   - Contrato de implementacion frontend detallado.
   - Contrato de ejecucion Docker y pruebas.
   - Plan de reportes y findings.
   - Pruebas QA.
   - Riesgos de seguridad/IDOR/BOLA.
   - Politica UTF-8.
   - Definition of Done.
   - Matriz de trazabilidad con columnas `ID`, `Fuente`, `Historia o criterio`, `Tarea planificada`, `Validacion`, `Evidencia esperada` y `Estado`.
6. Ademas del plan canonico, genera o actualiza:
   - `docs/opencode/tasks/user-stories/US-00X.md`
   - `docs/opencode/tasks/ui-automation/UIA-00X.md`
   - `docs/opencode/tasks/api-automation/APIA-00X.md`
   - una matriz `Historia -> Criterio -> Backend -> Frontend -> QA -> UIA -> APIA`
   - Estos tres artefactos auxiliares se generan con `/plan-task`; no hay comandos separados para crearlos.
   - Si cualquiera de los tres falta, crealo en la misma ejecucion antes de validar el plan.
   - Si existe, auditelo contra la matriz, BE/FE/QA y plan canonico, y actualizalo sin borrar evidencia vigente.
   - Si un implementador o gate reporta `US-00X`, `UIA-00X` o `APIA-00X` faltante, el comando correcto para regenerarlo es `/plan-task BE-00X`.
7. El contrato frontend debe definir obligatoriamente:
   - Rutas y acceso publico/privado.
   - Flujos de usuario y estados loading, submitting, error, empty y success.
   - Contrato API por accion: endpoint, metodo, request, response, errores y autenticacion.
   - Formularios, campos y validaciones.
   - Arquitectura de componentes y ubicacion en `app`, `features`, `entities` o `shared`.
   - Responsive, accesibilidad y lineamientos visuales.
   - Pruebas unitarias, de componentes, integracion y E2E aplicables.
8. Genera tareas atomicas para backend, frontend y QA con el formato exacto de la plantilla:
   - `- [ ] BE|FE|QA-00X-TNN - Titulo`
   - `Capa: backend|frontend|qa`
   - `Tipo: contrato|persistencia|caso de uso|api|seguridad|cliente api|ruta|componente|estado ux|prueba|qa|documentacion|docker|reporte`
   - `Historia o criterio: AC-...`
   - `Objetivo: ...`
   - `Responsabilidad unica: Si`
   - `Depende de: Ninguna|IDs de tarea`
   - `Contexto necesario: ...`
   - `Contratos usados: ...`
   - `Entregables: ...`
   - `Criterios de aceptacion: ...`
   - `Validacion: ...`
   - `Resultado esperado: ...`
   - `Evidencia: pending`
   - `Paralelismo[P]: Si|No`
9. Cada tarea debe tener un unico objetivo, dependencias explicitas, entregables concretos, contexto minimo, contratos usados, resultado esperado y criterios verificables.
   - Usa `docs/opencode/references/slice_task_context.md` como fuente para enriquecer titulo, descripcion, entregables y criterios de aceptacion.
   - Si el brief, la matriz y las tasks BE/FE/QA discrepan, registra la decision en `Revision de gaps`.
   - Cada `CA-NN` debe quedar cubierto por UI automation, API automation o una justificacion manual.
   - Si una tarea contiene objetivos unidos por `y`, `ademas`, `tambien`, `/`, `+` o `;`, dividela.
   - Si una tarea toca mas de una capa o tipo de trabajo, dividela.
   - Si una tarea necesita varios entregables independientes para ser verificable, dividela.
10. No implementes codigo fuente en este comando.
   - `/plan-task` nunca implementa backend, frontend ni QA; solo crea o corrige `docs/opencode/plans/BE-00X-plan.md`.
11. Si falta informacion critica, existen contradicciones entre matriz/tareas o no se pueden derivar criterios de aceptacion medibles:
   - Deten la planificacion solo cuando el gap sea bloqueante.
   - Haz preguntas concretas al usuario antes de guardar el plan final.
   - No inventes endpoints, permisos, entidades ni reglas de negocio.
   - Si el hueco no bloquea el plan, documenta la suposicion en una seccion `Suposiciones`.
12. Si el plan ya existe, ejecuta una revision de gaps antes de reescribir:
   - Verifica que todo lo indicado en matriz, BE, FE y QA este representado en el plan.
   - Identifica secciones faltantes, criterios incompletos, tareas duplicadas, dependencias no documentadas y riesgos no cubiertos.
   - Corrige gaps no bloqueantes dentro del mismo plan.
   - Preserva tareas `- [x]` solo si sus criterios siguen validos y `Evidencia` contiene archivos o comandos reproducibles.
   - Si una tarea completada carece de evidencia, regresala a `- [ ]`, usa `Evidencia: pending` y registra el motivo en `Revision de gaps`.
   - No dupliques tareas existentes; actualizalas o agrega solo las tareas faltantes.
   - Documenta cambios en una seccion `Revision de gaps`.
13. Si el plan canonico falta y existe un backup en `payload/`, recuperalo como migracion legacy:
   - Usa el backup solo como fuente historica.
   - Crea el archivo nuevo en `docs/opencode/plans/BE-00X-plan.md`.
   - Migra objetivo, alcance, endpoints, riesgos y evidencias vigentes.
   - Completa todas las secciones nuevas de schema v3.
   - Divide tareas legacy compuestas en tareas atomicas con todos los campos obligatorios.
   - No declares aprobaciones de QA, reviews o checks desde backups.
14. Agrega un `Checklist tecnico` obligatorio con validaciones de rutas, contratos API, permisos, migraciones/modelos, estados de error, pruebas, Docker, run-checks, reportes/findings, UTF-8 y documentacion.
15. Al terminar, ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage plan`.
   - No declares la planificacion terminada mientras el validador reporte errores.
16. Escribe y conserva el plan en UTF-8.
   - Los textos en espanol deben conservar acentos y eñes.
   - Si aparece mojibake como `Ã`, `Â` o `â` en artefactos nuevos, corrige antes de validar.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
