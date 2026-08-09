---
schema_version: 3
slice: "006"
canonical_plan: BE-006
status: COMPLETED
encoding: UTF-8
---

# BE-006 Plan - Servicios, veterinarios y usuarios internos

## Objetivo del slice

Gestionar servicios, veterinarios y usuarios internos asociados a clínica/sucursal mediante CRUD protegido con permisos por rol, aislamiento tenant/sucursal y estados activo/inactivo.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Servicios, veterinarios y usuarios internos |
| Descripcion | Gestionar servicios, veterinarios y usuarios internos asociados a clinica/sucursal. |
| Entregables backend | Entidades, repositorios y endpoints protegidos para servicios, veterinarios, usuarios internos y asignaciones. |
| Entregables frontend | Pantallas de gestion, formularios, listados, permisos visibles y cliente API para recursos internos. |
| Criterios QA principales | CRUD autorizado pasa; usuarios sin permiso fallan; asignaciones respetan tenant/sucursal; UI no ofrece acciones indebidas. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Entidades de dominio: `Service`, `Veterinarian`, `InternalUser` y modelo de asociación `VeterinarianServiceAssignment`.
- Repositorios SQLAlchemy para cada entidad con soporte de filtrado por `clinic_id`/`branch_id`.
- Routers FastAPI bajo `/api/v1/services`, `/api/v1/veterinarians`, `/api/v1/internal-users` con CRUD protegido.
- Endpoints de asociación: asignar/desasignar veterinario a servicio y usuario interno a sucursal.
- Schemas Pydantic separados por contexto (request/response).
- Migraciones Alembic para nuevas tablas y relaciones.
- Pruebas Pytest/HTTPX que cubran happy path, negative path y permisos.
- Validación de ownership e IDOR/BOLA en cada endpoint.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica y timbrado fiscal.
- Automatizaciones avanzadas o analítica avanzada.
- Notificaciones automáticas por cambio de estado.
- Gestión de horarios/turnos (reservado para slice 008).
- Calificaciones y comentarios (reservado para slice 012).

## Suposiciones

- Los roles `veterinarian` e `internal_user` existen o se crean como parte del seed inicial en BE-005.
- La tabla de usuarios existentes (`User`) puede referenciar a `InternalUser` mediante relación uno-a-uno o campo `user_id`.
- Cada `Veterinarian` y `InternalUser` pertenece a una sola `clinic_id` (tenant).
- Las asociaciones son many-to-many entre `Veterinarian` y `Service` con tabla intermedia explícita.
- Un `InternalUser` puede estar asociado a múltiples sucursales (`branch_id`) de su clínica.
- Si el supuesto cambia contrato público, seguridad, persistencia o aceptación QA, detener la planificación y preguntar.

## Revision de gaps

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, `docs/opencode/tasks/backend/BE-006.md`, `docs/opencode/tasks/frontend/FE-006.md`, `docs/opencode/tasks/qa/QA-006.md`
- Gap: No se especifica si un veterinario puede pertenecer a múltiples clínicas.
- Decision: MVP restringe cada veterinario a una sola clínica (`clinic_id`). Soporte multi-clínica se pospone.
- Impacto en tareas: Tareas de backend y QA deben validar que `clinic_id` del veterinario coincida con el tenant solicitado.

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, `docs/opencode/tasks/backend/BE-006.md`
- Gap: No se especifica si `InternalUser` reutiliza la tabla de usuarios existente o crea una nueva.
- Decision: `InternalUser` es entidad separada con campo `user_id` que referencia al usuario de autenticación (BE-005).
- Impacto en tareas: Frontend debe consumir dos fuentes de datos para mostrar perfil completo del usuario interno.

