---
schema_version: 3
slice: "008"
canonical_plan: BE-008
status: IN_PROGRESS
encoding: UTF-8
last_updated: 2026-08-16
---

# BE-008 Plan — Solicitud y gestión de citas / Appointment scheduling and management

## Estado actual

| Componente | Archivo | Estado |
|-----------|---------|--------|
| Modelo dominio | `backend/app/domain/entities/appointment.py` | ✅ EXISTS |
| Protocolo repositorio | `backend/app/domain/repositories/appointment_repository.py` | ✅ EXISTS |
| ORM SQLAlchemy | `backend/app/infrastructure/database/models/appointment.py` | ✅ EXISTS |
| Repo implementación | `backend/app/infrastructure/database/repositories/appointment_repository_impl.py` | ✅ EXISTS |
| Casos de uso | `backend/app/application/use_cases/appointment_use_cases.py` | ✅ EXISTS (~350 líneas, 7 use cases) |
| Esquemas API | `backend/app/api/v1/schemas/appointment_schemas.py` | ✅ EXISTS (~160 líneas, 6 schemas) |
| Router FastAPI | `backend/app/api/v1/routers/appointment_router.py` | ✅ EXISTS (todos endpoints registrados) |
| Migración Alembic | `backend/alembic/versions/a008_appointments.py` | ✅ EXISTING (corregida en 2026-08-16) |
| Pruebas unitarias | `backend/app/tests/test_appointment_use_cases.py` | ✅ CREATED (2026-08-16) |
| Pruebas API | `backend/app/tests/api/test_appointments_api.py` | ✅ CREATED (2026-08-16) |

## Implementación completa

Todos los componentes del backend para BE-008 están implementados:

### Endpoints expuestos (`/api/v1/appointments`)

| Acción | Método | Ruta | Auth | Response Code |
|--------|--------|------|------|---------------|
| Solicitar cita | POST | `/appointments` | Bearer | 201 Created |
| Listar citas | GET | `/appointments?my_appointments=1&page=&status=&veterinarian_id=` | Bearer | 200 OK |
| Obtener detalle | GET | `/appointments/{id}` | Bearer | 200/404 |
| Actualizar cita | PUT | `/appointments/{id}` | Bearer | 200/404 |
| Transición estado | POST | `/appointments/{id}/status` | Bearer | 200/422 |
| Cancelar cita | DELETE | `/appointments/{id}` | Bearer | 204 No Content |
| Disponibilidad | GET | `/appointments/availability?date=&vet_id=&clinic_id=` | Bearer | 200 OK |

### Transiciones de estado validadas

```
pending → approved, cancelled, rescheduled
approved → confirmed, cancelled, rescheduled
confirmed → completed, no_show, cancelled
rescheduled → pending, cancelled
completed/no_show/cancelled → TERMINAL (sin transiciones)
```

### Pruebas unitarias incluidas

- `TestCreateAppointmentUseCase`: 4 tests (éxito, tipo inválido, duración corta, conflicto vet)
- `TestTransitionAppointmentStatusUseCase`: 7 tests (todas transiciones + casos de error)
- `TestListAppointmentsByOwnerUseCase`: 2 tests (listado paginado, vacío)
- `TestGetAvailabilityUseCase`: 1 test (slots con citas ocupadas)
- `TestTenantIsolation`: 1 test (aislamiento por clínica)
- **Total: 15+ casos de prueba unitaria**

### Pruebas API incluidas

- Unauthenticated access → 401/403
- Invalid appointment type → 422
- Missing required fields → 422
- Past date rejected → 422/400
- Duration validation (min/max) → 422/400

---

## Objetivo del slice

Crear el flujo vertical completo de solicitud, gestión y seguimiento de citas médicas veterinarias dentro del MVP: un propietario puede solicitar una cita desde su perfil, la clínica puede aprobar/confirmar/reprogramar/cancelar/marcar no-show/completar citas, y QA valida el end-to-end con coverage de permisos, estados inválidos e IDOR/BOLA.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Solicitud y gestión de citas |
| Descripcion | Crear/solicitar/confirmar/cancelar/reprogramar/marcar no-show/completar citas dentro del MVP, con disponibilidad basica y control de estados. |
| Entregables backend | Modelo `Appointment`, enums de estado, repositorio, endpoints CRUD + transicion de estados bajo `/api/v1/appointments` implementados en `backend/app/api/v1/routers/appointment_router.py`, schemas Pydantic en `backend/app/api/v1/schemas/appointment_schemas.py`, migracion Alembic, pruebas pytest/HTTPX. |
| Entregables frontend | Flujo de solicitud desde perfil del propietario, vistas de agenda de propietario y agenda clinica en `frontend/src/app/portal/owner/appointments` y `frontend/src/app/clinic/appointments`, componentes de cambio de estado, feedback visual (loading, submitting, error, success, empty). |
| Criterios QA principales | Transiciones validas pasan; transiciones invalidas fallan con error claro; disponibilidad se respeta; permisos por rol (propietario/clinica/veterinario) funcionan; IDOR/BOLA falla de forma segura; estados UI consistentes. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Modelo `Appointment` con campos minimos:
  - `id`, `owner_id`, `pet_id`, `veterinarian_id` (nullable), `clinic_id`, `branch_id`, `appointment_type` (consulta_general/vacunacion/control/reemergencia), `status` (pending/approved/confirmed/completed/cancelled/no_show/rescheduled), `scheduled_start`, `scheduled_end`, `duration_minutes` (default 30), `reason` (textarea opcional), `notes` (texto libre clinico), `created_by` (FK a user_id), `updated_at`.
  - Enum de estado con transiciones validas documentadas.
- Transiciones de estado validadas en backend:
  - `pending` → `approved`, `rejected`, `rescheduled`, `cancelled`
  - `approved` → `confirmed`, `cancelled`, `rescheduled`
  - `confirmed` → `completed`, `no_show`, `cancelled`
  - `rescheduled` → `pending` (nueva cita por reschedule) o `cancelled`
  - `completed` / `no_show` / `cancelled` son estados terminales.
- Disponibilidad basica: endpoint que devuelve slots disponibles por fecha/veterinario/sucursal (sin integracion con calendario externo).
- Endpoints protegidos con Bearer token:
  - Propietario: solicitar, listar sus citas, cancelar solo si status permite.
  - Clinica/Veterinario: aprobar, confirmar, reprogramar, marcar no-show, completar citas asignadas o de su sucursal.
  - IDOR/BOLA: validacion de ownership y tenant/branch en cada endpoint.
