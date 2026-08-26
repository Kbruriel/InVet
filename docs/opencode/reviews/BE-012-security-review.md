# BE-012 Security Review

**Slice**: BE-012 (Calificaciones y comentarios)
**Review Date**: 2026-08-25
**Tipo de review**: Seguridad
**Estado global**: APPROVED

- Decision: APPROVED

---

## Executive Summary

BE-012 está **APPROVED** desde la perspectiva de seguridad. Los endpoints implementados (POST `/reviews`, GET `/reviews/public/{branch_id}`, GET `/reviews`, GET `/reviews/{review_id}`, POST `/reviews/{review_id}/respond`) cubren autenticación obligatoria en los no públicos, autorización por rol (solo roles clínicos responden/listan clínicamente), aislamiento de tenant (clínica) en todas las consultas autenticadas, validación de entrada con Pydantic, paginación acotada y deduplicación (una reseña por cita, una respuesta por reseña).

No se identificó ninguna vulnerabilidad explotable. IDOR/BOLA, ownership y aislamiento por clínica están aplicados en router + use case y verificados por `test_reviews_api.py` (401/403/404/409/422 cobrados por endpoint) y por `test_review_service.py`.

---

## Checklist OWASP — Backend

### 1. Autenticación en endpoints privados

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Endpoints no públicos requieren auth | `Depends(get_current_access_user)` en create, list clínico, get, respond | ✅ |
| Listado público intencionalmente anónimo | `GET /reviews/public/{branch_id}` sin auth; sucursal inexistente → 404 | ✅ |
| user_id ausente → 403/401 | `create()` exige `clinic_id` y `user_id` del token → `ReviewNotAuthorizedError` (403) | ✅ |

### 2. Autorización por rol

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Responder restringido a roles clínicos | `_RESPOND_ROLES = {veterinarian, clinic, staff, admin, internal}`; `_require_respond_role` → 403 | ✅ |
| Listado clínico restringido | `_require_clinic_role` → 403 (propietario bloqueado) | ✅ |
| `clinic_id` tomado del token, nunca del payload | `_get_clinic_id_from_user` le el claim; el campo `clinic_id` del dominio nunca viene del body | ✅ |

### 3. Prevención IDOR/BOLA

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Creación: cita filtrada por clínica + owner | `_get_completed_appointment(appointment_id, clinic_id)` + chequeo de `owner_id` → 403/422 | ✅ |
| Responder: reseña filtrada por clínica | `review_repo.get_by_id(review_id, clinic_id)` → 404 si ajena | ✅ |
| Detalle: reseña filtrada por clínica | `get_by_id(review_id, clinic_id)` → 404 | ✅ |
| Listado clínico: filtrado por tenant | `list_clinical(clinic_id, branch_id, ...)` | ✅ |
| Respuesta no filtra el scope | Mensajes genéricos ("Reseña no encontrada", "La cita ya cuenta con una reseña") | ✅ |

### 4. Ownership por propietario

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Solo owner de la cita califica | `get_owner_id_by_user(user_id)` + comparación contra `appointment.owner_id` → `ReviewNotAuthorizedError` | ✅ |
| Owner no responde | `_require_respond_role` → role propietario ∉ set → 403 | ✅ |
| 404 (no 403) a reseñas ajenas | `get_by_id(id, clinic_id)` → None → 404 | ✅ |

### 5. Validación de entrada

| Control | Evidencia | Estado |
|---------|-----------|--------|
| `appointment_id` gt=0 | `Field(..., gt=0)` (schemas + dominio) | ✅ |
| `rating` acotado | `Field(..., ge=1, le=5)` | ✅ |
| `comment` acotado | `max_length=2048`, opcional | ✅ |
| `body` (respuesta) | `min_length=1`, `max_length=2048` | ✅ |
| `page`/`page_size` acotados | `page ge=1`, `page_size ge=1 le=100` | ✅ |

### 6. Deduplicación / estado

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Una reseña por cita | `exists_by_appointment()` → `ReviewDuplicateError` (409) + unique constraint `appointment_id` | ✅ |
| Una respuesta por reseña | `respond()` verifica respuesta existente → `ReviewRespondDuplicateError` (409) + unique constraint `review_id` | ✅ |
| Solo citas COMPLETED calificables | `_get_completed_appointment` → `ReviewNotCompletedError` (422) | ✅ |

### 7. Logs sin datos sensibles

- `logging`/`print(` en `review_router.py`, `review.py` (use case) y `review_schemas.py` → **0 coincidencias**. ✅

### 8. Respuesta sin campos internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| DTO Pydantic explícito | `ReviewRead.model_validate` / `ReviewResponseRead.model_validate`; schemas separados del ORM | ✅ |
| Sin password/token/secret | `password\|token\|secret` en `review_schemas.py` → **0 coincidencias** | ✅ |
| Sin stack trace | `detail=exc.message` con mensajes estáticos controlados | ✅ |

