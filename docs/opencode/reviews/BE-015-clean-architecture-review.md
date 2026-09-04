---
encoding: UTF-8
artifact: review_clean_architecture
slice: BE-015
aliases: [FE-015]
type: clean-architecture
date: 2026-09-03
estado: APPROVED
decision: APPROVED
---

# Revisión de arquitectura limpia para slice BE-015 — Reportes operativos

## Normalización y agente ejecutor

El índice vertical es `BE-015`. Este gate valida la separación de capas y la
aplicación correcta del patrón limpio sobre el deliverable de reportes, sin
modificar código de producto.

Comandos reproducibles desde `C:\InVet`:

```powershell
python backend/scripts/validate_slice_plan.py BE-015 --stage backend
python backend/scripts/validate_slice_plan.py BE-015 --stage secure-persistence
python backend/scripts/validate_slice_plan.py BE-015 --stage review
npx tsc --noEmit    # en frontend/
npx jest src/features/reports src/app/portal/admin/reports
```

## Evidencia ejecutada

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Validación backend (plan) | PASS | `validate_slice_plan.py BE-015 --stage backend` |
| Validación persistencia segura | PASS | `validate_slice_plan.py BE-015 --stage secure-persistence` |
| Gate review | PASS (al escribir este doc) | `validate_slice_plan.py BE-015 --stage review` |
| Backend tests | PASS | 124 tests de reportes en Docker contra PG real (evidencia BE-015) |
| Frontend typecheck | PASS | `npx tsc --noEmit` (frontend) sin errores |
| Frontend lint | PASS | `npx eslint` sobre `features/reports` + `app/portal/admin/reports` sin errores |
| Frontend tests | PASS | `npx jest` → 53 suites / 302 tests; 32 de FE-015 |

## Arquitectura de dominio aplicada

### Capa API (HTTP)

- `backend/app/api/v1/routers/reports_router.py` — Router delgado: valida
  entrada (`period_start`, `period_end`, `page`, `size`), resuelve
  `clinic_id` del JWT vía `_clinic_id_from(current_user)`, y delega el negocio
  a `app.application.usecases.reports`.
- Schemas Pydantic en `backend/app/api/v1/schemas/report_schemas.py` para los
  DTOs comunes (`AppointmentSummaryDto`, `ServiceSummaryDto`,
  `ConsultationSummaryDto`, `PetCountDto`, `PaginatedResponse[T]`).
- Los schemas `RatingsReportResponse` y `PaymentsReportResponse` se declaran
  inline en el router porque agregan campos propios (`clinic_avg`,
  `total_amount`) sobre el patrón `PaginatedResponse`. Decisión documentada en
  `BE-015-review.md` (hallazgo F1).

### Capa aplicación

- `backend/app/application/usecases/reports/report_appointments.py`
- `backend/app/application/usecases/reports/report_services.py`
- `backend/app/application/usecases/reports/report_pets_count.py`
- `backend/app/application/usecases/reports/report_consultations.py`
- `backend/app/application/usecases/reports/report_ratings_summary.py`
- `backend/app/application/usecases/reports/report_payments.py`

Los casos de uso son **read-only** (sin side effects). Filtran por
`clinic_id` (tenant), `period_start/end`, y aplican paginación. Devuelven
DTOS Pydantic (no ORM) al router.

### Capa infraestructura

- **No se crean modelos ORM ni migración nueva** (los reportes agregan sobre
  slices 008-012).
- Se reutilizan los modelos ya existentes de citas, servicios, mascotas,
  consultas y ratings.

### Capa frontend (Next.js)

- **App Router**: `frontend/src/app/portal/admin/reports/page.tsx` compone la
  página `/portal/admin/reports` (privada, `RequireAuth`).
- **Feature**: `frontend/src/features/reports/`
  - `api.ts` — Cliente HTTP tipado (6 funciones) sobre `apiClient`.
  - `hooks/useReports.ts` — Hook central de estados (loading/error/data/total/
    page/size/pages/hasMore/isEmpty + `apply`, `goToPage`, `retry` +
    race-guard por `requestId`).
  - `components/FilterBar.tsx` — Form `[role=search]` con selector de tipo y
    rango de fechas + validación start<=end.
  - `components/ReportTable.tsx` — Tabla genérica con estados
    loading/error/empty/success + paginación.
  - `report-columns.ts` — Mapper `ReportType → {title, columns, getRows}`.
- **Shared**: `RequireAuth`, `Button`, `LoadingSpinner`, `EmptyState`,
  `apiClient` (ya disponibles).

## Separación de responsabilidades

| Capa | Responsabilidad | Cumplimiento |
|---|---|---|
| API router | HTTP, validación, auth, mapeo a aplicación | ✓ Sin lógica de negocio |
| Use-case (application) | Reglas de reporte, paginación, filtros | ✓ Sin dependencia directa de FastAPI |
| Schemas Pydantic | Contratos HTTP (request/response) | ✓ Separados del ORM |
| Infraestructura | ORM, sesión de BD | ✓ Aislado detrás de `get_db` (inmutada) |
| Frontend feature | UI, estado, clientes API | ✓ Sin acceso HTTP ad hoc (usa `api.ts`) |
| Frontend shared | Autenticación, UI primitivas | ✓ Reutilizado |

## Hallazgos de arquitectura

| # | Severidad | Descripción | Acción |
|---|---|---|---|
| CA-01 | **Info** — Los use-cases reportes importan modelos ORM directamente. Patrón aceptado para read-only agregados; no se introduce puerto de repositorio. | Documentado; sin refactor en MVP. |
| CA-02 | **Info** — Schemas de rating y payment agregan campos propios al patrón `PaginatedResponse`. Alineación con `report_schemas.py` pendiente de futuro slice. | Documentado en BE-015-review.md F1. |
| CA-03 | **Info** — `_db()` envuelve `get_db` para evitar import en el router. Patrón aceptado. | Documentado en BE-015-review.md F4. |

## Checklist de arquitectura

- [x] Routers delgados: validación de entrada + auth + delegación a application.
- [x] Casos de uso en `application`; reglas de filtro/paginación en use-cases.
- [x] Schemas Pydantic en `api/v1/schemas/report_schemas.py` (y los inline
      para ratings/payments, documentado).
- [x] No hay migración nueva: se reutilizan los modelos de slices 008-012.
- [x] `clinic_id` derivado del JWT en todos los endpoints (tenant isolation).
- [x] Frontend con feature compartida, hook de estado, tabla genérica reutilizable.
- [x] Sin acceso HTTP ad hoc: `api.ts` centraliza.
- [x] Evidencia de pruebas trazada a AC-015.

## Estado de ejecución

**APPROVED** — La arquitectura del slice es coherente, las capas están bien
separadas, no hay dependencias inversas entre capas, y los contratos están
alineados con el plan del slice.

## Siguiente paso recomendado

Ejecutar `/security-review BE-015` con el agente `invet-security-reviewer` y
después `/run-checks BE-015` → `/update-docs BE-015` → `/final-gate BE-015`.

- Decision: APPROVED
