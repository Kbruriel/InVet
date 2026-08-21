# BE-009 Security Review

**Slice**: BE-009 (Consulta Médica Básica)  
**Review Date**: 2026-08-21  
**Tipo de review**: Seguridad  
**Estado global**: APPROVED

- Decision: APPROVED

---

## Executive Summary

BE-009 está **APPROVED** desde la perspectiva de seguridad. Los 3 endpoints implementados (POST/GET single/GET list `/consultations`) cubren los controles de autenticación, autorización por rol, aislamiento de tenant (clínica), control de ownership (propietario → mascota), validación de entrada, y deduplicación idempotente.

No se identificó ninguna vulnerabilidad explotable. Los controles IDOR/BOLA, ownership por dueño, y aislamiento por clínica están aplicados en el use case y verificados por los tests `test_consultation_ownership.py` y los cases de QA-009.

---

## Checklist OWASP — Backend

### 1. Autenticación en endpoints privados

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Todos los endpoints requieren auth | `Depends(get_current_access_user)` en los 3 endpoints (`consultation_router.py:178,244,290`) | ✅ |
| Token JWT válido | `get_current_access_user` valida exp, sub y type | ✅ |
| Error sin detalles internos | `detail="Token inválido"` + `WWW-Authenticate` del guard de auth | ✅ |

### 2. Autorización por rol y contexto

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Creación restringida a roles clínicos | `_require_write_role` valida `role in {"veterinarian","clinic","staff","admin"}` (`consultation_router.py:131-138`, `:191`) | ✅ |
| Read sin restricción de rol clínico | GET `/consultations/{id}` y GET `/consultations` solo requieren auth + tenant/ownership check | ✅ (propio owner puede leer su historial) |
| `clinic_id` tomado del token | `_get_clinic_id_from_user` extrae del claim, nunca del payload (`consultation_router.py:108-116`) | ✅ |
| `user_id` tomado del token | `_extract_user_id` normaliza `user_id`/`id` (`consultation_router.py:97-105`) | ✅ |

### 3. Prevención IDOR/BOLA

| Control | Evidencia | Estado |
|---------|-----------|--------|
| `clinic_id` filtrado en `get_by_id` | `ConsultationRepository.get_by_id(consultation_id, clinic_id)` — solo devuelve si coincide (`consultation_use_cases.py:144`) | ✅ |
| Creación valida pertenencia de la cita | `AppointmentRepository.get_by_id(data.appointment_id, data.clinic_id)` en use case (`consultation_use_cases.py:86`) → si es None, `OwnershipError` → 403 | ✅ |
| Pertenencia de la mascota validada | `pet_owner_resolver(data.pet_id, data.clinic_id)` compara `owner_id` vs owner del user (`consultation_use_cases.py:102`) | ✅ |
| Listado aislado por clínica | `list_by_pet(pet_id, clinic_id, ...)` (owner) / `ListConsultationsUseCase.execute(clinic_id=..., ...)` (clínico) | ✅ |
| Respuesta 403/404 no filtra el scope interno | Mensajes genéricos: `"La cita no existe o no es accesible."`, `"La consulta no existe."` | ✅ |

Evidencia de código en use case:
```python
# CreateConsultationUseCase.execute
if self.appointment_repo.get_by_id(data.appointment_id, data.clinic_id) is None:
    raise OwnershipError("La cita no existe o no es accesible.")
if not appointment.is_completed:
    raise AppointmentNotCompletedError(...)
if appointment.pet_id != data.pet_id:
    raise OwnershipError("La mascota no coincide con la cita.")
```

### 4. Ownership por propietario (endpoint público)

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Owner exige `pet_id` en list | `pet_id is None → 422` (`consultation_router.py:303-308`) | ✅ |
| Owner solo ve historial de su mascota | `pet.owner_id != owner_id → 404` (`consultation_router.py:310-315`) | ✅ |
| Owner solo ve detalle de consulta de su mascota | `pet.owner_id != owner_id → 404` (`consultation_router.py:265-271`) | ✅ |
| Clínicos ven su clínica completa | Sin restricción de `pet_id` para roles clínicos (`consultation_router.py:323-330`) | ✅ |

### 5. Idempotencia / deduplicación

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Una consulta por cita | `if consultation_repo.get_by_appointment(data.appointment_id, data.clinic_id): raise DuplicateConsultationError(...)` (`consultation_use_cases.py:107-110`) → 409 | ✅ |
| Sin token de idempotencia exigido | Aceptable para MVP: el duplicate guard + unique index en DB cubre el doble post | ✅ |

### 6. Validación de entrada

