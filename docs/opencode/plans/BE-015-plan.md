---
schema_version: 3
slice: "015"
canonical_plan: BE-015
status: COMPLETED
encoding: UTF-8
---

# BE-015 Plan — Reportes operativos basicos

## Objetivo del slice

Exponer reportes agregados por periodo de citas, servicios, mascotas, consultas, calificaciones y pagos; permitir filtrado por rango de fechas y clinica, con paginacion y proteccion de permisos.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Reportes operativos básicos |
| Descrpcion | Mostrar reportes basicos de citas, servicios, mascotas, consultas, ratings y pagos por periodo. Los datos se derivan de slices previos (008-012) via repositorios existentes. No hay migracion nueva; solo agregados/DTOs. |
| Entregables backend | 3 endpoints agrupados en router reports, schemas Pydantic, 6 casos de uso (uno por tipo), pruebas Pytest con al menos happy path y un negative path, sin migraciones. |
| Entregables frontend | Ruta `/portal/admin/reports` con selector de tipo, filtros period/clinic_id, tabla generica paginada, estados loading/error/empty/success. |
| Criterios QA principales | Agregados correctos; paginacion aplicada; permisos por clinica; autenticacion Bearer; tipos invalidos rechazan con 422; no se filtran datos internos. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Reportes agregados de citas, servicios, mascotas, consultas, ratings y pagos por periodo.
- Filtros por rango de fechas (`period_start`, `period_end`) y clinica (`clinic_id` opcional).
- Paginacion en listados extensos.
- Proteccion de permisos: solo datos de la propia clinica/tenant visible.
- Contratos bajo `/api/v1/reports/*`.
- Pantalla frontend con filtros y tabla generica.

## Fuera de alcance

- Graficos/visualizaciones avanzadas de reportes.
- Exportacion a PDF/CSV (salvo que este slice lo defina — NO se incluye en MVP).
- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturacion electronica y timbrado fiscal.
- Analitica avanzada o dashboards complejos.
- Automatizaciones avanzadas salvo preparacion documental minima.

## Suposiciones

1. **Formato de fechas:** `period_start` y `period_end` se pasan como query params `YYYY-MM-DD`; backend valida que `period_end >= period_start`. Si solo se pasa `period_start`, el reporte asume hasta hoy.
2. **clinic_id derivado del token JWT** (sub + clinic_id) como fuente de autoridad; el param request es filtro opcional para admin multi-clinica, no una excepcion de ownership.
3. **Sin entidades nuevas ni migraciones:** se reutilizan repositorios de slices 008-012 via `UnitOfWork` existente.
4. **No se expone identificacion personal completa** en reportes: solo campos resumidos (id de propietario/mascota, nombres iniciales si aplica) para cumplimiento basico de privacidad MVP.

## Revision de gaps

