---
encoding: UTF-8
artifact: review_findings
---

# Hallazgos de revisión de slice BE-009

## Resumen

- Slice: BE-009 — Consulta médica básica
- Tipo de review: Revisión funcional (contrato BE/FE + seguridad + arquitectura + evidencia)
- Estado: `RESOLVED`
- Decision: `APPROVED`

## Alcance revisado

- Backend: `POST /api/v1/consultations`, `GET /api/v1/consultations/{id}`, `GET /api/v1/consultations` (listado paginado). Entidad de dominio, casos de uso, repositorio (interfaz + implementación ORM), schemas Pydantic, router, migración `a009`.
- Frontend: `src/shared/api/consultation.ts` (cliente de API) + 3 páginas (`/clinic/appointments/[id]/consultation`, `/portal/owner/pets/[id]/consultations`, `/portal/owner/consultations/[id]`).
- QA: `docs/opencode/qa/QA-009-results.md` (APPROVED) + pruebas de API (HTTPX) y use-cases re-ejecutadas (evidencia fresca) + `tsc --noEmit` del frontend.

## Resumen ejecutivo

La implementación es **completa, coherente y verde**. Los tres endpoints existen con contratos consistentes entre backend y frontend, la lógica de negocio vive en `application/use_cases` (los routers son adaptadores delgados), el tenant isolation y el control de owner se aplican en los tres casos de lectura, y la evidencia de pruebas es fresca y exitosa.

Se detectó **un defecto real (Major)**: un archivo residual `backend/app/api/fmt/v1/routers/consultation_router.py` que no está importado por ningún lugar y que además es inválido/incompatible. No bloquea la aprobación porque no es código vivo, pero debe eliminarse.

## Evidencia fresca de pruebas (ejecutada en esta revisión)

- Use-cases: `pytest app/tests/test_consultation_use_cases.py` → **9 passed** (0.15s).
- API (HTTPX): `pytest app/tests/api/test_consultations_api.py` → **14 passed** (0.98s). Cubren happy path, deriva de campos opcionales, lectura propia (200), lectura de ajeno (404), listado propio por mascota.
- Frontend: `npm run typecheck` (`tsc --noEmit`) → **sin errores**.
- Nota: `docs/opencode/plans/BE-009-plan.md` y `docs/opencode/tasks/backend/BE-009.md` aún muestran `status: PLANNED` / checkboxes `- [ ]` y `Evidencia: pending`. Es un **artefacto de tracking**, NO indica código incompleto: los archivos de implementación existen y son sustantivos (mismo patrón ya documentado en `BE-008-review.md`).

## Hallazgos por severidad

### Blocker

- Ninguno.

### Critical

- Ninguno.

### Major

- **M1 — Código residual huérfano/incompatible en ruta no registrada (`api/fmt`)**.
  `backend/app/api/fmt/v1/routers/consultation_router.py` contiene un fragmento aislado (sin `import`s, sin `router = APIRouter(...)`) que define `GET /{consultation_id}` y `GET ""` usando `ConsultationPage(total=..., page=..., size=...)`. Ese constructor es incompatible con el schema real `ConsultationPage(items, meta)` (`backend/app/api/schemas/consultation_schemas.py`). El router vivo se registra desde `app.api.v1.routers.consultation_router` (ver `backend/app/api/v1/router.py:10,26`); el paquete `app/api/fmt` **no es importado por ningún módulo** (búsqueda `api\.fmt`/`fmt.v1` sin resultados). Riego: si alguien lo importara en el futuro fallaría en runtime y además contradice el contrato vigente.
  Corrección: eliminar el directorio `backend/app/api/fmt/` completo.

### Minor

- **m1 — Deriva nullable en `updated_at` (migration vs ORM).**
  En la migración `a009` se declara `updated_at` con `nullable=False` + `server_default=CURRENT_TIMESTAMP`, pero el ORM `backend/app/infrastructure/database/models/consultation.py:26-30` no marca `nullable=False` y usa `default=`/`onupdate=` en Python. Ambos son no-nulos en la práctica y los tests pasan, pero conviene alinear la declaración ORM con la migración para evitar divergencia en futuras autogeneraciones de Alembic.

- **m2 — Tracking desalineado (artefacto).**
  `BE-009-plan.md`/task `BE-009.md` con `PLANNED`/`- [ ]`/`Evidencia: pending` pese a implementación completa y QA aprobado. Actualizar checkboxes y `Evidencia` a `completed`.

- **m3 — Cambios sin commit.**
  La implementación de BE-009 (routers vivos, tests, checkpoints, specs de UIA/APIA) está en working tree sin commit (último commit = refactor de docs + BE-008). No es defecto de diseño, pero la evidencia de aprobación depende de un estado no versionado; conviene fijarlo en un commit.

## Archivos afectados

- `backend/app/api/fmt/v1/routers/consultation_router.py` (eliminar — M1)
- `backend/app/domain/entities/consultation.py`
- `backend/app/application/use_cases/consultation_use_cases.py`
- `backend/app/api/v1/routers/consultation_router.py`
- `backend/app/api/schemas/consultation_schemas.py`
- `backend/app/domain/repositories/consultation_repository.py`
- `backend/app/infrastructure/database/repositories/consultation_repository_impl.py`
- `backend/app/infrastructure/database/models/consultation.py` (m1)
- `backend/alembic/versions/a009_consultations.py` (m1)
- `backend/app/tests/api/test_consultations_api.py`
- `backend/app/tests/test_consultation_use_cases.py`
- `frontend/src/shared/api/consultation.ts`
- `frontend/src/app/clinic/appointments/[id]/consultation/page.tsx`
- `frontend/src/app/portal/owner/pets/[id]/consultations/page.tsx`
- `frontend/src/app/portal/owner/consultations/[id]/page.tsx`
- `docs/opencode/plans/BE-009-plan.md` (m2)
- `docs/opencode/tasks/backend/BE-009.md` (m2)

