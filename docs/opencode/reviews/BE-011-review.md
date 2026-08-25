---
encoding: UTF-8
artifact: review_findings
---

# Hallazgos de revisión de slice BE-011

## Resumen

- Slice: BE-011 — Registro operativo de pagos de servicios (payments)
- Tipo de review: Revisión funcional (contrato BE/FE + seguridad + arquitectura + evidencia)
- Estado: `RESOLVED`
- Decision: `APPROVED`

## Alcance revisado

- Backend:
  - `POST /api/v1/payments` (201), `GET /api/v1/payments?appointment_id=&from=&to=&page=&page_size=` (listado 200 con `meta {page, page_size, size, total, pages}`), `GET /api/v1/payments/{id}` (200), `POST /api/v1/payments/{id}/cancel` (200).
  - Entidad de dominio (`Payment` + enums `PaymentMethod`/`PaymentStatus`): `backend/app/domain/entities/payment.py`.
  - Contrato de repositorio (interfaz): `backend/app/domain/repositories/payment_repository.py`.
  - Implementación ORM: `backend/app/infrastructure/database/repositories/payment_repository_impl.py`.
  - Migración Alembic `a011` con FKs + índices: `backend/alembic/versions/a011_payments.py`.
  - Casos de uso: `backend/app/application/use_cases/payment_use_cases.py`.
  - Schemas Pydantic: `backend/app/api/v1/schemas/payment_schemas.py`.
  - Router: `backend/app/api/v1/routers/payment_router.py`.
  - Pruebas: `backend/app/tests/test_payment_use_cases.py`, `backend/app/tests/api/test_payments_{create,read,cancel,auth}.py`.
- Frontend:
  - Cliente API tipado: `frontend/src/shared/api/payment.ts` (`createPayment`, `getPayment`, `listPayments`, `cancelPayment`).
  - Formulario: `frontend/src/app/clinic/payments/page.tsx`.
  - Listado: `frontend/src/app/clinic/payments/history/page.tsx`.
  - Detalle + cancel: `frontend/src/app/clinic/payments/[id]/page.tsx`.
  - Pruebas unitarias: `frontend/src/shared/api/payment.test.ts`.
- QA / QA-Automation:
  - `docs/opencode/qa/QA-011-results.md` (APPROVED). 0 findings abiertos.
  - Evidencia: pytest 42 + UIA 36/36 (4 proyectos) + APIA 12/12.

## Resumen ejecutivo

La implementación es **completa, coherente y verde**. Los 4 endpoints existen con contratos consistentes entre backend y frontend, la lógica de negocio vive en `application/use_cases` (los routers son adaptadores delgados con mapeo de excepciones de dominio a HTTP), el tenant isolation se aplica en todos los endpoints, y los cinco estados UX (loading, submitting, empty, success, error) están cubiertos en la UI.

La seguridad del flujo está alineada con el brief: `POST` y `cancel` restringidos a roles clínicos (`_WRITE_ROLES` = `{veterinarian, clinic, staff, admin}`), 403 para propietario, 409 por cancelación duplicada, 404 en lectura de pago ajeno, 401 sin token, y 422 para validaciones de negocio (cita/servicio inactivos, cambio inválido).

Ningún defecto real (producto) fue encontrado. El gate de revisión es **APPROVED**.

## Evidencia fresca de pruebas

- Use-cases + API: **42 passed** (docker compose run --rm backend pytest ...).
- Frontend: `npx tsc --noEmit` → **sin errores**.
- UIA-011: **36/36 PASS** (chromium + firefox + webkit + mobile-chromium, 27.6s).
- APIA-011: **12/12 PASS** (1.7s).
- QA Gate: `docs/opencode/qa/QA-011-results.md` → **APPROVED** (§8).

## Hallazgos por severidad

### Blocker

- Ninguno.

### Critical

- Ninguno.

### Major

- Ninguno.

### Minor

- **m1 — UIA firefox/webkit disponibles y pasando en este slice (4 proyectos), a diferencia de BE-010 (2 proyectos).**
  En este entorno firefox y webkit funcionan correctamente. La cobertura E2E es de 4 proyectos (chromium, firefox, webkit, mobile-chromium). Sin riesgo residual.

- **m2 — Idempotencia explícita no implementada.**
  El duplicate guard + unique constraint `(appointment_id, service_id, status='PAID')` cubren el doble registro. Sin `Idempotency-Key` explícito. Mismo patrón que BE-009/BE-010. Aceptable para MVP.

## Archivos afectados

