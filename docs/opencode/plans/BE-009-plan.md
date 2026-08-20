---
schema_version: 3
slice: "009"
canonical_plan: BE-009
status: PLANNED
encoding: UTF-8
last_updated: 2026-08-19
---

# BE-009 Plan — Consulta médica básica / Basic medical consultation

## Estado actual

| Componente | Archivo | Estado |
|-----------|---------|--------|
| Brief de tarea | `docs/opencode/tasks/backend/BE-009.md` | ✅ EXISTS |
| Brief frontend | `docs/opencode/tasks/frontend/FE-009.md` | ✅ EXISTS |
| Brief QA | `docs/opencode/tasks/qa/QA-009.md` | ✅ EXISTS |
| Breve contexto slice | `docs/opencode/references/slice_task_context.md` (fila 009) | ✅ EXISTS |
| Contexto carryovers | `docs/opencode/carryovers/BE-009-carryovers.md` | ✅ CREATED |

## Objetivo del slice

Crear el flujo vertical completo de registro, consulta y listado de consultas médicas veterinarias vinculadas a citas completadas: un veterinario puede registrar una consulta desde el portal clínico asociada a una cita con `status = completed`, un propietario puede visualizar el historial de consultas de sus mascotas (read-only), y QA valida el end-to-end con coverage de permisos, ownership, IDOR/BOLA y estados UI.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Consulta médica básica |
| Descripcion | Registrar consulta vinculada a cita completada y mascota; formulario clinico veterinario; historial de consultas por mascota en portal propietario; listado paginado con filtros por pet_id/clinic. |
| Entregables backend | Entidad `Consultation`, repositorio (protocolo + ORM), casos de uso, schemas Pydantic, router `/api/v1/consultations` con POST/GET detalle/GET listado paginado, migracion Alembic, pruebas pytest/HTTPX. |
| Entregables frontend | Cliente API en `src/shared/api`, formulario clinico `clinic/appointments/[id]/consultation/page.tsx`, historial de consultas por mascota `portal/owner/pets/[id]/consultations/page.tsx`, vista detalle `portal/owner/consultations/[id]/page.tsx`. |
| Criterios QA principales | Solo se crea para cita completed; permisos por rol funcionan (401/403); IDOR/BOLA falla seguro; paginacion consistente; formularios muestran loading/error/success; listados tienen estados empty/loading/success. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Modelo `Consultation` con campos minimos:
  - `id`, `appointment_id` (unique FK, referencia cita), `pet_id` (FK a Pet), `clinic_id` (FK a Clinica), `branch_id`, `veterinarian_id` (FK a user autorizada), `history` (texto descripcion clinica), `diagnosis` (texto diagnostico), `recommendations` (texto recomendaciones tratamiento), `created_by` (FK user), `updated_at`.
  - Constraint unique sobre `appointment_id` para evitar duplicados.
- Regla de negocio critica: solo se permite crear consulta cuando `Appointment.status == completed`. Si el status no es completed, retornar 422 con mensaje claro.
- Validacion de ownership: veterinario debe pertenecer a la misma clinica/branch que la cita asociada. Propietario solo ve consultas de mascotas de su propiedad.
- Endpoints protegidos con Bearer token:
  - Veterinario/Clinica: crear consulta (`POST`), listar por pet_id/clinic (GET con paginacion).
  - Propietario: ver detalle de consulta (`GET /{id}`), ver historial de mascotas (`GET ?pet_id=`).
- Migraciones Alembic para tabla `consultations` con indices compuestos `(pet_id)`, `(clinic_id)`, unique sobre `(appointment_id)`.
- Paginacion en listados (`?page=1&page_size=20`).
- Pruebas pytest/HTTPX: happy path creacion, negative path cita no completed, 401 sin token, 403 sin permiso, IDOR con IDs cruzados.

## Fuera de alcance

- Actualizacion de consulta despues de creada (no se implementa PUT/PATCH para este slice).
- Eliminacion de consultas registradas.
- Notas clinicas avanzadas o adjuntos/archivos (imagenes, PDFs).
- Historial clinico completo del paciente integrado (solo consultas de este slice).
- Notificaciones por consulta nueva (slice siguiente si aplica).
- Reportes estadisticos ni dashboard clinico.
- Productos, marketplace, carrito, checkout, pasarela de pago, facturacion electronica y timbrado fiscal.
- Analitica avanzada o dashboards avanzados.

## Suposiciones

- La entidad `Appointment` del slice BE-008 existe con campo `status` incluyendo valor `completed`.
- La entidad `Pet` del slice BE-007 existe y tiene FK a `owner_id`.
- Los roles de usuario (`propietario`, `clinica`, `veterinario`) ya existen definidos en slices previos (BE-002, BE-006).
- La tabla `clinics` y `branches` existe con campos `id`, `name`, `tenant_id`.
- El owner del slice BE-007 tiene acceso de lectura donde se permite por rol.
- Si el supuesto sobre roles o estructuras existentes cambia, detener planificacion y preguntar.

## Revision de gaps