| Control | Evidencia | Estado |
|---------|-----------|--------|
| `appointment_id` gt=0 | `Field(..., gt=0)` (`consultation_schemas.py:19`) | ✅ |
| `pet_id` gt=0 | `Field(..., gt=0)` (`consultation_schemas.py:20`) | ✅ |
| `diagnosis` requerido 1–2000 | `Field(..., min_length=1, max_length=2000)` (`consultation_schemas.py:35-36`) | ✅ |
| `history` / `recommendaciones` acotadas | `max_length=3000` (`consultation_schemas.py:32-40`) | ✅ |
| `page`/`page_size` acotados | `page ge=1`, `page_size ge=1 le=100` (`consultation_router.py:285-288`) | ✅ |
| `pet_id` (filtro list) gt=0 | `Query(None, gt=0)` (`consultation_router.py:289`) | ✅ |

### 7. Logs sin datos sensibles

Verificación: grep de `log | print | logging` en `consultation_router.py` → **0 matches de import logging/print**. El router no escribe logs. ✅

### 8. Respuesta sin campos internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| DTO Pydantic explicito | `ConsultationRead.model_validate(result)` (sin `orm_mode` raw) | ✅ |
| Sin `password`, `token`, `secret` | Schemas `consultation_schemas.py` no incluyen esos campos | ✅ |
| Sin stack trace | `detail=exc.message` con mensajes estáticos controlados | ✅ |

### 9. Audit de `created_by`

| Control | Evidencia | Estado |
|---------|-----------|--------|
| `created_by` resuelto por tenant | `_resolve_created_by(internal_user_repo, user_id, clinic_id)` → `None` si el user es owner/externo (`consultation_router.py:141-151`) | ✅ |
| No se sobrescribe por payload | `created_by` no es campo de `ConsultationCreate` (schema sin ese campo) | ✅ |

### 10. Errores sin detalles internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| 401 generic | `"Token inválido"` | ✅ |
| 403 generic | `"La cita no existe o no es accesible."` / `"Solo un veterinario o staff de clínica puede registrar consultas."` | ✅ |
| 404 generic | `"La consulta no existe."` | ✅ |
| 409/422 controlados | `"La cita aún no está completada"` / `"Ya existe una consulta para esta cita."` | ✅ |

---

## Checklist OWASP — Frontend

| Control | Evidencia | Estado |
|---------|-----------|--------|
| No almacena tokens/sesiones de forma insegura | `ConsultationForm` no persiste datos locales | ✅ |
| No loguea payloads médicos | `consultation.ts` (shared api) sin `console.log` de body | ✅ |
| Usa `Auth` provider para header `Authorization` | `shared/api/client.ts` inyecta `Bearer` token | ✅ |
| Maneja 401/403 sin filtrar | `api client` mapea a `ApiError` sin exponer internals | ✅ |
| No confía en permisos visuales | El endpoint 403 en el backend es la fuente de verdad | ✅ |
| Validación duplicada en client | `consultation.ts` valida `diagnosis` no vacío antes del POST | ✅ |

---

## Hallazgos Detectados

### Minor — no bloqueantes

| # | Hallazgo | Severidad | Recomendación |
|---|----------|-----------|---------------|
| M1 | Sin token de idempotencia HTTP en `POST /consultations`. La deduplicación por `(appointment_id, clinic_id)` + unique index en DB protege contra doble post, pero no hay cabecera `Idempotency-Key`. | Minor | Documentar el comportamiento de duplicate en la API spec y agregar `Idempotency-Key` opcional en Stage 2. |
| M2 | Sin rate-limiting explícito en `POST /consultations`. Aceptable para MVP (protegido por duplicate guard + auth); añadir `fastapi-limiter` o rate-limit en gateway en Stage 2. | Minor | Agregar `fastapi-limiter` en `application.py` en Stage 2 (out-of-scope BE-009). |
| M3 | `_resolve_created_by` devuelve `None` cuando el caller es owner/externo. Aceptable: `created_by` es `nullable` por diseño; la auditoría fuerte (tabla `consultation_audit_log`) se deja para Stage 2. | Minor | Registrar en la matriz de Stage 2. |
| M4 | `GET /consultations` para owner exige `pet_id`, pero no valida `page`/`size` para el caso del owner. El `list_by_pet` sí aplica `page`/`size`, por lo que está cubierto por el repository. | Minor | Ya cubierto por `list_by_pet(pet_id, clinic_id, page, size)`. Sin acción. |

### Ningún Hallazgo Critical ni Blocker

