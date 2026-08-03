---
schema_version: 2
slice: "005"
canonical_plan: BE-005
status: DONE
---

# BE-005 Plan - Administracion de clinica y sucursales

## Objetivo del slice

Implementar CRUD para clinica y sucursales con horarios, contacto, ubicacion y activacion o inactivacion, exponiendo contratos consistentes bajo `/api/v1`.

## Alcance MVP

- Entidades de dominio para clinica, sucursal y horarios.
- Endpoints REST para crear, consultar, actualizar y eliminar de forma logica.
- Persistencia con SQLAlchemy y migraciones si el esquema lo requiere.
- Frontend administrativo para listar, crear y editar clinicas y sucursales.
- QA reproducible sobre permisos, horarios y estados de activacion.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago y facturacion.
- Automatizacion avanzada o analitica compleja.
- Integraciones externas de agenda o mapas.

## Revision de gaps

- El plan anterior no seguia el contrato V2 ni separaba frontend, QA y criterios de cierre.
- Se normaliza el alcance para evitar mezclar administracion de sucursales con otros slices.
- Los errores deben mantenerse seguros y sin exponer datos internos.

## Entidades y reglas de negocio

- **Clinic**: nombre, contacto, direccion, status y timestamps.
- **Branch**: pertenece a una clinic, incluye ubicacion, contacto, status y timestamps.
- **BranchHour**: define apertura por dia, con hora de inicio, cierre y marca de cerrado.
- Una clinic puede tener multiples sucursales.
- Cada sucursal tiene horarios por dia de la semana.
- Los listados deben ser paginados donde aplique.

## Endpoints esperados

- `GET /api/v1/clinics`
- `POST /api/v1/clinics`
- `GET /api/v1/clinics/{id}`
- `PUT /api/v1/clinics/{id}`
- `DELETE /api/v1/clinics/{id}`
- `GET /api/v1/branches`
- `POST /api/v1/branches`
- `GET /api/v1/branches/{id}`
- `PUT /api/v1/branches/{id}`
- `DELETE /api/v1/branches/{id}`
- `GET /api/v1/branches/{id}/hours`
- `POST /api/v1/branches/{id}/hours`
- `PUT /api/v1/branches/{id}/hours/{hour_id}`
- `DELETE /api/v1/branches/{id}/hours/{hour_id}`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /admin/clinicas` para listado administrativo.
- `GET /admin/clinicas/nueva` para alta.
- `GET /admin/clinicas/[id]` para detalle y edicion.
- `GET /admin/sucursales/[id]` para horarios y mantenimiento.

### Flujos y estados UX

- Listado con filtros por status y busqueda.
- Formularios con validacion de campos requeridos.
- Estados loading, error, empty y success en listas y formularios.
- Confirmaciones claras para eliminacion logica.

### Contratos API por accion

- Listado consume `GET /api/v1/clinics` y `GET /api/v1/branches`.
- Alta y edicion consumen `POST` y `PUT` respectivos.
- Los horarios consumen el subrecurso `/hours`.

### Formularios y validacion

- Nombre y direccion obligatorios.
- Horarios con hora de apertura menor a cierre.
- Mensajes claros si falta una sucursal o la clinic no existe.

### Arquitectura de componentes

- Paginas administrativas en `frontend/src/app/admin`.
- Formularios compartidos en `frontend/src/features/clinics/components`.
- Cliente API en `frontend/src/shared/api`.
- Componentes de tabla, modal y status badge reutilizables.

### Responsive y accesibilidad

- Tablas adaptables a mobile con vista apilada.
- Controles accesibles por teclado.
- Mensajes de error y confirmacion legibles.

### Estrategia de pruebas frontend

- Pruebas de componente para formularios, tablas y dialogos.
- Typecheck, lint y smoke visual del flujo administrativo.

## Pruebas QA

- Happy path: crear clinic, sucursal y horario.
- Negative path: horario invalido o clinic inexistente.
- Permisos: solo usuarios autorizados pueden administrar sucursales.
- IDOR/BOLA: una clinic ajena no debe ser visible ni editable.

## Riesgos de seguridad/IDOR/BOLA

- Acceso cruzado a sucursales de otra clinic.
- Errores que revelen IDs internos o estructura de persistencia.
- Validacion incompleta de horarios que permita estados imposibles.

## Checklist tecnico

- [x] Rutas backend para clinics, branches y hours definidas.
- [x] Schemas request/response documentados.
- [x] Frontend administrativo con estados basicos.
- [x] QA de horarios y permisos trazable.

## Checklist de tareas

### Backend

- [x] BE-005-T01 - Normalizar el contrato de clinics, branches y branch hours
  Capa: backend
  Objetivo: Exponer el CRUD administrativo del slice bajo `/api/v1`.
  Depende de: Ninguna
  Entregables: routers FastAPI, schemas Pydantic, casos de uso y pruebas.
  Criterios de aceptacion: Existen listados paginados, detalle, alta, edicion y eliminacion logica; los horarios se validan por dia.
  Validacion: python -m pytest app/tests/test_clinics_api.py -q
  Evidencia: Validacion del plan v2 y pruebas backend del slice
  Paralelismo[P]: No

- [x] BE-005-T02 - Asegurar persistencia y validacion de horarios
  Capa: backend
  Objetivo: Mantener consistencia entre clinic, branch y branch hours.
  Depende de: BE-005-T01
  Entregables: repositorios, migraciones y validaciones de dominio.
  Criterios de aceptacion: Los horarios no aceptan rangos invalidos; las relaciones de sucursal a clinic quedan protegidas.
  Validacion: python -m pytest app/tests/test_clinic_hours.py -q
  Evidencia: Pruebas de horario y ownership en backend
  Paralelismo[P]: No

### Frontend

- [x] FE-005-T01 - Construir pantallas administrativas de clinics y branches
  Capa: frontend
  Objetivo: Permitir listar, crear, editar y eliminar logicamente sucursales desde la UI.
  Depende de: BE-005-T01
  Entregables: paginas admin, formularios y componentes de tabla/modal.
  Criterios de aceptacion: El usuario ve listas, formularios y estados de carga/error/empty sin enlaces rotos.
  Validacion: npm test -- --run
  Evidencia: Cobertura de UI y build estable del slice
  Paralelismo[P]: Si

### QA

- [x] QA-005-T01 - Validar administracion completa de clinica y sucursales
  Capa: qa
  Objetivo: Confirmar happy path, negative path y seguridad del slice.
  Depende de: BE-005-T01, BE-005-T02, FE-005-T01
  Entregables: resultados QA y evidencia de validacion.
  Criterios de aceptacion: El flujo principal funciona; los errores son seguros; la accesibilidad basica existe.
  Validacion: python backend/scripts/validate_slice_plan.py BE-005 --stage plan
  Evidencia: Plan V2 validado para el slice 005
  Paralelismo[P]: No

## Definition of Done

- [x] El CRUD de clinica y sucursales esta descrito en V2.
- [x] Frontend y QA del slice 005 tienen contrato trazable.
- [x] El plan pasa la validacion de esquema.
