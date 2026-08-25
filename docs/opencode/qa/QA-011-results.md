# QA-011 Results — Registro operativo de pagos de servicios

**Slice:** BE-011 / FE-011 / QA-011
**Date:** 2026-08-25
**Reviewer:** InVet QA Validator
**Estado global:** APPROVED

- Decision: APPROVED (ver §8)

---

## 1. Preflight Validation

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Plan existe y schema v3 | ✅ EXISTS | `docs/opencode/plans/BE-011-plan.md` (endpoints POST/GET/POST cancel; schemas PaymentCreate/Read/ListMeta/Method/Status) |
| Backend task con DoD | ✅ EXISTS | `docs/opencode/tasks/backend/BE-011.md` |
| Frontend task | ✅ EXISTS | `docs/opencode/tasks/frontend/FE-011.md` |
| QA task con DoD checkboxes | ✅ EXISTS | `docs/opencode/tasks/qa/QA-011.md` (DoD completado + evidencia 2026-08-25) |
| UIA-011 / APIA-011 | ✅ EXISTS | `InVet_UI_Automation/tests\e2e\fe-011-payments.spec.ts` (C1..C9), `InVet_UI_Automation/tests\api\apia-011-payments.spec.ts` (C1..C12) |
| Stack de prueba | ✅ healthy | `docker compose` invet-db / invet-backend / invet-frontend; PostgreSQL `invet` |

---

## 2. Inventory del SUT

| Componente | Estado | Archivo |
|-----------|--------|---------|
| Domain Entity | ✅ EXISTS | `backend/app/domain/entities/payment.py` (Payment: id, appointment_id, service_id, clinic_id, amount, method, amount_received, change_amount, status, paid_at, cancelled_at, created_at, updated_at) |
| Repository contrato | ✅ EXISTS | `backend/app/domain/repositories/payment_repository.py` (ABC: create, get_by_id, list, cancel) |
| ORM Modelo | ✅ EXISTS | `backend/app/infrastructure/database/models/payment.py` |
| Repositorio ORM | ✅ EXISTS | `backend/app/infrastructure/database/repositories/payment_repository_impl.py` |
| Use Cases | ✅ EXISTS | `backend/app/application/use_cases/payment_use_cases.py` (RegisterPayment, GetPayment, ListPayments, CancelPayment) |
| Schemas Pydantic | ✅ EXISTS | `backend/app/api/v1/schemas/payment_schemas.py` (PaymentCreate, PaymentRead, PaymentListMeta, PaymentMethod, PaymentStatus) |
| Router | ✅ EXISTS | `backend/app/api/v1/routers/payment_router.py` (POST 201, GET listado, GET detalle, POST cancel) |
| Migration | ✅ EXISTS | `backend/alembic/versions/a011_payments.py` (tabla payments, índices appointment_id/service_id/clinic_id/status) |
| Cliente API FE | ✅ EXISTS | `frontend/src/shared/api/payment.ts` (createPayment, getPayment, listPayments, cancelPayment) |
| Formulario | ✅ EXISTS | `frontend/src/app/clinic/payments/page.tsx` |
| Listado | ✅ EXISTS | `frontend/src/app/clinic/payments/history/page.tsx` |
| Detalle + cancel | ✅ EXISTS | `frontend/src/app/clinic/payments/[id]/page.tsx` |

---

## 3. Evidencia de ejecución

### 3.1 Happy path (registro CASH con cambio, listado por periodo, detalle) — ✅ PASS

| Suite | Resultado |
|-------|-----------|
| pytest payments (create/read/cancel/auth + use cases) | **42 passed** — `docker compose run --rm backend pytest app/tests/api/test_payments_create.py app/tests/api/test_payments_read.py app/tests/api/test_payments_cancel.py app/tests/api/test_payments_auth.py app/tests/test_payment_use_cases.py -q` |
| UIA-011 e2e `fe-011-payments.spec.ts` C1..C9 (chromium + firefox + webkit + mobile-chromium) | **36/36 PASS** (27.6s) — registro CASH con cambio, listado, detalle, cancelación |
| APIA-011 `apia-011-payments.spec.ts` C1..C12 | **12/12 PASS** (1.7s) — 401, 403, 422, 201+200, 409, 403 BOLA, listado paginado, listado periodo |

### 3.2 Negative / validaciones — ✅ PASS

| Caso | Esperado | Obtenido |
|------|----------|----------|
| `amount` < 0 | 422 | ✅ 422 validación Pydantic (`ge=0`) |
| Cita inexistente | 422 | ✅ 422 `PaymentAppointmentInvalidError` |
| Servicio inactivo / inexistente | 422 | ✅ 422 `PaymentServiceInvalidError` |
| `amount_received` < `amount` (CASH) | 422 | ✅ 422 `PaymentChangeInvalidError` |
| `method` fuera de enum (CASH/TRANSFER/CARD/OTHER) | 422 | ✅ 422 validación Pydantic |
| `amount_received` ausente cuando method=CASH | 422 | ✅ 422 `PaymentAmountReceivedRequiredError` |
| Sin token | 401 | ✅ 401 `get_current_access_user` |
| Cancelar pago ya cancelado | 409 | ✅ 409 `PaymentAlreadyCancelledError` |
| Cancelar pago inexistente | 404 | ✅ 404 `PaymentNotFoundError` |

### 3.3 Permisos / IDOR / BOLA — ✅ PASS

