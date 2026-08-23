# BE-010 Security Review

**Slice**: BE-010 (Recetas, tratamientos y recordatorios)
**Review Date**: 2026-08-22
**Tipo de review**: Seguridad
**Estado global**: APPROVED

- Decision: APPROVED

---

## Executive Summary

BE-010 está **APPROVED** desde la perspectiva de seguridad. Los 3 endpoints implementados (POST `/prescriptions`, GET `/prescriptions/{id}`, GET `/prescriptions?pet_id=`) cubren autenticación obligatoria, autorización por rol (solo roles clínicos escriben), aislamiento de tenant (clínica) en todas las consultas, control de ownership (propietario → mascota), deduplicación idempotente por consulta, validación de entrada con Pydantic y paginación acotada.

No se identificó ninguna vulnerabilidad explotable. IDOR/BOLA, ownership y aislamiento por clínica están aplicados en router + use case y verificados por `test_prescriptions_idor.py`, `test_prescriptions_auth.py`, la suite UIA (C4/C7 access) y las AC de QA-010.

---

## Checklist OWASP — Backend

### 1. Autenticación en endpoints privados

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Todos los endpoints requieren auth | `Depends(get_current_access_user)` en los 3 endpoints (`prescription_router.py:181,239,280`) | ✅ |
| Token JWT válido | `get_current_access_user` valida exp, sub y type (core.security) | ✅ |
| user_id ausente → 401 | `_extract_user_id` lanza 401 "No se pudo identificar al usuario autenticado." (`prescription_router.py:108-116`) | ✅ |

### 2. Autorización por rol y contexto

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Escritura restringida a roles clínicos | `_WRITE_ROLES = {"veterinarian","clinic","staff","admin"}`; `_require_write_role` → 403 (`prescription_router.py:36,141-148,194`) | ✅ |
| Lectura sin restricción de rol clínico | GETs solo requieren auth + tenant/ownership (`prescription_router.py:237-263,274-311`) | ✅ (owner ve sus recetas) |
| `clinic_id` tomado del token, nunca del payload | `_get_clinic_id_from_user` extrae del claim; `to_domain_create(payload, clinic_id, ...)` lo inyecta (`prescription_router.py:119-127`, `prescription_schemas.py:114-137`) | ✅ |
| `created_by` resuelto de server-side | `_resolve_created_by(internal_user_repo, user_id, clinic_id)`; no es campo editable del payload (no incluido en `PrescriptionCreate` API schema) | ✅ |

### 3. Prevención IDOR/BOLA

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Creación: consulta filtrada por clínica | `consultation_repository.get_by_id(data.consultation_id, data.clinic_id)` (`prescription_use_cases.py:69-75`) → 422 genérico si no coincide | ✅ |
| Creación: cita filtrada por clínica | `appointment_repository.get_by_id(consultation.appointment_id, data.clinic_id)` (`prescription_use_cases.py:77-84`) | ✅ |
| Creación: mascota debe coincidir | `consultation.pet_id != data.pet_id → OwnershipError` → 403 (`prescription_use_cases.py:86-87`) | ✅ |
| Detalle/listado: receta filtrada por clínica | `repository.get_by_id(prescription_id, clinic_id)` (`prescription_use_cases.py:122`); `list_by_pet(pet_id, clinic_id, ...)` (`prescription_use_cases.py:142-143`) | ✅ |
| Duplicado aislado por tenant | `exists_by_consultation(data.consultation_id, data.clinic_id)` (`prescription_use_cases.py:89-94`) | ✅ |
| Respuesta no filtra el scope | Mensajes genéricos: "La consulta no existe o no es accesible.", "La receta no existe." | ✅ |

