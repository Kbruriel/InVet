---
schema_version: "3"
slice: "014"
canonical_plan: "BE-014"
owner: "InVet Product Planner"
created_at: "2026-09-01"
updated_at: "2026-09-01"
status: "IN_PROGRESS"
encoding: "UTF-8"
---

# BE-014 Plan — Soporte básico

## Objetivo del slice

Entregar la gestión básica de tickets de soporte para usuarios autenticados de una clínica, con creación, consulta, categorías y transición controlada de estados.

## Brief operativo del slice

BE-014 habilita a una persona usuaria para registrar una solicitud de soporte y seguir su avance. El personal interno de la clínica puede consultar los tickets de su clínica y actualizar su estado según las reglas del dominio.

## Alcance MVP

- Crear tickets con título, descripción opcional y categoría opcional.
- Consultar categorías activas de la clínica autenticada.
- Listar tickets con paginación y filtro de estado.
- Consultar el detalle de un ticket autorizado.
- Cambiar el estado de un ticket mediante transiciones permitidas.
- Exponer el flujo en una interfaz protegida de soporte.

## Fuera de alcance

- Adjuntos, comentarios, notificaciones y asignación de agentes.
- Panel de administración global de categorías.
- Búsqueda de texto completo, métricas operativas o acuerdos de servicio.
- Edición del contenido de tickets después de su creación.

## Entidades y reglas de negocio

| Entidad | Campos relevantes | Reglas |
|---|---|---|
| SupportTicket | id, clinic_id, owner_id, title, description, category_id, status, created_at | title requerido entre 5 y 200 caracteres; description máxima de 2000; clinic_id y owner_id proceden del token. |
| SupportCategory | id, clinic_id, name, active | Nombre único por clínica; sólo se devuelven categorías activas. |
| TicketStatus | initiated, pendiente, proceso, completado, cerrado | initiated puede pasar a pendiente o proceso; proceso puede pasar a completado o cerrado. |

No se permite crear dos tickets con el mismo título para la misma persona durante 24 horas. Una lectura fuera de clínica o propiedad responde con 404 seguro. El personal interno puede consultar tickets de su clínica.

## Fuentes y artefactos de contexto

- docs/opencode/requirements/US-014.md
- docs/opencode/requirements/BE-014.md
- docs/opencode/requirements/FE-014.md
- docs/opencode/requirements/QA-014.md
- backend/app
- frontend/src
- backend/scripts/validate_slice_plan.py

## Matriz de trazabilidad

| Criterio | Tareas | Evidencia prevista |
|---|---|---|
| AC-01 Crear ticket | BE-014-T01, BE-014-T03, BE-014-T04, QA-014-T01 | Prueba API de creación válida e inválida. |
| AC-02 Categorías activas | BE-014-T01, BE-014-T04, FE-014-T01, QA-014-T01 | Respuesta de categorías limitada a clínica. |
| AC-03 Listado | BE-014-T02, BE-014-T04, FE-014-T02, QA-014-T02 | Prueba paginada con filtro. |
| AC-04 Detalle autorizado | BE-014-T02, BE-014-T04, FE-014-T03, QA-014-T03 | 200 propio y 404 ajeno. |
| AC-05 Transiciones | BE-014-T03, BE-014-T04, QA-014-T01 | Casos válidos e inválidos. |
| AC-06 Datos iniciales | BE-014-T01, QA-014-T02 | Migración con categorías mínimas. |
| AC-07 Autenticación | BE-014-T04, FE-014-T01, QA-014-T03 | Casos 401 y 403. |
| AC-08 Formulario | FE-014-T01, FE-014-T02, QA-014-T04 | Validación visual y envío. |
| AC-09 Estados de lista | FE-014-T02, QA-014-T04 | Carga, vacío, error y datos. |
| AC-10 Reversión | BE-014-T01, QA-014-T02 | Migración reversible. |
| AC-11 Aislamiento | BE-014-T02, BE-014-T04, QA-014-T03 | Pruebas IDOR y BOLA. |

## Endpoints esperados

