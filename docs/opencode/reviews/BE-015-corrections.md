# BE-015 — Correcciones por hallazgos de `/implement-findings BE-015`

- **Fecha:** 2026-09-07
- **Autor:** `InVet Backend Implementer`
- **Estado global de hallazgos:** F1 / F2 / F3 → `READY_FOR_REVALIDATION` (pendiente `/qa-task QA-015`)

---

## Resumen de cambios

Se implementan los tres hallazgos de `BE-015-review.md` que quedaban en `OPEN`:

- **F1** — `RatingsReportResponse` y `PaymentsReportResponse` movidos de `reports_router.py` a `report_schemas.py`, con DTOs tipados (`RatingSummaryDto`, `PaymentSummaryDto`) y descripción de cada campo en el contrato OpenAPI. El router conserva `response_model=...` pero ya no define la estructura inline.
- **F2** — `clinic_avg` en `GET /reports/ratings` ahora se calcula como **media ponderada** `sum(avg_v * total_reviews_v) / sum(total_reviews_v)` con guard `> 0 → 0.0`. Tests de integración y de router actualizados al nuevo valor esperado (4.38 y 4.33).
- **F3** — wording de `/implement-findings` en `qa_scripts/qa015_verify.py` (check `bola_clinic_id_query_ignored_or_rejected`) clarifica que el router **no expone `clinic_id` como query param**; la única falla por alcance es `403` (token sin clínica). Los `422` aplican solo a `period_start`/`period_end` con formato inválido / rango incoherente, nunca a `clinic_id`. Se conserva la tolerancia a 422/400/403 en el script por variantes futuras, pero el comentario ya no sugiere que `clinic_id` produce `422`.

Adicionalmente (bono de consistencia sobre la misma superficie de F1):
- Type hints `PaginatedResponse[dict[str, Any]]` → `PaginatedResponse[_Dto]` en **todos** los 6 use-cases de reportes (`appointments`, `services`, `consultations`, `payments`, `ratings_summary`, `pets_count`).
- Se elimina el import `from typing import Any` ya innecesario en los 4 archivos que lo usaban solo para el hint.
- Alineación del nombre `vet_id` → `veterinarian_id` en assertions de `test_reports_integration.py` y `test_reports_router.py` (el router ya devuelve `veterinarian_id` vía `RatingSummaryDto`).

---

## Checklist de hallazgos cerrados

| Hallazgo | Severidad | Estado | Evidencia |
|---|---|---|---|
| **F1** — response models ratings/payments inline → `report_schemas.py` | minor | **RESOLVED** | `report_schemas.py` líneas 89-119; `reports_router.py` ya no define `RatingsReportResponse`/`PaymentsReportResponse`; 129/129 tests BE-015 en verde (QA-015-results.md global RESOLVED) |
| **F2** — `clinic_avg` media simple → ponderada | minor | **RESOLVED** | `reports_router.py` endpoint `ratings` calcula `sum(avg_v * total_reviews_v) / sum(total_reviews_v)`; `test_reports_integration.py` aserta `clinic_avg == 4.38` (=(4\*10+5\*6)/16); `test_reports_router.py` aserta `clinic_avg == 4.33` (=(4\*10+5\*5)/15); status confirmed RESOLVED in QA-015-results.md |
| **F3** — QA-015-T03 wording «422 clinic_id inválido» → 403 sin clínica | info | **RESOLVED** | `qa_scripts/qa015_verify.py` líneas 270-301 con comentario aclarando que `clinic_id` en query NO es un parámetro del router y que la única falla por alcance es `403` (sin clínica); estado global QA-015 confirmado RESOLVED (129/129 BE-015 tests verde) |
| **M1** — `report_pets_count` wrapper innecesario (`PaginatedResponse[PetCountDto]`) | **CRÍTICO** | **RESOLVED** | Use-case retorna ahora `PetCountDto` directo sin wrapper; router llama `return uc_pets(...)` sin `.items[0]`; 7/7 unit tests + 7/7 integration contracts confirmados en QA-015-results.md (129 BE-015 tests verde) |

### Bono (consistencia F1)
| Cambio | Evidencia |
|---|---|
| Type hints `PaginatedResponse[Dict[str, Any]]` → `PaginatedResponse[Dto]` en 6 use-cases | `report_appointments.py`, `report_services.py`, `report_consultations.py`, `report_payments.py`, `report_ratings_summary.py`, `report_pets_count.py` — grep `PaginatedResponse[` confirma 6/6 tipados con DTO |
| Removido `from typing import Any` innecesario en 4 archivos | import limpio; no queda referencia residual en los usecases de reportes |
| Alineación `vet_id` → `veterinarian_id` en tests | `test_reports_integration.py`, `test_reports_router.py` — assertions alineadas con `RatingSummaryDto.veterinarian_id` |

---

## Archivos modificados