- Fuente revisada: `docs/opencode/02_be_fe_qa_task_matrix.md` (fila 009), `BE-009.md`, `FE-009.md`, `QA-009.md`, `slice_task_context.md` (fila 009), `slice_plan_template.md`, `missing_artifact_generation.md`, `carryovers_governance.md` y `BE-009-carryovers.md` (sin carryovers OPEN/TRANSFERRED).
- Gap: No se especifica si se permite modificar consulta despues de creada.
- Decision: NO se implementa actualizacion (PUT/PATCH) en este slice. Solo creacion y lectura. Si se requiere en futuro, agregar como carryover a slice siguiente.
- Gap: No se especifica si historial clinico completo integra consultas de otros slices previos.
- Decision: Por ahora solo se listan consultas de este slice filtradas por `pet_id`. Integracion con otros tipos de registros clinicos queda para slice futuro si existe.
- Impacto en tareas: Backend T05 (use case) valida que solo se crea; Frontend T01 y T02 reflejan contrato POST unico sin PUT/PATCH.

### Revision de gaps — Re-planificacion BE-009 (2026-08-19)

- Gap: Mojibake/texto roto en AC-009-02 (AC-009-02: `appointment_id指向非completed`), AC-009-10 (`camp req missing`) y en Formularios (`debe指向 cita`).
  - Decision: Corregido a UTF-8 espanol: AC-009-02 usa "cita no completed", AC-009-10 "campo requerido ausente", formularios "debe referirse a una cita con status=completed". Adicionalmente se corrigio "errores fixeados" → "errores corregidos".
  - Impacto: Solo redaccion; sin cambio de alcance.
- Gap: AC-009-03 (owner ve historial, criterio frontend) estaba mapeado a `BE-009-T07` (endpoint POST de creacion), inconsistente.
  - Decision: Mapeado a `FE-009-T03` con validacion de ruta `/portal/owner/pets/[id]/consultations` + `QA-009-T01` para evidencia end-to-end.
  - Impacto: Matriz de trazabilidad y campo `Historia o criterio` de FE-009-T03.
- Gap: Mapeo tarea↔criterio incompleto o incorrecto en tareas BE/FE.
  - Decision: Auditoria completa de la matriz. Cambios registrados:
    - BE-009-T05 pasa de `AC-009-01, AC-009-02, AC-009-06` a `AC-009-01, AC-009-02, AC-009-06, AC-009-11` (la regla de ownership vet/clinica es de capa use case).
    - BE-009-T06 pasa de `AC-009-01, AC-009-07, AC-009-11` a `AC-009-07, AC-009-10` (validacion de campos es de schema, no de T06→AC-009-11; AC-009-11 se cubre en T05).
    - BE-009-T07 pasa de `AC-009-03, AC-009-07` a `AC-009-01, AC-009-02, AC-009-07, AC-009-10` (T07 es el endpoint POST; AC-009-03 es criterio de lectura y no aplica a un POST).
    - BE-009-T08 pasa de `AC-009-01, AC-009-07, AC-009-11` a `AC-009-04, AC-009-05, AC-009-09, AC-009-12` (los GET de listado/detalle son los que materializan ownership, paginacion y authn en lectura).
    - FE-009-T01 pasa de `AC-009-07, AC-009-08, AC-009-09` a `AC-009-07, AC-009-09` (AC-009-08 es criterio de formulario, no de cliente API).
    - FE-009-T02 pasa de `AC-009-10, AC-009-07` a `AC-009-08, AC-009-10` (el formulario es el responsable de los estados UX de submit; AC-009-07 queda cubierto por el endpoint).
    - FE-009-T03 pasa de `AC-009-08, AC-009-13` a `AC-009-03, AC-009-05, AC-009-09, AC-009-13` (historial por mascota: AC-009-03 owner, AC-009-05 ownership filtrado, AC-009-09 paginado, AC-009-13 empty state).
    - FE-009-T04 pasa de `AC-009-09, AC-009-13` a `AC-009-04, AC-009-13` (detalle individual: AC-009-04 view, AC-009-13 empty state si consulta no existe).
  - Impacto: La matriz de trazabilidad refleja ahora un mapeo coherente por criterio: cada `AC-009-NN` apunta a la(s) tarea(s) de la capa que implementa el criterio y a la tarea QA de la area que lo valida.
- Gap: `QA-009-T01` era una tarea compuesta (cubria AC-009-02/03/04/11/14 juntas), violando las reglas de atomicidad (`Responsabilidad unica: Si` con un solo objetivo).
  - Decision: Dividida en 5 tareas atomicas por area de validacion:
    - QA-009-T01 — happy path (AC-009-01, AC-009-03, AC-009-04).
    - QA-009-T02 — errores/validaciones (AC-009-02, AC-009-06, AC-009-10).
    - QA-009-T03 — permisos/IDOR/authn (AC-009-05, AC-009-11, AC-009-12).
    - QA-009-T04 — regresion UI y estados (AC-009-07, AC-009-08, AC-009-09, AC-009-13).
    - QA-009-T05 — evidencia de migracion y cierre de reportes (AC-009-14).
  - Impacto: Matriz de trazabilidad; section QA del plan; sidecars UIA/APIA referenciados.
- Gap: El plan canónico declaraba `status: COMPLETED` en el frontmatter mientras todas las tareas estaban en `- [ ]` con `Evidencia: pending`.
  - Decision: Corregido a `status: PLANNED`, consistente con el estado real del slice. La seccion "Estado actual" (que no esta en la plantilla pero no contradice el frontmatter) se conserva como informacion de contexto.
  - Impacto: Solo frontmatter.
