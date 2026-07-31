# BE-003 — Plan de ejecución

## Objetivo del slice

Implementar endpoints públicos para exponer clínicas, servicios, sucursales, filtros y paginación. Los endpoints deben estar bajo `/api/v1` y cumplir con las reglas de separación entre capas y seguridad definidas en la arquitectura.

## Alcance MVP

- Implementar capas backend para el slice `003` (Landing pública y búsqueda).
- Exponer endpoint `/api/v1/clinics` con soporte para búsqueda, filtros y paginación.
- Definir estructuras Pydantic de respuesta.
- Agregar pruebas automatizadas y validaciones de seguridad.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica ni timbrado fiscal.
- Automatizaciones avanzadas o analítica avanzada salvo que este slice sea de hardening y solo como preparación documental.

## Suposiciones

- Los modelos para clínicas/sucursales ya existen.
- El backend se implementa en Python con FastAPI, SQLAlchemy y Alembic.
- Las pruebas serán ejecutadas en entornos aislados.
- No se requiere integración o migraciones al sistema de autenticación (ya definida en BE-002).

## Entidades y reglas de negocio

### Entidades

1. **Clinica**
   - Propiedades: `id`, `nombre`, `direccion`, `ciudad`, `telefono`, `email`, `horario_atencion`, `latitud`, `longitud`.
   - Regla: Un ID único y no nulo.
2. **Sucursal** (Relacionado con Clínica)
   - Propiedades: `id`, `nombre`, `direccion`, `ciudad`, `telefono`, `email`, `horario_atencion`, `latitud`, `longitud`, `clinic_id`.
   - Regla: Todas las sucursales deben estar asociadas a una clínica.

### Reglas de negocio

- Las respuestas son paginadas cuando hay listados.
- La búsqueda pública se basa en filtros como nombre, ciudad y servicios ofrecidos.
- Los errores son consistentes y no filtran información interna.
- Las rutas no contienen lógica de negocio.

## Endpoints esperados bajo `/api/v1`

### GET /clinics

- Descripción: Obtiene lista paginada de clínicas incluyendo sucursales.
- Parámetros:
  - `page` (opcional, int): número de página.
  - `size` (opcional, int): cantidad de elementos por página.
  - `search` (opcional, str): texto para búsqueda avanzada.
  - `city` (opcional, str): filtrar por ciudad.
- Respuesta:
  - 200 OK: Lista paginada
  - 400 Bad Request: Parámetros inválidos
  - 401 Unauthorized: No autenticado
  - 403 Forbidden: Acceso no permitido

## Componentes frontend esperados

### Rutas

- `src/app/clinics/` para página de búsqueda de clínicas.
- `src/app/search/` para landing principal con buscador.

### Componentes

- `ClinicCard` para representar clínica en lista.
- `SearchForm` para formulario de búsqueda.
- `FiltersBar` para aplicar filtros por ciudad.
- `LoadingSkeleton`, `EmptyState`, `ErrorMessage`.

## Pruebas QA

### Casos Positivos

1. Acceso a `/api/v1/clinics` desde IP anónima.
2. Respuesta paginada con datos de clínicas.
3. Filtros funcionan correctamente (ciudad, búsqueda).

### Casos Negativos

1. Llamada sin autenticación recibe 401.
2. Parámetros inválidos devuelven 400.

### Criterios de aceptación

- Todos los endpoints de `/api/v1/clinics` son accesibles por usuarios no autenticados.
- Los listados están paginados y responden con formato definido.
- Se valida el uso correcto de filtros avanzados y búsqueda.
- No se exponen modelos ORM en respuesta.
- Errores no filtran informacion interna.
- Las rutas siguen reglas de autenticación de BE-002.

## Riesgos de seguridad/IDOR/BOLA

1. **IDOR**: Asegurar que las clínicas devueltan solo datos públicos.
2. **BOLA**: Validar que no se expongan claves o rutas internas en respuesta de errores.
3. **Ruta de búsqueda**: El acceso a `/api/v1/clinics?search=xxx` debe filtrar adecuadamente.

## Checklist numerado

### Backend

- [ ] Revisar entidades Clínica y Sucursal.
- [ ] Crear casos de uso para obtención de clínicas con filtros.
- [ ] Crear interfaces de repositorio/ports.
- [ ] Implementar repositorios SQLAlchemy.
- [ ] Crear schemas Pydantic específicos para respuesta de `/api/v1/clinics`.
- [ ] Crear router `/api/v1/clinics` y endpoint `GET`.
- [ ] Implementar paginación, búsqueda avanzada y filtros por ciudad.
- [ ] Agregar pruebas Pytest con HTTPX para escenarios happy_path y error.
- [ ] Validar permisos de acceso para endpoints públicos.
- [ ] Actualizar OpenAPI.

### Frontend

- [ ] Consumir `/api/v1/clinics` en feature `ClinicsSearch`.
- [ ] Implementar componentes: `SearchBar`, `ClinicCard`, `LoadingSkeleton`.
- [ ] Manejar estado HTTP 400, 401, 403, 404.
- [ ] Integrar con `src/shared/api` para llamadas.
- [ ] Validar responsive para mobile y desktop.

### QA

- [ ] Ejecutar test de happy path desde `/api/v1/clinics`.
- [ ] Verificar que se devuelvan listados paginados.
- [ ] Validar que filtros funcionan correctamente.
- [ ] Asegurar que parámetros inválidos devuelven 400.
- [ ] Validar seguridad IDOR/BOLA en endpoints públicos.
- [ ] Verificar estados UI: loading, error, empty, success.

## Checklist técnico

### Backend:

- [ ] Rutas backend definidas: `/api/v1/clinics`.
- [ ] Contratos request/response documentados (Pydantic).
- [ ] Permisos del endpoint: `public` (sin autenticación requerida).
- [ ] Estados de error esperados: 400, 401, 403, 404.
- [ ] Migraciones o cambios de persistencia identificados (se asume que `Clinic`, `Branch` ya están).
- [ ] Caso QA positivo y negativo trazado a criterios de aceptación.
- [ ] Checks esperados: pytest, black, mypy.

### Frontend:

- [ ] Componentes integrados con librería de UI compartida.
- [ ] Consumo centralizado desde `src/shared/api`.
- [ ] Gestionar loading/error/empty/success en todos los casos.
- [ ] Tests configurados (no implementados aún).

### QA:

- [ ] Comandos ejecutados (curl/postman).
- [ ] Resultados de pruebas comparados con criterios de aceptación.
- [ ] Validaciones de estados HTTP documentadas.

## Definition of Done

- Implementación backend completa: todos los puntos de checklist técnico de backend completos.
- Implementación frontend: todas las tareas del checklist frontend completas.
- Pruebas QA: todos los casos de prueba ejecutados y resultados validados.
- Documentación actualizada en `docs/opencode/plans/BE-003-plan.md`.
- Verificación de alcance y criterios de aceptación según definido.