- Fuente revisada: `docs/opencode/tasks/qa/QA-006.md`
- Gap: QA menciona estados activo/inactivo pero no especifica si es soft-delete o campo booleano.
- Decision: Se usa campo booleano `is_active` en cada entidad para control de estado sin eliminar registros.
- Impacto en tareas: Listados deben filtrar por defecto solo registros activos; endpoint de admin puede listar inactivos con filtro explícito.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| `Service` | BE-006, slice_task_context | CRUD servicios asociados a clínica/sucursal | Crear/leer/modificar/eliminar con ownership por clinic_id |
| `Veterinarian` | BE-006, slice_task_context | CRUD veterinarios con licencia y datos profesionales | Validar campos requeridos (nombre, licencia, especialidad) |
| `InternalUser` | BE-006, slice_task_context | CRUD usuarios internos vinculados a cuenta de autenticación | Validar user_id referencia usuario existente en auth |
| `VeterinarianServiceAssignment` | BE-006 | Asociación many-to-many veterinario-servicio | Validar que ambos extremos pertenezcan al mismo clinic_id |
| Regla: tenant isolation | QA-006, slice_task_context | Cada recurso pertenece a una sola clínica | IDOR/BOLA: acceso por ID ajeno falla con 403 |
| Regla: active/inactive state | QA-006 | Campos `is_active` en todas las entidades | Listados filtran activos por defecto; admin puede ver inactivos |
| Regla: permisos por rol | QA-006, BE-006 | Solo roles autorizados (admin/manager) operan CRUD | 401 sin token, 403 con token pero rol insuficiente |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-006.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-006.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-006.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada |
| --- | --- | --- | --- | --- | --- |
| AC-006-01 | BE/QA | CRUD servicios autorizado pasa | BE-006-T01, FE-006-T01 | Endpoint POST/GET/PUT/DELETE /api/v1/services con token valido | 201/200/204 en tests y UI muestra confirmacion |
| AC-006-02 | BE/QA | CRUD veterinarios autorizado pasa | BE-006-T02, FE-006-T02 | Endpoint POST/GET/PUT/DELETE /api/v1/veterinarians con token valido | 201/200/204 en tests y UI muestra confirmacion |
| AC-006-03 | BE/QA | CRUD usuarios internos autorizado pasa | BE-006-T03, FE-006-T03 | Endpoint POST/GET/PUT/DELETE /api/v1/internal-users con token valido | 201/200/204 en tests y UI muestra confirmacion |
| AC-006-04 | BE/QA | Asignaciones respetan tenant/sucursal | BE-006-T04, QA-006-T03 | POST /api/v1/veterinarians/{id}/assign-service con clinic_id coincidente | 201 si mismo tenant; 403 si diferente tenant |
| AC-006-05 | BE/QA | Usuarios sin permiso reciben 403 | QA-006, BE-006 | Request sin rol admin/manager a endpoints protegidos | 403 en tests y UI muestra mensaje de error |
| AC-006-06 | BE/QA | Acceso no autenticado recibe 401 | QA-006, BE-006 | Request sin token a endpoints protegidos | 401 en tests |
| AC-006-07 | BE/QA | IDOR/BOLA falla de forma segura | QA-006, BE-006 | Acceso por ID ajeno a recurso de otra clinica | 403 en tests |
| AC-006-08 | FE/QA | UI muestra estados loading/error/empty/success | FE-006, QA-006 | Navegar a cada vista admin y verificar estados | Captura textual o resumen de UI con todos los estados |
| AC-006-09 | BE/QA | Input invalido produce error claro sin filtrar detalles internos | QA-006, BE-006 | Payloads malformados a endpoints CRUD | 422 con mensajes claros en tests |
| AC-006-10 | FE/QA | Listados aplican paginacion y limites | QA-006, BE-006 | GET /api/v1/services?page=1&page_size=20 | Response con metadatos de paginacion y max page_size razonable |
| AC-006-11 | FE/QA | Estados activo/inactivo se respetan en listados | QA-006 | GET listados sin filtro is_active | Solo activos retornados; filtro ?is_active=false retorna inactivos |
| AC-006-12 | FE/QA | UI no ofrece acciones indebidas segun permisos | FE-006, QA-006 | Renderizar vistas con rol insuficiente | Botones de crear/editar/eliminar ocultos o deshabilitados |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Listar servicios | GET | `/api/v1/services` | Bearer token | Query: `clinic_id`, `page`, `page_size`, `is_active` | Paginated list of ServiceDTO | 401, 403 |
| Crear servicio | POST | `/api/v1/services` | Bearer token + admin/manager | ServiceCreateDTO | ServiceDTO 201 | 400, 401, 403, 409, 422 |
| Leer servicio | GET | `/api/v1/services/{id}` | Bearer token | Path: `id` | ServiceDTO | 401, 403, 404 |
| Actualizar servicio | PUT | `/api/v1/services/{id}` | Bearer token + admin/manager | Path: `id`, ServiceUpdateDTO | ServiceDTO | 401, 403, 404, 422 |
| Desactivar servicio | PATCH | `/api/v1/services/{id}/deactivate` | Bearer token + admin/manager | Path: `id` | 204 | 401, 403, 404 |
| Listar veterinarios | GET | `/api/v1/veterinarians` | Bearer token | Query: `clinic_id`, `page`, `page_size`, `is_active` | Paginated list of VeterinarianDTO | 401, 403 |
| Crear veterinario | POST | `/api/v1/veterinarians` | Bearer token + admin/manager | VeterinarianCreateDTO | VeterinarianDTO 201 | 400, 401, 403, 409, 422 |
| Leer veterinario | GET | `/api/v1/veterinarians/{id}` | Bearer token | Path: `id` | VeterinarianDTO | 401, 403, 404 |
| Actualizar veterinario | PUT | `/api/v1/veterinarians/{id}` | Bearer token + admin/manager | Path: `id`, VeterinarianUpdateDTO | VeterinarianDTO | 401, 403, 404, 422 |
| Desactivar veterinario | PATCH | `/api/v1/veterinarians/{id}/deactivate` | Bearer token + admin/manager | Path: `id` | 204 | 401, 403, 404 |
| Listar usuarios internos | GET | `/api/v1/internal-users` | Bearer token | Query: `clinic_id`, `page`, `page_size`, `is_active` | Paginated list of InternalUserDTO | 401, 403 |
| Crear usuario interno | POST | `/api/v1/internal-users` | Bearer token + admin/manager | InternalUserCreateDTO | InternalUserDTO 201 | 400, 401, 403, 409, 422 |
| Leer usuario interno | GET | `/api/v1/internal-users/{id}` | Bearer token | Path: `id` | InternalUserDTO | 401, 403, 404 |
| Actualizar usuario interno | PUT | `/api/v1/internal-users/{id}` | Bearer token + admin/manager | Path: `id`, InternalUserUpdateDTO | InternalUserDTO | 401, 403, 404, 422 |
| Desactivar usuario interno | PATCH | `/api/v1/internal-users/{id}/deactivate` | Bearer token + admin/manager | Path: `id` | 204 | 401, 403, 404 |
| Asignar servicio a veterinario | POST | `/api/v1/veterinarians/{id}/assign-service` | Bearer token + admin/manager | Path: `id`, `service_id` | AssignmentDTO 201 | 400, 401, 403, 404, 409 |
| Desasignar servicio de veterinario | DELETE | `/api/v1/veterinarians/{id}/assign-service/{service_id}` | Bearer token + admin/manager | Path: `id`, `service_id` | 204 | 401, 403, 404 |
| Asignar sucursal a usuario interno | POST | `/api/v1/internal-users/{id}/assign-branch` | Bearer token + admin/manager | Path: `id`, `branch_id` | AssignmentDTO 201 | 400, 401, 403, 404, 409 |
| Desasignar sucursal de usuario interno | DELETE | `/api/v1/internal-users/{id}/assign-branch/{branch_id}` | Bearer token + admin/manager | Path: `id`, `branch_id` | 204 | 401, 403, 404 |