| Método | Ruta | Actor | Resultado |
|---|---|---|---|
| POST | /api/v1/tickets | Usuario autenticado | Crea un ticket y devuelve 201. |
| GET | /api/v1/tickets | Usuario o personal interno | Devuelve lista paginada de la clínica. |
| GET | /api/v1/tickets/{ticket_id} | Usuario o personal interno | Devuelve el ticket autorizado. |
| PATCH | /api/v1/tickets/{ticket_id}/status | Personal interno | Cambia el estado según transición válida. |
| GET | /api/v1/tickets/categories | Usuario autenticado | Devuelve categorías activas de la clínica. |

Los errores usan el formato estándar de la API. page_size admite de 5 a 100. El filtro status acepta únicamente valores del enum TicketStatus.

## Contrato de implementacion frontend

La interfaz consume los endpoints sin reconstruir reglas de autorización. El token de sesión se adjunta por el cliente API compartido. La respuesta de lista conserva items, page, page_size y total; la pantalla traduce esos datos a paginación accesible. Los errores de validación por campo se muestran junto al control correspondiente.

## Rutas y acceso

| Ruta | Acceso | Propósito |
|---|---|---|
| /support | Sesión autenticada | Lista y creación de tickets. |
| /support/{ticket_id} | Sesión autenticada | Detalle de ticket autorizado. |

Una persona sin sesión se redirige al acceso. Una respuesta 404 en detalle muestra el estado no encontrado sin revelar pertenencia.

## Flujos y estados UX

- La vista de lista muestra carga inicial, datos, estado vacío, error recuperable y recarga.
- El formulario mantiene valores al fallar una solicitud y anuncia el error.
- El detalle usa carga, contenido, no encontrado y error.
- El cambio de estado refleja éxito sin ocultar un rechazo de regla de negocio.

## Contratos API por accion

| Acción | Solicitud | Respuesta usada | Error tratado |
|---|---|---|---|
| Crear | POST /api/v1/tickets | Ticket creado | 400, 401, 409, 422 |
| Listar | GET /api/v1/tickets | Página de tickets | 400, 401, 500 |
| Detalle | GET /api/v1/tickets/{ticket_id} | Ticket | 401, 404, 500 |
| Estado | PATCH /api/v1/tickets/{ticket_id}/status | Ticket actualizado | 400, 401, 403, 404, 409 |
| Categorías | GET /api/v1/tickets/categories | Categorías activas | 401, 500 |

## Formularios y validacion

El título es obligatorio y admite de 5 a 200 caracteres. La descripción es opcional con máximo de 2000. La categoría es opcional y procede de la lista recibida. La validación de cliente mejora la experiencia; el servidor conserva la decisión final.

## Arquitectura de componentes

SupportPage coordina consulta y creación. TicketForm presenta el formulario. TicketList renderiza la página de resultados. TicketDetail presenta un recurso autorizado. supportApi encapsula las llamadas y sus tipos.

## Responsive y accesibilidad

La lista funciona en una columna en pantallas estrechas. Los controles tienen etiqueta visible, foco perceptible y orden de tabulación lógico. Los mensajes de carga, error y éxito usan regiones anunciables. El estado no depende sólo del color.

## Estrategia de pruebas frontend

Pruebas de componente cubren validación del formulario, renderizado de lista, vacíos, errores y navegación a detalle. Pruebas de integración usan respuestas simuladas para creación, paginación y 404 seguro.

## Contrato de ejecucion Docker y pruebas

La validación se ejecuta dentro de los servicios definidos por el repositorio. Backend instala dependencias, aplica migraciones en una base aislada y ejecuta pruebas API. Frontend instala dependencias bloqueadas y ejecuta sus pruebas. No se incorporan secretos en imágenes, salidas ni evidencia.

| Capa | Comprobación | Resultado esperado |
|---|---|---|
| Backend | Migraciones y pruebas de API | Esquema aplicable y pruebas verdes. |
| Frontend | Pruebas de componentes | Estados de soporte cubiertos. |
| Plan | validate_slice_plan.py BE-014 --stage backend | Estado PASS. |

## Plan de reportes y findings

Las pruebas guardan un resumen con caso, resultado, fecha y evidencia. Un hallazgo bloqueante incluye pasos mínimos, actor, endpoint o pantalla afectada y severidad. Los hallazgos de seguridad se registran sin exponer tokens ni datos personales.

## Pruebas QA

