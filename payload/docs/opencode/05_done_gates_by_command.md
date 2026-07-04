# 05 - Gates de cierre por comando

## Gate despues de `/plan-task`

- Slice definido.
- Scope MVP claro.
- Fuera de alcance explicito.
- Contratos backend/frontend definidos.
- QA planificado.
- Plan guardado en `docs/opencode/plans/BE-00X-plan.md`.
- Checklist numerado con objetivo, criterios de aceptacion medibles y `Paralelismo[P]`.

## Gate despues de `/implement-backend-task`

- Tareas backend pendientes del plan implementadas.
- Tareas backend completadas marcadas como `- [x]` solo despues de verificar criterios.
- API bajo `/api/v1`.
- Casos de uso fuera del router.
- Dominio sin dependencia de frameworks.
- Repositorios desacoplados.
- Migraciones si aplican.
- Pruebas backend.

## Gate despues de `/implement-frontend-task`

- Tareas frontend pendientes del plan implementadas.
- Tareas frontend completadas marcadas como `- [x]` solo despues de verificar criterios.
- Rutas y componentes implementados.
- Tailwind local.
- Tokens InVet aplicados.
- Estados loading/error/empty/success.
- Consumo API centralizado.
- Rutas privadas protegidas si aplica.

## Gate despues de `/qa-task`

- Casos QA derivados de objetivos y criterios de aceptacion del plan.
- Resultados documentados con trazabilidad por tarea del plan.
- Tareas QA completadas marcadas como `- [x]` solo despues de evidencia de validacion.
- Happy path validado.
- Negative path validado.
- Permisos e IDOR/BOLA validados.
- Regresion cubierta.
- Evidencia registrada.
- Pruebas creadas o ajustadas cuando eran necesarias.
- Bloqueos de ejecucion/configuracion documentados en Markdown si existieron.

## Gate arquitectura

- Sin logica de negocio en routers.
- Sin ORM expuesto.
- Dominio limpio.
- Frontend modular.

## Gate seguridad

- Auth y permisos correctos.
- Aislamiento tenant/owner/branch.
- Logs sin sensibles.
- Paginacion/rate limit donde aplica.

## Gate checks

- Backend y frontend compilan o fallos documentados.
- Tests/lint/typecheck/build ejecutados segun disponibilidad.

## Gate docs

- Estado del slice actualizado.
- Decisiones y riesgos documentados.
