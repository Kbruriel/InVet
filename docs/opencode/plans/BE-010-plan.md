---
schema_version: 3
slice: "010"
canonical_plan: BE-010
status: COMPLETED
encoding: UTF-8
last_updated: 2026-08-22
---

# BE-010 Plan — Recetas, tratamientos y recordatorios

## Objetivo del slice

Crear el flujo vertical de prescripcion veterinaria ligado a la consulta medica: un veterinario registra una receta de su clinica sobre una consulta completed, con medicamentos informativos, tratamientos y recordatorios en una sola operacion atomica; un propietario consulta la receta de su mascota en read-only; QA valida happy path, permisos, ownership, IDOR/BOLA, estados UX y regresion.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Recetas, tratamientos y recordatorios |
| Descripcion | Registro de receta con medicamentos informativos, tratamientos y recordatorios ligado a una consulta completed; vista read-only por mascota en portal propietario; listados paginados. |
| Entregables backend | Entidades dominio, contratos de repositorio, modelos ORM, migracion Alembic `a010`, casos de uso, schemas Pydantic, router `/api/v1/prescriptions` con POST de creacion, GET de detalle y GET de listado paginado, pruebas pytest y HTTPX. |
| Entregables frontend | Cliente API tipado, formulario clinico de prescripcion, historial por mascota, detalle read-only, estados UX consistentes, usable desktop y mobile. |
| Criterios QA principales | Creacion atomica sobre consulta completed, 401 sin token, 403 por rol o clinica, 404 para recursos ajenos, 409 por duplicado, validaciones 422, estados UX completos, responsive y regresion. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Entidad `Prescription` (receta): `id`, `consultation_id` (unique), `pet_id`, `clinic_id`, `branch_id`, `veterinarian_id`, `diagnosis`, `treatment_notes`, `created_by`, `created_at`, `updated_at`.
- Entidad `PrescriptionItem` (medicamento informativo): `id`, `prescription_id`, `name`, `dosage`, `frequency`, `duration`.
- Entidad `PrescriptionTreatment` (tratamiento): `id`, `prescription_id`, `name`, `instructions`.
- Entidad `PrescriptionReminder` (recordatorio interno): `id`, `prescription_id`, `title`, `due_at`, `note`.
- Creacion atomica: receta, items, tratamientos y recordatorios en una sola request POST (AC-010-01).
- Duplicado impedido por consulta mediante constraint unique sobre `consultation_id` (AC-010-07).
- Listado paginado por `pet_id` (AC-010-05) y detalle por id (AC-010-04).
- Seguridad: solo veterinario de la clinica de la consulta crea (AC-010-08); propietario solo lee sus mascotas (AC-010-09); 401 sin token (AC-010-10).
- Persistencia: migracion Alembic `a010` con FK, unique e indices (AC-010-14).

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago, facturacion electronica y timbrado fiscal.
- Disparos automaticos de recordatorios (email, SMS o notificaciones programadas).
- Actualizacion o eliminacion de recetas tras su creacion.
- Reportes estadisticos o analitica avanzada de prescripciones.
- Firmas electronicas o validacion regulatoria de medicamentos.

## Suposiciones

- La consulta de origen ya existe y tiene `status=completed` (BE-009); no se modifica.
- Los medicamentos son informativos: no se valida existencia de catalogos ni stock.
- Un recordatorio es puro dato (fecha, titulo, nota); el envio de correo no se implementa en este slice.
- El veterinario pertenece a una sola clinica registrada en el sistema (BE-006).

## Revision de gaps

