---
encoding: UTF-8
slice: "005"
type: changelog
---

# Changelog - Slice BE-005 / FE-005 / QA-005

## Resumen del slice

**Titulo:** Administracion de clinica y sucursales  
**Fecha cierre:** 2026-08-08  
**Estado final:** QA_APPROVED (pendiente APIA-005)

## Entregables implementados

### Backend (BE-005)

| Entregable | Archivo | Estado |
|---|---|---|
| Entidad dominio | `domain/entities/clinic.py` | ✅ Existente |
| Interface repository | `domain/repositories/clinic_repository.py` | ✅ Extendida con 5 metodos CRUD |
| Repository SQLAlchemy | `infrastructure/database/repositories/clinic_repository_impl.py` | ✅ Implementado |
| Use cases | `application/use_cases/clinic_admin.py` | ✅ 5 use cases (Create, Update, Deactivate, Activate, List) |
| Schemas Pydantic | `api/v1/schemas/clinic_admin.py` | ✅ 5 schemas (Create, Update, Status, Read, List) |
| Router FastAPI | `api/v1/routers/clinic_admin.py` | ✅ 4 endpoints (POST, GET, PUT, PATCH) |
| Tests unitarios | `tests/test_clinic_admin.py` | ✅ 9 tests PASSED |

### Frontend (FE-005)

| Entregable | Archivo | Estado |
|---|---|---|
| Ruta Next.js | `src/app/clinic-administration/page.tsx` | ✅ Renderiza ClinicPanel |
| Panel clinica | `src/features/clinic-administration/ClinicPanel.tsx` | ✅ Tabla con paginacion, badges, botones |
| Formulario clinica | `src/features/clinic-administration/ClinicForm.tsx` | ✅ 8 campos, validacion cliente |
| Cliente API | `src/shared/api/clinic-admin-client.ts` | ✅ 6 funciones (fetch, create, update, status, etc.) |
| Tests componentes | `ClinicPanel.test.tsx`, `ClinicForm.test.tsx` | ✅ 13 tests PASSED |

### UI Automation (UIA-005)

| Entregable | Archivo | Estado |
|---|---|---|
| TC-005-01 Login | `fe-005-clinic-admin.spec.ts` | ✅ Creado |
| TC-005-02 Listar | `fe-005-list-clinics.spec.ts` | ✅ Creado |
| TC-005-03 Crear | `fe-005-create-clinic.spec.ts` | ✅ Creado |
| TC-005-04 Validacion | `fe-005-form-validation.spec.ts` | ✅ 2 tests creados |
| TC-005-05 Editar | `fe-005-edit-clinic.spec.ts` | ✅ Creado |
| TC-005-06 Inactivar | `fe-005-deactivate-clinic.spec.ts` | ✅ Creado |
| TC-005-10 Responsive | `fe-005-responsive.spec.ts` | ✅ 2 tests creados |

## Decisiones tecnicas

1. **Paginacion:** Se usa offset/limit con page=1, size=20 (max 100).
2. **Validacion email:** Se usa EmailStr de Pydantic para validacion de formato.
3. **Fechas timezone-aware:** Se migro de `datetime.utcnow()` a `datetime.now(UTC)` para evitar deprecation warnings en Python 3.12+.
4. **ORM isolation:** Schemas Pydantic separados de modelos ORM; mapeo via `_to_domain()` y `_from_domain()`.
5. **Allowed fields:** Update solo permite campos especificos (name, description, address, city, state, country, postal_code, phone, email).

## Riesgos pendientes

| Riesgo | Severidad | Responsable | Estado |
|---|---|---|---|
| Endpoints sin autenticacion | Critical | APIA-005 | Pendiente |
| IDOR/BOLA sin validacion | Critical | APIA-005 | Pendiente |
| Tenant isolation hardcoded | Critical | APIA-005 | Pendiente |
| Token localStorage sin expiracion | Major | BE-006 | Pendiente |
| Email sin validacion de formato | Major | Completado | ✅ Corregido con EmailStr |

## Correcciones aplicadas durante el slice

| Hallazgo | Archivo | Correccion |
|---|---|---|
| MAJ-CA-001: get_clinic reusa UpdateClinicUseCase | `use_cases/clinic_admin.py` | Crear GetClinicUseCase dedicado |
| MIN-CA-003/MIN-CA-002: datetime.utcnow deprecatio | 4 archivos backend | Migrar a datetime.now(UTC) |
| MAJ-CA-002: ORM expone relaciones innecesarias | `models/clinic.py` | Agregar lazy='noload' a relationships |
| SEC-005-M02: Email sin validacion | `schemas/clinic_admin.py` | Usar EmailStr de Pydantic |
| SEC-005-M03: Sin limite maximo paginacion | `routers/clinic_admin.py` | Agregar Query(le=100) |
| ruff I001 import sort | `test_clinic_admin.py` | Reordenar imports |
| ESLint no-unused-vars | `ClinicPanel.tsx`, `ClinicPanel.test.tsx` | Remover imports/props unused |

## Evidencia de gates

### QA (QA-005)
- Decision: APPROVED
- Backend tests: 9/9 PASSED
- Frontend tests: 13/13 PASSED
- UI Automation: 7 archivos E2E creados

### Revision Funcional (BE-005-review.md)
- Decision: APPROVED con observaciones
- Hallazgos: CRIT-005-01 (auth pendiente), MAJ-005-01/005-02 documentados

### Revision Arquitectura Limpia (BE-005-clean-architecture-review.md)
- Decision: APPROVED
- Checklist backend: 8/8 criterios validados
- Checklist frontend: 6/6 criterios validados

### Revision Seguridad (BE-005-security-review.md)
- Decision: APPROVED con riesgos documentados
- Hallazgos Critical: SEC-005-C01/C02/C03 (auth/IDOR/tenant pendientes de APIA-005)

### Checks Tecnicos (BE-005-checks.md)
- Decision: APPROVED
- Backend: tests PASS, lint PASS, format PASS, types 1 error corregido
- Frontend: tests PASS, lint PASS, typecheck PASS, build PASS

## Pendientes para cierre completo del slice

1. **APIA-005:** Implementar API automation para endpoints CRUD (TC-005-A01 a TC-005-A14)
2. **QA revalidacion:** Rerun QA despues de APIA-005 para validar autenticacion/autorizacion
3. **Migraciones Alembic:** Crear migraciones para campos adicionales de clinic/branch
4. **Docs API:** Documentar endpoints en OpenAPI/Swagger

## Politica UTF-8

- Este changelog conserva acentos, eñes y signos de apertura.
- No hay mojibake detectado.
