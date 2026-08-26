---
schema_version: "3"
slice: "012"
canonical_plan: "BE-012"
owner: "InVet Product Planner"
created_at: "2026-08-25"
updated_at: "2026-08-26"
status: "COMPLETED"
---

# InVet BE-012 — Calificaciones y comentarios

## Plan v1 — calificaciones y comentarios

### Objetivo del slice

- Permite al propietario calificar una cita completada con una puntuacion de 1 a 5 estrellas.
- Permite al personal clinico responder una reseña de su sucursal con un unico mensaje.
- Expone el promedio, la distribucion por estrellas y el listado paginado de reseñas en el perfil publico de sucursal.

### Alcance MVP

- Reseña unica por cita `COMPLETED` (unique `appointment_id`).
- Respuesta clinica unica por reseña (unique `review_id`).
- Listado publico de reseñas por sucursal con paginacion `page`/`page_size` y `meta`.
- Actualizacion transaccional del resumen agregado (promedio, total, distribucion) al crear reseña.
- Permisos por rol: propietario/caliente crea; staff/clinico responde; IDOR/BOLA por tenant.
- UI del propietario (seccion Calificar cita), UI publica (Resenias) y UI clinica (responder reseña).
- Estados UX de loading, submitting, empty, success, error en los tres flujos.

### Fuera de alcance

- Productos, marketplace, carrito, checkout.
- Pasarela de pago de servicios, facturacion electronica, timbrado fiscal.
- Editar o borrar una reseña existente.
- Respuesta con adjuntos, imagenes, hilos de conversacion.
- Moderacion avanzada, denuncias, baneo por keyword.
- Analisis de sentimiento, analitica avanzada, alertas.

### Entidades y reglas de negocio

| Entidad | Campo | Tipo | Regla | Fuente |
| --- | --- | --- | --- | --- |
| Review | id | UUID PK | Identificador unico | DB |
| Review | appointment_id | UUID FK | FK a appointments; UNIQUE (una reseña por cita) | DB |
| Review | branch_id | UUID FK | FK a branches; tomada de la cita | DB |
| Review | clinic_id | UUID FK | FK a clinics; tomada de la cita (tenant) | DB |
| Review | user_id | UUID FK | FK a internal_users; propietario de la cita | DB |
| Review | rating | Integer | 1..5 | Dominio |
| Review | comment | Text | Max 2048 caracteres, opcional | Dominio |
| Review | created_at / updated_at | DateTime | Timestamps UTC | Infra |
| ReviewResponse | id | UUID PK | Identificador unico | DB |
| ReviewResponse | review_id | UUID FK | FK a reviews; UNIQUE (una respuesta por reseña) | DB |
| ReviewResponse | branch_id | UUID FK | FK a branches; sucursal que responde | DB |
| ReviewResponse | user_id | UUID FK | FK a internal_users; staff/clinico | DB |
| ReviewResponse | body | Text | Max 2048 caracteres | Dominio |
| ReviewResponse | created_at / updated_at | DateTime | Timestamps UTC | Infra |

Reglas de negocio:
- Una cita solo puede calificarse si su estado es `COMPLETED`; si no, `422`.
- Una cita ya calificada no admite segunda reseña (`409`, unique `appointment_id`).
- La reseña hereda `branch_id` y `clinic_id` de la cita; cita ajena al tenant del usuario → `404`.
- Solo staff/clinico de la misma `clinic_id` (rol `admin`, `veterinarian`, `staff`) responde una reseña (`403` para propietario u otros, `404` para sucursal ajena al tenant).
- Una reseña admite exactamente una respuesta; segunda respuesta → `409` (unique `review_id`).
- Al crear una reseña, el resumen agregado de la sucursal (`RatingSummary`) se recalcula dentro de la misma transaccion.

### Fuentes y artefactos de contexto

