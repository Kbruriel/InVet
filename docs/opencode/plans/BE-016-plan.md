---
schema_version: 3
slice: "016"
canonical_plan: BE-016
status: PLANNING
encoding: UTF_8
---

# BE-016 — Administrative del sistema

## Objetivo del slice

Administracion central de usuarios, clinicas, terminos/privacidad, soporte basico y reportes globales aggregates.

## Alcance mvp

### Backend (BE-016)

- Modelo `admin_settings` para terminos_de_servicio y politica_de_privacidad con seed inicial.
- Migracion Alembic `a015` crea tabla + seed de categorias soporte default por clinica.
- Endpoints CRUD admin settings: `GET/PUT /api/v1/terms` y `GET/PUT /api/v1/privacy` (public GET, PUT solo system_admin).
- Endpoints list/get internal-users scope global admin: `GET/PUT/PATCH /api/v1/admin/internal-users{user_id}`.
- Endpoints list/create clinic: `GET /api/v1/admin/clinics`, `POST /api/v1/admin/clinics`.
- Endpoint reporte global por periodo reusando agregadores BE-015 con rol system_admin: `GET /api/v1/admin/reports/{tipo}?period_start=&period_end=`.
- Endpoint soporte basico: `GET/PUT /api/v1/admin/support-tickets{ticket_id}`.

### Frontend (FE-016)

- Rutas `/portal/admin/users`, `/portal/admin/clinics`, `/portal/admin/settings/terms`, `/portal/admin/settings/privacy`, `/portal/admin/reports`, `/portal/admin/support`.
- Formularios creacion edicion usuarios clinicas con validacion frontend.
- Estados UX: loading, error, empty, success, submitting.
- Consumir cliente API y mapear errores HTTP.

### QA (QA-016)

- Validar admin-rol system_admin en endpoints criticos.
- Validar aislamiento tenant/ownership por endpoint.
- Happy path + negative path cada flujo administrativo.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios.
- Facturacion electronica y timbrado fiscal.
- Automatizaciones avanzadas o analitica avanzada.
- App movil nativa.
- Recomendaciones medicas automaticas.

## Entidades y reglas de negocio

### Entidades nuevas

```markdown
| Entidad | Tabla | Reglas |
| --- | --- | --- |
| AdminSettings | `admin_settings` (nueva) | key unique; content TEXT nullable; published_at TIMESTAMP default NULL |
```

### Entidades existentes reusadas

```markdown
| Entidad | Tabla | Uso en slice |
| --- | --- | --- |
| InternalUser | `internal_users` (existente) | CRUD + desactivacion admin global |
| Clinic | `clinics` (existente) | Listado global y creacion admin global |
| SupportTicket | `support_tables` (existente BE-014) | Gestion estado tickets soporte |
| ReportAggregator | Reusado desde BE-015 | Agregadores: appointments/services/pets/consultations/ratings/payments |
```

**Reglas derivadas:**

- Solo usuarios con rol "system_admin" pueden acceder a los endpoints bajo `/api/v1/admin/*`.
- Los endpoints `/api/v1/terms` y `/api/v1/privacy` son publicos para lectura (sin autenticacion).
- Todas las lecturas de recursos entre clinicas deben filtrar por `clinic_id` derivado del token JWT excepto en administracion global donde el rol garantiza scope.

## Revision de gaps

| Gap identificado | Severidad | Decision / Suposicion | Estado |
| --- | --- | --- | --- |
| Definicion de campos exactos para reportes globales | Baja | Se reusaran los DTOs de BE-015 extendiendo el scope a global. | Documentado |
| Criterios de "publicacion" de terminos | Baja | Se asume que el campo `published_at` controla la visibilidad. | Supuesto |
| Redirecciones post-login admin | Baja | Redirigir a `/portal/admin/users` por defecto. | Supuesto |


| Fuente | Ruta | Uso |
| --- | --- | --- |
| Tarea backend BE-016 | `docs/opencode/tasks/backend/BE-016.md` | Alcance actividades |
| Tarea frontend FE-016 | `docs/opencode/tasks/frontend/FRE-016.md` | Contract UI |
| Tarea QA QA-016 | `docs/opencode/tasks/qa/QA-016.md` | Casos minimo QA |
| Brief MVP slice 016 | `docs/opencode/references/slice_task_context.md L41` | Titulo entregables criterios |
| Matriz BE/FE/QA 02 | `docs/opencode/02_be_fe_qa_task_matrix.md` | IDs equivalentes |
| Security guard | `backend/app/core/security.py L139` | Verificacion rol system_admin |
| Router admin existente | `backend/app/api/v1/routers/clinic_admin.py` | Patron CRUD admin |
| Migration a014 | `backend/alembic/versions/a/a014_support.py` | Referencia proxima migration a015 |
| Router principal | `backend/app/api/v1/router.py` | Registro routers nuevos |