### 4. Ownership por propietario

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Owner: detalle solo de sus mascotas | `owner_id is not None → _assert_owner_pet(pet_repo, result.pet_id, owner_id)` → 404 (`prescription_router.py:260-261,159-166`) | ✅ |
| Owner: listado exige mascota propia | `pet_id` obligatorio (`Query(..., gt=0)`) + `_assert_owner_pet(pet_repo, pet_id, owner_id)` → 404 (`prescription_router.py:275,294-295`) | ✅ |
| Clínicos: sin restricción de owner | `owner_id is None` (sin owner vinculado) → omite el assert; filtran por `clinic_id` | ✅ |
| 404 (no 403) al owner ajenas | `_assert_owner_pet` responde 404 "La receta no existe." — no confirma existencia | ✅ |

### 5. Idempotencia / deduplicación

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Una receta por consulta | `exists_by_consultation` + `UniqueConstraint("consultation_id")` en migración `a010` → 409 "Ya existe una receta registrada para esta consulta." | ✅ |
| Sin token de idempotencia exigido | Aceptable para MVP: duplicate guard + unique index cubren el doble post | ✅ |

### 6. Validación de entrada

| Control | Evidencia | Estado |
|---------|-----------|--------|
| `consultation_id` / `pet_id` gt=0 | `Field(..., gt=0)` (`prescription_schemas.py:61-64`) | ✅ |
| `diagnosis` 1–2000 | `Field(..., min_length=1, max_length=2000)` (`prescription_schemas.py:71`) | ✅ |
| `treatment_notes` / `instructions` / `note` acotadas | `max_length=3000/2000/1000` (`prescription_schemas.py:41,49,72-74`) | ✅ |
| Colecciones acotadas | `items/treatments/reminders max_length=50` (`prescription_schemas.py:75-83`) | ✅ |
| `page`/`page_size` acotados | `page ge=1`, `page_size ge=1 le=100` (`prescription_router.py:276-279`) | ✅ |

### 7. Logs sin datos sensibles

- `logging`/`print(` en `prescription_router.py` + `prescription_use_cases.py` → **0 coincidencias**. El slice no escribe logs. ✅

### 8. Respuesta sin campos internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| DTO Pydantic explícito | `PrescriptionRead.model_validate(result)`; schemas separados del ORM | ✅ |
| Sin password/token/secret | `password\|token\|secret` en `prescription_schemas.py` → **0 coincidencias** | ✅ |
| Sin stack trace | `detail=exc.message` con mensajes estáticos controlados | ✅ |

### 9. Errores sin detalles internos

| Control | Evidencia | Estado |
|---------|-----------|--------|
| 401 | "No se pudo identificar al usuario autenticado." | ✅ |
| 403 | "Solo un veterinario o staff de clínica puede prescribir." / "La mascota no coincide con la consulta." | ✅ |
| 404 | "La receta no existe." / "La consulta no existe o no es accesible." | ✅ |
| 409 / 422 | "Ya existe una receta registrada para esta consulta." / "Solo se puede registrar una receta cuando la cita está completada..." | ✅ |

---

## Checklist OWASP — Frontend

| Control | Evidencia | Estado |
|---------|-----------|--------|
| No almacena tokens/payloads médica local | `localStorage`/`sessionStorage`/`document.cookie` en páginas + API client → **0 coincidencias** | ✅ |
| No loguea payloads médicas | `console.log/error/warn` en `prescription.ts` + 3 páginas → **0 coincidencias** | ✅ |
| Sin inyección HTML | `dangerouslySetInnerHTML` → **0 coincidencias**; React escapa por defecto | ✅ |
| Usa shared API client con `Authorization` | `prescription.ts` consume `client` (`shared/api`) que inyecta Bearer | ✅ |
| No confía en permisos visuales | 403/404 del backend son la fuente de verdad; `ErrorBanner` solo renderiza `detail` | ✅ |
| Estados de error UI sin filtrar | `page.tsx:256` `ErrorBanner` muestra el `detail` genérico del API | ✅ |

---

## Hallazgos Detectados

### Minor — no bloqueantes

