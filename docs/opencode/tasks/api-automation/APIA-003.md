"""Cobertura API externa para BE-003 - Landing pública y búsqueda

Este archivo se completa durante /implement-api-automation-task BE-003.
"""

schema_version: "3"

# ===========================================================================
# APIA-003 - Cobertura API externa para Landing pública y búsqueda
# ===========================================================================

## Metadata

| Campo | Valor |
|---|---|
| ID | APIA-003 |
| Slice vertical | BE-003 / FE-003 / QA-003 |
| Capa | Backend/API |
| Estado | BLOCKED |
| Framework | Playwright APIRequestContext |

## Alcance MVP

- Validar endpoints públicos de clínicas, sucursales y servicios.
- Confirmar que listados responden 200 sin autenticación.
- Verificar filtros (search, clinica_id, sucursal_id, clinica_id combinados).
- Comprobar paginación consistente en todos los listados.
- Validar estructura de respuestas DTOs públicos (sin ORM models expuestos).
- Verificar IDOR/BOLA: datos privados no se exponen en endpoints públicos.
- Comprobar errores 422 para params inválidos y 404 para IDs inexistentes.

## Fuera de alcance

- Pruebas de carga o rendimiento.
- Validación detallada de schemas response complejos más allá de campos clave.
- Simulación de ataques OASIS avanzados (solo IDOR/BOLA básico).
- Pruebas de autenticación/autorización (no aplica a endpoints públicos).

## Pruebas API planificadas

| ID | Criterio | Metodo | Ruta | Expected HTTP | Estado | Comentario |
|---|---|---|---|---|---|---|
| APIA-003-01 | Listado clínicas 200 sin auth | GET | /api/v1/clinicas | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-02 | Filtro search en clínicas | GET | /api/v1/clinicas?search=nombre | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-03 | Param inválido en clínicas | GET | /api/v1/clinicas?invalid_param=x | 422 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-04 | Detalle clinica existe | GET | /api/v1/clinicas/{id} | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-05 | Detalle clinica no existe | GET | /api/v1/clinicas/{invalid_id} | 404 | PASSED | Comportamiento correcto |
| APIA-003-06 | Listado sucursales 200 | GET | /api/v1/sucursales | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-07 | Filtro clinica_id en sucursales | GET | /api/v1/sucursales?clinica_id=X | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-08 | Listado servicios 200 | GET | /api/v1/servicios | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-09 | Filtros combinados servicios | GET | /api/v1/servicios?sucursal_id=X&clinica_id=Y | 200 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-10 | IDOR/BOLA datos privados no expuestos | GET | Todos los endpoints | 200/404 | BLOCKED | Backend endpoint no implementado (404) |
| APIA-003-11 | Estructura response sin ORM models | GET | Todos los endpoints | 200 | BLOCKED | Backend endpoint no implementado (404) |

## Criterios de aprobacion

- [ ] Todas las pruebas listadas tienen estado PASSED o JUSTIFIED_SKIP.
- [ ] No hay bloqueos de entorno (DB no levanta, servicios caidos).
- [ ] Evidencia escrita en Seccion Evidencia abajo.
- [ ] IDOR/BOLA verificado: ningún endpoint público expone datos privados.

## Evidencia

| Campo | Valor |
|---|---|
| Servidor usado | FastAPI local (uvicorn) |
| Puerto esperado | 8000 |
| Motor DB | PostgreSQL (via docker-compose.yml) |
| Resultado general | BLOCKED — BE-003 backend endpoints not implemented |
| Pruebas ejecutadas | 11 |
| Aprobadas | 1 (404 esperado para ID invalido) |
| Rechazadas | 10 (todos los endpoints retornan 404) |

## Hallazgos y correcciones

### Hallazgo: APIA-003-H01 — Bloqueo critico

| Campo | Valor |
|---|---|
| ID | APIA-003-H01 |
| Severidad | BLOCKER |
| Estado | OPEN |
| Descripcion | Endpoints publicos de BE-003 NO estan implementados — todos retornan 404 |
| Endpoint afectado | /api/v1/clinicas, /api/v1/sucursales, /api/v1/servicios |
| Evidencia | 10 de 11 pruebas fallaron con HTTP 404. El backend solo expone /api/v1/clinics/search (ruta en ingles, no coincide con el plan BE-003 que especifica /clinicas en espanol). No existen routers para sucursales ni servicios. |
| Corregido por | Pendiente — requiere implementacion de BE-003 |
| Revalidacion QA | PENDIENTE |

### Hallazgo: APIA-003-H02 — Ruta no coincide con plan

| Campo | Valor |
|---|---|
| ID | APIA-003-H02 |
| Severidad | HIGH |
| Estado | OPEN |
| Descripcion | Router existente usa prefix /clinics (ingles) en lugar de /clinicas (espanol) segun BE-003 plan |
| Endpoint actual | GET /api/v1/clinics/search |
| Endpoint esperado | GET /api/v1/clinicas con query params page, limit, search |
| Evidencia | Solo existe clinic_search.py con prefix="/clinics". No hay routers para sucursales (/sucursales) ni servicios (/servicios). |
| Corregido por | Pendiente — requiere ajuste de router o actualizacion del plan |
| Revalidacion QA | PENDIENTE |