| Grupo | Casos |
|---|---|
| Creación | Título límite, descripción límite, duplicado en 24 horas, categoría de otra clínica. |
| Consulta | Paginación, filtro válido, filtro inválido, categorías activas. |
| Autorización | Sin sesión, otra clínica, otro propietario, personal interno. |
| Estados | Cada transición permitida y cada transición rechazada. |
| Interfaz | Carga, vacío, error, validación, teclado y anuncio de mensajes. |

## Riesgos de seguridad/IDOR/BOLA

| Riesgo | Control | Verificación |
|---|---|---|
| IDOR en detalle | Filtrar por clínica y propietario antes de responder. | Solicitud de recurso ajeno devuelve 404. |
| BOLA en cambio de estado | Exigir rol interno y clínica coincidente. | Usuario común recibe 403 o 404 según contrato. |
| Categoría ajena | Validar clinic_id de categoría contra token. | Creación con categoría ajena falla. |
| Exposición de datos | Respuestas mínimas y errores seguros. | No se revela existencia de ticket ajeno. |

## Politica UTF-8

Todos los archivos, respuestas JSON, migraciones, mensajes y evidencias usan UTF-8. Las pruebas incluyen texto con acentos y caracteres del español. No se aceptan cadenas con codificación dañada.

## Agente y workflow de ejecucion

### Ejecucion backend de BE-014

El comando exacto es /implement-backend-task BE-014 y debe ejecutarse con el agente invet-backend-implementer. Este agente trabaja directamente con el modelo de la sesión; no inicia subagentes.

| Paso | Accion del agente invet-backend-implementer | Condicion de salida |
|---|---|---|
| 1 | Validar el plan en etapa backend. | El plan termina en PASS. |
| 2 | Generar y verificar el manifiesto de la capa backend. | El manifiesto BE-014-backend está vigente. |
| 3 | Leer el checkpoint backend. | Identifica sólo tareas backend pendientes. |
| 4 | Comprobar dependencias y responsabilidad única. | Cada tarea es ejecutable o se devuelve a planificación. |
| 5 | Iniciar una tarea BE, declarar estado operativo y limitar cambios a sus entregables. | La tarea queda en progreso con alcance controlado. |
| 6 | Implementar respetando Clean Architecture, permisos y aislamiento por clínica. | Código alineado al contrato de la tarea. |
| 7 | Crear o actualizar migraciones cuando aplique. | Esquema aplicable con reversión prevista. |
| 8 | Añadir pruebas unitarias y HTTPX cuando corresponda. | Criterios backend cubiertos por pruebas. |
| 9 | Ejecutar la validación de persistencia segura cuando aplique. | Validación de persistencia aprobada. |
| 10 | Ejecutar validaciones de la tarea, registrar evidencia y cerrarla. | Checkpoint y plan reflejan evidencia verificable. |
| 11 | Ejecutar el cierre Docker Compose si está disponible. | Entorno reiniciado o causa del salto registrada. |
| 12 | Informar resultado y recomendar el siguiente comando. | Si no hay bloqueo, continúa frontend. |

Si un preflight falla, una dependencia permanece abierta, una tarea mezcla responsabilidades o existe un hallazgo formal, este agente no continúa con esa tarea. La ruta de corrección es /plan-task BE-014 para un contrato de plan inválido, /implement-backend-task BE-014 para trabajo backend pendiente o /implement-findings BE-014 para hallazgos registrados.

### Cadena completa del slice

| Orden | Comando | Agente responsable | Resultado que habilita el siguiente paso |
|---|---|---|---|
| 1 | /plan-task BE-014 | invet-product-planner | Plan, sidecars y manifiestos válidos. |
| 2 | /implement-backend-task BE-014 | invet-backend-implementer | Tareas backend terminadas con evidencia. |
| 3 | /implement-frontend-task BE-014 | invet-frontend-implementer | Tareas frontend terminadas con evidencia. |
| 4 | /implement-ui-automation-task BE-014 | invet-ui-automation-implementer | Automatización UI validada contra Docker Compose. |
| 5 | /implement-api-automation-task BE-014 | invet-api-automation-implementer | Automatización HTTP validada contra Docker Compose. |
| 6 | /qa-task QA-014 | invet-qa-validator | Decisión APPROVED sin hallazgos bloqueantes. |
| 7 | /review-slice BE-014 | invet-slice-reviewer | Revisión funcional APPROVED. |
| 8 | /clean-architecture-review BE-014 | invet-clean-architecture-reviewer | Revisión de arquitectura APPROVED. |
| 9 | /security-review BE-014 | invet-security-reviewer | Revisión de seguridad APPROVED. |
| 10 | /run-ui-checks BE-014 | invet-check-runner | Checks visuales aprobados. |
| 11 | /run-checks BE-014 | invet-check-runner | Checks técnicos aprobados. |
| 12 | /update-docs BE-014 | invet-docs-updater | Documentación actualizada. |
| 13 | /final-gate BE-014 | invet-final-reviewer | Slice cerrado. |

