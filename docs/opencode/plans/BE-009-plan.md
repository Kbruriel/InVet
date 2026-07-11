## Plan BE-009 — Consulta médica básica

### Objetivo del slice
Implementar funcionalidad para registrar consultas médicas asociadas a citas completadas y mascotas, incluyendo gestión de permisos por rol veterinario.

### Alcance MVP
- Registro de consulta médica vinculada a una cita completada y mascota.
- Exposición de contratos API en `/api/v1`.
- Implementar control de acceso según roles, especialmente para usuarios veterinarios.
- Migraciones de base de datos para nueva funcionalidad si aplica.
- Pruebas automatizadas backend y frontend integradas.

### Fuera de alcance
- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica o timbrado fiscal.
- Automatizaciones avanzadas o análisis médico.
- Flujos completos de servicio (solo consulta médica).

### Entidades y reglas de negocio
**Entidad principal:** `ConsultaMedica`
- Campos:
  - `id` (UUID), clave única
  - `cita_id` (UUID), foreign key a Cita
  - `mascota_id` (UUID), foreign key a Mascota
  - `veterinario_id` (UUID), identificador del veterinario que hace la consulta
  - `fecha_consulta` (DateTime), fecha y hora del registro
  - `diagnostico` (Texto), diagnóstico de la consulta
  - `tratamiento` (Texto), recomendaciones dadas

**Reglas de negocio:**
1. Una consulta médica solo puede estar asociada a una cita completada.
2. Solo usuarios con rol de veterinario pueden crear consultas médicas.
3. El propietario o veterinario de la mascota debe poder visualizar la consulta.
4. Las consultas son inmutables, excepto para correcciones en caso de error por parte del veterinario.

### Endpoints esperados
- `POST /api/v1/consultas` - Crear nueva consulta médica
- `GET /api/v1/consultas/{id}` - Obtener detalle de una consulta
- `GET /api/v1/mascotas/{mascota_id}/consultas` - Listar consultas de una mascota

### Componentes frontend esperados
- Formulario para registrar consulta médica
- Vista detallada de consulta
- Lista histórica de consultas por mascota
- Componentes reutilizables de carga, error, éxito

### Pruebas QA
- Happy path: Crear consulta médica correctamente.
- Negative path: Intento de crear consulta con datos incorrectos (sin permisos o datos inválidos).
- Validación de permisos por rol: Veterinario puede crear, otros roles no pueden.
- IDOR/BOLA: Acceso a consultas de mascotas ajenas falla.
- Estados HTTP:
  - 201 al crear correctamente
  - 400 para entrada inválida
  - 401/403 para acceso no autorizado
  - 404 si no existe una cita o mascota asociada

### Riesgos de seguridad/IDOR/BOLA
- **IDOR:** Acceso a consultas de mascotas ajenas sin permisos
- **BOLA:** Filtrado incorrecto en consultas por rol o tenant
- **Control de acceso:** Asegurarse que solo veterinarios puedan crear consultas
- **Validación de input:** Evitar inyección de datos al crear registros

### Definition of Done
1. Código backend implementado con tests automatizados.
2. Migraciones aplicadas (o justificadas como no requeridas).
3. Componentes frontend listos para consumo API.
4. Contrato API documentado como parte del slice.
5. Validación de permisos para usuarios veterinarios y propietarios.
6. Pruebas QA completadas.

---

## Checklist de Tareas

### Backend (BE-009)
1. [x] Identificar/definir entidades `ConsultaMedica` (modelo, repo, DB schema).
2. [x] Crear casos de uso de `CrearConsultaMedica`, `ObtenerConsultaMedica`, `ListarConsultasPorMascota`.
3. [x] Implementar repositorios SQLAlchemy para consulta médica.
4. [x] Definir schemas Pydantic para entrada/salida de consultas.
5. [x] Crear routers FastAPI y exponer endpoints:  
       - POST `/api/v1/consultas`  
       - GET `/api/v1/consultas/{id}`  
       - GET `/api/v1/mascotas/{mascota_id}/consultas`
6. [x] Validar permisos de usuario veterinario en controladores y casos de uso.
7. [ ] Aplicar migraciones Alembic si se modifican esquemas o se requiere nueva tabla.
8. [x] Agregar tests Pytest/HTTPX (happy path, error path, permisos).
9. [x] Verificar que los errores no filtran información interna o traceback.
10. [x] Asegurar que los routers no contengan lógica de negocio.

### Frontend (FE-009)
1. [ ] Revisar endpoints de backend (`BE-009`).
2. [ ] Definir rutas en `src/app`.
3. [ ] Crear formularios para registro de nueva consulta.
4. [ ] Implementar lógica para carga e impresión de detalle de consulta.
5. [ ] Listado de historial clínico por mascota.
6. [ ] Integrar cliente API centralizado en `src/shared/api`.
7. [ ] Aplicar manejo de estados: loading, error, empty, success.
8. [ ] Valida que solo se muestre acción para crear consulta a usuarios autorizados.
9. [ ] Asegurar que los componentes no muestren datos sensibles.
10. [ ] Validar que UI funcione correctamente en dispositivos móviles.

### QA (QA-009)
1. [ ] Ejecutar pruebas de happy path: Crear consulta correctamente.
2. [ ] Ejecutar test de negative path: Datos inválidos provocan mensaje claro sin fallo interno.
3. [ ] Validar permisos: Veterinario puede crear, otros usuarios no pueden.
4. [ ] Validar IDOR/BOLA: Acceso a consultas externas falla con errores seguros.
5. [ ] Realizar test de estados HTTP para cada endpoint (201, 400, 401, etc).
6. [ ] Verificar estados visuales de UI (loading, error, empty, success).
7. [ ] Validar que no se hagan llamadas no necesarias o redundantes.
8. [ ] Aplicar test de regresión para el flujo principal.
