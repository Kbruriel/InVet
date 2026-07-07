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

### Entidades
1. Appointment (Cita)
2. AppointmentSlot (Franja horaria disponible)

### Reglas
1. Un propietario puede solicitar una cita para su mascota.
2. Solo se pueden crear citas en franjas horarias disponibles.
3. Solo un veterinario puede confirmar, cancelar, o completar citas.
4. Los usuarios internos solo pueden gestionar citas en sus sucursales asignadas.

### Endpoints esperados
- `POST /api/v1/appointments`
- `GET /api/v1/appointments/{appointment_id}`
- `PUT /api/v1/appointments/{appointment_id}/cancel`
- `PUT /api/v1/appointments/{appointment_id}/confirm`
- `PUT /api/v1/appointments/{appointment_id}/reschedule`
- `PUT /api/v1/appointments/{appointment_id}/no-show`
- `PUT /api/v1/appointments/{appointment_id}/complete`
- `GET /api/v1/clinics/{clinic_id}/branches/{branch_id}/availability`
- `GET /api/v1/users/{user_id}/appointments`

## Fuera de alcance

1. Productos, marketplace, carrito, checkout o pasarela de pago.
2. Facturación electrónica.
3. Timbrado fiscal.
4. Automatización avanzada de recomendaciones médicas.
5. Soporte para múltiples mascotas en una sola cita.
6. Sincronización con Google Calendar u otros servicios externos.

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

## Definition of Done

- Todos los endpoints implementados y expuestos por `/api/v1`.
- Código backend implementado, migraciones aplicadas (si hay).
- Tests backend (Pytest/HTTPX) implementados.
- Pruebas QA validadas y documentadas.
- No se ha agregado funcionalidad fuera del MVP.