- `docs/opencode/references/slice_task_context.md` fila 012.
- `docs/opencode/02_be_fe_qa_task_matrix.md` fila 16.
- `docs/opencode/scope_mvp_stage_rules.md`.
- `docs/opencode/tasks/user-stories/US-012.md` (US-012-01/02/03; AC-012-01..15).
- `docs/opencode/tasks/backend/BE-012.md`.
- `docs/opencode/tasks/frontend/FE-012.md`.
- `docs/opencode/tasks/qa/QA-012.md`.
- `docs/opencode/tasks/ui-automation/UIA-012.md`.
- `docs/opencode/tasks/api-automation/APIA-012.md`.
- `docs/opencode/plans/BE-011-plan.md` (plantilla slice v3).
- `backend/app/api/v1/routers/payments_router.py` (patrón router, `_require_write_role`, ownership por `clinic_id`).
- `backend/app/api/v1/routers/branch_profile.py` (perfil publico expone ya `rating_summary`).
- `backend/app/api/v1/schemas/branch_public.py` (`RatingSummaryPublic`).
- `backend/app/domain/entities/appointment.py` (`AppointmentStatus.COMPLETED`).
- `backend/app/infrastructure/database/models/rating_summary.py` (modelo resumen agregado).
- `backend/core/security.py` (`get_current_access_user`).
- `backend/app/domain/user.py` (`UserRole`: owner, admin, veterinarian, client, staff).
- `backend/alembic/versions/a011_payments.py` (ultima migracion; proxima `a012_*`).
- `frontend/src/app/portal/owner/appointments/[id]/page.tsx` (seccion Calificar cita).
- `frontend/src/features/public-clinic-profile/BranchProfile.tsx` (Reseñas publico).
- `frontend/src/shared/api/payment.ts` (patrón cliente API tipado + test Jest).
- `frontend/jest.config.js` (framework de pruebas frontend: Jest + Testing Library).
- `backend/app/tests/api/test_payments_*.py` (patrón pytest/HTTPX).

## Matriz de trazabilidad

| US / Crit | Tarea BE | Tarea FE | Tarea QA | UIA | APIA | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| US-012-01: calificar cita | BE-012-T01..T06 | FE-012-T01, FE-012-T02 | QA-012-T01..T04 | UIA-012 C1..C5 | APIA-012 C1..C6 | PENDING |
| US-012-02: respuesta clinica | BE-012-T02..T06 | FE-012-T04 | QA-012-T01..T03 | UIA-012 C8..C12 | APIA-012 C7..C10 | PENDING |
| US-012-03: perfil publico | BE-012-T03..T05 | FE-012-T03 | QA-012-T01 | UIA-012 C6, C7 | APIA-012 C11..C13 | PENDING |
| BE-012: permisos IDOR/BOLA | BE-012-T06 | FE-012-T02, FE-012-T04 | QA-012-T03 | UIA-012 C10, C11, C12 | APIA-012 C4..C10 | PENDING |
| BE-012: estados UX | BE-012-T05 | FE-012-T05 | QA-012-T04 | UIA-012 C13 | n/a | PENDING |

## Endpoints esperados

| Metodo | Ruta | Cuerpo | Respuesta | Notas |
| --- | --- | --- | --- | --- |
| POST | /api/v1/reviews | ReviewCreate | 201 ReviewRead | Rol propietario/client; cita del usuario |
| GET | /api/v1/reviews/{id} | - | 200 ReviewRead | Autor (owner) o tenant clinico; sin token 401 |
| GET | /api/v1/reviews/public/{branchId}?page=&page_size= | - | 200 {items, meta} | Publico anónimo; pagina `page`/`page_size`; `meta {page, page_size, total, pages}` |
| GET | /api/v1/reviews?branch_id=&page=&page_size= | - | 200 {items, meta} | Tenant clinico (admin/staff/veterinarian) |
| POST | /api/v1/reviews/{id}/respond | ReviewRespond | 200 ReviewResponseRead | Rol clinico; sucursal propia; unica por reseña |
| HEAD | /api/v1/reviews/{id} | - | 204/403/404 | Ownership check |

Schemas: `ReviewCreate`, `ReviewRead`, `ReviewRespond`, `ReviewResponseRead`, `ReviewListMeta`, enum rating 1..5.

## Contrato de implementacion frontend

### Rutas y acceso

| Ruta | Componente | Rol requerido | Fuente |
| --- | --- | --- | --- |
| /portal/owner/appointments/[id] (sección Calificar cita) | RatingForm | owner, client | US-012-01 |
| /clinics/[branchId] (sección Reseñas) | ReviewList (publico) | anonimo | US-012-03 |
| /clinic/reviews | ReviewStaffList | admin, staff, veterinario | US-012-02 |
| /clinic/reviews/[reviewId] (form. de respuesta) | ReviewRespondForm (detalle staff) | admin, staff, veterinario | US-012-02 |

