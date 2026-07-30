# BE-010 Plan — Recetas, tratamientos y recordatorios

## Objetivo del slice
Implementar la capacidad de registrar recetas médicas, tratamientos asociados y configurar recordatorios para los dueños de mascotas, todo vinculado a una consulta médica ya realizada (BE-009).

## Alcance MVP
- **Backend**: Creación, lectura y gestión de entidades `Receta`, `Tratamiento` y `Recordatorio`. Vinculación con la consulta médica (`Consulta`). Implementación de lógica para que los recordatorios sean consultables por el staff.
- **Frontend**: Formularios de creación/edición de recetas y tratamientos. Visualización de la lista de prescripciones dentro del detalle de una consulta médica. Configuración básica de recordatorios.

## Fuera de alcance
- Generación automática de PDFs con formato legal (se dejará como capacidad extendida).
- Integración con servicios de envío de SMS/WhatsApp (solo se preparará la persistencia del recordatorio).
- Notificaciones Push automáticas en tiempo real (el mecanismo de notificación debe ser el provisto por BE-013).
- Marketplace o venta de medicamentos.

## Suposiciones
- Se asume que las entidades `Consulta` y `Paciente/Mascota` ya existen y son accesibles desde este slice.
- Los "Recordatorios" se entienden como registros en la base de datos que el sistema debe procesar posteriormente (vía BE-013).

## Entidades y Reglas de Negocio
- **Receta**: Vinculada a una `Consulta`. Contiene instrucciones generales.
- **Tratamiento**: Vinculado a una `Receta` o directamente a la `Consulta`. Describe la dosificación y duración.
- **Recordatorio**: Vinculado a un `Tratamiento` o `Receta`. Tiene una fecha/hora programada y un estado (pendiente, completado, cancelado).
- **Regla de Ownership**: Solo el veterinario o staff autorizado de la clínica/sucursal puede crear/editar recetas. Los dueños de mascotas pueden ver las recetas pero no editarlas.

## Endpoints esperados (`/api//v1`)
- `POST /api/v1/consultas/{consulta_id}/recetas`: Crear una nueva receta para una consulta específica.
- `GET /api/v1/consultas/{consulta_id}/recetas`: Listar todas las recetas de una consulta.
- `GET /api/v1/recetas/{receta_id}`: Detalle de una receta y sus tratamientos asociados.
- `POST /api/v1/recetas/{receta_id}/tratamientos`: Agregar un tratamiento a una receta existente.
- `POST /api/v1/recetas/{receta_id}/recordatorios`: Programar un recordatorio para un tratamiento/receta.
- `GET /api/v1/staff/mis-recordatorios`: Listar recordatorios pendientes para el staff.

## Componentes Frontend esperados
- `RecetaForm`: Formulario de creación de receta médica.
- `TratamientoItem`: Componente de línea para listar tratamientos dentro de una receta.
- `RecordatorioSelector`: Selector de fecha y hora para programar alertas.
- `ConsultaPrescripcionesView`: Panel dentro de la vista de consulta que muestra el historial de prescripciones.

## Pruebas QA
- **Happy Path**: Creación completa de flujo (Receta -> Tratamiento -> Recordatorio) con datos válidos.
- **Negative Path**: Intentar crear receta para una consulta inexistente; intentar editar receta de otra clínica (BOLA).
- **Permisos**: Verificar que un usuario de la Clínica A no pueda ver recetas de la Clínica B.

## Riesgos de seguridad/IDOR/BOLA
- **BOLA (Broken Object Level Authorization)**: Un usuario podría intentar consultar `GET /api/v1/recetas/{id_ajeno}`. Se requiere validar que el `receta_id` pertenezca a una consulta de la misma clínica y que el usuario tenga permiso.
- **Inyección de datos**: Validar estrictamente los campos de dosificación para evitar scripts maliciosos en instrucciones médicas.

## Checklist técnico
- [ ] Rutas backend y prefijos API definidos (`/api/v1/...`).
- [ ] Contratos request/response documentados (schemas Pydantic).
- [ ] Permisos y ownership definidos por endpoint (Staff vs Dueño).
- [ ] Estados de error esperados (400 para datos inválidos, 403 para falta de permiso, 404 si la consulta no existe).
- [ ] Modelos SQLAlchemy y migraciones Alembic para `Receta`, `Tratamiento` y `Recordatorio`.
- [ ] Casos QA positivos y negativos trazados.
- [ ] Implementación de Pytest para lógica de negocio.
- [ ] Checks de linting (ruff, black, mypy) superados.
- [ ] Documentación de API actualizada (OpenAPI).

