# BE-015 / FE-015 — Verificacion de contrato frontend vs `Develop`

- **Autor:** agente frontend (lane FE-015).
- **Alcance:** verificar que el frontend FE-015 consume un contrato estable
  (`/api/v1/reports/*`) y que **su capa no depende de la estructura interna
  del backend**. No toca backend ni empuja.
- **Comparado contra:** `origin/Develop` (fetch hecho). Base de trabajo: rama `BE-003`.
- **Fecha:** 2026-09-04.

## Veredicto

**EL CONTRATO HTTP DE FE-015 ESTÁ ALINEADO** con lo que la rama de trabajo
(`BE-003`) expone y **no introduce acoplamiento a la interna del backend**.
FE-015 solo fija: (1) 6 rutas `/reports/{segmento}`, (2) auth por `Bearer JWT`,
(3) query params opcionales `period_start|period_end|page|size`, (4) DTOs.

**RIESGO DE INTEGRACIÓN (no de FE-015):** `origin/Develop` **NO contiene aún**
`reports_router` ni la carpeta `backend/app/api/v1/routers/`. Todo el backend de
reportes (routers + usecases en `application/usecases/reports/` + schemas) es
nuevo e introducido por `BE-003`. Si `Develop` avanza con la refactorización
clean-architecture que trae (nueva estructura `infrastructure/`, `domain/`,
container DI), el **backend** de BE-015 puede necesitar realineación de imports/
DI al integrarse. Eso es trabajo del **agente backend**, no del frontend: la
camada FE-015 (paths, auth, DTO) permanece válida mientras esos endpoints se
mantengan.

## Evidencia por ítem

### 1) Rutas (paths) — 6 segmentos
`frontend/src/features/reports/api.ts` fija `BASE_PATH = '/reports'` y 6 funciones:

| Endpoint FE-015 | Función exportada |
|---|---|
| `GET /api/v1/reports/appointments` | `listAppointmentsReport` |
| `GET /api/v1/reports/services` | `listServicesReport` |
| `GET /api/v1/reports/pets` | `getPetsCountReport` |
| `GET /api/v1/reports/consultations` | `listConsultationsReport` |
| `GET /api/v1/reports/ratings` | `listRatingsReport` |
| `GET /api/v1/reports/payments` | `listPaymentsReport` |

Contraparte backend en `BE-003`:
`backend/app/api/v1/router.py` → `router.include_router(reports_router, prefix="/reports")`.
Los 6 métodos existen en `reports_router.py` (`@router.get("/appointments|/services|/pets|/consultations|/ratings|/payments")`).

✅ Match 1:1 entre paths del frontend y del backend de la rama de trabajo.

### 2) Auth por JWT (tenant isolation)
- `frontend/src/shared/api/client.ts` → `buildHeaders()` inyecta
  `Authorization: Bearer <token>` leyendo `getAccessToken()` de `@/shared/auth/session`.
- `backend/app/api/v1/routers/reports_router.py` → cada endpoint depende de
  `get_current_access_user` (tenant isolation por `clinic_id` derivado del JWT);
  el **frontend NUNCA envía `clinic_id` en el body/query** (verificado en `api.ts`).

✅ Contract "JWT solo + clinic_id por backend" cumple la política de
tenant isolation. FE-015 no expone `clinic_id` por parámetro.

### 3) Query params opcionales
`buildQuery()` en `api.ts` emite solo `period_start`, `period_end`, `page`, `size`
cuando están definidos. `FilterBar` (FE-015-T03) valida `period_start <= period_end`.

✅ Params opcionales. Sin `clinic_id`. Sin `page`/`size` para `pets` y `ratings`
(por diseño de esos endpoints: conteo por periodo y agregado por veterinario).

### 4) DTOs (cámaras de respuesta)
Tipos TS declarados en `api.ts`: `AppointmentSummary`, `ServiceSummary`,
`PetCount`, `ConsultationSummary`, `RatingSummary`, `RatingsReport`,
`PaymentSummary`, `PaymentsReport`, `Paginated<T>`.