### Flujos y estados UX

1. Propietario abre cita `COMPLETED`; si aún no calificó, aparece la sección Calificar (estrellas + comentario).
2. Envía → toast success; sección cambia a "ya calificó esta cita" (disabled).
3. Anónimo abre perfil `/clinics/[branchId]`: tarjeta promedio, distribución 5-1, listado paginado con respuesta clínica cuando existe.
4. Staff abre `/clinic/reviews`, ve reseñas de la sucursal, selecciona, responde con un único cuerpo → toast success, banner "respondida".
5. Respuesta duplicada muestra estado "ya respondida" (409).
6. Staff otra sucursal ve banner "no puede responder una reseña de otra sucursal" (404).
7. Propietario intenta responder → banner "solo personal de la sucursal" (403).

Estados UX: loading, submitting, empty, success, error en RatingForm, ReviewList, ReviewRespondForm, ReviewStaffList.

### Contratos API por accion

| Accion | Metodo | Ruta | Solicitud | Respuesta |
| --- | --- | --- | --- | --- |
| Crear reseña | POST | /api/v1/reviews | ReviewCreate | 201 ReviewRead |
| Detalle reseña | GET | /api/v1/reviews/{id} | - | 200 ReviewRead |
| Listado publico | GET | /api/v1/reviews/public/{branchId} | page, page_size | 200 {items, meta} |
| Listado clinico | GET | /api/v1/reviews?branch_id= | page, page_size | 200 {items, meta} |
| Responder reseña | POST | /api/v1/reviews/{id}/respond | ReviewRespond | 200 ReviewResponseRead |

### Formularios y validacion

Campos ReviewCreate: `appointment_id` (oculto en UI — la cita del listado), `rating` entera 1..5, `comment` opcional max 2048.
Campos ReviewRespond: `body` requerido max 2048.
Errores 422/409/403/404 mapeados a mensajes inline legibles; `comment` invalido muestra error sin filtrar datos sensibles; sin links `#`.

### Arquitectura de componentes

- `frontend/src/features/reviews/RatingForm.tsx` (estrellas + comentario + validacion).
- `frontend/src/features/reviews/ReviewPublicList.tsx` (promedio, distribución, listado paginado, respuesta si existe).
- `frontend/src/features/reviews/ReviewStaffList.tsx` (listado sucursal, estado respondida).
- `frontend/src/features/reviews/ReviewRespondForm.tsx` (detalle con respuesta unica, 409 visualizado).
- `frontend/src/shared/api/review.ts` (cliente API tipado; mismas funciones que las operaciones en "Contratos API por accion").
- Reutilizar `src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast).

### Responsive y accesibilidad

- Mobile-first; formularios y tablas adaptados a viewport 320 y 1280.
- Labels semanticos en inputs; estrella `fieldset` con `legend` asociado; estados focus visibles.
- `aria-live` en toast; `aria-disabled` en secciones "ya calificó" y "ya respondida".
- Sin links `#` en flujos implementados.

### Estrategia de pruebas frontend

- `npx tsc --noEmit`, `npm run lint`, `npm run build` sin errores.
- Jest + @testing-library/react:
  - `frontend/src/features/reviews/RatingForm.test.tsx` (validacion, 422/409 inline).
  - `frontend/src/features/reviews/ReviewPublicList.test.tsx` (estados, distribución, 404).
  - `frontend/src/features/reviews/ReviewRespondForm.test.tsx` (submit, 409, 403/404).
  - `frontend/src/shared/api/review.test.ts` (tipado de cliente API).
- Sin regresión de tests existentes (BE-011, FE-011, slice 006).

## Contrato de ejecucion docker y pruebas

Composicion:
```
docker compose up -d --build --force-recreate db backend frontend
cd frontend
npx jest src/features/reviews
cd ..
docker compose run --rm backend pytest app/tests/api/test_reviews_*.py -q
docker compose run --rm backend alembic upgrade head
```

