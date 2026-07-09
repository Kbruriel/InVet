# BE-007 — Propietarios y mascotas - Plan de Ejecución

## Objetivo del slice
Implementar CRUD para propietarios, mascotas y expediente básico inicial.

## Alcance MVP
- Implementación de entidades dominio para propietarios y mascotas.
- Implementación de casos de uso CRUD aplicables.
- Routers FastAPI expuestos en `/api/v1/owners`, `/api/v1/pets`.
- Componentes frontend para visualización básica de listados, detalle, edición y creación de propietarios y mascotas.
- Pruebas backend, frontend y QA.

## Fuera de alcance
- Productos, marketplace, carrito, checkout, pasarela de pago.
- Facturación electrónica o timbrado fiscal.
- Automatizaciones avanzadas o analítica avanzada.

## Entidades y reglas de negocio
1. **Owner** (Propietario):
    - Identificador único (UUID).
    - Nombre completo.
    - Correo electrónico.
    - Teléfono de contacto.
    - Dirección postal (opcional).
    - Fecha de creación, actualización.
    - Asociado a un tenant/empresa/sucursal.
2. **Pet** (Mascota):
    - Identificador único (UUID).
    - Nombre.
    - Especie.
    - Raza.
    - Sexo.
    - Fecha de nacimiento.
    - Color.
    - Peso (opcional).
    - Historial médico básico (opcional).
    - Fecha de creación, actualización.
    - Asociado a un owner.

Reglas:
- Un owner puede tener múltiples pets.
- Solo se permite eliminar mascotas si no tienen historial de tratamiento.
- Acceso limitado por ownership/tenant.
- Validaciones:
  - Email válido.
  - Nombre no vacío.
  - Fecha de nacimiento no en futuro.

## Endpoints esperados

### `GET /api/v1/owners`
- Objetivo: Listado de propietarios.
- Criterios de aceptación:
  - Retorna lista paginada.
  - Respuesta contiene campo `total`.
  - No incluye información sensible sin permisos.
- Paralelismo[P]: Si

### `GET /api/v1/owners/{id}`
- Objetivo: Detalle de propietario.
- Criterios de aceptación:
  - Retorna propietario completo.
  - Responde con error 404 si no existe.
- Paralelismo[P]: No

### `POST /api/v1/owners`
- Objetivo: Crear nuevo propietario.
- Criterios de aceptación:
  - Acepta datos de owner en body.
  - Retorna el owner creado con ID asignado.
  - Valida requeridos y formatos.
- Paralelismo[P]: No

### `PUT /api/v1/owners/{id}`
- Objetivo: Actualizar propietario existente.
- Criterios de aceptación:
  - Acepta datos actualizados en body.
  - Retorna el owner actualizado con ID.
  - Valida requeridos y formatos.
- Paralelismo[P]: No

### `DELETE /api/v1/owners/{id}`
- Objetivo: Eliminar propietario.
- Criterios de aceptación:
  - Elimina el owner si no tiene mascotas asociadas.
  - Responde con error 409 si tiene mascotas.
- Paralelismo[P]: No

### `GET /api/v1/pets`
- Objetivo: Listado de mascotas.
- Criterios de aceptación:
  - Retorna lista paginada.
  - Permite filtrar por owner ID y raza.
  - No incluye información sensible sin permisos.
- Paralelismo[P]: Si

### `GET /api/v1/pets/{id}`
- Objetivo: Detalle de mascota.
- Criterios de aceptación:
  - Retorna mascota completa.
  - Responde con error 404 si no existe.
- Paralelismo[P]: No

### `POST /api/v1/pets`
- Objetivo: Crear nueva mascota.
- Criterios de aceptación:
  - Acepta datos de mascota en body.
  - Retorna la mascota creada con ID asignado.
  - Valida requeridos y formatos.
- Paralelismo[P]: No

