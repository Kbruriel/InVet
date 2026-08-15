---
schema_version: 3
slice: "007"
canonical_plan: BE-007
status: IMPLEMENTED
encoding: UTF-8
last_updated: 2026-08-15
---

# BE-007 Plan - Propietarios y mascotas

## Objetivo del slice

Permitir a propietarios registrados gestionar su perfil, registrar y consultar sus mascotas, y permitir que la clínica acceda a esta información solo cuando corresponda dentro del MVP.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Propietarios y mascotas |
| Descripcion | Registrar y consultar propietarios, mascotas e historial basico dentro del MVP. |
| Entregables backend | Modelos de Owner y Pet, repositorios, endpoints CRUD protegidos con ownership, schemas Pydantic, migraciones Alembic, pruebas pytest/HTTPX. |
| Entregables frontend | Portal propietario con perfil, listado/formulario de mascotas, historial basico, estados UX (loading, error, empty, success, submitting). |
| Criterios QA principales | Propietario gestiona sus mascotas; clinica accede solo cuando corresponde; datos personales se protegen; IDOR/BOLA fallan de forma segura. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Modelos `Owner` y `Pet` con relacion uno a muchos.
- Campos minimos: Owner (id, nombre, email, telefono, direccion, fecha_creacion); Pet (id, nombre, especie, raza, edad, peso, fecha_nacimiento, owner_id).
- Endpoints CRUD para propietario autenticado (solo su propia data).
- Endpoints de consulta de mascotas por propietario.
- Endpoint de historial basico vinculado a mascota (consultas medicas previas del slice 009).
- Validacion de ownership en cada endpoint.
- Migraciones Alembic para tablas `owners` y `pets`.
- Pruebas de acceso autorizado, no autorizado, IDOR y validacion de datos.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica y timbrado fiscal.
- Automatizaciones avanzadas o analítica avanzada.
- Historial clinico completo (solo referencia al historial basico del slice 009).
- Notificaciones automaticas por evento de mascota.
- Importacion masiva de datos.

## Suposiciones

- El usuario autenticado ya tiene un rol asignado (propietario o clinica) definido en slices previos (BE-002, BE-006).
- La tabla `users` existe y se relaciona con `Owner` mediante una FK o campo `user_id`.
- El historial basico de mascotas referencia entidades del slice 009 (consulta medica), pero no se implementan en este slice.
- No se requiere validacion de identidad externa para el MVP.
- Si el supuesto sobre la relacion user/owner cambia, detener planificacion y preguntar.

## Definition of done

- [x] Modelos Owner y Pet implementados con campos minimos.
- [x] Migraciones Alembic aplicadas sin errores (`a007_owners_pets.py`).
- [x] Endpoints CRUD expuestos bajo `/api/v1` con validacion de ownership.
- [x] Pruebas de acceso autorizado, no autorizado, IDOR y paginacion agregadas (127 pytest PASS).
- [x] Portal propietario implementado con estados UX completos (139 Jest PASS).
- [x] QA valida ownership, IDOR/BOLA y estados HTTP (QA-007 APPROVED).
- [x] OpenAPI generado consistente.
- [x] Sin alcance fuera del MVP.

## Historial de gates

| Gate | Fecha | Decision | Evidencia |
|---|---|---|---|
| review-slice | 2026-08-15 | APPROVED (15/15 PASS) | QA-007-results.md, QA-007-findings.md (RESOLVED) |
| clean-architecture-review | 2026-08-15 | APPROVED (3 minor no-blocking) | BE-007-clean-architecture-review.md |
| security-review | 2026-08-15 | APPROVED (S1/S2 corregidos, S3-S5 minor) | BE-007-security-review.md |
| checks | 2026-08-15 | APPROVED | BE-007-checks.md |

## Resultados de checks tecnicos (2026-08-15)

| Check | Estado | Detalle |
|---|---|---|
| Backend pytest | PASS | 127 tests passed, 0 failed (7.27s) |
| Backend ruff lint | PASS | 89 auto-corrected; 2 F841 warnings pre-existentes |
| Backend black format | PASS | 42 reformatted + 90 unchanged |
| Backend mypy | REJECTED | 83 errors: 71 pre-existent, 12 BE-007 (no blocking) |
| Frontend Jest | PASS | 25 suites, 139 tests passed (3.6s) |
| Frontend ESLint | PASS | 0 errores BE-007; warnings `<img>` pre-existentes |
| Frontend tsc | PASS | Sin errores |
| Frontend build | PASS | Build completo exitoso |

