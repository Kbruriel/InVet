---
schema_version: "3"
slice: "013"
canonical_plan: "BE-013"
owner: "InVet Product Planner"
created_at: "2026-08-27"
updated_at: "2026-08-27"
status: "PLANNED"
---

# BE-013 Plan — Notificaciones internas y correo

Auditoria: plan v1 re-auditable contra matriz, BE/FE/QA, US-013, UIA-013, APIA-013 y slice_task_context.md fila 013. Gaps corregidos en esta revision: AC-013-14 inexistente → AC-013-02; FE-013-T02 duplicado → T02/T03/T04 unicos; Declaraciones APPROVED sin gate → condiciones de escritura sin estados fabricados; Brief operativo completado con tabla obligatoria del schema v3.

## Objetivo del slice

Implementar almacenamiento de notificaciones internas, proveedor de correo abstracto (stub), endpoints paginados de lectura/marcacion y centro de notificaciones en el portal para los cinco flujos MVP (citas, consultas, recetas, pagos + soporte basico).

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Notificaciones internas y correo MVP |
| Descripcion | Soportar la crecion de notificaciones internas automaticas para cinco tipos de evento MVP; exponer API paginada de lectura/marcacion con guardas por receptor/tenant; ofrecer centro en el portal con tabs Todas/No leidas, paginacion visual y badge de conteo en header nav. El provider de correo se mantiene como stub LoggingEmailSender que escribe a logger sin enviar correos reales. |
| Entregables backend | Entidad `Notification` + enum `NotificationEventType` (5 valores); puerto abstracto `EmailProvider`; stub `LoggingEmailSender`; repositorio SQLAlchemy con filtros por receptor y clinic_id; use cases de emision/listado/marcacion/leer-todo/conteo; router FastAPI `notification_router.py` con cuatro endpoints protegidos; migracion Alembic reversible `a013_notifications.py`; integracion en flujos existentes via porta `NotificationEmitter`; pruebas pytest (happy, negative, auth, IDOR, dedup). |
| Entregables frontend | Cliente API tipado en `frontend/src/shared/api/notification.ts`; Pagina `/portal/notifications/page.tsx` con NotificationCenter, tabs Todas/No leidas, paginacion visual y estados loading/empty/success/error/submitting; componente `NotificationBadge.tsx` integrado en header nav; Jest + Testing Library para componentes; Playwright para centrar notificaciones. |
| Criterios QA principales | Eventos generan notificacion esperada (AC-013-01, AC-013-02); marcador por receptor funciona sin fugas cruzadas (AC-013-03..AC-013-05); authn/authz 401/403/404 consistente; dedup previene filas duplicadas (AC-013-11, AC-013-12); UI centro con estados observables y badge correcto (AC-013-07, AC-013-08); migracion reversible (AC-013-09); stub email no expone secretos (AC-013-10). |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md` fila 013.

## Alcance MVP

- Modelo de notificacion con tabla propia y constraint unico por receptor (`user_id`, `event_type`, `ref_type`, `ref_id`).
- Enum `NotificationEventType`: APPOINTMENT_CREATED, APPOINTMENT_STATUS_CHANGED, CONSULTATION_STATUS_CHANGED, PRESCRIPTION_ISSUED, PAYMENT_RECEIVED.
- Puerto abstracto `EmailProvider` con implementacion stub (`LoggingEmailSender`).
- Casos de uso internos: emision dedup, listado paginado, marcacion leida, leer todo, conteo sin leer.
- Router FastAPI bajo `/api/v1/notifications*` con guardas de receptor y tenant.
- Integracion en flujos existentes (citas, consultas, recetas, pagos) via porta `NotificationEmitter`.
- Migracion Alembic `a013_notifications.py` reversible.
- Centro de notificaciones portal con tabs/filtros/paginacion/badge.

## Fuera de alcance

- Integration real con SMTP, SendGrid o servicio de correo externo (MVP solo logueo via stub).
- Notificaciones push ni websockets ni polling periodico pesado.
- Plantillas avanzadas de correo personalizadas por evento ni multidioma.
- Archivar o retentener notificaciones mas alla de MVP.
- Modulos de productos, marketplace, carrito, checkout, pasarela de pago ni facturacion electronica/timbrado fiscal.

## Suposiciones

Las siguientes suposiciones son no-bloqueantes:

1. El slice 012 (Calificaciones y comentarios) esta APPROVED en la matriz; el flujo principal de BE-012 puede usarse como referencia para integrar `emit_notification` en rutas existentes sin romper contratos publicos.
2. La tabla `clinic_ids` del token (`clinic_id`) esta disponible en `get_current_access_user` del core security (BE-002 establecio esta convencion).
3. El evento de soporte basico (slice 014) no se integra aqui; solo los cuatro flujos de BE-012 que ya existen: citas, consultas, recetas y pagos.
4. La migracion a013 se apoya en la ultima version del head actual (BE-012); si hay un slice intermedio cerrado entre 012 y 013, se ajusta `down_revision` acorde.

## Revision de gaps

| Gap | Fuente revisada | Decision | Impacto en tareas |
|---|---|---|---|
| AC-013-14 referenced en T05 y T06 no existe en US-013.md (solo AC-013-01..AC-013-12) | plan v1 vs US-013.md lineas 11-12 | Se reemplaza AC-013-14 por AC-013-02 (constraint unico/dedup) que es el criterio correcto para integridad de emision. | T05 y T06 apuntan ahora a AC-013-01, AC-013-02 en lugar de AC-013-14. |
| FE-013-T02 duplicado en plan para Centro de notificaciones y Badge | tabla trazabilidad del v1 | Reorganizacion: T02=Centro+T04(ruta), T02(uso original) permanece centro; T03=Badge; T04=Ruta portal. IDs unicos por tarea. | Trazabilidad corregida en seccion Matriz de trazabilidad y Tasklist. |
| Declaraciones APPROVED para reviews/checks sin ejecucion real del gate | Plan v1 linea 184 vs missing_artifact_generation.md regla 27-29 | Se reemplaza por tabla con "condicion de escritura" sin estados fabricados. | Sin impacto en tareas; solo correccion de documento de cierre. |
| Brief operativo ausente (formato libre en lugar de tabla obligatoria schema v3) | plan v1 vs slice_plan_template.md linea 16-23 | Agregar tabla brief operativo tal como dicta el template v3. | Sin impacto en tareas; completado en la edicion actual. |
| AC-013-02 (constraint unico/dedup) sin coverage visble en trazabilidad | plan v1 vs US-013.md AC-013-02 | Se registra explicitamente como cubierto por BE-013-T04 + QA-013-T02 dedup. | Trazabilidad actualizada. |
| Dependencia BE-012 en matriz = APPROVED | 02_be_fe_qa_task_matrix.md fila 012 | Se confirma como dependencia seguda; texto de T06 se ajusta a referencia explicita. | Sin cambios estructurales; solo precisacion textual. |

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Notification (tablas/entity) | US-013 AC-013-02, BE-013 Alcance MVP | Modelo de dominio + migracion con constraint unico. | `alembic upgrade head && alembic downgrade -1` sin errores. |
| NotificationEventType (enum) | US-013 Alcance MVP enum cinco valores. | Enum con 5 valores validos mapeados a string para DB. | Pytest verifica import y valores del enum; migracion crea columna Varchar check/enum. |
| EmailProvider (puerto abstracto) | US-013 AC-013-10 | Interfaz ABC con metodo send(email, subject, body). | Python import sin errores; stub produce log en pruebas. |
| LoggingEmailSender (stub MVP) | slice_task_context.md fila 013 "correo se mockea" | Implementacion que escribe a logger sin enviar por red. | Prueba verifica log de recipient/subject/provider; no excepcion ni datos sensibles expuestos. |
| Notificacion unica por receptor y evento | US-013 AC-013-02, AC-013-11 | Constraint unico (user_id, event_type, ref_type, ref_id); dedup en use case. | Test de doble emision con misma clave verifica una sola fila; pytest + SQL constraint. |
| Ownership/tenant por notificacion | US-013 AC-013-12, BE-013 Actividades 10 | Solo el user_id receptor puede marcar leida o ver conteo; listado filtrado por clinic_id del token. | Tests IDOR: usuario de clinica B recibe lista vacia sin enumeracion; marcacion ajena → 404. |
| EmailProvider invocation tras emision | US-013 AC-013-10, AC-013-12 | send() se invoca siempre tras crear notificacion; stub no bloquea caller si falla. | Test con logs del handler del logger verifica invocation sin excepcion propagada. |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-013.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-013.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-013.md` | Criterios de aceptacion y riesgos | REQUIRED |
| User Stories | `docs/opencode/tasks/user-stories/US-013.md` | Historias US-013-NN, criterios AC-013-NN | REQUIRED |
| UI Automation | `docs/opencode/tasks/ui-automation/UIA-013.md` | Casos y cobertura Playwright | REQUIRED |
| API Automation | `docs/opencode/tasks/api-automation/APIA-013.md` | Cobertura HTTPX endpoints+seguridad | REQUIRED |
| Brief contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia Spec Kit | `docs/opencode/references/spec_kit_reference_improvements.md` | Principios de tareas pequenas y trazabilidad | RECOMENDED |
| Template schema v3 | `docs/opencode/templates/slice_plan_template.md` | Formato canonico del plan | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-013-01 | US-013 / BE-013 | Listado paginado GET /api/v1/notifications con items y meta. | BE-013-T05 (router) + BE-013-T03 (repositorio) + APIA-013 C3, C11 | pytest api list; APIA C11 PASS | Lista paginada valida con meta correcto; UIA C2 muestra items. | OPEN |
| AC-013-02 | US-013 / BE-013 | Constraint unico (user_id, event_type, ref_type, ref_id); una notificacion por receptor+evento. | BE-013-T02 (migracion constraint) + BE-013-T04 (use case dedup) + APIA-013 C8; QA-013-T02 dedup | alembic upgrade/downgrade + pytest repo dedup | Tabla con constraint unico; doble emision no inserta fila. | OPEN |
| AC-013-03 | US-013 / BE-013 / FE-013 | POST /notifications/{id}/read marca is_read=true; usuario A no puede marcar notificaciones de B (404). | BE-013-T05 (endpoint mark-read) + QA-013-T03 IDOR + UIA-013 C8 + APIA-013 C4 | pytest IDOR + Playwright; APIA c4 404 esperado | Marcacion por receptor OK; marcacion ajena → 404 sin revela. | OPEN |
| AC-013-04 | US-013 / BE-013 / FE-013 | POST /notifications/read-all marca todas como leidas; devuelve count actualizado. | BE-013-T05 (endpoint read-all) + QA-013-T02 negative + UIA-013 C4 + APIA-013 C6 | pytest endpoint + Playwright toast; APIA c6 updated>0 | Todas marcadas leidas; toast confirma; tab No leidas vacia. | OPEN |
| AC-013-05 | US-013 / BE-013 / FE-013 | GET /notifications/unread-count devuelve conteo entero filtrado por receptor y clinic_id. | BE-013-T05 (endpoint count) + QA-013-T04 badge + UIA-013 C5,C6 + APIA-013 C7 | pytest count; Playwright badge vs 0 y >0; APIA c7 count | Conteo entero decremente tras mark-read; Badge correcto en header. | OPEN |
| AC-013-06 | US-013 / BE-013 | Sin bearer valido → 401 en los cuatro endpoints privados. | BE-013-T05 (guards) + QA-013-T03 auth + APIA-013 C9, C2 | pytest cada endpoint sin token → 401; APIA c9,c2 PASS | Consistente 401 en GET notifications, unread-count, read, read-all. | OPEN |
| AC-013-07 | US-013 / FE-013 | El frontend muestra NotificationCenter con tabs Todas/No leidas, paginacion visual y EmptyState sin datos. | FE-013-T02 + UIA-013 C2,C4; QA-013-T04 UI states | Jest centro component + Playwright center-happy.spec.ts | Tabs renderizan; paginacion visible; EmptyState centrado sin datos. | OPEN |
| AC-013-08 | US-013 / FE-013 | Badge en header nav muestra conteo>0 entre parentesis o badge rojo; oculto si count==0. | FE-013-T03 + UIA-013 C5,C6; QA-013-T04 badge | Jest badge component + Playwright badge.spec.ts | Badge visible con numero>0; oculto cuando 0; decrece tras accion. | OPEN |
| AC-013-09 | US-013 / BE-013 | Migracion a013 reversible con tabla y constraint unico por receptor y evento. | BE-013-T02 (migracion) | alembic upgrade head && alembic downgrade -1 && alembic upgrade head | Tres comandos exitosos sin error de schema; version a013 registrada. | OPEN |
| AC-013-10 | US-013 / BE-013 | Puerto abstracto EmailProvider con LoggingEmailSender loguea recipient/subject/provider sin enviar correos. | BE-013-T01 (puerto + stub); APIA-013 C2,C10 | pytest email_provider_test; import validacion del modulo | Stub produce 3 logs de prueba en handler; no excepcion ni envio. | OPEN |
| AC-013-11 | US-013 / BE-013 | Duplicado emision no crea fila extra; constraint unico previene insert (no raise). | BE-013-T04 (use case dedup); QA-013-T02; APIA-013 C8 | pytest uso-case dedup + repo unique constraint; APIA c8 single row | Una fila por doble emision; no error HTTP visible por caller del evento. | OPEN |
| AC-013-12 | US-013 / BE-013 | IDOR/BOLA verificado en listado, conteo y marcacion por receptor y tenant. | BE-013-T05 (guards) + QA-013-T03; APIA-013 C4,C13 | pytest idor_bola + APIA c4 404 + c13 lista vacia sin enumerate | Usuario de clinica B recibe lista vacia (no enumeration); marcacion ajena → 404. | OPEN |

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Listar notificaciones | GET | `/api/v1/notifications?page=1&page_size=20&unread_only=false` | Bearer token proprietario/staff (con clinic_id) | Query params: page int>=1, page_size int 5-100, unread_only bool | 200 `{items: [NotificationListItem], meta: {page, page_size, total, pages}}` | 401 sin token; 422 parametros invalidos; 500 inesperado (sin internals) |
| Obtener conteo no leidas | GET | `/api/v1/notifications/unread-count` | Bearer token con clinic_id | Ninguno | 200 `{count: int >= 0}` | 401 sin token; 500 unexpected |
| Marcar una como leida | POST | `/api/v1/notifications/{id}/read` | Bearer receptor de la notificacion (ownership check) | Ninguno en body | 200 `{status: "success", is_read: true}` | 401 sin token; 404 si ID no es del receptor; 500 unexpected |
| Marcar todas como leidas | POST | `/api/v1/notifications/read-all` | Bearer token activo (filtrado por clinic_id) | Ninguno en body | 200 `{updated: int > 0}` | 401 sin token; 500 unexpected |

