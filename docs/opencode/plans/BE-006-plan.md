---
schema_version: 2
slice: "006"
canonical_plan: BE-006
status: DONE
---

# BE-006 Plan - Servicios, veterinarios y usuarios internos

## Objetivo del slice

Implementar la administracion de servicios, veterinarios y usuarios internos con reglas de ownership, acceso por rol y contratos consistentes bajo `/api/v1`.

## Alcance MVP

- CRUD de servicios, veterinarios y usuarios internos.
- Reglas de ownership por clinic y sucursal.
- Validaciones de permisos y proteccion contra IDOR/BOLA.
- Frontend administrativo para gestion de catalogos y personal interno.
- QA sobre permisos, integridad y acceso cruzado.

## Fuera de alcance

- Facturacion, checkout y pasarelas de pago.
- Turnos automaticos o analitica avanzada.
- Integraciones externas de agenda o RH.

## Revision de gaps

- El plan anterior estaba resumido y no contenia la estructura V2 requerida.
- Se agregan frontend, QA y Definition of Done para dejar trazabilidad completa.
- El slice debe validar ownership antes de responder datos sensibles.

## Entidades y reglas de negocio

- **Service**: catalogo de servicio ofrecido por la clinic.
- **Veterinarian**: usuario interno con credenciales y rol clinico.
- **InternalUser**: personal con permisos limitados por sucursal o clinic.
- Un servicio pertenece a una clinic.
- Un veterinario puede estar asignado a una o varias sucursales segun permiso.
- Un usuario interno no puede leer ni editar datos fuera de su ownership.

## Endpoints esperados

- `GET /api/v1/services`
- `POST /api/v1/services`
- `GET /api/v1/services/{id}`
- `PUT /api/v1/services/{id}`
- `DELETE /api/v1/services/{id}`
- `GET /api/v1/veterinarians`
- `POST /api/v1/veterinarians`
- `GET /api/v1/veterinarians/{id}`
- `PUT /api/v1/veterinarians/{id}`
- `DELETE /api/v1/veterinarians/{id}`
- `GET /api/v1/internal-users`
- `POST /api/v1/internal-users`
- `GET /api/v1/internal-users/{id}`
- `PUT /api/v1/internal-users/{id}`
- `DELETE /api/v1/internal-users/{id}`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /admin/servicios`
- `GET /admin/veterinarios`
- `GET /admin/usuarios-internos`
- Rutas protegidas para usuarios con rol administrativo.

### Flujos y estados UX

- Listado con busqueda y paginacion.
- Formularios de alta y edicion con validacion.
- Estados loading, error, empty y success.
- Confirmacion previa a borrado logico.

### Contratos API por accion

- Listados consumen colecciones paginadas.
- Formularios usan `POST` y `PUT`.
- Eliminacion usa `DELETE` con confirmacion explicita.

### Formularios y validacion

- Campos requeridos: nombre, contacto y rol segun recurso.
- Emails y telefonos con formato valido.
- Mensajes de autorizacion claros cuando el rol no coincide.

### Arquitectura de componentes

- Paginas admin en `frontend/src/app/admin`.
- Feature de personal y catalogos en `frontend/src/features/staff`.
- Cliente API compartido en `frontend/src/shared/api`.

### Responsive y accesibilidad

- Tablas y formularios adaptables a mobile.
- Interacciones por teclado y etiquetas correctas.
- Errores y confirmaciones comprensibles.

### Estrategia de pruebas frontend

- Pruebas de formulario y estado.
- Typecheck, lint y smoke de navegacion protegida.

## Pruebas QA

- Happy path: crear y editar servicios, veterinarios y usuarios internos.
- Negative path: intentar modificar un recurso fuera de ownership.
- Permisos: rol invalido no accede a administracion.
- IDOR/BOLA: un usuario no debe ver informacion de otra clinic.

## Riesgos de seguridad/IDOR/BOLA

- Acceso cruzado entre clinics o sucursales.
- Fuga de datos del personal interno.
- Permisos inconsistentes en endpoints de edicion.

## Checklist tecnico

- [x] Contrato backend para services, veterinarians e internal-users definido.
- [x] Validaciones de ownership y rol documentadas.
- [x] Frontend administrativo con formularios base.
- [x] QA de seguridad y permisos trazable.

## Checklist de tareas

### Backend

- [x] BE-006-T01 - Normalizar el CRUD de servicios y personal interno
  Capa: backend
  Objetivo: Exponer los endpoints del slice con reglas de ownership.
  Depende de: Ninguna
  Entregables: routers, schemas, use cases y tests.
  Criterios de aceptacion: Existen CRUD y los permisos bloquean accesos fuera de ownership.
  Validacion: python -m pytest app/tests/test_staff_api.py -q
  Evidencia: Backend del slice 006 validado
  Paralelismo[P]: No

- [x] BE-006-T02 - Consolidar protecciones IDOR/BOLA en permisos internos
  Capa: backend
  Objetivo: Evitar acceso cruzado a servicios, veterinarios o usuarios.
  Depende de: BE-006-T01
  Entregables: reglas de autorizacion y pruebas de acceso.
  Criterios de aceptacion: El usuario recibe 403 o 404 segun politica sin fuga de datos.
  Validacion: python -m pytest app/tests/test_staff_permissions.py -q
  Evidencia: Pruebas de ownership y permisos en backend
  Paralelismo[P]: No

### Frontend

- [x] FE-006-T01 - Construir UI administrativa de servicios y personal
  Capa: frontend
  Objetivo: Permitir gestion basica de catalogos y usuarios internos.
  Depende de: BE-006-T01
  Entregables: paginas, listas, formularios y estados visuales.
  Criterios de aceptacion: La UI consume la API real y muestra estados de carga, vacio y error.
  Validacion: npm run build
  Evidencia: Build del frontend del slice 006
  Paralelismo[P]: Si

### QA

- [x] QA-006-T01 - Verificar administracion de servicios y usuarios internos
  Capa: qa
  Objetivo: Confirmar permisos, ownership y estabilidad.
  Depende de: BE-006-T01, BE-006-T02, FE-006-T01
  Entregables: reporte de QA y evidencia de seguridad.
  Criterios de aceptacion: El flujo principal funciona y los accesos cruzados son bloqueados.
  Validacion: python backend/scripts/validate_slice_plan.py BE-006 --stage plan
  Evidencia: Plan V2 validado para el slice 006
  Paralelismo[P]: No

## Definition of Done

- [x] El CRUD de services, veterinarians e internal-users esta en V2.
- [x] Frontend y QA del slice 006 quedaron trazables.
- [x] El plan pasa validacion de esquema.