Contraparte Pydantic: `backend/app/api/v1/schemas/report_schemas.py`
(`AppointmentSummaryDto`, `ServiceSummaryDto`, `PetCountDto`,
`ConsultationSummaryDto`, `ServiceRatingSummaryDto`, `RatingsReportDto`,
`PaymentSummaryDto`, `PaginatedResponse`).

✅ Nombres y formas alineadas. `clinic_id` aparece en `AppointmentSummary`,
`ServiceSummary`, `PetCount`, `ConsultationSummary`, `PaymentSummary` como dato
informativo retornado por el backend; no es input.

### 5) `api-base.ts` — dependencia de infra del frontend
`frontend/src/shared/api/api-base.ts` **no está en `origin/Develop`** (verificado
con `git ls-tree -r origin/Develop -- frontend/src/shared/` vacío).

- Es introducida por `BE-003` (commit que la agrega; ya versionada en el repo).
- **No es una tarea FE-015**, pero es una **dependencia** de todo el frontend.
- `Develop` **no tiene `frontend/` completo** (no tiene `frontend/src/shared/`)
  → todo el frontend (incl. `api-base.ts`) es netamente nuevo respecto a `Develop`.

✅ FE-015 **no rompe** nada en `Develop`. Su dependiente `api-base.ts` es nuevo
y compartido por todo el frontend de `BE-003`.

## Hallazgos de acción

| # | Nivel | Hallazgo | Acción |
|---|---|---|---|
| H1 | **Backend (lane agente BE)** | `origin/Develop` no tiene `reports_router` ni `application/usecases/reports/`. Si `Develop` avanza con clean-architecture, el **backend** de BE-015 puede necesitar realineación de imports/structure al integrarse. | Agente backend verificar imports (`reports_router.py`, `report_*.py`, `report_schemas.py`) contra `origin/Develop` y rebase/rewrite si aplica. |
| H2 | **Frontend (este agente)** | FE-015 solo consume paths, JWT y DTOs: **contrato estable** mientras el backend mantenga los 6 endpoints y sus formas. | Ninguna. FE-015 no requiere cambios. |
| H3 | **Integración** | `BE-003` trae el **frontend completo** (no solo FE-015) y varios slices. El PR `BE-003 → Develop` ingresará 43 commits. | Decisión de alcance del orchestrator: PR a `Develop` vs rama intermedia. |

## Criterios de cierre de esta verificación (auto-lane FE-015)

- [x] No tocar backend.
- [x] No empujar.
- [x] Confirmar 6 paths FE-015 ↔ 6 paths backend (match 1:1).
- [x] Confirmar auth Bearer + absence de `clinic_id` en query.
- [x] Confirmar params opcionales y DTOs alineada.
- [x] Confirmar `api-base.ts` como dependencia frontend nueva (no rompe `Develop`).
- [x] Hallazgo H1 derivado a agente backend con evidencia de `git ls-tree`.
- [x] Evidencia reproducible registrada en este documento.

Repro:
```
# paths: Develop no trae report_schemas ni routers reports
git ls-tree -r origin/Develop --name-only | Select-String "reports"     # (vacío)

# paths: BE-003 trae reports_router con prefix=
git show HEAD:backend/app/api/v1/router.py | Select-String "reports"    # prefix="/reports"

# auth: client.ts inyecta Bearer y no expone clinic_id
Select-String -Path frontend/src/shared/api/client.ts -Pattern "Authorization|Bearer"

# FE-015 build + tests
cd frontend; npx tsc --noEmit            # exit=0 (clean)
cd frontend; npx jest --testPathPattern='features/reports|app/portal/admin/reports'  # 32/32 PASS, 5/5 suites
```

## Verificación ejecutada (auto-lane FE-015)

| Check | Resultado |
|---|---|
| `npx tsc --noEmit` (frontend) | ✅ exit=0 |
| `npx jest --testPathPattern='features/reports\|app/portal/admin/reports'` | ✅ 5 suites / **32/32 tests PASS** |
| `git ls-tree -r origin/Develop --name-only | Select-String "reports"` | vacío → `Develop` **no** trae `reports_router` |
| `git show HEAD:backend/app/api/v1/router.py` (BE-003) | trae `reports_router` con `prefix="/reports"` + 6 endpoints |
| Contrato HTTP FE-015 (6 paths + JWT + DTOs) | **ALINEADO** |