---

## Hallazgos Detectados

### Minor — no bloqueantes

| # | Hallazgo | Severidad | Recomendación |
|---|----------|-----------|---------------|
| S1 | Sin cabecera `Idempotency-Key`. El duplicate guard + unique constraint cubren el doble post. | Minor | Agregar opcional en Stage 2. |
| S2 | Sin rate-limiting explícito en `POST /reviews` y `/respond`. Protegido por auth + rol + ownership + duplicate guard. | Minor | Agregar `fastapi-limiter` en Stage 2 (out-of-scope). |

### Ningún Hallazgo Critical, Major ni Blocker

- ❌ No IDOR/BOLA explotable: `clinic_id` filtrado en `get_by_id` / `list_clinical` / `_get_completed_appointment`.
- ❌ No creación por no-owner: chequeo de `owner_id` → 403.
- ❌ No lectura de reseña ajena: tenant filter → 404.
- ❌ No exposición de passwords/tokens/stack traces.
- ❌ No logs de secretos.
- ❌ `clinic_id` y `user_id` nunca sobrescritibles por payload.

---

## Análisis de Ataques Potenciales

### Escenario 1 — IDOR: vet de clínica A responde reseña de clínica B
**Protección**: `review_repo.get_by_id(review_id, clinic_id)` filtra tenant.
**Resultado**: 404 "Reseña no encontrada para responder." ✅

### Escenario 2 — BOLA: cliente crea reseña para cita de otra clínica
**Protección**: `_get_completed_appointment(appointment_id, clinic_id)` → fuera de tenant → 403/422.
**Resultado**: 403 "No autorizado a calificar esta cita." ✅

### Escenario 3 — Cliente califica cita que es de otro owner
**Protección**: `get_owner_id_by_user(user_id) != appointment.owner_id` → `ReviewNotAuthorizedError`.
**Resultado**: 403. ✅

### Escenario 4 — Owner intenta responder
**Protección**: `_require_respond_role` → role propietario ∉ `_RESPOND_ROLES` → 403.
**Resultado**: 403 "Solo el equipo clínico de la sucursal puede responder reseñas." ✅

### Escenario 5 — Payload spoofing de tenant/owner
**Protección**: `clinic_id` y `user_id` del token; ignora cualquier valor del payload.
**Resultado**: el payload es ignorado para tenant/owner. ✅

### Escenario 6 — Doble reseña / doble respuesta
**Protección**: `exists_by_appointment()` / verificación de respuesta existente → 409 + unique constraint.
**Resultado**: 409 "La cita ya cuenta con una reseña." / "La reseña ya cuenta con una respuesta." ✅

### Escenario 7 — Reseña sobre cita no completada
**Protección**: `_get_completed_appointment` → `ReviewNotCompletedError`.
**Resultado**: 422. ✅

### Escenario 8 — Token fabricado / expirado
**Protección**: `get_current_access_user` → 401.
**Resultado**: 401. ✅

---

## Checklist de Verificación Final

- [x] 5 endpoints con auth/rol/tenant aplicados correctamente.
- [x] Rol clínico obligatorio para `respond` y listado clínico (propietario → 403).
- [x] Ownership de la cita verificado al crear (owner → 403 si no coincide).
- [x] IDOR/BOLA mitigado por `clinic_id` en `get_by_id` / `list_clinical` / `_get_completed_appointment`.
- [x] 404 (no 403) a reseñas ajenas en detalle/responder.
- [x] Deduplicación: 1 reseña/cita (409) + 1 respuesta/reseña (409).
- [x] Solo citas COMPLETED calificables (422).
- [x] `clinic_id`/`user_id` nunca sobrescritibles por payload.
- [x] Pydantic validation con `ge`/`le`/`gt`/`min_length`/`max_length`.
- [x] Paginación `page ge=1`, `page_size ge=1 le=100`.
- [x] 0 coincidencias de `logging`/`print(` en router + use case + schemas.
- [x] 0 coincidencias de `password`/`token`/`secret` en schema API.
- [x] 401/403/404/409/422 con mensajes genéricos, sin internas.
- [x] Tests de seguridad: `test_reviews_api.py` (20 tests, 401/403/404/409/422 por endpoint) + `test_review_service.py` (15).

---

## Decision Final

- Decision: APPROVED
- Evidencia: 5 endpoints con auth + rol + ownership + tenant isolation + IDOR/BOLA + validación + deduplicación + no filtrado de internas, cubiertos por 35 pytest (15 service + 20 API).

---

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No hay mojibake en el archivo.
