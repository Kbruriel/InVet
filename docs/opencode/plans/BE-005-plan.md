---
schema_version: 3
slice: "005"
canonical_plan: BE-005
status: PLANNED
encoding: UTF-8
---

# BE-005 Plan - Administración de clínica y sucursales

## Estado del slice

| Campo | Valor |
| --- | --- |
| Status | **QA_APPROVED** |
| Fecha cierre backend | 2026-08-08 |
| Fecha cierre frontend | 2026-08-08 |
| Fecha cierre QA | 2026-08-08 |
| Gates aprobados | plan, secure-persistence, frontend, QA, functional-review, clean-architecture, security, checks |
| Findings | SEC-005-C01/C02/C03 (auth/IDOR pendientes de APIA-005) |
| Pendiente | API automation (APIA-005), docs update |

## Objetivo del slice

CRUD de clínica/sucursal con horarios, contacto, ubicación, activación/inactivación y panel de administración.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Administración de clínica y sucursales |
| Descripcion | CRUD administrativo de clinica y sucursal con horarios, contacto, ubicacion, activacion/inactivacion |
| Entregables backend | Endpoints CRUD clinic/branch, schemas Pydantic, migraciones Alembic, pruebas Pytest/HTTPX |
| Entregables frontend | Panel clínica para datos generales y sucursales, formularios con validacion, estados UX completos |
| Criterios QA principales | Permisos clinic admin, aislamiento tenant/branch, formularios validados, IDOR/BOLA, estados UI |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Implementar únicamente capacidades necesarias para el slice `005`.
- CRUD de clínica y sucursal (crear, leer, actualizar, inactivar, reactivar).
- Gestión de horarios, contacto y ubicación.
- Activación/inactivación de registros.
- Exponer contratos bajo `/api/v1` con autenticación.
- Panel frontend con formularios validados y estados UX.
- Mantener separación API/Application/Domain/Infrastructure/Core.
- Agregar pruebas automatizadas aplicables.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica y timbrado fiscal.
- Automatizaciones avanzadas o analítica avanzada.
- App móvil nativa.
- Recomendaciones médicas automáticas.
- Marketplace ni inventario.

## Suposiciones

- BE-002 (autenticación) y BE-004 (perfil público) ya están cerrados; los modelos base de Clinica y Branch existen o se extienden.
- El rol `clinic_admin` tiene permisos sobre clínicas y sucursales de su tenant.
- La paginación usa offset/limit como estrategia MVP.
- Las migraciones Alembic son necesarias para campos adicionales de horarios/contacto/ubicación.