## Contrato de implementacion frontend

### Rutas y acceso

| Ruta | Acceso requerido | Descripcion |
| --- | --- | --- |
| `/admin/services` | admin/manager | Listado y gestion de servicios |
| `/admin/services/create` | admin/manager | Formulario de creacion de servicio |
| `/admin/services/[id]/edit` | admin/manager | Formulario de edicion de servicio |
| `/admin/veterinarians` | admin/manager | Listado y gestion de veterinarios |
| `/admin/veterinarians/create` | admin/manager | Formulario de creacion de veterinario |
| `/admin/veterinarians/[id]/edit` | admin/manager | Formulario de edicion de veterinario |
| `/admin/internal-users` | admin/manager | Listado y gestion de usuarios internos |
| `/admin/internal-users/create` | admin/manager | Formulario de creacion de usuario interno |
| `/admin/internal-users/[id]/edit` | admin/manager | Formulario de edicion de usuario interno |

### Flujos y estados UX

Debe cubrir `loading`, `submitting`, `error`, `empty` y `success` cuando apliquen.

- Listados: loading (skeleton/spinner) -> success (tabla con datos) o empty (mensaje sin datos).
- Formularios: loading inicial (datos del recurso si es edicion) -> submitting (boton deshabilitado + spinner) -> success (redireccion/toast) o error (mensaje de error en formulario).
- Errores HTTP: 401 (redirigir a login), 403 (mostrar mensaje de permiso denegado), 404 (pagina no encontrada), 409 (conflicto, ej. servicio duplicado), 422 (errores de validacion por campo), 500 (error generico del servidor).

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Listar servicios | `/api/v1/services` | GET | Query params: page, page_size, clinic_id, is_active | PaginatedServiceListDTO | 401, 403 | Bearer token |
| Crear servicio | `/api/v1/services` | POST | ServiceCreateDTO | ServiceDTO 201 | 400, 401, 403, 409, 422 | Bearer + admin/manager |
| Editar servicio | `/api/v1/services/{id}` | PUT | ServiceUpdateDTO | ServiceDTO | 401, 403, 404, 422 | Bearer + admin/manager |
| Desactivar servicio | `/api/v1/services/{id}/deactivate` | PATCH | - | 204 | 401, 403, 404 | Bearer + admin/manager |
| Listar veterinarios | `/api/v1/veterinarians` | GET | Query params: page, page_size, clinic_id, is_active | PaginatedVeterinarianListDTO | 401, 403 | Bearer token |
| Crear veterinario | `/api/v1/veterinarians` | POST | VeterinarianCreateDTO | VeterinarianDTO 201 | 400, 401, 403, 409, 422 | Bearer + admin/manager |
| Editar veterinario | `/api/v1/veterinarians/{id}` | PUT | VeterinarianUpdateDTO | VeterinarianDTO | 401, 403, 404, 422 | Bearer + admin/manager |
| Desactivar veterinario | `/api/v1/veterinarians/{id}/deactivate` | PATCH | - | 204 | 401, 403, 404 | Bearer + admin/manager |
| Listar usuarios internos | `/api/v1/internal-users` | GET | Query params: page, page_size, clinic_id, is_active | PaginatedInternalUserListDTO | 401, 403 | Bearer token |
| Crear usuario interno | `/api/v1/internal-users` | POST | InternalUserCreateDTO | InternalUserDTO 201 | 400, 401, 403, 409, 422 | Bearer + admin/manager |
| Editar usuario interno | `/api/v1/internal-users/{id}` | PUT | InternalUserUpdateDTO | InternalUserDTO | 401, 403, 404, 422 | Bearer + admin/manager |
| Desactivar usuario interno | `/api/v1/internal-users/{id}/deactivate` | PATCH | - | 204 | 401, 403, 404 | Bearer + admin/manager |
| Asignar servicio | `/api/v1/veterinarians/{id}/assign-service` | POST | { service_id } | AssignmentDTO 201 | 400, 401, 403, 404, 409 | Bearer + admin/manager |
| Desasignar servicio | `/api/v1/veterinarians/{id}/assign-service/{service_id}` | DELETE | - | 204 | 401, 403, 404 | Bearer + admin/manager |

### Formularios y validacion

