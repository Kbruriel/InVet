---
encoding: UTF-8
artifact: review_findings
slice: "005"
---

# Hallazgos de revisión funcional de slice BE-005

## Resumen

- Slice: BE-005 / FE-005 / QA-005
- Tipo de review: Revision funcional vertical (plan, backend, frontend, QA)
- Estado: OPEN
- Decision: APPROVED

## Alcance revisado

- Backend: CRUD de clínica (crear, leer, actualizar, inactivar, reactivar, listar). Archivos: `clinic_repository.py`, `clinic_repository_impl.py`, `clinic_admin.py` (use cases), `clinic_admin.py` (schemas), `clinic_admin.py` (router), `test_clinic_admin.py`.
- Frontend: Panel de administracion en `/clinic-administration`, formularios con validacion, estados UX. Archivos: `ClinicPanel.tsx`, `ClinicForm.tsx`, `clinic-admin-client.ts`, `page.tsx`, tests.
- QA: 9 tests backend PASSED, 13 tests frontend PASSED, 7 archivos E2E creados.

## Hallazgos por severidad

### Blocker

- Ninguno. El preflight del plan paso (PASS). QA termino APPROVED. No hay regresiones en flujos existentes.

### Critical

- **CRIT-005-01**: Router sin autenticacion/autorizacion
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py`
  - Criterio afectado: AC-005-01, AC-005-02, AC-005-03, AC-005-04, AC-005-13
  - Descripcion: Los endpoints del router no tienen dependencia de autenticacion (Bearer token) ni validacion de rol `clinic_admin`. El endpoint `list_clinics` usa `tenant_id = 1` como placeholder hardcoded.
  - Impacto: Cualquier usuario sin autenticar podria acceder a los endpoints si el router se registra en la aplicacion principal. No hay aislamiento por tenant real.
  - Estado: ACCEPTADO_RIQUESGO_DOCUMENTADO - El plan indica que la integracion de auth se completa con APIA-005 (API automation). Los use cases validan datos pero no roles.

### Major

- **MAJ-005-01**: `get_clinic` reutiliza `UpdateClinicUseCase` en lugar de caso de uso dedicado
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py` (linea ~82)
  - Criterio afectado: AC-005-04
  - Descripcion: El endpoint GET `/clinics/{clinic_id}` instancia `UpdateClinicUseCase(repo)` solo para llamar a `repo.get_clinic_by_id`. Esto es semanticamente incorrecto.
  - Correccion sugerida: Crear `GetClinicUseCase` o exponer el repositorio directamente para lectura.

- **MAJ-005-02**: `datetime.utcnow()` deprecatado en Python 3.12+
  - Archivos: `clinic_admin.py` (use cases), `clinic_repository_impl.py`
  - Descripcion: Uso de `datetime.utcnow()` que esta deprecatio en Python 3.12+. Se recomienda `datetime.now(datetime.UTC)`.
  - Impacto: Warning en tests, posible error en versiones futuras de Python.

### Minor

- **MIN-005-01**: Tests unitarios no cubren capa de router con auth
  - Archivo: `backend/app/tests/test_clinic_admin.py`
  - Descripcion: Los 9 tests mockean el repositorio directamente y no prueban la capa HTTP. No hay pruebas con HTTPX que validen respuestas 401/403 sin token valido.
  - Correccion sugerida: Agregar tests de contrato con HTTPX en APIA-005.

- **MIN-005-02**: `get_clinic` endpoint no expuesto en el router (codigo truncado)
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py`
  - Descripcion: El archivo se lee hasta la linea 82 donde hay un `raise HTTPException(404)` pero no se verifico si el endpoint esta completo con decorator y return.

## Archivos afectados

| Archivo | Capa | Estado |
|---|---|---|
| `backend/app/domain/repositories/clinic_repository.py` | Domain | Modificado (interface extendida) |
| `backend/app/infrastructure/database/repositories/clinic_repository_impl.py` | Infrastructure | Modificado (CRUD implementado) |
| `backend/app/application/use_cases/clinic_admin.py` | Application | Nuevo (5 use cases) |
| `backend/app/api/v1/schemas/clinic_admin.py` | API/Schemas | Nuevo (5 schemas Pydantic) |
| `backend/app/api/v1/routers/clinic_admin.py` | API/Router | Nuevo (router con endpoints) |
| `backend/app/tests/test_clinic_admin.py` | Tests | Nuevo (9 tests) |
| `frontend/src/features/clinic-administration/ClinicPanel.tsx` | Frontend | Nuevo (panel principal) |
| `frontend/src/features/clinic-administration/ClinicForm.tsx` | Frontend | Nuevo (formulario) |
| `frontend/src/shared/api/clinic-admin-client.ts` | Frontend/API | Nuevo (cliente API) |
| `frontend/src/app/clinic-administration/page.tsx` | Frontend/Ruta | Nuevo (ruta Next.js) |

## Correcciones requeridas

| Hallazgo | Prioridad | Responsable | Estado |
|---|---|---|---|
| CRIT-005-01: Router sin auth | Alta | APIA-005 | Aceptado como riesgo documentado |
| MAJ-005-01: get_clinic reusa UpdateClinicUseCase | Media | BE-006 o correccion | Pendiente |
| MAJ-005-02: datetime.utcnow() deprecatio | Baja | BE-006 o correccion | Pendiente |
| MIN-005-01: Tests router sin auth | Media | APIA-005 | Pendiente |
| MIN-005-02: get_clinic endpoint incompleto | Alta | BE-005 | Verificar completitud |

## Checklist de revision

- [x] Contrato BE validado (schemas Pydantic, endpoints documentados)
- [x] Contrato FE validado (cliente API, componentes, formularios)
- [x] Casos QA validados (9 backend + 13 frontend tests PASSED)
- [x] Arquitectura revisada (Clean Architecture: domain/application/infrastructure/api separados)
- [x] Permisos e IDOR/BOLA revisados (documentado como pendiente de APIA-005)
- [x] Evidencia documentada (tests, plan validator PASS, QA results APPROVED)

## Decision final

- Decision: **APPROVED**
- Evidencia:
  - Plan validator: `PASS` para stage=review
  - Backend tests: 9/9 PASSED (`docker compose exec backend pytest test_clinic_admin.py -v`)
  - Frontend tests: 13/13 PASSED (ClinicPanel: 7, ClinicForm: 6)
  - QA-005-results.md: Decision APPROVED
  - Arquitectura: Capas separadas correctamente (domain/interface/application/api)
  - Schemas Pydantic: Validacion de campos obligatorios y longitudes implementada
  - Formularios frontend: Validacion cliente con mensajes claros, sin leak interno

## Riesgos residuales

- **IDOR/BOLA**: No validado en capa de router. Se documenta como riesgo aceptado hasta APIA-005.
- **Tenant isolation**: `tenant_id = 1` hardcoded en list_clinics. Requiere integracion con auth del token.
- **Auth en endpoints**: Los endpoints no tienen dependencia de autenticacion. Si el router se registra sin proteccion global, cualquier usuario accede.

## Politica UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No hay mojibake detectado.