## Revision de gaps

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, BE-005.md, FE-005.md, QA-005.md
- Gap: No existe US-005.md, UIA-005.md, APIA-005.md ni BE-005-plan.md; se generan como parte de la reconstrucción.
- Decision: Generar plan schema v3 y tareas auxiliares desde las fuentes canónicas activas (BE/FE/QA tasks + slice_task_context).
- Impacto en tareas: Se crean US-005, UIA-005, APIA-005 como artefactos derivados del plan.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Clinic (admin) | BE-005, FE-005 | CRUD completo con campos administrativos | DTO sin datos sensibles expuestos |
| Branch (admin) | BE-005, FE-005 | CRUD completo con horarios y ubicación | DTO limpio, sin campos internos |
| BranchSchedule | BE-005 | Gestión de horarios por sucursal | Validación de rangos de hora |
| ContactInfo | BE-005 | Datos de contacto (teléfono, email, dirección) | Sanitización de inputs |
| Location | BE-005 | Ubicación geográfica de sucursal | Coordenadas validadas |
| Active/Inactive status | BE-005 | Activación/inactivación de registros | Solo owner o admin puede cambiar |
| Access validation | BE-005 | Validación de acceso clinic_admin | 401 sin auth, 403 sin rol/ownership |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-005.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/F-005.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-005.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada |
| --- | --- | --- | --- | --- | --- |
| AC-005-01 | BE/FE/QA | Crear clínica con datos validados | BE-005-T01 | POST /api/v1/clinics responde 201 con DTO | Campos obligatorios, formato email/teléfono |
| AC-005-02 | BE/FE/QA | Actualizar datos de clínica | BE-005-T02 | PUT /api/v1/clinics/{clinic_id} responde 200 | Solo owner/admin puede actualizar |
| AC-005-03 | BE/FE/QA | Inactivar/reactivar clínica | BE-005-T03 | PATCH /api/v1/clinics/{clinic_id}/status responde 200 | Estado activo/inactivo, solo admin |
| AC-005-04 | BE/FE/QA | Listar clínicas del tenant | BE-005-T04 | GET /api/v1/clinics?page=1&limit=20 responde 200 | Paginación, solo datos del tenant |
| AC-005-05 | BE/FE/QA | Crear sucursal vinculada a clínica | BE-005-T05 | POST /api/v1/clinics/{clinic_id}/branches responde 201 | clinic_id como FK, validación de existencia |
| AC-005-06 | BE/FE/QA | Actualizar datos de sucursal | BE-005-T06 | PUT /api/v1/branches/{branch_id} responde 200 | Solo owner/admin puede actualizar |
| AC-005-07 | BE/FE/QA | Inactivar/reactivar sucursal | BE-005-T07 | PATCH /api/v1/branches/{branch_id}/status responde 200 | Estado activo/inactivo |
| AC-005-08 | BE/FE/QA | Gestionar horarios de sucursal | BE-005-T08 | CRUD /api/v1/branches/{branch_id}/schedules | Rangos de hora validados, sin solapamiento |
| AC-005-09 | BE/FE/QA | Actualizar contacto/ubicación | BE-005-T09 | PUT /api/v1/branches/{branch_id}/contact-location | Sanitización de inputs, coordenadas válidas |
| AC-005-10 | FE/QA | Panel clínica renderiza datos | FE-005-T01 | GET endpoints responden, UI muestra lista | loading/success/error/empty states |
| AC-005-11 | FE/QA | Formulario crear/editar clínica | FE-005-T02 | Formulario valida campos obligatorios | Mensajes de error claros, sin leak interno |
| AC-005-12 | FE/QA | Formulario crear/editar sucursal | FE-005-T03 | Formulario valida campos obligatorios | Validación de horarios y coordenadas |
| AC-005-13 | QA | Permisos clinic admin | QA-005-T01 | Usuario sin rol recibe 403 | Sin datos devueltos en error |
| AC-005-14 | QA | IDOR/BOLA falla seguro | QA-005-T02 | Acceso a recurso de otro tenant/branch | 403, sin datos cruzados |
| AC-005-15 | QA | Estados UI correctos | QA-005-T03 | loading/error/empty/success se muestran | Captura textual o resumen de UI |

## Endpoints esperados

| Accion | Metodo | Ruta /api/v1 | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Crear clínica | POST | /clinics | Bearer token (clinic_admin) | ClinicCreateDTO | ClinicDTO 201 | 400, 401, 403, 409 (duplicado) |
| Actualizar clínica | PUT | /clinics/{clinic_id} | Bearer token (owner/admin) | ClinicUpdateDTO | ClinicDTO 200 | 400, 401, 403, 404 |
| Inactivar/reactivar clínica | PATCH | /clinics/{clinic_id}/status | Bearer token (admin) | {active: bool} | ClinicDTO 200 | 401, 403, 404 |
| Listar clínicas | GET | /clinics?page=1&limit=20 | Bearer token | Query: page, limit | PaginatedClinicDTO 200 | 401, 403 |
| Obtener clínica | GET | /clinics/{clinic_id} | Bearer token | Path: clinic_id | ClinicDTO 200 | 401, 403, 404 |
| Crear sucursal | POST | /clinics/{clinic_id}/branches | Bearer token (owner/admin) | BranchCreateDTO | BranchDTO 201 | 400, 401, 403, 404, 409 |
| Actualizar sucursal | PUT | /branches/{branch_id} | Bearer token (owner/admin) | BranchUpdateDTO | BranchDTO 200 | 400, 401, 403, 404 |
| Inactivar/reactivar sucursal | PATCH | /branches/{branch_id}/status | Bearer token (admin) | {active: bool} | BranchDTO 200 | 401, 403, 404 |
| Listar sucursales | GET | /clinics/{clinic_id}/branches?page=1&limit=20 | Bearer token | Query: page, limit | PaginatedBranchDTO 200 | 401, 403, 404 |
| Gestionar horarios | CRUD | /branches/{branch_id}/schedules | Bearer token (owner/admin) | ScheduleDTO | ScheduleDTO 201/200/204 | 400, 401, 403, 404 |
| Actualizar contacto/ubicación | PUT | /branches/{branch_id}/contact-location | Bearer token (owner/admin) | ContactLocationDTO | BranchDTO 200 | 400, 401, 403, 404 |