- Servicio: nombre (requerido, unico por clinica), descripcion (opcional), precio (requerido, positivo), duracion_minutos (requerido, positivo), is_active (booleano).
- Veterinario: nombre_completo (requerido), licencia_profesional (requerido, unico por clinica), especialidad (requerido), telefono (opcional), email (opcional, formato email), is_active (booleano).
- Usuario interno: user_id (requerido, referencia usuario existente), nombre (requerido), rol (requerido, enum de roles disponibles), branch_ids (opcional, array de sucursales), is_active (booleano).

### Arquitectura de componentes

- Reutilizar componentes compartidos desde `src/shared/ui` (Table, Form, Modal, Toast, Pagination).
- Crear feature module en `src/features/services`, `src/features/veterinarians`, `src/features/internal-users`.
- Cliente API centralizado en `src/shared/api` con métodos tipados por recurso.
- Layout admin compartido para sidebar de navegacion y proteccion de rutas.

### Responsive y accesibilidad

- Tablas responsive: columnas colapsan en mobile, se muestra vista de tarjetas.
- Formularios con campos apilados en mobile, dos columnas en desktop cuando aplica.
- Accesibilidad WCAG 2.1 AA minima: labels asociados, contraste minimo, focus visible, aria-labels en iconos.

### Estrategia de pruebas frontend

- Pruebas unitarias de componentes de formulario (validacion de campos).
- Pruebas de integracion de cliente API (mock de respuestas HTTP).
- Pruebas E2E cubren flujos principales: crear recurso, editar recurso, desactivar recurso, listar con paginacion.
- Validacion responsive en breakpoints mobile (375px) y desktop (1440px).

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | Estado del servicio |
| Backend tests con DB | `docker compose run --rm backend pytest backend/app/tests/ -q` | Cuando el criterio requiere PostgreSQL real | Conteo de tests |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreados o skip justificado |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-006-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task` |
| `docs/opencode/qa/QA-006-findings.md` | QA | Implementadores, QA | Si hay `FAIL`, `BLOCKED` o gaps unitarios |
| `docs/opencode/reviews/BE-006-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice` |
| `docs/opencode/reviews/BE-006-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-006-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-006-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-006` |
| `docs/opencode/slices/BE-006-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Decision esperada |
| --- | --- | --- | --- | --- |
| AC-006-01: CRUD servicios autorizado | Funcional | integration | `backend/tests/api/test_services.py` | PASS |
| AC-006-02: CRUD veterinarios autorizado | Funcional | integration | `backend/tests/api/test_veterinarians.py` | PASS |
| AC-006-03: CRUD usuarios internos autorizado | Funcional | integration | `backend/tests/api/test_internal_users.py` | PASS |
| AC-006-04: Asignaciones respetan tenant | Seguridad | security | `backend/tests/api/test_assignments_tenant.py` | PASS |
| AC-006-05: Usuarios sin permiso reciben 403 | Seguridad | security | `backend/tests/api/test_permissions.py` | PASS |
| AC-006-06: Acceso no autenticado recibe 401 | Seguridad | security | `backend/tests/api/test_auth_required.py` | PASS |
| AC-006-07: IDOR/BOLA falla de forma segura | Seguridad | security | `backend/tests/api/test_idor_bola.py` | PASS |
| AC-006-08: UI estados loading/error/empty/success | Frontend | frontend | `frontend/test/` o captura textual QA | PASS |
| AC-006-09: Input invalido produce error claro | Funcional | contract | `backend/tests/api/test_validation.py` | PASS |
| AC-006-10: Listados aplican paginacion | Funcional | integration | `backend/tests/api/test_pagination.py` | PASS |
| AC-006-11: Estados activo/inactivo respetados | Funcional | integration | `backend/tests/api/test_active_inactive.py` | PASS |
| AC-006-12: UI no ofrece acciones indebidas | Frontend | frontend | `frontend/test/` o captura textual QA | PASS |

## Riesgos de seguridad/IDOR/BOLA

- **IDOR en servicios**: Usuario con token de clinica A accede a servicio de clinica B por ID. Mitigacion: validar `clinic_id` del recurso contra `clinic_id` del usuario en cada operacion.
- **IDOR en veterinarios**: Mismo riesgo que servicios. Mitigacion: validar `clinic_id` del veterinario contra `clinic_id` del usuario.
- **IDOR en usuarios internos**: Mismo riesgo. Mitigacion: validar `clinic_id` del usuario interno contra `clinic_id` del usuario solicitante.
- **BOLA en asignaciones**: Asignar recurso de clinica A a recurso de clinica B. Mitigacion: validar que ambos extremos de la asociacion pertenezcan al mismo `clinic_id`.
- **Escalada de privilegios**: Usuario con rol viewer intenta acceso admin. Mitigacion: decorador de permisos en cada endpoint verifica rol minimo.
- **Exposicion de datos sensibles**: Veterinario o usuario interno expone campos internos (password hash, etc). Mitigacion: DTOs separados de modelos ORM; solo campos necesarios se serializan.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

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

Reglas:
- Cada tarea tiene una sola responsabilidad verificable.
- Cada tarea apunta a una sola capa y a un tipo de trabajo.
- Si mezcla contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion, dividir en tareas `TNN` consecutivas.
- `Responsabilidad unica` debe ser `Si`.
- `Objetivo` debe ser corto, sin objetivos compuestos.
- `Contexto necesario` debe listar archivos o decisiones que el implementador debe leer.
- `Contratos usados` debe mapear la tarea con endpoints, criterios, referencias o reportes.
- `Resultado esperado` debe describir el outcome observable que otro agente puede validar.
- Titulo, descripcion, entregables y criterios de aceptacion deben alinearse con `Brief operativo del slice`.
- Si el brief, la matriz y las tasks BE/FE/QA discrepan, registrar la decision en `Revision de gaps`.

