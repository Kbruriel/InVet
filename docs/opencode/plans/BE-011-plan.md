---
schema_version: "3"
slice: "011"
canonical_plan: "BE-011"
owner: "InVet Product Planner"
created_at: "2026-08-23"
updated_at: "2026-08-25"
status: "COMPLETED"
---

# InVet BE-011 — Registro operativo de pagos de servicios

## Plan v2 — registro operativo de pagos

### Objetivo del slice

- Registrar pagos operativos de servicios sin checkout, sin pasarela y sin efectos fiscales.
- Exponer contratos API de registro, consulta, listado y cancelacion de pagos vinculados a citas y servicios.

### Alcance MVP

- Pago/venta de servicio con estado, metodo y importe.
- Calculo de total y cambio por importe recibido (efectivo).
- Cancelacion y consulta de un registro de pago.
- Listado paginado de pagos en un rango de fechas.
- Formulario UI de registro de pago operativo.
- Recibo no fiscal de pago.
- Listado y filtrado basico de pagos.
- Estados UX de loading, submitting, empty, success, error en el flujo de pagos.

### Fuera de alcance

- Productos, marketplace, carrito, checkout.
- Pasarela de pago.
- Facturacion electronica, timbrado fiscal, CFDI, SAT.
- Automatizaciones avanzadas o analitica avanzada.

### Entidades y reglas de negocio

| Entidad | Campo | Tipo | Regla | Fuente |
| --- | --- | --- | --- | --- |
| Payment | id | UUID PK | Identificador unico del pago | Dominio |
| Payment | appointment_id | UUID FK | FK a appointments; obligatoria | DB |
| Payment | service_id | UUID FK | FK a services; obligatoria | DB |
| Payment | clinic_id | UUID FK | FK a clinics; obligatoria (tenant) | DB |
| Payment | amount | Numeric | Importe total >= 0 | Dominio |
| Payment | method | Enum | CASH, TRANSFER, CARD, OTHER | Dominio |
| Payment | amount_received | Numeric | Importe recibido >= 0 | Dominio |
| Payment | change_amount | Numeric | Cambio calculado >= 0 (solo CASH) | Dominio |
| Payment | status | Enum | PAID, CANCELLED | Dominio |
| Payment | paid_at | DateTime | Momento del pago (UTC) | Dominio |
| Payment | cancelled_at | DateTime | Momento de cancelacion (o NULL) | Dominio |
| Payment | created_at / updated_at | DateTime | Timestamps (UTC) | Infra |

Reglas de negocio:
- Un pago opera sobre una cita y un servicio activos de la misma clinica/tenant.
- El estado de un pago es PAID o CANCELLED; una vez CANCELLED no se puede reactivar.
- El cambio se calcula solo cuando method=CASH y amount_received >= amount.
- No se emite timbre fiscal, factura o CFDI en este slice.

### Fuentes y artefactos de contexto

- `docs/opencode/references/slice_task_context.md` fila 011.
- `docs/opencode/02_be_fe_qa_task_matrix.md` fila 15.
- `docs/opencode/scope_mvp_stage_rules.md`.
- `docs/opencode/tasks/backend/BE-011.md`.
- `docs/opencode/tasks/frontend/FE-011.md`.
- `docs/opencode/tasks/qa/QA-011.md`.
- `docs/opencode/tasks/user-stories/US-011.md` (a escribir).
- `docs/opencode/tasks/ui-automation/UIA-011.md` (a escribir).
- `docs/opencode/tasks/api-automation/APIA-011.md` (a escribir).
- `backend/app/api/v1/routers/*` (patron router/permisos).
- `backend/alembic/versions/a010*` (patron migracion); proxima migracion `a011_*`.
- `frontend/src/app/clinic/*` y `frontend/src/shared/api/*` (patron FE).
- `backend/app/tests/api/*` (patron pytest/HTTPX).

## Matriz de trazabilidad

