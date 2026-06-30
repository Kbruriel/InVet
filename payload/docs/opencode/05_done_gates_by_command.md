# 05 — Gates de cierre por comando

## Gate después de `/plan-task`

- Slice definido.
- Scope MVP claro.
- Fuera de alcance explícito.
- Contratos backend/frontend definidos.
- QA planificado.

## Gate después de `/implement-backend-task`

- API bajo `/api/v1`.
- Casos de uso fuera del router.
- Dominio sin dependencia de frameworks.
- Repositorios desacoplados.
- Migraciones si aplican.
- Pruebas backend.

## Gate después de `/implement-frontend-task`

- Rutas y componentes implementados.
- Tailwind local.
- Tokens InVet aplicados.
- Estados loading/error/empty/success.
- Consumo API centralizado.
- Rutas privadas protegidas si aplica.

## Gate después de `/qa-task`

- Happy path validado.
- Negative path validado.
- Permisos e IDOR/BOLA validados.
- Regresión cubierta.
- Evidencia registrada.

## Gate arquitectura

- Sin lógica de negocio en routers.
- Sin ORM expuesto.
- Dominio limpio.
- Frontend modular.

## Gate seguridad

- Auth y permisos correctos.
- Aislamiento tenant/owner/branch.
- Logs sin sensibles.
- Paginación/rate limit donde aplica.

## Gate checks

- Backend y frontend compilan o fallos documentados.
- Tests/lint/typecheck/build ejecutados según disponibilidad.

## Gate docs

- Estado del slice actualizado.
- Decisiones y riesgos documentados.
