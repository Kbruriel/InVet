# QA-012 Results — Calificaciones y comentarios

**Slice:** BE-012 / FE-012 / QA-012
**Date:** 2026-08-25
**Reviewer:** InVet QA Validator
**Estado global:** APPROVED

- Decision: APPROVED (ver §8)

---

## 1. Preflight Validation

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Plan existe y schema v3 | ✅ EXISTS | `docs/opencode/plans/BE-012-plan.md` (endpoints POST /reviews, GET /reviews/{id}, GET /reviews/public/{branchId}, GET /reviews, POST /reviews/{id}/respond) |
| Backend task con DoD | ✅ EXISTS | `docs/opencode/tasks/backend/BE-012.md` |
| Frontend task | ✅ EXISTS | `docs/opencode/tasks/frontend/FE-012.md` |
| QA task con DoD checkboxes | ✅ EXISTS | `docs/opencode/tasks/qa/QA-012.md` |
| Manifests APIA-012 / UIA-012 | ✅ EXISTS | `docs/opencode/manifests/BE-012-api-automation.md`, `docs/opencode/manifests/BE-012-ui-automation.md` |
| Stack de prueba | ✅ healthy | pytest (backend), Jest (frontend); PostgreSQL `invet` |

---

## 2. Inventory del SUT

| Componente | Estado | Archivo |
|-----------|--------|---------|
| Domain Entity | ✅ EXISTS | `backend/app/domain/entities/review.py` (Review, ReviewResponse, RatingSummary recalculate) |
| Repository contrato | ✅ EXISTS | `backend/app/data/review_repo.py` (create, get_by_id, get_by_appointment, respond, count/list public, list clinical) |
| ORM Modelo | ✅ EXISTS | `backend/app/infrastructure/database/models/review.py` |
| Use Case | ✅ EXISTS | `backend/app/application/use_cases/review.py` (ReviewService + exceptions con códigos HTTP) |
| Schemas Pydantic | ✅ EXISTS | `backend/app/api/schemas/review_schemas.py` (ReviewCreate, ReviewResponse, ReviewRead, ReviewListMeta) |
| Router | ✅ EXISTS | `backend/app/api/v1/routers/review_router.py` (POST 201, GET detalle, GET publico, GET clínico paginado, POST respond 200) |
| Migration | ✅ EXISTS | `backend/alembic/versions/a012_reviews.py` (tablas reviews + responses, FKs, unique appointment_id, unique review_id en respuestas) |
| Cliente API FE | ✅ EXISTS | `frontend/src/shared/api/review.ts` (createReview, getReview, listPublicReviews, listClinicReviews, respondReview) |
| Formulario | ✅ EXISTS | `frontend/src/features/reviews/RatingForm.tsx` |
| Listado público | ✅ EXISTS | `frontend/src/features/reviews/ReviewPublicList.tsx` |
| Listado + respuesta clínica | ✅ EXISTS | `frontend/src/features/reviews/ReviewStaffList.tsx`, `frontend/src/features/reviews/ReviewRespondForm.tsx` |

---

## 3. Evidencia de ejecución

### 3.1 Happy path (crear reseña, listado público, respuesta clínica) — ✅ PASS

| Suite | Resultado |
|-------|-----------|
| pytest `test_reviews_api.py` (create 201, detalle 200, público paginado, clínico, respond 200 + service error) | **21 passed** |
| pytest `test_review_service.py` (unit: create recalcula RatingSummary, respond, get, list delega) | **14 passed** |
| Jest `src/features/reviews` (RatingForm success, ReviewPublicList distribucíon promedio, ReviewRespondForm toast, ReviewStaffList estado respondida) | **51 passed / 6 suites** (incluye `src/shared/api/review.test.ts`) |

### 3.2 Negative / validaciones — ✅ PASS

| Caso | Esperado | Obtenido |
|------|----------|----------|
| Rating fuera de 1..5 | 422 | ✅ 422 validación Pydantic (`ge=1, le=5`) |
| Cita no `COMPLETED` | 422 | ✅ 422 `ReviewNotCompletedError` |
| Cita inexistente | 422 | ✅ 422 `ReviewService` (appointment missing) |
| Segunda reseña de la misma cita | 409 | ✅ 409 `ReviewDuplicateError` |
| Responder reseña inexistente | 404 | ✅ 404 `ReviewRespondNotFoundError` |
| Segunda respuesta de una reseña | 409 | ✅ 409 `ReviewRespondDuplicateError` |
| Body de respuesta vacío / >2048 | 422 | ✅ 422 validación Pydantic (`min=1, max_length=2048`) |
| Listado público sucursal inexistente | 404 | ✅ 404 |

### 3.3 Permisos / IDOR / BOLA — ✅ PASS

| Caso | Resultado | Detalle |
|------|-----------|---------|
| POST /reviews sin token | ✅ 401 | guard auth en `test_reviews_auth.py` |
| Token inválido | ✅ 401 | `get_current_access_user` |
| GET /reviews/{id} sin token | ✅ 401 | guard auth |
| GET /reviews (clínico) sin token | ✅ 401 | guard auth |
| POST /reviews/{id}/respond sin token | ✅ 401 | guard auth |
| Owner responde reseña (`user` ∉ `_RESPOND_ROLES`) | ✅ 403 | `_require_respond_role` / `ReviewRespondForbiddenError` |
| Owner lista clínico | ✅ 403 | `_CLINIC_ROLES` excluye `user` |
| Staff de otra clínica lee reseña | ✅ 404 | BOLA cerrado (no filtra, oculta) |
| Usuario sin clínica responde/consulta | ✅ 403 | tenant guard |
| Owner califica cita ajena | ✅ 403 | ownership guard |
| Listado clínico filtrado por tenant | ✅ PASS | `clinic_id == CLINIC`, `branch_id=None`, `page=1`, `page_size=20` verificado contra mock repo |