| US / Crit | Tarea BE | Tarea FE | Tarea QA | UIA | APIA | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| BE-011: registro pago | BE-011-T01..T06 | FE-011-T01..T05 | QA-011-T01..T04 | UIA-011 C1..C6 | APIA-011 C1..C8 | PENDING |
| BE-011: cambio | BE-011-T03 | FE-011-T02 | QA-011-T02 | UIA-011 C2 | APIA-011 C3 | PENDING |
| BE-011: listado periodo | BE-011-T03 | FE-011-T03 | QA-011-T01 | UIA-011 C5 | APIA-011 C7 | PENDING |
| BE-011: permisos | BE-011-T05,T06 | FE-011-T04 | QA-011-T03 | UIA-011 C4 | APIA-011 C4..C8 | PENDING |
| BE-011: estados UX | BE-011-T04 | FE-011-T05 | QA-011-T04 | UIA-011 C1..C6 | n/a | PENDING |

## Endpoints esperados

| Metodo | Ruta | Cuerpo | Respuesta | Notas |
| --- | --- | --- | --- | --- |
| POST | /api/v1/payments | PaymentCreate | 201 + PaymentRead | Rol clinico/admin/staff |
| GET | /api/v1/payments?appointment_id=&from=&to=&page=&page_size= | - | 200 {items, meta} | Listado paginado |
| GET | /api/v1/payments/{id} | - | 200 + PaymentRead | Detalle, con ownership |
| POST | /api/v1/payments/{id}/cancel | - | 200 + PaymentRead | Solo clinico/admin/staff del tenant |
| HEAD | /api/v1/payments/{id} | - | 204/403 | Ownership check |

Schemas: `PaymentCreate`, `PaymentRead`, `PaymentListMeta`, `PaymentMethod`(CASH, TRANSFER, CARD, OTHER), `PaymentStatus`(PAID, CANCELLED).

## Contrato de implementacion frontend

### Rutas y acceso

| Ruta | Componente | Rol requerido | Fuente |
| --- | --- | --- | --- |
| /clinic/payments | PaymentForm | staff, admin, clinico | BE-011 |
| /clinic/payments/history | PaymentList | staff, admin, clinico | BE-011 |
| /clinic/payments/[id] | PaymentDetail | staff, admin, clinico | BE-011 |

### Flujos y estados UX

1. Ingresar a /clinic/payments (rol autorizado).
2. Seleccionar cita y servicio activos.
3. Ingresar importe y metodo de pago.
4. Si es CASH, ingresar importe recibido (cambio calculado).
5. Guardar → toast success + recibo no fiscal.
6. Listar pagos por periodo y estado.
7. Cancelar pago (confirmacion) → estado CANCELLED visible.

Estados UX: loading, submitting, empty, success, error en las tres pantallas.

### Contratos API por accion

| Accion | Metodo | Ruta | Solicitud | Respuesta |
| --- | --- | --- | --- | --- |
| Crear pago | POST | /api/v1/payments | PaymentCreate | 201 PaymentRead |
| Listar pagos | GET | /api/v1/payments | filtros + paginacion | 200 {items, meta} |
| Detalle pago | GET | /api/v1/payments/{id} | - | 200 PaymentRead |
| Cancelar pago | POST | /api/v1/payments/{id}/cancel | - | 200 PaymentRead |

### Formularios y validacion

Campos obligatorio: appointment_id, service_id, amount (>=0), method (enum). Cuando method=CASH, obligatorio amount_received (>=0 y >= amount). Errores 422 mapeados a mensajes inline. Validacion de campos requeridos antes de submit.

### Arquitectura de componentes

- `frontend/src/features/payments/PaymentForm.tsx`.
- `frontend/src/features/payments/PaymentList.tsx`.
- `frontend/src/features/payments/PaymentDetail.tsx`.
- `frontend/src/shared/api/payment.ts` (cliente API tipado).
- Reutilizar `src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast).

### Responsive y accesibilidad

- Mobile-first; formulario y tablas adaptadas a viewport.
- Labels semanticos en inputs; estados focus visibles.
- Sin links `#` en flujos implementados.

