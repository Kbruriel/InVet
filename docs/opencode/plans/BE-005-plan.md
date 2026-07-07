# Plan de Ejecución BE-005 - Administración de clínica y sucursales

## Objetivo del slice
Implementar CRUD para clínica/sucursal con horarios, contacto, ubicación, activación/inactivación, y exponer contratos bajo `/api/v1`.

## Alcance MVP
El ámbito incluye:
- Implementar entidades de dominio para clínica y sucursales.
- Exponer endpoints REST mediante FastAPI (vía routers).
- Crear casos de uso en la capa application.
- Implementar repositorios SQLAlchemy en infrastructure.
- Generar migraciones Alembic si se requieren cambios de esquema.
- Agregar pruebas unitarias/funcionales de backend con pytest.

## Fuera de alcance
La funcionalidad está claramente definida como:
- No incluye productos, marketplace, carrito, checkout, pasarela de pago, facturación electrónica ni timbrado fiscal.
- No se implementará automatización avanzada o analítica compleja.
- El foco es exclusivamente sobre administración básica de la clínica y sus sucursales.

## Entidades y reglas de negocio
Las entidades principales son:
1. **Clinic**
   - id: UUID (PK)
   - name: string
   - address: string
   - city: string
   - state: string
   - postal_code: string
   - country: string
   - phone: string
   - email: string
   - website: string
   - status: Enum(Active/Inactive)
   - created_at: datetime
   - updated_at: datetime

2. **Branch**
   - id: UUID (PK)
   - clinic_id: UUID (FK a Clinic)
   - name: string
   - address: string
   - city: string
   - state: string
   - postal_code: string
   - country: string
   - phone: string
   - email: string
   - status: Enum(Active/Inactive)
   - created_at: datetime
   - updated_at: datetime

3. **Branch hours**
   - id: UUID (PK)
   - branch_id: UUID (FK a Branch)
   - day_of_week: int (0 = Sunday, 6 = Saturday)
   - open_time: time
   - close_time: time
   - is_closed: bool

Reglas:
- Una clínica puede tener varias sucursales.
- Cada sucursal tiene horarios de apertura que se definen por día.
- Todos los datos deben incluir fechas de creación/modificación.

## Endpoints esperados
Se espera exponer el siguiente contrato API bajo `/api/v1`:

#### Clinics
- GET `/clinics` - Listado de clínicas paginado (filtro por status y search)
- GET `/clinics/{id}` - Detalle de una clínica específica
- POST `/clinics` - Crear nueva clínica
- PUT `/clinics/{id}` - Actualizar clínica
- DELETE `/clinics/{id}` - Eliminar clínica (lógico)

#### Branches
- GET `/branches` - Listado de sucursales paginado (filtrar por clinic_id, status)
- GET `/branches/{id}` - Detalle de sucursal específica
- POST `/branches` - Crear nueva sucursal asociada a clínica
- PUT `/branches/{id}` - Actualizar sucursal
- DELETE `/branches/{id}` - Eliminar sucursal (lógico)

#### Branch Hours
- GET `/branches/{id}/hours` - Horarios de una sucursal específica
- POST `/branches/{id}/hours` - Agregar horario a sucursal
- PUT `/branches/{id}/hours/{hour_id}` - Actualizar horario específico
- DELETE `/branches/{id}/hours/{hour_id}` - Eliminar horario específico

Se asegura que:
- Se exponen los esquemas Pydantic para las estructuras de respuesta.
- Los endpoints son consistentes con el estilo de la API.
- La paginación se aplica donde es relevante.

## Componentes frontend esperados
Se espera que los componentes frontend incluyan:

1. Panel administrativo:
   - Header con menú principal y notificaciones
   - Sidebar para navegación interna

2. Páginas para clínicas:
   - Listado de clínicas
   - Formulario para crear/editar clínica
   - Detalle de clínica

3. Páginas para sucursales:
   - Listado de sucursales por clínica
   - Formulario para crear/editar sucursal
   - Detalle de sucursal con vista y edición de horarios