- Migraciones Alembic para tabla `appointments` y posibles indices compuestos `(clinic_id, branch_id, scheduled_start)`.
- Paginacion en listados (`?page=1&page_size=20`).
- Pruebas pytest/HTTPX: happy path de transicion, negative path de transicion invalida, 401 sin token, 403 sin permiso, IDOR con IDs cruzados.

## Fuera de alcance

- Notificaciones por correo o push (slice 013).
- Integracion con calendario externo (Google Calendar, Outlook).
- Recordatorios automaticos (slice 010).
- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica y timbrado fiscal.
- Recomendaciones medicas automaticas.
- Analitica avanzada o dashboards avanzados (slice 015).
- Reservas recurrentes (series de citas).
- Waitlist / cola de espera para citas canceladas.

## Suposiciones

- La entidad `Owner` del slice BE-007 existe y se vincula a `users` con campo `user_id`.
- La entidad `Pet` del slice BE-007 existe y tiene FK a `owner_id`.
- Los roles de usuario (`propietario`, `clinica`, `veterinario`) ya existen definidos en slices previos (BE-002, BE-006).
- La tabla `clinics` y `branches` existe con campos `id`, `name`, `tenant_id`.
- No se requiere aprobacion del usuario sobre los datos de `Appointment` para este MVP.
- Si el supuesto sobre roles o estructuras existentes cambia, detener planificacion y preguntar.

## Revision de gaps

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, `BE-008.md`, `FE-008.md`, `QA-008.md`.
- Gap: No se especifica si el endpoint de disponibilidad debe devolver slots por veterinario individual o solo por sucursal.
- Decision: Disponibilidad basica devuelve slots por `vet_id` (nullable) Y por `branch_id`. Si `vet_id` es null, se usan todos los vets de la sucursal para esa fecha.
- Impacto en tareas: BE debe crear endpoint GET `/appointments/availability` que acepta `?date=YYYY-MM-DD&vet_id=<optional>&clinic_id=&branch_id=` y responde lista de slots libres basado en citas existentes.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Appointment | BE-008, slice_task_context | Modelo principal con campos completos y enum status | Pytest + HTTPX |
| Status transitions | BE-008, reglas de negocio | Validar transicion permitida en backend | Prueba de cada transicion valida/invalida |
| Disponibilidad | BE-008, gap decision | Endpoint de slots disponibles por fecha/vet/sucursal | GET con query params, response lista de slots |
| Ownership/BOLA | BE-007, QA-008 | Validar que solo owner/vet autor operen su cita | IDOR tests cruzados |
| Paginacion | BE-008, reglas existentes | Listados paginados en /appointments | Verificar query params page/page_size |
| appointment_type | BE-008, dominio | Enum: consulta_general, vacunacion, control, reemergencia | Validacion en schema Pydantic |
| Duration default | BE-008 | Default 30 minutos, configurable entre 15 y 120 | Schema validation |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-008.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-008.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-008.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| Carryovers governance | `docs/opencode/references/carryovers_governance.md` | Reglas de carryovers (verificar no hay carryovers pendientes) | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-008-01 | BE-008, slice_task_context | Owner solicita cita valida | BE-008-T03 | POST /api/v1/appointments responde 201 con datos de cita creada | Response JSON con status=pending, scheduled_start en el futuro | OPEN |
| AC-008-02 | BE-008, slice_task_context | Owner lista sus citas con paginacion | BE-008-T05 | GET /api/v1/appointments?owner_id=me&page=1 responde 200 con paginacion | JSON con items y meta.total | OPEN |
| AC-008-03 | BE-008, reglas negocio | Transicion pending→approved valida pasa | BE-008-T06 | PUT /api/v1/appointments/{id}/status con action=approve responde 200 status=approved | Status actualizado en response | OPEN |
| AC-008-04 | BE-008, reglas negocio | Transicion invalida (completed→approved) falla | BE-008-T06 | PUT /api/v1/appointments/{id}/status con action=approve desde completed responde 422 | Error claro "invalid transition" | OPEN |
| AC-008-05 | BE-008, reglas negocio | Clinica aprueba cita de su sucursal | BE-008-T06 | PUT con token clinica en cita de otra sucursal responde 403 o 404 | Status 403/404 sin datos expuestos | OPEN |
| AC-008-06 | BE-008, QA-008 | Transicion confirmed→completed pasa para veterinario asignado | BE-008-T06 | PUT con action=complete responde 200 status=completed | Response con status=completed, updated_at actualizado | OPEN |
| AC-008-07 | BE-008, QA-008 | Transicion confirmed→no_show pasa para veterinario | BE-008-T06 | PUT con action=no_show responde 200 status=no_show | Response con status=no_show | OPEN |
| AC-008-08 | BE-008, QA-008 | Owner cancela cita valida (antes de confirmed) | BE-008-T07 | DELETE o PUT action=cancel responde 200 status=cancelled | Response con status=cancelled | OPEN |
| AC-008-09 | BE-008, reglas negocio | Clinica reprograma cita | BE-008-T06 | PUT /api/v1/appointments/{id}/reschedule responde 200 con nuevos horarios | Response con scheduled_start/scheduled_end nuevos | OPEN |
| AC-008-10 | BE-008, FE-008 | Endpoint de disponibilidad devuelve slots | BE-008-T04 | GET /api/v1/appointments/availability?date=2026-09-01 responde 200 con lista de slots | JSON con slots libres y ocupados | OPEN |
| AC-008-11 | FE-008, QA-008 | Owner solicita cita desde perfil con feedback visual | FE-008-T02 | Ruta /portal/owner/appointments/new renderiza formulario y envia POST | UI muestra success/error/empty segun caso | OPEN |
| AC-008-12 | FE-008, QA-008 | Agenda del propietario muestra citas pendientes/activas/completadas | FE-008-T03 | Ruta /portal/owner/appointments agenda filtra por estado y muestra timeline | UI con estados loading/success/empty/error | OPEN |
| AC-008-13 | FE-008, QA-008 | Agenda de clinica permite gestionar citas (aprobar/confirmar/reprogramar/cancelar/no-show/completar) | FE-008-T04 | Ruta /clinic/appointments agenda con acciones por estado | UI con botones segun status y permisos | OPEN |
| AC-008-14 | QA-008 | Transiciones invalidas son rechazadas con error legible | QA-008-T01 | Intentar transicion prohibida via endpoint responde 422 | Response con mensaje de validacion claro | OPEN |
| AC-008-15 | QA-008 | Usuario no autenticado recibe 401 en endpoints protegidos | QA-008-T01 | GET /api/v1/appointments sin token responde 401 | Status 401 | OPEN |
| AC-008-16 | QA-008, BE-007 | IDOR: propietario accede a cita de otro propietario falla seguro | QA-008-T01 | GET /api/v1/appointments/{other_id} con token de otro owner responde 403/404 | Status 403/404 sin datos expuestos | OPEN |
| AC-008-17 | QA-008 | Input invalido (fecha en pasado) produce error claro | QA-008-T01 | POST con scheduled_start en pasado responde 422 | Response con mensaje de validacion legible | OPEN |
| AC-008-18 | QA-008, FE-008 | UI muestra loading/error/empty/success correctamente | QA-008-T01 | Navegar a vistas de cita con y sin datos | Estados visibles en UI | OPEN |
| AC-008-19 | QA-008 | Listados aplican paginacion consistentemente | QA-008-T01 | GET /api/v1/appointments?page=2&page_size=5 responde con max 5 items | JSON con meta.total y items.count <= 5 | OPEN |
| AC-008-20 | QA-008, BE-008 | Migracion Alembic crea tabla appointments sin perder data | QA-008-T01 | Migration genera tabla con columnas correctas e indices | Migration reversible y aplica limpia | OPEN |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Solicitar cita | POST | `/appointments` | Bearer (propietario) | `{pet_id, veterinarian_id?, appointment_type, scheduled_start, scheduled_end, reason}` | 201 `{id, status=pending, ...}` | 400, 403, 409, 422 |
| Listar citas propias | GET | `/appointments/me` | Bearer (propietario) | `?page=1&page_size=20&status=pending` | 200 `{items: [...], meta: {...}}` | 401, 404 |
| Listar clinica citas | GET | `/appointments/clinic` | Bearer (clinica/vet) | `?page=1&page_size=20&status=pending&branch_id=` | 200 `{items: [...], meta: {...}}` | 401, 403, 404 |
| Obtener cita | GET | `/appointments/{id}` | Bearer (propietario/clinica) | — | 200 `{id, status, scheduled_start, ...}` | 401, 403, 404 |
| Cambiar estado | PUT | `/appointments/{id}/status` | Bearer (rol adecuado) | `{action: approve|confirm|complete|cancel|no_show|reschedule, new_start?, new_end?}` | 200 `{id, status, ...}` | 400, 403, 422 |
| Reprogramar cita | PUT | `/appointments/{id}/reschedule` | Bearer (clinica/vet) | `{new_start, new_end, reason?}` | 200 `{id, scheduled_start, ...}` | 400, 403, 409, 422 |
| Cancelar cita | PUT/DELETE | `/appointments/{id}/cancel` | Bearer (propietario/clinica) | — | 200 `{status=cancelled}` | 401, 403, 422 |
| Disponibilidad | GET | `/appointments/availability` | Bearer (cualquier rol) | `?date=YYYY-MM-DD&vet_id=&clinic_id=&branch_id=` | 200 `{slots: [{start, end, available}]}` | 401, 404 |

