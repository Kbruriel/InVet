# Final Gate Flow Report — BE-015 / FE-015 / QA-015

**Slice**: US-015 — Reportes operativos básicos
**Date**: 2026-09-08
**Overall Status**: **APPROVED** ✅
**Changelog del cierre**: docs stage reconciliado y aprobado.

---

## Resumen

El slice `BE-015` implementa reportes agregados read-only (appointments, services, pets,
consultations, ratings, payments) por clínica y periodo opcional, con paginación
determinista, autenticación Bearer y control de tenant/BOLA. La capa frontend consume el
contrato desde `/portal/admin/reports`. Todos los gates quedaron verdes y la
documentación fue reconciliada contra checkpoints, plan y reportes.

---

## Gate Flow Summary

| # | Gate | Status | Detalles |
|---|------|--------|---------|
| 1 | Backend implementado (T01–T10) | ✅ PASS | 10 tasks `completed` / `outcome: pass` (`BE-015-backend.json`) |
| 2 | Frontend implementado (FE-015-T01..T05) | ✅ PASS | 5 tasks `completed` / `outcome: pass` (checkpoint `frontend_gate`) |
| 3 | Runtime gate (DB + HTTP real) | ✅ PASS | 6 endpoints 200 autenticado, 401 sin token (`runtime_gate.http`) |
| 4 | Secure-persistence | ✅ PASS | `--stage secure-persistence` → `PASS` |
| 5 | QA-015 | ✅ APPROVED | 129/129 tests BE-015; 32/32 FE; 13 full-suite `ACCEPTED_RISK` (ajenos) (`BE-015-qa.json`) |
| 6 | API Automation (APIA-015) | ✅ PASS | 13/13 `apia015` reports green (C1..C9 + BOLA + LEAK) |
| 7 | UI Automation (UIA-015) | ✅ PASS | 9/9 `ui-automation` green; e2e 112 passed / 7 skipped; regression 100 passed / 2 skipped |
| 8 | Technical checks | ✅ APPROVED | `BE-015-checks.md`: 630 passed/1 skipped, ruff clean (scope), FE build/lint/tsc/test OK |
| 9 | Docs stage (cierre) | ✅ PASS | `--stage docs` → `[PASS] BE-015/FE-015/QA-015 stage=docs` |

---

## Contratos API (endpoint / método / permisos / DTO)

Base path: `/api/v1/reports` (prefix `router.py:41`, `api_v1_router` en `api/main.py:27`).
Todos requieren `Authorization: Bearer <JWT>`; `clinic_id` se deriva **exclusivamente** de la
carga del JWT (no expuesto como query param → BOLA-safe).

| Endpoint | Método | Permisos | Respuesta |
| --- | --- | --- | --- |
| `/api/v1/reports/appointments` | GET | Auth Bearer + clínico con `clinic_id` | `PaginatedResponse[AppointmentSummaryDto]` |
| `/api/v1/reports/services` | GET | Same | `PaginatedResponse[ServiceSummaryDto]` |
| `/api/v1/reports/pets` | GET | Same | `PetCountDto` (conteo activo, flat) |
| `/api/v1/reports/consultations` | GET | Same | `PaginatedResponse[ConsultationSummaryDto]` |
| `/api/v1/reports/ratings` | GET | Same | `PaginatedResponse[RatingSummaryDto]` |
| `/api/v1/reports/payments` | GET | Same | `PaginatedResponse[PaymentSummaryDto]` |

Parámetros comunes: `page`, `size`, `period_start`, `period_end` (ISO-8601, opción).
Errores: `401` sin/Token inválido/expirado; `403` usuario sin `clinic_id`; `422` fechas
inválidas / `size` fuera de rango. Valores de `amount` convertidos de centavos a moneda
(/100.0) en `payments` y `services`.

---

## Componentes frontend

- `frontend/src/features/reports/api.ts` — 6 funciones tipadas sobre `apiClient` de
  `@/shared/api/client`, `BASE_PATH='/reports'`; tipos `PaginatedResponse` / `PetCount` / `RatingsReport`.
- `frontend/src/features/reports/hooks/useReports.ts` — `apply/goToPage/retry` + estados
  `loading/error/data/total/pages/hasMore/isEmpty` + race-guard.
- `frontend/src/features/reports/components/FilterBar.tsx` — `form[role=search]`, select de
  6 tipos + Desde/Hasta + Aplicar/Restaurar, valida `start<=end`.
- `frontend/src/features/reports/components/ReportTable.tsx` — genérica loading/error/empty/
  success + banner Reintentar + paginación.
- `frontend/src/features/reports/report-columns.ts` — `getReportColumns()`.
- `frontend/src/app/portal/admin/reports/page.tsx` — composición `RequireAuth` + `FilterBar` +
  `useReports` + `ReportTable`.