| # | Hallazgo | Severidad | Recomendación |
|---|----------|-----------|---------------|
| S1 | Sin cabecera `Idempotency-Key` en `POST /prescriptions`. El duplicate guard + `UniqueConstraint("consultation_id")` cubren el doble post; sin idempotencia explícita. | Minor | Documentar comportamiento de 409; agregar `Idempotency-Key` opcional en Stage 2 (mismo M1 de BE-009). |
| S2 | Sin rate-limiting explícito en `POST /prescriptions`. Protegido por auth + rol + duplicate guard; suficiente para MVP. | Minor | Agregar `fastapi-limiter` en aplicación en Stage 2 (out-of-scope del slice). |
| S3 | `_get_clinic_id_from_user` lanza **403** cuando el usuario no tiene `clinic_id`. Un rol clínico sin clínica (marginal) vería un 403 genérico; sin filtrado de info. | Minor | Aceptable: mensaje genérico "El usuario no tiene una clínica asociada." Sin acción. |
| S4 | `_assert_owner_pet` usa `pet_repo.get_pet_by_id(pet_id)` sin `clinic_id` (compara solo `owner_id`). El scope final es `owner_id` (correcto para owner) y `clinic_id` (correcto para clínicos, vía use case); no hay fuga. | Minor | Documentar; si el `pet repository` soporte `get_pet_by_id(pet_id, clinic_id)`, alinear en refactoring futuro. |

### Ningún Hallazgo Critical, Major ni Blocker

- ❌ No IDOR/BOLA explotable: `clinic_id` filtrado en `get_by_id` (creación, detalle, listado, duplicate).
- ❌ No creación por owner: `_require_write_role` → 403 (role `"user"` ∉ `_WRITE_ROLES`).
- ❌ No lectura de receta ajena (otra clínica u otro owner): tenant filter + `_assert_owner_pet` → 404.
- ❌ No duplicación: `exists_by_consultation` + unique index → 409.
- ❌ No exposición de passwords/tokens/stack traces.
- ❌ No logs de secretos.
- ❌ `clinic_id`/`created_by` nunca sobrescritibles por payload.

---

## Análisis de Ataques Potenciales

### Escenario 1 — IDOR: vet de clínica A lee receta de clínica B
**Intento**: `GET /prescriptions/{id}` con token de clínica A sobre receta de clínica B.
**Protección**: `GetPrescriptionUseCase.execute(id, clinic_id)` → `repository.get_by_id(prescription_id, clinic_id)` filtra tenant.
**Resultado**: `PrescriptionNotFoundError` → 404 "La receta no existe." ✅

### Escenario 2 — BOLA: vet crea receta para consulta de otra clínica
**Intento**: `POST /prescriptions` con `consultation_id` de otra clínica.
**Protección**: `consultation_repository.get_by_id(consultation_id, data.clinic_id)` → None → `ConsultationInvalidError`.
**Resultado**: 422 "La consulta no existe o no es accesible." ✅

### Escenario 3 — Owner lee receta de otra mascota
**Intento**: `GET /prescriptions/{id}` con token owner A sobre receta de owner B.
**Protección**: `_assert_owner_pet(pet_repo, result.pet_id, owner_id)` compara `pet.owner_id != owner_id` (`prescription_router.py:159-166`).
**Resultado**: 404 "La receta no existe." ✅

### Escenario 4 — Listado cruzado
**Intento**: `GET /prescriptions?pet_id=X` con token owner A sobre mascota de owner B (misma/distinta clínica).
**Protección**: `_assert_owner_pet` (404) + `list_by_pet(pet_id, clinic_id)` (tenant).
**Resultado**: 404 / lista vacía de su tenant. ✅

### Escenario 5 — Doble post / replay
**Intento**: `POST /prescriptions` dos veces con el mismo `consultation_id`.
**Protección**: `exists_by_consultation` + `UniqueConstraint("consultation_id")` en `a010` → `DuplicatePrescriptionError`.
**Resultado**: 409 (segundo request en adelante) ✅

