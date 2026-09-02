# APIA-014 — Automatizacion de pruebas API / Soporte básico

## Proposito

Ejecutar pruebas automatizadas contra endpoints del backend (Docker container `backend` con PostgreSQL `db`) para verificar contratos, estados HTTP, seguridad y validaciones de todos los criterios AC del slice 014.

## Alcance y cobertura

| Casos | Cubre criterio(s) | Endpoint probado |
| --- | --- | --- |
| C1 - Ticket creation happy path (POST /tickets valido) | AC-014-01 | POST /api/v1/tickets |
| C2 - Title <5 chars rejected → 400 | AC-014-03 | POST /api/v1/tickets invalid title |
| C3 - Pagination list tickets with valid page/page_size/status filter | AC-014-03 | GET /api/v1/tickets ?page&page_size&status |
| C4 - Detail for own ticket → 200; detail for other owner → 404 secure | AC-014-04 | GET /api/v1/tickets/{id} |
| C5 - Status transition initiated→pending valid by admin internal_user PATCH ok | AC-014-05 | PATCH /api/v1/tickets/{id}/status |
| C6 - Owner attempting status change → 403 forbidden (not admin role) | AC-014-05 | PATCH /api/v1/tickets/{id}/status owner |
| C7 - Invalid transition attempted → 422 state machine invalid | AC-014-05 | PATCH /invalid status |
| C8 - Categories list endpoint returns active categories for clinic scope | AC-014-06 | GET /api/v1/tickets/categories |
| C9 - All five endpoints return 401 without Bearer token | AC-014-07 | Each /tickets* endpoint without auth header |
| C10 - Migration a014 reversible upgrade head/downgrade/-1/upgrade head succeeds | AC-014-10 | alembic upgrade/downgrade commands |
| C11 - Cross-clinic ticket cannot be listed by unauthorized user → 404 or empty list (no enumeration) | AC-014-11 | GET /api/v1/tickets with cross-clinic user |
| C12 - Status enum validation backend rejects values not in [iniciado, pendiente, proceso, completado, cerrado] | AC-014-05 | PATCH invalid new_status |

## Requisitos de ejecucion

| Necesidad | Detalle | Evidencia esperada |
| --- | --- | --- |
| Docker container `db` running | `docker compose up -d db` with Postgres healthy. | `pg_isready` output or docker inspect state = healthy |
| Database schema applied | Alembic migration a014 must be at head before tests run. | alembic current returns a014 |
| Seed categories table | At least 3 rows in categories with distinct (clinic_id,name). | SELECT count FROM ticket_category → >=3 |
| Test data isolation | Each test creates temporary tickets in isolated transaction/fixture or rollback after each case. | No interference between C1 and others; clean assertions post-test. |

## Herramienta y ejecucion

- Framework: `pytest` con HTTPX transport para FastAPI (testing client) o Docker container with pytest hitting endpoints via published port 8000.
- Comandos esperados de ejecucion en contenedor Docker backend:
  - `docker compose run --rm backend pytest tests/api/test_tickets_creation.py tests/api/test_tickets_list.py tests/api/test_tickets_detail.py tests/api/test_tickets_status.py tests/api/test_tickets_categories.py tests/api/test_tickets_auth.py tests/api/test_tickets_idor.py -q`

## Criterios de aprobacion

- Todos los casos (C1-C12) terminan PASS.
- Sin regresion en endpoint tests de slices previos (BE-002, BE-013) durante ejecucion de suite completa.
- No hay pruebas bloqueadas o skip con justificacion no verificable.

## Regresiones planificadas

| Slice origen | Riesgo de regresion por slice 014 | Comprobacion automatica |
| --- | --- | --- |
| BE-013 Notifications | Endpoints notifications no afectados por routers nuevos; sin collision de prefix /tickets vs /notifications | APIA C14: run all prior + 014 suites together PASS |
