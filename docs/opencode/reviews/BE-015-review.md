# BE-015 - Revisión funcional del slice de reportes operativos

**Slice:** BE-015 / FE-015 / QA-015  
**Fecha:** 2026-09-03  
**Revisor:** InVet Slice Reviewer  

---

## Resumen ejecutivo

El slice BE-015 (reportes operativos) implementa seis endpoints GET agregados bajo `/api/v1/reports/*` para citas, servicios, mascotas, consultas, calificaciones y pagos. La capa aplicación (`app/application/usecases/reports/`) concentra los casos de uso; el router (`app/api/v1/routers/reports_router.py`) es delgado y solo valida entrada + resuelve `clinic_id` desde JWT + delega. El frontend (`frontend/src/features/reports/*` + `frontend/src/app/portal/admin/reports/`) compone `FilterBar` + `useReports` + `ReportTable` con estados loading/error/empty/success y paginación.

- Backend: 124/124 tests de reports + 8 suites en Docker contra PostgreSQL real (evidencia cerrada en BE-015-checkpoint).
- Frontend: `npx tsc --noEmit` limpio; `npx eslint` limpio; `npx jest` → 53 suites / 302 tests PASS (incluye 32 de FE-015).
- Gate BE/secure-persistence: `PASS`.
- QA-015: `APPROVED` (evidencia en `docs/opencode/reports/`).

El slice no introduce migración nueva (solo agregados sobre slices 008-012) ni nuevos models ORM. `clinic_id` se deriva del JWT (tenant isolation) y no es aceptado como query param, lo que elimina IDOR/BOLA en todos los endpoints.

## Hallazgos por severidad

| # | Severidad | Descripción | Estado |
|---|-----------|-------------|--------|
| F1 | Minor — Los schemas `RatingsReportResponse` y `PaymentsReportResponse` se definen en `reports_router.py` en vez de `app/api/v1/schemas/report_schemas.py`. La razón es que estos dos endpoints agregan campos propios (`clinic_avg`, `total_amount`) fuera del patrón `PaginatedResponse`, y no fue necesario agregar un módulo de schemas. | Sin impacto funcional — solo de consistencia. Los contratos expuestos (OpenAPI) son correctos. Se documenta sin corrección obligatoria. | Aceptado |
| F2 | Minor — Los casos de uso en `app/application/usecases/reports/*.py` importan directamente ORM (`from app.infrastructure.database.models.appointment import Appointment`). El slice no introduce un puerto de repositorio; el patrón de "consulta de reporte" se resolvió con query SQLAlchemy directo en application. | Sin impacto funcional: read-only agregado; sin side effects; todas las queries filtran por `clinic_id`. Patrón aceptado para este slice; no se requiere refactor en MVP. Se deja documentado para futuras mejoras. | Aceptado |
| F3 | Info — `report_appointments` devolve `PaginatedResponse[dict[str, Any]]` (no `[AppointmentSummaryDto]`, como sugiere el return-type). En tiempo de ejecución el contenido es `AppointmentSummaryDto`; el `# type: ignore` en el router cubre la diferencia. | Sin impacto en runtime (FastAPI serializa vía Pydantic `response_model`). El tipo estático difiere; no afecta el API público. | Cierre sin acción |
| F4 | Info — `_db()` envuelve `app.infrastructure.database.session.get_db` en un local-import + `yield from` para desacoplar el import del router. Patrón aceptado (no hay cíclico import) pero inusual. | Sin riesgo de seguridad ni funcional. | Cierre sin acción |

No se identificaron hallazgos **High**, **Critical** ni bloqueantes.

## Archivos afectados por el slice

