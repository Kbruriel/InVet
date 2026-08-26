---
encoding: UTF-8
artifact: review_findings
---

# Hallazgos de revisión de slice BE-012

## Resumen

- Slice: BE-012 — Calificaciones y comentarios (reseñas)
- Tipo de review: Revisión funcional (backend: contrato API + seguridad + arquitectura + evidencia)
- Estado: `RESOLVED`
- Decision: `APPROVED`

## Alcance revisado (backend)

- Entidad de dominio: `backend/app/domain/entities/review.py` — `Review`, `ReviewResponse`, `ReviewCreate`, `ReviewRespond`.
- ORM: `backend/app/infrastructure/database/models/review.py`.
- Migración Alembic: `backend/alembic/versions/a012_reviews.py` (a012, reversible, único `appointment_id`).
- Repositorio: `backend/app/data/review_repo.py` — ABC `ReviewRepository` + `ReviewRepositoryImpl`.
- Casos de uso: `backend/app/application/use_cases/review.py` — `ReviewService` + 7 excepciones de dominio.
- Schemas API: `backend/app/api/schemas/review_schemas.py`.
- Router: `backend/app/api/v1/routers/review_router.py` (5 endpoints, registrado en `app/api/v1/router.py`).
- Pruebas: `backend/app/tests/test_review_service.py` (15) + `backend/app/tests/api/test_reviews_api.py` (20) → **35 passed**.

## Resumen ejecutivo

La implementación backend está **completa y coherente**. Los 5 endpoints de reseñas (crear, detalle, listado público, listado clínico, responder) tienen contratos consistentes y el mapeo de errores de dominio a HTTP es correcto (201, 200, 401, 403, 404, 409, 422). La lógica de negocio vive en `application/use_cases/review.py`; los routers son adaptadores delgados. El tenant isolation se aplica en todos los endpoints autenticados. Ningún defecto productivo fue encontrado.

## Evidencia fresca de pruebas

- Suite combinada (service + API): **35/35 passed**.
- Suite completa del repo: **355 passed, 1 skipped, 2 deselected** (pre-existing, no relacionados con BE-012).
- Migración: `alembic upgrade head` → head `a012`. `downgrade -1 && upgrade head` → sin errores (verificado contra SQLite).

## Hallazgos por severidad

### Blocker / Critical / Major

- Ninguno.

### Minor

- **m1 — Idempotencia explícita no implementada.**
  El duplicate guard (`exists_by_appointment`) + unique constraint `appointment_id` cubren la doble reseña. Mismo patrón que BE-011. Aceptable para MVP.

- **m2 — `ReviewCreate.user_id` es opcional en el domain model.**
  El router no expone `user_id` como campo del payload (viene del token). El dominio lo permite para tests. Sin riesgo.

## Archivos afectados (backend)

- `backend/app/domain/entities/review.py`
- `backend/app/infrastructure/database/models/review.py`
- `backend/alembic/versions/a012_reviews.py`
- `backend/app/data/review_repo.py`
- `backend/app/application/use_cases/review.py`
- `backend/app/api/schemas/review_schemas.py`
- `backend/app/api/v1/routers/review_router.py`
- `backend/app/api/v1/router.py`
- `backend/app/tests/test_review_service.py`
- `backend/app/tests/api/test_reviews_api.py`

## Notas de seguridad

- **Autenticación**: los endpoints no públicos requieren `get_current_access_user`; 401 sin token.
- **Autorización**: `_RESPOND_ROLES = {veterinarian, clinic, staff, admin, internal}`; `_require_respond_role` → 403; `_require_clinic_role` → 403 en listado clínico.
- **IDOR/BOLA**: `clinic_id` resuelto del token; `list_clinical(clinic_id)` y `get(review_id, clinic_id)` filtran por tenant; 404 en reseña ajena.
- **Ownership**: propietario no puede responder (403); personal de otra sucursal no puede leer (404).
- **Validación**: `rating ge=1 le=5`, `comment max_length=2048`, `body min_length=1 max_length=2048`.
- **Sin filtrado de info interna**: mensajes genéricos y estables.
- **Public listing**: `GET /reviews/public/{branch_id}` no requiere auth; sucursal inexistente → 404.

## Clean architecture

- **Domain**: `Review`/`ReviewResponse` como Pydantic puro; sin dependencia de ORM ni framework.
- **Application**: `ReviewService` inyecta repositorios por constructor; desacoplado.
- **Infrastructure**: implementación ORM aislada; FKs + unique constraint en migración `a012`.
- **API**: routers como adaptadores delgados; mapeo de `ReviewError` a HTTP; listado paginado con `meta`.

## Comparison con criterios

| Criterio | Estado |
|---|---|
| 5 endpoints con contratos (201/200/403/404/409/422) | ✅ |
| Routers sin lógica de negocio | ✅ Lógica en `review.py` |
| No se exponen modelos ORM | ✅ `ReviewRead.model_validate` |
| Listado paginado con `meta` | ✅ `ReviewList` |
| Errores consistentes, sin info interna | ✅ mensajes estáticos |
| Seguridad IDOR/BOLA por rol y clínica | ✅ `_require_respond_role`, tenant filter |
| Pruebas happy + negative + seguridad | ✅ 35 pytest |
| Migración `a012` reversible | ✅ upgrade/downgrade verificado |
| Rating recalcular en transacción | ✅ `upsert_rating_summary` |

## Checklist de revisión

- [x] Contrato BE validado.
- [x] Casos de uso validados (15 pytest).
- [x] Router validado (20 pytest).
- [x] Arquitectura revisada.
- [x] Permisos e IDOR/BOLA revisados.
- [x] Evidencia documentada.
- [x] Migración reversible.
- [x] Findings de QA: pendiente de QA-012 (FE/QA aún open).

## Decision final

- Decision: `APPROVED`
- Evidencia: 35/35 pytest pass, migración `a012` reversible verificada, contrato API coherente, seguridad IDOR/BOLA + rol + tenant aplicados.
- Sin hallazgos bloqueantes, críticos ni mayores.
- Nota: FE-012 y QA-012 están pendientes; quedan en su propio slice.

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