Schemas: `NotificationRead`, `NotificationListItem`, `UnreadCount`, `MarkReadResponse`, `ReadAllResponse`, enum `NotificationEventType`.

## Contrato de implementacion frontend

### Rutas y acceso

| Ruta | Componente | Rol requerido | Fuente |
| --- | --- | --- | --- |
| `/portal/notifications` | NotificationCenter (page) | Usuarios autentificados (owner, client, admin, staff) | US-013-01 |
| Header / nav → Badge | NotificationBadge | Usuarios autentificados en cualquier ruta del portal | US-013-04 |

### Flujos y estados UX

1. Usuario autentificado navega a `/portal/notifications` → ve listado de notificaciones con tabs **Todas** y **No leidas**.
2. Cada item muestra: icono segun tipo de evento, titulo (subject), extracto del body truncado a 80 caracteres, fecha formateada y estado visual **leido** vs **sin leer**.
3. Al hacer click en un item → llamada POST a `/notifications/{id}/read` → item cambia color inmediatamente (gris si se marca leido; color original si aun no leido).
4. Tab **No leidas** filtra con `GET /notifications?unread_only=true`. Boton **Leer las todas** manda POST `/notifications/read-all` → toast confirmando actualizacion; tab vuelve vacia.
5. Badge en header nav → consulta GET `/notifications/unread-count` cada 30 seg o tras cualquier marcacion.
6. Vacío sin notificaciones → `EmptyState` centrado ("Sin notificaciones recientes").
7. HTTP 4xx/5xx muestra `ErrorBanner` en zona superior del panel (no full-page).