Ante findings o un gate bloqueado, invet-findings-implementer ejecuta /implement-findings BE-014. Después se repiten /qa-task QA-014 y todos los reviews, checks o gates que dependan del cambio. El flujo no puede cerrarse mientras exista un finding OPEN, IN_PROGRESS o READY_FOR_REVALIDATION.

## Checklist tecnico

- [x] La migración crea tickets, categorías, índices y datos mínimos.
- [x] Las restricciones de clínica y propietario se aplican en consultas.
- [x] Las transiciones se centralizan en el caso de uso.
- [x] Los contratos API tipan solicitudes y respuestas.
- [x] Las pruebas cubren aislamiento, reversión y límites.
- [x] La interfaz cubre estados de espera, vacío y error.

## Checklist de tareas

### Backend

- [x] BE-014-T01 - Persistir esquema de tickets
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-01, AC-02, AC-06, AC-10
  Objetivo: Crear esquema persistente de soporte.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: Entidades SupportTicket y SupportCategory.
  Contratos usados: Reglas de datos del slice.
  Entregables: `backend/app/infrastructure/database/models/support_ticket_model.py`, registro del modelo en `backend/app/infrastructure/database/models/__init__.py`, `backend/alembic/versions/a014_support.py`, eliminación del duplicado inválido `backend/app/infraestructure/database/models/support_ticket_model.py` y pruebas en `backend/app/tests/api/test_support_ticket_api.py`.
  Criterios de aceptacion: La migración crea tablas, unicidad por clínica y categorías activas.
  Validacion: Aplicar migración en base aislada.
  Resultado esperado: Esquema disponible con reversión funcional.
  Evidencia: 17 pruebas aprobadas: 4 de migración y 13 de regresión API; el paquete de modelos registra soporte, el seed propaga errores y se eliminó el modelo en la ruta mal escrita.
  Paralelismo[P]: No

- [x] BE-014-T02 - Implementar repositorio seguro
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-03, AC-04, AC-11
  Objetivo: Implementar repositorio seguro de tickets.
  Responsabilidad unica: Si
  Depende de: BE-014-T01
  Contexto necesario: Modelo de tickets y contexto autenticado.
  Contratos usados: Consulta paginada de tickets.
  Entregables: Repositorio seguro en `backend/app/data/support_ticket_repo.py` y pruebas en `backend/app/tests/data/test_support_ticket_repo.py`.
  Criterios de aceptacion: El recurso ajeno no es visible para un actor no autorizado.
  Validacion: Pruebas de lectura propia, ajena e interna.
  Resultado esperado: Consultas aisladas por clínica.
  Evidencia: 16 pruebas de repositorio y 13 de regresión API aprobadas, con lecturas y cambios aislados por owner y clínica.
  Paralelismo[P]: No

- [x] BE-014-T03 - Centralizar reglas de soporte
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-01, AC-05
  Objetivo: Centralizar reglas de soporte.
  Responsabilidad unica: Si
  Depende de: BE-014-T01
  Contexto necesario: Estados permitidos y ventana de duplicados.
  Contratos usados: TicketStatus y reglas de dominio.
  Entregables: Reglas de creación, deduplicación de 24 horas y transición en `backend/app/application/support_ticket_use_cases.py`, consulta de duplicados en `backend/app/data/support_ticket_repo.py` y pruebas en `backend/app/tests/usecases/test_support_ticket_rules.py` y `backend/app/tests/data/test_support_ticket_repo.py`.
  Criterios de aceptacion: Rechaza duplicados y transiciones inválidas.
  Validacion: Pruebas unitarias de reglas.
  Resultado esperado: Reglas consistentes fuera de controladores.
  Evidencia: 37 pruebas de reglas y repositorio aprobadas; cubren deduplicación normalizada en 24 horas, aislamiento y validación previa de transiciones.
  Paralelismo[P]: Si