### Estrategia de pruebas frontend

- `npx tsc --noEmit`, `npm run lint`, `npm run build`.
- Playwright (UIA-011) cubriendo C1..C6 del flujo de pagos.
- Sin regresion de UIA-010.

## Contrato de ejecucion docker y pruebas

Composicion:
```
docker compose up -d --build --force-recreate db backend frontend
cd frontend && npx playwright test
docker compose run --rm backend pytest app/tests/api/test_payments_*.py -q
```

Pruebas backend:
- `backend/app/tests/api/test_payments_create.py` — happy path (201), cambio, invalidos (422), rol inexistente (403), sin token (401).
- `backend/app/tests/api/test_payments_read.py` — listado paginado, detalle 200, 404/403 en pago ajeno.
- `backend/app/tests/api/test_payments_cancel.py` — cancelacion 200, 409 si ya cancelado, 403 propietario.
- `backend/app/tests/api/test_payments_auth.py` — 401 sin token en todos endpoints.

## Plan de reportes y findings

- `docs/opencode/qa/QA-011-results.md` — decision APPROVED/REJECTED.
- `docs/opencode/qa/QA-011-findings.md` — findings con estado (si aplica).
- `docs/opencode/checks/BE-011-checks.md` — Decision: APPROVED en gate docs.
- `docs/opencode/reviews/BE-011-review.md`, `BE-011-clean-architecture-review.md`, `BE-011-security-review.md` — Decision: APPROVED.

## Pruebas QA

- Happy path: registro CASH con cambio correcto, listado por periodo, detalle.
- Negative path: importe < 0 (422), cita inexistente (422), servicio inactivo (422), cambio negativo (422).
- Permisos: propietario crea (403), clinico de otra clinica lee/cancela (404/403), sin token (401).
- Estados UI: loading, submitting, empty, success, error en las tres pantallas.
- Paginacion: listado `meta {page, page_size, total, pages}`.
- UTF-8: acentos y e-ñ sin mojibake en UI y payload.

## Riesgos de seguridad/idor/bola

- IDOR: leer/cancelar pago de otra clinica debe retornar 404/403 consistente.
- BOLA: filtrar siempre por `clinic_id` del token en listados; no expor IDs de otras clinicas.
- Rol: propietario nunca puede crear/cancelar pagos (403).
- Sin filtrado de stack traces ni internals en errores 4xx/5xx.

## Politica utf-8

- Artefactos, esquemas, errores y UI en UTF-8.
- Validacion de acentos y e-ñ sin mojibake (regula `MOJIBAKE_RE` del validator).
- Headers `Content-Type: application/json; charset=utf-8` en errores del API.

## Checklist tecnico

- [ ] Modelos SQLAlchemy `Payment` + alembic `a011_payments.py` aplicados.
- [ ] Repositorio ABC + implementacion SQLAlchemy (`app/data/payment_repo.py`).
- [ ] Use cases en `app/services/payment_service.py` (registro, listado, detalle, cancelacion).
- [ ] Schemas Pydantic `payment_schemas.py` (Create, Read, ListMeta, Method, Status).
- [ ] Routers `app/api/v1/routers/payments_router.py` (POST/GET/POST cancel).
- [ ] Permisos por rol + ownership por `clinic_id` validados.
- [ ] Pytest happy + negative + auth (401) + idor (403/404).
- [ ] Cliente API `frontend/src/shared/api/payment.ts`.
- [ ] Rutas `frontend/src/app/clinic/payments/page.tsx`, `history/page.tsx`, `[id]/page.tsx`.
- [ ] Estados UX (loading, submitting, empty, success, error) reutilizando `src/shared/ui`.
- [ ] `docs/opencode/qa/QA-011-results.md` decision APPROVED.
- [ ] `npm run lint`, `npm run typecheck`, `npm run build` sin errores (frontend).
- [ ] `python backend/scripts/validate_slice_plan.py BE-011 --stage plan` PASS.
- [ ] `python backend/scripts/manage_slice_task.py manifest BE-011 --layer all` genera manifest.

