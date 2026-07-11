# Plan de Ejecución — BE-008

## Objetivo del slice

Implementar funcionalidades esenciales para la solicitud y gestión de citas de veterinaria, permitiendo a los usuarios crear, confirmar, cancelar, reprogramar, registrar no-show y completar citas.

## Alcance MVP

### Funcionalidades implementadas
1. Creación de solicitudes de cita.
2. Confirmación de citas solicitadas.
3. Cancelación de citas.
4. Reprogramación de citas.
5. Registro de "no-show".
6. Completar citas.
7. Gestión de agendas por clínica y usuario.

### Entidades y reglas de negocio

#### Entidades
1. Appointment (Cita)
2. AppointmentSlot (Franja horaria disponible)

#### Reglas de negocio
1. Un propietario puede solicitar una cita para su mascota.
2. Solo se pueden crear citas en franjas horarias disponibles.
3. Solo un veterinario puede confirmar, cancelar, o completar citas.
4. Los usuarios internos solo pueden gestionar citas en sus sucursales asignadas.
5. Una cita debe estar en estado "solicitada" antes de ser confirmada.
6. No se permite crear citas fuera del horario disponible.

### Endpoints esperados

#### Citas
- `POST /api/v1/appointments`
- `GET /api/v1/appointments/{appointment_id}`
- `PUT /api/v1/appointments/{appointment_id}/cancel`
- `PUT /api/v1/appointments/{appointment_id}/confirm`
- `PUT /api/v1/appointments/{appointment_id}/reschedule`
- `PUT /api/v1/appointments/{appointment_id}/no-show`
- `PUT /api/v1/appointments/{appointment_id}/complete`

#### Franjas horarias
- `GET /api/v1/clinics/{clinic_id}/branches/{branch_id}/availability`

#### Consulta de citas
- `GET /api/v1/users/{user_id}/appointments`

## Fuera de alcance

1. Productos, marketplace, carrito, checkout o pasarela de pago.
2. Facturación electrónica.
3. Timbrado fiscal.
4. Automatización avanzada de recomendaciones médicas.
5. Soporte para múltiples mascotas en una sola cita.
6. Sincronización con Google Calendar u otros servicios externos.

## Suposiciones

1. La estructura base de entidades para `Appointment` y `AppointmentSlot` ya está definida en BE-007 o se creará como parte de este slice.
2. Los permisos y reglas de ownership se implementarán conforme a los patrones de dominio establecidos en el sistema.
3. En caso de fallo de validación de horario, se retorna un error HTTP 400 con mensaje claro sin filtrar información sensible.
4. La lógica de negocio no incluye casos avanzados como notificaciones automáticas o disparadores condicionales.

## Revision de gaps

El plan existente contiene información sobre:
- Objetivo
- Alcance MVP
- Fuera de alcance
- Entidades y reglas de negocio (parcialmente completo)
- Endpoints esperados (completo según BE-008.md)
- Componentes frontend esperados (faltante)
- Pruebas QA (parcialmente completo)
- Riesgos de seguridad/IDOR/BOLA (completos)

Se agregaron:
1. Completó la definición de reglas de negocio.
2. Agregó componentes frontend y pruebas QA faltantes.
3. Agregaron suposiciones.

## Componentes frontend esperados

1. Formulario de solicitud de cita.
2. Lista de citas agendadas.
3. Detalle de cada cita (estado, horario, información del usuario).
4. Botones de acción para modificar el estado de la cita.

## Pruebas QA

- Happy path: Crear, consultar y modificar una cita.
- Negative path: Intenta crear una cita fuera de horario disponible.
- Permisos: Usuario sin permiso no puede modificar citas de otros usuarios.
- IDOR/BOLA: No se permite acceder a recursos ajenos al usuario autenticado.
- Estados HTTP: Validar códigos 200, 404, 400, 403, etc.
- Estados UI: Mostrar loading, error, empty, success.

## Riesgos de seguridad/IDOR/BOLA

1. IDOR: Asegurar que los usuarios solo puedan ver y modificar citas asignadas a su perfil o sucursal.
2. BOLA: Validar que no se exponga información sensibilidad en respuestas de error.
3. Acceso restringido: Verificar que los endpoints exijan el permiso correcto para cada operación.

## Checklist numerado de tareas backend