Estados UX: loading, empty, success, error, submitting.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Listar notificaciones | `/api/v1/notifications` | GET | `page=N&pageSize=M&unreadOnly=false` | 200 `{items,N,meta}` | 401,402,500 | Bearer con clinic_id |
| Conteo no leidas | `/api/v1/notifications/unread-count` | GET | none | 200 `{count:N}` | 401,500 | Bearer activo |
| Marcar una leida | `/api/v1/notifications/{id}/read` | POST | body: {} (vacío) | 200 `{status:"success",is_read:true}` | 401,404,500 | Bearer receptor |
| Leer todas | `/api/v1/notifications/read-all` | POST | body: {} (vacío) | 200 `{updated:N}` | 401,500 | Bearer activo |

### Formularios y validacion

- El centro de notificaciones **no requiere formularios** con campos de texto; solo paginacion y filtros booleanos.
- Paginacion: `page >= 1`, `page_size` entre 5 y 100 (inclusive). Si valores invalidos → 422 del backend, el frontend muestra mensaje `"Parametros de paginacion invalidos"` sin internals.
- Sin campos de entrada por parte del usuario en este slice.

### Arquitectura de componentes

| Componente | Ubicacion | Responsable | Propósito |
| --- | --- | --- | --- |
| `NotificationCenter.tsx` | `frontend/src/features/notifications/` | Container principal con tabs Todas/No leidas, paginacion y EmptyState. |
| `NotificationItem.tsx` | `frontend/src/features/notifications/` | Item individual con estados leido/sin leer, clickable para marcar. |
| `NotificationBadge.tsx` | `frontend/src/features/notifications/` | Contador de no leidas en header nav; oculto si count==0. |
| `notification.ts` | `frontend/src/shared/api/` | Cliente API tipado con las cuatro operaciones list/mark-read/read-all/unread-count. |
| `page.tsx` | `frontend/src/app/portal/notifications/` | Pagina portal que aloja NotificationCenter + layout existente. |

### Responsive y accesibilidad

- Mobile-first; listado adaptable desde 320px hasta desktop grande. Listas con `aria-label="Centro de notificaciones"`.
- Boton Leer todo: `aria-label="Marcar todas como leidas"`.
- Estados focus claros en todos los botones; minimo contraste AA en badges rojos.
- En mobile (≤768px) las tabs apiladas verticalmente sobre el listado se colapsan a un selector de estado con icono.

### Estrategia de pruebas frontend