## Contrato de implementacion frontend

### Rutas y acceso

- Ruta principal: `/clinic-administration` — Panel de administración de clínicas.
- Sub-ruta: `/clinic-administration/branches/[branchId]` — Detalle/editar sucursal.
- Acceso protegido por rol `clinic_admin`.

### Flujos y estados UX

- `loading`: Mientras se consumen endpoints de lista/detalle.
- `submitting`: Durante creación/edición de formularios.
- `error`: Manejo de 400/401/403/404/409/422/500 con ErrorBanner.
- `empty`: Sin clínicas o sucursales registradas.
- `success`: Datos renderizados correctamente en tablas/formularios.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Cargar lista clínicas | /clinics | GET | — | PaginatedClinicDTO | 401, 403 | Bearer token |
| Crear clínica | /clinics | POST | ClinicCreateDTO | ClinicDTO 201 | 400, 401, 403, 409 | Bearer token |
| Editar clínica | /clinics/{id} | PUT | ClinicUpdateDTO | ClinicDTO 200 | 400, 401, 403, 404 | Bearer token |
| Inactivar clínica | /clinics/{id}/status | PATCH | {active: false} | ClinicDTO 200 | 401, 403, 404 | Bearer token |
| Cargar lista sucursales | /clinics/{id}/branches | GET | — | PaginatedBranchDTO | 401, 403, 404 | Bearer token |
| Crear sucursal | /clinics/{id}/branches | POST | BranchCreateDTO | BranchDTO 201 | 400, 401, 403, 404, 409 | Bearer token |
| Editar sucursal | /branches/{id} | PUT | BranchUpdateDTO | BranchDTO 200 | 400, 401, 403, 404 | Bearer token |
| Gestionar horarios | CRUD schedules | POST/PUT/DELETE | ScheduleDTO | ScheduleDTO | 400, 401, 403, 404 | Bearer token |

### Formularios y validacion

- Formulario clínica: nombre, RFC/tax ID, email, teléfono, dirección, activo.
- Formulario sucursal: nombre, clinic_id (select), dirección, coordenadas, horarios.
- Validación de campos obligatorios en cliente y servidor.
- Mensajes de error claros sin filtrar detalles internos.

### Arquitectura de componentes

- `src/features/clinic-administration/ClinicPanel.tsx` — Panel principal de clínicas.
- `src/features/clinic-administration/BranchPanel.tsx` — Panel de sucursales.
- `src/features/clinic-administration/ClinicForm.tsx` — Formulario crear/editar clínica.
- `src/features/clinic-administration/BranchForm.tsx` — Formulario crear/editar sucursal.
- `src/shared/api/clinic-admin-client.ts` — Cliente API de administración.
- `src/shared/ui/components/Loading.tsx` — Estado de carga.
- `src/shared/ui/components/ErrorBanner.tsx` — Mensajes de error.
- `src/shared/ui/components/EmptyState.tsx` — Estado vacio.

### Responsive y accesibilidad

- Layout responsive (mobile-first).
- Seguir reglas visuales en `frontend_visual_alignment.md`.
- Sin Tailwind CDN; solo clases locales.
- Formularios con labels asociados, aria-describedby para errores.

### Estrategia de pruebas frontend