- Reutiliza `Button`/`LoadingSpinner`/`EmptyState` de `src/shared/ui`. No hay `fetch` dispersa
  ni `console.log` de datos sensibles (verificado en `features/reports/**`).

Build (`next build`): `/portal/admin/reports 5.79 kB`, **29/29 páginas**, 0 errores de tipo/ruta.

---

## Variables / permisos / migraciones

- **Variables**: sin variables de entorno nuevas para BE-015 (reportes agregados usan la
  sesión/DB ya configuradas por el stack). `clinic_id` proviene del claim del JWT.
- **Permisos**: todos los endpoints requieren autenticación Bearer; se validan `401`
  (sin/Token inválido/expirado), `403` (sin `clinic_id`) y aislamiento de tenant
  (`test_reports_auth.py` + `test_reports_tenant_isolation.py`).
- **Migraciones**: **sin nueva migración** (BE-015 agregación read-only). Checkpoint
  `runtime_gate.alembic`: `current head = a013`, `be015_new_migrations: 0`; `a014` (support
  tickets) pertenece a BE-014 y queda en el registro propio de carryovers de BE-014.

---

## Trazabilidad AC → evidencia

| AC | Estado | Evidencia principal |
| --- | --- | --- |
| AC-015-01 | CLOSED | Filtro por tipo+fechas/totales — `test_reports_appointments_aggregation.py` + `test_reports_integration.py` |
| AC-015-02 | CLOSED | Paginación — `test_reports_invalid_input.py` (12 pagination 422) + `test_reports_integration.py` |
| AC-015-03 | CLOSED | Citas contrato — `test_reports_appointments_aggregation.py` + `test_reports_router.py` |
| AC-015-04 | CLOSED | Servicios contrato — `test_reports_services_aggregation.py` + `test_reports_router.py` |
| AC-015-05 | CLOSED | Conteo mascotas — `test_reports_pets_count.py` + `test_reports_router.py` |
| AC-015-06 | CLOSED | Consultas contrato — `test_reports_consultations.py` + `test_reports_router.py` |
| AC-015-07 | CLOSED | Ratings promedio — `test_reports_ratings_summary.py` + `test_reports_router.py` |
| AC-015-08 | CLOSED | Pagos/totales — `test_reports_payments.py` + `test_reports_router.py` |
| AC-015-09 | CLOSED | Auth Bearer 401 — `test_reports_auth.py` (12/12) |
| AC-015-10 | CLOSED | 422 tipo/parámetros inválidos — `test_reports_invalid_input.py` (18 period 422) |
| AC-015-11 | CLOSED | IDOR/BOLA — `test_reports_tenant_isolation.py` (12/12) |

---

## Decisiones técnicas y funcionales

- **Orden determinista (QF-015-01, RESOLVED)**: se añadió `id` como segundo criterio de
  orden en cada use-case paginado para eliminar overlap/ausencias al compartir el valor de la
  columna primaria de orden. 5 pruebas de regresión.
- **BOLA-safe por diseño (QF-015-02, RESOLVED)**: `clinic_id` se deriva del JWT en el router
  (no expuesto como query param); el key-mismatch del script QA (`total_active` vs `active_count`)
  se corrigió en `qa_scripts/qa015_verify.py`.
- **Migración no requerida**: BE-015 read-only → 0 migraciones nuevas.
- **`PetCountDto` flat** en `/reports/pets` (conteo) frente a `PaginatedResponse` para los 5
  listados (contrato validado en `test_reports_router.py`).

---

## Riesgos pendientes (fuera de scope BE-015)

| Riesgo | Severidad | Estado | Impacto |
| --- | --- | --- | --- |
| QF-015-03 — 3 fallos full-suite (agencia/planning schema v3 + catálogos) | low | `ACCEPTED_RISK` | Ajenos a reportes/auth/persistencia de BE-015; quedan en el carryover de infraestructura de planning. |
| 47 fallos legacy API automation (APIA-008/009, slice-006, BE-003) | low | debt preexistente | Payloads desactualizados (`date`, `pet_id`, `consulta_general`); **ninguno toca reports/BE-015**. |
| `mypy`: 90 errores preexistentes (Column vs int/str en data repos/usecases) | low | fuera de scope | No bloquea cierre de BE-015. |
| `scripts/verify_a013.py:53` f-string inválida (deuda A-013) | low | fuera de scope | Fuera del slice. |
| C901 en `scripts/manage_slice_task.py` / `validate_agent_catalog.py` | low | fuera de scope | Complejidad preexistente. |

---

## Evidencia resumida (QA + reviews + checks)

