# 05 - Done Gates by Command

Este archivo define requisitos, no el estado de un slice. Los checks permanecen sin marcar para evitar confundir el contrato con evidencia real.

## `/plan-task BE-00X|FE-00X|QA-00X`

- [ ] El ID fue normalizado explicitamente al mismo slice.
- [ ] El plan usa `schema_version: 3` y declara `encoding: UTF-8`.
- [ ] Existe contrato frontend completo.
- [ ] Existe matriz de trazabilidad criterio -> tarea -> validacion.
- [ ] Existe contrato de ejecucion Docker y pruebas.
- [ ] Existe plan de reportes y findings.
- [ ] Existen `US-00X`, `UIA-00X` y `APIA-00X`.
- [ ] Cada criterio `CA-NN` tiene cobertura UI, API o justificacion manual.
- [ ] Hay tareas BE, FE y QA con IDs, capa, tipo, dependencias, contexto, contratos usados y entregables.
- [ ] Cada tarea tiene responsabilidad unica, criterios, validacion, resultado esperado, evidencia y paralelismo.
- [ ] No hay tareas compuestas que mezclen contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion.
- [ ] Las tareas completadas contienen evidencia reproducible.
- [ ] El plan no contiene mojibake y conserva UTF-8.
- [ ] `validate_slice_plan.py --stage plan` termina en `PASS`.

## `/implement-backend-task BE-00X`

- [ ] El preflight backend pasa.
- [ ] Solo se implementan tareas `Capa: backend`.
- [ ] Las dependencias estan completas y evidenciadas.
- [ ] Cada tarea implementada declara `Responsabilidad unica: Si`.
- [ ] Se usaron `Contexto necesario`, `Contratos usados` y `Resultado esperado`.
- [ ] Los archivos productivos modificados tienen pruebas unitarias.
- [ ] La validacion de cada tarea pasa.
- [ ] El plan contiene evidencia actualizada.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando aplicaba.

## `/implement-frontend-task FE-00X`

- [ ] El preflight frontend pasa.
- [ ] El contrato frontend define rutas, flujos, API, formularios, arquitectura, accesibilidad y pruebas.
- [ ] Solo se implementan tareas `Capa: frontend`.
- [ ] Cada tarea implementada declara `Responsabilidad unica: Si`.
- [ ] Se usaron `Contexto necesario`, `Contratos usados` y `Resultado esperado`.
- [ ] Los archivos productivos modificados tienen pruebas unitarias/de componente.
- [ ] Lint, typecheck, test y build aplicables pasan.
- [ ] El plan contiene evidencia actualizada.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando aplicaba.

## `/qa-task QA-00X`

- [ ] El plan schema v3 es valido.
- [ ] Cada criterio tiene trazabilidad y estado.
- [ ] La matriz QA incorpora historia o criterio, contexto necesario, contratos usados y resultado esperado.
- [ ] Los reportes pertenecen a la corrida actual.
- [ ] Los gaps unitarios producen `REJECTED` y findings `OPEN`.
- [ ] QA no repara pruebas unitarias de producto.
- [ ] La regresion relevante pasa.
- [ ] La decision es `APPROVED`, `REJECTED` o `BLOCKED`.
- [ ] Solo QA cambia findings a `RESOLVED`.
- [ ] Los resultados y findings estan escritos en UTF-8.
- [ ] Si existen tareas heredadas, el registro `docs/opencode/carryovers/BE-00X-carryovers.md` existe y no tiene estados `OPEN` o `TRANSFERRED`.
- [ ] Antes del cierre se valido si habia cambios pendientes que justificaran actualizar contenedores y se confirmo que los contenedores Docker aplicables quedaron actualizados o recreados.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando QA quedo `APPROVED`.

## `/implement-ui-automation-task FE-00X`

- [ ] Existe `UIA-00X.md`.
- [ ] Se leyeron `US-00X`, `BE-00X`, `FE-00X`, `QA-00X` y `UIA-00X`.
- [ ] Los specs se implementaron en `InVet_UI_Automation/tests/e2e`.
- [ ] Los tests referencian `US-00X-NN` y `CA-NN`.
- [ ] `npm run test:e2e` pasa o el bloqueo queda documentado.
- [ ] `npm run test:regression` pasa o el bloqueo queda documentado.
- [ ] `UIA-00X` contiene evidencia y casos no automatizados.