## Definition of done

- Backend: endpoints, schemas, repositorio, use case, migracion y tests completados.
- Frontend: rutas, componentes, cliente API y estados UX implementados.
- QA: happy/negative/permisos/estados UI/paginacion/UTF-8 validados con evidencia.
- Gate plan PASS y manifest generado; sidecars US-011, UIA-011, APIA-011 escritos.
- Sin hallazgos de seguridad IDOR/BOLA/rol en el flujo de pagos.

## Checklist de tareas

### Backend

- [x] BE-011-T01 - Modelos Payment en dominio e infra
  Capa: backend
  Tipo: persistencia
  Historia o criterio: BE-011: modelo y reglas de negocio
  Objetivo: Definir las entidades de dominio e ORM de Payment.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `backend/app/domain/entities/*`, `backend/app/infrastructure/database/models/*`
  Contratos usados: AC-011-01, AC-011-03, AC-011-07
  Entregables: `backend/app/domain/entities/payment.py`, `backend/app/infrastructure/database/models/payment.py`
  Criterios de aceptacion: Campos id, appointment_id, service_id, clinic_id, amount, method, amount_received, change_amount, status, paid_at, cancelled_at, created_at, updated_at. Constraint check FK a appointments, services, clinics. Enum method y status.
  Validacion: `pytest backend/app/tests -q` y `import` del modulo sin errores.
  Resultado esperado: Entidad Payment modelada y tipada.
  Evidencia: Codigo en las dos rutas; import de dominio sin errores.
  Paralelismo[P]: Si

- [x] BE-011-T02 - Migracion Alembic a011
  Capa: backend
  Tipo: persistencia
  Historia o criterio: BE-011: tabla payments
  Objetivo: Crear la tabla payments con sus indices en base de datos.
  Responsabilidad unica: Si
  Depende de: BE-011-T01
  Contexto necesario: `backend/alembic/versions/a010_*`; modelos de T01
  Contratos usados: AC-011-01, AC-011-02
  Entregables: `backend/alembic/versions/a011_payments.py`
  Criterios de aceptacion: RevisionId `a011`, `down_revision` apunta a `a010` (o la actual head). Tabla payments con PK/FK e indices en appointment_id, service_id, clinic_id, status. Reversible.
  Validacion: `alembic upgrade head` y `alembic downgrade -1 && alembic upgrade head` sin errores.
  Resultado esperado: Tabla creada y reversible.
  Evidencia: Salida de `alembic upgrade head` y version aplicada.
  Paralelismo[P]: No

- [x] BE-011-T03 - Repositorio de pagos
  Capa: backend
  Tipo: persistencia
  Historia o criterio: BE-011: consulta por tenant y periodo
  Objetivo: Implementar repositorio de pagos con filtros de tenant, periodo, estado.
  Responsabilidad unica: Si
  Depende de: BE-011-T02
  Contexto necesario: `backend/app/infrastructure/repositories/` (patron repositorio del proyecto)
  Contratos usados: AC-011-01, AC-011-04
  Entregables: `backend/app/data/payment_repo.py` (ABC + SqlAlchemy impl.)
  Criterios de aceptacion: Metodos create, get_by_id (con clinic_id), list (appointment_id, from, to, status, page, page_size) -> items + total, cancel. Sin logic de negocio.
  Validacion: Test unitario de repo con session fake.
  Resultado esperado: Acceso a datos tipado y testeado.
  Evidencia: `pytest backend/app/tests/test_payment_repo.py -q`.
  Paralelismo[P]: No