- Gap: Faltaban los sidecars `US-009.md`, `UIA-009.md` y `APIA-009.md` (obligatorio por `missing_artifact_generation.md`).
  - Decision: Creados en esta ejecucion con la misma cobertura AC-009-01..14, evidencias `pending`, y estado `OPEN` (no se declara `PASSED` sin gate vigente).
  - Impacto: `docs/opencode/tasks/user-stories/US-009.md`, `docs/opencode/tasks/ui-automation/UIA-009.md`, `docs/opencode/tasks/api-automation/APIA-009.md`.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Consultation | BE-009, rules of slice | Modelo principal con campos clinicos basicos | Pytest + HTTPX |
| Status validation | BE-008 (Appointment.status) | Solo crear si `status == completed` | Prueba negativa: intentar crear para no-completed → 422 |
| Unique appointment_id | BE-009, reglas de negocio | Unica consulta por cita completada | Constraint DB + prueba duplication |
| Ownership/BOLA | BE-007, QA-009 | Validar ownership vet/clinic en creacion; owner solo ve sus mascotas | IDOR tests cruzados |
| Paginacion | BE-009, reglas existentes | Listados paginados en /consultations | Verificar query params page/page_size |
| Veterinarian authorization | BE-009 | Solo veterinario/clinica autorizada puede registrar | Prueba 403 sin rol adecuado |
| Read-only owner | FE-009, QA-009 | Propietario solo visualiza (read-only) | UI tests: no botones de edicion para owner |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-009.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-009.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-009.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Historias de usuario | `docs/opencode/tasks/user-stories/US-009.md` | Historias US-009-NN con criterios AC-009-NN | REQUIRED |
| Automatizacion UI | `docs/opencode/tasks/ui-automation/UIA-009.md` | Cobertura Playwright prevista por criterio | REQUIRED |
| Automatizacion API | `docs/opencode/tasks/api-automation/APIA-009.md` | Cobertura HTTP prevista por criterio | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| Carryovers governance | `docs/opencode/references/carryovers_governance.md` | Reglas de carryovers (verificar no hay carryovers pendientes) | REQUIRED |
| BE-008 plan (referencia) | `docs/opencode/plans/BE-008-plan.md` | Patrones de implementacion, ORM, router, schemas | REFERENCE |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-009-01 | BE-009, slice_task_context | Veterinario registra consulta valida para cita completed | BE-009-T05+T07; QA-009-T01 | POST /api/v1/consultations responde 201 con datos de consulta creada | Response JSON con fields clinicos, status=ok | OPEN |
| AC-009-02 | QA-009 | Intentar crear consulta para cita no completed falla con error claro | BE-009-T05, BE-009-T07; QA-009-T02 | POST con appointment_id de cita no completed → 422 | Response con mensaje "appointment not completed" | OPEN |
| AC-009-03 | QA-009, FE-009 | Owner ve historial de consultas de su mascota (read-only) | FE-009-T03; QA-009-T01 | Ruta /portal/owner/pets/[id]/consultations renderiza listado paginado | UI con items, meta paginacion, sin botones edicion | OPEN |
| AC-009-04 | QA-009 | Owner ve detalle de consulta individual (read-only) | FE-009-T04; QA-009-T01 | Ruta /portal/owner/consultations/[id] muestra campos clinicos legibles | UI con campos display-read only, accesible | OPEN |
| AC-009-05 | BE-009, QA-009 | Solo propietario ve consultas de sus mascotas; no filtrado incorrecto | BE-009-T08; QA-009-T03 | GET /consultations?pet_id= con token owner A → solo items del pet de owner A | Respuesta sin datos de otras mascotas | OPEN |
| AC-009-06 | BE-009, reglas negocio | Unique constraint sobre appointment_id evita duplicados | BE-009-T03+T07; QA-009-T02 | Intentar doble creacion para misma cita → 409 o 422 | Error claro "consulta ya existe" | OPEN |
| AC-009-07 | BE-009, FE-009 | Endpoint POST crea consulta con validacion completa de campos | BE-009-T06+T07; QA-009-T04 | Schemas Pydantic validan campos requeridos; response 201 exitosa | JSON response con todos los campos clinicos | OPEN |
| AC-009-08 | FE-009, QA-009 | Formulario clinico muestra estados UI correctos (loading/success/error) | FE-009-T02; QA-009-T04 | Submit formulario con y sin datos valida feedback visual | Spinner loading → success toast / error banner | OPEN |
| AC-009-09 | FE-009, QA-009 | Listado paginado de consultas muestra estados UI consistentes | FE-009-T03; QA-009-T04 | GET paginado con y sin datos → loading/empty/success | Tabla con items o empty state con CTA | OPEN |
| AC-009-10 | QA-009 | Input invalido (campo requerido ausente) produce error 422 claro | BE-009-T06, BE-009-T07; QA-009-T02 | POST sin diagnosis → 422 response legible | JSON error con campo invalido | OPEN |
| AC-009-11 | QA-009, BE-007 | IDOR: veterinario de otra clinica no accede a consulta ajena | BE-009-T05+T08; QA-009-T03 | POST con vet clinic B para cita clinic A → 403 | Status 403 sin datos expuestos | OPEN |
| AC-009-12 | QA-009 | Usuario no autenticado recibe 401 en endpoints protegidos | BE-009-T08; QA-009-T03 | GET /consultations sin token → 401 | Status 401 | OPEN |
| AC-009-13 | FE-009, QA-009 | Historial muestra estado empty cuando mascota no tiene consultas | FE-009-T03, FE-009-T04; QA-009-T04 | GET con pet_id sin consultas → empty state | UI con "No hay consultas registradas" | OPEN |
| AC-009-14 | QA-009 | Migracion Alembic crea tabla consultations sin perder data | BE-009-T03; QA-009-T05 | Migration genera tabla con indices y unique constraint | Migration reversible, aplica limpia | OPEN |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Registrar consulta | POST | `/consultations` | Bearer (veterinario/clinica) | `{appointment_id, pet_id, diagnosis, history?, recommendations?}` | 201 `{id, ...consulta completa}` | 400, 403, 409, 422 |
| Obtener detalle | GET | `/consultations/{id}` | Bearer (owner/vet/clinica) | — | 200 `{id, diagnosis, history, recommendations, ...}` | 401, 403, 404 |
| Listar por mascota | GET | `/consultations?pet_id=` | Bearer (propietario) | `?pet_id=<int>&page=1&page_size=20` | 200 `{items: [...], meta: {...}}` | 401, 404 |
| Listar por clinica | GET | `/consultations?clinic_id=` | Bearer (clinica/vet) | `?clinic_id=<int>&page=1&page_size=20` | 200 `{items: [...], meta: {...}}` | 401, 403 |

