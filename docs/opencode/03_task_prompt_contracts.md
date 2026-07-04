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
- Implementar rutas, layouts, componentes, formularios, validaciones, cliente API, estados UX y pruebas segun aplique.
- Respetar `Paralelismo[P]` y dependencias previas.
- Marcar `- [x]` solo en tareas frontend cuyos criterios quedaron verificados.
- Dejar `- [ ]` y documentar bloqueo cuando una tarea no pueda completarse.

Debe aplicar el sistema visual InVet.

## `/qa-task QA-00X`

Debe validar backend + frontend + integracion del slice:
- Leer `docs/opencode/plans/BE-00X-plan.md`.
- Usar objetivos y criterios de aceptacion del plan para derivar casos QA.
- Disenar o ajustar pruebas automatizadas cuando hagan falta para cubrir el slice.
- Ejecutar pruebas disponibles si el entorno lo permite.
- Documentar trazabilidad por tarea, comandos y resultados esperados vs obtenidos.
- Validar happy path, negative path, permisos, IDOR/BOLA, responsive, estados de error y regresion.
- Marcar `- [x]` solo en tareas QA o de validacion cuyos criterios quedaron verificados.
- Si existen problemas de ejecucion o de configuracion del entorno, crear `docs/opencode/qa/QA-00X-findings.md` siguiendo `docs/opencode/templates/qa_findings_template.md` para que luego lo consuma `/implement-findings`.

## Reviews y cierre

`/clean-architecture-review`, `/security-review`, `/run-checks` y `/update-docs` son gates obligatorios.