## Matriz de trazabilidad

| AC-ID | Tipo Cobertura | Endpoint cubierto | Tareas BE | Tareas FE | Tareas QA | Evidencia esperada |
| --- | --- | --- | --- | --- | --- | --- |
| AC-016-01 | API + UI | POST /api/v1/admin/internal-users | BE-016-T05 | FE-016-T04 | QA-016-T02 | HTTP 201; user visible in admin table |
| AC-016-02 | API + UI | PATCH /api/v1/admin/internal-users/{id}/deactivate | BE-016-T06 | FE-016-T03 | QA-016-T02 | HTTP 204; user deactivated in DB |
| AC-016-03 | API + UI | GET /api/v1/admin/internal-users | BE-016-T05 | FE-016-T03 | QA-016-T02 | HTTP 200; paginated list returned |
| AC-016-04 | Security + QA | All /admin/* endpoints | BE-016-T04 | N/A | QA-016-T01 | 403 for non-system_admin tokens |
| AC-016-05 | API + APIA | GET /api/v1/terms | BE-016-T02 | FE-016-T07 | QA-016-T04 | HTTP 200; JSON content returned |
| AC-016-06 | API + UIA | PUT /api/v1/terms | BE-016-T02 | FE-016-T07 | QA-016-T04 | 200 for admin, 403 for others |
| AC-016-07 | API + UI | GET /api/v1/terms (terms privacy) | BE-016-T02, T03 | FE-016-T07 | QA-016-T04 | Public access verified |
| AC-016-08 | API + UI | POST /api/v1/admin/clinics | BE-016-T08 | FE-016-T06 | QA-016-T03 | HTTP 201; clinic in admin table |
| AC-016-09 | API | GET /api/v1/admin/clinics | BE-016-T07 | FE-016-T05 | QA-016-T03 | Paginated list verified |
| AC-016-10 | API + QA | GET /api/v1/admin/reports/* | BE-016-T09 | FE-016-T08 | QA-016-T05 | Global aggregates returned |
| AC-016-11 | API + QA | PUT /api/v1/admin/support-tickets/{id} | BE-016-T10 | FE-016-T09 | QA-016-T06 | 200; status=resolved confirmed in DB |
| AC-016-12 | UIA + QA | Admin panel states UX | N/A | FE-016-T10 | QA-016-T08 | Screenshots of UX states |

## Endpoints esperados

### Endpoints de administracion global (/admin/*)

```markdown
| Metodo | Ruta (ba /api/v1) | Autenticacion | Rol requerido | Descripcion |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/admin/internal-users` | Bearer | `system_admin` | Listar todos los usuarios internos de todas las clinicas. Paginated. |
| GET | `/api/v1/admin/clinics` | Bearer | `system_admin` | Liste de todas las clinicas registradas. Paginated. |
| POST | `/api/v1/admin/clinics` | Bearer | `system_admin` | Crear nueva clinica con datos basicos (nombre, direccion). |
| GET | `/api/v1/admin/reports/{tipo}?period_start=&period_end=` | Bearer | `system_admin` | Reportes globales agregados reusando BE-015 usecases filtro sin clinic_id |
| GET | `/api/v1/admin/support-tickets?page=1&size=20` | Bearer | `system_admin` | Listar tickets soporte de todas las clinicas. Paginated. |
```

### Endpoints settings y recursos globales (terms/privacy)

```markdown
| Metodo | Ruta (ba /api/v1) | Autenticacion | Rol requerido |
| --- | --- | --- | --- |
| GET | `/api/v1/terms` | Ninguna N/A | Publico — obtiene terminos de servicvio publicados |
| PUT | `/api/v1/terms` | Bearer | `system_admin`. Solo admin del sistema puede actualizar terminos |
| GET | `/api/v1/privacy` | N/A | N/A | Publico — obtiene politica privacidad publicada |
| PUT | `/api/v1/privacy` | Bearer | `system_admin` | Solo admin del sistema puede alterar la politica de privacidad |
```

### Endpoints para gestos de usuarios internos (/admin/internal-users)

```markdown
| Metodo | Ruta | Autenticacion | Rol requerido Descripcion |
| --- | --- | --- | --- |
| GET | `/api/v1/admin/internal-users` | Bearer | `system_admin` Obtener lista paginada de todos los usuarios. |
| GET | `/api/v1/admin/internal-users/{user_id}` | Bearer | `system_admin` Obtener detalle de un usuario especifico. |
| PUT | `/api/v1/admin/internal-users/{user_id}` | Bearer | `system_admin` Actualizar informacion (email, rol nombre). |
| PATCH | `/api/v1/admin/internal-users/{user_id}/activate` | Bearer | `system_admin` Activar cuenta de usuario. |
```

## Contrato de implementacion frontend

### Rutas y acceso

```markdown
| Ruta | Clasificacion | Acceso |
| --- | --- | --- |
| /portal/admin/users | Privada | system_admin |
| /portal/admin/clinics | Privada | system_admin |
| /portal/admin/settings/terms | Mixta (GET publica / PUT privada) | GET any; PUT admin only |
| /portal/ｱadmin/settings/privacy | Mixta (GET publica / PUT privada) | GET any; PUT admin only |
| /portal/admin/reports | Privada | system_admin |
| /portal/admin/support | Privada | system_admin or admin |
```

### Flujos y estados ux

- `loading`: Mostrar spinner mientras se cargan datos desde API.
- `submitting`: Desabilitar botones submit mientras se envia PUT/POST.
- `error`: Banner de error con mensaje traducido + opcion Reintentar.
- `empty`: Mensaje "Sin registros" si el listado esta vacio.
- `success`: Datos visibles inmediatamente despues de obtener respuesta HTTP valida.

### Contratos api por accion

| Accion UI | Metdo | Endpoint | Request | Response | Errores | Autenticacion |
| --- | --- | --- | --- | --- | --- | --- |
| Listar usuarios internos | GET | /api/v1/admin/internal-users?page=&size= | query params page/size | paginated JSON | 401, 403 | Bearer system_admin |
| Desactivar usuario | PATCH | /api/v1/admin/internal-users/{user_id}/deactivate | - | HTTP 204 no content | 401, 403, 404 | Bearer admin |
| Crear clinica | POST | /api/v1/admin/clinics | JSON {name,address,phone} | HTTP 201 + created entity | 400, 401, 403, 409 (duplicate) | Bearer system_admin |
| Leer terminos | GET | /api/v1/terms | - | JSON {id,content,published_at} | 404 si no existe null body | Ninguna |
| Editar terminos | PUT | /api/v1/terms | JSON {content} | HTTP 200 + updated entity | 401, 403 | Bearer system_admin |
| Ver reportes | GET | /api/v1/admin/reports/appointments?period_start=&period_end= | query params period/page/size | paginated JSON | 400 (invalido periodo), 403 | Bearer system_admin |
| Gestionar tickets | GET + PUT | /api/v1/admin/support-tickets/{id} | query/state update | JSON ticket updated | 403 if not assignee | Bearer admin/system_admin |

### Formularios y validacion

- **Formulario crear/editar usuario interno**: email (obligatorio, formato email); username (obligatorio, min. 3 caracteres; rol (select obligatorio: `admin`/`manager`/`veterinarian`. Validacion inline antes de enviar al backend.
- **Formulario crear clinica**: name (oobligatorio, 2+ caracteres), address optional), phone (formato numerico si se proporciona).
- **Formularios editar terminos/privacidad**: content (textarea obligatoria, min. 10 caracteres para vacios).

### Arquitectura de componentes

| Componente | Ubicacion | Descripcion |
| --- | --- | --- |
| UserListPage | `frontend/src/app/portal/admin/users/page.tsx` | Pagina principal list/admin. |
| UserFormComponent | `frontend/src/features/admin/components/UserForm.tsx` | Formulario crear/editar usuario. |
| ClinicListPage | `frontend/src/app/portal/admin/clinics/page.tsx` | Pagina listado clinicas. |
| ClinicFormComponent | `frontend/src/features/admin/components/ClinicForm.tsx` | Formulario crear-clinica. |
| SettingsTermsPage | `frontend/src/app/portal/admin/settings/terms/page.tsx` | Pagina terminos de servicio. |
| SettingsPrivacyPage | `frontend/src/app/portal/admin/settings/privacy/page.tsx` | Politica privacidad |
| ReportsPage | `frontend/src/app/portal/admin/reports/page.tsx` | Pagina reportes globales (filter+table). |
| SupportPage | `frontend/src/app/portal/admin/support/page.tsx` | Gestion tickets soporte. |
| AdminApiClient | `frontend/src/features/admin/api.ts` | Client API centralizado para endpoints del slice. |

### Responsive y accesibilidad

- Layout responsive: desktop column-full-width > tablet 2-column grid > mobile stacked-stack blocks.
- Labels HTML for every input field. ARIA labels donde el icono o placeholder no son suficientes.
- Contraste de color WCAG AA minimo en componentes UI existentes reutilizados (ver `frontend_visual_alignment.md` si aplica).

### Estrategia de pruebas frontend

| Capa | Cobertura | Herramienta Esperada | Comandos Ejecutaos |
| --- | --- | --- | --- |
| Unit/Componentes | UserForm + ClinicForm validation logic | Jest/RTL or Vitest (dependiendo setup existente) | `npx vitest run --testPathPattern="admin/form"` |
| Integration | ApiClient mocks para cada endpoint con success+error cases | Mocked HTTP client | `npm test -- --testPath/pattern="admin" --coverage` |
| E2E | Flow admin login > list users > create clinic > update terms | Playwright | `npx playwright test --grep="admin"` |

## Contrato de ejecucion docker y pruebas

### Infraestructura necesaria

El stack requiere servicios: `db` Postgres, `backend`, `frontend` desde docker-compose.yml existente.

### Comandos validacion backend

```bash
# Migraciones
docker compose up -d db
python -m alembic upgrade head

# Tests unitarios usecases/schemas
pytest backend/app/tests/useto_cases/ -q --timeout=30
pytest backend/app/api/v1/test_admin_internal_users.py -q --timeout=30
```

### Comandos validacion frontend

```bash
cd frontend/
npx tsc --noEmit --project tsconfig.json
npm test -- --testPathPattern="admin" --coverage
npx playwright test --grep="admin"
```

### Evidencia esperada

- Tests backend deben ejecutarse con contenedor Postgres real (no SQLite), por que los filtros `clinic_im_id` dependen de columnas reales.
- Frontend E2E debe ejecutarse con frontend container levantado o Next dev server running on localhost:3000.

## Plan de reportes y findings

### Reportes esperados

| Reporte | Ruta resultado | Autor | Cuando |
| --- | --- | --- | --- |
| QA results | `docs/opencode/qa/QA-016-results.md` | QA engineer | Tras QA tasks |
| QA findings | `docs/opencode/qa/QA-016-findings.md` | QA engineer | Si hay defects bloqueantes |
| Functional review | `docs/opencode/reviews/BE-016-final-review.md` | Reviewer funcional | Post-plan-backend |
| Security review | `docs/opencode/reviews/BE-016-security-review.md` | Security auditor | Tras implementacion backend/guards |
| Clean architecture review | `docs/opencode/reviews/BE-016-clean-architecture.md` | Architecture reviewer | Tras implementar use-cases/repos |

## Pruebas qa

### Casos de prueba principales

| TC-ID | Area | Caso | Endpoint | Esperado |
| --- | --- | --- | --- | --- |
| QC-016-01 | Happy-path | Administrador crea usuario interno | POST /api/v1/admin/internal-users | 201; data persisted correctly |
| QC-016-02 | Positive | Admin lista internal users across all clinics | GET /api/v1/admin/internal-users | 200; paginated JSON correct |
| QC-016-03 | Negative | Sin token en admin endpoint | any /admin/* | 4or1 |
| QC-016-04 | AC-ID | Token normal sin admin role in global admin | GET/admin/internal-users | 403 Forbidden |
| QC-016-05 | Positive | GET public terminos sin auth | GET /api/v1/terms | 200; JSON has content |
| QC-016-06 | Negative | PUT terminos con token no-admin | PUT /api/v1/terms | 403 Forbidden |
| QC-016-07 | Positive | Admin actualiza estado ticket soport | PUT/a/admin/support-tickets/{id} | 200; state=resolved in DB |
| QC-016-08 | IDOR/BOLA | Token clinica A accede a datos admin global | GET /admin/internal-users | 403 if not system_admin |

### Estados HTTP definidos

| Estado | Descripcion | Ejemplo |
| --- | --- | --- |
| 2/00 | Ok (GET/PUT success) | Successful read or update |
| 201 | Created (POST success) | New clinic created successfully |
| 204 | No content (DELETE/partial deactivate) | User deactivated; no response body |
| 400 | Bad input validation failed | Invalid email format in form |
| 401 | Missing or invalid token asdf Empty Authorization header |
| 403 | Authzinsufficient role | Normal user accessing global admin |
| 404 | Not found resource | Internal user does not exist |
| 422 | Schema validation failed | Missing required field in POST body |

## Riesgos de seguridad/idor/bola

### Analisis de riesgos slice

| Riesgo | Prioridad | Mitigacion | Caso QA cubre |
| --- | --- | --- | --- |
| Admin local accede a recursos global /admin/* | ALTA | Guard explicit `system_admin` en routers; clinic_id del token NO se usa para endpoints globales. QC-016-04 + BOLA-C1 | QC-016-05, QC-016-08 |
| Terminos/privacidad expuestos sin autenticacion (intencional) pero manipulados por no-admin | MEDIA | GET is public; PUT requires admin auth; no-write to non-authenticated. QC-016-06 | |
| IDOR: user_id en internal-user endpoint permite enumerar usuarios | ALTA | Filtro implicito + rol guard. No se expone lista publica de user_ids sin autorizacion. QC-016-08 | |
| Data leak en reportes globales (expose PII personal) | MEDIA | DTOs resumidos; no email/phone completo en response global Implementer debe auditar fields exportados por cada endpoint del slice | QC-016-03, review manual |

## Politica utf-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

**Checklist antes de guardar:**

- [ ] Rutas backend y prefijos API definidos (`/api/v1/admin/*`, `/api/v1/terms`, `/api/v1/privacy`).
- [ ] Contratos request/response documentados (seccion Endpoints esperado).
- [ ] Permisos y ownership definidos por endpoint o accion (guard `system_admin` para global admin routes; JWT `clinic_im_id` para scoped routes).
- [ ] Estados 401, 403, 404 y validaciones documentados.
- [ ] Modelos/extensiones de persistencia identificados (solo nueva tabla `admin_settings`; todas las demas reusando existentes: users, internal users, clinics, support_tickets).
- [ ] Casos QA positivos negativos y de permisos trazados a criterios completos.
- [ ] Checks esperados definidos para backend y frontend (seccion Contrato Docker).
- [ ] Documentacion a actualizar identificada (Openrag OpenAPI schema debe extenderse).

## Checklist de tareas

- [ ] Todos los endpoints de admin estan protegidos por system_admin guard.
- [ ] Las migraciones Alembic han sido creadas y probadas.
- [ ] El frontend tiene los nuevos componentes de admin con estado loading/error.

## Tareas del slice

- [ ] BE-016-T01 - Implementar modelo admin_settings y migration a015.
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-016-01
  Objetivo: Implementar tabla admin_settings.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: models/admin_settings.py
  Contratos usados: None
  Entregables: migration file, alembic script.
  Criterios de aceptacion: Tabelle creada.
  Validacion: alembic upgrade head.
  Resultado esperado: Table exists in DB.
  Evidencia: pending
  Paralelismo[P]: Si

- [ ] BE-016-T02 - Implementar endpoints CRUD para terminos y privacidad.
  Capa: backend
  Tipo: api
  Historia o criterio: AC-016-05
  Objetivo: Implementar endpoints CRUD para terminos.
  Responsabilidad unica: Si
  Depende de: BE-016-T01
  Contexto necesario: admin_settings table
  Contratos usados: /api/v1/terms, /api/v1/privacy
  Entregables: router, endpoints, schemas.
  Criterios de aceptacion: endpoints work.
  Validacion: pytest.
  Resultado esperado: endpoint active.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-016-T03 - Implementar guard de permisos para rutas admin.
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-016-04
  Objetivo: Implement admin guard.
  Responsabilidad unica: Si
  Depende de: BE-016-T02
  Contexto necesario: JWT provider
  Contratos usados: system_admin role
  Entregables: Guard logic.
  Criterios de aceptacion: 403 for non-admin.
  Validacion: pytest.
  Resultado esperado: security active.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-016-T04 - Implementar endpoint de gestion de clinicas.
  Capa: backend
  Tipo: api
  Historia o criterio: AC-016-08
  Objetivo: Clinic CRUD auth.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: clinics table
  Contratos usados: /api/v1/admin/clinics
  Entregables: router, schemas.
  Criterios de aceptacion: clinic created.
  Validacion: pytest.
  Resultado esperado: clinic endpoint.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-016-T05 - Implementar endpoint de reportes globales agregados.
  Capa: backend
  Tipo: api
  Historia o criterio: AC-016-10
  Objetivo: Global reports endpoint.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: aggregation logic
  Contratos usados: /api/v1/admin/reports
  Entregables: router, service.
  Criterios de aceptacion: JSON returned.
  Validacion: pytest.
  Resultado esperado: report endpoint.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] FE-016-T01 - Implementar routing administrativo y layout base.
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-016-12
  Objetivo: Setup admin routes.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: next.js router
  Contratos usados: portal/admin routes
  Entregables: routes, page.tsx.
  Criterios de aceptacion: routes exist.
  Validacion: browser check.
  Resultado esperado: accessible routes.
  Evidencia: pending
  Paralelismo[P]: Si

- [ ] FE-016-T02 - Implementar interfaz de gestion de terminos y privacidad.
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-016-05
  Objetivo: Implementar interfaz para terminos.
  Responsabilidad unica: Si
  Depende de: FE-016-T01
  Contexto necesario: AdminApiClient
  Contratos usados: /api/v1/terms
  Entregables: pages, components.
  Criterios de aceptacion: forms visible.
  Validacion: jest/cypress.
  Resultado esperado: UI components.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] FE-016-T03 - Integrar AdminApiClient con endpoints nuevos.
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-016-0 $
  Objetivo: Fetch data via api client.
  Responsabilidad unica: Si
  Depende de: FE-016-T01
  Contexto necesario: api/v1 endpoints
  Contratos usados: AdminApiClient
  Entregables: api client methods.
  Criterios de aceptacion: axios/fetch working.
  Validacion: integration tests.
  Resultado esperado: data fetched.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-016-T01 - Validar autenticacion y permisos en endpoints admin.
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-016-04
  Objetivo: Verify 403 for non-admin.
  Responsabilidad unica: Si
  Depende de: BE-016-T03
  Contexto necesario: tokens
  Contratos usados: /api/v1/admin/*
  Entregables: test plan, results.
  Criterios de aceptacion: correct status codes.
  Validacion: pytest/playwright.
  Resultado esperado: security verified.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-016-T02 - Validar flujo de error y estados UX en admin dashboard.
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-016-12
  Objetivo: Verificar estados vacios de la interfaz.
  Responsabilidad unica: Si
  Depende de: FE-016-T02
  Paralelismo[P]: No
  Contexto necesario: test data
  Contratos usados: loading, error, empty, success
  Entregables: automated tests.
  Criterios de aceptacion: UX states matched.
  Validacion: playwright.
  Resultado esperado: UX matches spec.
  Evidencia: pending
  Paralelismo[P]: No

## Definition of Done

### Backend (BE-016)

- [ ] Modelo `admin_settings` creado + migration `a015` aplicada.
- [ ] Routers `/api/v1/admin/*`, `/api/v1/terms`, `/api/v1/privacy` implementados.
- [ ] Guards de permisos (system_admin) en cada endpoint.
- [ ] Tests unitarios e integration para cada endpoint (pytest).
- [ ] OpenAPI schema extendido con nuevos endpoints.

### Frontend (FE-016)

- [ ] Rutas `/portal/admin/*` implementadas con proteccion por rol.
- [ ] Formularios validacion inline.
- [ ] Estados UI UX (loading, error, empty, success).
- [ ] API client centralizado (AdminApiClient) consumiendo backend endpoints.
- [ ] Pruevas unitarias de componentes + E2E admin flow.

### QA (QA-016)

- [ ] Todos los TC (QC-016-T01 through QC-016-T08) ejecutados y evidenciados.
- [ ] Casos IDOR/BOLA validados sin fugas.
- [ ] Documentacion de resultados en `QA-results.md`.

### Final checklist plan validation

- [ ] Matriz BE/FE/QA 02 existe.
- [ ] US-016.md, UIA-016.md y APIA-016 existidos o actualizados.
- [ ] Objetivo del slice y alcance mvp separados de fuera de alcance.
- [ ] Todos los criterios CA/AC medibles.
- [ ] Cada AC con cobertura BE, FE, QA, UIA o manual con justificacion.
- [ ] Plan cubre todos los archivos matriz BE/FE/QA base existentes.
- [ ] `python backend/scripts/validate_slice_plan.py BE-016 --stage plan` = PASS (se valida antes de cualquier generacion de tareas).