## Contrato de implementacion frontend

### Rutas y acceso

- `/portal/owner/appointments/new` — Formulario de solicitud de nueva cita desde perfil del propietario.
- `/portal/owner/appointments` — Agenda del propietario con filtro por estado (todas/pendientes/activas/completadas/canceladas).
- `/portal/owner/appointments/{id}` — Detalle de cita individual con acciones permitidas segun status.
- `/clinic/appointments` — Agenda clinica global con lista de citas y acciones masivas (aprobar/confirmar/reprogramar/cancelar/no-show/completar).
- `/clinic/appointments/{id}` — Panel de gestion detallada de una cita desde la perspectiva clinica.

### Flujos y estados UX

**Solicitud de cita:**
1. Owner navega a `/portal/owner/appointments/new`.
2. Selecciona mascota (de su lista BE-007), tipo de cita, fecha/hora disponible (desde availability API).
3. Agrega motivo opcional.
4. Estado: loading → submitting → success / error / empty (si no hay mascota registrada).

**Agenda del propietario:**
1. Listado con tabs por estado: pendientes/activas/completadas/canceladas.
2. Estado: loading → success / empty (sin citas registradas) / error.
3. Cada item muestra: fecha/hora, tipo de cita, veterinario asignado, status con color, acciones permitidas.

**Agenda clinica:**
1. Vista tipo calendario/lista con filtros por estado/fecha/veterinario/sucursal.
2. Estado: loading → success / empty (sin citas en el periodo) / error.
3. Cada cita muestra acciones segun status actual: aprobar, confirmar, reprogramar, cancelar, no-show, completar.

**Estados UX requeridos por componente:**
- `loading`: spinner en listados y formularios al obtener datos.
- `submitting`: botón disabled con spinner al enviar formulario de solicitud.
- `error`: banner rojo con mensaje de error legible (no interno).
- `empty`: estado vacio con CTA de "Solicitar primera cita" cuando aplica.
- `success`: toast/banner verde de confirmacion tras operacion exitosa.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Solicitar cita | POST `/appointments` | Bearer (propietario) | `{pet_id, vet_id?, type, start, end, reason?}` | 201 `{id, status=pending}` | 400, 403, 409, 422 | Propietario |
| Obtener slots disponibles | GET `/appointments/availability` | Bearer (cualquier rol) | `?date=&vet_id=&branch_id=` | 200 `{slots: [...]}` | 401, 404 | Cualquiera |
| Listar citas propias | GET `/appointments/me` | Bearer (propietario) | `?page=&status=` | 200 `{items: [...], meta: {...}}` | 401, 404 | Propietario |
| Listar citas clinica | GET `/appointments/clinic` | Bearer (clinica/vet) | `?page=&status=&branch_id=&vet_id=` | 200 `{items: [...], meta: {...}}` | 401, 403 | Clinica/Veterinario |
| Obtener detalle cita | GET `/appointments/{id}` | Bearer (propietario/clinica) | — | 200 `{...cita completa}` | 401, 403, 404 | Propietario/Clinica |
| Aprobar cita | PUT `/appointments/{id}/status` | Bearer (clinica/vet) | `{action: approved}` | 200 `{status=approved}` | 400, 403, 422 | Clinica/Veterinario |
| Confirmar cita | PUT `/appointments/{id}/status` | Bearer (clinica/vet) | `{action: confirmed}` | 200 `{status=confirmed}` | 400, 403, 422 | Clinica/Veterinario |
| Completar consulta | PUT `/appointments/{id}/status` | Bearer (vet asignado) | `{action: completed}` | 200 `{status=completed}` | 400, 403, 422 | Veterinario asignado |
| Marcar no-show | PUT `/appointments/{id}/status` | Bearer (vet asignado/clinica) | `{action: no_show}` | 200 `{status=no_show}` | 400, 403, 422 | Veterinario/Clinica |
| Reprogramar cita | PUT `/appointments/{id}/reschedule` | Bearer (clinica/vet) | `{new_start, new_end}` | 200 `{scheduled_start, scheduled_end}` | 400, 403, 409, 422 | Clinica/Veterinario |
| Cancelar cita | PUT `/appointments/{id}/cancel` | Bearer (propietario/clinica) | — | 200 `{status=cancelled}` | 401, 403, 422 | Propietario/Clinica |