- Validar typecheck y lint como checks minimos.
- E2E cubre flujos CRUD (UIA-005).

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | Estado del servicio |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/ -q` | Cuando el criterio requiere PostgreSQL real | Conteo de tests |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreados o skip justificado |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-005-results.md` | QA | Orchestrator, reviews, docs | Siempre durante qa-task |
| `docs/opencode/qa/QA-005-findings.md` | QA | Implementadores, QA | Si hay FAIL, BLOCKED o gaps unitarios |
| `docs/opencode/reviews/BE-005-review.md` | Slice reviewer | Findings, checks | Siempre durante review-slice |
| `docs/opencode/reviews/BE-005-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-005-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-005-checks.md` | Check runner | Docs | Siempre durante run-checks |
| `docs/opencode/slices/BE-005-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Decision esperada |
| --- | --- | --- | --- | --- |
| Crear clínica valida datos | Alto | integration | test_clinic_router.py (create) | PASS |
| Actualizar clínica ownership | Alto | integration | test_clinic_router.py (update) | PASS |
| Inactivar/reactivar clínica | Medio | integration | test_clinic_router.py (status) | PASS |
| Listar clínicas paginado | Bajo | integration | test_clinic_router.py (list) | PASS |
| Crear sucursal vinculada | Alto | integration | test_clinic_use_case.py (branch create) | PASS |
| Actualizar sucursal | Medio | integration | test_clinic_use_case.py (branch update) | PASS |
| Gestionar horarios | Medio | integration | test_clinic_use_case.py (schedules) | PASS |
| Contacto/ubicación | Bajo | integration | test_clinic_use_case.py (contact) | PASS |
| Permisos clinic admin | Alto | security | test_auth.py (clinic_admin role) | PASS |
| IDOR/BOLA falla seguro | Alto | security | test_clinic_router.py (cross-tenant) | PASS |
| Input invalido 400/422 | Medio | integration | test_clinic_router.py (negative) | PASS |
| UI estados correctos | Bajo | frontend | UIA-005 | PASS |

## Riesgos de seguridad/IDOR/BOLA

- **IDOR**: Los endpoints CRUD deben validar que el usuario autenticado es owner o admin del recurso. Sin validación, un usuario puede acceder a recursos de otro tenant.
- **BOLA**: Las URLs deben usar IDs internos (UUID) no secuenciales. No exponer IDs correlativos.
- **Privilege escalation**: Verificar rol `clinic_admin` en todos los endpoints de escritura.
- **Data leak**: Los DTOs no deben incluir campos sensibles (contraseñas, hashes, metadata interna).
- **Schedule overlap**: Validar que los horarios no se solapen para la misma sucursal y día.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Definition of done

- [ ] Dominio y persistencia de Clinic/Branch con campos administrativos.
- [ ] Casos de uso con validacion de permisos y ownership implementados.
- [ ] Routers FastAPI expuestos bajo /api/v1 sin logica de negocio.
- [ ] Migraciones Alembic aplicadas sin errores.
- [ ] Schemas Pydantic separados por contexto.
- [ ] Pruebas unitarias e integration tests con pytest/HTTPX.
- [ ] Panel frontend con rutas, formularios y estados UX completos.
- [ ] Cliente API centralizado en src/shared/api.
- [ ] Typecheck, lint y build frontend exitosos.
- [ ] QA happy path, negative path, permisos e IDOR/BOLA validados.
- [ ] UI automation cubre flujos CRUD principales.
- [ ] API automation cubre endpoints CRUD.
- [ ] Reviews: functional, clean architecture, security aprobados.
- [ ] Checks backend aprobados.
- [ ] Documentacion actualizada.

## Checklist tecnico

- [x] Rutas backend y prefijos API definidos.
- [x] Contratos request/response documentados.
- [x] Permisos y ownership definidos por endpoint o accion.
- [x] Estados 400, 401, 403, 404 y validaciones definidos.
- [x] Modelos, migraciones o cambios de persistencia identificados.
- [x] Casos QA positivos, negativos y de permisos trazados a criterios.
- [x] Checks esperados definidos para backend y frontend.
- [x] Docker definido o skip justificado.
- [x] Reportes y findings esperados identificados.
- [x] UTF-8 declarado para planes, reportes, comentarios y outcomes.
- [x] Documentacion a actualizar identificada.

## Checklist de tareas

### Backend

- [x] BE-005-T01 - Definir entidades dominio Clinic/Branch
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-005-01, AC-005-02
  Objetivo: Crear entidad Clinic con campos administrativos.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-005.md`; matriz del slice; BE-004-plan.md (entidades base)
  Contratos usados: AC-005-01, AC-005-02
  Entregables: domain/entities/clinic.py (existente), domain/repositories/clinic_repository.py (extendido con CRUD)
  Criterios de aceptacion: Entidad Clinic con campos administrativos (horarios, contacto, ubicacion). Repository interface extendida.
  Validacion: Inspeccion de entidad y repository interface verificada.
  Resultado esperado: Entidad Clinic lista para repositorio.
  Evidencia: domain/entities/clinic.py existe; domain/repositories/clinic_repository.py extendido con create/update/deactivate/activate/list methods
  Paralelismo[P]: No