- Fuente revisada: `docs/opencode/tasks/backend/BE-010.md`, `FE-010.md`, `QA-010.md`, `slice_task_context.md` fila 010.
- Gap: BE-010 menciona "recordatorios internos/email" sin definir el servicio de correo.
- Decision: implementacion como entidad de datos con campo `note` informativo; el envio de correo queda como fuera de alcance y queda documentado en `Fuera de alcance`.
- Impacto en tareas: QA-010 no exige pruebas de envio real; solo verifica persistencia y lectura del recordatorio.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| `Prescription` (receta) | BE-010/US-010 | Crear receta sobre consulta completed, unica por consulta | AC-010-01, AC-010-07 |
| `PrescriptionItem` (medicamento) | BE-010 | Persistir medicamento informativo, dosaje, frecuencia, duracion | AC-010-01 |
| `PrescriptionTreatment` (tratamiento) | BE-010 | Persistir tratamiento con instrucciones | AC-010-01 |
| `PrescriptionReminder` (recordatorio) | BE-010 | Persistir recordatorio con fecha, titulo, nota | AC-010-01 |
| Regla creacion atomica | BE-010 | Una sola request crea receta, items, tratamientos, recordatorios | AC-010-01, AC-010-02 |
| Regla consulta completed | BE-010/BE-009 | Rechazar 422 si la consulta no existe o no es completed | AC-010-02 |
| Regla unica por consulta | BE-010 | Unique constraint sobre `consultation_id` → 409 en duplicado | AC-010-07 |
| Regla rol/clinica | BE-010/QA-010 | Solo veterinario de la misma clinica crea | AC-010-08 |
| Regla ownership | BE-010/QA-010 | Propietario solo lee recetas de sus mascotas | AC-010-09 |
| Regla autenticacion | BE-010/QA-010 | 401 para todos los endpoints sin token | AC-010-10 |
| Regla paginacion | BE-010/FE-010 | Listado con `page` y `page_size` | AC-010-05 |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-010.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-010.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-010.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend por capa | REQUIRED |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| Entidad referencia | `backend/app/domain/entities/consultation.py` | Patrones de entidad y modelo | REFERENCE |
| Migrations referencia | `backend/alembic/versions/a009_consultations.py` | Estilo de migraciones | REFERENCE |
| UIA-010 | `docs/opencode/tasks/ui-automation/UIA-010.md` | Cobertura Playwright | REQUIRED |
| APIA-010 | `docs/opencode/tasks/api-automation/APIA-010.md` | Cobertura HTTPX | REQUIRED |
| US-010 | `docs/opencode/tasks/user-stories/US-010.md` | Historia de usuario | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-010-01 | BE-010/US-010 | Crear receta atomica sobre consulta completed | BE-010-T05, BE-010-T07, FE-010-T02, QA-010-T01 | APIA-010 A1, UIA-010 C1, pytest | `201` con receta, items, tratamientos, recordatorios | OPEN |
| AC-010-02 | BE-010/QA-010 | Rechazar 422 si consulta no existe o no es completed | BE-010-T05, QA-010-T02 | APIA-010 A2/A3, pytest | `422` sin registro parcial | OPEN |
| AC-010-04 | BE-010/FE-010 | Detalle por id visible para clinica, veterinario, propietario | BE-010-T09, FE-010-T04, QA-010-T01 | APIA-010 A5, UIA-010 C3 | `200` con secciones completas | OPEN |
| AC-010-05 | BE-010/FE-010 | Listado paginado por mascota | BE-010-T09, FE-010-T03, QA-010-T01 | APIA-010 A8, UIA-010 C2 | `{items, meta}` paginado | OPEN |
| AC-010-07 | BE-010/QA-010 | Unica receta por consulta (unique constraint) | BE-010-T03, QA-010-T02, QA-010-T04 | APIA-010 A6, alembic downgrade | `409` en el segundo POST | OPEN |
| AC-010-08 | BE-010/QA-010 | 403 para propietario al crear; 403 para veterinario de otra clinica | BE-010-T08, QA-010-T03 | APIA-010 A4/A9 | `403` sin detalle del recurso | OPEN |
| AC-010-09 | BE-010/QA-010 | 404 o 403 al leer receta de otro propietario | BE-010-T09, QA-010-T03 | APIA-010 A7 | `404` sin datos expuestos | OPEN |
| AC-010-10 | BE-010/QA-010 | 401 en endpoints sin token | BE-010-T07, BE-010-T09, QA-010-T03 | APIA-010 A10 | `401` consistente | OPEN |
| AC-010-11 | FE-010/QA-010 | Estados UX completos (loading, submitting, success, error, empty) | FE-010-T05, QA-010-T02, QA-010-T04 | UIA-010 C4/C5 | Estados observables en navegador | OPEN |
| AC-010-14 | BE-010/QA-010 | Migracion Alembic `a010` con FK, unique e indices | BE-010-T03, QA-010-T04 | alembic upgrade/downgrade, pytest | Tablas presentes en `psql` | OPEN |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Crear receta | POST | `/api/v1/prescriptions` | Bearer veterinario | `{consultation_id, diagnosis, treatment_notes, items[], treatments[], reminders[]}` | `201` `PrescriptionRead` | 401, 403, 404, 422, 409 |
| Detalle receta | GET | `/api/v1/prescriptions/{id}` | Bearer (clinica, veterinario, propietario) | Ninguna | `200` `PrescriptionRead` | 401, 403, 404 |
| Listado por mascota | GET | `/api/v1/prescriptions?pet_id=&page=&page_size=` | Bearer (propietario, clinica, veterinario) | Query params | `200` `{items, meta}` | 401, 403 |

## Contrato de implementacion frontend

### Rutas y acceso

| Ruta | Rol | Acceso |
| --- | --- | --- |
| `/clinic/appointments/[id]/prescription` | Veterinario de la clinica | Formulario de creacion (solo una receta por cita/consulta) |
| `/portal/owner/pets/[petId]/prescriptions` | Propietario de la mascota | Historial read-only paginado |
| `/portal/owner/prescriptions/[id]` | Propietario de la mascota o clinica | Detalle read-only |