### Formularios y validacion

**Formulario de solicitud de cita:**
- `pet_id`: requerido, entero > 0 (mascota debe pertenecer al owner autenticado).
- `veterinarian_id`: opcional (si null se asigna por disponibilidad clinica).
- `appointment_type`: requerido, enum de opciones.
- `scheduled_start`: requerido, fecha/hora en el futuro (no pasado).
- `scheduled_end`: requerido, debe ser > scheduled_start y diferencia max 120 min.
- `reason`: opcional, string max 500 chars.

**Formulario de reprogramacion (clinica):**
- `new_start`: requerido, fecha/hora en el futuro.
- `new_end`: requerido, > new_start y <= new_start + 120 min.
- `reason`: opcional, texto libre.

### Arquitectura de componentes

**Frontend features:**
- Feature module en `src/features/appointments` con:
  - `AppointmentForm` — formulario de solicitud desde perfil propietario.
  - `OwnerAgenda` — agenda del propietario con tabs por estado.
  - `ClinicAgenda` — vista clinica con acciones por status.
  - `AppointmentDetail` — detalle individual de cita con timeline de estados.
  - `AvailabilityCalendar` — componente de disponibilidad (mini-calendario + slots).
  - `StatusBadge` — badge de estado con colores semanticos.
  - `ActionMenu` — menu contextual de acciones segun status/permisos.

**Componentes compartidos reutilizados:**
- `src/shared/ui`: Button, Input, Select, DatePicker, Table, EmptyState, LoadingSpinner, ErrorBanner, SuccessToast.
- `src/shared/api`: cliente API tipado con methods para `/appointments`.

### Responsive y accesibilidad

- **Mobile-first**: formulario en columna completa; agenda clinica en vista lista vertical en mobile, grid/columnas en desktop.
- **Calendario/availability**: scroll horizontal de slots en mobile; grid visible en desktop.
- **Accesibilidad minima**: labels asociados a inputs, aria-labels en botones iconicos, contraste WCAG AA, orden tabulacion logica.

### Estrategia de pruebas frontend

- Pruebas unitarias de `AppointmentForm` (validacion de campos requeridos, rango de horas).
- Pruebas unitarias de `StatusBadge` (colores correctos por estado).
- Pruebas de integracion de flujo completo con mocks: solicitar cita → listar en agenda → reprogramar.
- Typecheck (`tsc`) y lint limpios sin errores nuevos del slice.

## Estrategia de automatizacion UI

- Tests E2E con Playwright (dentro de `InVet_UI_Automation/tests/`):
  - `test_008_appointment_request.ts`: propietario autentica, navega a nueva cita, completa formulario, verifica creacion exitosa.
  - `test_008_owner_agenda.ts`: propietario lista citas filtrando por estado; UI muestra tabs correctos.
  - `test_008_clinic_approval_flow.ts`: clinica autentica, aprueba cita desde agenda, verifica status change en UI.
  - `test_008_reschedule.ts`: clinica reprograma cita, propietario ve cambio en su agenda.
  - `test_008_cancel_by_owner.ts`: propietario cancela cita valida; status actualizado en ambas agendas.

## Estrategia de automatizacion API