## Checklist de Tareas

### Backend (BE-010)
- [ ] 1.0 Crear modelos SQLAlchemy y migraciones para `Receta`, `Tratamiento` y `Recordatorio`.
  `Objetivo: Definir la persistencia de datos.`
  `Criterios de aceptacion: Las tablas existen en DB con relaciones correctas a Consulta/Paciente.`
  `Paralelismo[P]: No`
- [ ] 1.1 Implementar Repositorios y Casos de Uso para gestión de recetas y tratamientos.
  `Objetivo: Lógica de negocio desacoplada de la API.`
  `Criterios de aceptacion: Las operaciones CRUD funcionan sin dependencias de HTTP.`
  `Paralelismo[P]: No`
- [ ] 1.2 Implementar Schemas Pydantic para Request/Response.
  `Objetivo: Validación de entrada y serialización de salida.`
  `Criterios de aceptacion: Los esquemas validan tipos de datos y no exponen campos sensibles (ej. IDs internos ocultos si es necesario).`
  `Paralelismo[P]: Si`
- [ ] 1.3 Implementar API Endpoints en FastAPI.
  `Objetivo: Exponer la funcionalidad vía HTTP.`
  `Criterios de aceptacion: Los endpoints responden con los contratos definidos y manejan errores correctamente.`
  `Paralelismo[P]: Si`
- [ ] 1.4 Implementar validaciones de permisos (Ownership/BOLA).
  `Objetivo: Evitar acceso no autorizado a recetas de otras clínicas.`
  `Criterios de aceptacion: Un usuario de otra clínica recibe 403 al intentar acceder a una receta ajena.`
  `Paralelismo[P]: Si`

### Frontend (FE-010)
- [ ] 2.0 Crear servicios de API en `src/shared/api` para recetas y tratamientos.
  `Objetivo: Integración cliente-servidor.`
  `Criterios de aceptacion: Las llamadas a la API funcionan con los endpoints creados en BE.`
  `Paralelismo[P]: Si`
- [ ] 2.1 Implementar formulario `RecetaForm`.
  `Objetivo: Permitir la creación de recetas desde la UI.`
  `Criterios de aceptacion: El formulario valida campos obligatorios y envía los datos al backend.`
  `Paralelismo[P]: No`
- [ ] 2.2 Implementar componente `TratamientoItem` y gestión de lista en detalle de consulta.
  `Objetivo: Visualizar tratamientos asociados.`
  `Criterios de aceptacion: Se listan todos los tratamientos vinculados a la receta cargada.`
  `Paralelismo[P]: Si`
- [ ] 2.3 Implementar componente `RecordatorioSelector`.
  `Objetivo: Permitir programar alertas.`
  `Criterios de aceptacion: El usuario puede elegir fecha/hora y se guarda en el backend.`
  `Paralelismo[P]: No`

### QA (QA-010)
- [ ] 3.0 Ejecutar pruebas de Happy Path para flujo completo.
  `Objetivo: Validar funcionamiento nominal.`
  `Criterios de aceptacion: Se puede crear receta, tratamiento y recordatorio con éxito.`
 `Paralelismo[P]: No`
- [ ] 3.1 Ejecutar pruebas de Seguridad (BOLA/IDOR).
  `Objetivo: Garantizar que no hay fuga de datos entre clínicas.`
  `Criterios de aceptacion: El acceso a recursos ajenos devuelve 403 o 404 según configuración.`
  `Paralelismo[P]: No`
- [ ] 3.2 Ejecutar pruebas de validación de errores (Negative Path).
  `Objetivo: Validar robustez ante inputs erróneos.`
  `Criterios de aceptacion: Los errores 400/422 muestran mensajes claros y no rompen la UI.`
  `Paralelismo[P]: No`

## Definition of Done
- [ ] Todos los endpoints BE-010 están operativos y testeados.
- [ ] La interfaz FE-010 permite completar el flujo de prescripción.
- [ ] Las pruebas QA confirman la integridad de los datos y la seguridad del slice.
- [ ] El código cumple con los estándares de calidad (linting, tests).