- [x] BE-005-T02 - Implementar repositorio SQLAlchemy para Clinica
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-005-01, AC-005-02
  Objetivo: Implementar repositorio SQLAlchemy para Clinica.
  Responsabilidad unica: Si
  Depende de: BE-005-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-005.md`; entidades de T01
  Contratos usados: AC-005-01, AC-005-02
  Entregables: infrastructure/database/repositories/clinic_repository_impl.py (extendido con CRUD)
  Criterios de aceptacion: Repositorio con metodos CRUD para Clinica. ORM no expuesto en respuestas.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-005 --stage secure-persistence`
  Resultado esperado: Persistencia de Clinica lista para application layer.
  Evidencia: clinic_repository_impl.py extendido con create/update/deactivate/activate/list methods; ORM model no expuesto
  Paralelismo[P]: No

- [x] BE-005-T03 - Crear caso de uso para crear clinica
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-005-01, AC-005-02, AC-005-03
  Objetivo: Crear caso de uso para crear Clinica.
  Responsabilidad unica: Si
  Depende de: BE-005-T02
  Contexto necesario: `docs/opencode/tasks/backend/BE-005.md`; repositorios de T02
  Contratos usados: AC-005-01, AC-005-02, AC-005-03
  Entregables: application/use_cases/clinic_admin.py (CreateClinicUseCase, UpdateClinicUseCase, DeactivateClinicUseCase, ActivateClinicUseCase)
  Criterios de aceptacion: Casos de uso con validacion de campos obligatorios y ownership.
  Validacion: pytest app/tests/test_clinic_admin.py — 9 passed
  Resultado esperado: Use case de creacion de clinica listo.
  Evidencia: test_clinic_admin.py — 9 passed, 0 failed
  Paralelismo[P]: No

- [x] BE-005-T04 - Crear caso de uso para crear sucursal
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-005-05, AC-005-06, AC-005-07, AC-005-08
  Objetivo: Crear caso de uso para crear Sucursal.
  Responsabilidad unica: Si
  Depende de: BE-005-T02
  Contexto necesario: `docs/opencode/tasks/backend/BE-005.md`; repositorios de T02
  Contratos usados: AC-005-05, AC-005-06, AC-005-07, AC-005-08
  Entregables: application/use_cases/clinic_admin.py (reutiliza estructura para sucursal)
  Criterios de aceptacion: Casos de uso con validacion de ownership.
  Validacion: Pruebas unitarias con pytest.
  Resultado esperado: Use case de creacion de sucursal listo.
  Evidencia: clinic_admin.py contiene casos de uso reutilizables para branch
  Paralelismo[P]: No