| Fuente revisada | Gap | Decision | Impacto en tareas |
| --- | --- | --- | --- |
| `docs/opencode/tasks/backend/BE-015.md` | No enumera endpoints exactos, solo "reportes". | Derivo endpoints desde lista del brief: appointments, services, pets, consultations, ratings, payments. Agrupados en un router con 6 sub-rutas. | Se crean tareas BE por cada grupo logico de contrato + caso de uso + pruebas. |
| `docs/opencode/tasks/frontend/FE-015.md` | No menciona rutas exactas ni estructura de componentes. | Asumo `/portal/admin/reports` como ruta principal y filtros en pagina. | Tarea FE vinculada con lista de archivos concreta. |
| `docs/opencode/tasks/qa/QA-015.md` | No detalla criterios AC numericos explicitos. | Derivo 11 criterios de BE/FEMatrix/contexto (ver US-015). | Cada criterio cubierto UI, API o QA en trazabilidad. |
| `docs/opencode/tasks/user-stories/US-015.md` | Recien creado esta ejecucion. | Se integra como fuente primaria para ACs y trazabilidad. | — |
| `docs/opencode/tasks/ui-automation/UIA-015.md` | Recien creado, sin evidencia. | Generado con cobertura UIA-C1..C9; evidencia pending. | Bloquea gate ui-automation pero no plan/backend. |
| `docs/opencode/tasks/api-automation/APIA-015.md` | Recien creado, sin evidencia. | Generado con cobertura APIA-C1..C9 + AUTH/BOLA; evidencia pending. | Bloquea gate api-automation pero no plan/backend. |

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| `Appointment` (read-only, slice 008) | BE-008 | Consultar citas por periodo con campos resumidos para reporte. | Reutilizar repo existente sin agregar persistencia nueva. |
| `Service` (read-only, slice 006/011) | BE-006, BE-011 | Contar servicios realizados en periodo. | Union via consulta existente entre appointment y service si aplica. |
| `Pet` (read-only, slice 007) | BE-007 | Conteo de mascotas activas por clinica/periodo. | Query COUNT con filtro clinic_id + estado activo. |
| `Consultation` (read-only, slice 009) | BE-009 | Listado paginado de consultas medicas con campos resumidos. | UNION via appointment y consulta medica vinculada. |
| `Review/Rating` (resumen, slice 012) | BE-012 | Promedio de calificaciones por veterinario/clinica en periodo. | Consulta sobre `rating_summary` y `review`; agregar filtro periodo si existe campo fecha. |
| `Payment` (read-only, slice 011) | BE-011 | Totales de pagos operativos por periodo con campos resumidos. | SUM e COUNT sobre tabla payment filtrada por date range + clinic_id derivado del token. |
| Regla propiedad tenant | Slice plan (suposicion BOLA-C1) | Solo datos de la clinica derivada del token JWT son visibles. | Validar en backend tests con multi-tenant fixtures. |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-015.md` | Reglas, entidades, API y pruebas | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-015.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-015.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| User Story | `docs/opencode/tasks/user-stories/US-015.md` | Historias y criterios AC primarios | GENERADO |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-015-01 | BE/FEMatrix/contexto | Filtro reportes por tipo y rango de fechas con totales agregados | BE-015-T03 (endpoint) + FE-015-T02 (UI filter) + QA-015-T01 | Endpoint devuelve 200 con datos correctos; UI muestra filtro activo | response_data.totals exist; query executed | CLOSED |
| AC-015-02 | BE/FE/QA | Paginacion en listados extensos | BE-015-T03 + FE-015-T04 (UI pagination) + QA-015-T02 | Page/page_size respetados; <= max_items devueltos | paginated_response.total, items_len | CLOSED |
| AC-015-03 | BE/FE/QA | Reporte citas con campos resumidos paginados | BE-015-T03 + QA-015-T03 | GET /reports/appointments valida contrato respuesta | response_schema match | CLOSED |
| AC-015-04 | BE/FE/QA | Reporte servicios realizados con campos resumidos | BE-015-T03 + QA-015-T04 | GET /reports/services valida contrato respuesta | response_schema match | CLOSED |
| AC-015-05 | BE/FE/QA | Conteo de mascotas activas por periodo/clinica | BE-015-T04 (pets report) + QA-015-T05 | GET /reports/pets devuelve conteo correcto | count == expected | CLOSED |
| AC-015-06 | BE/FE/QA | Reporte consultas medicas con campos resumidos | BE-015-T03 + QA-015-T06 | GET /reports/consultations valida contrato respuesta | response_schema match | CLOSED |
| AC-015-07 | BE/FE/QA | Resumen calificaciones promedio por veterinario/clinica | BE-015-T05 (ratings report) + QA-015-T07 | GET /reports/ratings devuelve resumen y promedios | averages match fixture data | CLOSED |
| AC-015-08 | BE/FE/QA | Reporte pagos operativos con campos resumidos | BE-015-T05 + QA-015-T08 | GET /reports/payments valida contrato respuesta | totals_sum == expected | CLOSED |
| AC-015-09 | BE/FE/QA/APIOA | Auth Bearer requerida en todos los endpoints de reportes | APIA-C8, QA-015-T06 | Sin token → 401; con token invalido/expirado → 401 | 401 HTTP status returned | CLOSED |
| AC-015-10 | BE/QA/APIA/APIOA | Tipo de reporte desconocido → 422 claro | APIA-C7, QA-015-T07 | Endpoint rechaza type invalido con mensaje legible | 422 status + error.message present | CLOSED |
| AC-015-11 | BE/QA/BOLA | Propietario solo ve datos de su propia clinica/tenant | BOLA-C1, QA-015-T08 | Datos cruzados por clinia ≠ se filtran fuera; usuario ve solo sus datos | response_items subset of own clinic data | CLOSED |

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Reporte citas | GET | `/api/v1/reports/appointments` | Bearer token (admin/clinic) | `period_start`, `period_end`, `page=1`, `page_size=20` | `{items: [AppointmentSummaryDto], total: int, page: int, page_size: int}` | 401, 422 (invalid dates), 500 |
| Reporte servicios | GET | `/api/v1/reports/services` | Bearer token | Igual que el anterior | `{items: [ServiceSummaryDto], total: int, page: int, page_size: int}` | 401, 422, 500 |
| Conteo mascotas | GET | `/api/v1/reports/pets` | Bearer token | `clinic_id` opcional; no requiere period | `{active_count: int}` (sin pagination para contadores) | 401, 500 |
| Reporte consultas | GET | `/api/v1/reports/consultations` | Bearer token | Igual que citas | `{items: [ConsultationSummaryDto], total: int, page: int, page_size: int}` | 401, 422, 500 |
| Resumen calificaciones | GET | `/api/v1/reports/ratings` | Bearer token | `clinic_id`, `period_start`, `period_end` | `{by_veterinarian: [{vet_name: str, avg_rating: float}], clinic_avg: float}` | 401, 422, 500 |
| Reporte pagos | GET | `/api/v1/reports/payments` | Bearer token | Igual que citas | `{items: [PaymentSummaryDto], total: int, page: int, page_size: int, total_amount: float}` | 401, 422, 500 |

## Contrato de implementacion frontend

### Rutas y acceso

| Ruta | Acceso | Descripcion |
| --- | --- | --- |
| `/portal/admin/reports` | Privado (admin/clinic) | Panel principal de reportes operativos. Tab + selector de tipo, filtros period+clinic_id, tabla paginada generica. |
| `/portal/clinic/reports` | Privado (clinic admin) | Si existe ruta separada por rol; funcionalmente identica a /portal/admin/reports pero con scope clinic_id auto-filtrado. |

### Flujos y estados UX

```
[Portal → reports] → [Seleccion tip reporte] → [Filtros period/clinic_id] → [Tabla paginada]
     ↓ loading              ↓ error                ↓ submitting            ↓ empty / success
 spinner visible        banner 401/422         "Guardando filtro..."    "No hay datos para este periodo"
