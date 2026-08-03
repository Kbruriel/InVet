---
schema_version: 2
slice: "008"
canonical_plan: BE-008
status: DONE
---

# BE-008 Plan - Citas y disponibilidad

## Objetivo del slice

Implementar la solicitud y gestion de citas veterinarias con disponibilidad por sucursal, cambios de estado y control de permisos por rol.

## Alcance MVP

- Crear, confirmar, cancelar, reprogramar, marcar no-show y completar citas.
- Gestion de disponibilidad por clinic y sucursal.
- Reglas de acceso para propietario, veterinario y usuarios internos.
- Frontend para agenda, detalle y acciones de cita.
- QA reproducible sobre estados y permisos.

## Fuera de alcance

- Sincronizacion con calendarios externos.
- Multi-mascota en una sola cita.
- Automatizaciones avanzadas de recordatorios.

## Revision de gaps

- El plan previo era util, pero no seguia el contrato V2 de manera completa.
- Se agregan los bloques de frontend, QA y definicion de cierre.
- La validacion de disponibilidad debe vivir en dominio y backend, no solo en la UI.

## Entidades y reglas de negocio

- **Appointment**: cita con estado, propietario, mascota, sucursal y veterinario asignado o pendiente.
- **AppointmentSlot**: franja horaria disponible por clinic y sucursal.
- Una cita debe crearse solo en una franja disponible.
- Solo un veterinario o usuario autorizado puede confirmar, cancelar o completar.
- Los usuarios internos solo gestionan citas de sus sucursales.
- No se permiten citas fuera del horario disponible.

## Endpoints esperados

- `POST /api/v1/appointments`
- `GET /api/v1/appointments/{appointment_id}`
- `PUT /api/v1/appointments/{appointment_id}/cancel`
- `PUT /api/v1/appointments/{appointment_id}/confirm`
- `PUT /api/v1/appointments/{appointment_id}/reschedule`
- `PUT /api/v1/appointments/{appointment_id}/no-show`
- `PUT /api/v1/appointments/{appointment_id}/complete`
- `GET /api/v1/clinics/{clinic_id}/branches/{branch_id}/availability`
- `GET /api/v1/users/{user_id}/appointments`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /citas`
- `GET /citas/nueva`
- `GET /citas/[id]`
- Rutas protegidas segun rol y ownership.

### Flujos y estados UX

- Formulario de solicitud de cita.
- Lista de citas agendadas.
- Detalle con acciones segun estado.
- Estados loading, error, empty y success.

### Contratos API por accion

- Crear cita usa `POST /api/v1/appointments`.
- Ver detalle usa `GET /api/v1/appointments/{appointment_id}`.
- Cambios de estado usan endpoints dedicados por accion.
- La disponibilidad usa el subrecurso de clinic y branch.

### Formularios y validacion

- Fecha y hora obligatorias dentro de disponibilidad.
- La mascota y la sucursal deben existir.
- Mensaje claro si la franja ya no esta disponible.

### Arquitectura de componentes

- Feature de citas en `frontend/src/features/appointments`.
- Calendario y selector de horario reutilizables.
- Cliente API compartido en `frontend/src/shared/api`.

### Responsive y accesibilidad

- Vista de calendario y lista adaptables a mobile.
- Botones y estados con etiquetas accesibles.
- Confirmaciones claras para cancelacion y reprogramacion.

### Estrategia de pruebas frontend

- Pruebas de formulario, estado y acciones.
- Smoke de navegacion y permisos por rol.

## Pruebas QA

- Happy path: crear, confirmar y completar una cita.
- Negative path: intentar crear en horario no disponible.
- Permisos: usuario sin permiso no puede modificar otra cita.
- IDOR/BOLA: no se exponen citas ajenas.

## Riesgos de seguridad/IDOR/BOLA

- Acceso cruzado a citas de otros usuarios o sucursales.
- Validacion solo visual sin control real en backend.
- Fugas de datos en errores de disponibilidad.

## Checklist tecnico

- [x] Contrato backend de citas y disponibilidad definido.
- [x] Reglas de estado y permiso documentadas.
- [x] Frontend de agenda y detalle descrito.
- [x] QA de citas trazable.

## Checklist de tareas

### Backend

- [x] BE-008-T01 - Normalizar el flujo de citas y disponibilidad
  Capa: backend
  Objetivo: Exponer la gestion de citas con estados y disponibilidad.
  Depende de: Ninguna
  Entregables: routers, schemas, casos de uso y pruebas.
  Criterios de aceptacion: Las citas se crean solo en franjas validas y los cambios de estado respetan permisos.
  Validacion: python -m pytest app/tests/test_appointments_api.py -q
  Evidencia: Backend del slice 008 validado
  Paralelismo[P]: No

- [x] BE-008-T02 - Consolidar reglas de ownership y calendario
  Capa: backend
  Objetivo: Evitar accesos cruzados y estados invalidos.
  Depende de: BE-008-T01
  Entregables: validaciones de dominio, control de acceso y tests negativos.
  Criterios de aceptacion: Las citas ajenas no se pueden ver ni modificar; la disponibilidad no permite colisiones.
  Validacion: python -m pytest app/tests/test_appointments_rules.py -q
  Evidencia: Reglas de permisos y calendario cubiertas
  Paralelismo[P]: No

### Frontend

- [x] FE-008-T01 - Construir UI de agenda y gestion de citas
  Capa: frontend
  Objetivo: Permitir solicitar, ver y modificar citas desde la UI.
  Depende de: BE-008-T01
  Entregables: paginas, calendario, formularios y detalle de cita.
  Criterios de aceptacion: La UI maneja loading, error, empty y success y respeta permisos.
  Validacion: npm test -- --run
  Evidencia: UI del slice 008 con regresion estable
  Paralelismo[P]: Si

### QA

- [x] QA-008-T01 - Verificar agenda, permisos y estados de cita
  Capa: qa
  Objetivo: Confirmar el flujo principal y las protecciones.
  Depende de: BE-008-T01, BE-008-T02, FE-008-T01
  Entregables: reporte QA y evidencia de disponibilidad.
  Criterios de aceptacion: El flujo completo funciona y los casos negativos fallan de forma segura.
  Validacion: python backend/scripts/validate_slice_plan.py BE-008 --stage plan
  Evidencia: Plan V2 validado para el slice 008
  Paralelismo[P]: No

## Definition of Done

- [x] El flujo de citas y disponibilidad esta descrito en V2.
- [x] Frontend y QA del slice 008 quedaron trazables.
- [x] El plan pasa validacion de esquema.