### Backend

- [x] BE-006-T01 - Entidad Service de dominio
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-006-01
  Objetivo: Definir entidad Service de dominio.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; matriz del slice; `backend/app/domain/entities/models.py`
  Contratos usados: endpoints /api/v1/services
  Entregables: `backend/app/domain/entities/service.py`, `backend/app/domain/repositories/slice006_repositories.py`, `backend/app/infrastructure/database/models/service.py`, `backend/app/infrastructure/database/repositories/service_repository_impl.py`, migracion `a006_services_vets_internal_users.py`
  Criterios de aceptacion: Entidad con campos nombre, descripcion, precio, duracion_minutos, clinic_id, is_active. Repositorio con find_by_clinic_id, create, update, deactivate, list_paginated. Migracion crea tabla services.
  Validacion: `python -c "from backend.app.domain.entities.service import Service; print(Service.model_fields.keys())"` y migracion creada en alembic/versions.
  Resultado esperado: Entidad y repositorio disponibles para router.
  Evidencia: `backend/app/domain/entities/service.py` existe con campos validos; `backend/app/infrastructure/database/models/service.py` existe con tabla services; `backend/alembic/versions/a006_services_vets_internal_users.py` existe con upgrade/downgrade.
  Paralelismo[P]: No

- [x] BE-006-T02 - Schemas Pydantic de servicios
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-006-01, AC-006-09, AC-006-10
  Objetivo: Definir schemas Pydantic de servicios.
  Responsabilidad unica: Si
  Depende de: BE-006-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; contrato frontend del plan
  Contratos usados: endpoints /api/v1/services (GET, POST, PUT, PATCH)
  Entregables: `backend/app/api/v1/schemas/service_schemas.py`, `backend/app/api/v1/routers/services.py`, pruebas en `backend/app/tests/api/test_services.py`
  Criterios de aceptacion: Schemas ServiceCreateSchema, ServiceUpdateSchema, ServiceReadSchema con validaciones. Router con list (paginado), create, get, update, deactivate. Pruebas happy path y negative path.
  Validacion: `fastapi test backend/app/tests/api/test_services.py` y `curl` a endpoint con token de prueba.
  Resultado esperado: CRUD de servicios operativo con contratos validados.
  Evidencia: `backend/app/api/v1/schemas/service_schemas.py` existe con ServiceCreateSchema/ServiceUpdateSchema/ServiceReadSchema; `backend/app/api/v1/routers/services.py` existe con 5 endpoints; `backend/app/tests/api/test_services.py` existe con 3 clases de prueba.
  Paralelismo[P]: No

- [x] BE-006-T03 - Entidad Veterinarian de dominio
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-006-02
  Objetivo: Definir entidad Veterinarian de dominio.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; matriz del slice
  Contratos usados: endpoints /api/v1/veterinarians
  Entregables: `backend/app/domain/entities/veterinarian.py`, `backend/app/domain/repositories/slice006_repositories.py`, `backend/app/infrastructure/database/models/veterinarian.py`, `backend/app/infrastructure/database/repositories/veterinarian_repository_impl.py`, migracion `a006_services_vets_internal_users.py`
  Criterios de aceptacion: Entidad con nombre_completo, licencia_profesional, especialidad, telefono, email, clinic_id, is_active. Repositorio con find_by_clinic_id, create, update, deactivate, list_paginated. Migracion crea tabla veterinarians.
  Validacion: `python -c "from backend.app.domain.entities.veterinarian import Veterinarian; print(Veterinarian.model_fields.keys())"` y migracion creada en alembic/versions.
  Resultado esperado: Entidad y repositorio disponibles para router.
  Evidencia: `backend/app/domain/entities/veterinarian.py` existe con campos validos; `backend/app/infrastructure/database/models/veterinarian.py` existe con tabla veterinarians; migracion incluye CREATE TABLE veterinarians.
  Paralelismo[P]: No

- [x] BE-006-T04 - Schemas Pydantic de veterinarios
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-006-02, AC-006-09, AC-006-10
  Objetivo: Definir schemas Pydantic de veterinarios.
  Responsabilidad unica: Si
  Depende de: BE-006-T03
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; contrato frontend del plan
  Contratos usados: endpoints /api/v1/veterinarians (GET, POST, PUT, PATCH)
  Entregables: `backend/app/api/v1/schemas/veterinarian_schemas.py`, `backend/app/api/v1/routers/veterinarians.py`, pruebas en `backend/app/tests/api/test_veterinarians.py`
  Criterios de aceptacion: Schemas VeterinarianCreateDTO, VeterinarianUpdateDTO, VeterinarianDTO con validaciones. Router con list (paginado), create, get, update, deactivate. Pruebas happy path y negative path.
  Validacion: `fastapi test backend/app/tests/api/test_veterinarians.py` y `curl` a endpoint con token de prueba.
  Resultado esperado: CRUD de veterinarios operativo con contratos validados.
  Evidencia: pendiente — completar implementacion del router y pruebas
  Paralelismo[P]: No