### QA
- `QA-015-results.md` → **Decision `APPROVED`**; 129/129 tests BE-015; 32/32 frontend.
- `QA-015-findings.md` → `RESOLVED`: QF-015-01 (RESOLVED), QF-015-02 (RESOLVED), QF-015-03
  (`ACCEPTED_RISK`, justificado y fuera de scope). **Criterios de cierre**: ningún finding
  bloqueante en `OPEN/IN_PROGRESS`.
- `qa_scripts/qa015_verify.py` T01/T02/T03 contra PostgreSQL real → `ok: true`
  (T01 8/8, T02 6/6, T03 6/6). Artefacto `qa_scripts/qa015_results.json`.
- `python backend/scripts/validate_slice_plan.py BE-015 --stage qa` → `PASS`.
- `python backend/scripts/validate_slice_plan.py BE-015 --stage secure-persistence` → `PASS`.

### Reviews
- Functional Review → `APPROVED` (BE-015/FE-015/QA-015 gate flow).
- Security Review → `APPROVED` (findings RESOLVED o ACCEPTED_RISK; 401/403/BOLA cubiertos).
- Clean Architecture Review → `APPROVED` (router sin lógica de negocio, DTO por contexto, sin ORM expuesto).

### Technical checks (`BE-015-checks.md`, Decision `APPROVED`)
- `pytest app/tests -q` → **630 passed, 1 skipped** (tras fix de `reports_pets_dto` +
  `notification_repo.unread` + payload sync).
- `ruff check` → `All checks passed!` (3 C901 preexistentes en scripts, fuera de scope).
- `black --check` → PASS (14 archivos BE-015 formateados).
- Frontend: `npm run test` 53 suites / **302 tests** pass; `npm run lint` PASS; `tsc --noEmit` 0 errors; `next build` OK.
- API Automation (contra Docker): **13/13 APIA-015** green; full API 134 passed / 47 failed (debt legacy).
- UI Automation: UIA-015 9/9 green; e2e 112 passed / 7 skipped; regression 100 passed / 2 skipped.

### Docker (estado al cierre)
- `docker compose up -d --build --force-recreate db backend frontend` → **3 contenedores
  `Up (healthy)`**: `invet-db`, `invet-backend`, `invet-frontend`.
- `python backend/scripts/validate_agent_catalog.py` → `[PASS] Agent catalog: 14 agents, 15 commands, direct execution, payload synchronized.`

---

## Estado de tareas al cierre

- `BE-015.md` (task backend): **6/6 DoD `[x]`**.
- `FE-015.md` (task frontend): **6/6 DoD `[x]`** (ya cerradas: Rutas, Componentes, Estados UX, Validaciones, Consumo API, Sin alcance).
- `QA-015.md` (task QA): **6/6 DoD `[x]`**.
- `BE-015-plan.md`: `status: PLANNED → COMPLETED`; trazabilidad AC-015-01..11 → `CLOSED`; Pruebas QA AC-015-01..11 → `CLOSED`.
- `02_be_fe_qa_task_matrix.md`: slice 015 Estado → `APPROVED`.
- Sin tareas abiertas `- [ ]` aplicables a BE-015 en `docs/opencode/tasks/*`.
- Sin `CANCELLED` sin evidencia verificable en los 5 manifiestos BE-015.

## Changelog del slice (docs)

1. Restaurado `QA-015-findings.md` al contenido íntegro (QF-015-01/02/03 + Criterios de cierre) — la copia de trabajo estaba truncada (15 líneas).
2. `BE-015-plan.md`: frontmatter `status: PLANNED → COMPLETED`; matriz de trazabilidad AC-015-01..11 → `CLOSED`; tabla Pruebas QA AC-015-01..11 → `CLOSED` con los ficheros reales de prueba.
3. `BE-015.md` (task): DoD 6/6 cerrada con evidencia + bloque de evidencia de cierre.
4. `QA-015.md` (task): DoD 6/6 cerrada con evidencia + bloque de evidencia de cierre.
5. `02_be_fe_qa_task_matrix.md`: slice 015 Estado `APPROVED`.
6. **Reconciliation de checkpoints**: se reconstruyó `docs/opencode/checkpoints/BE-015-qa.json` (layer `qa`, QA-015-T01/T02/T03) a partir de `BE-015-backend.json#qa_gate` + `QA-015-results.md` para completar el set canónico 5/5 (`backend`, `frontend`, `qa`, `api-automation`, `ui-automation`).
7. Este report (`BE-015-report.md`) como cierre de gate-flow.

## Final Status

```text
Estado de ejecucion: APPROVED
Siguiente paso recomendado: Release BE-015/FE-015/QA-015 a staging
Motivo: all gates passed, all findings RESOLVED/ACCEPTED_RISK, documentation reconciled
```

**Slice US-015 is COMPLETE and ready for release.**