### `PUT /api/v1/pets/{id}`
- Objetivo: Actualizar mascota existente.
- Criterios de aceptación:
  - Acepta datos actualizados en body.
  - Retorna la mascota actualizada con ID.
  - Valida requeridos y formatos.
- Paralelismo[P]: No

### `DELETE /api/v1/pets/{id}`
- Objetivo: Eliminar mascota.
- Criterios de aceptación:
  - Elimina la mascota si no tiene historial.
  - Responde con error 409 si tiene historial.
- Paralelismo[P]: No

## Componentes frontend esperados
1. `src/features/owners`:
    - Listado: `/owners`.
    - Detalle: `/owners/{id}`.
    - Creación: `/owners/new`.
    - Edición: `/owners/{id}/edit`.
2. `src/features/pets`:
    - Listado: `/pets`.
    - Detalle: `/pets/{id}`.
    - Creación: `/pets/new`.
    - Edición: `/pets/{id}/edit`.
3. Formularios de edición con validaciones.
4. Componentes de estado (`loading`, `error`, `empty`, `success`).
5. Uso del cliente API centralizado para consumir el backend.

## Pruebas QA
1. Happy path CRUD para owner y pet.
2. Negative paths:
    - Input inválido en POST/PUT.
    - Acceso a datos ajeno sin permisos (IDOR).
3. Permisos por rol: Owner vs Staff.
4. Estados UI:
    - Loading, error, success.
5. Paginación para listados.
6. Regresión del flujo principal.

## Riesgos de seguridad/IDOR/BOLA
1. IDOR:
    - Verificar que acceso a `/owners/{id}` y `/pets/{id}` no permita ver registros ajenos.
2. BOLA (Binding of Anomalous Line):
    - Asegurar que el backend no se auto-enlace con datos de usuario sin verificación previa.
3. Error handling:
    - No filtrar información interna en respuestas HTTP en error.

## Checklist de tareas

### Backend
- [x] 1. Revisar entidades relacionadas con propietarios y mascotas
- [x] 2. Crear/value objects para Owner
- [x] 3. Crear/value objects para Pet
- [x] 4. Implementar casos de uso CRUD para Owner
- [x] 5. Implementar casos de uso CRUD para Pet
- [x] 6. Crear interfaces de repositorio/ports para Owner
- [x] 7. Crear interfaces de repositorio/ports para Pet
- [x] 8. Implementar repositorios SQLAlchemy para Owner
- [x] 9. Implementar repositorios SQLAlchemy para Pet
- [x] 10. Crear schemas Pydantic para Owner (entrada y salida)
- [x] 11. Crear schemas Pydantic para Pet (entrada y salida)
- [x] 12. Crear/ajustar routers FastAPI para Owner
- [x] 13. Crear/ajustar routers FastAPI para Pet
- [x] 14. Validar permisos de ownership en rutas

### Frontend
- [ ] 18. Crear rutas frontend para Owner
- [ ] 19. Crear rutas frontend para Pet
- [ ] 20. Implementar componentes UI de listado, detalle y CRUD para Owner
- [ ] 21. Implementar componentes UI de listado, detalle y CRUD para Pet
- [ ] 22. Integrar cliente API en frontend para llamadas a BE-007
- [ ] 23. Implementar estados UX para listados, loading, error, success

### QA
- [ ] 24. Validar IDOR/BOLA en endpoints de backend y UI
- [ ] 25. Validar permisos por rol (Owner vs Staff)
- [ ] 26. Testing QA: happy path
- [ ] 27. Testing QA: negative paths e IDOR
- [ ] 28. Testing QA: validación de estados UI
- [ ] 29. Documentación del contrato de BE-007 (openapi)

## Definition of Done
- [x] Código backend implementado.
- [x] Migraciones aplicadas o justificadas como no requeridas.
- [x] Tests backend agregados/actualizados.
- [x] Permisos y ownership validados.
- [x] OpenAPI consistente.
- [x] Sin alcance fuera del MVP.