## `/implement-api-automation-task BE-00X`

- [ ] Existe `APIA-00X.md`.
- [ ] Se leyeron `US-00X`, `BE-00X`, `FE-00X`, `QA-00X` y `APIA-00X`.
- [ ] Los specs se implementaron en `InVet_UI_Automation/tests/api`.
- [ ] Los tests referencian `US-00X-NN` y `CA-NN`.
- [ ] `npm run test:api` pasa o el bloqueo queda documentado.
- [ ] `APIA-00X` contiene evidencia y casos no automatizados.

## `/run-ui-checks FE-00X`

- [ ] Existe `UIA-00X.md`.
- [ ] La UI/regresion corre sobre `http://localhost:3000`.
- [ ] Las rutas relevantes del slice quedaron explicitas en la evidencia (`/clinicas`, `/portal/owner/appointments`, `/portal/owner/appointments/new`, `/clinic/appointments`).
- [ ] `npm run test:e2e` pasa.
- [ ] `npm run test:regression` pasa.
- [ ] Los fallos o skips tienen evidencia verificable.

## Reviews

- [ ] Todas las tareas aplicables del plan estan en `- [x]` con evidencia reproducible antes del primer review.
- [ ] Toda tarea abierta no aplicable declara `Estado: CANCELLED` y evidencia verificable.
- [ ] `/review-slice BE-00X` escribe `BE-00X-review.md`.
- [ ] `/clean-architecture-review BE-00X` escribe su reporte.
- [ ] `/security-review BE-00X` escribe su reporte.
- [ ] Cada reporte contiene `Decision: APPROVED|REJECTED`.
- [ ] Los reviews no infieren IDs ambiguos ni modifican producto.

## `/implement-findings BE-00X|FE-00X`

- [ ] Corrige solo hallazgos del slice.
- [ ] Agrega pruebas unitarias faltantes en la capa responsable.
- [ ] Reejecuta validaciones relevantes.
- [ ] Documenta correcciones.
- [ ] Cambia findings QA a `READY_FOR_REVALIDATION`, no `RESOLVED`.
- [ ] Deriva el cierre a `/qa-task QA-00X`.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando las correcciones quedaron listas.

## `/run-checks BE-00X`

- [ ] No quedan tareas aplicables abiertas ni tareas `CANCELLED` sin evidencia verificable.
- [ ] QA y reviews estan aprobados.
- [ ] UI automation y API automation estan aprobadas o justificadas.
- [ ] `run-ui-checks` ya paso para el slice.
- [ ] La API del slice corrió sobre `http://localhost:8000/api/v1`.
- [ ] Tests, lint, formato, tipos y build aplicables pasan.
- [ ] Cada skip es realmente no aplicable.
- [ ] Se valido si habia cambios pendientes que justificaran actualizar contenedores antes del cierre.
- [ ] Existe `docs/opencode/checks/BE-00X-checks.md`.
- [ ] El reporte contiene `Decision: APPROVED`.
- [ ] Si existen tareas heredadas, el registro de carryovers sigue cerrado o cancelado y coincide con el plan origen.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando todos los checks aplicables pasaron.

## `/update-docs BE-00X`

- [ ] No quedan tareas aplicables abiertas ni inconsistencias entre checkbox, estado y evidencia.
- [ ] Plan, QA, reviews y checks estan aprobados.
- [ ] Contratos, riesgos, decisiones y changelog estan actualizados.
- [ ] No quedan findings abiertos.
- [ ] Si existen tareas heredadas, el plan origen, el plan destino y el registro de carryovers muestran la misma evidencia.
- [ ] El estado final contiene enlaces a evidencia.

## `/final-gate BE-00X`

- [ ] QA, reviews, checks y documentacion estan cerrados.
- [ ] Se revisaron logs, reintentos mecanicos y correcciones fallidas.
- [ ] El reviewer final usa una segunda opinion de alta capacidad.
- [ ] Si existen tareas heredadas, el registro de carryovers esta en `CLOSED` o `CANCELLED` con evidencia reproducible.
- [ ] Existe `docs/opencode/reviews/BE-00X-final-review.md`.
- [ ] El reporte contiene `Decision: APPROVED|REJECTED|BLOCKED`.