| Caso | Resultado | Detalle |
|------|-----------|---------|
| POST sin token | ✅ 401 | guard auth |
| Owner crea pago (rol `user` ∉ `_WRITE_ROLES`) | ✅ 403 | `_require_write_role` |
| Vet otra clínica crea pago | ✅ 403 | cross-clinic rechazado |
| Owner lee pago ajena (GET) | ✅ 404 | BOLA/IDOR cerrado |
| Admin → pago clínica ajena | ✅ 404 | aislamiento por tenant |
| APIA C4 (unauth API) | ✅ 401 | endpoint protegido |
| UIA C4 propietario sin permiso | ✅ PASS | formulario clínico no expuesto al rol owner |
| UIA C7 pago ajena no visible | ✅ PASS | owner no ve pago de otra mascota |
| Cancel por owner | ✅ 403 | `_require_write_role` en cancel |

### 3.4 Estados UX y responsive — ✅ PASS

| Suite | Resultado |
|-------|-----------|
| UIA-011 C1 (loading/submitting/success) | **4/4 PASS** (chromium + firefox + webkit + mobile) |
| UIA-011 C2 (cambio calculado en CASH) | **4/4 PASS** |
| UIA-011 C3 (error 422 inline) | **4/4 PASS** |
| UIA-011 C5 (empty state listado) | **4/4 PASS** |
| UIA-011 C8 (responsive mobile) | **4/4 PASS** |
| UIA-011 C9 (acentes sin mojibake) | **4/4 PASS** |
| **UIA-011 TOTAL** | **36/36 PASS** (9 casos × 4 proyectos) — 27.6s |

---

## 4. Migración Alembic — ✅ PASS

- **Migration:** `a011_payments.py`, `revision=a011` ← `down_revision=a010`.
- **Estructura:** tabla `payments` con PK `id` UUID, FKs a `appointments`/`services`/`clinics`; índices `appointment_id`/`service_id`/`clinic_id`/`status`. `upgrade()`/`downgrade()` reversibles.
- **Cobertura de datos:** sin pérdida (tabla nueva).

---

## 5. Cobertura de aceptación

| AC | Criterio | Evidencia | Estado |
|----|----------|-----------|--------|
| AC-011-01 | Registrar pago sobre cita + servicio activos | pytest 201 + UIA C1 + APIA C1 | ✅ |
| AC-011-02 | 422 si cita/servicio inactivo | pytest 422 + APIA C3 | ✅ |
| AC-011-03 | Cambio calculado solo CASH (amount_received >= amount) | pytest + UIA C2 + APIA C5 | ✅ |
| AC-011-04 | Listado paginado por tenant + periodo | pytest `meta` + UIA C5 + APIA C7 | ✅ |
| AC-011-05 | Detalle por id visible | pytest 200 + UIA C6 | ✅ |
| AC-011-06 | Cancelación 200 → CANCELLED; 409 si ya cancelado | pytest + UIA C7 + APIA C9 | ✅ |
| AC-011-07 | 403 owner; 404 pago ajena; 401 sin token | pytest + UIA C4/C7 + APIA C4 | ✅ |
| AC-011-08 | Estados UX (loading, submitting, empty, success, error) | UIA C1/C3/C5 + jest | ✅ |
| AC-011-09 | Migración `a011` con FK/índices | `a011` vigente, reversible | ✅ |
| AC-011-10 | UTF-8 sin mojibake en UI y payload | UIA C9 | ✅ |

> Todos los ACs definidos en el plan están cubiertos con evidencia reproducible.

---

## 6. Riesgo residual / evidencia-gaps

- **Envío de recibo fiscal** fuera de alcance MVP (`recibo no fiscal` renderizado en UI; sin efecto SAT/CFDI). Queda pendiente en backlog Stage 2. No es defecto.
- **Idempotencia explícita** (`Idempotency-Key`) no implementada; se cubre con duplicate guard + unique constraint `(appointment_id, service_id, status='PAID')`. Mismo patrón que BE-009/BE-010.

---

## 7. Findings

- **0 findings** abiertos al momento del gate.
- Ningún defecto de producto encontrado durante la sesión de QA.

---

## 8. Gate Decision

- 10/10 ACs cubiertos con evidencia reproducible (pytest 42 + UIA 36 + APIA 12).
- UIA 36/36 PASS en **4 proyectos** (chromium, firefox, webkit, mobile-chromium).
- Sin hallazgos de seguridad IDOR/BOLA/rol abiertos en el flujo de pagos.
- Migración `a011` vigente, reversible, sin pérdida de datos.
- Sin findings abiertos.

### Decision: **APPROVED**

---

## 9. Evidence Log

- pytest payments (create/read/cancel/auth + use cases): **42 passed**
- UIA-011 e2e (`--project chromium --project firefox --project webkit --project mobile-chromium`): **36/36 PASSED** (27.6s)
- APIA-011 (proyecto `api`): **12/12 PASSED** (1.7s)
- frontend `tsc --noEmit` / `next lint`: **0 errores**
- alembic `heads`: **`a011 (head)`**
- Regresión API completa: **84 passed, 64 skipped, 0 failed** (skips feature-gated: seeded tenant, LOGIN_API_ENABLED=false, JUSTIFIED_SKIP — patrón BE-009/BE-010)

---

*Estado de ejecución: APPROVED*
*Siguiente paso: `/review-slice BE-011` — QA aprobado sin findings abiertos.*