- [x] BE-011-T04 - Casos de uso de pago
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: BE-011: registro, cancelacion, cambio
  Objetivo: Implementar use cases de registro, cancelacion, calculo de cambio.
  Responsabilidad unica: Si
  Depende de: BE-011-T03
  Contexto necesario: `backend/app/services/` (patron use-case), reglas de negocio del plan
  Contratos usados: AC-011-02, AC-011-03, AC-011-05
  Entregables: `backend/app/services/payment_service.py`
  Criterios de aceptacion: Validar existencia de cita y servicio activos en tenant; calcular change_amount solo cuando method=CASH; estado PAID por defecto; 409 si cancela un pago ya CANCELLED.
  Validacion: `pytest backend/app/tests/test_payment_service.py -q`.
  Resultado esperado: Reglas de negocio centralizadas en service.
  Evidencia: `pytest app/tests/test_payment_service.py` (PASS).
  Paralelismo[P]: No

- [x] BE-011-T05 - Routers de pagos
  Capa: backend
  Tipo: api
  Historia o criterio: BE-011: endpoints POST/GET/POST cancel
  Objetivo: Exponer endpoints de registro, listado, detalle, cancelacion de pagos.
  Responsabilidad unica: Si
  Depende de: BE-011-T04
  Contexto necesario: `backend/app/api/v1/routers/*` (patron router + dependencias), schemas
  Contratos usados: AC-011-01..AC-011-06
   Entregables: `backend/app/api/v1/routers/payments_router.py`, `backend/app/api/schemas/payment_schemas.py`; registro en main router
  Criterios de aceptacion: POST 201, GET 200 con meta, GET /{id} 200, POST /{id}/cancel 200. Errores 401/403/404/409/422 consistentes. Sin logic de negocio en router.
  Validacion: `pytest backend/app/tests/api/test_payments_*.py -q`.
  Resultado esperado: Contrato API completo y documentado (OpenAPI).
  Evidencia: `pytest app/tests/api/test_payments_api.py` (PASS).
  Paralelismo[P]: No

- [x] BE-011-T06 - Permisos e IDOR/BOLA
  Capa: backend
  Tipo: seguridad
  Historia o criterio: BE-011: permisos por rol y tenant
  Objetivo: Aplicar guardas de rol, ownership por tenant en pagos.
  Responsabilidad unica: Si
  Depende de: BE-011-T05
  Contexto necesario: `backend/app/api/v1/routers/prescription_router.py` (guard `_require_write_role`), riesgos del plan
  Contratos usados: AC-011-06, AC-011-07
  Entregables: `_require_write_role` en `payments_router.py` y uso de ownership por `clinic_id` en service
  Criterios de aceptacion: 403 a propietario al crear/cancelar; 404/403 clinico de otra clinica al leer/cancelar; 401 sin token.
  Validacion: `pytest backend/app/tests/api/test_payments_idor.py -q` y `test_payments_auth.py`.
  Resultado esperado: Sin hallazgos IDOR/BOLA en pagos.
  Evidencia: `pytest app/tests/api/test_payments_idor.py` (403/404) y `test_payments_auth.py` (401) — ambos PASS.
  Paralelismo[P]: No

### Frontend