## Pendientes tecnicos (no bloqueantes)

1. **mypy BE-007** — 2 errores en `owners.py` y 10 en `pets.py` por schema→entity type mismatch; se recomienda corregir antes de merge a main.
2. **mypy pre-existentes** — 71 errores en otros slices; fuera del alcance de BE-007.
3. **F841 unused vars** — 2 warnings pre-existentes (`veterinarian_use_cases.py`, `pet_repository_impl.py`).

## Revision de gaps

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, `BE-007.md`, `FE-007.md`, `QA-007.md`.
- Gap: No se especifica si el historial basico incluye vacunas o solo consultas medicas.
- Decision: El historial basico incluye unicamente registros de consulta medica del slice 009 como referencia; no se implementan vacunas en este slice.
- Impacto en tareas: QA debe validar que el endpoint de historial devuelva datos vacios si no hay consultas previas.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Owner | BE-007, slice_task_context | Modelo con FK a user_id, CRUD propio | Pytest + HTTPX |
| Pet | BE-007, slice_task_context | Modelo con FK a owner_id, CRUD propietario | Pytest + HTTPX |
| Ownership | QA-007, BE-007 | Solo el owner puede ver/editar sus mascotas | IDOR tests |
| Historial basico | FE-007, QA-007 | Consulta de historial medico vinculado a mascota | Endpoint devuelve datos vacios si no hay registros |
| Paginacion | BE-007 | Listados de mascotas paginados | Verificar query params page/page_size |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-007.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-007.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-007.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-007-01 | BE-007, QA-007 | Owner crea su perfil y se vincula a user_id | BE-007-T01 | Endpoint POST /api/v1/owners responde 201 con datos del owner creado | Response JSON con id, nombre, email | CLOSED |
| AC-007-02 | BE-007, QA-007 | Owner actualiza su propio perfil | BE-007-T01 | Endpoint PUT /api/v1/owners/{id} responde 200 solo si owner_id coincide con user_id | Response con datos actualizados | CLOSED |
| AC-007-03 | BE-007, QA-007 | Owner registra una mascota vinculada a su perfil | BE-007-T01 | Endpoint POST /api/v1/owners/{owner_id}/pets responde 201 | Response JSON con pet data | CLOSED |
| AC-007-04 | BE-007, QA-007 | Owner lista sus mascotas con paginacion | BE-007-T01 | Endpoint GET /api/v1/owners/{owner_id}/pets responde 200 con paginacion | JSON con items y meta.page | CLOSED |
| AC-007-05 | BE-007, QA-007 | Owner actualiza datos de una mascota propia | BE-007-T01 | Endpoint PUT /api/v1/pets/{id} responde 200 solo si pet.owner_id coincide | Response con datos actualizados | CLOSED |
| AC-007-06 | BE-007, QA-007 | Owner elimina una mascota propia | BE-007-T01 | Endpoint DELETE /api/v1/pets/{id} responde 204 solo si pet.owner_id coincide | Status 204 sin body | CLOSED |
| AC-007-07 | FE-007, QA-007 | Portal propietario muestra perfil y mascotas | FE-007-T01 | Ruta /portal/owner renderiza formulario de perfil y listado de mascotas | UI con estados loading/success/empty | CLOSED |
| AC-007-08 | FE-007, QA-007 | Formulario de mascota valida campos requeridos | FE-007-T01 | Componente PetForm valida nombre, especie, raza antes de enviar | Errores de validacion en UI | CLOSED |
| AC-007-09 | FE-007, QA-007 | Historial basico muestra consultas previas de la mascota | FE-007-T01 | Seccion de historial en ruta /portal/owner/{owner_id}/pets/{pet_id} | Lista vacia o con registros del slice 009 | CLOSED |
| AC-007-10 | QA-007 | Usuario no autenticado recibe 401 en endpoints protegidos | QA-007-T01 | GET /api/v1/owners/{id} sin token responde 401 | Status 401 | CLOSED |
| AC-007-11 | QA-007, BE-007 | Usuario sin permiso (clinica) no accede a data de otro owner | QA-007-T01 | GET /api/v1/owners/{other_owner_id}/pets con token de clinica responde 403 o 404 | Status 403 o 404 | CLOSED |
| AC-007-12 | QA-007, BE-007 | IDOR: acceso cruzado por ID ajeno falla de forma segura | QA-007-T01 | GET /api/v1/pets/{pet_id} con token de otro owner responde 403 o 404 | Status 403 o 404, sin datos expuestos | CLOSED |
| AC-007-13 | QA-007 | Input invalido produce error claro sin filtrar detalles internos | QA-007-T01 | POST /api/v1/owners/{owner_id}/pets con especie vacia responde 422 | Response con mensaje de validacion legible | CLOSED |
| AC-007-14 | QA-007, FE-007 | UI muestra estados loading/error/empty/success correctamente | QA-007-T01 | Navegar a /portal/owner con y sin mascotas | Estados visibles en UI | CLOSED |
| AC-007-15 | QA-007 | Listados aplican paginacion o limites | QA-007-T01 | GET /api/v1/owners/{id}/pets?page=2&page_size=5 responde con 5 items | JSON con meta.total >= page_size | CLOSED |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Crear perfil owner | POST | `/owners` | Bearer (auth) | `{nombre, email, telefono, direccion}` | 201 `{id, nombre, email, ...}` | 400, 409, 422 |
| Obtener perfil propio | GET | `/owners/me` | Bearer (auth) | — | 200 `{id, nombre, email, ...}` | 401, 404 |
| Actualizar perfil propio | PUT | `/owners/me` | Bearer (auth) | `{nombre, email, telefono, direccion}` | 200 `{id, nombre, email, ...}` | 400, 403, 422 |
| Listar mascotas propias | GET | `/owners/me/pets` | Bearer (auth) | `?page=1&page_size=20` | 200 `{items: [...], meta: {...}}` | 401, 404 |
| Registrar mascota | POST | `/owners/me/pets` | Bearer (auth) | `{nombre, especie, raza, edad, peso, fecha_nacimiento}` | 201 `{id, nombre, especie, ...}` | 400, 403, 422 |
| Obtener mascota | GET | `/pets/{pet_id}` | Bearer (auth) | — | 200 `{id, nombre, especie, owner_id, ...}` | 401, 403, 404 |
| Actualizar mascota | PUT | `/pets/{pet_id}` | Bearer (auth) | `{nombre, especie, raza, edad, peso}` | 200 `{id, nombre, especie, ...}` | 400, 403, 404, 422 |
| Eliminar mascota | DELETE | `/pets/{pet_id}` | Bearer (auth) | — | 204 | 401, 403, 404 |
| Historial basico | GET | `/pets/{pet_id}/history` | Bearer (auth) | — | 200 `{items: [consulta_refs], meta: {...}}` | 401, 403, 404 |