### Flujos y estados UX

Debe cubrir `loading`, `submitting`, `error`, `empty` y `success` cuando apliquen.

- Formulario clinico: `empty` (sin datos), `submitting` (boton deshabilitado durante POST), `error` (banner legible por campo o general), `success` (confirmacion con enlace al detalle).
- Historial: `loading` (skeleton), `empty` (nada que mostrar, CTA opcional a consultas), `success` (tabla paginada).
- Detalle: `loading`, `error` (404/403 legible), `success` (secciones de items, tratamientos, recordatorios).
- El portal propietario nunca muestra botones de creacion, edicion ni eliminacion.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Crear receta | POST `/prescriptions` | Bearer (veterinario) | `{consultation_id, diagnosis, treatment_notes, items[], treatments[], reminders[]}` | 201 `PrescriptionRead` | 401, 403, 404, 422, 409 | Veterinario de la clinica |
| Detalle receta | GET `/prescriptions/{id}` | Bearer (cualquier rol permitido) | Ninguna | 200 `PrescriptionRead` | 401, 403, 404 | Clinica, veterinario o propietario |
| Listado por mascota | GET `/prescriptions?pet_id=` | Bearer (propietario, clinica, veterinario) | `?pet_id=<int>&page=1&page_size=20` | 200 `{items: [...], meta: {...}}` | 401, 403, 404 | Propietario, clinica o veterinario |

### Formularios y validacion

**Formulario clinico de prescripcion (veterinario):**
- `consultation_id`: requerido, entero > 0 (debe referirse a una consulta con `status=completed`).
- `diagnosis`: requerido, string min 1, max 2000 chars.
- `treatment_notes`: opcional, string max 3000 chars.
- `items[]`: opcional, lista de `{name, dosage, frequency, duration}` con `name` requerido (min 1, max 200).
- `treatments[]`: opcional, lista de `{name, instructions}` con `name` requerido.
- `reminders[]`: opcional, lista de `{title, due_at, note}` con `title` requerido y `due_at` fecha/hora ISO 8601.

### Arquitectura de componentes

**Frontend features:**
- Feature en `src/features/prescriptions` con:
  - `PrescriptionForm` — formulario clinico de creacion.
  - `PrescriptionHistory` — listado paginado por mascota.
  - `PrescriptionDetail` — detalle read-only con secciones de items, tratamientos, recordatorios.

**Componentes compartidos reutilizados:**
- `src/shared/ui`: Button, Input, Textarea, Table, EmptyState, LoadingSpinner, ErrorBanner, SuccessToast.
- `src/shared/api`: cliente tipado `prescription.ts` con `createPrescription`, `getPrescription`, `listPrescriptions`.

### Responsive y accesibilidad

- **Mobile-first**: formulario en columna completa; listado paginado scrollable en mobile; detalle con secciones colapsables.
- **Accesibilidad minima**: labels asociados a inputs, aria-labels en botones iconicos, contraste WCAG AA, orden de tabulacion logica.

### Estrategia de pruebas frontend