| Archivo | Capa | Propósito |
|---------|------|-----------|
| `backend/app/api/v1/routers/reports_router.py` | BE | 6 endpoints GET bajo `/reports/*` + schemas `RatingsReportResponse` / `PaymentsReportResponse`. |
| `backend/app/api/v1/schemas/report_schemas.py` | BE | `PaginatedResponse[T]`, `AppointmentSummaryDto`, `ServiceSummaryDto`, `ConsultationSummaryDto`, `PetCountDto`. |
| `backend/app/application/usecases/reports/report_appointments.py` | BE | Caso de uso: citas paginados por clínica + periodo. |
| `backend/app/application/usecases/reports/report_services.py` | BE | Caso de uso: servicios realizados paginados. |
| `backend/app/application/usecases/reports/report_pets_count.py` | BE | Caso de uso: conteo de mascotas activas. |
| `backend/app/application/usecases/reports/report_consultations.py` | BE | Caso de uso: consultas paginados. |
| `backend/app/application/usecases/reports/report_ratings_summary.py` | BE | Caso de uso: calificaciones por veterinario. |
| `backend/app/application/usecases/reports/report_payments.py` | BE | Caso de uso: pagos + suma de monto del periodo. |
| `backend/app/tests/integration/test_reports_router.py` | QA-API | Contrato HTTP: 200, shapes, 401/422. |
| `backend/app/tests/integration/test_reports_auth.py` | QA-API | AuthN Bearer en 6 endpoints. |
| `backend/app/tests/integration/test_reports_tenant_isolation.py` | QA-API | IDOR/BOLA: clinic_id del JWT; sin filtrar por query. |
| `backend/app/tests/integration/test_reports_integration.py` | QA-integration | E2E con datos de prueba controlados. |
| `backend/app/tests/integration/test_reports_invalid_input.py` | QA-API | 422 para dates inválidos / page/size límites. |
| `backend/app/tests/usecases/test_reports_schemas.py` | QA-UC | Schemas Pydantic y paginación. |
| `backend/app/tests/usecases/test_reports_appointments_aggregation.py` | QA-UC | Happy path + negative path cita. |
| `backend/app/tests/usecases/test_reports_services_aggregation.py` | QA-UC | Happy path + negative path servicio. |
| `backend/app/tests/usecases/test_reports_pets_count.py` | QA-UC | Happy path + negative path mascota. |
| `backend/app/tests/usecases/test_reports_consultations.py` | QA-UC | Happy path + negative path consulta. |
| `backend/app/tests/usecases/test_reports_ratings_summary.py` | QA-UC | Happy path + negative path calificaciones. |
| `backend/app/tests/usecases/test_reports_payments.py` | QA-UC | Happy path + negative path pagos + `total_amount`. |
| `frontend/src/features/reports/api.ts` | FE | Cliente API tipado para los 6 endpoints. |
| `frontend/src/features/reports/api.test.ts` | FE | 5 tests: shape response y propagación de filtros. |
| `frontend/src/features/reports/hooks/useReports.ts` | FE | Hook central de estados (loading/error/data/pagination/retry). |
| `frontend/src/features/reports/hooks/useReports.test.ts` | FE | 9 tests: no-fetch on mount, race-guard, retry, boundaries. |
| `frontend/src/features/reports/components/FilterBar.tsx` | FE | Form `[role=search]` con tipo + fechas + validación start<=end. |
| `frontend/src/features/reports/components/FilterBar.test.tsx` | FE | 6 tests: 6 opciones, submit, rechazo start>end, resta. |
| `frontend/src/features/reports/components/ReportTable.tsx` | FE | Tabla genérica con estados + paginación + Reintentar. |
| `frontend/src/features/reports/components/ReportTable.test.tsx` | FE | 8 tests: tabla, loading/error/empty, paginación, onRetry. |
| `frontend/src/features/reports/report-columns.ts` | FE | Mapper `ReportType` → `{title, columns, getRows}`. |
| `frontend/src/app/portal/admin/reports/page.tsx` | FE | Página `/portal/admin/reports` que compone FilterBar + hook + tabla. |
| `frontend/src/app/portal/admin/reports/page.test.tsx` | FE | 5 tests: header, placeholder, datos, submit, retry. |

## Correcciones requeridas

No hay correcciones bloqueantes. Los hallazgos F1-F4 son observaciones menores aceptadas:
- F1: Documentado como decisión de consistencia aceptable en MVP; se puede refactorizar en un slice posterior.
- F2: Patrón aceptado para read-only; documentado.
- F3/F4: Cierre sin acción.

## Checklist de revisión

- [x] `validate_slice_plan.py BE-015 --stage backend` → PASS
- [x] `validate_slice_plan.py BE-015 --stage secure-persistence` → PASS
- [x] `validate_slice_plan.py BE-015 --stage review` → PASS (con este documento)
- [x] `npx tsc --noEmit` en frontend → sin errores
- [x] `npx eslint` en features/reports + page → sin errores
- [x] `npx jest` (todo frontend) → 53 suites / 302 tests PASS
- [x] 124 tests backend de reportes pasando en Docker contra PG real (evidencia BE-015)
- [x] Tenant isolation: `clinic_id` derivado del JWT en el 6/6 endpoints (no se expone query param); pruebas en `test_reports_tenant_isolation.py`
- [x] AuthN Bearer: 401 sin token (pruebas `test_reports_auth.py`)
- [x] 422 para period_start > period_end + formato inválido (pruebas `test_reports_invalid_input.py`)
- [x] OpenAPI expone los 6 endpoints bajo `/api/v1/reports/*` con `response_model` Pydantic correctos
- [x] Frontend: rutas `/portal/admin/reports` protegida por `RequireAuth` (auth + redirect `/login`)
- [x] Frontend: `useReports` no dispara fetch en mount; solo tras `apply()` (verificados en tests)
- [x] Frontend: Estados loading / error + Reintentar / empty / success cubiertos (verificados en tests)
- [x] Frontend: cambio de página invoca `goToPage` sin perder filtros (verificado en tests)
- [x] No hay carryovers abiertos para BE/FE/QA-015
- [x] UTF-8 declarado en todos los reportes; sin mojibake `Ã`, `Â`, `â`

## Decision final

El slice BE-015 cumple con todos los criterios de aceptación (AC-015-01..AC-015-09), el aislamiento por tenant es probado, la paginación funciona, los estados UX están cubiertos, y no hay hallazgos bloqueantes.

- Decision: APPROVED

---

## Siguiente paso recomendado

1. `/clean-architecture-review BE-015` — Revisión de la separación de capas y del patrón read-only en application.
2. Si la arquitectura es `APPROVED`, continuar por: `/security-review BE-015` → `/run-checks BE-015` → `/update-docs BE-015` → `/final-gate BE-015`.
