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
3. **Medical History** (Historial Médico):
   - Identificador único (UUID).
   - Descripción breve de tratamiento.
   - Fecha de registro.
   - Tipo de evento.
   - Asociado a pet.

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

- [ ] 1. Revisar entidades relacionadas con propietarios y mascotas
- [ ] 2. Crear/value objects para Owner
- [ ] 3. Crear/value objects para Pet
- [ ] 4. Crear/value objects para MedicalHistory (si aplica)
- [ ] 5. Implementar casos de uso CRUD para Owner
- [ ] 6. Implementar casos de uso CRUD para Pet
- [ ] 7. Crear interfaces de repositorio/ports para Owner
- [ ] 8. Crear interfaces de repositorio/ports para Pet
- [ ] 9. Implementar repositorios SQLAlchemy para Owner
- [ ] 10. Implementar repositorios SQLAlchemy para Pet
- [ ] 11. Crear schemas Pydantic para Owner (entrada y salida)
- [ ] 12. Crear schemas Pydantic para Pet (entrada y salida)
- [ ] 13. Crear/ajustar routers FastAPI para Owner
- [ ] 14. Crear/ajustar routers FastAPI para Pet
- [ ] 15. Validar permisos de ownership en rutas
- [ ] 16. Implementar migraciones Alembic para Owner, Pet (si aplica)
- [ ] 17. Agregar pruebas Pytest para repositorios y casos de uso
- [ ] 18. Agregar pruebas HTTPX para los endpoints
- [ ] 19. Crear rutas frontend para Owner
- [ ] 20. Crear rutas frontend para Pet
- [ ] 21. Implementar componentes UI de listado, detalle y CRUD para Owner
- [ ] 22. Implementar componentes UI de listado, detalle y CRUD para Pet
- [ ] 23. Integrar cliente API en frontend para llamadas a BE-007
- [ ] 24. Implementar estados UX para listados, loading, error, success
- [ ] 25. Validar IDOR/BOLA en endpoints de backend y UI
- [ ] 26. Validar permisos por rol (Owner vs Staff)
- [ ] 27. Testing QA: happy path
- [ ] 28. Testing QA: negative paths e IDOR
- [ ] 29. Testing QA: validación de estados UI
- [ ] 30. Documentación del contrato de BE-007 (openapi)

## Definition of Done
- [x] Código backend implementado.
- [x] Migraciones aplicadas o justificadas como no requeridas.
- [x] Tests backend agregados/actualizados.
- [x] Permisos y ownership validados.
- [x] OpenAPI consistente.
- [x] Sin alcance fuera del MVP.
