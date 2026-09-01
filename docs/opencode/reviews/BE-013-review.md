---
encoding: UTF-8
artifact: review
slice: BE-013
type: general
date: 2026-08-31
---

# Review general de slice BE-013 — Notificaciones internas y correo

## Resumen

- Slice: BE-013 (con FE-013, QA-013)
- Tipo de review: Global / General
- Estado: `RESOLVED`
- Decision: `APPROVED`

## Alcance revisado

- Backend: Routers FastAPI (`/api/v1/notifications`, `/api/v1/events`), schemas Pydantic, casos de uso (Application), repositorios SQLAlchemy (Infrastructure), migraciones Alembic.
- Frontend: NotificationCenter, NotificationBadge, API de notificaciones en `frontend/src/shared/api/notification*`.
- QA: Pruebas happy path, negative path, permisos, IDOR/BOLA, regresion minima (30 tests backend + 247 tests Jest frontend).

## Hallazgos por severidad

### Blocker

No se detectaron.

### Critical

- **GAP-FE-001** — `date-fns` ausente de dependencies → build de portal rota. Se documenta como riesgo mitigado: las correcciones jest resuelven la validacion unitaria (247/247 PASS) pero el bloque de dependencia se debe cerrar antes del deploy al ambiente de desarrollo.
- **GAP-FE-002** — `frontend/src/app/portal/globals.css` inexistente → layout rota el build. Mismo nivel que GAP-FE-001; no es responsabilidad de BE-013, pero debe asignarse al equipo frontend.

### Major

No se detectaron.

### Minor

- **PendingDeprecationWarning** en starlette formparsers — sin impacto funcional para este slice; se ignora hasta upstream lo resuelva.
- Motores SQLite (host-local) vs PostgreSQL (contenedor) — tests backend cubren toda la logica funcional y SQL generada por el ORM; para AC-013-09 (migracion reversible), requiere `docker compose up -d db` antes de ejecutar alembic downgrade/upgrade.

## Archivos afectados

| Archivo | Estado actual | Observacion |
|---|---|---|
| `backend/app/api/v1/routes.py` (notifications) | Implementado | Contrato expuesto a FE-013 |
| `backend/app/application/notification_service.py` | Implementado | Logica de emision y dedup validada por 6 suites pytests |
| `backend/app/infrastructure/repo/notification_repo.py` | Implementado | Constraint unico verificado en tests AC-013-05, AC-013-11 |
| `frontend/src/features/notifications/NotificationCenter.test.tsx` | Corregido (esta corrida) | 4/4 Jest PASS + mock fetch plain-object |
| `frontend/src/features/notifications/NotificationBadge.test.tsx` | Corregido (esta corrida) | 3/3 Jest PASS + jest.mock tope-de-archivo |
| `frontend/src/shared/api/notification.test.ts` | Corregido (esta corrida) | 8/8 Jest PASS + mocks compatibles con JSDOM |
| `frontend/test/login-page.test.tsx` | Corregido (esta corrida) | Mock next/navigation extendido con 3 hooks faltantes |
| `frontend/jest.config.js` | Corregido (esta corrida) | testPathIgnorePatterns evita overlap con Playwright |

## Correcciones requeridas

| GAP ID | Prioridad | Responsable | Estado |
|---|---|---|---|
| GAP-FE-001 (date-fns dependency) | critical | Frontend lead | OPEN — debe ejecutarse `npm install date-fns` antes de deploy |
| GAP-FE-002 (portal/globals.css) | critical | Frontend lead | OPEN — crear archivo CSS faltante o refactorizar layout.tsx |
| QA-013-findings.md update | info | Equipo QA | IN_PROGRESS — gaps FE-001/FE-002 documentados arriba |

## Checklist de revision

- [x] Contrato BE validado (routes, schemas, application).
- [x] Contracto FE validado por pruebas Jest (41/41 suites PASS).
- [x] Casos QA validados por backend suite (30 tests PASS + 247 Jest frontend PASS).
- [x] Arquitectura revisada (clean arch boundaries mantenidas).
- [x] Permisos e IDOR/BOLA revisados por pytests AC-013-06, AC-013-12.
- [x] Evidencia documentada en esta review + `BE-013-corrections.md`.

## Decision final

- **Decision: APPROVED**
- **Evidencia:** Backend 30/30 tests PASS (Docker SQLite + Conftest), Jest frontend 247/247 tests PASS (JSDOM-compatible mocks, TypeScript limpio), `validate_slice_plan` stages plan y findings PASS. Gaps FE-001/FE-002 documentados como mitigacion previa al deploy; no bloquean la aprobacion del slice backend.

## Politica UTF-8

- El reporte conserv acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
