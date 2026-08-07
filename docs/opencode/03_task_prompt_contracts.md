# 03 - Contratos de prompts por comando

## `/plan-task BE-00X|FE-00X|QA-00X`

Debe producir `docs/opencode/plans/BE-00X-plan.md` y los artefactos `US-00X`, `UIA-00X` y `APIA-00X` con:
- Frontmatter `schema_version: 3`, indice, plan canonico y `encoding: UTF-8`.
- Objetivo.
- Brief operativo del slice con titulo, descripcion, entregables backend, entregables frontend y criterios QA principales.
- Historias `US-00X-NN` y criterios `CA-NN`.
- Alcance MVP.
- Fuera de alcance.
- Entidades.
- Reglas.
- Fuentes y artefactos de contexto.
- Matriz de trazabilidad criterio -> tarea -> validacion.
- Endpoints.
- Contrato frontend con rutas, flujos, API, formularios, arquitectura, accesibilidad y pruebas.
- Contrato de ejecucion Docker y pruebas.
- Plan de reportes y findings.
- Casos QA.
- Riesgos.
- Politica UTF-8.
- Definition of Done.
- Checklist numerado de tareas para backend, frontend y QA.
- Matriz `Historia -> Criterio -> Backend -> Frontend -> QA -> UIA -> APIA`.

Cada tarea del checklist debe incluir:
- `- [ ] BE|FE|QA-00X-TNN - Titulo`
- `Capa: backend|frontend|qa`
- `Tipo: contrato|persistencia|caso de uso|api|seguridad|cliente api|ruta|componente|estado ux|prueba|qa|documentacion|docker|reporte`
- `Historia o criterio: AC-...`
- `Objetivo: ...`
- `Responsabilidad unica: Si`
- `Depende de: ...`
- `Contexto necesario: ...`
- `Contratos usados: ...`
- `Entregables: ...`
- `Criterios de aceptacion: ...`
- `Validacion: ...`
- `Resultado esperado: ...`
- `Evidencia: pending`
- `Paralelismo[P]: Si|No`

Cada tarea debe ser pequena, de una sola capa y un solo tipo. Si mezcla contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion, debe dividirse antes de implementar.

No debe escribir codigo fuente. Los tres tipos de ID normalizan explicitamente el mismo indice y producen un unico plan canonico.
Debe usar `docs/opencode/references/slice_task_context.md` para enriquecer titulo, descripcion, entregables y criterios de aceptacion de cada task.
Si la matriz, las tasks BE/FE/QA y `slice_task_context.md` no coinciden, debe registrar la decision en `Revision de gaps` antes de generar tareas.
Debe crear o actualizar `docs/opencode/tasks/user-stories/US-00X.md`, `docs/opencode/tasks/ui-automation/UIA-00X.md` y `docs/opencode/tasks/api-automation/APIA-00X.md`.
Cada `CA-NN` debe tener cobertura UI, API o una justificacion manual explicita.
Debe terminar con `python backend/scripts/validate_slice_plan.py BE-00X --stage plan` en `PASS`.
Debe escribir el plan en UTF-8 y corregir mojibake antes de cerrar.

## Estados de cierre compartidos

Todos los prompts y comandos de este documento deben terminar con `Estado de ejecucion` y `Siguiente paso recomendado`.

Estados de ejecucion permitidos por familia:

- QA y reviewers: `APPROVED`, `REJECTED` o `BLOCKED`.
- Findings implementer: `READY_FOR_REVALIDATION`, `COMPLETED` o `BLOCKED`.
- Implementadores, planner, check runner, docs updater y final reviewer: `COMPLETED` o `BLOCKED`, salvo que el gate concreto use `APPROVED` o `REJECTED`.

`READY_FOR_REVALIDATION` solo describe findings. No debe usarse como estado de cierre de QA o de un review.

## `/implement-backend-task BE-00X`

Debe implementar solo tareas backend pendientes del plan:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Ejecutar el preflight `--stage backend`.
- Usar objetivo y criterios de aceptacion de cada tarea como contrato.
- Usar `Tipo`, `Historia o criterio`, `Contexto necesario`, `Contratos usados` y `Resultado esperado` para interpretar cada tarea.
- Detenerse si `Responsabilidad unica` no es `Si` o si la tarea mezcla responsabilidades independientes.
- Implementar entidades/value objects, casos de uso, repositorios/ports, ORM/migraciones, schemas, routers y pruebas segun aplique.
- Respetar `Paralelismo[P]` y dependencias previas.
- Marcar `- [x]` solo en tareas backend cuyos criterios quedaron verificados.
- Registrar evidencia y crear pruebas unitarias de los archivos productivos modificados.
- Dejar `- [ ]` y documentar bloqueo cuando una tarea no pueda completarse.

