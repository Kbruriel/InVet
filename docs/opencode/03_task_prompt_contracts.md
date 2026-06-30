# 03 — Contratos de prompts por comando

## `/plan-task BE-00X`

Debe producir:
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

No debe escribir código.

## `/implement-backend-task BE-00X`

Debe implementar solo backend del slice:
- Entidades/value objects.
- Casos de uso.
- Repositorios/ports.
- ORM/migraciones.
- Schemas.
- Routers.
- Pruebas.

Debe cumplir Clean Architecture.

## `/implement-frontend-task FE-00X`

Debe implementar solo frontend del slice:
- Rutas.
- Layouts.
- Componentes.
- Formularios.
- Validaciones.
- Cliente API.
- Estados UX.
- Pruebas.

Debe aplicar el sistema visual InVet.

## `/qa-task QA-00X`

Debe validar backend + frontend + integración del slice:
- Happy path.
- Negative path.
- Permisos.
- IDOR/BOLA.
- Responsive.
- Estados de error.
- Regresión.

## Reviews y cierre

`/clean-architecture-review`, `/security-review`, `/run-checks` y `/update-docs` son gates obligatorios.