- ❌ No IDOR/BOLA explotable (clinic_id filtrado en todos los `get_by_id` + use case + repository).
- ❌ No creación de consulta para cita de otra clínica (validado en `CreateConsultationUseCase`).
- ❌ No lectura de consulta de otra clínica / otro owner (validado en router + use case).
- ❌ No duplicación de consulta (duplicate guard + unique index).
- ❌ No exposición de contraseñas/tokens/stack traces.
- ❌ No logs de secretos.

---

## Análisis de Ataques Potenciales

### Escenario 1 — IDOR: leer consulta de otra clínica
**Intento**: `GET /consultations/{id}` con token de clínica A sobre consulta de clínica B.
**Protección**: `ConsultationRepository.get_by_id(consultation_id, clinic_id)` filtra `WHERE clinic_id = {token}`.
**Resultado**: `ConsultationNotFoundError` → 404 "La consulta no existe." ✅

### Escenario 2 — BOLA: crear consulta para cita ajena
**Intento**: `POST /consultations` con `appointment_id` de otra clínica.
**Protección**: `AppointmentRepository.get_by_id(appointment_id, clinic_id)` en use case → None si no coincide → `OwnershipError` → 403.
**Resultado**: 403 "La cita no existe o no es accesible." ✅

### Escenario 3 — Owner lee consulta de otra mascota
**Intento**: `GET /consultations/{id}` con token de owner A sobre consulta de owner B.
**Protección**: router resuelve `owner_id` del token y compara `pet.owner_id != owner_id → 404` (`consultation_router.py:265-271`).
**Resultado**: 404 "La consulta no existe." ✅

### Escenario 4 — Doble post / replay
**Intento**: `POST /consultations` dos veces con el mismo `appointment_id`.
**Protección**: duplicate guard `get_by_appointment` + unique index `(appointment_id, clinic_id)` → `DuplicateConsultationError` → 409.
**Resultado**: 409 (segundo request en adelante) ✅

### Escenario 5 — Token falso
**Intento**: `POST /consultations` con JWT fabricado.
**Protección**: `get_current_access_user` valida firma + exp + sub → 401.
**Resultado**: 401 "Token inválido." ✅

### Escenario 6 — Owner crea consulta
**Intento**: `POST /consultations` con rol `owner`.
**Protección**: `_require_write_role` → `role not in _WRITE_ROLES` → 403.
**Resultado**: 403 "Solo un veterinario o staff de clínica puede registrar consultas." ✅

---

## Checklist de Verificación Final

- [x] Contrato BE-009 validado con seguridad (3 endpoints).
- [x] Permisos y rol validados en `POST /consultations`.
- [x] IDOR/BOLA mitigado por `clinic_id` en `get_by_id` (use case + repository).
- [x] Ownership por owner validado en `GET /consultations` y `GET /consultations/{id}`.
- [x] Deduplicación por `(appointment_id, clinic_id)`.
- [x] `created_by` resuelto por tenant, no sobrescritible por payload.
- [x] Pydantic validation con `min_length`/`max_length` en campos de texto.
- [x] Paginación `page ge=1`, `page_size le=100`.
- [x] 0 logs de secretos en router.
- [x] 401/403/404/409/422 con mensajes genéricos.
- [x] DTOs Pydantic (`ConsultationRead`) sin campos ORM internos.
- [x] Frontend sin almacenamiento inseguro de tokens/payloads médicas.

---

## Decision Final

```
Decision: APPROVED
Evidencia:
  - 3 endpoints con `get_current_access_user` (auth obligatoria).
  - `clinic_id` extraído del token y filtrado en `get_by_id` (tenant isolation).
  - IDOR/BOLA mitigado por `get_by_id(entity_id, clinic_id)` en use case y repository.
  - Ownership por owner validado en `GET /consultations` y `GET /consultations/{id}`.
  - Deduplicación por `(appointment_id, clinic_id)` con unique index + 409.
  - Rol clínico obligatorio para `POST /consultations` (403 si owner).
  - Pydantic validation con `min_length=1` y `max_length` acotados.
  - Paginación `page ge=1`, `page_size ge=1 le=100`.
  - 0 logs de secretos (verified via grep).
  - 401/403/404/409/422 con mensajes genéricos.
  - `ConsultationRead.model_validate()` (DTO, sin ORM raw).
  - Frontend sin almacenamiento inseguro de tokens/payloads médicas.
```

---

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No hay mojibake en el archivo.

---

*Este documento cumple con el formato `review_findings_template.md` del slice BE-009.*
*Siguiente gate: `/run-checks BE-009` (ya ejecutado y APPROVED) → `/update-docs BE-009`.*