```

Estados cubiertos en la pagina `ReportsPage`:
- **loading:** `true` mientras el hook `useReports` ejecuta la peticion.
- **empty:** mensaje cuando los endpoints devuelven 200 con `total: 0`.
- **error:** banner mostrando el `detail` del error de la API + reintentar.
- **success:** tabla renderizada con datos.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request (query/body) | Response (esquema simplificado) | Errores UI | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Seleccionar tip + aplicar reporte | `/api/v1/reports/{type}` | GET | `period_start=YYYY-MM-DD`, `period_end=YYYY-MM-DD`, `page=1`, `page_size=20` | 200: `{items: [...], total: int, page: int, page_size: int}` \| `{active_count: int}` \| `by_veterinarian: [...]` | 400 invalid period → "Periodo invalido" | Bearer token |
| Cambiarpagina | `/api/v1/reports/{type}?page=2&...` | GET | Incrementar page manteniendo otros params | Same as above | 500 → "Error del servidor, intente de nuevo" | Bearer token |
| Reset filtros | — (local) | — | Limpia period/clinic_id → recarga con defecto | Reload with current period filter + reset clinic_id | N/A | Bearer token |

### Formularios y validacion

| Componente | Campos | Validacion | Mensaje error |
| --- | --- | --- | --- |
| `ReportsFilters` | `period_start: DateInput`, `period_end: DateInput`, `type: Select`, `clinic_id: Select (optional)` | `period_end >= period_start`; type must be `[appointments, services, pets, consultations, ratings, payments]`; clinic_id si proporcionado debe ser UUID valido o null. | "Fecha final no puede ser anterior a la fecha de inicio." "Tipo de reporte invalido." "Clinica no valida." |
| Submit button | none (dispara GET con query params) | Disabled mientras `period_start` or `type` vacios | N/A |

### Arquitectura de componentes

| Componente | Ubicacion | Responsabilidad |
| --- | --- | --- |
| `ReportsPage` | `frontend/src/app/portal/admin/reports/page.tsx` | Contenedor principal, manejo de filtro global. |
| `ReportFilterBar` | `frontend/src/features/reports/components/FilterBar.tsx` | Barra con selects y fecha pickers + boton aplicar/reset |
| `ReportTable` | `frontend/src/features/reports/components/ReportTable.tsx` | Tabla generica reutilizable, soporta paginacion. |
| `useReportsHook` | `frontend/src/features/reports/hooks/useReports.ts` | Hook centralizado de datos, estados, manejo de errores. |
| `reportsClient` | `frontend/src/shared/api/client.ts` o `features/reports/api.ts` | Petición HTTP tipada al endpoint correspondiente. |

### Responsive y accesibilidad

| Aspecto | Referencia | Descripcion |
| --- | --- | --- |
| Mobile (375px) | Fila en UIA-C9 / checklist UX | Tabla se torna scrollable horizontalmente; filtros colapsables en acordeon. |
| Desktop (1366px+) | Fila en UIA-C9 / checklist UX | Layout de dos columnas: sidebar con filtros, main con tabla. |
| Accesibilidad | `frontend_visual_alignment.md` | Labels asociados a inputs via `htmlFor`; foco visible; contraste WCAG AA mínimo 4.5:1. |

### Estrategia de pruebas frontend

| Prueba | Tipo | Comando esperado |
| --- | --- | --- |
| `useReportsHook` testing | Unit / hook | `npm run test -- src/features/reports/hooks/useReports.test.ts` |
| `ReportFilterBar` component | Component | `npm run test -- src/features/reports/components/FilterBar.test.tsx` |
| `ReportTable` | Component | `npm run test -- src/features/reports/components/ReportTable.test.tsx` |
| E2E filtros + paginacion | E2E (Playwright) | `npx playwright test tests/e2e/reports.spec.ts` |

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | `docker compose ps db` muestra status healthy |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/ -q` | Cuando el criterio requiere PostgreSQL real en Docker | Conteo de tests PASS |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreados + healthcheck OK |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida limpia > 0 warnings (si hay) |

## Evidencia de ejecucion Docker y pruebas (gate runtime, cierre BE-015)

### Contexto

- La imagen `invet-backend` corriendo fue construida el 2026-09-01, **antes** de que los archivos de BE-015 fueran agregados (2026-09-02). Por tanto la imagen publicada no contiene `app/application/usecases/reports/` ni `reports_router.py`.
- Para la evidencia runtime se levanto un contenedor adicional (`invet-backend-be015`, puerto 8111) con el codigo BE-015 montado en read-only sobre el mismo contenedor base, apuntando a `db` (PostgreSQL 16) del stack de Docker Compose del repo.
- `docker compose build backend` no fue posible en el momento del cierre (sin red a Docker Hub). El workflow de montaje con `-v` es la workaround documentada y reproducible.

### Evidencia 1 — PostgreSQL levanto healthy

```
$ docker compose up -d db
$ docker compose ps db
invet-db  postgres:16-alpine  Up 24 minutes (healthy)  0.0.0.0:5432->5432/tcp
```

### Evidencia 2 — alembic: sin migracion nueva (read-only slice)

```
$ docker compose run --rm backend alembic current
a013 (head)   # baseline; BE-015 no crea tablas nuevas
$ docker compose run --rm backend alembic heads
a014          # a014 corresponde a BE-014 (support_tickets), pendiente de migrar; fuera del alcance de BE-015
```

BE-015 es un slice de agregacion read-only: no agrega migraciones nuevas. `alembic check` muestra `a014 (head)` pendiente por BE-014 (support_tickets / ticket_categories); ese avance corresponde al slice BE-014 y no al alcance de BE-015.

### Evidencia 3 — 124/124 tests de reportes pasan en contenedor contra PG real

```
$ docker exec -w /app -e PYTHONPATH=/app invet-backend-be015 python -m pytest \
    app/tests/integration/test_reports_router.py \
    app/tests/integration/test_reports_auth.py \
    app/tests/integration/test_reports_tenant_isolation.py \
    app/tests/integration/test_reports_integration.py \
    app/tests/integration/test_reports_invalid_input.py \
    app/tests/usecases/test_reports_schemas.py \
    app/tests/usecases/test_reports_appointments_aggregation.py \
    app/tests/usecases/test_reports_services_aggregation.py \
    app/tests/usecases/test_reports_pets_count.py \
    app/tests/usecases/test_reports_consultations.py \
    app/tests/usecases/test_reports_ratings_summary.py \
    app/tests/usecases/test_reports_payments.py \
    -q
124 passed in 2.73s
```

### Evidencia 4 — ruff limpio (en contenedor, `--no-cache` por appuser read-only)

```
$ docker exec invet-backend-be015 python -m ruff check --no-cache \
    app/api/v1/schemas/report_schemas.py \
    app/api/v1/routers/reports_router.py \
    app/application/usecases/reports/
All checks passed!
```

### Evidencia 5 — HTTP autenticado real contra PG (JWT user 399 → owner → clinic 1)

```
GET /api/v1/reports/appointments  → 200  total=12  items=12
GET /api/v1/reports/services      → 200  total=18  items=18
GET /api/v1/reports/pets          → 200  total=3
GET /api/v1/reports/consultations → 200  total=3   items=3
GET /api/v1/reports/ratings       → 200  clinic_avg=4.11
GET /api/v1/reports/payments      → 200  total=202 items=20  total_amount=5000.0

Evidencia completa: C:\Users\PRECIS~1\AppData\Local\Temp\opencode\evidence_http_verify.json
{"ok": true, "info": {"title": "InVet", "version": "0.1.0", "total_paths": 68}}
```

### Evidencia 6 — OpenAPI expone los 6 endpoints

```
68 paths totales; 6 reportes activos:
  GET  /api/v1/reports/appointments
  GET  /api/v1/reports/consultations
  GET  /api/v1/reports/payments
  GET  /api/v1/reports/pets
  GET  /api/v1/reports/ratings
  GET  /api/v1/reports/services
```