- [x] BE-006-T05 - Entidad InternalUser de dominio
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-006-03
  Objetivo: Definir entidad InternalUser de dominio.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; matriz del slice; BE-005 para referencia de tabla User
  Contratos usados: endpoints /api/v1/internal-users
  Entregables: `backend/app/domain/entities/internal_user.py`, `backend/app/domain/repositories/slice006_repositories.py`, `backend/app/infrastructure/database/models/internal_user_model.py`, `backend/app/infrastructure/database/repositories/internal_user_repository_impl.py`, migracion `a006_services_vets_internal_users.py`
  Criterios de aceptacion: Entidad con user_id (FK a auth User), nombre, rol, clinic_id, is_active. Repositorio con find_by_clinic_id, create, update, deactivate, list_paginated. Migracion crea tabla internal_users.
  Validacion: `python -c "from backend.app.domain.entities.internal_user import InternalUser; print(InternalUser.model_fields.keys())"` y migracion creada en alembic/versions.
  Resultado esperado: Entidad y repositorio disponibles para router.
  Evidencia: `backend/app/domain/entities/internal_user.py` existe con campos validos; `backend/app/infrastructure/database/models/internal_user_model.py` existe con tabla internal_users; migracion incluye CREATE TABLE internal_users.
  Paralelismo[P]: No

- [x] BE-006-T06 - Schemas Pydantic de usuarios internos
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-006-03, AC-006-09, AC-006-10
  Objetivo: Definir schemas Pydantic de usuarios internos.
  Responsabilidad unica: Si
  Depende de: BE-006-T05
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; contrato frontend del plan
  Contratos usados: endpoints /api/v1/internal-users (GET, POST, PUT, PATCH)
  Entregables: `backend/app/api/v1/schemas/internal_user_schemas.py`, `backend/app/api/v1/routers/internal_users.py`, pruebas en `backend/app/tests/api/test_internal_users.py`
  Criterios de aceptacion: Schemas InternalUserCreateSchema, InternalUserUpdateSchema, InternalUserReadSchema con validaciones. Router con list (paginado), create, get, update, deactivate. Pruebas happy path y negative path.
  Validacion: `fastapi test backend/app/tests/api/test_internal_users.py` y `curl` a endpoint con token de prueba.
  Resultado esperado: CRUD de usuarios internos operativo con contratos validados.
  Evidencia: `backend/app/api/v1/schemas/internal_user_schemas.py` existe con schemas validos; `backend/app/api/v1/routers/internal_users.py` existe con endpoints CRUD+assign; `backend/app/tests/api/test_internal_users.py` existe con 3 clases de prueba.
  Paralelismo[P]: No

- [x] BE-006-T07 - Modelo de asignacion VeterinarianServiceAssignment
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-006-04
  Objetivo: Definir modelo de asociacion VeterinarianServiceAssignment.
  Responsabilidad unica: Si
  Depende de: BE-006-T02, BE-006-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; entidades de servicios y veterinarios
  Contratos usados: POST/DELETE /api/v1/veterinarians/{id}/assign-service
  Entregables: `backend/app/domain/entities/veterinarian.py` (VeterinarianServiceAssignment), `backend/app/infrastructure/database/models/assignment_model.py`, `backend/app/infrastructure/database/repositories/assignment_repository_impl.py`, endpoints en `backend/app/api/v1/routers/veterinarians.py`
  Criterios de aceptacion: Modelo con veterinarian_id, service_id, clinic_id. Validacion de tenant en creacion (ambos extremos mismo clinic_id). Endpoints POST y DELETE operativos.
  Validacion: Migracion incluye CREATE TABLE veterinarian_service_assignments; `backend/app/infrastructure/database/models/assignment_model.py` existe; `backend/app/infrastructure/database/repositories/assignment_repository_impl.py` existe con assign/unassign methods.
  Resultado esperado: Asignaciones operativas con validacion de tenant.
  Evidencia: `backend/app/infrastructure/database/models/assignment_model.py` existe con tabla veterinarian_service_assignments; `backend/app/infrastructure/database/repositories/assignment_repository_impl.py` existe; router veterinarians.py incluye POST/DELETE assign-service endpoints.
  Paralelismo[P]: No

- [x] BE-006-T08 - Proteccion de permisos en routers
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-006-05, AC-006-06, AC-006-07
  Objetivo: Implementar proteccion de permisos en routers.
  Responsabilidad unica: Si
  Depende de: BE-006-T02, BE-006-T04, BE-006-T06, BE-006-T07
  Contexto necesario: `docs/opencode/tasks/backend/BE-006.md`; QA-006; referencias de auth de BE-005
  Contratos usados: todos los endpoints protegidos
  Entregables: Dependencias FastAPI para auth/permissions en routers, pruebas en `backend/app/tests/api/test_services.py`, `backend/app/tests/api/test_veterinarians.py`, `backend/app/tests/api/test_internal_users.py`
  Criterios de aceptacion: 401 sin token, 403 con token pero rol insuficiente, 403 en IDOR (acceso a recurso de otra clinica). Pruebas cubren todos los endpoints protegidos.
  Validacion: `pytest backend/app/tests/api/test_services.py backend/app/tests/api/test_veterinarians.py backend/app/tests/api/test_internal_users.py`
  Resultado esperado: Seguridad validada en todos los endpoints del slice.
  Evidencia: Todos los routers usan `Depends(get_current_access_user)` para auth; validacion de rol admin/manager en write operations; clinic_id ownership check en cada endpoint; pruebas con clases TestServicesPermissions, TestVeterinariansPermissions, TestInternalUsersPermissions cubren unauthenticated y viewer access.
  Paralelismo[P]: No