- Pruebas contractuales con HTTPX dentro de `backend/app/tests/`:
  - `test_appointments_create.py`: happy path de creacion (201).
  - `test_appointments_status_transitions.py`: todas las transiciones validas (200) e invalidas (422).
  - `test_appointments_availability.py`: slots disponibles sin solapamiento.
  - `test_appointments_idor.py`: acceso cruzado con tokens de diferentes owners/clinicas.
  - `test_appointments_auth.py`: 401 sin token, 403 sin rol adecuado.
  - `test_appointments_pagination.py`: paginacion consistente (page/page_size).

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | Estado del servicio |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/ -q -k appointment` | Cuando el criterio requiere PostgreSQL real | Conteo de tests PASS |
| Validacion plan | `python backend/scripts/validate_slice_plan.py BE-008 --stage plan` | Preflight de implementacion | Salida valida o errores fixeados |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreados |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida 0 |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-008-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task QA-008` |
| `docs/opencode/qa/QA-008-findings.md` | QA | Implementadores, QA | Si hay FAIL, BLOCKED o gaps unitarios |
| `docs/opencode/reviews/BE-008-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice BE-008` |
| `docs/opencode/reviews/BE-008-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-008-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-008-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-008` |
| `docs/opencode/slices/BE-008-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| AC-008-01: Owner solicita cita valida | Creacion sin ownership | integration | `tests/api/test_appointments_create.py` | PENDING |
| AC-008-03: Transicion pending→approved pasa | Estado invalido | integration | `tests/api/test_status_transitions.py` | PENDING |
| AC-008-04: Transicion invalida rechazada | Bypass de negocio | integration | `tests/api/test_invalid_transitions.py` | PENDING |
| AC-008-06: confirmed→completed para vet asignado | Flujo completado erroneo | integration | `tests/api/test_status_transitions.py` | PENDING |
| AC-008-07: confirmed→no_show pasa | Marcacion erronia | integration | `tests/api/test_status_transitions.py` | PENDING |
| AC-008-08: Owner cancela cita valida | Cancelacion indebida | integration | `tests/api/test_appointments_cancel.py` | PENDING |
| AC-008-10: Disponibilidad devuelve slots correctos | Slots solapados | integration | `tests/api/test_appointments_availability.py` | PENDING |
| AC-008-14: Transiciones invalidas error legible | UX defectuoso | unit | Backend validation tests | PENDING |
| AC-008-15: 401 sin token | Acceso no autorizado | security | `tests/api/test_appointments_auth.py` | PENDING |
| AC-008-16: IDOR propietario cruzado | BOLA critico | security | `tests/api/test_appointments_idor.py` | PENDING |
| AC-008-17: Input fecha pasado 422 | Validacion bypass | unit | Schema validation tests | PENDING |
| AC-008-18: Estados UI consistentes | UX defectuoso | frontend | Jest component tests | PENDING |
| AC-008-19: Paginacion consistente | Datos truncados | integration | `tests/api/test_appointments_pagination.py` | PENDING |
| AC-008-20: Migracion limpia | Data loss | infrastructure | Alembic upgrade/downgrade test | PENDING |

## Riesgos de seguridad/IDOR/BOLA

- **BOLA en citas**: Si el endpoint GET/PUT/DELETE `/appointments/{id}` no valida que `appointment.owner_id` coincida con el `user_id` del token, un propietario puede ver/modificar citas de otro. Mitigacion: validacion de ownership obligatoria en cada operacion.
- **IDOR en clinica**: Un clinico/veterinario de una sucursal puede acceder a citas de otra sucursal si no se valida `branch_id` o `clinic_id` contra el tenant/rol del token. Mitigacion: validar que el usuario pertenezca a la misma sucursal/clinica que la cita.
- **State bypass**: Un propietario podria intentar transiciones reservadas para clinica (e.g., aprobar una cita) si no se valida rol en el endpoint `/appointments/{id}/status`. Mitigacion: validar `rol` en cada accion de estado.
- **Slot availability race condition**: Dos propietarios pueden reservar el mismo slot simultaneamente. El endpoint debe usar transaccion DB con lock o validacion atomic.
- **Exposicion de datos personales**: Las respuestas de citas no deben exponer datos sensibles del propietario (email, telefono) salvo permiso explicito por rol.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [ ] Rutas backend y prefijos API definidos.
- [ ] Contratos request/response documentados.
- [ ] Permisos y ownership definidos por endpoint o accion.
- [ ] Estados 400, 401, 403, 404, 422 y validaciones definidos.
- [ ] Modelos, migraciones o cambios de persistencia identificados.
- [ ] Casos QA positivos, negativos y de permisos trazados a criterios.
- [ ] Checks esperados definidos para backend y frontend.
- [ ] Docker definido o skip justificado.
- [ ] Reportes y findings esperados identificados.
- [ ] UTF-8 declarado para planes, reportes, comentarios y outcomes.
- [ ] Documentacion a actualizar identificada.
- [ ] Artefactos US-008, UIA-008, APIA-008 creados en `docs/opencode/tasks/`.

## Checklist de tareas

Reglas:
- Cada tarea tiene una sola responsabilidad verificable.
- Cada tarea apunta a una sola capa y a un tipo de trabajo.
- Si mezcla contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion, dividir en tareas `TNN` consecutivas.
- `Responsabilidad unica` debe ser `Si`.
- `Objetivo` debe ser corto, sin objetivos compuestos.
- `Contexto necesario` debe listar archivos o decisiones que el implementador debe leer.
- `Contratos usados` debe mapear la tarea con endpoints, criterios, referencias o reportes.
- Titulo, descripcion, entregables y criterios de aceptacion deben alinearse con `Brief operativo del slice`.
- Si el brief, la matriz y las tasks BE/FE/QA discrepan, registrar la decision en `Revision de gaps`.

### Dependencias previas

- **BE-007 (Propietarios y mascotas) debe estar cerrado** antes de iniciar BE-008. El modelo `Appointment` requiere entidades `Owner`, `Pet`, `Clinic`, `Branch`, `Veterinarian` existentes y estables.
- Si QA-007 no muestra decision `APPROVED`, bloquear inicio de BE-008.

### Backend

- [x] BE-008-T01 - Definir modelo Appointment con campos minimos
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-008-01, AC-008-20
  Objetivo: Definir el modelo de dominio Appointment con sus campos obligatorios.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; modelos Owner/Pet de BE-007; slice_task_context
  Contratos usados: AC-008-01, AC-008-20
  Entregables: `app/domain/models/appointment.py`.
  Criterios de aceptacion: Modelo con todos los campos definidos.
  Validacion: `python -c "from app.domain.models.appointment import Appointment; print('OK')"` + revisar modelo.
  Resultado esperado: Modelo de dominio disponible para implementacion.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T01a - Definir enum de estados de cita
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-008-01, AC-008-20
  Objetivo: Definir el enum AppointmentStatus con todas sus transiciones validas.
  Responsabilidad unica: Si
  Depende de: BE-008-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; matriz de transiciones del plan
  Contratos usados: AC-008-01, AC-008-20
  Entregables: Enum `AppointmentStatus` en `app/domain/models/appointment.py`.
  Criterios de aceptacion: Enum con valores pending/approved/confirmed/completed/cancelled/no_show/rescheduled.
  Validacion: Revisar enum y sus metodos de validacion de transicion.
  Resultado esperado: Enum de estados disponible para modelo y casos de uso.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T02 - Definir reglas validacion del modelo
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-008-01, AC-008-20
  Objetivo: Agregar reglas de validacion en Pydantic schemas para Appointment.
  Responsabilidad unica: Si
  Depende de: BE-008-T01a
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; modelo de dominio creado en T01
  Contratos usados: AC-008-01, AC-008-20
  Entregables: Pydantic schemas con validacion de campos.
  Criterios de aceptacion: Validacion de campos requeridos. Validacion de rango fechas. Validacion de duracion entre 15 y 120 min.
  Validacion: `python -c "from app.domain.models.appointment import AppointmentCreateSchema; print('OK')"` + revisar schemas.
  Resultado esperado: Schemas validados disponibles para implementacion.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T03 - Crear migracion Alembic para tabla de citas
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-008-20
  Objetivo: Generar la migration Alembic que cree la tabla appointments con indices.
  Responsabilidad unica: Si
  Depende de: BE-008-T01
  Contexto necesario: `app/infrastructure/db.py`; migration template de BE-007
  Contratos usados: AC-008-20
  Entregables: Migracion Alembic (`a*_appointments.py`).
  Criterios de aceptacion: Migracion crea tabla con columnas e indices correctos. Migration reversible (downgrade limpio). Sin loss de data preexistente.
  Validacion: `alembic upgrade head`; migracion down+upgrade sin errores.
  Resultado esperado: Persistencia disponible y migracion verificable.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T04 - Implementar repositorio de citas
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-008-20
  Objetivo: Crear el repositorio AppointmentRepository con capacidad CRUD.
  Responsabilidad unica: Si
  Depende de: BE-008-T03
  Contexto necesario: `app/infrastructure/repositories/`; pattern de BE-007
  Contratos usados: AC-008-20
  Entregables: `app/infrastructure/repositories/appointment_repository_impl.py`.
  Criterios de aceptacion: Repositorio implementa CRUD completo. Busqueda por filtros funciona. Paginacion incluida.
  Validacion: `python -c "from app.infrastructure.repositories.appointment_repository_impl import AppointmentRepository; print('OK')"` + revisar codigo.
  Resultado esperado: Repositorio disponible para casos de uso.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T05 - Implementar caso de uso crear cita
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-008-01, AC-008-17
  Objetivo: Crear el caso de uso CreateAppointmentUseCase con validacion de ownership.
  Responsabilidad unica: Si
  Depende de: BE-008-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; modelo de dominio
  Contratos usados: AC-008-01, AC-008-17
  Entregables: `app/application/use_cases/appointment_create.py`.
  Criterios de aceptacion: Caso de uso valida ownership del owner. Valida fecha en futuro. Retorna error si slot ocupado.
  Validacion: `pytest -q app/application/test_appointment_create.py` → PASS.
  Resultado esperado: Caso de uso disponible para endpoint.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T06 - Exponer endpoint POST de solicitud de cita
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-01, AC-008-02
  Objetivo: Exponer el endpoint POST para creacion de citas que responde 201.
  Responsabilidad unica: Si
  Depende de: BE-008-T05
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; pattern router de BE-007
  Contratos usados: AC-008-01, AC-008-02
  Entregables: Router FastAPI con endpoint POST.
  Criterios de aceptacion: Endpoint responde 201 con status=pending. Response JSON completo con datos de cita.
  Validacion: `pytest -q -k test_appointments_create` → PASS.
  Resultado esperado: Endpoint de creacion disponible para frontend.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T07 - Exponer endpoint GET de disponibilidad
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-10
  Objetivo: Exponer el endpoint GET para consultar slots disponibles que devuelve lista de fechas.
  Responsabilidad unica: Si
  Depende de: BE-008-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; gap decision (slots por vet + branch)
  Contratos usados: AC-008-10
  Entregables: Endpoint availability con query params date/vet_id/branch_id.
  Criterios de aceptacion: Responde lista de slots basados en horario clinica menos citas existentes. Filtros funcionan. Sin solapamiento.
  Validacion: HTTPX test + consulta manual GET con distintos filtros.
  Resultado esperado: Disponibilidad disponible para frontend scheduling.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T08 - Exponer endpoint GET de listado propietario
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-02, AC-008-19
  Objetivo: Exponer el endpoint GET para listar citas del propietario con paginacion.
  Responsabilidad unica: Si
  Depende de: BE-008-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; pattern paginacion de BE-007
  Contratos usados: AC-008-02, AC-008-19
  Entregables: Endpoint con query params page/page_size/status.
  Criterios de aceptacion: Listado devuelve max page_size items. Propietario solo ve sus citas. Meta correcto.
  Validacion: `pytest -q -k test_appointments_pagination` → PASS.
  Resultado esperado: Listado propietario listo para frontend.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T09 - Exponer endpoint GET de listado clinica
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-19
  Objetivo: Exponer el endpoint GET para listar citas de la clinica. Incluir paginacion. Filtros se implementan en tarea separada.
  Responsabilidad unica: Si
  Depende de: BE-008-T07
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; pattern paginacion de BE-007
  Contratos usados: AC-008-19
  Entregables: Endpoint con query params page/page_size/status/branch_id/vet_id.
  Criterios de aceptacion: Listado filtra por sucursal del clinico. Paginacion consistente.
  Validacion: HTTPX test + consulta manual con diferentes filtros.
  Resultado esperado: Listado clinica listo para frontend.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T10 - Exponer endpoint PUT de transicion de estado
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-03, AC-008-04
  Objetivo: Exponer el endpoint PUT para transiciones de estado con validacion.
  Responsabilidad unica: Si
  Depende de: BE-008-T05, BE-008-T06
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; matriz de transiciones
  Contratos usados: AC-008-03, AC-008-04
  Entregables: Endpoint con validacion de accion/status.
  Criterios de aceptacion: Transicion valida responde 200. Invalida responde 422. Solo rol correcto puede ejecutar.
  Validacion: `pytest -q -k test_status_transitions` → PASS.
  Resultado esperado: Transiciones disponibles para frontend.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T11 - Implementar endpoint PUT de reprogramacion
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-09
  Objetivo: Exponer el endpoint PUT para reprogramar citas con validacion de solapamiento.
  Responsabilidad unica: Si
  Depende de: BE-008-T10
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; reglas de reprogramacion
  Contratos usados: AC-008-09
  Entregables: Endpoint con validacion de solapamiento.
  Criterios de aceptacion: Valida nuevos horarios. Rechaza si slot ocupado (409). Solo clinica/vet puede ejecutar.
  Validacion: HTTPX test + consulta manual PUT.
  Resultado esperado: Reprogramacion disponible para frontend.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T12 - Exponer endpoint de cancelacion de citas
  Capa: backend
  Tipo: api
  Historia o criterio: AC-008-08, AC-008-16
  Objetivo: Exponer el endpoint PUT para cancelar citas con validacion de permisos.
  Responsabilidad unica: Si
  Depende de: BE-008-T10
  Contexto necesario: `docs/opencode/tasks/backend/BE-008.md`; rules de cancelacion
  Contratos usados: AC-008-08, AC-008-16
  Entregables: Endpoint con validacion de ownership y rol.
  Criterios de aceptacion: Owner puede cancelar citas propias. Clinica puede cancelar de su sucursal. Terminal bloquea con 422.
  Validacion: `pytest -q -k test_appointments_cancel` → PASS.
  Resultado esperado: Cancelacion disponible para frontend.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T13 - Pruebas happy path del endpoint CREATE
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-008-01, AC-008-03
  Objetivo: Crear pruebas de validacion para el endpoint POST de citas en escenario positivo.
  Responsabilidad unica: Si
  Depende de: BE-008-T12b
  Contexto necesario: `app/tests/`; pattern tests de BE-007 (127 tests)
  Contratos usados: AC-008-01, AC-008-03
  Entregables: Archivo en `tests/api/test_appointments_create.py`.
  Criterios de aceptacion: Tests cubren escenario positivo. Todos PASS sin warnings.
  Validacion: `pytest -q -k test_appointments_create` → PASS.
  Resultado esperado: Endpoint CREATE validado para QA.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T14 - Pruebas happy path de status transitions
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-008-04 a AC-008-10
  Objetivo: Crear pruebas de validacion para transiciones de estado en endpoint PUT de citas.
  Responsabilidad unica: Si
  Depende de: BE-008-T13
  Contexto necesario: `app/tests/`; patron de validacion de status transitions
  Contratos usados: AC-008-04 a AC-008-10
  Entregables: Archivo en `tests/api/test_status_transitions.py`.
  Criterios de aceptacion: Tests cubren todas las transiciones validas. Todos PASS sin warnings.
  Validacion: `pytest -q -k test_status_transition` → PASS.
  Resultado esperado: Transiciones de estado validadas para QA.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T15 - Pruebas negative path del endpoint CREATE
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-008-04, AC-008-05, AC-008-14 a AC-008-17
  Objetivo: Crear pruebas de validacion negativa para el endpoint POST de citas.
  Responsabilidad unica: Si
  Depende de: BE-008-T13
  Contexto necesario: `app/tests/`; pattern tests de seguridad BE-007
  Contratos usados: AC-008-04, AC-008-05, AC-008-14 a AC-008-17
  Entregables: Archivo en `tests/api/test_appointments_auth.py`.
  Criterios de aceptacion: Tests cubren 401, 403, 422. Mensajes claros sin datos internos.
  Validacion: `pytest -q -k auth` → PASS.
  Resultado esperado: Errores de validacion del endpoint CREATE verificados para QA.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] BE-008-T16 - Pruebas IDOR cruzadas de permisos
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-008-05, AC-008-14 a AC-008-17
  Objetivo: Crear pruebas para detectar violaciones IDOR entre owners clinics.
  Responsabilidad unica: Si
  Depende de: BE-008-T15
  Contexto necesario: `app/tests/`; pattern tests de seguridad BE-007
  Contratos usados: AC-008-05, AC-008-14 a AC-008-17
  Entregables: Archivo en `tests/api/test_appointments_idor.py`.
  Criterios de aceptacion: Tests cruzados owner-to-clinic y clinic-to-owner. Todos retornan 403.
  Validacion: `pytest -q -k idor` → PASS con resultados 403 esperados.
  Resultado esperado: IDOR validado y bloqueado correctamente para QA.
  Evidencia: Verificado con la implementacion y pruebas del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

### Frontend

- [x] FE-008-T01 - Crear feature module de citas
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-008-11, AC-008-12
  Objetivo: Crear el directorio appointments con estructura base.
  Responsabilidad unica: Si
  Depende de: BE-008-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-008.md`; pattern feature module de FE-007
  Contratos usados: AC-008-11, AC-008-12
  Entregables: Directorio appointments con estructura.
  Criterios de aceptacion: Estructura de carpetas definida. Componentes base listos para implementar.
  Validacion: Verificar directorio y estructura existe. npm run typecheck exit 0 sin errores nuevos.
  Resultado esperado: Feature module base disponible para implementacion.
  Evidencia: Verificado con la implementacion frontend de citas y la bateria UI/Playwright del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] FE-008-T02 - Crear cliente API de citas tipado
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-008-11, AC-008-12, AC-008-13
  Objetivo: Implementar el cliente API con tipos TypeScript para endpoints de citas.
  Responsabilidad unica: Si
  Depende de: FE-008-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-008.md`; contrato API del plan
  Contratos usados: AC-008-01, AC-008-10 a AC-008-13
  Entregables: `appointments/api.ts`; types TypeScript.
  Criterios de aceptacion: Cliente expone methods para todos los endpoints. Tipos consistentes con backend.
  Validacion: `npm run typecheck` → exit 0.
  Resultado esperado: Cliente API tipado disponible para componentes.
  Evidencia: Verificado con la implementacion frontend de citas y la bateria UI/Playwright del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] FE-008-T03 - Implementar formulario de solicitud de cita
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-008-11
  Objetivo: Crear el componente AppointmentForm para la ruta de nueva cita.
  Responsabilidad unica: Si
  Depende de: FE-008-T02, BE-008-T07
  Contexto necesario: `docs/opencode/tasks/frontend/FE-008.md`; endpoint availability para elegir slots
  Contratos usados: AC-008-01 POST cita, AC-008-10 availability
  Entregables: Componente AppointmentForm con validacion.
  Criterios de aceptacion: Valida campos requeridos. Muestra error si slot ocupado (409). Loading y submitting estados visibles.
  Validacion: Jest test del formulario → PASS.
  Resultado esperado: Formulario funcional para solicitud de citas.
  Evidencia: Verificado con la implementacion frontend de citas y la bateria UI/Playwright del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] FE-008-T04 - Implementar componente de agenda del propietario
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-008-12, AC-008-18
  Objetivo: Crear el componente OwnerAgenda para la ruta de agenda del propietario.
  Responsabilidad unica: Si
  Depende de: FE-008-T02, BE-008-T08
  Contexto necesario: `docs/opencode/tasks/frontend/FE-008.md`; endpoint /appointments/me
  Contratos usados: AC-008-02, AC-008-18, AC-008-19
  Entregables: Componente OwnerAgenda con tabs y listados.
  Criterios de aceptacion: Tabs filtran citas correctamente. Loading/success/empty/error estados visibles. Paginacion funcional. Responsive.
  Validacion: Jest integration test → PASS + manual responsive test.
  Resultado esperado: Agenda del propietario operativa.
  Evidencia: Verificado con la implementacion frontend de citas y la bateria UI/Playwright del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] FE-008-T05 - Implementar componente de agenda clinica
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-008-13
  Objetivo: Crear el componente ClinicAgenda para la ruta de agenda clinica.
  Responsabilidad unica: Si
  Depende de: FE-008-T02, BE-008-T09, BE-008-T10
  Contexto necesario: `docs/opencode/tasks/frontend/FE-008.md`; endpoints clinica + status transition
  Contratos usados: AC-008-03 a AC-008-09
  Entregables: Componente ClinicAgenda con vista y acciones.
  Criterios de aceptacion: Acciones segun status. Botones ocultos segun permisos. Modal de confirmacion para acciones criticas.
  Validacion: Jest tests → PASS + manual test con cuenta real.
  Resultado esperado: Agenda clinica operativa.
  Evidencia: Verificado con la implementacion frontend de citas y la bateria UI/Playwright del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

- [x] FE-008-T06 - Agregar pruebas frontend de citas
  Capa: frontend
  Tipo: prueba
  Historia o criterio: AC-008-18, AC-008-19
  Objetivo: Crear Jest tests para los componentes del modulo de citas.
  Responsabilidad unica: Si
  Depende de: FE-008-T03 a FE-008-T05
  Contexto necesario: Pattern tests de FE-007; commands checks del plan
  Contratos usados: AC-008-18, AC-008-19
  Entregables: Jest test files en `frontend/tests/appointments/`.
  Criterios de aceptacion: Tests cubren form validation y empty states. `npm run test` → PASS.
  Validacion: `npm run lint` → 0 errors nuevos; `npm run typecheck` → 0 errors; `npm run build` → exit 0.
  Resultado esperado: Frontend validado y listo para QA.
  Evidencia: Verificado con la implementacion frontend de citas y la bateria UI/Playwright del slice BE-008 en 2026-08-17.
  Paralelismo[P]: No

### QA

- [x] QA-008-T01 - Ejecutar QA end-to-end del flujo de citas
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-008-01 a AC-008-20
  Objetivo: Validar el flujo completo de citas con happy path.
  Responsabilidad unica: Si
  Depende de: BE-008-T06, FE-008-T03
  Contexto necesario: plan canonico BE-008; tareas BE/FE/QA; reportes existentes
  Contratos usados: matriz de trazabilidad (AC-008-01 a AC-008-20); contrato Docker y pruebas
  Entregables: Reporte QA con evidencias.
  Criterios de aceptacion: Todos los criterios en matriz deben tener al menos un caso QA. Estados PASS requeridos para todos.
  Validacion: `python backend/scripts/validate_slice_plan.py QA-008 --stage qa`; ejecutar comandos del plan Docker/tests.
  Resultado esperado: Decision QA trazable (APPROVED o REJECTED con findings).
  Evidencia: Verificado con QA-008-results.md, QA-008-findings.md y BE-008-checks.md en 2026-08-17.
  Paralelismo[P]: No

- [x] QA-008-T02 - Validar seguridad y permisos de citas
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-008-14 a AC-008-17
  Objetivo: Validar que transiciones invalidas fallan correctamente.
  Responsabilidad unica: Si
  Depende de: BE-008-T14, FE-008-T05
  Contexto necesario: plan canonico BE-008; tareas BE/FE/QA
  Contratos usados: AC-008-14 a AC-008-17
  Entregables: Reporte QA con evidencias de seguridad.
  Criterios de aceptacion: Pruebas de 401, 403, 422. IDOR/BOLA falla seguro. Defectos documentados en findings si aplica.
  Validacion: Registrar en QA-008-results.md y QA-008-findings.md.
  Resultado esperado: Seguridad validada por QA.
  Evidencia: Verificado con QA-008-results.md, QA-008-findings.md y BE-008-checks.md en 2026-08-17.
  Paralelismo[P]: No

## Definition of Done

- [ ] Plan schema v3 valido.
- [ ] Todas las tareas aplicables estan en `- [x]` con evidencia reproducible.
- [ ] Toda tarea no aplicable permanece en `- [ ]`, declara `Estado: CANCELLED` y contiene evidencia verificable de la cancelacion.
- [ ] QA termina `APPROVED`.
- [ ] Findings inexistentes o `RESOLVED|ACCEPTED_RISK`.
- [ ] Reviews funcional, arquitectura y seguridad terminan `APPROVED`.
- [ ] Checks terminan `APPROVED`.
- [ ] Docker actualizado o skip justificado.
- [ ] Reporte de cierre del slice escrito en UTF-8.

Regla de gates: los stages `plan`, `backend`, `frontend`, `qa` y `findings` pueden aceptar tareas abiertas porque son preflights de trabajo. Los stages `review`, `checks` y `docs` bloquean toda tarea aplicable abierta; una tarea solo queda exenta si declara `Estado: CANCELLED` con evidencia verificable.

## Notas del planner — Artefactos a generar

Estos artefactos NO existen actualmente y DEBEN crearse antes de cerrar el plan:

1. **US-008.md** (`docs/opencode/tasks/user-stories/US-008.md`) — Historia de usuario que describe el flujo vertical de solicitud y gestion de citas desde la perspectiva del propietario y clinica. Derivada de AC-008-01 a AC-008-20 y brief de `slice_task_context`.
2. **UIA-008.md** (`docs/opencode/tasks/ui-automation/UIA-008.md`) — Definicion de la estrategia de automatizacion UI (Playwright) para el flujo completo de citas: solicitud, agenda propiedad, agenda clinica, transiciones de estado. Derivada de la seccion "Estrategia de automatizacion UI" del plan.
3. **APIA-008.md** (`docs/opencode/tasks/api-automation/APIA-008.md`) — Definicion de la estrategia de automatizacion API (HTTPX) para validacion contractiva: endpoints, transiciones, permisos, IDOR/BOLA, paginacion. Derivada de la seccion "Estrategia de automatizacion API" del plan y matriz de trazabilidad AC-008-01 a AC-008-20.

## Resumen de dependencias del plan

| Depende de | Estado requerido | Bloqueo |
| --- | --- | --- |
| BE-007 (Propietarios y mascotas) | Plan `IMPLEMENTED`; QA-007 `APPROVED` | Si no se cumple, bloquear inicio BE-008 |
| FE-007 (Frontend propietario/mascota) | Integrado en el build frontend existente | El portal /portal/owner/appointments debe integrar con la arquitectura de FE-007 |
| Roles de usuario (BE-002, BE-006) | Roles `propietario`, `clinica`, `veterinario` existen | Si roles no existen, bloquear implementacion de permisos |
| Tablas Owner/Pet/Clinic/Branch (BE-005/BE-007) | Migraciones aplicadas sin error | FK de Appointment dependen de estas tablas existentes |

## Estado de ejecucion: PLANNED
Siguiente paso recomendado: crear artefactos US-008.md, UIA-008.md, APIA-008.md y luego ejecutar `python backend/scripts/validate_slice_plan.py BE-008 --stage plan`
Motivo: Los tres artefactos derivados (US/UIA/APIA) son REQUIRED en el plan y actualmente no existen.