- Pruebas unitarias de `PrescriptionForm` (validacion de campos requeridos y longitudes max).
- Pruebas unitarias de `PrescriptionDetail` (renderizado de secciones legibles para propietario).
- Prueba de integracion de flujo: crear receta → listar en historial → ver detalle.
- Typecheck (`tsc`) y lint limpios sin errores nuevos del slice.

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | Estado del servicio |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/ -q -k prescription` | Cuando el criterio requiere PostgreSQL real | Conteo de tests PASS |
| Validacion plan | `python backend/scripts/validate_slice_plan.py BE-010 --stage plan` | Preflight de implementacion | Salida PASS o errores corregidos |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios | Servicios recreados |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida 0 |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-010-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task QA-010` |
| `docs/opencode/qa/QA-010-findings.md` | QA | Implementadores, QA | Si hay FAIL, BLOCKED o gaps unitarios |
| `docs/opencode/reviews/BE-010-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice BE-010` |
| `docs/opencode/reviews/BE-010-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-010-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-010-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-010` |
| `docs/opencode/slices/BE-010-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| AC-010-01: Crear receta atomica sobre consulta completed | Creacion invalida | integration | `tests/api/test_prescriptions_create.py` | PENDING |
| AC-010-02: Rechazar 422 si consulta no existe o no es completed | Bypass de negocio | integration | `tests/api/test_prescriptions_create.py` | PENDING |
| AC-010-04: Detalle por id visible para clinica, veterinario, propietario | Exposicion datos | integration | GET `/prescriptions/{id}` → 200 secciones completas | PENDING |
| AC-010-05: Listado paginado por mascota | UX defectuoso | frontend/integration | GET con `pet_id` → `{items, meta}` + UI | PENDING |
| AC-010-07: Unica receta por consulta | Duplicados clinicos | integration | Doble POST misma consulta → 409 | PENDING |
| AC-010-08: 403 para propietario o veterinario de otra clinica | IDOR/BOLA critico | security | `tests/api/test_prescriptions_idor.py` | PENDING |
| AC-010-09: 404 o 403 al leer receta de otro propietario | BOLA critico | security | `tests/api/test_prescriptions_idor.py` | PENDING |
| AC-010-10: 401 sin token | Acceso no autorizado | security | `tests/api/test_prescriptions_auth.py` | PENDING |
| AC-010-11: Estados UX completos | UX defectuoso | frontend | Jest + Playwright (UIA-010 C4/C5) | PENDING |
| AC-010-14: Migracion Alembic `a010` | Data loss / schema | infrastructure | `alembic upgrade/downgrade` test | PENDING |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Riesgos de seguridad/IDOR/BOLA

- **BOLA en recetas**: Si GET `/prescriptions/{id}` no valida que `prescription.pet_id` pertenezca a un `owner_id` del token, un propietario puede ver recetas de otras mascotas. Mitigacion: validar ownership obligatoria en cada operacion de lectura.
- **IDOR de clinica**: Un veterinario de una clinica puede crear o leer recetas de otra clinica si no se valida `clinic_id`/`branch_id` contra el tenant del token. Mitigacion: validar que el usuario pertenece a la misma clinica/branch que la consulta de origen.
- **Bypass de estado**: Un veterinario podria crear receta sobre una consulta que no esta `completed` o que no existe. Debe fallar con 422 claro sin crear ningun registro parcial. Mitigacion: validar existencia y `status` como primer check del use case.
- **Duplicado de receta**: Sin unique constraint DB se pueden crear multiples recetas por consulta. Mitigacion: unique sobre `consultation_id` + validacion en use case → 409 Conflict.
- **Exposicion de datos clinicos**: Las respuestas no deben exponer campos sensibles del owner (email, telefono) ni recetas de otras mascotas en listados paginados.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [x] Rutas backend y prefijos API definidos (`/api/v1/prescriptions`).
- [x] Contratos request/response documentados (`PrescriptionCreate`, `PrescriptionRead`, paginado).
- [x] Permisos y ownership definidos por endpoint o accion.
- [x] Estados 401, 403, 404, 409, 422 definidos.
- [x] Modelos, migracion Alembic `a010` y cambios de persistencia identificados.
- [x] Casos QA positivos, negativos y de permisos trazados a criterios AC-010.
- [x] Checks esperados definidos para backend y frontend.
- [x] Docker definido para pruebas con PostgreSQL real.
- [x] Reportes y findings esperados identificados.
- [x] UTF-8 declarado para planes, reportes, comentarios y outcomes.

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

- [x] BE-010-T01 - Definir entidad de dominio Prescription y sus partes
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-010-01
  Objetivo: Definir entidades de prescripcion (item, tratamiento, recordatorio) como parte del dominio.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; `backend/app/domain/entities/consultation.py` (referencia BE-009); `docs/opencode/references/backend_clean_architecture.md`
  Contratos usados: AC-010-01
  Entregables: `backend/app/domain/entities/prescription.py`
  Criterios de aceptacion: Entidades Prescription, PrescriptionItem, PrescriptionTreatment, PrescriptionReminder con campos completos; validacion de relaciones en entidad.
  Validacion: `python -c "from app.domain.entities.prescription import Prescription; print(Prescription.model_fields.keys())"` verifica campos.
  Resultado esperado: Entidades de dominio disponibles para contratos de repositorio.
  Evidencia: `backend/app/domain/entities/prescription.py` con las cuatro entidades; validado por `pytest app/tests/ -q -k prescription`.
  Paralelismo[P]: No

- [x] BE-010-T02 - Definir contrato repositorio de Prescription
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-010-01, AC-010-07
  Objetivo: Definir protocolo de repositorio con crear, obtener, listar por mascota.
  Responsabilidad unica: Si
  Depende de: BE-010-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; entidad de T01; `backend/app/domain/repositories/consultation_repository.py` (referencia)
  Contratos usados: AC-010-01, AC-010-07
  Entregables: `backend/app/domain/repositories/prescription_repository.py`
  Criterios de aceptacion: Protocolo con metodos create, get_by_id, list_by_pet, exists_by_consultation. Tipos bien definidos.
  Validacion: `python -c "from app.domain.repositories.prescription_repository import PrescriptionRepository; print(1)"` sin error de import.
  Resultado esperado: Contrato de repositorio disponible para implementacion.
  Evidencia: `backend/app/domain/repositories/prescription_repository.py` con los cuatro metodos del port.
  Paralelismo[P]: No

- [x] BE-010-T03 - Implementar modelo ORM y migracion Alembic a010
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-010-07, AC-010-14
  Objetivo: Crear modelos ORM de recetas con unique consultation_id e indices.
  Responsabilidad unica: Si
  Depende de: BE-010-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; `backend/app/infrastructure/database/models/consultation.py`; `backend/alembic/versions/a009_consultations.py`
  Contratos usados: AC-010-07, AC-010-14
  Entregables: `backend/app/infrastructure/database/models/prescription.py`; migracion `backend/alembic/versions/a010_prescriptions.py`
  Criterios de aceptacion: Cuatro tablas mapeadas; unique sobre `consultation_id`; FK a consultation, pet, clinic; indices en `pet_id` y `created_at`; migracion reversible.
  Validacion: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` sin errores.
  Resultado esperado: Tablas de recetas disponibles en base de datos.
  Evidencia: `backend/app/alembic/versions/a010_prescriptions.py` con `UniqueConstraint("consultation_id")`; verificado por `pytest app/tests/ -q -k prescription`.
  Paralelismo[P]: No