## Correcciones requeridas

1. Eliminar el directorio residual `backend/app/api/fmt/` (M1, bloqueante para mantener el árbol limpio; no bloqueante funcional).
2. Alinear `nullable` de `updated_at` entre ORM y migración `a009` (m1).
3. Actualizar tracking de `BE-009` a `completada`/checkboxes marcados (m2).
4. Fijar los cambios de BE-009 en commit (m3).

## Notas de seguridad

- **Autenticación**: todos los endpoints dependen de `get_current_access_user`; 401 si no hay `user_id` (`_extract_user_id`, `consultation_router.py:83-91`).
- **Autorización (escritura)**: `_require_write_role` restringe `POST` a `{veterinarian, clinic, staff, admin}` → 403 en caso contrario (`consultation_router.py:117-124`).
- **IDOR/BOLA en creación**: el `clinic_id` siempre se resuelve del usuario autenticado (nunca del payload — `clinic_id` del schema se ignora); la cita se busca por `(appointment_id, clinic_id)` → 403/`OwnershipError` si no es de esa clínica; se exige estado `completed` (422); duplicados por cita → 409 (`consultation_use_cases.py:86-113`).
- **Tenant isolation en lectura**: `GetConsultationUseCase` usa `get_by_id(id, clinic_id)`; `ListConsultationsUseCase` usa `list_by_clinic(...)`; el repositorio filtra siempre por `clinic_id` (`consultation_use_cases.py:137-167`).
- **Vista de propietario**: en `GET /{id}` y `GET ""` se fuerza `pet_id` + se verifica `pet.owner_id == owner_id` → 404 en caso contrario (no expuesto, no filtra info; `consultation_router.py:260-266`, `305-310`).
- **Validación de entrada**: Pydantic con longitudes (`diagnosis` min1/max2000, `history`/`recommendaciones` max3000, ID `gt=0`, `page_size` ge1/le100). El frontend replica los límites (2000/3000) y `maxLength`.
- **No filtrado de info interna**: mensajes de error genéricos y estables; sin stack traces ni detalles de esquema.

## Clean architecture

- **Domain**: `Consultation` / `ConsultationCreate` como modelos Pydantic puros; sin dependencia de ORM ni framework.
- **Application**: casos de uso inyectan repositorios por constructor y un `PetOwnerResolver` (Callable) para desacoplar del repositorio de mascotas — correcto.
- **Infrastructure**: implementación ORM aislada; `lazy="noload"` para evitar carga accidental; `UniqueConstraint("appointment_id")` como backstop anti-duplicado.
- **API**: routers como adaptadores delgados; mapeo de excepciones de dominio a códigos HTTP (`404/409/422/403`); **no se exponen modelos ORM** (siempre `ConsultationRead.model_validate`); listado paginado con `meta`.

## Contrato BE↔FE

- `Consultation` TS ≡ `ConsultationRead` (id, appointment_id, pet_id, clinic_id, branch_id, veterinarian_id, history, diagnosis, recommendations, created_by, updated_at).
- `ConsultationListResponse { items, meta }` ≡ `ConsultationPage { items, meta }`; `meta` incluye `page`, `page_size/size`, `total`, `pages` — consistente con el router (`consultation_router.py:327-335`).
- Query param de página: el router usa `alias="page_size"` (`consultation_router.py:281-283`) y el frontend envía `page_size` (`consultation.ts:67`) — coincidente.
- `ConsultationCreateData` (frontend) ⊂ `ConsultationCreate` (schema de API): los campos opcionales (`clinic_id`, `branch_id`, `veterinarian_id`, `history`, `recommendations`) derivan del backend según la cita — validado por test de deriva (`test_create_consultation_api_derives_optional_fields` → 201).

## Comparison con criterios (task `BE-009.md`)

| Criterio | Estado |
|---|---|
| Contrato requerido por FE-009 existe | ✅ Los 3 endpoints + cliente de API |
| Routers sin lógica de negocio | ✅ Lógica en use cases |
| No se exponen modelos ORM | ✅ Siempre `ConsultationRead` |
| Listados paginados | ✅ `items` + `meta` |
| Errores consistentes, sin info interna | ✅ 401/403/404/409/422 estables |
| Pruebas happy + negative | ✅ 14 API + 9 use-cases, incluyen 404 ajeno / 403 / 422 |

## Checklist de revisión

- [x] Contrato BE validado.
- [x] Contrato FE validado.
- [x] Casos QA validados (re-ejecutados: 14 + 9).
- [x] Arquitectura revisada.
- [x] Permisos e IDOR/BOLA revisados.
- [x] Evidencia documentada.

## Decision final

- Decision: `APPROVED`
- Evidencia: use-cases 9/9, API HTTPX 14/14, frontend `tsc --noEmit` sin errores, contrato BE↔FE consistente, seguridad (authz + tenant isolation + IDOR/BOLA + validación) verificada en código. El único defecto real (M1, archivo huérfano `api/fmt`) no es código vivo y no impide la aprobación; se exige su eliminación junto con las mejoras menores.

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
