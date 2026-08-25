# BE-011 Security Review

**Slice**: BE-011 (Registro operativo de pagos de servicios)
**Review Date**: 2026-08-25
**Tipo de review**: Seguridad
**Estado global**: APPROVED

- Decision: APPROVED

---

## Executive Summary

BE-011 está **APPROVED** desde la perspectiva de seguridad. Los 4 endpoints implementados (POST `/payments`, GET `/payments?filters`, GET `/payments/{id}`, POST `/payments/{id}/cancel`) cubren autenticación obligatoria, autorización por rol (solo roles clínicos escriben/cancelan), aislamiento de tenant (clínica) en todas las consultas, validación de entrada con Pydantic y paginación acotada.

No se identificó ninguna vulnerabilidad explotable. IDOR/BOLA, ownership y aislamiento por clínica están aplicados en router + use case y verificados por `test_payments_auth.py`, `test_payments_read.py` (403/404), la suite UIA (C4/C7 access) y las AC de QA-011.

---

## Checklist OWASP — Backend

### 1. Autenticación en endpoints privados

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Todos los endpoints requieren auth | `Depends(get_current_access_user)` en los 4 endpoints (`payment_router.py`) | ✅ |
| Token JWT válido | `get_current_access_user` valida exp, sub y type (core.security) | ✅ |
| user_id ausente → 401 | `_extract_user_id` lanza 401 | ✅ |

### 2. Autorización por rol y contexto

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Escritura restringida a roles clínicos | `_WRITE_ROLES = {"veterinarian","clinic","staff","admin"}`; `_require_write_role` → 403 | ✅ |
| Cancel restringida a roles clínicos | `_require_write_role` en `POST /{id}/cancel` → 403 | ✅ |
|LECTURA sin restricción de rol clínico | GETs solo requieren auth + tenant/ownership | ✅ |
| `clinic_id` tomado del token, nunca del payload | `_get_clinic_id_from_user` extrae del claim | ✅ |

### 3. Prevención IDOR/BOLA

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Creación: cita filtrada por clínica | `appointment_repository.get_by_id(appointment_id, clinic_id)` → 422 genérico si no coincide | ✅ |
| Creación: servicio filtrado por clínica | `service_repository.get_by_id(service_id, clinic_id)` → 422 | ✅ |
| Detalle: pago filtrado por clínica | `repository.get_by_id(payment_id, clinic_id)` → 404 si ajeno | ✅ |
| Listado: filtrado por tenant | `list(appointment_id, from, to, clinic_id, ...)` | ✅ |
| Cancel: pago filtrado por clínica | `get_by_id(payment_id, clinic_id)` + `_require_write_role` | ✅ |
| Respuesta no filtra el scope | Mensajes genéricos: "El pago no existe." | ✅ |

### 4. Ownership por propietario

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Owner no puede crear | `_require_write_role` → 403 (role `"user"` ∉ `_WRITE_ROLES`) | ✅ |
| Owner no puede cancelar | `_require_write_role` en cancel → 403 | ✅ |
| 404 (no 403) a pagos ajenos | `get_by_id(id, clinic_id)` → None → 404 | ✅ |

### 5. Validación de entrada

| Control | Evidencia | Estado |
|---------|-----------|--------|
| `appointment_id` / `service_id` gt=0 | `Field(..., gt=0)` | ✅ |
| `amount` ge=0 | `Field(..., ge=0)` | ✅ |
| `amount_received` ge=0, obligatorio para CASH | use case valida → 422 | ✅ |
| `method` enum (CASH, TRANSFER, CARD, OTHER) | Pydantic Literal/Enum | ✅ |
| `page`/`page_size` acotados | `page ge=1`, `page_size ge=1 le=100` | ✅ |

### 6. Logs sin datos sensibles

- `logging`/`print(` en `payment_router.py` + `payment_use_cases.py` → **0 coincidencias**. ✅

### 7. Respuesta sin campos internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| DTO Pydantic explícito | `PaymentRead.model_validate(result)`; schemas separados del ORM | ✅ |
| Sin password/token/secret | `password\|token\|secret` en `payment_schemas.py` → **0 coincidencias** | ✅ |
| Sin stack trace | `detail=exc.message` con mensajes estáticos controlados | ✅ |

### 8. Errores sin detalles internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| 401 | "No se pudo identificar al usuario autenticado." | ✅ |
| 403 | "Solo un veterinario o staff de clínica puede gestionar pagos." | ✅ |
| 404 | "El pago no existe." | ✅ |
| 409 | "El pago ya está cancelado." | ✅ |
| 422 | Mensajes de validación genéricos (cita inactiva, cambio inválido, etc.) | ✅ |