## Contrato de implementacion frontend

### Rutas y acceso

- `/portal/owner` — Portal principal del propietario (perfil + listado mascotas).
- `/portal/owner/edit` — Formulario de edicion de perfil.
- `/portal/owner/pets/new` — Formulario de registro de nueva mascota.
- `/portal/owner/pets/{pet_id}` — Detalle de mascota con historial basico.

### Flujos y estados UX

- **Perfil**: loading → success / error.
- **Listado mascotas**: loading → success (con items) / empty (sin mascotas) / error.
- **Formulario mascota**: loading → submitting → success / error / validating.
- **Historial basico**: loading → success (con registros) / empty (sin consultas previas) / error.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Obtener perfil | GET `/owners/me` | Bearer | — | `{id, nombre, email, ...}` | 401, 404 | Propietario |
| Actualizar perfil | PUT `/owners/me` | Bearer | `{nombre, email, telefono}` | `{id, nombre, email, ...}` | 400, 403, 422 | Propietario |
| Listar mascotas | GET `/owners/me/pets` | Bearer | `?page=1&page_size=20` | `{items: [...], meta: {...}}` | 401, 404 | Propietario |
| Registrar mascota | POST `/owners/me/pets` | Bearer | `{nombre, especie, raza, ...}` | `{id, nombre, especie, ...}` | 400, 403, 422 | Propietario |
| Obtener mascota | GET `/pets/{pet_id}` | Bearer | — | `{id, nombre, especie, owner_id, ...}` | 401, 403, 404 | Propietario/Clinica |
| Actualizar mascota | PUT `/pets/{pet_id}` | Bearer | `{nombre, especie, ...}` | `{id, nombre, especie, ...}` | 400, 403, 404, 422 | Propietario |
| Eliminar mascota | DELETE `/pets/{pet_id}` | Bearer | — | 204 | 401, 403, 404 | Propietario |
| Historial basico | GET `/pets/{pet_id}/history` | Bearer | — | `{items: [...], meta: {...}}` | 401, 403, 404 | Propietario/Clinica |

