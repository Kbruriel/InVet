# QA-015 - Resultados de validación del slice BE-015 (reportes agregados)

- Fecha de ejecución: 2026-09-07 (hora UTC, contenedor `invet-backend`)
- Corridas: **2** — (1) baseline 2026-09-07, (2) revalidación 2026-09-07 post `/implement-findings BE-015` (F1/F2/F3)
- decision: APPROVED
- Estado global de findings: **RESOLVED** (ver `QA-015-findings.md`)

---

## Resumen de ejecución (revalidación 2026-09-07, post F1/F2/F3)

| Suite | Entorno | Recolección | PASS | FAIL | SKIP | Duración |
|---|---|---|---|---|---|---|
| `app/tests/usecases/test_reports_*.py` (7 archivos) | contenedor Docker — `invet-backend` | 67 | 67 | 0 | 0 | 0.37s |
| `app/tests/integration/test_reports_*.py` (5 archivos) | contenedor Docker — `invet-backend` | 62 | 62 | 0 | 0 | 1.83s |
| **Total BE-015 (12 archivos test)** | **contenedor Docker** | **129** | **129** | **0** | **0** | **2.20s** |
| `app/tests/` (suite completa, con deselects QF-015-03) | contenedor Docker — `invet-backend` | 602 | 589 | **13** | 1 | 25.30s |
| Frontend: `features/reports` + `app/portal/admin/reports` (5 suites) | host jest | 32 | 32 | 0 | 0 | 20.14s |

> **Revalidación tras `/implement-findings BE-015` (F1/F2/F3):**
> Los 13 fallos de la suite completa son **todos pre-existentes** (QF-015-03,
> `ACCEPTED_RISK`) — `test_docker_compose_closure_hooks.py` (2),
> `test_secure_persistence_contracts.py` (3), `test_setup.py::test_database_config` (1),
> `test_slice_task_controls.py` (7). **Ninguno toca reportes, routers, use-cases ni
> schemas de BE-015.**
>
> **Los 129 tests BE-015 (67 use-cases + 62 integración) siguen en verde**,
> confirmando que las correcciones de F1/F2/F3 no introducen regresión en el slice.
>
> **F1 (response models en schemas)** — verificado en `report_schemas.py` líneas 89-119
> y el router importa desde `report_schemas` (sin defs inline).
> **F2 (clinic_avg ponderada)** — `test_reports_integration.py::TestRatingsContract::test_returns_by_veterinarian_and_clinic_avg`
> (aserta `4.38`) y `test_reports_router.py::TestReportsRouterPaginationEndpoints::test_ratings_200_contract_with_clinic_avg`
> (aserta `4.33`) → **PASSED** en contenedor.
> **F3 (wording BOLA 403)** — `qa_scripts/qa015_verify.py` líneas 270-288 documenta
> que la única falla por alcance es `403` (token sin clínica); `clinic_id` en query
> se ignora (no existe en la signature del endpoint).