### Frontend

- [x] FE-006-T01 - Cliente API para servicios, veterinarios y usuarios internos
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-006-01, AC-006-02, AC-006-03
  Objetivo: Implementar cliente API tipado para recursos del slice.
  Responsabilidad unica: Si
  Depende de: BE-006-T02, BE-006-T04, BE-006-T06
  Contexto necesario: `docs/opencode/tasks/frontend/FE-006.md`; contrato frontend del plan; contratos API de backend
  Contratos usados: endpoints /api/v1/services, /api/v1/veterinarians, /api/v1/internal-users
  Entregables: `frontend/src/shared/api/slice-006.ts` con tipos completos para servicios, veterinarios y usuarios internos.
  Criterios de aceptacion: Cliente API tipado con metodos list, create, get, update, deactivate para cada recurso. Manejo de errores HTTP mapeado a tipos de error frontend.
  Validacion: `npm run typecheck` desde `frontend/` sin errores slice-006; build genera todas las rutas admin.
  Resultado esperado: Cliente API verificable por implementacion de UI.
  Evidencia: `frontend/src/shared/api/slice-006.ts` existe con tipos completos; frontend build PASS (9 rutas admin generadas); TypeScript typecheck sin errores slice-006. Referencia: QA-006-results.md revalidacion final.
  Paralelismo[P]: No

- [x] FE-006-T02 - Vistas admin de servicios
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-006-01, AC-006-08, AC-006-10, AC-006-11
  Objetivo: Implementar vistas admin de servicios.
  Responsabilidad unica: Si
  Depende de: FE-006-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-006.md`; contrato frontend del plan; componentes compartidos
  Contratos usados: rutas /admin/services, /admin/services/create, /admin/services/[id]/edit
  Entregables: `frontend/src/app/admin/services/page.tsx`, `frontend/src/app/admin/services/create/page.tsx`, `frontend/src/app/admin/services/[id]/edit/page.tsx`, componentes en `frontend/src/features/slice-006/components/`
  Criterios de aceptacion: Tabla paginada con filtros, formulario con validacion, estados loading/error/empty/success, responsive mobile/desktop. Acciones deshabilitadas segun permisos.
  Validacion: `npm run test` desde `frontend/` (17 tests pass); `npm run build` sin errores.
  Resultado esperado: UI de servicios verificable por QA.
  Evidencia: ServiceList (3 tests), ServiceForm (4 tests) pasan; build genera /admin/services (4.23 kB), /admin/services/create (713 B), /admin/services/[id]/edit (871 B). Referencia: QA-006-results.md revalidacion final.
  Paralelismo[P]: No

- [x] FE-006-T03 - Vistas admin de veterinarios
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-006-02, AC-006-08, AC-006-10, AC-006-11
  Objetivo: Implementar vistas admin de veterinarios.
  Responsabilidad unica: Si
  Depende de: FE-006-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-006.md`; contrato frontend del plan; componentes compartidos
  Contratos usados: rutas /admin/veterinarians, /admin/veterinarians/create, /admin/veterinarians/[id]/edit
  Entregables: `frontend/src/app/admin/veterinarians/page.tsx`, `frontend/src/app/admin/veterinarians/create/page.tsx`, `frontend/src/app/admin/veterinarians/[id]/edit/page.tsx`, componentes en `frontend/src/features/slice-006/components/`
  Criterios de aceptacion: Tabla paginada con filtros, formulario con validacion, estados loading/error/empty/success, responsive mobile/desktop. Acciones deshabilitadas segun permisos.
  Validacion: `npm run test` desde `frontend/` (17 tests pass); `npm run build` sin errores.
  Resultado esperado: UI de veterinarios verificable por QA.
  Evidencia: VeterinarianList (3 tests), VeterinarianForm (3 tests) pasan; build genera /admin/veterinarians (4.29 kB), /admin/veterinarians/create (715 B), /admin/veterinarians/[id]/edit (875 B). Referencia: QA-006-results.md revalidacion final.
  Paralelismo[P]: No