## Contrato de implementacion frontend

### Rutas y acceso

- `/clinic/appointments/[id]/consultation` — Formulario de registro de consulta medica desde agenda veterinaria. Solo accesible para usuarios con rol veterinario/clinica con cita associada al status completed.
- `/portal/owner/pets/[id]/consultations` — Historial de consultas por mascota en portal del propietario. Read-only, sin botones de edicion.
- `/portal/owner/consultations/[id]` — Detalle individual de consulta para el propietario. Campos clinicos legibles, sin Edicion.

### Flujos y estados UX

**Registro de consulta (veterinario):**
1. Veterinario navega a `/clinic/appointments/[id]/consultation` desde agenda de citas.
2. Verifica que cita tenga status = completed.
3. Completa campos: diagnosis (requerido), history (opcional), recommendations (opcional).
4. Estado: loading → submitting → success / error / empty (si datos de cita no disponibles).

**Historial de consultas (propietario):**
1. Propietario navega a `/portal/owner/pets/[id]/consultations`.
2. Listado paginado con todas las consultas de la mascota ordenadas por fecha descendente.
3. Estado: loading → success / empty (sin consultas registradas) / error.

**Detalle de consulta (propietario):**
1. Propietario navega a `/portal/owner/consultations/[id]`.
2. Visualiza campos clinicos con etiquetas legibles para no-medicos.
3. Estado: loading → success / empty (consulta no existe o sin permiso) / error.

**Estados UX requeridos por componente:**
- `loading`: spinner en listados y formularios al obtener datos.
- `submitting`: botón disabled con spinner al enviar formulario de creacion.
- `error`: banner rojo con mensaje de error legible (no interno).
- `empty`: estado vacio con CTA apropiado cuando no hay datos.
- `success`: toast/banner verde de confirmacion tras operacion exitosa.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Registrar consulta | POST `/consultations` | Bearer (vet/clinica) | `{appointment_id, pet_id, diagnosis, history?, recommendations?}` | 201 `{id, ...}` | 400, 403, 409, 422 | Veterinario/Clinica |
| Obtener detalle | GET `/consultations/{id}` | Bearer (cualquier rol) | — | 200 `{...consulta}` | 401, 403, 404 | Cualquiera con permiso |
| Listar por mascota | GET `/consultations?pet_id=` | Bearer (propietario) | `?pet_id=<int>&page=1&page_size=20` | 200 `{items: [...], meta: {...}}` | 401, 404 | Propietario |
| Listar por clinica | GET `/consultations?clinic_id=` | Bearer (clinica/vet) | `?clinic_id=<int>&page=1&page_size=20` | 200 `{items: [...], meta: {...}}` | 401, 403 | Clinica/Veterinario |

### Formularios y validacion

**Formulario de registro de consulta (veterinario):**
- `appointment_id`: requerido, entero > 0 (debe referirse a una cita con status=completed).
- `pet_id`: requerido, entero > 0 (mascota debe pertenecer a la misma clinica o ser del owner vinculado a la cita).
- `diagnosis`: requerido, string max 2000 chars.
- `history`: opcional, string max 3000 chars (descripcion historia clinica relevante).
- `recommendations`: opcional, string max 3000 chars (tratamiento recomendaciones).

### Arquitectura de componentes

**Frontend features:**
- Feature module en `src/features/consultations` con:
  - `ConsultationForm` — formulario de registro desde vista veterinaria.
  - `ConsultationHistory` — listado paginado por mascota.
  - `ConsultationDetail` — detalle individual de consulta.
  - `ConsultationList` — componente reusable para listados (paginacion + estados UI).

**Componentes compartidos reutilizados:**
- `src/shared/ui`: Button, Input, Textarea, Table, EmptyState, LoadingSpinner, ErrorBanner, SuccessToast.
- `src/shared/api`: cliente API tipado con methods para `/consultations`.

### Responsive y accesibilidad

- **Mobile-first**: formulario en columna completa; listado de consultas en vista tabla scrollable en mobile, expandida en desktop.
- **Accesibilidad minima**: labels asociados a inputs, aria-labels en botones iconicos, contraste WCAG AA, orden tabulacion logica.

### Estrategia de pruebas frontend