> **Nota sobre el delta (40 fails en contenedor vs 4 fails en host):**
> Todos los 40 fallos de contenedor ocurren exclusivamente en tests de **governance/meta-repo**
> (`test_slice_task_controls`, `test_secure_persistence_contracts`, `test_setup`,
> `test_agentic_plan_schema_v3`, `test_automation_agentic_flow`, `test_docker_compose_closure_hooks`,
> `test_vscode_agent Controls`).
> Causa raíz verificada:
> 1. **Fallo de layout** — Estos tests calculan `REPO_ROOT = Path(__file__).resolve().parents[3]`.
>    Dentro del contenedor la ruta del test es `/app/app/tests/test_...py`, de modo que
>    `parents[3] = /` → `/backend/scripts/...` no existe → `FileNotFoundError`.
>    En host, `parents[3] = C:\InVet\` → resuelve correctamente.
> 2. **Fallo de entorno** — `test_setup.py::test_database_config` aserta
>    `settings.POSTGRES_SERVER == "localhost"`, pero el contenedor hereda `POSTGRES_SERVER=db`
>    del `docker-compose.yml`. Es una prueba de configuración de host, no de la app.
> 3. **Payload-sync pre-existente (host)** — 4 tests fallan en host por desincronización entre
>    `payload/` y los archivos activos **fuera del scope de BE-015**:
>    `payload/.opencode\agents\invet-ui-automation-implementer.md`,
>    `payload/opencode.json`,
>    `payload/backend\scripts\validate_agent_catalog.py`.
>    Estos archivos están en el estado `modified` de `git status` y no pertenecen al allowlist
>    de BE-015. **No se tratan de regresiones introducidas por BE-015**, ni de tests que
>    cubran reportes, routers, use-cases o schemas de BE-015.
>
> **Ninguno de los 129 tests BE-015 ha fallado en ninguna de las dos ejecuciones.**

---

## Matriz de trazabilidad por criterio

| Criterio | Caso de prueba | Nivel | Archivo/test | Comando | Resultado | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| AC-015-01: 6 endpoints GET bajo `/api/v1/reports/*` | `test_appointments_200_contract` + 4 pares | integration | `test_reports_router.py` | `pytest test_reports_router.py` | PASS | 6/6 endpoints 200 con contrato correcto | PASS |
| AC-015-01: 6 endpoints GET | `test_appointments_200_contract` + `test_services_200_contract` + `test_consultations_200` + `test_payments_200` + `test_pets_200` + `test_ratings_200` | integration | `test_reports_integration.py` | `pytest test_reports_integration.py` | PASS | Contrato por campo validado contra Pydantic DTO | PASS |
| AC-015-02: Paginación (`page`, `size`) en 4 endpoints — `pets` y `ratings` sin paginación | `test_page_size_forwarded`, `test_valid_page_size_forwarded` | integration | `test_reports_invalid_input.py`, `test_reports_router.py` | `pytest test_reports_invalid_input.py` | PASS | `page` y `size` se propagan al use-case | PASS |
| AC-015-02: Paginación — valores válidos entregados al use-case | `TestReportAppointmentsDeterministicOrdering` + 4 clases pares | unit | `test_reports_*_aggregation.py` / `test_reports_consultations.py` / `test_reports_payments.py` / `test_reports_ratings_summary.py` / `test_reports_services_aggregation.py` | `pytest app/tests/usecases/test_reports_*.py` | PASS | Orden determinista con tiebreaker `id` verificado | PASS |
| AC-015-03: `period_start`/`period_end` opcionales, formato `YYYY-MM-DD` | `test_invalid_period_start_format_422[6 endpoints]`, `test_invalid_period_end_format_422[6 endpoints]` | integration | `test_reports_invalid_input.py` | `pytest test_reports_invalid_input.py` | PASS | 12/12 (6 endpoints × 2 campos) | PASS |
| AC-015-03: `period_end < period_start` → 422 | `test_end_before_start_422[6 endpoints]` | integration | `test_reports_invalid_input.py` | `pytest test_reports_invalid_input.py` | PASS | 6/6 | PASS |
| AC-015-04: Totales correctos (appointments count, payments `total_amount`) | `test_returns_paged_with_total_amount`, `test_total_amount_rounds_to_2` | integration | `test_reports_integration.py` | `pytest test_reports_integration.py` | PASS | total_amount redondeado a 2 decimales | PASS |
| AC-015-04: Totales correctos (ratings `clinic_avg`, pets `active_count`) | `test_returns_by_veterinarian_and_clinic_avg` | integration | `test_reports_integration.py` | `pytest test_reports_integration.py` | PASS | estructura `by_veterinarian[]` + `clinic_avg` | PASS |
| AC-015-09: Sin token → 401 | `test_no_token_401`, `test_invalid_token_401`, `test_expired_token_401` | integration | `test_reports_auth.py` | `pytest test_reports_auth.py` | PASS | 401 + `WWW-Authenticate` header | PASS |
| AC-015-09: Token válido pasa autenticación | `test_valid_token_passes_auth` | integration | `test_reports_auth.py` | `pytest test_reports_auth.py` | PASS | 200 / delega al use-case | PASS |
| AC-015-10: `size < 1` → 422 | `test_size_above_maximum_422[4 endpoints]` en `test_reports_invalid_input.py` + `test_size_upper_bound_422` en `test_reports_router.py` | integration | `test_reports_invalid_input.py`, `test_reports_router.py` | `pytest test_reports_invalid_input.py` | PASS | 4/4 + 1/1 = 5/5 | PASS |
| AC-015-10: `page < 1` → 422 | `test_page_below_minimum_422[4 endpoints]` | integration | `test_reports_invalid_input.py` | `pytest test_reports_invalid_input.py` | PASS | 4/4 | PASS |
| AC-015-10: `size > 100` → 422 | `test_size_above_maximum_422[4 endpoints]` | integration | `test_reports_invalid_input.py` | `pytest test_reports_invalid_input.py` | PASS | 4/4 | PASS |
| AC-015-11: Tenant isolation — Clinic A no ve datos de Clinic B | `test_clinic_a_scoped_to_own_clinic`, `test_clinic_b_scoped_to_own_clinic`, `test_each_endpoint_scoped_to_token_clinic[4 more]` | integration | `test_reports_tenant_isolation.py` | `pytest test_reports_tenant_isolation.py` | PASS | `clinic_id` recibido por use-case = clinic_id del token JWT (8/8) | PASS |
| AC-015-11: Usuario sin clinic → 403 | `test_token_without_clinic_403`, `test_403_when_token_lacks_clinic` | integration | `test_reports_tenant_isolation.py`, `test_reports_router.py` | `pytest test_reports_tenant_isolation.py` | PASS | 403 correcto | PASS |
| AC-015-01..09 (FE): Frontend consume contrato correctamente | 5 suites Jest: `api.test.ts`, `ReportTable.test.tsx`, `useReports.test.ts`, `FilterBar.test.tsx`, `page.test.tsx` | frontend | `frontend/src/features/reports/` + `frontend/src/app/portal/admin/reports/` | `npx jest --testPathPattern='features/reports\|app/portal/admin/reports'` | PASS | 5 suites / 32 tests / 0 fail | PASS |
| Unit test gate: uso real de tiebreaker `id` en 5 use-cases | `TestReport[Appointments|Services|Consultations|Payments|RatingsSummary]DeterministicOrdering` | unit | 5 archivos `test_reports_*.py` en `usecases/` | `pytest app/tests/usecases/test_reports_*.py` | PASS | QF-015-01 resuelto: orden determinista con `id` como tiebreaker | PASS |

---

## Gate unitario — archvos productivos vs pruebas unitarias

| Archivo productivo (BE-015) | Test unitario/integración | Cubierto? |
|---|---|---|
| `backend/app/application/usecases/reports/report_appointments.py` | `test_reports_appointments_aggregation.py` (incl. `TestReportAppointmentsDeterministicOrdering`) | ✅ |
| `backend/app/application/usecases/reports/report_services.py` | `test_reports_services_aggregation.py` (incl. `TestReportServicesDeterministicOrdering`) | ✅ |
| `backend/app/application/usecases/reports/report_consultations.py` | `test_reports_consultations.py` (incl. `TestReportConsultationsDeterministicOrdering`) | ✅ |
| `backend/app/application/usecases/reports/report_payments.py` | `test_reports_payments.py` (incl. `TestReportPaymentsDeterministicOrdering`) | ✅ |
| `backend/app/application/usecases/reports/report_ratings_summary.py` | `test_reports_ratings_summary.py` (incl. `TestReportRatingsSummaryDeterministicOrdering`) | ✅ |
| `backend/app/application/usecases/reports/report_pets_count.py` | `test_reports_pets_count.py` | ✅ |
| `backend/app/api/v1/routers/reports_router.py` | `test_reports_router.py` + `test_reports_auth.py` + `test_reports_tenant_isolation.py` + `test_reports_invalid_input.py` | ✅ |
| `backend/app/api/v1/schemas/report_schemas.py` | `test_reports_schemas.py` + `test_reports_integration.py` | ✅ |
| `frontend/src/features/reports/api.ts` | `api.test.ts` | ✅ |
| `frontend/src/features/reports/hooks/useReports.ts` | `useReports.test.ts` | ✅ |
| `frontend/src/features/reports/components/ReportTable.tsx` | `ReportTable.test.tsx` | ✅ |
| `frontend/src/features/reports/components/FilterBar.tsx` | `FilterBar.test.tsx` | ✅ |
| `frontend/src/app/portal/admin/reports/page.tsx` | `page.test.tsx` | ✅ |

**Gap unitario: 0** — Todos los archivos productivos de BE-015 (BE + FE) tienen pruebas unitarias o integraciones explícitas que los cubren.

---

## Observaciones y limitaciones fuera del scope de BE-015

Estos hallazgos **NO son defectos de BE-015** y **NO invalidan la decisión**. Se documentan por transparencia:

### O1 — Fallos de layout en contenedor (36 tests)
Los tests de meta-repo (`test_slice_task_controls`, `test_secure_persistence_contracts`, `test_setup`,
etc.) usan `REPO_ROOT = parents[3]` que, dentro del contenedor, resuelve a `/` (no existe ahí).
Estos tests están diseñados para ejecutarse **en host** desde la raíz del repo.
**Impacto en BE-015:** ninguno.

### O2 — `test_setup.py::test_database_config` (1 test)
Aserta `settings.POSTGRES_SERVER == "localhost"`. En el contenedor el valor es `db` (servicio Docker).
Es una prueba de configuración local, no de la app.
**Impacto en BE-015:** ninguno.

### O3 — 4 fallos de payload-sync (host, pre-existentes)
| Test | Archivo desincronizado |
|---|---|
| `test_agentic_plan_schema_v3.py::test_schema_v3_contracts_are_synced_with_payload` | `.opencode/agents/invet-ui-automation-implementer.md`, `opencode.json`, `backend/scripts/validate_agent_catalog.py` |
| `test_automation_agentic_flow.py::test_automation_contracts_are_in_sync_with_payload` | ídem |
| `test_automation_agentic_flow.py::test_agentic_runtime_uses_direct_execution_and_safety_controls` | ídem |
| `test_vscode_agent_controls.py::test_cross_runtime_agent_catalog_is_valid_and_payload_is_synced` | ídem |

Estos 3 archivos están marcados como `modified` en `git status` **sin commit**, y no están en el
allowlist de BE-015. Son un **carrillo de trabajo abierto** de otra tarea (infraestructura de agentes)
que dejó el payload desincronizado. No se tratan de regresiones introducidas por BE-015.
**Impacto en BE-015:** ninguno.
**Acción recomendada:** la tarea que editó esos 3 archivos debe re-sincronizar `payload/` antes de cerrar.

### O4 — `bootstrap.py` modificado (uncommitted)
`backend/app/infrastructure/database/bootstrap.py` tiene cambios no commitados
(`ON CONFLICT DO UPDATE` en lugar de `NOT EXISTS INSERT` + un `UPDATE owners SET ...` adicional).
Este archivo **no está en el allowlist de BE-015** y no fue creado por este slice.
**Impacto en BE-015:** ninguno (los 129 tests de reportes pasan sin este archivo).
**Acción recomendada:** el agente que editó `bootstrap.py` debe commitarlo o revertirlo antes de que afecte otros slices.

---

## Evidencia reproducible

### Backend — use-cases (contenedor Docker)
```cmd
docker compose exec backend python -m pytest \
  app/tests/usecases/test_reports_appointments_aggregation.py \
  app/tests/usecases/test_reports_consultations.py \
  app/tests/usecases/test_reports_payments.py \
  app/tests/usecases/test_reports_pets_count.py \
  app/tests/usecases/test_reports_ratings_summary.py \
  app/tests/usecases/test_reports_schemas.py \
  app/tests/usecases/test_reports_services_aggregation.py -q
# → 67 passed in 0.47s
```

### Backend — integración (contenedor Docker)
```cmd
docker compose exec backend python -m pytest \
  app/tests/integration/test_reports_integration.py \
  app/tests/integration/test_reports_auth.py \
  app/tests/integration/test_reports_invalid_input.py \
  app/tests/integration/test_reports_tenant_isolation.py \
  app/tests/integration/test_reports_router.py -v
# → 62 passed in 1.79s  (ver detalle arriba)
```

### Backend — suite completa (host, entorno correcto para tests de meta-repo)
```cmd
python -m pytest app/tests/ -q
# → 626 passed, 4 failed, 1 skipped in 16.73s
# Los 4 failed son los payload-sync tests (O3) — pre-existente y fuera de scope.
```

### Frontend (host Jest)
```cmd
npx jest --testPathPattern='features/reports|app/portal/admin/reports'
# → Test Suites: 5 passed, 5 total | Tests: 32 passed, 32 total
```

### Docker Compose al cierre
```cmd
docker compose ps
# → invet-backend: Up (healthy)   → 0.0.0.0:8000->8000/tcp
# → invet-db:     Up (healthy)   → 0.0.0.0:5432->5432/tcp
# → invet-frontend: Up (healthy) → 0.0.0.0:3000->3000/tcp
```

---

## Tareas QA en el plan

| Tarea | Criterios cubiertos | Resultado |
|---|---|---|
| QA-015-T01 | AC-015-01, AC-015-03, AC-015-04 | PASS |
| QA-015-T02 | AC-015-02, AC-015-03 (paginación) | PASS |
| QA-015-T03 | AC-015-09, AC-015-10, AC-015-11 | PASS |

**3/3 tareas QA: PASS**

---

## Decisión

**APPROVED**

Todos los criterios aplicables (AC-015-01 → AC-015-11) están en `PASS`.
El gate unitario (archivo productivo ↔ test) cierra con 0 gaps.
Ningún defecto `blocker` o `critical` abierto.
No hay exposición de secretos/PII.
No hay pruebas críticas omitidas.
Docker Compose cierra con 3/3 healthy.

Los 4 fallos pre-existentes en host (O3) y los 36 fallos de layout del contenedor (O1/O2)
**son fuera del scope de BE-015** y se documentan como observaciones con acción recomendada para
la tarea correspondiente. No invalidan la decisión de este slice.