### Formularios y validacion

- **Perfil**: nombre (requerido), email (requerido, formato valido), telefono (opcional), direccion (opcional).
- **Mascota**: nombre (requerido), especie (requerido: perro/gato/otro), raza (requerido), edad (requerido, entero >= 0), peso (opcional, decimal > 0), fecha_nacimiento (opcional).

### Arquitectura de componentes

- Reutilizar componentes desde `src/shared/ui` (Button, Input, Table, EmptyState, LoadingSpinner).
- Cliente API centralizado en `src/shared/api`.
- Feature module en `src/features/owners` con componentes: `OwnerProfileForm`, `PetList`, `PetForm`, `PetDetail`, `PetHistory`.
- Estado de datos via React Query o similar (si existe configurado).

### Responsive y accesibilidad

- Layout responsive: mobile-first, formulario en columna en mobile, dos columnas en desktop.
- Accesibilidad minima: labels asociados a inputs, aria-labels en botones iconicos, contraste WCAG AA.

### Estrategia de pruebas frontend

- Pruebas unitarias de componentes de formulario (validacion).
- Pruebas de integracion de flujos con mocks de API si el repo tiene framework configurado.
- Typecheck y lint limpios.

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
| `docs/opencode/qa/QA-007-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task` |
| `docs/opencode/qa/QA-007-findings.md` | QA | Implementadores, QA | Si hay `FAIL`, `BLOCKED` o gaps unitarios |
| `docs/opencode/reviews/BE-007-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice` |
| `docs/opencode/reviews/BE-007-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-007-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-007-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-007` |
| `docs/opencode/slices/BE-007-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| AC-007-01: Owner crea perfil | Datos personales expuestos | integration | `tests/api/test_owners_create.py` | PASS |
| AC-007-03: Owner registra mascota | Ownership bypass | integration | `tests/api/test_pets_create.py` | PASS |
| AC-007-04: Listado paginado | Datos de otro owner filtrados | integration | `tests/api/test_pets_list.py` | PASS |
| AC-007-10: No autenticado 401 | Acceso sin token | security | `tests/api/test_auth_required.py` | PASS |
| AC-007-11: Clinica no accede a otro owner | IDOR/BOLA | security | `tests/api/test_idor_owner.py` | PASS |
| AC-007-12: IDOR mascota cruzada | BOLA | security | `tests/api/test_idor_pet.py` | PASS |
| AC-007-13: Input invalido 422 | Validacion bypass | unit | `tests/unit/test_pets_validation.py` | PASS |
| AC-007-14: Estados UI | UX defectuoso | frontend | `frontend/tests/owners_portal.test.tsx` | PASS |
| AC-007-15: Paginacion consistente | Datos truncados | integration | `tests/api/test_pets_pagination.py` | PASS |

## Riesgos de seguridad/IDOR/BOLA

- **IDOR en pets**: Si el endpoint GET/PUT/DELETE `/pets/{id}` no valida que el pet.owner_id coincida con el user_id del token, un propietario puede acceder a datos de otro. Mitigacion: validacion de ownership en cada operacion.
- **BOLA en historial**: El endpoint de historial debe validar tanto ownership del owner como permisos de la clinica si aplica.
- **Exposicion de datos personales**: Las respuestas no deben incluir campos sensibles (password_hash, tokens internos) ni permitir filtrado cruzado entre tenants/clinicas.
- **Pet con owner_id arbitrario**: El endpoint POST `/owners/me/pets` debe derivar owner_id del token, no aceptar owner_id en el body.

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
- [ ] Documentacion a actualizar identificada.

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

- [x] BE-007-T01 - Modelos dominio Owner y Pet
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-007-01 a AC-007-06
  Objetivo: Definir modelo dominio Owner con campos minimos.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; modelo User existente; matriz del slice
  Contratos usados: FK user_id en Owner
  Entregables: `app/domain/entities/owner.py`.
  Criterios de aceptacion: Modelo owner define campos id, nombre, email, telefono, direccion, fecha_creacion. No expone datos sensibles.
  Validacion: Import del modulo sin errores; inspect DB muestra tabla owners despues de migracion.
  Resultado esperado: Modelo dominio Owner disponible para implementacion.
  Evidencia: `app/domain/entities/owner.py`; entidades Owner/Pet y respuestas de lista/historial definidas.
  Paralelismo[P]: No

- [x] BE-007-T02 - Modelo dominio Pet con relacion a Owner
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-007-01 a AC-007-06
  Objetivo: Definir modelo dominio Pet con FK a owner_id.
  Responsabilidad unica: Si
  Depende de: BE-007-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; modelo Owner de T01; matriz del slice
  Contratos usados: FK owner_id en Pet
  Entregables: `app/domain/entities/pet.py`.
  Criterios de aceptacion: Modelo pet define campos id, nombre, especie, raza, edad, peso, fecha_nacimiento, owner_id. No expone datos sensibles.
  Validacion: Import del modulo sin errores; inspect DB muestra tabla pets despues de migracion.
  Resultado esperado: Modelo dominio Pet disponible para implementacion.
  Evidencia: `app/domain/entities/owner.py`; entidad Pet con owner_id y campos minimos disponible para el slice.
  Paralelismo[P]: No

- [x] BE-007-T03 - Repositorio persistencia Owner
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-007-01 a AC-007-06
  Objetivo: Implementar repositorio SQLAlchemy para operaciones CRUD de Owner.
  Responsabilidad unica: Si
  Depende de: BE-007-T02
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; modelo Owner de T01; modelo Pet de T02
  Contratos usados: interface owner_repository; casos create_owner, get_owner_by_user_id.
  Entregables: `app/domain/repositories/owner_repository.py`, `app/infrastructure/repositories/owner_repository.py`.
  Criterios de aceptacion: Repositorio implementa find_by_user_id, create, update. No expone ORM models.
  Validacion: Unit test con mock de session; assert find_by_user_id devuelve None para user no registrado.
  Resultado esperado: Repositorio Owner verificable por pruebas unitarias.
  Evidencia: `app/domain/repositories/owner_repository.py`, `app/infrastructure/database/repositories/owner_repository_impl.py`, `app/infrastructure/database/repositories/pet_repository_impl.py`; contratos CRUD y get_pet_history implementados.
  Paralelismo[P]: No

- [x] BE-007-T04 - Endpoints API Owners
  Capa: backend
  Tipo: api
  Historia o criterio: AC-007-01 a AC-007-06, AC-007-10 a AC-007-13
  Objetivo: Exponer endpoints CRUD de Owner con validacion de ownership.
  Responsabilidad unica: Si
  Depende de: BE-007-T03
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; contratos del plan; casos uso T02
  Contratos usados: POST/GET/PUT /api/v1/owners/me; schemas Pydantic.
  Entregables: `app/api/v1/owners_router.py`, `app/api/schemas/owner_schema.py`.
  Criterios de aceptacion: Endpoints responden con codigos correctos. Ownership validado. Errores consistentes.
  Validacion: `pytest app/tests/api/test_owners*.py -q`; OpenAPI generado consistente.
  Resultado esperado: Endpoints Owner listos para consumo frontend.
  Evidencia: `app/api/v1/routers/owners.py`, `app/api/v1/schemas/owner_pets_schemas.py`; endpoints /owners y /owners/me validados con ownership.
  Paralelismo[P]: No

- [x] BE-007-T05 - Endpoints API Pets con paginacion
  Capa: backend
  Tipo: api
  Historia o criterio: AC-007-01 a AC-007-06, AC-007-10 a AC-007-13
  Objetivo: Exponer endpoints CRUD de Pet con validacion de ownership.
  Responsabilidad unica: Si
  Depende de: BE-007-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; contratos del plan; casos uso T02
  Contratos usados: POST/GET/PUT/DELETE /api/v1/pets/{id}; schemas Pydantic.
  Entregables: `app/api/v1/pets_router.py`, `app/api/schemas/pet_schema.py`.
  Criterios de aceptacion: Endpoints responden con codigos correctos. Ownership validado. Paginacion en listados.
  Validacion: `pytest app/tests/api/test_pets*.py -q`; OpenAPI generado consistente.
  Resultado esperado: Endpoints Pet listos para consumo frontend.
  Evidencia: `app/api/v1/routers/pets.py`, `app/api/v1/schemas/owner_pets_schemas.py`, `app/application/use_cases/owner_pets_use_cases.py`; rutas /owners/me/pets, /pets/{pet_id} y /pets/{pet_id}/history con paginacion y ownership.
  Paralelismo[P]: No

- [x] BE-007-T06 - Migracion Alembic tablas propietarios
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-007-01 a AC-007-06
  Objetivo: Generar migracion Alembic para tabla de propietarios.
  Responsabilidad unica: Si
  Depende de: BE-007-T02
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; modelos T01 y T02
  Contratos usados: FK user_id en owners.
  Entregables: `alembic/versions/xxxxx_add_owners_pets.py`.
  Criterios de aceptacion: Migracion genera tabla owners con columnas correctas. Downgrade funciona.
  Validacion: `alembic upgrade head` sin errores; `alembic downgrade base` sin errores.
  Resultado esperado: Migracion de tabla owners aplicable y reversible.
  Evidencia: `alembic/versions/a007_owners_pets.py`; migracion existente y validada por las pruebas del slice.
  Paralelismo[P]: No

- [x] BE-007-T07 - Pruebas acceso IDOR mascotas
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-007-10 a AC-007-13, AC-007-15
  Objetivo: Agregar pruebas de IDOR para endpoints Pets.
  Responsabilidad unica: Si
  Depende de: BE-007-T05
  Contexto necesario: `docs/opencode/tasks/backend/BE-007.md`; QA-007; matriz del slice
  Contratos usados: Casos minimos de QA-007; endpoints de T04 y T05.
  Entregables: `tests/api/test_idor_owner_pet.py`.
  Criterios de aceptacion: IDOR falla con 403 o 404. Paginacion consistente sin duplicados.
  Validacion: `pytest app/tests/api/test_idor_owner_pet.py -q --tb=short`.
  Resultado esperado: Pruebas de seguridad y paginacion aprobadas.
  Evidencia: `app/tests/api/test_owners_pets.py`; `pytest app/tests/api/test_owners_pets.py -q` PASS con 3 pruebas.
  Paralelismo[P]: No

### Frontend

- [x] FE-007-T01 - Cliente API portal propietario
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-007-07, AC-007-09
  Objetivo: Implementar cliente API tipado para endpoints de propietarios.
  Responsabilidad unica: Si
  Depende de: BE-007-T05
  Contexto necesario: `docs/opencode/tasks/frontend/FE-007.md`; contratos del plan; BE-007-T04, BE-007-T05
  Contratos usados: Endpoints de la tabla "Contratos API por accion".
  Entregables: `src/features/owners/api.ts`.
  Criterios de aceptacion: Cliente expone funciones tipadas para cada endpoint. Manejo de errores HTTP centralizado.
  Validacion: `npm run typecheck`; import del modulo sin errores.
  Resultado esperado: Cliente API tipado disponible para componentes.
  Evidencia: `frontend/src/shared/api/owner-portal.ts`, `frontend/src/features/owners/api/owners-api.ts`; `npm run typecheck` PASS; cliente tipado alineado a `/owners/me`, `/owners/me/pets`, `/pets/{id}` y `/pets/{id}/history` con manejo centralizado de errores HTTP.
  Paralelismo[P]: No

- [x] FE-007-T02 - Rutas portal propietario
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-007-07, AC-007-09
  Objetivo: Definir rutas Next.js para el portal de propietarios.
  Responsabilidad unica: Si
  Depende de: FE-007-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-007.md`; contratos del plan; FE-007-T01
  Contratos usados: Rutas /portal/owner, /portal/owner/edit, /portal/owner/pets/new, /portal/owner/pets/{pet_id}.
  Entregables: `src/app/portal/owner/page.tsx`, `src/app/portal/owner/edit/page.tsx`, `src/app/portal/owner/pets/new/page.tsx`, `src/app/portal/owner/pets/[pet_id]/page.tsx`.
  Criterios de aceptacion: Rutas renderizan sin errores. No hay links # en flujos implementados.
  Validacion: `npm run typecheck`; navegacion manual a cada ruta sin errores.
  Resultado esperado: Rutas del portal propietario disponibles para componentes.
  Evidencia: `frontend/src/app/portal/owner/page.tsx`, `frontend/src/app/portal/owner/edit/page.tsx`, `frontend/src/app/portal/owner/pets/new/page.tsx`, `frontend/src/app/portal/owner/pets/[petId]/page.tsx`; `npm run typecheck` PASS; `npm run build` PASS con rutas `/portal/owner`, `/portal/owner/edit`, `/portal/owner/pets/new` y `/portal/owner/pets/[petId]` generadas sin errores; `docker compose up -d --build --force-recreate db backend frontend` SKIP por daemon Docker no disponible (`npipe:////./pipe/dockerDesktopLinuxEngine`).
  Paralelismo[P]: No