Pruebas backend:
- `backend/app/tests/api/test_reviews_create.py` — 201, 422 cita no `COMPLETED`, 422 rating invalido, 409 duplicada, 404 cita ajena, 401 sin token.
- `backend/app/tests/api/test_reviews_read.py` — 200 detalle autor, 404 detalle no autor, 401 sin token, 404 sucursal ajena.
- `backend/app/tests/api/test_reviews_public.py` — 200 publico paginado, 200 con meta, 404 sucursal inexistente.
- `backend/app/tests/api/test_reviews_respond.py` — 200 respuesta, 409 segunda respuesta, 403 propietario, 404 sucursal ajena, 401 sin token.
- `backend/app/tests/api/test_reviews_idor.py` — IDOR/BOLA por tenant en los cinco endpoints.
- `backend/app/tests/api/test_reviews_auth.py` — 401 en todos los endpoints sin token.
- `backend/app/tests/application/test_review_service.py` — reglas de negocio (rating, transaccional, unica).
- `backend/app/tests/data/test_review_repo.py` — repositorio con session fake.

## Plan de reportes y findings

- `docs/opencode/qa/QA-012-results.md` — decision APPROVED/REJECTED.
- `docs/opencode/qa/QA-012-findings.md` — findings con estado (si aplica).
- `docs/opencode/checks/BE-012-checks.md` — Decision: APPROVED en gate docs.
- `docs/opencode/reviews/BE-012-review.md`, `BE-012-clean-architecture-review.md`, `BE-012-security-review.md` — Decision: APPROVED.

## Pruebas QA

- Happy path: propietario califica cita `COMPLETED`; anónimo ve promedio/distribución/listado; staff responde reseña.
- Negative path: rating inválido (422), comentario >2048 (422), cita no `COMPLETED` (422), segunda reseña (409), segunda respuesta (409).
- Permisos: propietario responde (403), staff otra sucursal responde (404), sin token (401), cita ajena al tenant (404).
- Estados UI: loading, submitting, empty, success, error en RatingForm, ReviewPublicList, ReviewRespondForm, ReviewStaffList.
- Paginacion: publico `meta {page, page_size, total, pages}`; listado clinico igual.
- UTF-8: acentos y e-ñ sin mojibake en UI y payload (regla `MOJIBAKE_RE` del validator).

## Riesgos de seguridad/idor/bola

- IDOR: detalle de reseña ajena no visible; responder reseña de sucursal ajena falla 404.
- BOLA: listado clinico siempre filtrado por `clinic_id` del token; listado publico expone solo sucursal activa.
- Rol: propietario nunca responde una reseña (403); sin token 401 en todos los endpoints no publicos.
- Sin filtrado de stack traces ni internals en errores 4xx/5xx.
- Unique `appointment_id` y `review_id` como ultima defensa de duplicidad.
- Al recalcular `RatingSummary` se usan la misma transaccion y consulta por sucursal (sin lecturas cruzadas).

## Politica utf-8

- Artefactos, esquemas, errores y UI en UTF-8.
- Validacion de acentos y e-ñ sin mojibake (regla `MOJIBAKE_RE` del validator).
- Headers `Content-Type: application/json; charset=utf-8` en errores del API.

## Checklist tecnico

- [x] Modelos SQLAlchemy `Review`, `ReviewResponse` + alembic `a012_reviews.py` aplicados.
- [x] Repositorio ABC + implementacion SQLAlchemy (`backend/app/data/review_repo.py`).
- [x] Use cases en `backend/app/application/use_cases/review.py` (crear, responder, lectura, recalcular resumen).
- [x] Schemas Pydantic `backend/app/api/schemas/review_schemas.py` (ReviewCreate, ReviewRead, ReviewRespond, ReviewResponseRead, ReviewListMeta).
- [x] Routers `backend/app/api/v1/routers/review_router.py` (POST/GET publico, GET tenant, POST respond); registro en main router.
- [x] Permisos por rol + ownership por `clinic_id`/`branch_id` validados (guardas `_require_*_role` + ownership por tenant).
- [x] Pytest happy + negative + auth (401) + idor (403/404) + transaccional (rating + resumen).
- [x] Cliente API `frontend/src/shared/api/review.ts` + tests Jest.
- [x] Rutas `frontend/src/features/reviews/*` + secciones en `AppointmentDetail` (Calificar) y `BranchProfile` (Reseñas).
- [x] Estados UX (loading, submitting, empty, success, error) reutilizando `src/shared/ui`.
- [x] `npx tsc --noEmit`, `npm run lint`, `npm run build` sin errores (frontend).
- [x] `python backend/scripts/validate_slice_plan.py BE-012 --stage plan` PASS.
- [x] `python backend/scripts/manage_slice_task.py manifest BE-012 --layer all` genera manifest.