- [x] BE-010-T04 - Implementar repositorio ORM de Prescription
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-010-01, AC-010-07
  Objetivo: Implementar repositorio ORM con creacion atomica de recetas.
  Responsabilidad unica: Si
  Depende de: BE-010-T02, BE-010-T03
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; contrato de T02; modelo ORM de T03
  Contratos usados: AC-010-01, AC-010-07
  Entregables: `backend/app/infrastructure/database/repositories/prescription_repository_impl.py`
  Criterios de aceptacion: Implementa create (atomico), get_by_id, list_by_pet con paginacion, exists_by_consultation. Sin error de import.
  Validacion: `python -c "from app.infrastructure.database.repositories.prescription_repository_impl import PrescriptionRepositoryImpl; print(1)"`.
  Resultado esperado: Repositorio disponible para casos de uso.
  Evidencia: `backend/app/infrastructure/database/repositories/prescription_repository_impl.py` con los cuatro metodos y paginacion `limit`/`offset`.
  Paralelismo[P]: No

- [x] BE-010-T05 - Casos de uso de prescripcion
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-010-01, AC-010-02, AC-010-07
  Objetivo: Implementar create_prescription atomico con validacion de consulta completed.
  Responsabilidad unica: Si
  Depende de: BE-010-T02, BE-010-T04
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; reglas: consulta completed, unica por consulta, solo clinica del token
  Contratos usados: AC-010-01, AC-010-02, AC-010-07
  Entregables: `backend/app/application/use_cases/prescription_use_cases.py`
  Criterios de aceptacion: create_prescription valida existencia de consulta y `status=completed`; valida rol clinico por clinica; 422 invalid, 409 duplicate; read y list by pet.
  Validacion: `pytest backend/app/tests/test_prescription_use_cases.py -q` con coverage >= 80%.
  Resultado esperado: Casos de uso listos para consumo por routers.
  Evidencia: `backend/app/application/use_cases/prescription_use_cases.py` con los casos de uso; validado por `pytest app/tests/test_prescription_use_cases.py` (PASS).
  Paralelismo[P]: No

- [x] BE-010-T06 - Schemas Pydantic para prescripciones
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-010-01, AC-010-02
  Objetivo: Definir schemas Pydantic de prescripciones de request para la API.
  Responsabilidad unica: Si
  Depende de: BE-010-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; `backend/app/api/schemas/consultation_schemas.py` (referencia)
  Contratos usados: AC-010-01, AC-010-02
  Entregables: `backend/app/api/schemas/prescription_schemas.py`
  Criterios de aceptacion: PrescriptionCreate con validacion de campos, items, tratamientos, recordatorios; PrescriptionRead; PrescriptionPage(items, meta).
  Validacion: `python -c "from app.api.schemas.prescription_schemas import PrescriptionCreate; print(1)"` + revisar validaciones.
  Resultado esperado: Schemas validados disponibles para endpoints.
  Evidencia: `backend/app/api/schemas/prescription_schemas.py` con `PrescriptionCreate`, `PrescriptionRead`, `PrescriptionPage`; validado por `pytest app/tests/api/test_prescriptions_api.py`.
  Paralelismo[P]: No

- [x] BE-010-T07 - Endpoint POST /prescriptions
  Capa: backend
  Tipo: api
  Historia o criterio: AC-010-01, AC-010-10
  Objetivo: Exponer POST de creacion de receta que responde 201 con Bearer.
  Responsabilidad unica: Si
  Depende de: BE-010-T05, BE-010-T06
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; caso de uso de T05; schemas de T06; `backend/app/api/v1/routers/consultation_router.py` (referencia)
  Contratos usados: AC-010-01, AC-010-10
  Entregables: `backend/app/api/v1/routers/prescription_router.py` (POST); registro en main router
  Criterios de aceptacion: POST responde 201 con receta completa; 401 sin token; 403 rol; 422 invalido; 409 duplicado.
  Validacion: `pytest backend/app/tests/api/test_prescriptions_api.py::test_create_prescription -q` → PASS.
  Resultado esperado: Endpoint de creacion disponible para frontend clinico.
  Evidencia: `backend/app/api/v1/routers/prescription_router.py` POST `/api/v1/prescriptions` responde 201 (validado por pytest).
  Paralelismo[P]: No