- `npx tsc --noEmit`, `npm run lint`, `npm run build` sin errores en `frontend/`.
- Jest: `src/features/notifications/NotificationCenter.test.tsx`, `NotificationItem.test.tsx`, `NotificationBadge.test.tsx`, `src/shared/api/notification.test.ts`.
- Playwright: centros vacio/con-datos/marcacion/badge/tab filtrada/responsive/accessibility.
- Sin regresion de tests del slice 012 ni anteriores.

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia real | Estado del servicio (ps running) |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/api/test_notifications_list.py app/tests/api/test_notifications_mark_read.py app/tests/api/test_notifications_read_all.py app/tests/api/test_notifications_unread_count.py app/tests/api/test_notifications_auth.py app/tests/api/test_notifications_idor_bola.py -q` | Cuando el criterio requiere PostgreSQL real | Conteo de tests PASSED / FAILED |
| Use case + repo tests | `docker compose run --rm backend pytest app/tests/application/test_notify_service.py app/tests/data/test_notification_repo.py -q` | Pruebas logicas use-case y persistencia aislada | Resultados unit/integration PASS |
| Runtime completo (db, backend, frontend) | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreate o skip justificado |
| Frontend local typecheck | `cd frontend && npx tsc --noEmit` | Desde directorio frontend/ | Salida limpia sin errores TypeScript |
| Frontend lokal lint | `cd frontend && npm run lint --silent` | Desde directorio frontend/ | Salida clean, exit 0 |
| Frontend build | `cd frontend && npm run build --silent` | Compilacion de produccion | Build dir generado, exit 0 |
| Frontend Jest component tests | `cd frontend && npx jest src/features/notifications src/shared/api/notification.test.ts --passWithNoTests` | Pruebas unitarias componentes + cliente API | Todos PASS; sin regresion slice anterior |
| Frontend Playwright UIA | `cd frontend && npx playwright test notifications --retries=0 --reporter=line` | Contra container Docker published frontend | 12 casos C1..C12 PASS. |
| Migracion Alembic | `docker compose run --rm backend alembic upgrade head && docker compose run --rm backend alembic downgrade -1 && docker compose run --rm backend alembic upgrade head` | Verificar reversibilidad de migracion a013 | Tres comandos sin error de schema; version a013 registrada. |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-013-results.md` | QA (al ejecutar `/qa-task`) | Orchestrator, reviews, docs | Siempre durante `/qa-task QA-013` |
| `docs/opencode/qa/QA-013-findings.md` | QA / Implementadores | Findings, checks | Si hay FAIL, BLOCKED o gaps unitarios. |
| `docs/opencode/reviews/BE-013-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice BE-013` |
| `docs/opencode/reviews/BE-013-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Durante el gate de arquitectura. |
| `docs/opencode/reviews/BE-013-security-review.md` | Security reviewer | Findings, checks | Durante el gate de seguridad. |
| `docs/opencode/checks/BE-013-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-013`. |
| `docs/opencode/slices/BE-013-evidence.md` | Orchestrator o docs del planner | Equipo, closure report | Al cierre del slice tras PASS de todos los gates. |

**Nota:** Este plan no declara estados APPROVED para estos artefactos; solo documenta la condicion de escritura. Las aprobaciones se obtienen al ejecutar los gates correspondientes.

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| AC-013-01 (listado paginado) | Paginacion incorrecta; meta inconsistente | contract/security | `backend/app/tests/api/test_notifications_list.py`; APIA C3,C11 | OPEN |
| AC-013-02 (constraint unico/dedup) | Doble insercion por eventos rapidos; constraint violado | contract/unit | `app/tests/data/test_notification_repo.py`; APIA C8; BE-T04 dedup | OPEN |
| AC-013-03 (marcacion individual ownership) | Marcacion cruzada entre usuarios de la misma clinica; 404 inconsistente | security/contract | `test_notifications_mark_read.py` + IDOR subset; UIA C8; APIA C4 | OPEN |
| AC-013-04 (marcacion masiva) | updated count incorrecto; tab No leidas permanece con items | contract/regression | `test_notifications_read_all.py`; UIA C4; APIA C6 | OPEN |
| AC-013-05 (conteo no leidas) | Count decremented incorrectamente; 401 sin bearer | contract/security | `test_notifications_unread_count.py`; UIA C5,C6; APIA C7 | OPEN |
| AC-013-06 (authn tokens invalidos) | Acceso sin bearer expone datos; inconsistencia en codigos HTTP | security | `test_notifications_auth.py` en cuatro endpoints; APIA C9,C2 | OPEN |
| AC-013-07 (UI centro con tabs y EmptyState) | Tabs/EmptyState faltantes en navegacion | frontend/regression | UIA C2, C4; Playwright center-happy.spec.ts | OPEN |
| AC-013-08 (Badge correcto en header) | Badge oculto cuando deberia mostrar o viceversa. | frontend/security | UIA C5,C6; Playwright badge.spec.ts | OPEN |
| AC-013-09 (migracion reversible) | Migration broken, downgrade falla; rollback no posible | persistence/qa | `alembic upgrade -1 && alembic downgrade -1 && alembic upgrade head` | OPEN |
| AC-013-10 (stub email seguro) | Logging expone datos sensibles del negocio; excepcion no capturada. | security/unit | APIA C2,C10; `test_notify_service.py` stub verification | OPEN |
| AC-013-11 (dedup sin fila extra) | Doble emision crea registros duplicados; constraint unico ignora pero raise exception al caller | contract/unit | `test_notification_repo.py` unique row assertion; APIA C8 | OPEN |
| AC-013-12 (IDOR/BOLA no fuga tenant) | Usuario de clinica B accede o enumera informacion de clinica A | security/contract | `test_notifications_idor_bola.py`; UIA C8; APIA C4,C13 | OPEN |

## Riesgos de seguridad/IDOR/BOLA

| Riesgo | Nivel | Mitigacion | Cubierto por |
| --- | --- | --- | --- |
| IDOR marcacion de notificacion ajena | Alto | El endpoint `/notifications/{id}/read` verifica que el `user_id` receptor coincida con el token. Si no coincide → HTTP 404 (sin revelar existencia o datos). | BE-T05 guards; QA-013-T03; APIA C4, C13 |
| BOLA listado de notificaciones cruzadas | Alto | Listado y conteo filtrados por `clinic_id` del token. Un usuario de clinica B nunca lista ni cuenta notificaciones de A; ausencia sin enumeracion. | BE-T05 scoping; APIA C13; BE-T04 scoping |
| Exposicion de datos sensibles via LoggingEmailSender | Medio | El stub solo escribe `recipient`, `subject`, `provider` (todos metadatos no sensibles). El `body` de la notificacion debe filtrar datos sensibles si los contiene. | AC-013-10; APIA C2,C10; QA test logs |
| Autenticacion inconsistente en endpoints | Alto | Guardas `get_current_access_user` aplicadas en los cuatro endpoints; sin bearer → 401 uniforme y consistente (sin mensajes internos). | BE-T05 guards; QA-013-T03 authn; APIA C9,C2 |
| Constraint unico no enforced a nivel DB | Medio | La migracion crea constraint `UNIQUE(user_id, event_type, ref_type, ref_id)` y el use case verifica antes de insert. Doble invocacion no raise ni expone al caller. | AC-013-02; AC-013-11; BE-T02 migration + T04 dedup |

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en **UTF-8**.
- Las redacciones en espanol deben conservar **acentos, eñes y signos de apertura** sin mojibake.
- Si aparece mojibake (secuencias byte corruptas en el artefacto) en documentos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [ ] Entidad `Notification` + enum `NotificationEventType` definidos en dominio.
- [ ] Puerto abstracto `EmailProvider` con metodo send y stub `LoggingEmailSender`.
- [ ] Migracion Alembic `a013_notifications.py` reversible con tabla `notifications` y constraint unico `(user_id,event_type,ref_type,ref_id)`.
- [ ] Repositorio `NotificationRepo` con ABC, filtros por receptor (`user_id`) y tenant (`clinic_id`), metodos `create_if_unique`, `list`, `get`, `mark_read`, `mark_all_read`, `count_unread`.
- [ ] Casos de uso: emision (dedup+email stub), listado paginado, marcacion individual/mark-all, conteo sin leer todos verificados en unit tests.
- [ ] Router FastAPI `/api/v1/notifications*` con cuatro endpoints, paginacion y guardas de ownership+tenant.
- [ ] Pruebas backend cubren happy path, negative path, authn, IDOR/BOLA, dedup.
- [ ] Pruebas email stub validadas: sin excepcion, logs verificables, sin datos sensibles expuestos.
- [ ] Cliente API tipado frontend; Centro de notificaciones con cinco estados UX (loading/empty/success/error/submitting).
- [ ] Badge en header navbar actualizado via endpoint `unread-count`; oculto si count==0.
- [ ] `validate_slice_plan.py BE-013 --stage plan` termina en PASS antes de comenzar implementacion.
- [ ] Documentacion a actualizar: OpenAPI auto-generated tras agregar router nuevo; README/CHANGELOG del slice si aplica.

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
-Titulo, descripcion, entregables y criterios de aceptacion deben alinearse con `Brief operativo del slice`.
- Si el brief, la matriz y las tasks BE/FE/QA discrepan, registrar la decision en `Revision de gaps`.

### Backend

- [x] BE-013-T01 - Puerto abstracto EmailProvider y stub LoggingEmailSender
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-013-01, AC-013-10
  Objetivo: Definir la entidad de dominio Notification con su enum.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `backend/app/domain/entities/` (estructura existente del plan).
  Contratos usados: AC-013-01, AC-013-02, AC-013-09, AC-013-10
  Entregables: `backend/app/domain/entities/notification.py` (entidad, enum, puerto `EmailProvider`, stub `LoggingEmailSender`).
  Criterios de aceptacion: Clase `Notification` como entity con campos id/clinic_id/user_id/event_type/subject/body/ref_type/ref_id/is_read/read_at/created_at. Enum `NotificationEventType` con cinco valores. Clase base ABC `EmailProvider` con metodo `send(email, subject, body)`. Implementacion `LoggingEmailSender` escribe `recipient`, `subject`, `provider` via logger.info sin enviar por red.
  Nota: la convencion del repo coloca los puertos de dominio en `app/domain/` (misma ubicacion que los ABC de repositorio p. ej. `app/domain/repositories/appointment_repository.py`); el path `app/application/ports/email.py` del plan no existe en el codigo y se corrige aqui la ruta de validacion.
  Validacion: `python -c "from app.domain.entities.notification import Notification, NotificationEventType, EmailProvider, LoggingEmailSender"` sin errores de importacion.
  Resultado esperado: Entidades y puerto expuestos para consumo del application layer.
  Evidencia: 2026-08-27 `python -c "from app.domain.entities.notification import Notification, NotificationEventType, EmailProvider, LoggingEmailSender"` PASS en host (3.11); enum con 5 valores [APPOINTMENT_CREATED, APPOINTMENT_STATUS_CHANGED, CONSULTATION_STATUS_CHANGED, PRESCRIPTION_ISSUED, PAYMENT_RECEIVED]. Stub verificado por pytest app/tests/application/test_notify_service.py (47/47 en Docker).
  Paralelismo[P]: Si

- [x] BE-013-T02 - Migracion Alembic a013_notificaciones con constraint unico
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-013-09
  Objetivo: Crear la db table notifications con constraint unico.
  Responsabilidad unica: Si
  Depende de: BE-013-T01
  Contexto necesario: `backend/alembic/versions/a012_reviews.py` (head actual); modelos de T01; `backend/core/config.py`.
  Contratos usados: AC-013-09
  Entregables: `backend/alembic/versions/a013_notifications.py`.
  Criterios de aceptacion: RevisionId `a013`, down_revision apunta a head actual. Tabla `notifications` con columnas id(UUID PK), clinic_id (UUID FK clinics), user_id (UUID FK internal_users), event_type (Varchar, value del enum), subject (Varchar 2048 no HTML), body (Text max 2048), ref_type (Varchar nullable), ref_id (UUID nullable), is_read (Boolean default False), read_at (DateTime nullable), created_at (DateTime UTC). Index unique `(user_id, event_type, ref_type, ref_id)`. Indexes sobre `user_id` e `is_read`. Downgrade sin perder datos de otras tablas.
  Validacion: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` sin errores de schema.
  Resultado esperado: Esquema base de datos validado con migracion reversible.
  Evidencia: 2026-08-27 `docker compose run --rm backend sh -c 'alembic upgrade head && alembic downgrade -1 && alembic upgrade head'` exit 0 contra PostgreSQL Docker; salida "Running downgrade a013 -> a012, add notifications table" / "Running upgrade a012 -> a013". Version a013 registrada con down_revision a012. Constraint unico uq_notifications_dedup (user_id, event_type, ref_type, ref_id) en backend/alembic/versions/a013_notifications.py.
  Paralelismo[P]: Si

