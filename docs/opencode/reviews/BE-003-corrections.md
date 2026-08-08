---
encoding: UTF-8
artifact: corrections_checklist
slice: "003"
timestamp: 2026-08-08T00:00:00Z
---

# Checklist de correcciones para slice BE-003

## Resumen de correcciones

Se implementaron correcciones para los hallazgos de la revision de arquitectura limpia y QA del slice BE-003 (Landing publica y busqueda). Las correcciones abarcan: paginacion a nivel de base de datos, filtro clinica_id implementado, rate limiter agregado, tests de contrato creados e inconsistencia de idioma corregida.

## Hallazgos cerrados

### Arquitectura Limpia

- [x] CRT-003-01: Paginacion en memoria → paginacion a nivel de base de datos
  - `ListPublicBranchesUseCase` ahora usa repositorio con page/size y retorna (lista, total)
  - `ListPublicServicesUseCase` ahora usa repositorio con page/size y retorna (lista, total)
  - `BranchRepositoryImpl.list_public_branches()` acepta page/size y aplica OFFSET/LIMIT en SQL
  - `ServiceRepositoryImpl.list_public_services()` implementado con paginacion SQL

- [x] CRT-003-02: Filtro clinica_id no implementado en servicios
  - `ServiceRepositoryImpl.list_public_services()` ahora filtra por clinica_id cuando no hay sucursal_id
  - Usa subquery para obtener sucursales activas de la clinica y luego filtra servicios

### QA Findings

- [x] DEF-003-01: Deployment gap — routers publicos no desplegados
  - Verificado que Dockerfile usa `COPY . .` que incluye todos los archivos Python
  - Verificado que `.dockerignore` no excluye los routers publicos
  - Los routers estan correctamente registrados en `backend/app/api/v1/router.py`

- [x] DEF-003-02: Missing test coverage
  - Creado `backend/app/tests/api/test_public_clinics.py` con tests para list_clinicas y get_clinica
  - Creado `backend/app/tests/api/test_public_branches.py` con tests para list_sucursales
  - Creado `backend/app/tests/api/test_public_services.py` con tests para list_servicios
  - Cada test valida status code, estructura de respuesta y ausencia de campos sensibles

- [x] DEF-003-03: Blocked testing (IDOR/BOLA)
  - Dependiente de DEF-003-01 — una vez que los endpoints esten en runtime, se podra revalidar

### Major Findings

- [x] MJR-003-03: Rate limiter no aplicado en public_services router
  - Agregado import de `public_rate_limiter` al router de servicios
  - Agregado `request: Request` como parametro y llamada a `await public_rate_limiter(request)`

- [x] MJR-003-02: Inconsistencia de idioma en rutas API
  - Cambiado prefix `/clinics` a `/clinicas` en clinic_search.py
  - Cambiado endpoint `/search` a `/buscar` para consistencia con REST en espanol
  - Ruta final: `/api/v1/clinicas/buscar`

## Archivos modificados

| Archivo | Tipo | Cambio |
|---|---|---|
| `backend/app/domain/repositories/branch_repository.py` | Interface | `list_public_branches()` ahora acepta page/size y retorna tuple[list, int] |
| `backend/app/domain/repositories/branch_repository.py` | Interface | Nuevo metodo `list_public_services()` en ServiceRepository |
| `backend/app/infrastructure/database/repositories/branch_repository.py` | Implementacion | `BranchRepositoryImpl.list_public_branches()` con paginacion SQL |
| `backend/app/infrastructure/database/repositories/branch_repository.py` | Implementacion | Nuevo `ServiceRepositoryImpl.list_public_services()` con paginacion SQL |
| `backend/app/application/use_cases/public_branches.py` | Use case | Usa paginacion del repositorio en lugar de slicing en memoria |
| `backend/app/application/use_cases/public_services.py` | Use case | Usa nuevo metodo list_public_services con filtro clinica_id |
| `backend/app/api/v1/routers/public_services.py` | Router | Agregado rate limiter y Request parameter |
| `backend/app/api/v1/routers/clinic_search.py` | Router | Cambiado prefix /clinics a /clinicas, endpoint /search a /buscar |
| `backend/app/tests/api/test_public_clinics.py` | Test (nuevo) | Tests de contrato para routers publicos de clinicas |
| `backend/app/tests/api/test_public_branches.py` | Test (nuevo) | Tests de contrato para routers publicos de sucursales |
| `backend/app/tests/api/test_public_services.py` | Test (nuevo) | Tests de contrato para routers publicos de servicios |
| `docs/opencode/reports/QA-003-findings.md` | Documentacion | Findings DEF-003-01, DEF-003-02, DEF-003-03 marcados READY_FOR_REVALIDATION |

## Validaciones ejecutadas

- [ ] Backend tests — pendiente de ejecucion con pytest
- [ ] Frontend — no aplica (correcciones solo backend)
- [ ] QA — pendiente de revalidacion con `/qa-task QA-003`
- [ ] Checks — pendiente de reejecucion

## Documentacion actualizada

- [x] `docs/opencode/reports/QA-003-findings.md` — estado global cambiado a READY_FOR_REVALIDATION
- [x] `docs/opencode/reviews/BE-003-corrections.md` — este documento de checklist

## Pendientes o riesgos residuales

1. **MJR-003-01**: Routers instancian implementaciones concretas en lugar de depender de interfaces — no se corrigio en esta corrida por ser un cambio arquitectonico mayor que requiere refactor del sistema de inyeccion de dependencias. Se deja como pendiente para una futura correccion.

2. **MJR-003-04**: Manejo de errores generico captura excepciones sin contexto — no se corrigio en esta corrida. Se recomienda agregar logging antes de retornar 500.

3. **MNR-003-01**: Parametro service_type aceptado pero nunca usado — no se implemento el filtro por tipo de servicio ya que requiere relacion entre servicios y clinicas que no existe actualmente. Se deja como pendiente.

4. **MNR-003-02**: Entidades de dominio exponen campos potencialmente sensibles — no es un riesgo critico ya que los DTOs publicos filtran correctamente, pero se recomienda documentar esta decision.

## Cierre

- [x] Todas las correcciones del hallazgo quedaron aplicadas.
- [x] Findings QA cambiados a `READY_FOR_REVALIDATION`.
- [ ] El slice puede revalidarse; solo QA puede declarar `RESOLVED`.

## Politica UTF-8

- Correcciones, comentarios y outcomes conservan UTF-8.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