---

## Checklist OWASP — Frontend

| Control | Evidencia | Estado |
|---------|-----------|--------|
| No almacena tokens/payloads local | `localStorage`/`sessionStorage`/`document.cookie` en páginas + API client → **0 coincidencias** | ✅ |
| No loguea payloads | `console.log/error/warn` en `payment.ts` + 3 páginas → **0 coincidencias** | ✅ |
| Sin inyección HTML | `dangerouslySetInnerHTML` → **0 coincidencias** | ✅ |
| Usa shared API client con `Authorization` | `payment.ts` consume `client` (`shared/api`) que inyecta Bearer | ✅ |
| No confía en permisos visuales | 403/404 del backend son la fuente de verdad; `ErrorBanner` solo renderiza `detail` | ✅ |

---

## Hallazgos Detectados

### Minor — no bloqueantes

| # | Hallazgo | Severidad | Recomendación |
|---|----------|-----------|---------------|
| S1 | Sin cabecera `Idempotency-Key` en `POST /payments`. El duplicate guard cubre el doble post. | Minor | Agregar `Idempotency-Key` opcional en Stage 2. |
| S2 | Sin rate-limiting explícito en `POST /payments`. Protegido por auth + rol + duplicate guard. | Minor | Agregar `fastapi-limiter` en Stage 2 (out-of-scope). |

### Ningún Hallazgo Critical, Major ni Blocker

- ❌ No IDOR/BOLA explotable: `clinic_id` filtrado en `get_by_id` (creación, detalle, listado, cancel).
- ❌ No creación/cancel por owner: `_require_write_role` → 403.
- ❌ No lectura de pago ajeno: tenant filter → 404.
- ❌ No exposición de passwords/tokens/stack traces.
- ❌ No logs de secretos.
- ❌ `clinic_id` nunca sobrescritible por payload.

---

## Análisis de Ataques Potenciales

### Escenario 1 — IDOR: vet de clínica A lee pago de clínica B
**Protección**: `PaymentRepository.get_by_id(payment_id, clinic_id)` filtra tenant.
**Resultado**: 404 "El pago no existe." ✅

### Escenario 2 — BOLA: vet crea pago para cita de otra clínica
**Protección**: `appointment_repository.get_by_id(appointment_id, clinic_id)` → None → 422.
**Resultado**: 422 "La cita no existe o no es accesible." ✅

### Escenario 3 — Owner intenta crear/cancelar pago
**Protección**: `_require_write_role` → role `"user"` ∉ `_WRITE_ROLES` → 403.
**Resultado**: 403 "Solo un veterinario o staff de clínica puede gestionar pagos." ✅

### Escenario 4 — Payload spoofing de tenant
**Protección**: `clinic_id` se resuelve del token; no es campo del payload.
**Resultado**: el payload es ignorado para tenant. ✅

### Escenario 5 — Token fabricado / expirado
**Protección**: `get_current_access_user` → 401.
**Resultado**: 401. ✅

### Escenario 6 — Cancel doble
**Protección**: use case verifica `status != CANCELLED` → `PaymentAlreadyCancelledError` → 409.
**Resultado**: 409 "El pago ya está cancelado." ✅

---

## Checklist de Verificación Final

- [x] Contrato BE-011 validado con seguridad (4 endpoints).
- [x] Rol clínico obligatorio para `POST /payments` y `cancel` (owner → 403).
- [x] IDOR/BOLA mitigado por `clinic_id` en `get_by_id`/`list`.
- [x] Ownership por owner en GET (→ 404 sin filtrar existencia).
- [x] Cancel dupla → 409.
- [x] `clinic_id` nunca sobrescritible por payload.
- [x] Pydantic validation con `ge=0`/`gt=0`/enum/colecciones acotadas.
- [x] Paginación `page ge=1`, `page_size ge=1 le=100`.
- [x] 0 coincidencias de `logging`/`print(` en router + use cases.
- [x] 0 coincidencias de `console.log`/`dangerouslySetInnerHTML`/`localStorage` en FE.
- [x] 0 coincidencias de `password`/`token`/`secret` en schema API.
- [x] 401/403/404/409/422 con mensajes genéricos, sin internas.
- [x] Tests de seguridad: `test_payments_auth.py`, `test_payments_read.py` (42 passed) + UIA C4/C7 (36/36) + APIA (12/12).

---

## Decision Final

- Decision: APPROVED
- Evidencia: 4 endpoints con auth + rolc + tenant isolation + IDOR/BOLA + validación + no filtrado + 42 pytest + 36 UIA + 12 APIA en verde.

---

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No hay mojibake en el archivo.