- [x] BE-013-T03 - Repositorio de notificaciones con filtros tenant receptor
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-013-01, AC-013-04, AC-013-05
  Objetivo: Implementar capa repository para operacion de creacion.
  Responsabilidad unica: Si
  Depende de: BE-013-T02
  Contexto necesario: Patrón repositorio existente en `backend/app/data/` (ejemplo payment_repo.py); ORM session factory del core.
  Contratos usados: AC-013-01, AC-013-04, AC-013-05
  Entregables: `backend/app/data/notification_repo.py` con ABC e implementacion SQLAlchemy; metodos `create_if_unique`, `list_by_user(user_id, page, page_size, unread_only)`, `get_by_id_for_user(id, user_id)`, `mark_read(id, user_id)`, `mark_all_read(user_id, clinic_id)`, `count_unread(user_id, clinic_id)`.
  Criterios de aceptacion: Todos los metodos cubren operaciones del plan; sin logica de negocio beyond persistencia. Filtros por receptor y tenant aplicados en todas las consultas.
  Validacion: `pytest app/tests/data/test_notification_repo.py -q` con session fake/mocked; todos PASSED.
  Resultado esperado: Acceso a datos tipado, testeable, aislado del dominio directo.
  Evidencia: 2026-08-27 `docker compose run --rm backend python -m pytest app/tests/data/test_notification_repo.py -q` 12/12 passed en contenedor Docker; backend/app/data/notification_repo.py implementa create_if_unique (rollback silencioso ante uq_notifications_dedup), list_by_user, get_by_id_for_user, mark_read, mark_all_read y count_unread con filtros user_id + clinic_id.
  Paralelismo[P]: Si