- Pruebas unitarias de `ConsultationForm` (validacion de campos requeridos, max longitud).
- Pruebas unitarias de `ConsultationDetail` (renderizado de campos clinicos con etiquetas legibles).
- Pruebas de integracion de flujo completo con mocks: registrar consulta → listar en historial → ver detalle.
- Typecheck (`tsc`) y lint limpios sin errores nuevos del slice.

## Estrategia de automatizacion UI

- Tests E2E con Playwright (dentro de `InVet_UI_Automation/tests/`):
  - `test_009_consultation_form.ts`: veterinario autentica, navega a formulario, completa campos, verifica creacion exitosa.
  - `test_009_owner_history.ts`: propietario visualiza historial de consultas de mascota; UI muestra loading/success/empty.
  - `test_009_consultation_detail.ts`: propietario ve detalle individual; campos legibles sin edicion.

## Estrategia de automatizacion API

- Pruebas contractuales con HTTPX dentro de `backend/app/tests/`:
  - `test_consultations_create.py`: happy path creacion (201), negative path cita no completed (422).
  - `test_consultations_auth.py`: 401 sin token, 403 sin rol adecuado.
  - `test_consultations_idor.py`: acceso cruzado con tokens de diferentes vets/owners.
  - `test_consultations_pagination.py`: paginacion consistente (page/page_size).
  - `test_consultations_duplicate.py`: intento creacion duplicate para mismo appointment_id → 409.

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | Estado del servicio |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/ -q -k consultation` | Cuando el criterio requiere PostgreSQL real | Conteo de tests PASS |
| Validacion plan | `python backend/scripts/validate_slice_plan.py BE-009 --stage plan` | Preflight de implementacion | Salida PASS o errores corregidos |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreados |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida 0 |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-009-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task QA-009` |
| `docs/opencode/qa/QA-009-findings.md` | QA | Implementadores, QA | Si hay FAIL, BLOCKED o gaps unitarios |
| `docs/opencode/reviews/BE-009-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice BE-009` |
| `docs/opencode/reviews/BE-009-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-009-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-009-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-009` |
| `docs/opencode/slices/BE-009-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| AC-009-01: Veterinario registra consulta valida (citas completed) | Creacion invalida | integration | `tests/api/test_consultations_create.py` | PENDING |
| AC-009-02: Intentar crear para cita no-completed falla | Bypass de negocio | integration | `tests/api/test_consultations_create.py` | PENDING |
| AC-009-03: Owner ve historial de consultas (read-only) | Acceso incorrecto | frontend/integration | Playwright test + UI states | PENDING |
| AC-009-04: Owner ve detalle de consulta individual | Exposicion datos | integration | GET /consultations/{id} → 200 fields legibles | PENDING |
| AC-009-05: Owner solo ve consultas de sus mascotas | IDOR critico | security | `tests/api/test_consultations_idor.py` | PENDING |
| AC-009-06: Unique constraint sobre appointment_id | Duplicados clinicos | integration | Double POST same appointment_id → 409/422 | PENDING |
| AC-009-07: Endpoint POST valida campos requeridos | Input invalido | unit | Schema validation tests | PENDING |
| AC-009-08: Formulario clinico estados UI correctos | UX defectuoso | frontend | Jest component tests + Playwright | PENDING |
| AC-009-09: Listado paginado estados UI consistentes | UX defectuoso | frontend | Jest component tests + Playwright | PENDING |
| AC-009-10: Input invalido produce error 422 claro | UX defectuoso | integration | POST missing required → 422 response legible | PENDING |
| AC-009-11: Veterinario de otra clinica no accede | IDOR/BOLA critico | security | `tests/api/test_consultations_idor.py` | PENDING |
| AC-009-12: 401 sin token | Acceso no autorizado | security | `tests/api/test_consultations_auth.py` | PENDING |
| AC-009-13: Estado empty en historial cuando no hay datos | UX defectuoso | frontend | GET pet sin consultas → empty state UI | PENDING |
| AC-009-14: Migracion limpia crea tabla consultations | Data loss/Schema error | infrastructure | Alembic upgrade/downgrade test | PENDING |

## Riesgos de seguridad/IDOR/BOLA

- **BOLA en consultas**: Si el endpoint GET `/consultations/{id}` no valida que `consultation.pet_id` pertenezca al `owner_id` del token, un propietario puede ver consultas de otras mascotas. Mitigacion: validacion de ownership obligatoria en cada operacion.
- **IDOR en clinica**: Un veterinario de una clinica puede acceder/modificar consultas de otra clinica si no se valida `clinic_id` o `branch_id` contra el tenant/rol del token. Mitigacion: validar que el usuario pertenezca a la misma clinica/branch que la cita asociada.
- **Bypass de estado**: Un veterinario podria intentar registrar consulta para una cita que no esta en status completed. Esto debe fallar con 422 claro y NO crear ningun registro parcial. Mitigacion: validar `appointment.status == 'completed'` como primer check en el use case.
- **Duplicado de consulta**: Si no existe unique constraint DB, se pueden crear multiples consultas para la misma cita. Mitigacion: unique sobre `appointment_id` + validacion de duplicado en use case → 409 Conflict.
- **Exposicion de datos clinicos**: Las respuestas no deben exponer campos sensibles del owner (email, telefono) ni datos clinicos de otras mascotas en listados paginados.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [ ] Rutas backend y prefijos API definidos.
- [ ] Contratos request/response documentados.
- [ ] Permisos y ownership definidos por endpoint o accion.
- [ ] Estados 400, 401, 403, 404 y validaciones definidos.
- [ ] Modelos, migraciones o cambios de persistencia identificados.
- [ ] Casos QA positivos, negativos y de permisos trazados a criterios.
- [ ] Checks esperados definidos para backend y frontend.
- [ ] Docker definido o skip justificado.
- [ ] Reportes y findings esperados identificados.
- [ ] UTF-8 declarado para planes, reportes, comentarios y outcomes.
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
- Titulo, descripcion, entregables y criterios de aceptacion deben alinearse con `Brief operativo del slice`.
- Si el brief, la matriz y las tasks BE/FE/QA discrepan, registrar la decision en `Revision de gaps`.

### Backend

- [ ] BE-009-T01 - Definir entidad de dominio Consultation
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-009-01, AC-009-06
  Objetivo: Definir entidad de dominio Consultation con constraint unique appointment_id.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; matriz del slice; `backend/app/domain/entities/appointment.py` (referencia BE-008)
  Contratos usados: AC-009-01, AC-009-06
  Entregables: `backend/app/domain/entities/consultation.py`
  Criterios de aceptacion: Clase Consultation con campos completos (id, appointment_id unique, pet_id, clinic_id, branch_id, veterinarian_id, history, diagnosis, recommendations, created_by, updated_at). Validacion en entidad.
  Validacion: `python -c "from app.domain.entities.consultation import Consultation; print(Consultation.model_fields.keys())"` verifica campos.
  Resultado esperado: Entidad de dominio disponible para contrato repositorio.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T02 - Definir contrato repositorio de Consultation
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-009-01, AC-009-06
  Objetivo: Definir protocolo abstracto de repositorio con metodos create, get_by_id, list_by_pet, list_by_clinic.
  Responsabilidad unica: Si
  Depende de: BE-009-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; entidad de dominio creada en T01
  Contratos usados: AC-009-01, AC-009-06
  Entregables: `backend/app/domain/repositories/consultation_repository.py` (protocolo/interface)
  Criterios de aceptacion: Protocolo con metodos create, get_by_id, list_by_pet, list_by_clinic. Tipos bien definidos.
  Validacion: `python -c "from app.domain.repositories.consultation_repository import ConsultationRepository; print(ConsultationRepository.__abstractmethods__)"` lista metodos.
  Resultado esperado: Contrato repositorio disponible para implementacion de infraestructura.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T03 - Implementar modelo ORM y migracion Alembic
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-009-06, AC-009-14
  Objetivo: Crear modelo SQLAlchemy para tabla consultations con indices.
  Responsabilidad unica: Si
  Depende de: BE-009-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; entidad de dominio; ORM pattern de BE-008 (`backend/app/infrastructure/database/models/appointment.py`)
  Contratos usados: AC-009-06, AC-009-14
  Entregables: `backend/app/infrastructure/database/models/consultation.py`, migracion Alembic en `alembic/versions/`
  Criterios de aceptacion: Modelo mapea campos correctamente. Indices compuestos en (pet_id), (clinic_id). Unique sobre (appointment_id). Migracion reversible con downgrade.
  Validacion: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` sin errores.
  Resultado esperado: Tabla consultations disponible en base de datos.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T04 - Implementar repositorio ORM
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-009-01, AC-009-06
  Objetivo: Implementar ConsultationRepository con logica de persistencia.
  Responsabilidad unica: Si
  Depende de: BE-009-T02, BE-009-T03
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; contrato repositorio; modelo ORM creado en T03
  Contratos usados: AC-009-01, AC-009-06
  Entregables: `backend/app/infrastructure/repositories/consultation_repository_impl.py`
  Criterios de aceptacion: Implementa create, get_by_id, list_by_pet, list_by_clinic. Paginacion funcional en list_by_* sin error.
  Validacion: `python -c "from app.infrastructure.repositories.consultation_repository_impl import ConsultationRepositoryImpl; print('OK')"` + revisar codigo.
  Resultado esperado: Repositorio disponible para casos de uso.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T05 - Casos de uso para consulta medica
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-009-01, AC-009-02, AC-009-06, AC-009-11
  Objetivo: Implementar caso de uso create_consultation con validacion de negocio.
  Responsabilidad unica: Si
  Depende de: BE-009-T02, BE-009-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; contrato repositorio; reglas de negocio (solo para completed)
  Contratos usados: AC-009-01, AC-009-02, AC-009-06, AC-009-11
  Entregables: `backend/app/application/use_cases/consultation_use_cases.py`
  Criterios de aceptacion: create_consultation valida appointment.status == completed. Valida rol veterinario por clinica. Errores consistentes (422 invalid input, 409 duplicate).
  Validacion: `pytest backend/app/tests/test_consultation_use_cases.py -q` con coverage >= 80%.
  Resultado esperado: Casos de uso listos para consumo por routers.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T06 - Schemas Pydantic para consultas
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-009-07, AC-009-10
  Objetivo: Definir schemas Pydantic de request para endpoint de consulta.
  Responsabilidad unica: Si
  Depende de: BE-009-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; entidad de dominio; pattern schema de BE-008
  Contratos usados: AC-009-07, AC-009-10
  Entregables: `backend/app/api/schemas/consultation_schemas.py`
  Criterios de aceptacion: Schema ConsultationCreate con validacion de campos requeridos y rangos.
  Validacion: `python -c "from app.api.schemas.consultation_schemas import ConsultationCreate; print('OK')"` + revisar schemas.
  Resultado esperado: Schemas validados disponibles para implementacion de endpoint.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T07 - Endpoint POST de registro de consulta
  Capa: backend
  Tipo: api
  Historia o criterio: AC-009-01, AC-009-02, AC-009-07, AC-009-10
  Objetivo: Exponer endpoint POST para creacion de consultas que responde 201.
  Responsabilidad unica: Si
  Depende de: BE-009-T05, BE-009-T06
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; caso de uso de T05; schemas de T06; pattern router de BE-008 (`backend/app/api/v1/routers/appointment_router.py`)
  Contratos usados: AC-009-01, AC-009-02, AC-009-07, AC-009-10
  Entregables: `backend/app/api/v1/routers/consultation_router.py` (POST), registro en main router.
  Criterios de aceptacion: POST responde 201 con datos de consulta creada. Valida Bearer auth.
  Validacion: `pytest backend/app/tests/api/test_consultations_api.py::test_create_consultation -q` → PASS.
  Resultado esperado: Endpoint de creacion disponible para frontend clinico.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-009-T08 - Endpoints GET listado y detalle de consultas
  Capa: backend
  Tipo: api
  Historia o criterio: AC-009-04, AC-009-05, AC-009-09, AC-009-12
  Objetivo: Exponer endpoint GET de lista paginada.
  Responsabilidad unica: Si
  Depende de: BE-009-T06, BE-009-T07
  Contexto necesario: `docs/opencode/tasks/backend/BE-009.md`; schemas; router pattern de BE-008
  Contratos usados: AC-009-04, AC-009-05, AC-009-09, AC-009-12
  Entregables: GET `/api/v1/consultations` con paginacion en router.
  Criterios de aceptacion: Listado responde con meta paginacion. Filtros de ownership funcionen. Router registrado en app/api/main.py.
  Validacion: `pytest backend/app/tests/api/test_consultations_api.py -q` con unauthenticated=401, authorized=200/201.
  Resultado esperado: Contrato API completo y documentado (OpenAPI).
  Evidencia: pending
  Paralelismo[P]: No