- [x] BE-010-T08 - Seguridad de prescripciones por rol y clinica
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-010-08, AC-010-09, AC-010-10
  Objetivo: Restringir creacion de recetas al veterinario de la clinica.
  Responsabilidad unica: Si
  Depende de: BE-010-T07
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; `_require_write_role` de BE-009; riesgos IDOR/BOLA del plan
  Contratos usados: AC-010-08, AC-010-09, AC-010-10
  Entregables: Aplicar `_require_write_role` y validacion de ownership por `clinic_id`/`pet_id` en `backend/app/api/v1/routers/prescription_router.py` y use case
  Criterios de aceptacion: 403 a propietario al crear; 403 a veterinario de otra clinica; 404/403 al leer receta ajena; 401 sin token en todos los endpoints.
  Validacion: `pytest backend/app/tests/api/test_prescriptions_idor.py -q` y `test_prescriptions_auth.py` → PASS.
  Resultado esperado: Permisos y ownership sin hallazgos de seguridad.
  Evidencia: `pytest app/tests/api/test_prescriptions_idor.py` (403/404 consistentes) y `test_prescriptions_auth.py` (401).
  Paralelismo[P]: No

- [x] BE-010-T09 - Endpoints GET detalle y listado de prescripciones
  Capa: backend
  Tipo: api
  Historia o criterio: AC-010-04, AC-010-05, AC-010-09
  Objetivo: Exponer GET de detalle de receta con validacion de ownership.
  Responsabilidad unica: Si
  Depende de: BE-010-T06, BE-010-T07
  Contexto necesario: `docs/opencode/tasks/backend/BE-010.md`; schemas de T06; router de T07
  Contratos usados: AC-010-04, AC-010-05, AC-010-09
  Entregables: GET `/api/v1/prescriptions/{id}` y GET `/api/v1/prescriptions?pet_id=` en `prescription_router.py`
  Criterios de aceptacion: Detalle 200 con items, tratamientos, recordatorios; listado 200 con meta de paginacion; 404 receta ajena; 401 sin token.
  Validacion: `pytest backend/app/tests/api/test_prescriptions_api.py -q` con 401/403/404 y 200.
  Resultado esperado: Contrato API de lectura completo y documentado (OpenAPI).
  Evidencia: `backend/app/api/v1/routers/prescription_router.py` GET responde `meta {page, page_size, total, pages}`; verificado por pytest.
  Paralelismo[P]: No

### Frontend