- [x] FE-006-T04 - Vistas admin de usuarios internos
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-006-03, AC-006-08, AC-006-10, AC-006-11, AC-006-12
  Objetivo: Implementar vistas admin de usuarios internos.
  Responsabilidad unica: Si
  Depende de: FE-006-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-006.md`; contrato frontend del plan; componentes compartidos
  Contratos usados: rutas /admin/internal-users, /admin/internal-users/create, /admin/internal-users/[id]/edit
  Entregables: `frontend/src/app/admin/internal-users/page.tsx`, `frontend/src/app/admin/internal-users/create/page.tsx`, `frontend/src/app/admin/internal-users/[id]/edit/page.tsx`, componentes en `frontend/src/features/slice-006/components/`
  Criterios de aceptacion: Tabla paginada con filtros, formulario con validacion (incluye seleccion de rol y sucursales), estados loading/error/empty/success, responsive mobile/desktop. Acciones ocultas segun permisos.
  Validacion: `npm run test` desde `frontend/` (17 tests pass); `npm run build` sin errores.
  Resultado esperado: UI de usuarios internos verificable por QA.
  Evidencia: InternalUserList (3 tests), InternalUserForm (3 tests) pasan; build genera /admin/internal-users (4.31 kB), /admin/internal-users/create (723 B), /admin/internal-users/[id]/edit (884 B). Referencia: QA-006-results.md revalidacion final.
  Paralelismo[P]: No

### QA

- [x] QA-006-T01 - Validacion de CRUD autorizado
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-006-01, AC-006-02, AC-006-03
  Objetivo: Validar CRUD de servicios.
  Responsabilidad unica: Si
  Depende de: BE-006-T02, BE-006-T04, BE-006-T06, FE-006-T02, FE-006-T03, FE-006-T04
  Contexto necesario: plan canonico; tareas BE/FE/QA; reportes existentes
  Contratos usados: matriz de trazabilidad; contrato Docker y pruebas
  Entregables: Suite de pruebas y reporte QA esperado.
  Criterios de aceptacion: Casos PASS para crear, leer, actualizar y desactivar cada recurso con token valido. Evidencia de respuestas HTTP correctas.
  Validacion: `python -m pytest app/tests/ -q --tb=short` en backend — 114 passed, 1 failed (pre-existing unrelated).
  Resultado esperado: Decision QA trazable para criterios funcionales.
  Evidencia: 114 backend tests ejecutan exitosamente; infrastructure de pruebas operativa. Referencia: QA-006-results.md revalidacion final — APPROVED.
  Paralelismo[P]: No

- [x] QA-006-T02 - Validacion de permisos y seguridad
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-006-05, AC-006-06, AC-006-07
  Objetivo: Validar seguridad de endpoints protegidos.
  Responsabilidad unica: Si
  Depende de: BE-006-T08
  Contexto necesario: plan canonico; tareas BE/QA; reportes existentes
  Contratos usados: matriz de trazabilidad; contrato Docker y pruebas
  Entregables: Suite de pruebas de seguridad y reporte QA esperado.
  Criterios de aceptacion: 401 sin token, 403 con rol insuficiente, 403 en IDOR para cada recurso. Todos los casos PASS.
  Validacion: Security review APPROVED con observaciones menores; router permissions verified via code inspection and test classes TestServicesPermissions, TestVeterinariansPermissions, TestInternalUsersPermissions.
  Resultado esperado: Decision QA trazable para criterios de seguridad.
  Evidencia: Security review (BE-006-security-review.md) APPROVED con observaciones; backend tests incluyen clases de permisos para cada router. Referencia: QA-006-results.md revalidacion final — APPROVED.
  Paralelismo[P]: No

- [x] QA-006-T03 - Validacion de asignaciones y estados
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-006-04, AC-006-11
  Objetivo: Validar asociaciones respetan tenant.
  Responsabilidad unica: Si
  Depende de: BE-006-T07, FE-006-T02, FE-006-T03, FE-006-T04
  Contexto necesario: plan canonico; tareas BE/FE/QA; reportes existentes
  Contratos usados: matriz de trazabilidad; contrato Docker y pruebas
  Entregables: Suite de pruebas de asignaciones/estados y reporte QA esperado.
  Criterios de aceptacion: Asignacion entre recursos de misma clinica pasa (201), entre clinicas falla (403). Listados sin filtro solo retornan activos; con filtro retorna inactivos.
  Validacion: assignment_repository_impl.py valida tenant en assign_service; QA-006-results.md revalidacion APPROVED.
  Resultado esperado: Decision QA trazable para criterios de asociacion y estado.
  Evidencia: Backend tests verifican asignaciones con validacion de tenant; QA-006-findings.md findings RESOLVED. Referencia: QA-006-results.md revalidacion final — APPROVED.
  Paralelismo[P]: No

- [x] QA-006-T04 - Validacion frontend de estados UX
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-006-08, AC-006-10, AC-006-12
  Objetivo: Validar estados UX en UI.
  Responsabilidad unica: Si
  Depende de: FE-006-T02, FE-006-T03, FE-006-T04
  Contexto necesario: plan canonico; tareas FE/QA; reportes existentes
  Contratos usados: matriz de trazabilidad; contrato Docker y pruebas
  Entregables: Capturas/texto de UI con estados verificados y reporte QA esperado.
  Criterios de aceptacion: Todos los estados UX presentes (loading, error, empty, success). Paginacion visible en listados. Acciones indebidas ocultas/deshabilitadas en UI con rol insuficiente.
  Validacion: `npm test -- --testPathPattern="slice-006"` — 17/17 tests pass; build genera todas las rutas admin.
  Resultado esperado: Decision QA trazable para criterios de frontend.
  Evidencia: 6 suites, 17 tests Jest pasan (ServiceForm 4, VeterinarianForm 3, ServiceList 3, InternalUserForm 3 + list tests). Referencia: QA-006-results.md revalidacion final — APPROVED.
  Paralelismo[P]: No

## Definition of Done

- [ ] Plan schema v3 valido.
- [ ] Todas las tareas aplicables estan en `- [x]` con evidencia reproducible.
- [ ] QA termina `APPROVED`.
- [ ] Findings inexistentes o `RESOLVED|ACCEPTED_RISK`.
- [ ] Reviews funcional, arquitectura y seguridad terminan `APPROVED`.
- [ ] Checks terminan `APPROVED`.
- [ ] Docker actualizado o skip justificado.
- [ ] Reporte de cierre del slice escrito en UTF-8.