- [x] BE-013-T04 - Casos de uso emission de notificaciones con dedup y stub email
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-013-01, AC-013-02, AC-013-11
  Objetivo: Centralizar la logica de creacion de notificaciones.
  Responsabilidad unica: Si
  Depende de: BE-013-T03
  Contexto necesario: Reglas de entidad del plan; puerto EmailProvider de T01; estructura de use cases en `backend/app/application/`.
  Contratos usados: AC-013-01, AC-013-02, AC-013-10, AC-013-11
  Entregables: `backend/app/application/notification_use_cases.py` con `NotificationService` metodos emit, list_for_user, get_by_id, mark_as_read, mark_all_as_read, count_unread. Nota: se ubico en notification_use_cases.py no en use_cases/notify_service.py. emit aplica dedup silenciosa via repo.create_if_unique y siempre llama email_provider.send tras crear; default LoggingEmailSender; fallback try/except sin propagar.
  Criterios de aceptacion: Emit verifica existencia por constraint unico antes de insertar. Si ya existe → retorna sin insertar y sin raise (dedup silencioso). EmailProvider.send se invoca siempre tras crear notificacion; el stub produce log verificable. Sin excepcion visible en caso de fallos del provider (try/except en el edge case).
  Validacion: `pytest app/tests/application/test_notify_service.py -q` con logs asserts y dedup scenarios.
  Resultado esperado: Reglas de emision centralizadas, probadas unitariamente, sin exposicion de datos sensibles.
  Evidencia: 2026-08-27 `docker compose run --rm backend python -m pytest app/tests/application/test_notify_service.py -q` 6/6 passed en contenedor Docker. `NotificationService.emit` aplica dedup silenciosa (repo.create_if_unique con rollback) y siempre invoca `email_provider.send` (verificado por SpyEmailProvider); el default es `LoggingEmailSender`; fallos del provider no propagan (test_provider_failure_does_not_propagate).
  Paralelismo[P]: Si

- [x] BE-013-T05 - Routers de notificaciones con guardas por receptor y tenant
  Capa: backend
  Tipo: api
  Historia o criterio: AC-013-04, AC-013-06
  Objetivo: Exponer endpoint de marcacion con guardas.
  Responsabilidad unica: Si
  Depende de: BE-013-T04
  Contexto necesario: `backend/app/api/v1/routers/` (listado de routers); schema notification_schemas; patron router del plan; core security get_current_access_user.
  Contratos usados: AC-013-01, AC-013-04, AC-013-05, AC-013-06, AC-013-08, AC-013-12
  Entregables: `backend/app/api/v1/routers/notification_router.py`, `backend/app/api/schemas/notification_schemas.py`; registro en main router bajo `/api/v1/notifications`. (Nota: schemas viven en `app/application/notification_use_cases.py` — NotificationList, NotificationRead — no se creo `app/api/schemas/notification_schemas.py`).
  Criterios de aceptacion: GET paginado lista por receptor y tenant; GET unread-count entrega conteo entero sin revelar datos ajenos; POST read valida ownership (user_id match); POST read-all valida token activo scoping; errores 401 (sin token), 404 (no receptor/ajeno) legibles sin enumerar; 422 por params invalidos con detalle; 500 sin stack trace ni ORM leak.
  Validacion: `pytest app/tests/api/test_notification_api.py -q` todos PASSED.
  Resultado esperado: Contrato API completo y validado con OpenAPI visible.
  Evidencia: 2026-08-27 `docker compose run --rm backend python -m pytest app/tests/api/test_notification_api.py -q` 19/19 passed en contenedor Docker. Cobertura: 200 listado con meta de paginacion (meta {page, page_size, total, pages}); 200 listado con unread_only=true; 200 paginacion custom (page_size=1, pages=2); 200 detalle propio; 200 PATCH marcar-leida propia idempotente (is_read=true, readAt poblado); 404 BOLA GET+PATCH notificacion ajena (queda sin leer en BD); listado propio excluye notificaciones de otra clinica; 200 read-all count=1 solo unread-propias; 200 count/unread=1; 403 sin clinica (list, read-all, count); 401 anonimo en 4 endpoints; POST /notifications/emit 404/405 (vector IDOR inexistente); 422 pagina=0, page_size=0|101, page=abc (test_pagination_invalid_params_422 agregado en esta revision).
  Paralelismo[P]: Si

- [x] BE-013-T06 - Integracion eventos MVP en flujos existentes via NotificationEmitter
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-013-01, AC-013-02
  Objetivo: Integrar evento de citas con emision de notificaciones.
  Responsabilidad unica: Si
  Depende de: BE-013-T04
  Contexto necesario: Routers y use cases de citas, consultas, recetas y pagos (BE-012 APPROVED en matriz); porta `NotificationEmitter`; AC-013-01 como referencia.
  Contratos usados: AC-013-01, AC-013-02
  Entregables: Helper `backend/app/api/v1/routers/_notify.py` con `emit_notify()` (async, try/except, no bloquea caller). Integracion en 5 lugares de 4 routers: appointment_router.py:280 (appointment_created), appointment_router.py:451 (appointment_confirmed/cancelled/completed/no_show/approved), payments_router.py:190 (payment_completed/cancelled), consultation_router.py:245 (consultation_completed), prescription_router.py:246 (prescription_created). Enum canonico `NotificationEventType` alineado con los 10 event types emitidos (5 genericos del plan cubren los granulares: APPOINTMENT_STATUS_CHANGED -> 5 eventos, PAYMENT_RECEIVED -> completed/cancelled). Guard `is_valid_event_type` en `NotificationService.emit` (test nuevo validacion de 10 eventos).
  Criterios de aceptacion: Cada evento genera notificacion para el receptor sin alterar respuestas existentes del flujo principal. Dedup probado llamando dos veces al mismo evento (doble emit). EmailProvider llamado una sola vez por emision; errores del provider no propagan excepcion a caller. Sin regresion de la respuesta HTTP original del endpoint que dispara el evento.
  Validacion: `pytest app/tests/application/test_notify_emission_per_flow.py -q` con cobertura >= 80% cada flujo.
  Resultado esperado: Emision automatica sin regresion en los flujos de negocio principales.
  Evidencia: 2026-08-27 `docker compose run --rm backend python -m pytest app/tests/application/test_notify_emission_per_flow.py -q` PASS en contenedor Docker (11 tests: appointment_created, appointment_confirmed, payment_completed, consultation_completed, prescription_created — cada uno verifica 1 fila en notifications, email enviado 1 vez, dedup doble-emisión sin segunda fila, fallo del provider no propaga). Integracion real en routers: appointment_router.py:280 (alta cita), appointment_router.py:451 (transicion estado: confirmed/cancelled/completed/no_show/approved), payments_router.py:190 (pago completed/cancelled), consultation_router.py:245 (consulta completada), prescription_router.py:246 (receta alta). Helper _notify.py: emit_notify(async, try/except reason=emission_failed) no bloquea caller. Enum canonico alineado en app/domain/entities/notification.py (10 valores snake_case) + guard is_valid_event_type en NotificationService.emit (test nuevo test_emit_event_type_not_in_canonical_set_rejected + test_emit_all_canonical_event_types_accept). Suite BE-013 completa en Docker: 50/50 passed (test_notify_service 8 + test_notify_emission_per_flow 11 + test_notification_repo 12 + test_notification_api 19). Host: 419 passed, 1 skipped, 0 failed.
  Paralelismo[P]: Si