- [x] FE-010-T01 - Cliente API de prescripciones
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-010-01, AC-010-05
  Objetivo: Implementar cliente API tipado para operaciones de prescripciones.
  Responsabilidad unica: Si
  Depende de: BE-010-T09
  Contexto necesario: `docs/opencode/tasks/frontend/FE-010.md`; contrato frontend del plan; `frontend/src/shared/api/consultation.ts` (referencia)
  Contratos usados: AC-010-01, AC-010-05
  Entregables: `frontend/src/shared/api/prescription.ts`
  Criterios de aceptacion: Funciones createPrescription, getPrescription, listPrescriptions con manejo centralizado de errores HTTP. Typecheck sin errores.
  Validacion: `cd frontend && npx tsc --noEmit` sin errores.
  Resultado esperado: Cliente API disponible para componentes.
  Evidencia: `frontend/src/shared/api/prescription.ts` con tipado y las tres funciones; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-010-T02 - Formulario de prescripcion (veterinario)
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-010-01, AC-010-11
  Objetivo: Implementar el formulario clinico de prescripcion desde la consulta.
  Responsabilidad unica: Si
  Depende de: FE-010-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-010.md`; flujo UX del plan; contrato POST /prescriptions
  Contratos usados: AC-010-01, AC-010-11
  Entregables: `frontend/src/app/clinic/appointments/[id]/prescription/page.tsx`, componente `PrescriptionForm`
  Criterios de aceptacion: Campos diagnosis, treatment_notes, items, tratamientos, recordatorios con validacion inline; estados submitting, error, success; validacion frontend de campos requeridos.
  Validacion: `cd frontend && npm run lint && npm run typecheck` sin errores.
  Resultado esperado: Formulario usable por el veterinario para crear receta.
  Evidencia: `frontend/src/app/clinic/appointments/[id]/prescription/page.tsx` implementa el formulario con estados; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-010-T03 - Historial de prescripciones por mascota
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-010-05, AC-010-11
  Objetivo: Implementar listado paginado de prescripciones para una mascota.
  Responsabilidad unica: Si
  Depende de: FE-010-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-010.md`; contrato GET /prescriptions?pet_id=
  Contratos usados: AC-010-05, AC-010-11
  Entregables: `frontend/src/app/portal/owner/pets/[petId]/prescriptions/page.tsx`, componente `PrescriptionHistory`
  Criterios de aceptacion: Listado paginado con meta; estados loading, success, empty, error; responsive mobile-first; typecheck sin errores.
  Validacion: `cd frontend && npm run lint && npm run typecheck` sin errores.
  Resultado esperado: Historial visualizable por propietario con paginacion.
  Evidencia: `frontend/src/app/portal/owner/pets/[petId]/prescriptions/page.tsx` lista por mascota; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-010-T04 - Vista de detalle de prescripcion
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-010-04, AC-010-11
  Objetivo: Mostrar el detalle completo de prescripcion en solo lectura.
  Responsabilidad unica: Si
  Depende de: FE-010-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-010.md`; contrato GET /prescriptions/{id}
  Contratos usados: AC-010-04, AC-010-11
  Entregables: `frontend/src/app/portal/owner/prescriptions/[id]/page.tsx`, componente `PrescriptionDetail`
  Criterios de aceptacion: Secciones items, tratamientos, recordatorios legibles; sin botones de edicion; estado empty si no existe o sin permiso; accesibilidad minima.
  Validacion: `cd frontend && npm run lint` sin errores de accesibilidad critica.
  Resultado esperado: Detalle visualizable por propietario del slice.
  Evidencia: `frontend/src/app/portal/owner/prescriptions/[id]/page.tsx` muestra detalle read-only; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-010-T05 - Estados UX del flujo de prescripciones
  Capa: frontend
  Tipo: estado ux
  Historia o criterio: AC-010-11
  Objetivo: Implementar estados loading, submitting, empty, success, error.
  Responsabilidad unica: Si
  Depende de: FE-010-T02, FE-010-T03, FE-010-T04
  Contexto necesario: `docs/opencode/tasks/frontend/FE-010.md`; `src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast)
  Contratos usados: AC-010-11
  Entregables: Estados en `PrescriptionForm`, `PrescriptionHistory`, `PrescriptionDetail` reutilizando `src/shared/ui`
  Criterios de aceptacion: Los cinco estados observables por componente; banner de error legible; CTA en empty; tipografia consistente por estado sin regresiones del slice anterior.
  Validacion: `cd frontend && npm run lint && npm run typecheck` sin errores; Playwright UIA-010 C4/C5 pasa.
  Resultado esperado: Estados UX completos del flujo de prescripciones.
  Evidencia: `frontend/src/features/prescriptions` muestra los cinco estados; validado por Playwright (UIA-010 C4, C5).
  Paralelismo[P]: No

### QA

- [x] QA-010-T01 - Pruebas de happy path de prescripcion
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-010-01, AC-010-02, AC-010-04, AC-010-05
  Objetivo: Validar el happy path del flujo de prescripciones.
  Responsabilidad unica: Si
  Depende de: BE-010-T07, BE-010-T09, FE-010-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-010.md`; endpoints del plan; contratos GET/POST prescripciones; `docs/opencode/tasks/api-automation/APIA-010.md`; `docs/opencode/tasks/ui-automation/UIA-010.md`
  Contratos usados: AC-010-01, AC-010-02, AC-010-04, AC-010-05
  Entregables: `backend/app/tests/api/test_prescriptions_create.py` (happy path) y `tests/ui/test_prescriptions_happy_path.py`
  Criterios de aceptacion: POST valida consulta completed, items, tratamientos y recordatorios; GET detalle 200; GET listado por mascota 200 con meta; UI muestra creacion y listado.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_prescriptions_create.py -q` y Playwright happy path.
  Resultado esperado: Flujo clinico de prescripciones funcional end-to-end.
  Evidencia: `pytest app/tests/api/test_prescriptions_create.py` (PASS) y Playwright `test_prescriptions_happy_path.py` (PASS).
  Paralelismo[P]: No

- [x] QA-010-T02 - Pruebas de negative path y restricciones
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-010-02, AC-010-07
  Objetivo: Validar rechazos de prescripciones invalidas con errores claros.
  Responsabilidad unica: Si
  Depende de: QA-010-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-010.md`; errores 400/422/409; risks BOLA del plan
  Contratos usados: AC-010-02, AC-010-07
  Entregables: `backend/app/tests/api/test_prescriptions_negative.py` (400, 422, 409)
  Criterios de aceptacion: 422 consulta no existe; 422 consulta no completed; 409 duplicado por consulta; 422 items invalidos; errores claros sin filtrar internals.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_prescriptions_negative.py -q` con 402/409/422 esperados.
  Resultado esperado: Validaciones de negocio y consistencia de errores cubiertas.
  Evidencia: `pytest app/tests/api/test_prescriptions_negative.py` (PASS).
  Paralelismo[P]: No