Backend (implementación viva):
- `backend/app/domain/entities/payment.py`
- `backend/app/domain/repositories/payment_repository.py`
- `backend/app/infrastructure/database/models/payment.py`
- `backend/app/infrastructure/database/repositories/payment_repository_impl.py`
- `backend/alembic/versions/a011_payments.py`
- `backend/app/application/use_cases/payment_use_cases.py`
- `backend/app/api/v1/schemas/payment_schemas.py`
- `backend/app/api/v1/routers/payment_router.py`
- `backend/app/tests/test_payment_use_cases.py`
- `backend/app/tests/api/test_payments_{create,read,cancel,auth}.py`

Frontend (implementación viva):
- `frontend/src/shared/api/payment.ts`
- `frontend/src/shared/api/payment.test.ts`
- `frontend/src/app/clinic/payments/page.tsx`
- `frontend/src/app/clinic/payments/history/page.tsx`
- `frontend/src/app/clinic/payments/[id]/page.tsx`

QA / tracking:
- `docs/opencode/plans/BE-011-plan.md` (cerrado en esta revisión)
- `docs/opencode/qa/QA-011-results.md`
- `docs/opencode/reviews/BE-011-review.md` (este documento)

## Notas de seguridad

- **Autenticación**: los 4 endpoints dependen de `get_current_access_user`; 401 si no hay `user_id`.
- **Autorización (escritura)**: `_WRITE_ROLES = {"veterinarian","clinic","staff","admin"}`. `_require_write_role` lanza 403 si el rol no está en el conjunto.
- **IDOR/BOLA**: `clinic_id` se resuelve del token; `get_by_id(payment_id, clinic_id)` y `list(appointment_id, from, to, clinic_id, ...)` filtran por tenant.
- **Ownership**: owner no puede crear/cancelar (403); 404 en lectura de pago ajeno.
- **Validación**: Pydantic con `ge=0`, enum validation, `amount_received` obligatorio para CASH.
- **No filtrado de info interna**: mensajes genéricos y estables.

## Clean architecture

- **Domain**: `Payment` como modelo Pydantic puro; enums `PaymentMethod`/`PaymentStatus`; sin dependencia de ORM ni framework.
- **Application**: los 4 casos de uso inyectan repositorios por constructor; desacoplado correctamente.
- **Infrastructure**: implementación ORM aislada; FKs + índices en migración `a011`.
- **API**: routers como adaptadores delgados; mapeo de excepciones de dominio a HTTP (`401/403/404/409/422`); listado paginado con `meta`.

## Contrato BE↔FE

- `PaymentRead` ≡ `Payment` TS: `id`, `appointment_id`, `service_id`, `clinic_id`, `amount`, `method`, `amount_received`, `change_amount`, `status`, `paid_at`, `cancelled_at`, `created_at`, `updated_at`.
- `PaymentListResponse { items, meta }` ≡ `PaymentPage { items, meta: dict }`.
- Query params: `appointment_id`, `from`, `to`, `page`, `page_size` coincidentes entre router y cliente FE.

## Comparison con criterios

| Criterio | Estado |
|---|---|
| Endpoints POST/GET/POST cancel con contratos | ✅ 4 endpoints + cliente API tipado |
| Routers sin lógica de negocio | ✅ Lógica en `payment_use_cases.py` |
| No se exponen modelos ORM | ✅ Siempre `PaymentRead.model_validate` |
| Listado paginado con `meta` | ✅ `payment_router.py` |
| Errores consistentes, sin info interna | ✅ 401/403/404/409/422 estables |
| Seguridad IDOR/BOLA por rol y clínica | ✅ `_require_write_role`, tenant filter |
| Pruebas happy + negative + seguridad | ✅ pytest 42 + UIA 36 + APIA 12 |
| Estados UX 5 | ✅ pages + UIA C1/C3/C5 |
| Migración `a011` reversible | ✅ FKs, índices |

## Checklist de revisión

- [x] Contrato BE validado.
- [x] Contrato FE validado.
- [x] Casos QA validados (pytest 42).
- [x] Arquitectura revisada.
- [x] Permisos e IDOR/BOLA revisados.
- [x] Evidencia documentada.
- [x] Findings de QA: 0 abiertos.

## Decision final

- Decision: `APPROVED`
- Evidencia: pytest **42 passed**, frontend `tsc --noEmit` **sin errores**, UIA **36/36** (4 proyectos), APIA **12/12**, contrato BE↔FE consistente, seguridad verificada, migración `a011` reversible.
- Sin hallazgos bloqueantes.

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