### Frontend

- [ ] FE-009-T01 - Cliente API de consultas
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-009-07, AC-009-09
  Objetivo: Implementar cliente API tipado para operaciones de consulta.
  Responsabilidad unica: Si
  Depende de: BE-009-T07
  Contexto necesario: `docs/opencode/tasks/frontend/FE-009.md`; contrato frontend del plan; endpoint contracts de BE-009
  Contratos usados: AC-009-07, AC-009-09
  Entregables: `frontend/src/shared/api/consultation.ts` (tipado, con fetch wrapper)
  Criterios de aceptacion: Funciones listConsultations(pet_id), getConsultation(id), createConsultation(body). Manejo centralizado de errores HTTP. Typecheck sin errores.
  Validacion: `cd frontend && npx tsc --noEmit` sin errores; typecheck pasa.
  Resultado esperado: Cliente API verificable por componentes y QA.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] FE-009-T02 - Formulario de registro de consulta (veterinario)
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-009-08, AC-009-10
  Objetivo: Implementar formulario clinico para registrar consulta desde agenda veterinaria.
  Responsabilidad unica: Si
  Depende de: FE-009-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-009.md`; flujo UX del plan; contrato POST /consultations
  Contratos usados: AC-009-08, AC-009-10
  Entregables: `frontend/src/app/clinic/appointments/[id]/consultation/page.tsx`, componentes formulario reutilizables.
  Criterios de aceptacion: Campos history, diagnosis, recommendations con validacion inline. Estados loading/submission/success/error consistentes. Validacion frontend de campos requeridos y longitudes max. Typecheck sin errores.
  Validacion: `cd frontend && npm run lint && npm run typecheck` sin errores.
  Resultado esperado: Formulario usable por veterinario para registrar consulta.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] FE-009-T03 - Historial de consultas por mascota (propietario)
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-009-03, AC-009-05, AC-009-09, AC-009-13
  Objetivo: Implementar listado paginado de consultas para una mascota en portal del propietario.
  Responsabilidad unica: Si
  Depende de: FE-009-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-009.md`; flujo UX del plan; contrato GET /consultations?pet_id=
  Contratos usados: AC-009-03, AC-009-05, AC-009-09, AC-009-13
  Entregables: `frontend/src/app/portal/owner/pets/[id]/consultations/page.tsx`, componente ConsultationList.
  Criterios de aceptacion: Listado con paginacion client-side o server-side. Estados UI: loading/success/empty/error consistentes. Responsive mobile-first. Typecheck sin errores.
  Validacion: `cd frontend && npm run lint && npm run typecheck` sin errores.
  Resultado esperado: Historial visualizable por propietario con paginacion.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] FE-009-T04 - Vista detalle de consulta (propietario)
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-009-04, AC-009-13
  Objetivo: Mostrar datos completos de una consulta en solo lectura para el propietario.
  Responsabilidad unica: Si
  Depende de: FE-009-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-009.md`; flujo UX del plan; contrato GET /consultations/{id}
  Contratos usados: AC-009-04, AC-009-13
  Entregables: `frontend/src/app/portal/owner/consultations/[id]/page.tsx`, componente ConsultationDetail.
  Criterios de aceptacion: Campos legibles por propietario (sin jargon clinico sin explicacion). Estado empty si consulta no existe o propietario no tiene permiso. Accesible con labels, contraste y keyboard navigation. Lint sin errores criticos.
  Validacion: `cd frontend && npm run lint` sin errores de accesibilidad critica.
  Resultado esperado: Detalle visualizable por propietario para cada consulta registrada.
  Evidencia: pending
  Paralelismo[P]: No

### QA

- [ ] QA-009-T01 - Validacion QA happy path de consultas
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-009-01, AC-009-03, AC-009-04
  Objetivo: Validar el happy path del flujo de consultas.
  Responsabilidad unica: Si
  Depende de: BE-009-T08, FE-009-T04
  Contexto necesario: plan canonico; `docs/opencode/tasks/qa/QA-009.md`; sidecars `US-009.md`, `UIA-009.md`, `APIA-009.md`; contrato Docker y pruebas
  Contratos usados: AC-009-01, AC-009-03, AC-009-04
  Entregables: Seccion happy path en `docs/opencode/qa/QA-009-results.md` con comandos y salidas.
  Criterios de aceptacion: POST crea consulta 201; owner ve historial paginado; owner ve detalle en solo lectura; evidencia reproducible de cada paso.
  Validacion: `docker compose run --rm backend pytest app/tests/ -q -k consultation` + ejecucion de UIA-009 C1/C2/C3; salida registrada en results.
  Resultado esperado: Happy path PASS con evidencia de API y UI.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-009-T02 - Validacion QA de errores y validaciones
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-009-02, AC-009-06, AC-009-10
  Objetivo: Validar que los negative paths fallan con errores claros sin exponer detalles internos.
  Responsabilidad unica: Si
  Depende de: QA-009-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-009.md`; APIA-009 casos de errores; endpoints del plan
  Contratos usados: AC-009-02, AC-009-06, AC-009-10
  Entregables: Seccion negative path en `docs/opencode/qa/QA-009-results.md` con codigos HTTP y mensajes.
  Criterios de aceptacion: cita no completed → 422; duplicado appointment_id → 409; campo requerido ausente → 422 legible sin detalles internos.
  Validacion: `docker compose run --rm backend pytest app/tests/ -q -k "consultations"` con los casos negativos; salidas registradas en results.
  Resultado esperado: Negative paths PASS con errores consistentes y sin filtracion de datos internos.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-009-T03 - Validacion QA de permisos, IDOR/BOLA y authn
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-009-05, AC-009-11, AC-009-12
  Objetivo: Validar los controles de seguridad ante acceso cruzado a consultas.
  Responsabilidad unica: Si
  Depende de: QA-009-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-009.md`; APIA-009 casos IDOR/auth; riesgos del plan
  Contratos usados: AC-009-05, AC-009-11, AC-009-12
  Entregables: Seccion permisos en `docs/opencode/qa/QA-009-results.md`; findings en `docs/opencode/qa/QA-009-findings.md` si hay FAIL.
  Criterios de aceptacion: sin token → 401; vet de otra clinica → 403; owner A no ve mascotas de owner B; respuestas sin datos ajenos expuestos.
  Validacion: `docker compose run --rm backend pytest app/tests/ -q -k "consultations_idor or consultations_auth"`; salidas registradas en results.
  Resultado esperado: Permisos y IDOR/BOLA PASS sin hallazgos OPEN de seguridad.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-009-T04 - Validacion QA de regresion UI y estados
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-009-07, AC-009-08, AC-009-09, AC-009-13
  Objetivo: Validar los estados UI del flujo principal de consultas.
  Responsabilidad unica: Si
  Depende de: QA-009-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-009.md`; UIA-009; contrato frontend del plan
  Contratos usados: AC-009-07, AC-009-08, AC-009-09, AC-009-13
  Entregables: Seccion UI/regresion en `docs/opencode/qa/QA-009-results.md` con capturas textuales o resumen de UI.
  Criterios de aceptacion: formulario con loading/submitting/success/error; listado con loading/success/empty; detalle read-only; flujo principal sin regresion.
  Validacion: `npx playwright test --project=chromium` para UIA-009 + `cd frontend && npm run test && npm run lint && npm run typecheck` sin errores nuevos.
  Resultado esperado: Estados UI y regresion PASS con evidencia de navegador.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-009-T05 - Evidencia de migracion y cierre de reportes QA
  Capa: qa
  Tipo: reporte
  Historia o criterio: AC-009-14
  Objetivo: Validar la migracion Alembic del schema de consultas.
  Responsabilidad unica: Si
  Depende de: QA-009-T02, QA-009-T03, QA-009-T04
  Contexto necesario: `docs/opencode/qa/QA-009-results.md` parcial; `backend/alembic/versions/`; contrato Docker
  Contratos usados: AC-009-14
  Entregables: `docs/opencode/qa/QA-009-results.md` completo con Decision APPROVED/REJECTED y seccion de migracion; `docs/opencode/qa/QA-009-findings.md` solo si hay FAIL.
  Criterios de aceptacion: `alembic upgrade head` y `alembic downgrade -1 && alembic upgrade head` sin errores; results file con Decision y evidencias de todas las areas.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-009 --stage qa` → PASS.
  Resultado esperado: QA-009 APPROVED con evidencias completas o findings registrados.
  Evidencia: pending
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
