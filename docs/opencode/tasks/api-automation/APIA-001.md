"""Cobertura API externa para BE-001 - Slice 001 (Base tecnica y design system)

Este archivo se completa durante /implement-api-automation-task BE-001.
"""

schema_version: "3"

# ===========================================================================
# APIA-001 - Cobertura API externa para Base tecnica y design system
# ===========================================================================

## Metadata

| Campo | Valor |
|---|---|
| ID | APIA-001 |
| Slice vertical | BE-001 / FE-001 / QA-001 |
| Capa | Backend/API |
| Estado | PENDING |
| Framework | Playwright APIRequestContext |

## Alcance MVP

- Validar que los endpoints base del backend responden correctamente.
- Confirmar que el healthcheck retorna estado saludable.
- Verificar comportamiento de rutas protegidas (401 sin token).
- Comprobar estructura OpenAPI disponible.

## Fuera de alcance

- Pruebas de carga o rendimiento.
- Validacion detallada de schemas response complejos.
- Simulacion de ataques OASIS/IDOR por ahora.

## Pruebas API planificadas

| ID | Criterio | Metodo | Ruta | Expected HTTP | Estado | Comentario |
|---|---|---|---|---|---|---|
| APIA-001-01 | Raiz responde 200 con mensaje JSON | GET | / | 200 | PENDING | Mensaje debe contener "InVet" |
| APIA-001-02 | Healthcheck responde healthy | GET | /health | 200 | PENDING | status=healthy |
| APIA-001-03 | Raiz v1 responde | GET | api/v1/ | 200 | PENDING | Estructura base |
| APIA-001-04 | Auth login requiere body | POST | api/v1/auth/login | 422 | PENDING | Validacion Pydantic |
| APIA-001-05 | Perfil requiere auth | GET | api/v1/auth/me | 401 | PENDING | Sin token=rechazado |
| APIA-001-06 | OpenAPI schema disponible | GET | openapi.json | 200 | PENDING | Swagger/Redoc disponibles |

## Criterios de aprobacion

- [ ] Todas las pruebas listadas tienen estado PASSED o JUSTIFIED_SKIP.
- [ ] No hay bloqueos de entorno (DB no levanta, servicios caidos).
- [ ] Evidencia escrita en Seccion Evidencia abajo.

## Evidencia

| Campo | Valor |
|---|---|
| Servidor usado | FastAPI local (uvicorn) |
| Puerto esperado | 8000 |
| Motor DB | PostgreSQL (via docker-compose.yml) |
| Resultado general | Pendiente de ejecucion |