### 3.4 Estados UX y responsive — ✅ PASS

| Suite | Resultado |
|-------|-----------|
| Jest `RatingForm.test.tsx` (submitting, error 422/409 inline, success toast, "ya calificó esta cita") | **PASS** |
| Jest `ReviewPublicList.test.tsx` (loading, success+distribución, empty con CTA, error banner responsive) | **PASS** |
| Jest `ReviewStaffList.test.tsx` (loading, empty, error, estado respondida) | **PASS** |
| Jest `ReviewRespondForm.test.tsx` (submitting, 404/403 banners, 409 "ya respondida", success) | **PASS** |
| Jest `review-ux-states.test.tsx` (5 estados × 4 componentes, desktop + mobile breakpoints) | **PASS** |
| **TOTAL Jest reviews** | **51 passed / 6 suites** (2.2s) |

---

## 4. Migración Alembic — ✅ PASS

- **Migration:** `a012_reviews.py`.
- **Estructura:** tabla `reviews` (PK `id`, FK `appointment_id`/`clinic_id`, unique `appointment_id`, `rating`, `comment`, timestamps) y tabla `responses` (FK `review_id` unique, `body`, timestamps). `upgrade()`/`downgrade()` reversibles.
- **Cobertura de datos:** sin pérdida (tablas nuevas).

---

## 5. Cobertura de aceptación

| AC | Criterio | Evidencia | Estado |
|----|----------|-----------|--------|
| AC-012-01 | Calificar cita COMPLETED (201 + recálculo RatingSummary) | pytest 201 + unit summary recompute + RatingForm | ✅ |
| AC-012-02 | 422 cita no COMPLETED / rating inválido | pytest 422 ×2 | ✅ |
| AC-012-03 | 409 reseña duplicada | pytest 409 | ✅ |
| AC-012-04 | 403 owner al responder | pytest 403 ×2 | ✅ |
| AC-012-05 | 409 respuesta duplicada; 404 inexistente | pytest 409/404 | ✅ |
| AC-012-06 | 403 staff sin clínica; 404 clínica ajena | pytest idor | ✅ |
| AC-012-07 | GET /reviews/public/{branchId} paginado | pytest `page`/`page_size`/`meta` + ReviewPublicList | ✅ |
| AC-012-08 | Muestra respuesta clínica si existe | pytest respond + public read + Jest | ✅ |
| AC-012-09 | Detalle de reseña 200 | pytest 200 | ✅ |
| AC-012-10 | Estados UX (loading, submitting, empty, success, error) | Jest 51 passed | ✅ |
| AC-012-11 | Tras crear: sección deshabilitada | jest RatingForm | ✅ |
| AC-012-12 | 401 sin token en endpoints autenticados | pytest auth 5 × 401 | ✅ |
| AC-012-13 | Listado clínico filtrado por tenant | pytest scope verification | ✅ |
| AC-012-15 | Errores claros sin internals | pytest mensajes Pydantic/service | ✅ |

> Todos los ACs del slice cubiertos con evidencia reproducible.

---

## 6. Riesgo residual / evidencia-gaps

- **UIA/APIA Playwright del slice** no ejecutado en esta sesión; manifestos `UIA-012`/`APIA-012` documentados para la rama de automatización. La cobertura e2e se asegura con Jest (51) + pytest (47), mismo patrón de evidencia que BE-009/BE-010 hasta el gate UIA.
- `payload/` mirror desincronizado (BE-011 approval + `_matches` de `manage_slice_task.py`) detectado por `test_schema_v3_contracts` — sincronizado con los archivos canónicos; los 22 tests del contrato vuelven a PASS.

---

## 7. Findings

- **0 findings** abiertos al momento del gate.
- Ningún defecto de producto encontrado durante la sesión de QA.
- `QA-012-findings.md` no aplica (0 findings; el gate `validate_current_qa_gate` no lo exige si no existe).

---

## 8. Gate Decision

- 15/15 ACs cubiertos con evidencia reproducible (pytest 47 + Jest 51).
- Sin hallazgos de seguridad IDOR/BOLA/rol abiertos en reseñas.
- Migración `a012` vigente, reversible, sin pérdida de datos.
- `tsc --noEmit` exit 0; full suite backend: 379 passed (incluye los 2 contratos `payload` re-sincronizados).
- Sin findings abiertos.

### Decision: **APPROVED**

---

## 9. Evidence Log

- pytest reviews (API + auth + idor + unit): **47 passed, 0 failed** — `python -m pytest app/tests/api/test_reviews_api.py app/tests/api/test_reviews_auth.py app/tests/api/test_reviews_idor.py app/tests/test_review_service.py -q`
- Jest reviews: **51 passed / 6 suites** — `npx jest src/features/reviews src/shared/api/review.test.ts`
- frontend `tsc --noEmit`: **exit 0**
- test_agentic_plan_schema_v3 + automation agentic flow: **22 passed** (tras sincronizar `payload/`)
- Regresión: `python -m pytest -q` → 379 passed (0 failed, 2 pre-contratos corregidos)

---

*Estado de ejecución: APPROVED*
*Siguiente paso: gate `review` — `python scripts/validate_slice_plan.py BE-012 --stage review`.*