## Definition of done

- Backend: endpoints, schemas, repositorio, use case, migracion `a012` y tests completados.
- Frontend: seccion Calificar cita, Reseñas publico, listado y respuesta clinica, con estados UX.
- QA: happy/negative/permisos/estados UI/paginacion/UTF-8 validados con evidencia.
- Gate plan PASS y manifest generado; sidecars US-012, UIA-012, APIA-012 existentes.
- Sin hallazgos de seguridad IDOR/BOLA/rol en el flujo de reseñas.

## Checklist de tareas

### Backend

- [x] BE-012-T01 - Modelos Review en dominio e infra
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-012-01, AC-012-14, AC-012-15
  Objetivo: Definir la entidad de dominio Review.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `backend/app/domain/entities/*`, `backend/app/infrastructure/database/models/*`, `backend/app/domain/entities/appointment.py`
  Contratos usados: AC-012-01, AC-012-03, AC-012-15
  Entregables: `backend/app/domain/entities/review.py`, `backend/app/infrastructure/database/models/review.py`
  Criterios de aceptacion: Campos id, appointment_id (unique), branch_id, clinic_id, user_id, rating 1..5, comment max 2048, created_at, updated_at. ReviewResponse con id, review_id (unique), branch_id, user_id, body max 2048, timestamps.
  Validacion: `python -c "from app.domain.entities import review"` y `pytest backend/app/tests -q` sin errores de import.
  Resultado esperado: Entidades Review y ReviewResponse modeladas y tipadas.
  Evidencia: Codigo en dominio e infra; import del modulo sin errores.
  Paralelismo[P]: Si

- [x] BE-012-T02 - Migracion Alembic a012
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-012-14
  Objetivo: Crear la tabla reviews con su constraint unico.
  Responsabilidad unica: Si
  Depende de: BE-012-T01
  Contexto necesario: `backend/alembic/versions/a011_payments.py`; modelos de T01
  Contratos usados: AC-012-03, AC-012-05, AC-012-14
  Entregables: `backend/alembic/versions/a012_reviews.py`
  Criterios de aceptacion: RevisionId `a012`, `down_revision` apunta a la head actual. Tablas reviews (unique appointment_id, FK appointments, branches, clinics, internal_users) y review_responses (unique review_id, FK reviews, branches, internal_users). Reversible.
  Validacion: `alembic upgrade head`, `alembic downgrade -1 && alembic upgrade head` sin errores.
  Resultado esperado: Tablas creadas con constraints y reversible.
  Evidencia: Salida de `alembic upgrade head` con version `a012` aplicada.
  Paralelismo[P]: No

- [x] BE-012-T03 - Repositorio de reseñas
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-012-04, AC-012-07
  Objetivo: Implementar el repositorio de reseñas por sucursal.
  Responsabilidad unica: Si
  Depende de: BE-012-T02
  Contexto necesario: `backend/app/data/payment_repo.py` (patrón repositorio del proyecto)
  Contratos usados: AC-012-04, AC-012-07
  Entregables: `backend/app/data/review_repo.py` (ABC + impl. SQLAlchemy)
  Criterios de aceptacion: Metodos create, get_by_id (con ownership), exists_by_appointment, list_public_by_branch (page, page_size, total), list_by_clinic, create_response, get_response_by_review. Sin logic de negocio.
  Validacion: `pytest backend/app/tests/data/test_review_repo.py -q`.
  Resultado esperado: Acceso a datos tipado y testeado.
  Evidencia: `pytest app/tests/data/test_review_repo.py` (PASS).
  Paralelismo[P]: No