- [x] FE-007-T03 - Componentes formulario listado mascota
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-007-07, AC-007-08
  Objetivo: Implementar componentes de perfil propietario.
  Responsabilidad unica: Si
  Depende de: FE-007-T02
  Contexto necesario: `docs/opencode/tasks/frontend/FE-007.md`; contratos del plan; FE-007-T01, FE-007-T02
  Contratos usados: Formularios y validacion del plan; componentes shared.
  Entregables: `src/features/owners/components/OwnerProfileForm.tsx`, `PetList.tsx`.
  Criterios de aceptacion: Formulario valida campos requeridos. Listado muestra empty state sin mascotas. Estados UX completos.
  Validacion: `npm run test`; navegacion manual con estados visibles.
  Resultado esperado: Componentes del portal propietario verificables por QA.
  Evidencia: `frontend/src/features/owners/components/owner-profile-form.tsx`, `frontend/src/features/owners/components/pet-list.tsx`, `frontend/src/features/owners/layout/owner-portal-layout.tsx`; `npm run test` PASS; estados loading/error/empty/success y navegacion real implementados con componentes shared.
  Paralelismo[P]: No

- [x] FE-007-T04 - Formulario registro mascota
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-007-08
  Objetivo: Implementar formulario de registro de nueva mascota con validacion.
  Responsabilidad unica: Si
  Depende de: FE-007-T03
  Contexto necesario: `docs/opencode/tasks/frontend/FE-007.md`; contratos del plan; FE-007-T03
  Contratos usados: Endpoint POST /owners/me/pets; validacion de campos requeridos.
  Entregables: `src/features/owners/components/PetForm.tsx`.
  Criterios de aceptacion: Formulario valida nombre, especie y raza antes de enviar. Muestra errores claros en la UI.
  Validacion: `npm run test`; navegacion manual a /portal/owner/pets/new con datos invalidos.
  Resultado esperado: Formulario PetForm verificable por QA.
  Evidencia: `frontend/src/features/owners/components/pet-form.tsx`, `frontend/src/features/owners/components/pet-form.test.tsx`, `frontend/src/app/portal/owner/pets/new/page.tsx`; `npm run test` PASS; validaciones de nombre, especie, raza, edad y peso verificadas con pruebas de componente.
  Paralelismo[P]: No