- [x] BE-014-T04 - Publicar API protegida
  Capa: backend
  Tipo: api
  Historia o criterio: AC-01, AC-02, AC-03, AC-04, AC-05, AC-07, AC-11
  Objetivo: Publicar API protegida de tickets.
  Responsabilidad unica: Si
  Depende de: BE-014-T02, BE-014-T03
  Contexto necesario: Casos de uso, repositorio y autenticación existente.
  Contratos usados: Endpoints esperados del slice.
  Entregables: Rutas y manejo de errores en `backend/app/api/v1/routers/support_ticket_router.py`, DTOs y serializadores en `backend/app/api/schemas/support_ticket_schemas.py`, registro en `backend/app/api/v1/router.py` y pruebas en `backend/app/tests/api/test_support_ticket_api.py`.
  Criterios de aceptacion: Las rutas responden según actor, contrato y transición.
  Validacion: Pruebas API autenticadas.
  Resultado esperado: API de soporte consumible por frontend.
  Evidencia: 14 pruebas API aprobadas; duplicado reciente responde 409, una transición inválida no muta el estado y existe una sola ruta de categorías.
  Paralelismo[P]: No

### Frontend

- [x] FE-014-T01 - Tipar llamadas de soporte
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-02, AC-07
  Objetivo: Tipar llamadas de soporte.
  Responsabilidad unica: Si
  Depende de: BE-014-T04
  Contexto necesario: Endpoints y envoltura API existente.
  Contratos usados: Contratos API por accion.
  Entregables: `frontend/src/shared/api/client.ts`, `frontend/src/shared/api/support.ts` y `frontend/src/shared/api/support.test.ts`.
  Criterios de aceptacion: Cada llamada conserva parámetros y errores relevantes.
  Validacion: Pruebas del cliente con respuestas simuladas.
  Resultado esperado: Cliente reutilizable para pantallas de soporte.
  Evidencia: Completada. El cliente tipa POST/GET/PATCH/categorías y conserva errores; 5/5 pruebas de `support.test.ts` pasaron con Jest.
  Paralelismo[P]: No

- [x] FE-014-T02 - Construir pantalla de soporte
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-01, AC-03, AC-08, AC-09
  Objetivo: Construir pantalla de soporte.
  Responsabilidad unica: Si
  Depende de: FE-014-T01
  Contexto necesario: Cliente tipado y ruta protegida.
  Contratos usados: Crear ticket y listar tickets.
  Entregables: `frontend/src/app/support/page.tsx`, `frontend/src/features/support/ui/ticket-form.tsx`, `frontend/src/features/support/ui/ticket-list.tsx`, `frontend/src/features/support/ui/ticket-list-filtered.tsx` y sus pruebas.
  Criterios de aceptacion: La pantalla valida, envía y muestra todos los estados UX.
  Validacion: Pruebas de componente e integración.
  Resultado esperado: Flujo principal disponible en /support.
  Evidencia: Completada. SupportPage, TicketForm, TicketList y filtro implementados; 12/12 pruebas de página/componentes pasaron con Jest.
  Paralelismo[P]: No

- [x] FE-014-T03 - Presentar detalle autorizado
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-04, AC-05
  Objetivo: Presentar detalle autorizado.
  Responsabilidad unica: Si
  Depende de: FE-014-T01
  Contexto necesario: Cliente tipado y navegación existente.
  Contratos usados: Consultar detalle y cambiar estado.
  Entregables: `frontend/src/app/support/[ticketId]/page.tsx`, `ticket-status-updater.tsx` y sus pruebas.
  Criterios de aceptacion: El detalle no revela datos ante respuesta 404.
  Validacion: Pruebas de ruta con 200, 404 y error.
  Resultado esperado: Consulta segura de tickets desde la interfaz.
  Evidencia: Completada. La ruta y el actualizador cubren 200, 404, ID inválido y transiciones; 6/6 pruebas pasaron con Jest.
  Paralelismo[P]: Si