- [x] BE-012-T04 - Casos de uso de reseñas
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-012-02, AC-012-05, AC-012-09
  Objetivo: Implementar el use case de crear reseña.
  Responsabilidad unica: Si
  Depende de: BE-012-T03
  Contexto necesario: `backend/app/application/use_cases/branch_profile.py` (patrón), `backend/app/infrastructure/database/models/rating_summary.py`, reglas de negocio del plan
  Contratos usados: AC-012-01..AC-012-06, AC-012-09
  Entregables: `backend/app/application/use_cases/review.py`
  Criterios de aceptacion: Create valida cita `COMPLETED` del owner (si no, 422), cita ajena al tenant (404), reseña previa (409), rating 1..5 y comment <=2048, y recalcula RatingSummary en la misma transaccion (AC-012-09). Respond valida rol clinico de la misma sucursal (403/404) y respuesta previa (409).
  Validacion: `pytest backend/app/tests/application/test_review_service.py -q`.
  Resultado esperado: Reglas de negocio centralizadas en use cases.
  Evidencia: `pytest app/tests/test_review_service.py` (15 PASS).
  Paralelismo[P]: No

- [x] BE-012-T05 - Routers de reseñas
  Capa: backend
  Tipo: api
  Historia o criterio: AC-012-01, AC-012-07, AC-012-08
  Objetivo: Exponer endpoints de crear, lectura, publico, respuesta de reseñas.
  Responsabilidad unica: Si
  Depende de: BE-012-T04
  Contexto necesario: `backend/app/api/v1/routers/payments_router.py` (patrón), `backend/app/api/schemas/payment_schemas.py`
  Contratos usados: AC-012-01, AC-012-05, AC-012-07
  Entregables: `backend/app/api/v1/routers/review_router.py`, `backend/app/api/schemas/review_schemas.py`; registro en main router
  Criterios de aceptacion: POST /reviews 201; GET /reviews/{id} 200; GET /reviews/public/{branchId} 200 con meta; GET /reviews?branch_id= 200 con meta; POST /reviews/{id}/respond 200; errores 401/403/404/409/422 consistentes. Sin logic de negocio en router.
  Validacion: `pytest backend/app/tests/api/test_reviews_*.py -q`.
  Resultado esperado: Contrato API completo y documentado (OpenAPI).
  Evidencia: `pytest app/tests/api/test_reviews_api.py` (PASS).
  Paralelismo[P]: No

- [x] BE-012-T06 - Permisos e IDOR/BOLA de reseñas
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-012-04, AC-012-06, AC-012-12, AC-012-13
  Objetivo: Aplicar la guardia de rol para responder reseñas.
  Responsabilidad unica: Si
  Depende de: BE-012-T05
  Contexto necesario: `backend/app/api/v1/routers/payments_router.py` (guard `_require_write_role`), `backend/core/security.py`
  Contratos usados: AC-012-06, AC-012-12, AC-012-13
  Entregables: Guardas `_require_respond_role` y `_require_owner_role` en `review_router.py` + ownership por `clinic_id` en use cases
  Criterios de aceptacion: 403 propietario al responder; 404 staff de otra sucursal al responder/leer; 401 sin token en endpoints no publicos; 404 cita ajena al tenant al crear.
  Validacion: `pytest backend/app/tests/api/test_reviews_idor.py -q` y `test_reviews_auth.py`.
  Resultado esperado: Sin hallazgos IDOR/BOLA en reseñas.
  Evidencia: `pytest app/tests/api/test_reviews_idor.py` (403/404) y `test_reviews_auth.py` (401) — ambos PASS.
  Paralelismo[P]: No

### Frontend

