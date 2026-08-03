---
schema_version: 2
slice: "007"
canonical_plan: BE-007
status: DONE
---

# BE-007 Plan - Propietarios y mascotas

## Objetivo del slice

Implementar CRUD para propietarios y mascotas con expediente basico inicial, reglas de ownership y contratos verificables en backend y frontend.

## Alcance MVP

- CRUD de owners y pets.
- Relacion uno a muchos entre propietario y mascota.
- Validaciones basicas de datos y ownership.
- UI para listar, crear, editar y ver detalle.
- QA con rutas protegidas, estados y regresion.

## Fuera de alcance

- Consultas medicas completas.
- Productos, marketplace, carrito, checkout o facturacion.
- Automatizaciones avanzadas o analitica.

## Revision de gaps

- El plan existente tenia contenido funcional pero no el formato V2.
- Se agregan los bloques obligatorios de frontend, QA y tareas.
- La proteccion por ownership debe mantenerse en toda la superficie del slice.

## Entidades y reglas de negocio

- **Owner**: nombre, email, telefono, direccion opcional y timestamps.
- **Pet**: nombre, especie, raza, sexo, nacimiento, color, peso opcional y timestamps.
- Un owner puede tener multiples pets.
- Una pet pertenece a un owner.
- No se permite eliminar una mascota con historial medico dependiente.

## Endpoints esperados

- `GET /api/v1/owners`
- `GET /api/v1/owners/{id}`
- `POST /api/v1/owners`
- `PUT /api/v1/owners/{id}`
- `DELETE /api/v1/owners/{id}`
- `GET /api/v1/pets`
- `GET /api/v1/pets/{id}`
- `POST /api/v1/pets`
- `PUT /api/v1/pets/{id}`
- `DELETE /api/v1/pets/{id}`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /admin/owners`
- `GET /admin/owners/[id]`
- `GET /admin/pets`
- `GET /admin/pets/[id]`
- Rutas internas protegidas por sesion.

### Flujos y estados UX

- Listados paginados con busqueda basica.
- Formularios de alta y edicion.
- Detalle con acciones permitidas por ownership.
- Estados loading, error, empty y success.

### Contratos API por accion

- Listados consumen colecciones de owners y pets.
- Formularios usan `POST` y `PUT`.
- Eliminacion usa `DELETE` con reglas de dependencia.

### Formularios y validacion

- Email obligatorio y valido.
- Nombre no vacio.
- Fecha de nacimiento no puede quedar en el futuro.

### Arquitectura de componentes

- Feature de propietarios y mascotas en `frontend/src/features/pets`.
- Paginas admin en `frontend/src/app/admin`.
- Cliente API compartido en `frontend/src/shared/api`.

### Responsive y accesibilidad

- Formularios y tablas aptos para mobile.
- Mensajes accesibles y etiquetas correctas.
- Navegacion clara entre owner y pet detail.

### Estrategia de pruebas frontend

- Pruebas de componente para listados y formularios.
- Smoke de navegacion protegida y estados visuales.

## Pruebas QA

- Happy path: alta, consulta y edicion de owner y pet.
- Negative path: datos invalidos o pet sin owner.
- Permisos: acceso sin sesion denegado.
- IDOR/BOLA: no se exponen owners o pets de otra cuenta.

## Riesgos de seguridad/IDOR/BOLA

- Exposicion cruzada de mascotas entre owners.
- Respuestas con campos sensibles no requeridos.
- Borrado de mascotas con historial activo.

## Checklist tecnico

- [x] Endpoints de owners y pets definidos.
- [x] Reglas de negocio y ownership documentadas.
- [x] Frontend administrativo base descrito.
- [x] QA del slice trazable.

## Checklist de tareas

### Backend

- [x] BE-007-T01 - Normalizar el CRUD de owners y pets
  Capa: backend
  Objetivo: Exponer los contratos del slice con ownership seguro.
  Depende de: Ninguna
  Entregables: routers, schemas, use cases y pruebas.
  Criterios de aceptacion: Los endpoints CRUD responden correctamente y bloquean accesos ajenos.
  Validacion: python -m pytest app/tests/test_owner_pet_api.py -q
  Evidencia: Backend del slice 007 validado
  Paralelismo[P]: No

- [x] BE-007-T02 - Asegurar reglas de eliminacion y relaciones
  Capa: backend
  Objetivo: Evitar borrados invalidos y relaciones inconsistentes.
  Depende de: BE-007-T01
  Entregables: validaciones de dominio y pruebas negativas.
  Criterios de aceptacion: No se elimina una pet con dependencias y la relacion owner-pet permanece consistente.
  Validacion: python -m pytest app/tests/test_owner_pet_rules.py -q
  Evidencia: Reglas de negocio y permisos cubiertas
  Paralelismo[P]: No

### Frontend

- [x] FE-007-T01 - Construir pantallas de owners y pets
  Capa: frontend
  Objetivo: Entregar listados, detalle y formularios del slice.
  Depende de: BE-007-T01
  Entregables: paginas admin, formularios y tarjetas de detalle.
  Criterios de aceptacion: La UI muestra estados loading, error, empty y success sin enlaces rotos.
  Validacion: npm test -- --run
  Evidencia: UI del slice 007 con pruebas y build estable
  Paralelismo[P]: Si

### QA

- [x] QA-007-T01 - Validar CRUD de owners y pets con seguridad
  Capa: qa
  Objetivo: Confirmar happy path, negative path y ownership.
  Depende de: BE-007-T01, BE-007-T02, FE-007-T01
  Entregables: reporte QA y evidencia del flujo principal.
  Criterios de aceptacion: El plan valida en esquema V2 y el flujo principal es verificable.
  Validacion: python backend/scripts/validate_slice_plan.py BE-007 --stage plan
  Evidencia: Plan V2 validado para el slice 007
  Paralelismo[P]: No

## Definition of Done

- [x] Owners y pets quedaron normalizados en V2.
- [x] Frontend y QA del slice 007 estan descritos.
- [x] El plan pasa la validacion requerida.