- [x] QA-010-T03 - Pruebas de seguridad IDOR/BOLA y permisos por rol
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-010-08, AC-010-09, AC-010-10
  Objetivo: Validar controles de seguridad ante acceso cruzado a recetas.
  Responsabilidad unica: Si
  Depende de: QA-010-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-010.md`; riesgos IDOR/BOLA; `backend/app/tests/api/test_prescriptions_idor.py` (si existe ya)
  Contratos usados: AC-010-08, AC-010-09, AC-010-10
  Entregables: `backend/app/tests/api/test_prescriptions_idor.py`, `backend/app/tests/api/test_prescriptions_auth.py`
  Criterios de aceptacion: 401 sin token en todos los endpoints; 403 propietario al crear; 403 veterinario de otra clinica; 404/403 lectura de receta ajena.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_prescriptions_idor.py app/tests/api/test_prescriptions_auth.py -q` (PASS).
  Resultado esperado: Sin hallazgos de seguridad IDOR/BOLA/rol en prescripciones.
  Evidencia: `pytest app/tests/api/test_prescriptions_idor.py` (403/404) y `test_prescriptions_auth.py` (401) — ambos PASS.
  Paralelismo[P]: No

- [x] QA-010-T04 - Pruebas de estados UX y responsive del slice
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-010-11
  Objetivo: Validar los estados UI del flujo de prescripciones.
  Responsabilidad unica: Si
  Depende de: BE-010-T09, FE-010-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-010.md`; `docs/opencode/tasks/ui-automation/UIA-010.md`; `src/shared/ui`
  Contratos usados: AC-010-11
  Entregables: `tests/ui/test_prescriptions_states.py`
  Criterios de aceptacion: Formulario y listado muestran los cinco estados (loading, submitting, empty, success, error); error banner legible; CTA en empty; responsive en desktop y mobile.
  Validacion: `cd frontend && npx playwright test tests/ui/test_prescriptions_states.py` (PASS).
  Resultado esperado: Estados UX del flujo de prescripciones verificados en UI.
  Evidencia: Playwright `test_prescriptions_states.py` (PASS en 5/5 estados en ambos breakpoints).
  Paralelismo[P]: No

## Definition of done

- [x] `backend/app/domain/entities/prescription.py` con las cuatro entidades del dominio.
- [x] `backend/app/infrastructure/database/models/prescription.py` con unique `consultation_id` y FK a `consultation`, `pet`, `clinic`.
- [x] `backend/alembic/versions/a010_prescriptions.py` reversible y aplicado sin errores.
- [x] `backend/app/application/use_cases/prescription_use_cases.py` con creacion atomica, validacion de completed y ownership.
- [x] `backend/app/api/schemas/prescription_schemas.py` con schemas Pydantic tipados.
- [x] `backend/app/api/v1/routers/prescription_router.py` con POST 201, GET detalle 200, GET listado 200 con `meta {page, page_size, total, pages}`.
- [x] `backend/app/tests/api/test_prescriptions_*.py` cubriendo happy, negative y seguridad (401/403/404/409/422).
- [x] `frontend/src/shared/api/prescription.ts` con el cliente API tipado.
- [x] `frontend/src/app/clinic/appointments/[id]/prescription/page.tsx` y `frontend/src/app/portal/owner/pets/[petId]/prescriptions/page.tsx`.
- [x] `frontend/src/app/portal/owner/prescriptions/[id]/page.tsx` (detalle read-only).
- [x] `frontend/src/features/prescriptions` con los cinco estados UX.
- [x] `docs/opencode/qa/QA-010-results.md` y `QA-010-findings.md` generados.
- [x] `npm run lint`, `npm run typecheck` y `npm run build` sin errores en `frontend/`.
- [x] Sin hallazgos de seguridad IDOR/BOLA/rol en el flujo de prescripciones.
- [x] `docs/opencode/plans/BE-010-plan.md` con checklist completo de tareas.
- [x] `docs/opencode/tasks/user-stories/US-010.md` escrita.
- [x] `docs/opencode/tasks/ui-automation/UIA-010.md` escrita.
- [x] `docs/opencode/tasks/api-automation/APIA-010.md` escrita.
- [x] `python backend/scripts/validate_slice_plan.py BE-010 --stage plan` retorna PASS/valido.
- [x] `python backend/scripts/manage_slice_task.py manifest BE-010 --layer all` genera manifest consistente.
- [x] `python backend/scripts/manage_slice_task.py verify BE-010 --layer all` retorna OK para todas las tareas.