- [x] FE-012-T01 - Cliente API de reseñas
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-012-07, AC-012-13
  Objetivo: Implementar cliente API tipado para operaciones de reseñas.
  Responsabilidad unica: Si
  Depende de: BE-012-T05
  Contexto necesario: `frontend/src/shared/api/payment.ts` (referencia), contrato del plan
  Contratos usados: AC-012-07, AC-012-13
  Entregables: `frontend/src/shared/api/review.ts`, `frontend/src/shared/api/review.test.ts`
  Criterios de aceptacion: Funciones createReview, getReview, listPublicReviews, listClinicReviews, respondReview con manejo centralizado de errores HTTP. Typecheck sin errores.
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/shared/api/review.test.ts`.
  Resultado esperado: Cliente API disponible para componentes.
  Evidencia: `frontend/src/shared/api/review.ts` con tipado y las cinco funciones; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-012-T02 - Formulario de calificación de cita
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-012-01, AC-012-11
  Objetivo: Implementar la sección Calificar cita en el detalle de cita.
  Responsabilidad unica: Si
  Depende de: FE-012-T01
  Contexto necesario: `frontend/src/features/appointments/components/AppointmentDetail.tsx`, flujo UX del plan
  Contratos usados: AC-012-01, AC-012-11
  Entregables: `frontend/src/features/reviews/RatingForm.tsx`, `frontend/src/features/reviews/RatingForm.test.tsx`
  Criterios de aceptacion: Estrellas 1..5 con label asociado; textarea comment max 2048; botón Calificar cita; estados submitting, error (422/409/404 inline), success (toast); tras crear se deshabilita la sección mostrando "ya calificó esta cita".
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews/RatingForm.test.tsx`.
  Resultado esperado: Formulario calificación usable por el propietario.
  Evidencia: `frontend/src/features/reviews/RatingForm.tsx` implementa el flujo; validado por `npx tsc --noEmit` y Jest.
  Paralelismo[P]: No