### QA

- [x] QA-014-T01 - Confirmar reglas de tickets
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-01, AC-02, AC-05
  Objetivo: Confirmar reglas de tickets.
  Responsabilidad unica: Si
  Depende de: BE-014-T04
  Contexto necesario: API desplegable con datos aislados.
  Contratos usados: Creación, categorías y estados.
  Entregables: `backend/app/tests/api/test_support_ticket_api.py`, `backend/app/tests/data/test_support_ticket_repo.py` y `backend/app/tests/usecases/test_support_ticket_rules.py`.
  Criterios de aceptacion: Límites, duplicados y transiciones están cubiertos.
  Validacion: Ejecutar suite API.
  Resultado esperado: Reglas verificadas con evidencia.
  Evidencia: Completada. La suite dirigida de backend terminó 55 passed; cubre límites, duplicado de 24 h/409, categorías y transiciones.
  Paralelismo[P]: No

- [x] QA-014-T02 - Confirmar migración reversible
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-03, AC-06, AC-10
  Objetivo: Confirmar migración reversible.
  Responsabilidad unica: Si
  Depende de: BE-014-T01
  Contexto necesario: Base de datos efímera.
  Contratos usados: Esquema persistente de soporte.
  Entregables: `backend/tests/api/test_support_ticket_migration.py` y migración `backend/alembic/versions/a014_support.py`.
  Criterios de aceptacion: Aplicar y revertir mantiene la integridad esperada.
  Validacion: Ejecutar migración hacia adelante y atrás.
  Resultado esperado: Persistencia apta para despliegue.
  Evidencia: Completada. Los 4 casos de migración pasaron dentro de 55 passed y validan aplicar, seed idempotente, restricciones y downgrade.
  Paralelismo[P]: Si

- [x] QA-014-T03 - Confirmar seguridad de tickets
  Capa: qa
  Tipo: seguridad
  Historia o criterio: AC-07, AC-11
  Objetivo: Confirmar seguridad de tickets.
  Responsabilidad unica: Si
  Depende de: BE-014-T04
  Contexto necesario: Usuarios de dos clínicas y un actor interno.
  Contratos usados: Lectura, listado y cambio de estado.
  Entregables: Casos de autorización en `backend/app/tests/api/test_support_ticket_api.py` y `backend/app/tests/data/test_support_ticket_repo.py`.
  Criterios de aceptacion: Ningún actor accede a recursos fuera de autorización.
  Validacion: Ejecutar matriz de autorización.
  Resultado esperado: Aislamiento demostrado por pruebas.
  Evidencia: Completada. La matriz de API/repositorio pasó dentro de 55 passed: aislamiento por clínica/propietario, 404 ajeno, 403 de estado y 401 sin sesión.
  Paralelismo[P]: No

- [x] QA-014-T04 - Confirmar experiencia de soporte
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-08, AC-09
  Objetivo: Confirmar experiencia de soporte.
  Responsabilidad unica: Si
  Depende de: FE-014-T02, FE-014-T03
  Contexto necesario: Interfaz conectada a respuestas simuladas.
  Contratos usados: Estados UX y validación de formulario.
  Entregables: Pruebas frontend de `frontend/src/app/support` y `frontend/src/features/support/ui`.
  Criterios de aceptacion: Carga, vacío, error y validación son comprensibles.
  Validacion: Ejecutar pruebas frontend.
  Resultado esperado: Flujo usable por teclado y lector de pantalla.
  Evidencia: Completada. 7 suites y 23 pruebas frontend pasaron; cubren carga, vacío, error, éxito, validación, envío y no encontrado. El build Docker y el stack completo quedaron saludables.
  Paralelismo[P]: No

## Definition of Done

- [x] Todas las tareas del checklist están completadas con evidencia verificable.
- [x] La validación canónica del plan termina en PASS.
- [x] Las pruebas de backend, frontend y QA relevantes terminan correctamente.
- [x] No existe acceso cruzado entre clínicas ni exposición de tickets ajenos.
- [x] Las migraciones se aplican y revierten en un entorno aislado.
- [x] Los cambios respetan UTF-8 y no introducen texto con codificación dañada.
