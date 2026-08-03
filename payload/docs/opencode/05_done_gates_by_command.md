# 05 - Done Gates by Command

Este archivo define requisitos, no el estado de un slice. Los checks permanecen sin marcar para evitar confundir el contrato con evidencia real.

## `/plan-task BE-00X|FE-00X|QA-00X`

- [ ] El ID fue normalizado explicitamente al mismo slice.
- [ ] El plan usa `schema_version: 2`.
- [ ] Existe contrato frontend completo.
- [ ] Hay tareas BE, FE y QA con IDs, capa, dependencias y entregables.
- [ ] Cada tarea tiene criterios, validacion, evidencia y paralelismo.
- [ ] Las tareas completadas contienen evidencia reproducible.
- [ ] `validate_slice_plan.py --stage plan` termina en `PASS`.

## `/implement-backend-task BE-00X`

- [ ] El preflight backend pasa.
- [ ] Solo se implementan tareas `Capa: backend`.
- [ ] Las dependencias estan completas y evidenciadas.
- [ ] Los archivos productivos modificados tienen pruebas unitarias.
- [ ] La validacion de cada tarea pasa.
- [ ] El plan contiene evidencia actualizada.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando aplicaba.

## `/implement-frontend-task FE-00X`

- [ ] El preflight frontend pasa.
- [ ] El contrato frontend define rutas, flujos, API, formularios, arquitectura, accesibilidad y pruebas.
- [ ] Solo se implementan tareas `Capa: frontend`.
- [ ] Los archivos productivos modificados tienen pruebas unitarias/de componente.
- [ ] Lint, typecheck, test y build aplicables pasan.
- [ ] El plan contiene evidencia actualizada.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando aplicaba.

## `/qa-task QA-00X`

- [ ] El plan schema v2 es valido.
- [ ] Cada criterio tiene trazabilidad y estado.
- [ ] Los reportes pertenecen a la corrida actual.
- [ ] Los gaps unitarios producen `REJECTED` y findings `OPEN`.
- [ ] QA no repara pruebas unitarias de producto.
- [ ] La regresion relevante pasa.
- [ ] La decision es `APPROVED`, `REJECTED` o `BLOCKED`.
- [ ] Solo QA cambia findings a `RESOLVED`.
- [ ] Antes del cierre se valido si habia cambios pendientes que justificaran actualizar contenedores.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando QA quedo `APPROVED`.

## Reviews

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

- [ ] QA y reviews estan aprobados.
- [ ] Tests, lint, formato, tipos y build aplicables pasan.
- [ ] Cada skip es realmente no aplicable.
- [ ] Se valido si habia cambios pendientes que justificaran actualizar contenedores antes del cierre.
- [ ] Existe `docs/opencode/checks/BE-00X-checks.md`.
- [ ] El reporte contiene `Decision: APPROVED`.
- [ ] El hook de Docker Compose de cierre se ejecuto cuando todos los checks aplicables pasaron.

## `/update-docs BE-00X`

- [ ] Plan, QA, reviews y checks estan aprobados.
- [ ] Contratos, riesgos, decisiones y changelog estan actualizados.
- [ ] No quedan findings abiertos.
- [ ] El estado final contiene enlaces a evidencia.

## `/final-gate BE-00X`

- [ ] QA, reviews, checks y documentacion estan cerrados.
- [ ] Se revisaron logs, reintentos mecanicos y correcciones fallidas.
- [ ] El reviewer final usa una segunda opinion de alta capacidad.
- [ ] Existe `docs/opencode/reviews/BE-00X-final-review.md`.
- [ ] El reporte contiene `Decision: APPROVED|REJECTED|BLOCKED`.