Debe cumplir Clean Architecture.
Hook de cierre: si Docker Compose esta disponible y el comando no quedo bloqueado, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.

## `/implement-frontend-task FE-00X`

Debe implementar solo tareas frontend pendientes del plan:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Ejecutar el preflight `--stage frontend`.
- Usar objetivo y criterios de aceptacion de cada tarea como contrato.
- Usar `Tipo`, `Historia o criterio`, `Contexto necesario`, `Contratos usados` y `Resultado esperado` para interpretar cada tarea.
- Detenerse si `Responsabilidad unica` no es `Si` o si la tarea mezcla responsabilidades independientes.
- Si la tarea corresponde a base tecnica y falta `frontend/package.json`, bootstrappear primero la app frontend verificable del workspace.
- Implementar rutas, layouts, componentes, formularios, validaciones, cliente API, estados UX y pruebas segun aplique.
- Respetar `Paralelismo[P]` y dependencias previas.
- Marcar `- [x]` solo en tareas frontend cuyos criterios quedaron verificados.
- Registrar evidencia y crear pruebas unitarias/de componente de los archivos productivos modificados.
- Dejar `- [ ]` y documentar bloqueo cuando una tarea no pueda completarse.

Debe aplicar el sistema visual InVet.
Hook de cierre: si Docker Compose esta disponible y el comando no quedo bloqueado, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.

## `/qa-task QA-00X`

Debe validar backend + frontend + integracion del slice:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Intentar auto-recuperacion del entorno antes de bloquear QA usando `python backend/scripts/prepare_qa_env.py --install-deps` o equivalente desde `backend/`.
- Usar objetivos y criterios de aceptacion del plan para derivar casos QA.
- Construir matriz de trazabilidad por criterio con riesgo, caso, nivel, suite, comando, resultado, evidencia y estado.
- Incluir en la matriz `Historia o criterio`, `Contexto necesario`, `Contratos usados` y `Resultado esperado` desde el plan.
- Disenar o ajustar pruebas QA de aceptacion, integracion, contrato, seguridad y regresion.
- Detectar archivos productivos BE/FE modificados sin pruebas unitarias explicitas y tratarlos como un gate material.
- Rechazar el gap y derivar su correccion; QA no implementa pruebas unitarias de producto.
- Ejecutar pruebas disponibles si el entorno lo permite.
- Si el slice requiere base de datos, usar el stack de Docker del repo como contexto de ejecucion: `docker compose up -d db` y luego `docker compose run --rm backend pytest app/tests/ -q` o una ruta puntual equivalente.
- Si el backend ya esta corriendo y la suite necesita el mismo contenedor, `docker compose exec backend ...` es valido.
- No dar por equivalente una corrida local en el host cuando el criterio pide PostgreSQL en contenedor.
- El contenedor de `frontend` es de runtime por defecto; solo usarlo para pruebas si el flujo de testing lo preparo explicitamente.
- Validar que las pruebas fueron recolectadas y ejecutadas de verdad, no solo que el comando termino con exit code cero.
- Documentar trazabilidad por tarea, comandos, reportes, resultados esperados vs obtenidos y decision final.
- Validar happy path, negative path, permisos, IDOR/BOLA, responsive, estados de error y regresion.
- Si persisten archivos productivos BE/FE sin pruebas unitarias explicitas al cierre de la corrida, marcar los criterios afectados en `FAIL`, generar `docs/opencode/qa/QA-00X-findings.md` y emitir `REJECTED`.
- Marcar `- [x]` solo en tareas QA o de validacion cuyos criterios quedaron verificados.
- Rechazar tareas compuestas o sin responsabilidad unica como `BLOCKED` por contrato de plan.
- Solo si falla la auto-recuperacion o si la suite requiere un servicio externo no mockeable, crear `docs/opencode/qa/QA-00X-findings.md` siguiendo `docs/opencode/templates/qa_findings_template.md` para que luego lo consuma `/implement-findings`.
- Usar `docs/opencode/templates/qa_results_template.md` para `docs/opencode/qa/QA-00X-results.md`.
- Cierre requerido: el reporte final debe incluir `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` antes de `Siguiente paso recomendado`.
- `READY_FOR_REVALIDATION` no es un estado de cierre de QA; ese valor pertenece al lifecycle de findings.
- Si el findings file sigue `READY_FOR_REVALIDATION`, la salida debe reflejar el bloqueo real y derivar al flujo de correcciones, no pedir un auto-rerun del mismo gate.
Hook de cierre: si QA termina en `APPROVED` y Docker Compose esta disponible, primero validar si existen cambios pendientes que afecten `backend`, `frontend`, `docker-compose.yml`, `Dockerfile*`, `backend/requirements.txt`, `backend/pyproject.toml`, `frontend/package.json` o lockfiles.
Si no existen cambios pendientes que requieran actualizar contenedores, registrar el skip con la causa exacta y no ejecutar el restart.
Si existen cambios pendientes, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.