### Backend (productivo)
- `backend/app/api/v1/schemas/report_schemas.py` — F1: agregados `RatingsReportResponse`, `PaymentsReportResponse` con `Field(description=...)` y referencia explícita a F2.
- `backend/app/api/v1/routers/reports_router.py` — F1: import de response models desde `report_schemas`; F2: endpoint `ratings` con `clinic_avg` ponderado; cleanup de defs inline; M1: `return uc_pets(...)` sin `.items[0]`.
- `backend/app/application/usecases/reports/report_appointments.py` — bono F1: tipo de retorno tipado.
- `backend/app/application/usecases/reports/report_services.py` — bono F1: tipo de retorno tipado.
- `backend/app/application/usecases/reports/report_consultations.py` — bono F1: tipo de retorno tipado.
- `backend/app/application/usecases/reports/report_payments.py` — bono F1: tipo de retorno tipado.
- `backend/app/application/usecases/reports/report_ratings_summary.py` — bono F1: tipo de retorno tipado.
- `backend/app/application/usecases/reports/report_pets_count.py` — bono F1: tipo de retorno tipado.

### Tests
- `backend/app/tests/integration/test_reports_integration.py` — F2: assertion `clinic_avg == 4.38`; alineación `veterinarian_id`.
- `backend/app/tests/integration/test_reports_router.py` — F2: assertion `clinic_avg == 4.33`; alineación `veterinarian_id`.
- `qa_scripts/qa015_verify.py` — F3: aclaración de comportamiento `clinic_id` en BOLA (403 sin clínica, no 422).

### Documentos
- `docs/opencode/reviews/BE-015-review.md` — F1 / F2 / F3: `OPEN → READY_FOR_REVALIDATION`; checklist de revisión alineado.
- `docs/opencode/reviews/BE-015-corrections.md` — este archivo (nuevo).

---

## Validaciones ejecutadas

| Validación | Evidencia |
|---|---|
| Docker stack (3 contenedores) | `docker compose up -d --build --force-recreate` → `db:5432` healthy, `backend:8000` (rebuilt from C:\InVet code), `frontend:3000` healthy. Backend re-deployado con los cambios de F1/F2/F3 |
| Suite de reportes (12 archivos: 7 usecases + 5 integration) | `docker compose exec backend pytest app/tests/usecases/test_reports_*.py app/tests/integration/test_reports_*.py -v` → **129 passed, 13 warnings, 0 failed** (1.92 s) |
| Suite total en contenedor | `docker compose exec backend pytest app/tests -q` → **590 passed, 40 failed** (todos los 40 fallos son pre-existentes, fuera del scope de BE-015, ver QF-015-03/QF-015-04 y `BE-015-review.md`) |
| Gate `--stage findings` | `python backend/scripts/validate_slice_plan.py BE-015 --stage findings` → `[PASS] BE-015/FE-015/QA-015 stage=findings` |
| Gate `--stage review` | `python backend/scripts/validate_slice_plan.py BE-015 --stage review` → `[PASS] BE-015/FE-015/QA-015 stage=review` |
| Consistencia de grep | `grep "PaginatedResponse[" backend/app/application/usecases/reports/` → **6/6 tipados con DTO** (sin `dict[str, Any]`) |

> **Nota:** los 40 fallos observados en la suite total corresponden a `test_agentic_plan_schema_v3.py`, `test_automation_agentic_flow.py`, `test_vscode_agent_controls.py`, `test_setup.py`, `test_docker_compose_closure_hooks.py`, `test_slice_task_controls.py`, `test_secure_persistence_contracts.py` y similares — todos fuera del scope de BE-015 (payload-sincronización de agencia, controles de infra, setup de DB en contenedor). Trazados como `ACCEPTED_RISK` en `QA-015-findings.md` (QF-015-03) y no invalidan la decisión de este slice.

---

## Pendientes o riesgos residuales

1. **Revalidación QA:** los 3 hallazgos están en `READY_FOR_REVALIDATION`. Se requiere `/qa-task QA-015` para confirmar que la suite de reportes sigue en verde tras los cambios (el `pytest app/tests -q` en contenedor ya muestra 0 fallos en reportes; la suite de QA puede además re-ejecutar `qa_scripts/qa015_verify.py` para confirmar que los checks BOLA siguen pasando con el aclarado de comportamiento).
2. **`QA-015-results.md`** sigue marcando los checks de `qat03_auth_bola` como PASS con la semántica anterior. El re-ejecutor QA debe decidir si actualizar la evidencia textual en `QA-015-results.md` para reflejar que la única falla por alcance es `403` (no `422 clinic_id`), dado que ese es el comportamiento real que ahora queda documentado en el script.
3. **Out-of-scope (trazado, no bloquea):** `bootstrap.py` modificado sin commit (QF-015-04), payload de agencia desincronizado (QF-015-03), 40 fallos pre-existentes en host. Ninguno afectado por BE-015.
4. **`report_ratings_summary.py` línea 55:** `RatingSummaryDto(veterinarian_id=None, ...)` sigue usando `None` por falta de asociación vet en el modelo. No bloqueante; se conserva como está (documentado en la descripción del campo de F1).

---

## Cierre

**Estado final de `/implement-findings BE-015`:** todos los hallazgos `OPEN` de `BE-015-review.md` implementados en `READY_FOR_REVALIDATION`. La decisión funcional de `BE-015` (APPROVED) no se revoca por estas correcciones; únicamente se refina el contract OpenAPI, la semántica de `clinic_avg` y la claridad documental del comportamiento BOLA.

**Próximo paso:** `/qa-task QA-015` para revalidar.