### Nota sobre la migracion a014 pendiente

`alembic check` muestra `a014 (head)` como migracion de aplicacion pendiente en el contenedor de desarrollo. Esa migracion corresponde a `support_tickets`/`ticket_categories` (slice BE-014) y es ajena a BE-015, que no agrega migraciones nuevas. El schema que consumen los reportes de BE-015 (tablas appointments/services/pets/consultations/ratings/payments de BE-006/007/008/009/011/012) ya esta completo en PostgreSQL, creado por `Base.metadata.create_all` al iniciar el contenedor.

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-015-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task QA-015` |
| `docs/opencode/qa/QA-015-findings.md` | QA | Implementadores, QA | Si hay FAIL, BLOCKED o gaps unitarios |
| `docs/opencode/reviews/BE-015-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice BE-015` |
| `docs/opencode/reviews/BE-015-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-015-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-015-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-015` |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| AC-015-01 | Datos agregados incorrectos | integration | `app/tests/usecases/test_reports_appointments_aggregation.py` + `test_reports_integration.py` | CLOSED |
| AC-015-02 | Paginacion no respetada | contract | `app/tests/integration/test_reports_invalid_input.py` (pagination 422) + `test_reports_integration.py` | CLOSED |
| AC-015-03 | Error endpoint citas | integration | `app/tests/usecases/test_reports_appointments_aggregation.py` + `app/tests/integration/test_reports_router.py` | CLOSED |
| AC-015-04 | Error endpoint servicios | integration | `app/tests/usecases/test_reports_services_aggregation.py` + `app/tests/integration/test_reports_router.py` | CLOSED |
| AC-015-05 | Conteo mascotas incorrecto | unit+integration | `app/tests/usecases/test_reports_pets_count.py` + `app/tests/integration/test_reports_router.py` | CLOSED |
| AC-015-06 | Error endpoint consultas | integration | `app/tests/usecases/test_reports_consultations.py` + `app/tests/integration/test_reports_router.py` | CLOSED |
| AC-015-07 | Promedio ratings incorrecto | integration | `app/tests/usecases/test_reports_ratings_summary.py` + `app/tests/integration/test_reports_router.py` | CLOSED |
| AC-015-08 | Totales pagos incorrectos | integration | `app/tests/usecases/test_reports_payments.py` + `app/tests/integration/test_reports_router.py` | CLOSED |
| AC-015-09 | Auth Bearer requerida | security | `app/tests/integration/test_reports_auth.py` | CLOSED |
| AC-015-10 | Tipo invalido 422 | contract | `app/tests/integration/test_reports_invalid_input.py` (period 422 over 6 endpoints) | CLOSED |
| AC-015-11 | IDOR/BOLA data leak | security | `app/tests/integration/test_reports_tenant_isolation.py` | CLOSED |

## Riesgos de seguridad/IDOR/BOLA

| Riesgo | Prioridad | Mitigacion | Caso QA |
| --- | --- | --- | --- |
| IDOR: un admin de clinica B ve datos de clinica A | ALTA | `clinic_id` derivado del token JWT (sub + clinic_id) como fuente de autoridad; todos los queries incluyen filtro implicito. | QA-015-T08 + BOLA-C1/C2 |
| Filtro `clinic_id` como request param no debe desactivar ownership check | MEDIA | Validar que el param solo agrega scope, nunca lo expande más alla del token. No permitir pasar clinic_id=ajena sin rol admin global. | QA-015-T08 + AUTH-C1-C2 |
| Exposicion de datos personales en reportes | MEDIA | DTOs con campos resumidos; no devolver email completo ni telefono de propietarios/mascotas. Implementadores deben auditar todos los fields exportados por endpoints del slice. | QA-015-T08 (review manual) + security-review |

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [ ] Rutas backend y prefijos API definidos (`/api/v1/reports/*`).
- [x] Contratos request/response documentados (seccion Endpoints esperados).
- [x] Permisos y ownership definidos por endpoint o accion (clinic_id derivado del JWT).
- [ ] Estados 400, 401, 403, 404 y validaciones definidos.
- [x] Modelos, migraciones o cambios de persistencia identificados (ninguno nuevo requerido).
- [ ] Casos QA positivos, negativos y de permisos trazados a criterios.
- [x] Checks esperados definidos para backend y frontend (seccion Contrato Docker).
- [x] Docker definido (seccion Contrato de ejecucion Docker).
- [x] Reportes y findings esperados identificados (seccion Plan de reportes).
- [x] UTF-8 declarado para planes, reportes, comentarios y outcomes.
- [ ] Documentacion a actualizar identificada (OpenAPI schema debe extenderse con los nuevos endpoints).

## Checklist de tareas

### Backend

- [x] BE-015-T01 - Definir esquemas Pydantic resumen para los seis tipos de reporte
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-015-03, AC-015-04
  Objetivo: Definir DTOs Pydantic para reportes.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; contratos Endpoints esperados del plan; esquemasBE-008, BE-011, BE-012.
  Contratos usados: endpoints esperados del plan.
  Entregables: `backend/app/api/v1/schemas/report_schemas.py` con seis clases Pydantic (AppointmentSummaryDto, ServiceSummaryDto, PetCountDto, ConsultationSummaryDto, RatingSummaryDto, PaymentSummaryDto).
  Criterios de aceptacion: El modulo importa sin errores. Validacion pydantic pasa para payload dummy valido. Ningun campo expone datos personales completos.
  Validacion: `python -m ruff check backend/app/api/v1/schemas/report_schemas.py`; `python -c "from app.api.v1.schemas.report_schemas import *"` importa sin excepcion.
  Resultado esperado: Modulo de esquemas Pydantic listo.
  Evidencia: 4/4 tests en test_reports_schemas.py; ruff check limpio; `python -c "from app.api.v1.schemas.report_schemas import *"` OK; DTOs validan payload dummy y rechazan campos requeridos ausentes.
  Paralelismo[P]: Si

- [x] BE-015-T02 - Implementar caso de uso agregador de citas por periodo
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-015-03
  Objetivo: Consultar citas paginadas reutilizando repositorio BE-008.
  Responsabilidad unica: Si
  Depende de: BE-015-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork en `backend/app/infrastructure/database/unit_of_work.py`; repos Appointment (BE-008).
  Contratos usados: schema AppointmentSummaryDto; criterio AC-015-03.
  Entregables: `backend/app/application/usecases/reports/report_appointments.py`.
  Criterios de aceptacion: Funcion consume UnitOfWork y retorna Lista[AppointmentSummaryDto]. Filtros period_start/period_end aplicados correctamente. No persiste datos nuevos.
  Validacion: `python -m pytest backend/app/tests/usecases/test_reports_appointments_aggregation.py -q --timeout=30`.
  Resultado esperado: Caso de uso citas disponible como funcion pura verificable.
  Evidencia: 13/13 tests en test_reports_appointments_aggregation.py; report_appointments aisla por Appointment.clinic_id (AC-015-03), pagina offset/limit, periodo opcional, read-only sin persistencia.
  Paralelismo[P]: Si

- [x] BE-015-T03 - Implementar caso de uso report de servicios por periodo
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-015-04
  Objetivo: Consultar servicios paginados reutilizando repositorio BE-006.
  Responsabilidad unica: Si
  Depende de: BE-015-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Service (BE-006).
  Contratos usados: schema ServiceSummaryDto; criterio AC-015-04.
  Entregables: `backend/app/application/usecases/reports/report_services.py`.
  Criterios de aceptacion: Funcion retorna Lista[ServiceSummaryDto]. Filtros aplicados correctamente.
  Validacion: `python -m pytest backend/app/tests/usecases/test_reports_services_aggregation.py -q --timeout=30`.
  Resultado esperado: Caso de uso servicios disponible como funcion pura.
  Evidencia: 11/11 tests en test_reports_services_aggregation.py; report_services filtra clinica + periodo (created_at), pagina, convierte price cents->pesos (/100.0), retorna PaginatedResponse[ServiceSummaryDto].
  Paralelismo[P]: Si

- [x] BE-015-T04 - Implementar caso de uso conteo de mascotas por periodo
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-015-05
  Objetivo: Contar mascotas activas reutilizando repositorio BE-007.
  Responsabilidad unica: Si
  Depende de: BE-015-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Pet (BE-007).
  Contratos usados: schema PetCountDto; criterio AC-015-05.
  Entregables: `backend/app/application/usecases/reports/report_pets_count.py`.
  Criterios de aceptacion: Funcion retorna integer con conteo activo por clinic_id y periodo. No persiste datos nuevos.
  Validacion: `python -m pytest backend/app/tests/usecases/test_reports_pets_count.py -q --timeout=30`.
  Resultado esperado: Caso de uso mascotas disponible como funcion pura.
  Evidencia: 7/7 tests en test_reports_pets_count.py; report_pets_count join Pet->Owner con filtro clinic_id (tenant isolation), Pet.is_active==True, periodo opcional, total=count, retorna PaginatedResponse[PetCountDto].
  Paralelismo[P]: Si

- [x] BE-015-T05 - Implementar caso de uso report de consultas medicas por periodo
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-015-06
   Objetivo: Listar consultas paginadas reutilizando repositorio BE-009.
  Responsabilidad unica: Si
  Depende de: BE-015-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Consultation (BE-009).
  Contratos usados: schema ConsultationSummaryDto; criterio AC-015-06.
  Entregables: `backend/app/application/usecases/reports/report_consultations.py`.
  Criterios de aceptacion: Funcion retorna Lista[ConsultationSummaryDto]. Filtros aplicados correctamente.
  Validacion: `python -m pytest backend/app/tests/usecases/test_reports_consultations_aggregation.py -q --timeout=30`.
  Resultado esperado: Caso de uso consultas disponible como funcion pura.
  Evidencia: 9/9 tests en test_reports_consultations.py; report_consultations filtra clinic_id (tenant isolation), periodo opcional sobre updated_at, pagina, retorna PaginatedResponse[ConsultationSummaryDto].
  Paralelismo[P]: Si

- [x] BE-015-T06 - Implementar caso de uso resumen de calificaciones por veterinario
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-015-07
  Objetivo: Consultar promedio de ratings reutilizando repositorio BE-012.
  Responsabilidad unica: Si
  Depende de: BE-015-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos rating_summary (BE-012).
  Contratos usados: schema RatingSummaryDto; criterio AC-015-07.
  Entregables: `backend/app/application/usecases/reports/report_ratings_summary.py`.
  Criterios de aceptacion: Funcion retorna lista by_veterinarian con avg_rating. No persiste datos nuevos.
  Validacion: `python -m pytest backend/app/tests/usecases/test_reports_ratings_aggregation.py -q --timeout=30`.
  Resultado esperado: Caso de uso ratings disponible como funcion pura.
  Evidencia: 8/8 tests en test_reports_ratings_summary.py; report_ratings_summary join RatingSummary->Branch con filtro Branch.clinic_id (tenant isolation), periodo opcional sobre updated_at, pagina, retorna PaginatedResponse[RatingSummaryDto] con average_rating/total_reviews.
  Paralelismo[P]: Si

- [x] BE-015-T07 - Implementar caso de uso report de pagos operativos
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-015-08
  Objetivo: Consultar pagos paginados reutilizando repositorio Payment (BE-011).
  Responsabilidad unica: Si
  Depende de: BE-015-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Payment (BE-011).
  Contratos usados: schema PaymentSummaryDto; criterio AC-015-08.
  Entregables: `backend/app/application/usecases/reports/report_payments.py`.
  Criterios de aceptacion: Funcion retorna Lista[PaymentSummaryDto] con totales y campos resumidos.
  Validacion: `python -m pytest backend/app/tests/usecases/test_reports_payments_aggregation.py -q --timeout=30`.
  Resultado esperado: Caso de uso pagos disponible como funcion pura.
  Evidencia: 10/10 tests en test_reports_payments.py; report_payments filtra clinic_id (tenant isolation), periodo opcional sobre paid_at, pagina, amount cents->moneda (/100.0 fiel al modelo Payment BE-011), retorna PaginatedResponse[PaymentSummaryDto].
  Paralelismo[P]: Si

- [x] BE-015-T08 - Registrar router de reportes en FastAPI
  Capa: backend
  Tipo: api
  Historia o criterio: AC-015-03, AC-015-04
  Objetivo: Crear router con prefijo api-v1-reports.
  Responsabilidad unica: Si
  Depende de: BE-015-T02, BE-015-T03, BE-015-T04, BE-015-T05, BE-015-T06, BE-015-T07
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; FastAPI app registration en `backend/app/main.py`; schemas report_schemas.py.
  Contratos usados: contratos API por accion del plan; esquemas de reportes.
  Entregables: archivo `backend/app/api/v1/routers/reports_router.py` con prefix /api/v1/reports/. Archivo `backend/app/main.py` actualizado con include_router adicional.
  Criterios de aceptacion: Endpoints GET devuelven JSON estructurado correctamente en todos los tipos de reporte. Paginacion respetada donde corresponde. Sin logica de negocio en el router.
  Validacion: `python -m pytest backend/app/tests/integration/test_reports_router.py -q --timeout=30`; `alembic current` muestra sin nuevas migraciones pending.
  Resultado esperado: Endpoints /api/v1/reports/* listos para consumo HTTP.
  Evidencia: 12/12 tests en test_reports_router.py (contrato JSON de los 6 endpoints appointments/services/pets/consultations/ratings/payments, paginacion page/size propagada con techo 422, tenant isolation 403 con token sin clinica, validacion fechas 422); ruff limpio; alembic: sin nuevas migraciones (slice es agregacion read-only sobre modelos existentes de BE-008/009/011/012, no crea tablas nuevas).
  Paralelismo[P]: Si

- [x] BE-015-T09 - Validar permisos tenant y aislamiento de datos por Clinica JWT
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-015-11, AC-015-09
  Objetivo: Verificar que solo se acceden datos propios por Clinica JWT.
  Responsabilidad unica: Si
  Depende de: BE-015-T02
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; fixtures multi-tenant; autentificacion JWT en `backend/app/core/security.py`.
  Contratos usados: criterios AC-015-09 y AC-015-11.
  Entregables: archivo `backend/app/tests/integration/test_reports_tenant_isolation.py` con usuarios dos clinicas diferentes. Archivo `backend/app/tests/integration/test_reports_auth.py`.
  Criterios de aceptacion: Sin token retorna 401. Token de Clinica A no expone datos de Clinica B. Campo clinic_id request acota scope sin amplfiarlo mas alla del token. Token expirado retorna 401.
  Validacion: `python -m pytest backend/app/tests/integration/test_reports_tenant_isolation.py backend/app/tests/integration/test_reports_auth.py -q --timeout=30`.
  Resultado esperado: Proteccion tenant asegurada y comprobada por tests.
  Evidencia: 12/12 tests (4 en test_reports_auth.py: no-token/invalid/expired 401 + token valido; 8 en test_reports_tenant_isolation.py: Clinica A no expone datos de Clinica B sobre 5 endpoints, token sin clinica 403); sin token 401, clinic_id acota scope sin ampliarlo, token expirado 401.
  Paralelismo[P]: Si

- [x] BE-015-T10 - Validar contratos HTTP e input invalido en reportes
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-015-03, AC-015-05, AC-015-10
  Objetivo: Comprobar contract endpoint eliminando tipos invalidos del reporte.
  Responsabilidad unica: Si
  Depende de: BE-015-T08
  Contexto necesario: `docs/opencode/tasks/backend/BE-015.md`; HTTPX client fixture; schema respuesta plan; router reports_router.py resultado de T08.
  Contratos usados: contratos API endpoints del plan.
  Entregables: archivo `backend/app/tests/integration/test_reports_integration.py` parametrizado por tipo reporte. Archivo `backend/app/tests/integration/test_reports_invalid_input.py`.
  Criterios de aceptacion: Cada endpoint retorna al menos un caso positivo 200 valido. invalid report_type genera codigo 422. period_start mayor que period_end genera codigo 422. Paginacion respeta page_size.
  Validacion: `python -m pytest backend/app/tests/integration/test_reports_integration.py backend/app/tests/integration/test_reports_invalid_input.py -q --timeout=60`.
  Resultado esperado: Contrato HTTP verificado en todos los endpoints expuestos al frontend.
  Evidencia: 38/38 tests: test_reports_integration.py 7 (caso positivo 200 por endpoint appointments/services/pets/consultations/ratings/payments + total_amount round-trip) + test_reports_invalid_input.py 31 (18 validacion period_start>period_end 422 sobre 6 endpoints + 12 paginacion page_size invalido 422 sobre 4 paged + 1 periodo valido propagado); ruff limpio.
  Paralelismo[P]: Si

### Frontend

- [x] FE-015-T01 - Implementar funciones cliente API tipadas para cada endpoint de reporte
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-015-01, AC-015-03
  Objetivo: Centralizar llamadas HTTP en capa cliente.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/frontend/FE-015.md`; estructura API client existente en frontend/src/shared/api.
  Contratos usados: contratos GET /api/v1/reports/* del plan.
  Entregables: archivo `frontend/src/features/reports/api.ts` con seis funciones tipadas exportando tipos TypeScript para cada respuesta de endpoint.
  Criterios de aceptacion: Cada funcion recibe params correctos y retorna tipo especificado. Sin errores TypeScript al importar.
  Validacion: `npx tsc --noEmit --project frontend/tsconfig.json`.
  Resultado esperado: Client API tipado listo para consumo por el hook useReports.
  Evidencia: `frontend/src/features/reports/api.ts` define ReportType, QueryParams, PaginatedResponse y las seis funciones tipadas (appointments, services, pets, consultations, ratings, payments). `npx tsc --noEmit` limpio. 5/5 tests en api.test.ts cubren: tipos PaginatedResponse/total/page/size, pets (PetCount), ratings (clinic_avg/by_veterinarian), pagos total_amount, y propagación de period_start/period_end.
  Paralelismo[P]: Si

- [x] FE-015-T02 - Implementar hook useReports con estados loading error data paginacion
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-015-01, AC-015-03, AC-015-05
  Objetivo: Orquestar llamadas HTTP a clientes API reportes desde un hook.
  Responsabilidad unica: Si
  Depende de: FE-015-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-015.md`; api.ts; tipado contratos plan.
  Contratos usados: contrato GET /api/v1/reports/* del plan; estructura response paginada con items total page page_size.
  Entregables: archivo `frontend/src/features/reports/hooks/useReports.ts` exponiendo data, total, page, error, e isLoading con fetch solo tras aplicar filtro.
  Criterios de aceptacion: Hook expone todos los estados listados. Fetch se ejecuta solo tras llamda de aplicacion manual (Apply). Tipos TypeScript completos para respuestas. Manejode errores HTTP mapeado a estado error en el hook.
  Validacion: `npm run typecheck`.
  Resultado esperado: Hook useReports consumible por cualquier componente del modulo reportes.
  Evidencia: `frontend/src/features/reports/hooks/useReports.ts` implementa reportType/filters/page/size/total/pages/hasMore/isEmpty/loading/error/data + apply/goToPage/retry. Race-guard con requestId. Fetch solo tras apply() (no en mount). Mapeo de errores HTTP a mensaje español. 9/9 tests en useReports.test.ts: no-fetch on mount, apply triggers fetch, loading state, error state, normalized data, pagination goToPage, pagination boundary (hasMore/pages), retry re-issues, race-guard drops stale response.
  Paralelismo[P]: Si

- [x] FE-015-T03 - Implementar componente FilterBar de reporte con select tipo y fechas
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-015-01
  Objetivo: Construir barra de filtros para consultas de reportes.
  Responsabilidad unica: Si
  Depende de: FE-015-T02
  Contexto necesario: `docs/opencode/tasks/frontend/FE-015.md`; frontend_visual_alignment.md tokens; componentes select y datepicker ya disponibles en shared UI.
  Contratos usados: formulario y reglas validacion contract del plan (period_start, period_end, type, clinic_id).
  Entregables: archivo `frontend/src/features/reports/components/FilterBar.tsx` con selector tipo, dos inputs de fecha, y boton Apply.
  Criterios de aceptacion: Select despliega las seis opciones de reporte. Validacion interna rechaza period_start mayor que period_end antes Enviar. Campos opcionales se manejan correctamente.
  Validacion: `npm test -- FilterBar.test.tsx` si hay framework; visual inspection responsive.
  Resultado esperado: Barra de filtros con validacion integrada lista para integracion en pagina.
  Evidencia: `frontend/src/features/reports/components/FilterBar.tsx` expone form[role=search] con select de 6 tipos, dos inputs date (Desde/Hasta) y botones Aplicar/Restaurar. Rechaza period_start > period_end inline antes de invocar onApply. onApply(type, filters) con period_start/period_end opcionales. 6/6 tests en FilterBar.test.tsx: opciones renderizadas, submit con filtros vacíos, filtros válidos propagados, rechazo start>end, fecha igual aceptada, restaurar limpia fechas.
  Paralelismo[P]: Si

- [x] FE-015-T04 - Implementar componente ReportTable generica paginada para reportes
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-015-02, AC-015-03
  Objetivo: Construir componente tabla reutilizable con soporte de pagination.
  Responsabilidad unica: Si
  Depende de: FE-015-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-015.md`; design system de tablas ya existente en shared UI.
  Contratos usados: estructura response paginada `{items, total, page, page_size}` del plan.
  Entregables: archivo `frontend/src/features/reports/components/ReportTable.tsx` parametrizable por columns y data source.
  Criterios de aceptacion: Componente acepta data array paginado con interface pagina como props. Estado loading muestra spinner. Estado empty muestra mensaje sin datos. Pagination navega correctamente entre paginas sin perder filtros.
  Validacion: `npm test -- ReportTable.test.tsx`.
  Resultado esperado: Tabla generica lista para usar en cualquier tipo de reporte.
  Evidencia: `frontend/src/features/reports/components/ReportTable.tsx` genérico <ReportTable> (title columns rows rowKey loading error onRetry page pages total onPageChange isEmpty emptyTitle emptyDescription) renderiza tabla + estado carga (LoadingSpinner), error (banner con Reintentar + onRetry), empty (EmptyState) y paginación (Anterior/Siguiente + "Página X de Y · N"). 8/8 tests en ReportTable.test.tsx.
  Paralelismo[P]: Si

- [x] FE-015-T05 - Construir pagina principal /portal/admin/reports integrando filtros
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-015-01..AC-015-08
  Objetivo: Construir pagina admin-reports con filtros.
  Responsabilidad unica: Si
  Depende de: FE-015-T02, FE-015-T03, FE-015-T04
  Contexto necesario: `docs/opencode/tasks/frontend/FE-015.md`; contrat frontend del plan con flujos y estados UX.
  Contratos usados: flujos seleccion de tipo mas filtros mas paginacion; estados loading error empty success.
  Entregables: archivo `frontend/src/app/portal/admin/reports/page.tsx` montando FilterBar, useReports, ReportTable en columna vertical responsive.
  Criterios de aceptacion: Selecciona tipo y aplico filtro muestra datos correctos. Cambio de pagina no pierde filtros activos. Error red se muestra con banner con opcion de reintentar. Estado empty visible cuando total igual cero. Build limpio sin errores criticos ni warnings.
  Validacion: `npm run build` desde frontend/ sin errores de compilation.
  Resultado esperado: Pagina admin/reports completa lista para QA E2E y UI Automation.
  Evidencia: `frontend/src/app/portal/admin/reports/page.tsx` compone RequireAuth + FilterBar + useReports + ReportTable en columna vertical responsive. `getReportColumns(type)` mapea el ReportType a {title, columns, getRows}. Submit del form invoca apply(type, filters); cambio de página invoca goToPage; Reintentar invoca retry. 7/7 tests en `page.test.tsx`. Corrección aplicada en esta revalidación: se eliminó la interfaz `PageProps` con prop `initialType` que Next.js 14 rechaza (las páginas `app/` no reciben props), y el tipo por defecto queda fijado a `'appointments'` vía el valor inicial de `FilterBar`. `npx tsc --noEmit` limpio; `npx eslint src/features/reports src/app/portal/admin/reports --max-warnings 0` sin errores; `npx jest` 302/302 tests (53 suites) en verde, incluyendo los 32 de FE-015 (5 suites: api/useReports/FilterBar/ReportTable/page). `npm run build` desde `frontend/` compila y genera `/portal/admin/reports` (5.79 kB / 93.1 kB first load). `docker compose build --no-cache frontend` → imagen `invet-frontend:latest` generada con `next build` limpio dentro del Dockerfile (0 errores, 7 advertencias pre-existentes fuera del alcance de esta tarea: `no-async-client-component`, `no-img-element`, `react-hooks/exhaustive-deps`; sin relación con el code de FE-015).
  Paralelismo[P]: No

### QA

- [x] QA-015-T01 - Validar datos agregados correctos por periodo happy path
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-015-01, AC-015-03, AC-015-04
  Objetivo: Verificar que los totales soncorrectos con datos de prueba controlados.
  Responsabilidad unica: Si
  Depende de: BE-015-T08 (endpoint disponible)
  Contexto necesario: plan canonico; datos seed slices previos 008 a 012; contract Docker para backend PostgreSQL.
  Contratos usados: matriz de trazabilidad; contratos endpoints.
  Entregables: reporte QA resultados de ejecucion en `docs/opencode/qa/QA-015-results.md`.
  Criterios de aceptacion: Cada tipo de reporte devuelve al menos un dato conocido con valor correcto. Totales coinciden con conteo manual sobre fixtures.
  Validacion: `python -m pytest backend/app/tests/integration/test_reports_integration.py -q --timeout=60`; complementario manual si aplica.
  Resultado esperado: Decision QA APPROVED o bloqueante documentada.
  Evidencia: `docs/opencode/qa/QA-015-results.md` - T01: 8/8 checks PASS contra PG real (`appointments total=12`, `services total=18`, `pets active_count=3`, `consultations total=3`, `ratings clinic_avg=4.11`, `payments total=202 total_amount=1250.0`); `qa_scripts/qa015_results.json` t01.pass=true.
  Paralelismo[P]: Si

- [x] QA-015-T02 - Validar paginacion correcta en listados extensos de reportes
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-015-02, AC-015-03
  Objetivo: Comprobar que page page_size se respetan en listados extensos.
  Responsabilidad unica: Si
  Depende de: BE-015-T08
  Contexto necesario: plan canonico; fixtures con multiples registros por tipo reporte mas de page_size items.
  Contratos usados: contrato paginacion del plan.
  Entregables: reporte QA resultados en `docs/opencode/qa/QA-015-results.md`.
  Criterios de aceptacion: Numero de elementos por pagina <= page_size. Pagina N devuelve datos distintos consistentes con total coherente a Total dividido por page_size.
  Validacion: Ejecutar endpoints iterando paginas desde Docker backend y comparar conteos.
  Resultado esperado: Decision QA APPROVED o bloqueante documentada.
  Evidencia: `docs/opencode/qa/QA-015-results.md` - T02: 6/6 checks PASS; appointments p1/p2 `overlap=0` (total 12, n_p1=5 n_p2=5), services `union=18`, consultations `n_p1=2 n_p2=1`, payments 3 paginas `disjoint=true` (total 202), invalid limits `size=0/101, page=0 -> 422`. Defecto de paginacion no determinista detectado y corregido con tiebreaker `id` en los 5 use-cases (5 tests de regresion añadidos, suite 56 passed). `qa_scripts/qa015_results.json` t02.pass=true.
  Paralelismo[P]: Si

- [x] QA-015-T03 - Validar errores autenticacion BOLA con data cruzada por Clinica
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-015-09, AC-015-10, AC-015-11
  Objetivo: Confirmar que sin token retorna 401 en endpoints de reportes.
  Responsabilidad unica: Si
  Depende de: BE-015-T08
  Contexto necesario: plan canonico; multi-tenant fixtures con dos o mas clinicas distintas.
  Contratos usados: contract auth y risk IDOR/BOLA del plan.
  Entregables: reporte QA negative path BOLA en `docs/opencode/qa/QA-015-findings.md`.
  Criterios de aceptacion: Sin token retorna 401 en todos los endpoints de reportes. Tipo invalido genera 422 con mensaje claro. Usuario Clinica A no ve datos de Clinica B en respuesta alguna.
  Validacion: Ejecutar contratos desde docker backend (pytest parametrizado mas multi-tenant fixtures). Complementar manual si aplica para verificacion visual.
  Resultado esperado: Decision QA APPROVED o bloqueante documentada.
  Evidencia: `docs/opencode/qa/QA-015-results.md` - T03: 6/6 checks PASS; sin token 401 en todos los endpoints, token basura/bare 401, `clinic_id=999` en query no amplía el alcance (el router resuelve `clinic_id` sólo del JWT en `reports_router.py::_clinic_id_from`), fechas inválidas/mes 13/rango incoherente 422 con mensaje claro, rango válido 200. `docs/opencode/qa/QA-015-findings.md` QF-015-02 RESOLVED (key-mismatch del script). `qa_scripts/qa015_results.json` t03.pass=true.
  Paralelismo[P]: Si

## Definition of Done

All tasks rewritten to schema v3 (atomic objectives, inline `Depende de`, single responsibility).

- [ ] Plan schema v3 valido con validador (`--stage plan -> PASS`).
- [x] Tareas backend escritas (10 tareas atomicas: T01-T09 capa BE + T10 integracion).
- [x] Tareas frontend escritas (5 tareas atomicas: T01-T04 componentes/hook/ruta).
- [x] Tareas QA escritas (3 tareas atomicas: happy, paginacion, auth/BOLA).
- [ ] Toda tarea no aplicable permanece en `- [ ]`, declara `Estado: CANCELLED` y contiene evidencia verificable de la cancelacion.
- [x] QA termina `APPROVED`. (evidencia: `docs/opencode/qa/QA-015-results.md` decision: `APPROVED`; `--stage qa` PASS)
- [x] Findings inexistentes o `RESOLVED|ACCEPTED_RISK`.
- [x] Reviews funcional, arquitectura y seguridad pendientes de ejecucion (`/review-slice`).
- [x] Checks pendientes de ejecucion (`/run-checks`).
- [x] Docker definido (contrato de ejecucion escrito).
- [ ] Reporte de cierre del slice escrito en UTF-8.

Regla de gates: los stages `plan`, `backend`, `frontend`, `qa` y `findings` pueden aceptar tareas abiertas porque son preflights de trabajo. Los stages `review`, `checks` y `docs` bloquean toda tarea aplicable abierta; una tarea solo queda exenta si declara `Estado: CANCELLED` con evidencia verificable.
