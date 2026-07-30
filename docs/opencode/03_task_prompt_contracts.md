# 03 - Contratos de prompts por comando

## `/plan-task BE-00X`

Debe producir `docs/opencode/plans/BE-00X-plan.md` con:
- Objetivo.
- Alcance MVP.
- Fuera de alcance.
- Entidades.
- Reglas.
- Endpoints.
- Componentes frontend relacionados.
- Casos QA.
- Riesgos.
- Definition of Done.
- Checklist numerado de tareas para backend, frontend y QA.

Cada tarea del checklist debe incluir:
- `- [ ] Numero de tarea`
- `Objetivo: ...`
- `Criterios de aceptacion: ...`
- `Paralelismo[P]: Si/No`

No debe escribir codigo fuente.
Si recibe `FE-00X` o `QA-00X`, debe detenerse y redirigir al comando correcto; no debe remapear silenciosamente a `BE-00X`.

## `/implement-backend-task BE-00X`

Debe implementar solo tareas backend pendientes del plan:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Usar objetivo y criterios de aceptacion de cada tarea como contrato.
- Implementar entidades/value objects, casos de uso, repositorios/ports, ORM/migraciones, schemas, routers y pruebas segun aplique.
- Respetar `Paralelismo[P]` y dependencias previas.
- Marcar `- [x]` solo en tareas backend cuyos criterios quedaron verificados.
- Dejar `- [ ]` y documentar bloqueo cuando una tarea no pueda completarse.

Debe cumplir Clean Architecture.

## `/implement-frontend-task FE-00X`

Debe implementar solo tareas frontend pendientes del plan:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Usar objetivo y criterios de aceptacion de cada tarea como contrato.
- Si la tarea corresponde a base tecnica y falta `frontend/package.json`, bootstrappear primero la app frontend verificable del workspace.
- Implementar rutas, layouts, componentes, formularios, validaciones, cliente API, estados UX y pruebas segun aplique.
- Respetar `Paralelismo[P]` y dependencias previas.
- Marcar `- [x]` solo en tareas frontend cuyos criterios quedaron verificados.
- Dejar `- [ ]` y documentar bloqueo cuando una tarea no pueda completarse.

Debe aplicar el sistema visual InVet.

## `/qa-task QA-00X`

Debe validar backend + frontend + integracion del slice:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Intentar auto-recuperacion del entorno antes de bloquear QA usando `python backend/scripts/prepare_qa_env.py --install-deps` o equivalente desde `backend/`.
- Usar objetivos y criterios de aceptacion del plan para derivar casos QA.
- Construir matriz de trazabilidad por criterio con riesgo, caso, nivel, suite, comando, resultado, evidencia y estado.
- Disenar o ajustar pruebas automatizadas cuando hagan falta para cubrir el slice.
- Ejecutar pruebas disponibles si el entorno lo permite.
- Validar que las pruebas fueron recolectadas y ejecutadas de verdad, no solo que el comando termino con exit code cero.
- Documentar trazabilidad por tarea, comandos, reportes, resultados esperados vs obtenidos y decision final.
- Validar happy path, negative path, permisos, IDOR/BOLA, responsive, estados de error y regresion.
- Marcar `- [x]` solo en tareas QA o de validacion cuyos criterios quedaron verificados.
- Solo si falla la auto-recuperacion o si la suite requiere un servicio externo no mockeable, crear `docs/opencode/qa/QA-00X-findings.md` siguiendo `docs/opencode/templates/qa_findings_template.md` para que luego lo consuma `/implement-findings`.
- Usar `docs/opencode/templates/qa_results_template.md` para `docs/opencode/qa/QA-00X-results.md`.

## `/review-slice BE-00X|FE-00X`

Debe revisar el slice vertical completo desde backend o frontend:
- Aceptar `BE-00X` o `FE-00X` como entrada valida.
- Si recibe `FE-00X`, derivar el `BE-00X` equivalente y revisar el mismo slice vertical.
- Si recibe `QA-00X`, detenerse y redirigir a `/qa-task QA-00X`; no debe remapear silenciosamente.
- Leer `docs/opencode/plans/BE-00X-plan.md` cuando exista.
- Leer `docs/opencode/tasks/backend/BE-00X.md`, `docs/opencode/tasks/frontend/FE-00X.md` y `docs/opencode/tasks/qa/QA-00X.md`.
- Revisar `git diff` y archivos modificados del slice.
- Documentar hallazgos en `docs/opencode/reviews/BE-00X-review.md` cuando existan.

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

## Reviews y cierre

`/clean-architecture-review`, `/security-review`, `/run-checks` y `/update-docs` son gates obligatorios.
`/implement-findings` debe aceptar `BE-00X` o `FE-00X`; si recibe `FE-00X`, debe derivar el `BE-00X` equivalente y corregir el mismo slice vertical.
`/implement-findings` puede consumir `docs/opencode/reviews/BE-00X-review.md`, `docs/opencode/reviews/BE-00X-clean-architecture-review.md`, `docs/opencode/reviews/BE-00X-security-review.md` y `docs/opencode/qa/QA-00X-findings.md`.