### Escenario 6 — Owner intenta prescribir
**Intento**: `POST /prescriptions` con token de owner (role `"user"`).
**Protección**: `_require_write_role` → role ∉ `_WRITE_ROLES` → 403.
**Resultado**: 403 "Solo un veterinario o staff de clínica puede prescribir." ✅

### Escenario 7 — Payload spoofing de tenant/auditoría
**Intento**: incluir `clinic_id` o `created_by` en el JSON del POST.
**Protección**: la API `PrescriptionCreate` acepta `clinic_id` opcional pero `to_domain_create(payload, clinic_id, created_by)` **sobrescribe** con el valor resuelto del token; `created_by` no existe en el schema API.
**Resultado**: el payload es ignorado para tenant/auditoría. ✅

### Escenario 8 — Token fabricado / expirado
**Intento**: JWT inválido en cualquiera de los 3 endpoints.
**Protección**: `get_current_access_user` (core.security) → 401.
**Resultado**: 401. ✅

---

## Checklist de Verificación Final

- [x] Contrato BE-010 validado con seguridad (3 endpoints).
- [x] Rol clínico obligatorio para `POST /prescriptions` (owner → 403).
- [x] IDOR/BOLA mitigado por `clinic_id` en `get_by_id` (creación/detalle/listado/duplicate).
- [x] Ownership por owner en `GET /prescriptions/{id}` y `GET /prescriptions?pet_id=`.
- [x] Deduplicación por `consultation_id` + unique index (`a010`) → 409.
- [x] `created_by` resuelto de server-side, no sobrescritible.
- [x] Pydantic validation con `min_length`/`max_length`/`gt=0`/colecciones acotadas.
- [x] Paginación `page ge=1`, `page_size ge=1 le=100`.
- [x] 0 coincidencias de `logging`/`print(` en router + use cases.
- [x] 0 coincidencias de `console.log`/`dangerouslySetInnerHTML`/`localStorage` en páginas + API client.
- [x] 0 coincidencias de `password`/`token`/`secret` en schema API.
- [x] 401/403/404/409/422 con mensajes genéricos, sin internas.
- [x] Tests de seguridad: `test_prescriptions_idor.py`, `test_prescriptions_auth.py` (25 passed en suite fresca) + UIA C4/C7 (18/18) + APIA (10/10).

---

## Decision Final

```
Decision: APPROVED
Evidencia:
  - 3 endpoints con `get_current_access_user` (auth obligatoria).
  - `_WRITE_ROLES` en POST (owner → 403); lectura autenticada con tenant isolation.
  - `clinic_id` extraído del token y filtrado en `get_by_id`/`list_by_pet`/`exists_by_consultation`.
  - `_assert_owner_pet` en detalle/listado (owner → 404 sin filtrar existencia).
  - Deduplicación por `(consultation_id)` con unique index en `a010` → 409.
  - `created_by` resuelto por tenant, no sobrescritible por payload.
  - Pydantic validation + paginación acotada (page ge=1, page_size 1..100).
  - 0 leaks: passwords/tokens/stack traces/logs.
  - Frontend: 0 console.log, 0 dangerouslySetInnerHTML, 0 storage local.
  - 401/403/404/409/422 con mensajes genéricos.
  - 25 pytest (create/read/idor/auth) + 18 UIA + 10 APIA en verde.
```

---

## Siguiente paso recomendado

Flujo de gates (`13_agents_architecture_and_gate_flow.md`): `review` ✅ → `clean-architecture` ✅ → `security` ✅ (este documento) → siguiente gate del pipeline.

Si el pipeline exige cierre de slice, el próximo paso es ejecutar el gate de cierre (`/run-checks BE-010` o `/update-docs BE-010`) según la matriz de continuidad; si el flujo es directo, cerrar BE-010 y abrir el siguiente slice.

---

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No hay mojibake en el archivo.

---

*Este documento cumple con el formato de `BE-00x-security-review.md` (BE-009 como referencia).*