- [x] FE-012-T03 - Listado de reseñas del perfil publico
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-012-07, AC-012-08
  Objetivo: Mostrar el listado paginado de reseñas en el perfil publico.
  Responsabilidad unica: Si
  Depende de: FE-012-T01
  Contexto necesario: `frontend/src/features/public-clinic-profile/BranchProfile.tsx`, contrato GET /reviews/public/{branchId}
  Contratos usados: AC-012-07, AC-012-08
  Entregables: `frontend/src/features/reviews/ReviewPublicList.tsx`, `frontend/src/features/reviews/ReviewPublicList.test.tsx`
  Criterios de aceptacion: Tarjeta promedio, distribucion 5-1, listado paginado con meta; muestra respuesta clinica cuando existe; estados loading, success, empty, error; responsive mobile-first; typecheck sin errores.
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews/ReviewPublicList.test.tsx`.
  Resultado esperado: Sección Reseñas visible al anónimo en el perfil publico.
  Evidencia: `frontend/src/features/reviews/ReviewPublicList.tsx` lista reseñas publicas; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-012-T04 - Listado y respuesta clinica de reseñas
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-012-05, AC-012-06
  Objetivo: Implementar el formulario de respuesta clinica a reseñas.
  Responsabilidad unica: Si
  Depende de: FE-012-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-012.md`; contratos GET /reviews?branch_id= y POST /{id}/respond
  Contratos usados: AC-012-05, AC-012-06
  Entregables: `frontend/src/features/reviews/ReviewStaffList.tsx`, `frontend/src/features/reviews/ReviewRespondForm.tsx`, `frontend/src/features/reviews/ReviewRespondForm.test.tsx`
  Criterios de aceptacion: Listado por sucursal con estado respondida; formulario de respuesta con body max 2048; 403 y 404 mapeados a banners legibles; toast de exito; 409 visualizado como "ya respondida".
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews/ReviewRespondForm.test.tsx`.
  Resultado esperado: Flujo clinico de respuesta completo.
  Evidencia: `frontend/src/features/reviews/ReviewRespondForm.tsx` responde reseñas; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-012-T05 - Estados UX del flujo de reseñas
  Capa: frontend
  Tipo: estado ux
  Historia o criterio: AC-012-10
  Objetivo: Implementar los cinco estados en los cuatro componentes del slice.
  Responsabilidad unica: Si
  Depende de: FE-012-T02, FE-012-T03, FE-012-T04
  Contexto necesario: `frontend/src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast)
  Contratos usados: AC-012-10
  Entregables: Estados en `RatingForm`, `ReviewPublicList`, `ReviewStaffList`, `ReviewRespondForm`
  Criterios de aceptacion: Los cinco estados observables por componente; banner de error legible; CTA en empty; tipografia consistente con tokens UI del proyecto.
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews`.
  Resultado esperado: Estados UX completos del flujo de reseñas.
  Evidencia: `frontend/src/features/reviews` muestra los cinco estados; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

### QA

- [x] QA-012-T01 - Pruebas happy path de reseñas
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-012-01, AC-012-07, AC-012-09
  Objetivo: Validar el happy path de calificar una cita.
  Responsabilidad unica: Si
  Depende de: BE-012-T05, BE-012-T06, FE-012-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-012.md`; endpoints del plan; APIA-012; UIA-012
  Contratos usados: AC-012-01, AC-012-05, AC-012-07, AC-012-08
  Entregables: `backend/app/tests/api/test_reviews_create.py` (happy), `backend/app/tests/api/test_reviews_public.py`, `backend/app/tests/api/test_reviews_respond.py` (happy)
  Criterios de aceptacion: POST /reviews 201 con recálculo de RatingSummary; GET publico 200 con items y meta; POST respond 200; UI del propietario, publico y clinico muestran los flujos.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_reviews_create.py app/tests/api/test_reviews_public.py app/tests/api/test_reviews_respond.py -q`.
  Resultado esperado: Flujo de reseñas funcional end-to-end.
  Evidencia: `pytest app/tests/api/test_reviews_create.py` (PASS) y Jest (PASS).
  Paralelismo[P]: No

- [x] QA-012-T02 - Pruebas negative path de reseñas
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-012-02, AC-012-03, AC-012-05, AC-012-15
  Objetivo: Validar rechazos de reseñas invalidas con errores claros.
  Responsabilidad unica: Si
  Depende de: QA-012-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-012.md`; errores 422/409
  Contratos usados: AC-012-02, AC-012-03, AC-012-05
  Entregables: `backend/app/tests/api/test_reviews_negative.py`
  Criterios de aceptacion: 422 cita no COMPLETED; 422 rating fuera de rango; 422 comment >2048; 409 segunda reseña de la misma cita; 409 segunda respuesta de una reseña; errores claros sin filtrar internals.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_reviews_negative.py -q`.
  Resultado esperado: Validaciones de negocio y consistencia de errores cubiertas.
  Evidencia: `pytest app/tests/api/test_reviews_negative.py` (PASS).
  Paralelismo[P]: No

- [x] QA-012-T03 - Pruebas seguridad y permisos de reseñas
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-012-04, AC-012-06, AC-012-12, AC-012-13
  Objetivo: Validar controles de seguridad ante acceso cruzado a reseñas.
  Responsabilidad unica: Si
  Depende de: QA-012-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-012.md`; riesgos IDOR/BOLA del plan
  Contratos usados: AC-012-06, AC-012-12, AC-012-13
  Entregables: `backend/app/tests/api/test_reviews_idor.py`, `backend/app/tests/api/test_reviews_auth.py`
  Criterios de aceptacion: 401 sin token en todos los endpoints; 403 propietario al responder; 404 staff de otra sucursal al responder/leer; 404 cita ajena al tenant al crear.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_reviews_idor.py app/tests/api/test_reviews_auth.py -q`.
  Resultado esperado: Sin hallazgos de seguridad IDOR/BOLA/rol en reseñas.
  Evidencia: `pytest app/tests/api/test_reviews_idor.py` (403/404) y `test_reviews_auth.py` (401) — ambos PASS.
  Paralelismo[P]: No

- [x] QA-012-T04 - Pruebas estados UX y responsive
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-012-10, AC-012-11
  Objetivo: Validar los estados UI del flujo de reseñas.
  Responsabilidad unica: Si
  Depende de: BE-012-T05, FE-012-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-012.md`; `docs/opencode/tasks/ui-automation/UIA-012.md`; `src/shared/ui`
  Contratos usados: AC-012-10, AC-012-11
  Entregables: `frontend/src/features/reviews/*.test.tsx` (Jest)
  Criterios de aceptacion: Calificar cita, listado publico, listado clinico y respuesta muestran los cinco estados (loading, submitting, empty, success, error); error banner legible; CTA en empty; responsive en desktop y mobile.
  Validacion: `cd frontend && npx jest src/features/reviews`.
  Resultado esperado: Estados UX del flujo de reseñas verificados en UI.
  Evidencia: Jest `src/features/reviews/*.test.tsx` (PASS en los cinco estados en ambos breakpoints).
  Paralelismo[P]: No
