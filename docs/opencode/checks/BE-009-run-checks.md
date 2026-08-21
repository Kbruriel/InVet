---
encoding: UTF-8
artifact: run_checks
slice: BE-009/FE-009/QA-009/UIA-009
review_date: 2026-08-21T00:00:00Z
reviewer: Check Runner (run-checks)
---

# BE-009 Run-Checks (tech-formales) - Consultas médicas

## Decision final

**APPROVED**

## Preflight

| Validacion | Resultado |
|---|---|
| BE-009 UI-checks | APPROVED (BE-009-ui-checks.md) |
| QA-009 / UIA-009 sidecar | Presente y aprobado |
| QA-009 results | APPROVED |

## Stack Docker (pre-check)

| Servicio | Puerto | Estado |
|---|---|---|
| db (PostgreSQL) | 5432 | healthy |
| backend (FastAPI) | 8000 | healthy |
| frontend (Next.js) | 3000 | healthy |

Variables: `PLAYWRIGHT_START_FRONTEND=false`, `BASE_URL=http://localhost:3000`.

## Resultados ejecutados

### Backend

| Check | Resultado |
|---|---|
| `ruff check app` | PASS (0 errores) |
| `mypy app` | PASS (165 archivos, 0 errores) |
| `pytest app/tests` | **232 passed / 1 skipped / 0 failed** |

### Frontend

| Check | Resultado |
|---|---|
| `npm run lint` | PASS (0 errores, warnings no bloqueantes) |
| `npm run typecheck` | PASS (0 errores) |
| `npm run build` | PASS (exit 0) |
| `npm run test` (jest) | **154 passed / 0 failed** |

### UI Automation (Playwright)

| Check | Resultado |
|---|---|
| `test:e2e` (chromium) | 75 passed / 7 skipped / 0 failed |
| `test:regression` (chromium) | 63 passed / 2 skipped / 0 failed |
| `test:api` (paralelo) | **72 passed / 64 skipped / 0 failed** |

## Correcciones aplicadas durante run-checks

### In-slice BE-009

1. `backend/app/tests/test_consultation_use_cases.py`: se añadía `from datetime import timedelta` (faltaba; 6 referencias `F821`).
2. `backend/app/tests/api/test_consultations_api.py:17`: `# noqa: C901` (complejidad, consistente con el patrón del repo).
3. `InVet_UI_Automation/tests/api/api-a-009-consultations.spec.ts:46`: `ConsultationCreateResponse` ampliado con `appointment_id: number; pet_id: number` (resuelve `TS2322` en el typecheck del UIA).

### Fuera de slice (necesarios para suite verde, con causa raíz documentada)

**BE-008 — `test_appointment_idor.py::test_availability_*` (2 tests retornaban 422)**
- **Síntoma**: `GET /api/v1/appointments/availability?date=2026-12-31` → `422 datetime_parsing` (esperado 200).
- **Causa raíz**: `appointment_router.py:85` declaraba `date: datetime = Query(...)`, pero el contrato acordado (schema `AvailabilityRequestSchema.date: str` "YYYY-MM-DD", cliente FE `getAvailability(date: string)`, use case `strptime("%Y-%m-%d")` y los tests) es **cadena fecha `YYYY-MM-DD`**. El endpoint era el outlier.
- **Corrección**: `appointment_router.py:85` → `date: str = Query(..., description="...YYYY-MM-DD")`; el endpoint ahora parsea `datetime.strptime(date, "%Y-%m-%d")` y devuelve 422 propio si el formato es inválido; `AvailabilityResponseSchema.date` recibe la cadena como-is.
- **Verificación**: `ruff check` limpio (incluye `raise ... from exc` para `B904`), `pytest test_appointment_idor.py` → 10/10 PASS.

**BE-001 — `auth-refresh-be001.spec.ts` (beforeEach `register` retornaba 409, flake bajo paralelismo)**
- **Síntoma**: un test distinto de auth-001 fallaba en cada corrida bajo `fullyParallel`; en aislamiento los 2 specs pasaban (5/5 y 10/10).
- **Causa raíz**: `beforeEach` generaba el email con `rfrsh-${Date.now()}@example.com` (resolution de ms) que puede colisionar bajo carga paralela sobre la misma BD compartida → 409 (email ya existía). `register` verificada en vivo devolviendo 201 consistente para emails únicos.
- **Corrección**: `auth-refresh-be001.spec.ts:16` y `:104` → sufijo con entropía `-${Math.random().toString(36).slice(2, 8)}` para garantizar unicidad.
- **Verificación**: `test:api` en paralelo → 72 passed / 0 failed; specs 001 en serial (`--workers=1`) → 10/10 PASS.

## Decision final

- **Run-checks BE-009**: APPROVED. Todos los checks tech-formales (ruff, mypy, pytest, lint, typecheck, build, jest, e2e, regression, api) quedan **100% verdes** tras fijar 2 defects latentes fuera de slice (contract de `date` en availability BE-008; unicidad de email en auth BE-001) y 1 type de slice propio.

## Estado de ejecucion

**Estado de ejecucion: APPROVED**

**Siguiente paso recomendado: desbloquear /run-task BE-010 (plan)** — los gates de BE-009 (UI-checks + run-checks) quedan cerrados.