1. [x] Revisar modelo de `Appointment` y `AppointmentSlot` definidos en BE-007 o crearlos.
2. [x] Implementar casos de uso Application para: crear, confirmar, cancelar, reprogramar, no-show y completar citas.
3. [x] Crear interfaces de repositorio/ports para las entidades de dominio.
4. [x] Implementar repositorios SQLAlchemy en infrastructure.
5. [x] Crear schemas Pydantic separados por contexto (request/response).
6. [x] Crear/ajustar routers FastAPI.
7. [x] Agregar pruebas Pytest/HTTPX para todos los casos esperados: happy path, negative path y permisos.
8. [ ] Validar permisos, ownership e IDOR/BOLA cuando aplique.
9. [x] Realizar validaciones de estado de citas: evitar crear cita fuera de horario disponible.

## Checklist numerado de tareas frontend

1. [ ] Revisar contrato de BE-008.
2. [ ] Definir rutas en `src/app`.
3. [ ] Crear feature en `src/features`.
4. [ ] Crear componentes reutilizables si aplica.
5. [ ] Crear formularios con validación.
6. [ ] Integrar cliente API.
7. [ ] Manejar errores HTTP 400/401/403/404/409/422/500.
8. [ ] Agregar estados visuales.
9. [ ] Validar responsive.
10. [ ] Agregar pruebas si el repo tiene framework configurado.

## Checklist numerado de tareas QA

1. [ ] Ejecutar happy path: Crear, consultar y modificar una cita.
2. [ ] Ejecutar negative path: Intenta crear una cita fuera de horario disponible.
3. [ ] Validar permisos para usuarios sin acceso a citas ajenas.
4. [ ] Verificar IDOR/BOLA: Acceso a recursos ajenos debe ser rechazado de forma segura.
5. [ ] Validar estados HTTP esperados en todos los endpoints.
6. [ ] Revisar estado UI: Verificar loading, error, empty, success.
7. [ ] Verificar regresión del flujo principal.

## Checklist tecnico

- [ ] Rutas backend y prefijos API definidos:
  - `/api/v1/appointments`
  - `/api/v1/clinics/{clinic_id}/branches/{branch_id}/availability`
  - `/api/v1/users/{user_id}/appointments`
- [ ] Contratos request/response documentados:
  - Appointment schema (incluye estado, horario, owner, etc.)
  - AppointmentSlot schema
- [ ] Permisos y ownership definidos por endpoint o accion:
  - POST /api/v1/appointments: Propietario/sucursal
  - PUT /api/v1/appointments/{id}/cancel: Veterinario/sucursal
  - PUT /api/v1/appointments/{id}/confirm: Veterinario/sucursal
  - PUT /api/v1/appointments/{id}/reschedule: Veterinario/sucursal
  - PUT /api/v1/appointments/{id}/no-show: Veterinario/sucursal
  - PUT /api/v1/appointments/{id}/complete: Veterinario/sucursal
- [ ] Estados de error esperados definidos, incluyendo 400, 401, 403, 404 y validaciones:
  - 400: Horario inválido o formato incorrecto de solicitud.
  - 401: Acceso no autorizado.
  - 403: Acceso prohibido por permisos.
  - 404: Recurso no encontrado (cita o franja horaria).
- [ ] Modelos, migraciones o cambios de persistencia identificados:
  - `Appointment` (entidad raíz)
  - `AppointmentSlot` (entidad raíz)
- [ ] Casos QA positivos, negativos y de permisos trazados a criterios de aceptacion:
  - Happy path: Crear, modificar y consultar citas OK.
  - Negative path: Horario inválido genera error 400.
  - Permisos: Cuenta con rol incorrecto no puede modificar citas ajenas.
- [ ] Checks esperados definidos: pytest, ruff, black, mypy y frontend si existe:
  - pytest para test backend
  - ruff, black, mypy para limpieza de código
  - ESLint + Jest o Vitest para frontend (si aplica)
- [ ] Documentacion a actualizar identificada:
  - Actualización del archivo de documentación de API
  - Actualización de la definición de entidades en el dominio

## Definition of Done

- Todos los endpoints implementados y expuestos por `/api/v1`.
- Código backend implementado, migraciones aplicadas (si hay).
- Tests backend (Pytest/HTTPX) implementados.
- Pruebas QA validadas y documentadas.
- No se ha agregado funcionalidad fuera del MVP.