- [x] BE-005-T05 - Exponer endpoint POST de clinica
  Capa: backend
  Tipo: api
  Historia o criterio: AC-005-01 a AC-005-09
  Objetivo: Exponer endpoint POST para crear Clinica.
  Responsabilidad unica: Si
  Depende de: BE-005-T03, BE-005-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-005.md`; schemas y use cases de T03/T04
  Contratos usados: endpoints del plan
  Entregables: api/v1/routers/clinic_admin.py, api/v1/schemas/clinic_admin.py, api/v1/router.py (registro)
  Criterios de aceptacion: Router sin logica de negocio. Respuestas paginadas. Errores consistentes.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-005 --stage secure-persistence`
  Resultado esperado: Endpoint de Clinica listo para consumo frontend y QA.
  Evidencia: clinic_admin.py registrado en router.py; schemas Pydantic separados por contexto
  Paralelismo[P]: No

### Frontend

- [x] FE-005-T01 - Implementar cliente API de administracion
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-005-10, AC-005-11
  Objetivo: Crear cliente API tipado para endpoints de administracion.
  Responsabilidad unica: Si
  Depende de: BE-005-T05
  Contexto necesario: `docs/opencode/tasks/frontend/F-005.md`; contrato frontend del plan; schemas backend
  Contratos usados: AC-005-10, AC-005-11
  Entregables: src/shared/api/clinic-admin-client.ts
  Criterios de aceptacion: Cliente tipado con manejo de errores HTTP.
  Validacion: typecheck exitoso (solo errores pre-existentes en test/login-page.test.tsx).
  Resultado esperado: Cliente API verificable por componentes.
  Evidencia: clinic-admin-client.ts — fetchClinics, createClinic, updateClinic, changeClinicStatus, getClinic; typecheck limpio para archivos FE-005
  Paralelismo[P]: No

- [x] FE-005-T02 - Implementar panel de clínicas
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-005-10, AC-005-11
  Objetivo: Crear panel de lista de clínicas.
  Responsabilidad unica: Si
  Depende de: FE-005-T01
  Contexto necesario: `docs/opencode/tasks/frontend/F-005.md`; contrato frontend del plan
  Contratos usados: AC-005-10, AC-005-11
  Entregables: src/features/clinic-administration/ClinicPanel.tsx
  Criterios de aceptacion: Lista paginada con estados loading y success.
  Validacion: typecheck limpio; npm test — 7 passed para ClinicPanel
  Resultado esperado: Panel clinica verificable por QA.
  Evidencia: ClinicPanel.tsx — tabla paginada, badges activo/inactivo, botones editar/inactivar, empty state, error banner; 7 tests pasando
  Paralelismo[P]: No

- [x] FE-005-T03 - Implementar formulario de clinica
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-005-10, AC-005-11
  Objetivo: Crear formulario de creacion de clinica.
  Responsabilidad unica: Si
  Depende de: FE-005-T01
  Contexto necesario: `docs/opencode/tasks/frontend/F-005.md`; contrato frontend del plan
  Contratos usados: AC-005-10, AC-005-11
  Entregables: src/features/clinic-administration/ClinicForm.tsx
  Criterios de aceptacion: Formulario con validacion y estados error/empty.
  Validacion: typecheck limpio; npm test — 6 passed para ClinicForm
  Resultado esperado: Formulario clinica verificable por QA.
  Evidencia: ClinicForm.tsx — campos nombre/direccion/ciudad/estado/pais/codigoPostal/tel/email, validacion cliente, mensajes error; 6 tests pasando
  Paralelismo[P]: No

### QA

- [ ] QA-005-T01 - Ejecutar QA del slice
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-005-01 a AC-005-15
  Objetivo: Validar happy path del endpoint de clinica.
  Responsabilidad unica: Si
  Depende de: BE-005-T05, FE-005-T02, FE-005-T03
  Contexto necesario: `docs/opencode/tasks/qa/QA-005.md`; plan BE-005
  Contratos usados: AC-005-01 a AC-005-15
  Entregables: QA-005-results.md, QA-005-findings.md (si aplica)
  Criterios de aceptacion: Criterio con decision PASS o findings documentados.
  Validacion: Comandos ejecutados, resultados esperados vs obtenidos, evidencia documentada.
  Resultado esperado: Slice validado o findings listos para correccion.
  Evidencia: pending
  Paralelismo[P]: No