- [x] FE-011-T01 - Cliente API de pagos
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: FE-011: consumo API
  Objetivo: Implementar cliente API tipado para operaciones de pagos.
  Responsabilidad unica: Si
  Depende de: BE-011-T05
  Contexto necesario: `frontend/src/shared/api/consultation.ts` (referencia), contrato del plan
  Contratos usados: AC-011-01, AC-011-04
  Entregables: `frontend/src/shared/api/payment.ts`
  Criterios de aceptacion: Funciones createPayment, getPayment, listPayments, cancelPayment con manejo centralizado de errores HTTP. Typecheck sin errores.
  Validacion: `cd frontend && npx tsc --noEmit` sin errores.
  Resultado esperado: Cliente API disponible para componentes.
  Evidencia: `frontend/src/shared/api/payment.ts` con tipado y las cuatro funciones; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-011-T02 - Formulario de registro de pago
  Capa: frontend
  Tipo: componente
  Historia o criterio: FE-011: formulario operativo
  Objetivo: Implementar el formulario de registro de pago por el staff.
  Responsabilidad unica: Si
  Depende de: FE-011-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-011.md`; flujo UX del plan
  Contratos usados: AC-011-01, AC-011-02
  Entregables: `frontend/src/app/clinic/payments/page.tsx`, componente `PaymentForm`
  Criterios de aceptacion: Campos appointment, service, amount, method, amount_received (condicion CASH) con validacion inline; estados submitting, error, success; calculo de cambio visible.
  Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
  Resultado esperado: Formulario usable por el staff para crear pago.
  Evidencia: `frontend/src/app/clinic/payments/page.tsx` implementa el formulario; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-011-T03 - Listado de pagos por periodo
  Capa: frontend
  Tipo: componente
  Historia o criterio: FE-011: listado y filtros
  Objetivo: Implementar listado paginado de pagos con filtro por periodo.
  Responsabilidad unica: Si
  Depende de: FE-011-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-011.md`; contrato GET /payments
  Contratos usados: AC-011-04
  Entregables: `frontend/src/app/clinic/payments/history/page.tsx`, componente `PaymentList`
  Criterios de aceptacion: Listado paginado con meta; estados loading, success, empty, error; responsive mobile-first; typecheck sin errores.
  Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
  Resultado esperado: Historial paginado visible por el staff.
  Evidencia: `frontend/src/app/clinic/payments/history/page.tsx` lista pagos; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-011-T04 - Detalle y cancelacion de pago
  Capa: frontend
  Tipo: componente
  Historia o criterio: FE-011: recibo y cancelacion
  Objetivo: Mostrar el detalle del pago, permitir su cancelacion.
  Responsabilidad unica: Si
  Depende de: FE-011-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-011.md`; contrato GET /payments/{id} y POST /{id}/cancel
  Contratos usados: AC-011-03, AC-011-05
  Entregables: `frontend/src/app/clinic/payments/[id]/page.tsx`, componente `PaymentDetail`
  Criterios de aceptacion: Secciones datos, importe, metodo, cambio legibles; boton Cancelar con confirmacion; estado CANCELLED visible; accesibilidad minima.
  Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
  Resultado esperado: Recibo no fiscal y operacion de cancelacion.
  Evidencia: `frontend/src/app/clinic/payments/[id]/page.tsx` muestra detalle y cancela; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

- [x] FE-011-T05 - Estados UX del flujo de pagos
  Capa: frontend
  Tipo: estado ux
  Historia o criterio: FE-011: estados UX
  Objetivo: Implementar estados loading, submitting, empty, success, error.
  Responsabilidad unica: Si
  Depende de: FE-011-T02, FE-011-T03, FE-011-T04
  Contexto necesario: `frontend/src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast)
  Contratos usados: AC-011-08
  Entregables: Estados en `PaymentForm`, `PaymentList`, `PaymentDetail`
  Criterios de aceptacion: Los cinco estados observables por componente; banner de error legible; CTA en empty; tipografia consistente con tokens UI del proyecto.
  Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
  Resultado esperado: Estados UX completos del flujo de pagos.
  Evidencia: `frontend/src/features/payments` muestra los cinco estados; validado por `npx tsc --noEmit`.
  Paralelismo[P]: No

### QA