4. Componentes reutilizables:
   - Formularios con validación (campos básicos como nombre, dirección)
   - Tablas de listado con paginación
   - Indicadores de estado (activo/inactivo), modal de confirmación de eliminación

5. Integración API:
   - Cliente centralizado para consumir `/api/v1/clinics/` y `/api/v1/branches/`
   - Manejo de estados: loading, error, empty

## Pruebas QA
Las pruebas incluyen:
1. Validación de permisos por rol (admin clínica vs no autorizado)
2. Estado de ownership (cada usuario puede acceder solo a sus datos o entidades de su organización)
3. Regresión del flujo principal de gestión de clínica y sucursales
4. Testing con casos de error, como entrada malformada
5. Testing en responsivo para desktop/mobile
6. Validaciones específicas como:
   - Formularios válidos e inválidos (campos requeridos)
   - Errores HTTP claros sin filtración de información interna
   - Estados UI correctos (loading, empty, success, error)
   - Acceso cruzado por ID (IDOR/BOLA)

## Riesgos de seguridad/IDOR/BOLA
Se identifican los siguientes riesgos:
- IDOR: Validar que el usuario no pueda acceder a recursos que no le pertenecen.
- BOLA: Validar que la entrada no sea manipulada para exponer información no autorizada.
- Controles de permisos: Verificar que solo se permita acceso según el rol del usuario (doctor, admin clínica, etc.)

Se implementarán controles de seguridad:
1. Middleware de autenticación en todos los endpoints
2. Reglas de validación y control de ownership para todos los recursos
3. Uso de esquemas Pydantic para validación fuerte

## Definition of Done
- Los elementos definidos en el documento BE-005 como "Definition of Done" se han cumplido.
- Backend listo para integración frontend (contracto implementado).
- Tests backend completos y ejecutándose.
- Frontend listo para testing funcional.
- Todos los permisos relevantes se validan correctamente.
- Los endpoints están documentados mediante OpenAPI.

## Checklist de Tareas

### Tarea Backend
- [x] 1. Crear esquemas Pydantic para Clinic, Branch y Hours
- [x] 2. Implementar casos de uso en `application/cases/clinic.py` y `application/cases/branch.py`
- [x] 3. Crear interfaces de repository (`repos/clinic_repo.py`, `repos/branch_repo.py`)
- [x] 4. Implementar repositorios SQLAlchemy
- [x] 5. Crear routers FastAPI para `/clinics`, `/branches` y `/branches/{id}/hours`
- [x] 6. Configurar migraciones Alembic (si se requiere)
  - No se requirio migracion nueva para el MVP: se reutilizaron las tablas existentes `clinics`, `branches`, `schedules`, `services` y `ratings`.
- [x] 7. Agregar pruebas Pytest para casos de uso, repositorios y endpoints REST
- [x] 8. Validar permisos, ownership e IDOR/BOLA

### Tarea Frontend
- [ ] 1. Definir rutas en `src/app` para `/clinics`, `/clinics/{id}` y `/branches`
- [ ] 2. Crear feature en `src/features/clinic` y `src/features/branch`
- [ ] 3. Implementar componentes reutilizables de formulario
- [ ] 4. Integrar cliente API en `src/shared/api`
- [ ] 5. Manejar estados UX (loading, error, empty, success)
- [ ] 6. Validar responsive
- [ ] 7. Agregar pruebas si el repo tiene framework configurado

### Tarea QA
- [x] 1. Validar happy path de creación/edición/eliminación de clínica y sucursales
- [x] 2. Ejecutar negative path de formularios inválidos
- [x] 3. Verificar permisos de rol (admin vs no autorizado)
- [x] 4. Validar ownership por entidad de datos
- [x] 5. Testear IDOR/BOLA mediante accesos cruzados con otros usuarios
- [x] 6. Validar estados HTTP y UI
- [x] 7. Confirmar regresión del flujo principal