## `/implement-ui-automation-task FE-00X`

Debe implementar solo tareas de automatizacion UI del slice:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Leer `docs/opencode/tasks/user-stories/US-00X.md`.
- Leer `docs/opencode/tasks/ui-automation/UIA-00X.md`.
- Leer las tasks `BE-00X`, `FE-00X` y `QA-00X` del mismo slice.
- Implementar specs Playwright en `InVet_UI_Automation/tests/e2e`.
- Cubrir flujos visibles, navegacion, formularios, redirects y estados UX.
- Referenciar `US-00X-NN` y `CA-NN`.
- Ejecutar `npm run test:e2e` y `npm run test:regression`.
- Documentar evidencia y casos no automatizados.

## `/implement-api-automation-task BE-00X`

Debe implementar solo tareas de automatizacion API del slice:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Leer `docs/opencode/tasks/user-stories/US-00X.md`.
- Leer `docs/opencode/tasks/api-automation/APIA-00X.md`.
- Leer las tasks `BE-00X`, `FE-00X` y `QA-00X` del mismo slice.
- Implementar specs Playwright en `InVet_UI_Automation/tests/api`.
- Validar payloads, statuses, authn/authz, IDOR/BOLA, aislamiento tenant y datos sensibles.
- Referenciar `US-00X-NN` y `CA-NN`.
- Ejecutar `npm run test:api`.
- Documentar evidencia y casos no automatizados.

## `/run-ui-checks FE-00X`

Debe ejecutar los checks UI oficiales del proyecto de automatizacion:
- Correr `npm run test:e2e`.
- Correr `npm run test:regression`.
- Reportar evidencia y bloqueos antes de permitir `/run-checks BE-00X`.

## `/review-slice BE-00X|FE-00X`

Debe revisar el slice vertical completo desde backend o frontend:
- Aceptar `BE-00X` o `FE-00X` como entrada valida.
- Si recibe `FE-00X`, derivar el `BE-00X` equivalente y revisar el mismo slice vertical.
- Si recibe `QA-00X`, detenerse y redirigir a `/qa-task QA-00X`; no debe remapear silenciosamente.
- Leer `docs/opencode/plans/BE-00X-plan.md` cuando exista.
- Leer `docs/opencode/tasks/backend/BE-00X.md`, `docs/opencode/tasks/frontend/FE-00X.md` y `docs/opencode/tasks/qa/QA-00X.md`.
- Revisar `git diff` y archivos modificados del slice.
- Documentar hallazgos en `docs/opencode/reviews/BE-00X-review.md` cuando existan.
- Cierre requerido: el reporte final debe incluir `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` antes de `Siguiente paso recomendado`.

## `/clean-architecture-review`

Debe revisar la implementacion actual con foco en Clean Architecture:
- Identifica el slice `BE-00X` afectado a partir del contexto actual.
- Revisa `git diff` y los archivos modificados.
- Valida backend por capas y frontend por modularidad.
- Si hay hallazgos, crea `docs/opencode/reviews/BE-00X-clean-architecture-review.md` usando `docs/opencode/templates/review_findings_template.md`.
- Si no hay hallazgos, reporta estado Aprobado.

## `/security-review`

Debe revisar la implementacion actual con foco en seguridad:
- Identifica el slice `BE-00X` afectado a partir del contexto actual.
- Revisa `git diff` y los archivos modificados.
- Valida autenticacion, autorizacion, IDOR/BOLA, tokens, logs y exposicion de datos.
- Si hay hallazgos, crea `docs/opencode/reviews/BE-00X-security-review.md` usando `docs/opencode/templates/review_findings_template.md`.
- Si no hay hallazgos, reporta estado Aprobado.
Hook de cierre: si las correcciones quedan listas y Docker Compose esta disponible, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.

## Reviews y cierre

`/clean-architecture-review`, `/security-review`, `/run-checks` y `/update-docs` son gates obligatorios.
`/implement-findings` debe aceptar `BE-00X` o `FE-00X`; si recibe `FE-00X`, debe derivar el `BE-00X` equivalente y corregir el mismo slice vertical.
`/implement-findings` puede consumir `docs/opencode/reviews/BE-00X-review.md`, `docs/opencode/reviews/BE-00X-clean-architecture-review.md`, `docs/opencode/reviews/BE-00X-security-review.md` y `docs/opencode/qa/QA-00X-findings.md`.
Hook de cierre: si las correcciones quedan listas y Docker Compose esta disponible, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.