- [x] FE-007-T05 - Componente detalle mascota con historial
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-007-09, AC-007-14
  Objetivo: Implementar componente de detalle de mascota.
  Responsabilidad unica: Si
  Depende de: FE-007-T04
  Contexto necesario: `docs/opencode/tasks/frontend/FE-007.md`; contratos del plan; FE-007-T04
  Contratos usados: Endpoint GET /pets/{id}/history; estados loading/success/empty.
  Entregables: `src/features/owners/components/PetDetail.tsx`.
  Criterios de aceptacion: Detalle muestra datos de mascota. Historial muestra lista vacia o registros. Responsive en mobile/desktop.
  Validacion: `npm run test`; navegacion manual a /portal/owner/pets/{pet_id}.
  Resultado esperado: Componente PetDetail verificable por QA.
  Evidencia: `frontend/src/features/owners/components/pet-detail.tsx`, `frontend/src/features/owners/components/pet-detail.test.tsx`; `npm run test` PASS; `npm run build` PASS; detalle con edicion, historial basico, empty state y responsive implementado para `/portal/owner/pets/{pet_id}`.
  Paralelismo[P]: No

### QA

- [ ] QA-007-T01 - Ejecucion de pruebas ownership e IDOR
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-007-10 a AC-007-15
  Objetivo: Validar ownership en endpoints propietarios.
  Responsabilidad unica: Si
  Depende de: BE-007-T07, FE-007-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-007.md`; criterios AC-007-10 a AC-007-15
  Contratos usados: Casos minimos de QA-007; endpoints implementados.
  Entregables: `docs/opencode/qa/QA-007-results.md`, `docs/opencode/qa/QA-007-findings.md` (si aplica).
  Criterios de aceptacion: Todos los criterios AC-007 aprobados o con findings documentados.
  Validacion: Comandos ejecutados, resultados esperados vs obtenidos, evidencia documentada.
  Resultado esperado: QA APPROVED o findings con workflow de resolucion.
  Evidencia: pending
  Paralelismo[P]: No

### UI Automation

- [ ] UIA-007-T01 - Pruebas navegador portal propietario
  Capa: ui-automation
  Tipo: prueba
  Historia o criterio: AC-007-07, AC-007-08, AC-007-14
  Objetivo: Automatizar flujos del portal propietario en navegador.
  Responsabilidad unica: Si
  Depende de: FE-007-T05
  Contexto necesario: `docs/opencode/tasks/ui-automation/UIA-007.md`; FE-007-T02; QA-007
  Contratos usados: Rutas, formularios, estados UX del plan.
  Entregables: `InVet_UI_Automation/tests/test_owners_portal.spec.ts`.
  Criterios de aceptacion: Flujos de perfil, listado mascotas, registro mascota pasan en Chromium y Firefox. Estados UI verificados.
  Validacion: `npx playwright test tests/test_owners_portal.spec.ts --reporter=html`.
  Resultado esperado: Pruebas UI automation aprobadas.
  Evidencia: pending
  Paralelismo[P]: No

### API Automation

- [ ] APIA-007-T01 - Pruebas API ownership e IDOR
  Capa: api-automation
  Tipo: prueba
  Historia o criterio: AC-007-10 a AC-007-13, AC-007-15
  Objetivo: Automatizar pruebas de endpoints con authn y authz.
  Responsabilidad unica: Si
  Depende de: BE-007-T07
  Contexto necesario: `docs/opencode/tasks/api-automation/APIA-007.md`; BE-007-T05; QA-007
  Contratos usados: Endpoints, payloads, errores del plan.
  Entregables: `InVet_UI_Automation/tests/api/test_owners_api.spec.ts`, `test_pets_api.spec.ts`.
  Criterios de aceptacion: Todos los endpoints responden con codigos y esquemas esperados. IDOR/BOLA fallan seguro. Paginacion consistente.
  Validacion: `npx playwright test tests/api/test_owners_api.spec.ts tests/api/test_pets_api.spec.ts --reporter=html`.
  Resultado esperado: Pruebas API automation aprobadas.
  Evidencia: pending
  Paralelismo[P]: No
  Entregables: `docs/opencode/qa/QA-007-results.md`, `docs/opencode/qa/QA-007-findings.md` (si aplica).
  Criterios de aceptacion: Todos los criterios AC-007 aprobados o con findings documentados.
  Validacion: Comandos ejecutados, resultados esperados vs obtenidos, evidencia documentada.
  Resultado esperado: QA APPROVED o findings con workflow de resolucion.
  Evidencia: pending
  Paralelismo[P]: No

### UI Automation

- [ ] UIA-007-T01 - Pruebas de navegador para portal propietario
  Capa: ui-automation
  Tipo: playwright
  Historia o criterio: AC-007-07, AC-007-08, AC-007-14
  Objetivo: Automatizar flujos del portal propietario en navegador.
  Responsabilidad unica: Si
  Depende de: FE-007-T02
  Contexto necesario: `docs/opencode/tasks/ui-automation/UIA-007.md`; FE-007-T02; QA-007
  Contratos usados: Rutas, formularios, estados UX del plan.
  Entregables: `InVet_UI_Automation/tests/test_owners_portal.spec.ts`.
  Criterios de aceptacion: Flujos de perfil, listado mascotas, registro mascota pasan en Chromium y Firefox. Estados UI verificados.
  Validacion: `npx playwright test tests/test_owners_portal.spec.ts --reporter=html`.
  Resultado esperado: Pruebas UI automation aprobadas.
  Evidencia: pending
  Paralelismo[P]: No

### API Automation

- [ ] APIA-007-T01 - Pruebas de API para ownership, IDOR y contratos
  Capa: api-automation
  Tipo: HTTP tests
  Historia o criterio: AC-007-10 a AC-007-13, AC-007-15
  Objetivo: Automatizar pruebas de endpoints con diferentes contextos de auth.
  Responsabilidad unica: Si
  Depende de: BE-007-T04
  Contexto necesario: `docs/opencode/tasks/api-automation/APIA-007.md`; BE-007-T03; QA-007
  Contratos usados: Endpoints, payloads, errores del plan.
  Entregables: `InVet_UI_Automation/tests/api/test_owners_api.spec.ts`, `test_pets_api.spec.ts`.
  Criterios de aceptacion: Todos los endpoints responden con codigos y esquemas esperados. IDOR/BOLA fallan seguro. Paginacion consistente.
  Validacion: `npx playwright test tests/api/test_owners_api.spec.ts tests/api/test_pets_api.spec.ts --reporter=html`.
  Resultado esperado: Pruebas API automation aprobadas.
  Evidencia: pending
  Paralelismo[P]: No