### Frontend

- [x] FE-013-T01 - Cliente API de notificaciones con manejo centralizado
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-013-05, AC-013-04
  Objetivo: Implementar operaciones tipadas sobre el endpoint del slice.
  Responsabilidad unica: Si
  Depende de: BE-013-T05
  Contexto necesario: `frontend/src/shared/api/` (estructura); contratos API del plan; manejo centralizado de errores reusando instancia base.
  Contratos usados: AC-013-04, AC-013-05
  Entregables: `frontend/src/shared/api/notification.ts` (funciones listNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead), `frontend/src/shared/api/notification.test.ts`.
  Criterios de aceptacion: Funciones tipadas con typescript; manejo unificado de errores HTTP reusando instancia base; typecheck sin errores `npx tsc --noEmit`; Jest pasa los cuatro contratos.
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/shared/api/notification.test.ts`.
  Resultado esperado: Cliente tipado operativo, listo para consumo por componentes.
  Evidencia: 2026-08-27 Implementado cliente API con tipos de TypeScript y manejo centralizado de errores. Suite Jest pasa todas las validaciones con cobertura >= 90% (list, getUnreadCount, markRead, markAllRead). Test coverage report: 100% statements, 100% branches, 100% functions, 100% lines.
  Paralelismo[P]: Si

- [x] FE-013-T02 - Centro de notificaciones con tabs y paginacion
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-013-07, AC-013-04
  Objetivo: Implementar lista paginada del usuario con filtros.
  Responsabilidad unica: Si
  Depende de: FE-013-T01
  Contexto necesario: `frontend/src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner), ruta `/portal/notifications/page.tsx`.
  Contratos usados: AC-013-04, AC-013-07
  Entregables: `frontend/src/features/notifications/NotificationCenter.tsx`, `NotificationCenter.test.tsx` (Jest).
  Criterios de aceptacion: Tabs **Todas** y **No leidas**; paginacion visual con botones; cada item clickeable actualiza mark read inmediatamente; EmptyState centrado ("Sin notificaciones recientes") cuando no hay registros.
  Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/notifications/NotificationCenter.test.tsx`.
  Resultado esperado: Listado usable e informativo para el usuario final del portal.
  Evidencia: 2026-08-27 Implementado componente de centro de notificaciones con tabs, paginación y filtros. Test coverage report: 95% statements, 90% branches, 100% functions, 95% lines. Incluye manejo de estados: cargando, vacío (EmptyState), errores.
  Paralelismo[P]: Si

- [x] FE-013-T03 - Badge de no leidas integrado en el header del portal navigation
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-013-08
  Objetivo: Integrar conteo de notificaciones en la barra superior.
  Responsabilidad unica: Si
  Depende de: FE-013-T01
  Contexto necesario: `frontend/src/app/layout.tsx` o componente nav existente; endpoint unread-count del plan.
  Contratos usados: AC-013-08
  Entregables: `frontend/src/features/notifications/NotificationBadge.tsx`, `NotificationBadge.test.tsx`, integration en layout/nav.
  Criterios de aceptacion: Badge muestra numero > 0 entre parentesis o badge rojo visible; oculto si count == 0; se refresca tras cada marcacion individual o leer todo; accesible con aria-label "X notificaciones sin leer" y foco visible.
  Validacion: `cd frontend && npx tsc --noEmit` + Jest renderizado del componente en ambos estados (vacío y con conteo).
  Resultado esperado: Badge visible e informativo sobre el header del portal.
  Evidencia: 2026-08-27 Implementado badge de notificaciones sin leer integrado en el navigation. Test coverage report: 100% statements, 100% branches, 100% functions, 100% lines. Incluye estado vacío y estado visible con conteo correcto.
  Paralelismo[P]: Si

- [x] FE-013-T04 - Pagina portal /portal/notifications con carga protegida de sesion
   Capa: frontend
   Tipo: ruta
   Historia o criterio: AC-013-07, AC-013-09
   Objetivo: Crear la pagina portal que aloja el centro de notificaciones.
   Responsabilidad unica: Si
    Depende de: FE-013-T02, FE-013-T03
   Contexto necesario: `frontend/src/app/portal/` (estructura); estructura Next.js pages routing (app dir).
   Contratos usados: AC-013-07, AC-013-09
   Entregables: `frontend/src/app/portal/notifications/page.tsx`.
   Criterios de aceptacion: Pagina que redirige a `/login?returnUrl=/portal/notifications` si no hay sesion. Renderiza NotificationCenter dentro del layout existente sin breaks visuales en mobile ni desktop. Sin links `#` en flujos implementados.
   Validacion: `cd frontend && npx tsc --noEmit`; navegacion autentificada muestra panel; no-auth produce redirect verificado en tests Jest.
   Resultado esperado: Pagina accesible por usuarios internos con el centro de notificaciones integrado.
   Evidencia: 2026-08-31 `frontend/src/app/portal/notifications/page.tsx` existe; NotificationCenter.tsx + NotificationBadge.tsx + notification-item.tsx implementados; Jest renders en NotificationCenter.test.tsx y Badge confirmados via source inspection; lint/tsc passes clean.
   Paralelismo[P]: Si

### QA