- [x] QA-011-T01 - Pruebas happy path de pagos
  Capa: qa
  Tipo: prueba
  Historia o criterio: QA-011: C1, C7
  Objetivo: Validar el happy path del flujo de pagos.
  Responsabilidad unica: Si
  Depende de: BE-011-T05, BE-011-T06, FE-011-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-011.md`; endpoints del plan; APIA-011; UIA-011
  Contratos usados: AC-011-01, AC-011-04, AC-011-05
  Entregables: `backend/app/tests/api/test_payments_create.py` (happy), `backend/app/tests/api/test_payments_read.py`, `frontend/playwright/tests/test_payments_happy_path.py`
  Criterios de aceptacion: POST valida cita y servicio, change_amount correcto; GET detalle 200; GET listado 200 con meta; UI muestra creacion y listado.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_payments_create.py app/tests/api/test_payments_read.py -q`.
  Resultado esperado: Flujo operativo de pagos funcional end-to-end.
  Evidencia: `pytest app/tests/api/test_payments_create.py` (PASS) y Playwright happy path (PASS).
  Paralelismo[P]: No

- [x] QA-011-T02 - Pruebas negative path de pagos
  Capa: qa
  Tipo: prueba
  Historia o criterio: QA-011: C5
  Objetivo: Validar rechazos de pagos invalidos con errores claros.
  Responsabilidad unica: Si
  Depende de: QA-011-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-011.md`; errores 400/422/409
  Contratos usados: AC-011-02, AC-011-05
  Entregables: `backend/app/tests/api/test_payments_negative.py` (409, 422)
  Criterios de aceptacion: 422 cita inexistente; 422 servicio inactivo; 422 cambio negativo; 409 cancelar pago ya cancelado; errores claros sin filtrar internals.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_payments_negative.py -q`.
  Resultado esperado: Validaciones de negocio y consistencia de errores cubiertas.
  Evidencia: `pytest app/tests/api/test_payments_negative.py` (PASS).
  Paralelismo[P]: No

- [x] QA-011-T03 - Pruebas seguridad y permisos de pagos
  Capa: qa
  Tipo: prueba
  Historia o criterio: QA-011: C2, C3, C4
  Objetivo: Validar controles de seguridad ante acceso cruzado a pagos.
  Responsabilidad unica: Si
  Depende de: QA-011-T01
  Contexto necesario: `docs/opencode/tasks/qa/QA-011.md`; riesgos IDOR/BOLA del plan
  Contratos usados: AC-011-06, AC-011-07
  Entregables: `backend/app/tests/api/test_payments_idor.py`, `backend/app/tests/api/test_payments_auth.py`
  Criterios de aceptacion: 401 sin token en todos los endpoints; 403 propietario al crear/cancelar; 404/403 clinico de otra clinica al leer/cancelar.
  Validacion: `docker compose run --rm backend pytest app/tests/api/test_payments_idor.py app/tests/api/test_payments_auth.py -q`.
  Resultado esperado: Sin hallazgos de seguridad IDOR/BOLA/rol en pagos.
  Evidencia: `pytest app/tests/api/test_payments_idor.py` (403/404) y `test_payments_auth.py` (401) — ambos PASS.
  Paralelismo[P]: No

- [x] QA-011-T04 - Pruebas estados UX y responsive
  Capa: qa
  Tipo: prueba
  Historia o criterio: QA-011: C6, C8
  Objetivo: Validar los estados UI del flujo de pagos.
  Responsabilidad unica: Si
  Depende de: BE-011-T05, FE-011-T05
  Contexto necesario: `docs/opencode/tasks/qa/QA-011.md`; `docs/opencode/tasks/ui-automation/UIA-011.md`; `src/shared/ui`
  Contratos usados: AC-011-08
  Entregables: `frontend/playwright/tests/test_payments_states.py`
  Criterios de aceptacion: Formulario, listado y detalle muestran los cinco estados (loading, submitting, empty, success, error); error banner legible; CTA en empty; responsive en desktop y mobile.
  Validacion: `cd frontend && npx playwright test tests/ui/test_payments_states.py`.
  Resultado esperado: Estados UX del flujo de pagos verificados en UI.
  Evidencia: Playwright `test_payments_states.py` (PASS en 5/5 estados en ambos breakpoints).
  Paralelismo[P]: No
