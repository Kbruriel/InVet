# Plan de Ejecución — BE-006

## Objetivo del slice

Implementar la funcionalidad CRUD para servicios, veterinarios y usuarios internos, asociados a sucursales, incluyendo los contratos API necesarios.

## Alcance MVP

- Implementación completa de CRUD (Crear, Leer, Actualizar, Eliminar) para:
  - Servicios
  - Veterinarios
  - Usuarios internos
  - Asociaciones entre estos elementos y sucursales
- Contratos de API bajo `/api/v1` 
- Asegurar seguridad mediante permisos y ownership (IDOR/BOLA)
- Implementación de paginación en listados

## Fuera de alcance

- Productos, marketplace, carrito, checkout o pasarela de pago
- Facturación electrónica ni timbrado fiscal
- Automatizaciones avanzadas o análisis médico
- Aplicaciones móviles nativas

## Entidades y Reglas de negocio

### Entidades

1. **Servicio**
    - Atributos: nombre, descripción, costo estimado, duración
2. **Veterinario**
    - Atributos: nombre, apellido, especialidad, correo electrónico, teléfono, matrícula
3. **Usuario Interno**
    - Atributos: nombre, apellido, correo electrónco, rol (admin, editor), contraseña (hash)
4. **Sucursal**
    - Atributos: nombre, dirección, ciudad, estado, código postal

### Asociaciones

1. Servicio ↔ Sucursal
2. Veterinario ↔ Sucursal
3. Usuario Interno ↔ Sucursal

### Reglas de negocio

1. Cada servicio puede estar asignado a una o más sucursales.
2. Cada veterinario debe pertenecer a al menos una sucursal. 
3. Un usuario interno debe tener un rol y al menos una sucursal asignada.
4. Los datos de los usuarios deben ser sensibles, por lo tanto se debe aplicar hashing de contraseñas.

## Endpoints esperados

1. `GET /api/v1/services`
2. `POST /api/v1/services`
3. `GET /api/v1/services/{id}`
4. `PUT /api/v1/services/{id}`
5. `DELETE /api/v1/services/{id}`

6. `GET /api/v1/veterinarians`
7. `POST /api/v1/veterinarians`
8. `GET /api/v1/veterinarians/{id}`
9. `PUT /api/v1/veterinarians/{id}`
10. `DELETE /api/v1/veterinarians/{id}`

11. `GET /api/v1/internal-users`
12. `POST /api/v1/internal-users`
13. `GET /api/v1/internal-users/{id}`
14. `PUT /api/v1/internal-users/{id}`
15. `DELETE /api/v1/internal-users/{id}`

16. `GET /api/v1/branches`
17. `POST /api/v1/branches`
18. `GET /api/v1/branches/{id}`
19. `PUT /api/v1/branches/{id}`
20. `DELETE /api/v1/branches/{id}`

## Componentes frontend esperados

- Vista de listado de servicios (`/services`)
- Vista de creación/editar servicios (`/services/create`, `/services/edit/:id`)
- Vista de detalle de servicio (`/services/:id`)
- Vista de listado de veterinarios (`/veterinarians`)
- Vista de creación/editar veterinarios (`/veterinarians/create`, `/veterinarians/edit/:id`)
- Vista de detalle de veterinario (`/veterinarians/:id`)
- Vista de listado de usuarios internos (`/internal-users`)
- Vista de creación/editar usuarios internos (`/internal-users/create`, `/internal-users/edit/:id`)
- Vista de detalle de usuario interno (`/internal-users/:id`)

## Pruebas QA

- Validación de permisos por rol (admin, editor)
- Verificación de IDOR/BOLA al acceder a entidades de otros usuarios
- Manejo de errores (400, 401, 403, 404, 409, 422, 500)
- Validación de estados UI (loading, error, empty, success)
- Pruebas de regresión del flujo principal
- Tests funcionales para el happy path y negative path

## Riesgos de seguridad/IDOR/BOLA

1. **IDOR (Insecure Direct Object Reference)**: Verificar que usuarios no puedan acceder a objetos pertenecientes a otros usuarios/sucursales.
2. **BOLA (Broken Object Level Authorization)**: Asegurar que las operaciones CRUD se realicen únicamente para los datos autorizados.
3. **Exposición de información sensible**: Revisar que no se expongan contraseñas o credenciales en respuestas.

## Checklist de tareas

### Backend

- [ ] 1. Revisar entidades y reglas existentes.
- [ ] 2. Crear o ajustar entidades/value objects de dominio.
- [ ] 3. Crear casos de uso en application.
- [ ] 4. Crear interfaces de repositorio/ports.
- [ ] 5. Implementar repositorios SQLAlchemy en infrastructure.
- [ ] 6. Crear schemas Pydantic separados por contexto.
- [ ] 7. Crear/ajustar routers FastAPI.
- [ ] 8. Crear migraciones Alembic si aplica.
- [ ] 9. Agregar pruebas Pytest/HTTPX.
- [ ] 10. Validar permisos, ownership e IDOR/BOLA cuando aplique.

### Frontend

- [ ] 1. Revisar contrato de `BE-006`.
- [ ] 2. Definir rutas en `src/app`.
- [ ] 3. Crear feature en `src/features`.
- [ ] 4. Crear componentes reutilizables si aplica.
- [ ] 5. Crear formularios con validación.
- [ ] 6. Integrar cliente API.
- [ ] 7. Manejar errores HTTP 400/401/403/404/409/422/500.
- [ ] 8. Agregar estados visuales.
- [ ] 9. Validar responsive.
- [ ] 10. Agregar pruebas si el repo tiene framework configurado.

### QA

- [ ] 1. Identificar casos mínimos de test para usuarios, servicios y veterinarios.
- [ ] 2. Ejecutar prueba de happy path.
- [ ] 3. Ejecutar prueba de negative path.
- [ ] 4. Validar permisos por rol.
- [ ] 5. Validar IDOR/BOLA.
- [ ] 6. Verificar respuestas HTTP.
- [ ] 7. Verificar estados UI.
- [ ] 8. Validar regresión del flujo principal.

## Criterios de aceptación y Definition of Done

### Criterios de aceptación

- El contrato requerido para `FE-006` existe o queda documentado como mock temporal aprobado.
- Los routers no contienen lógica de negocio.
- No se exponen modelos ORM.
- Las respuestas son paginadas cuando hay listados.
- Los errores son consistentes y no filtran información interna.
- Las pruebas cubren al menos happy path y un negative path.

### Definition of Done

- [ ] Código backend implementado.
- [ ] Migraciones aplicadas o justificadas como no requeridas.
- [ ] Tests backend agregados/actualizados.
- [ ] Permisos y ownership validados.
- [ ] OpenAPI consistente.
- [ ] Sin alcance fuera del MVP.