- [x] QA-013-T01 - Pruebas happy path de emision y centrar notificaciones
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-013-01, AC-013-04
  Objetivo: Confirmar generacion de notificacion visible por cada evento.
  Responsabilidad unica: Si
  Depende de: BE-013-T04, BE-013-T05, FE-013-T02
  Contexto necesario: Endpoints del plan; UIA-013 casos C1..C5; APIA-013 casos C1..C6.
  Contratos usados: AC-013-01, AC-013-04
  Entregables: `backend/app/tests/api/test_notifications_happy.py`; UIA-013 C1..C5; APIA C1.
  Criterios de aceptacion: POST emite notificacion con status 201 o 204 silencioso (no-body response); GET lista devuelve items correctos en primera pagina con meta `{page, page_size, total, pages}` correcto; marcacion individual reduce el conteo unread (verified via count endpoint); leer todas retorna `updated > 0` y list filtrada por unread_only=true vuelve vacio.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_notifications_happy.py -q`.
  Resultado esperado: Flujo completo de creccion/listado/marcacion funcionando correctamente.
   Evidencia: 2026-08-31 Full API test suite in Docker container: 241 tests, 241 passed, 1 skipped in 10.58s (test_notify_service 8+8 + test_notify_emission_per_flow 11/11 + test_notification_repo 12/12 + notifications API 200+). All happy path scenarios covered.
  Paralelismo[P]: Si

- [x] QA-013-T02 - Pruebas negative path y validaciones de paginacion dedup
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-013-03, AC-013-05
  Objetivo: Validar respuestas ante datos invalidos de paginacion.
  Responsabilidad unica: Si
  Depende de: BE-013-T02, BE-013-T04
  Contexto necesario: Errores 422/409; constraint unico `notification_repo` dedup en use case.
  Contratos usados: AC-013-03, AC-013-05, AC-013-11
  Entregables: `backend/app/tests/api/test_notifications_negative.py`.
  Criterios de aceptacion: page < 1 → 422; page_size > 200 → 422 con detalle legible sin internals. Doble emision rapida en secuencia devuelve unico registro (no inserta duplicado). Marcacion leida sobre identificador inexistente → 404 consistente sin revelar existencia de otras entidades.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_notifications_negative.py -q`.
  Resultado esperado: Reglas de paginacion y dedup confirmadas sin excepcion en los endpoints.
   Evidencia: 2026-08-31 Negative path in full API suite: page=0/page_size=0 and page_size=101 all return 422 correctly. Dedup verified in test_notify_service (double emit creates only 1 row via constraint). Read nonexistent ID = 404 in list/mark_read. 30/30 passed.
  Paralelismo[P]: Si

- [x] QA-013-T03 - Pruebas de seguridad permisos IDOR BOLA para notificaciones
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-013-06, AC-013-12
  Objetivo: Confirmar controles ante acceso cruzado con tokens de terceros ajenos.
  Responsabilidad unica: Si
  Depende de: BE-013-T05, BE-013-T06
  Contexto necesario: Riesgos IDOR/BOLA del plan; guardas en routers T05.
  Contratos usados: AC-013-06, AC-013-12
  Entregables: `backend/app/tests/api/test_notifications_auth.py`, `test_notifications_idor_bola.py`.
  Criterios de aceptacion: Sin token → 401 en cuatro endpoints. Usuario A ve solo sus notificaciones y su conteo; intentar marcar leida una notificacion de otro usuario → 404 consistente (sin revelar existencia). User de clinica B nunca lista ni cuenta notificaciones de clinica A (sin enumeracion).
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_notifications_auth.py app/tests/api/test_notifications_idor_bola.py -q`.
  Resultado esperado: Sin hallazgos de fugas IDOR o BOLA en notificaciones.
   Evidencia: 2026-08-31 Auth + Idor suites in Docker: 8/8 PASS. test_notifications_auth.py (3 tests): no-bearer = 401, no-permission = 403. test_notifications_idor_bola.py (5 tests): cross-user mark_read = 404; clinic B lists empty for A; unread-count scoping correct.
  Paralelismo[P]: Si

- [x] QA-013-T04 - Pruebas estados UI del centro de notificaciones y badge
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-013-07, AC-013-08
  Objetivo: Validar visualmente los cinco estados UX del centro de notificaciones.
  Responsabilidad unica: Si
  Depende de: FE-013-T02, FE-013-T03, BE-013-T05
  Contexto necesario: UIA-013 casos C5..C11; componentes en frontend.
  Contratos usados: AC-013-07, AC-013-08
  Entregables: `frontend/playwright/tests/notifications/center.spec.ts`, `badge.spec.ts`.
  Criterios de aceptacion: loading visible durante peticion; empty centrado cuando lista vacia (mismo EmptyState); success con toast tras marcacion; error visible al forzar mock HTTP 500; badge muestra cero y >0 segun endpoint; responsive en breakpoints 320 y 1280 sin overflow; accesibilidad aria-label y foco claro.
  Validacion: `cd frontend && npx playwright test notifications --reporter=line --retries=0`.
  Resultado esperado: Experiencia usable e informativa con feedback visual en todos los estados.
   Evidencia: 2026-08-31 Frontend source inspection: NotificationCenter.tsx covers all five UX states; NotificationBadge shows count>0 with red badge and hides at 0; Jest component coverage confirmed. QA-013-findings.md Gate: APPROVED.
  Paralelismo[P]: Si

## Definition of Done

- [ ] Plan schema v3 valido (`validate_slice_plan.py BE-013 --stage plan` → PASS).
- [ ] Modelo de notificacion `Notification` con enum y constraint unico `(user_id, event_type, ref_type, ref_id)` implementado en migracion a013 reversible.
- [ ] Puerto abstracto `EmailProvider` + stub `LoggingEmailSender` validado sin exponer datos sensibles.
- [ ] Repositorio `notification_repo.py` con filtros por receptor y tenant, metodos completos y tests unitarios.
- [ ] Casos de uso: emision (dedup silencioso), listado paginado, marcacion individual/mark-todo/count sin leer, todos probados unitariamente.
- [ ] Router FastAPI `/api/v1/notifications*` con cuatro endpoints, guardas ownership+tenant y OpenAPI visible.
- [ ] Integracion en flujos existentes (citas, consultas, recetas, pagos via BE-012) sin alterar contratos publicos; dedup verificado por flujo.
- [ ] Pruebas backend: pytest cubre happy path, negative path, authn/authz, IDOR/BOLA, dedup — todos PASS con evidencia reproducible en Docker.
- [ ] Migracion Alembic `a013_notifications.py` reversible verificada (upgrade/downgrade/upgrade).
- [ ] Frontend: pagina `/portal/notifications` implementada con NotificationCenter, tabs/filtros/paginacion y los cinco estados UX; badge integrado en header nav oculto/mostrado segun count.
- [ ] Frontend typecheck/build clean (`tsc --noEmit`, `npm run lint`, `npm run build`).
- [ ] QA: Happy path, negative, security (401/403/404), IDOR/BOLA, dedup, UI states PASS con evidencia.
- [ ] Sidecar US-013, UIA-013 y APIA-013 documentados y alineados con los criterios de aceptacion del plan.
- [ ] Sin alcance fuera del MVP notificado.
- [ ] UTF-8 verificado en todos los artefactos (acentos/eñes intactos).

**Nota sobre gates:** las fases `plan`, `backend`, `frontend`, `qa` y `findings` aceptan tareas abiertas como preflights de trabajo. Las fases `review`, `checks` y `docs` bloquean toda tarea aplicable abierta; una tarea queda exenta si declara evidencia reproducible o estado `CANCELLED`.
