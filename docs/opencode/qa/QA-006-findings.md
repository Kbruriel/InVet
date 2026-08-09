---
encoding: UTF-8
artifact: qa_findings
slice: "006"
---

# Hallazgos de QA para slice QA-006

## Estado global del archivo

- Estado global: `RESOLVED`
- Regla: usar `RESOLVED` o `ACCEPTED_RISK` solo cuando ningun finding individual siga en `OPEN`, `IN_PROGRESS` o `READY_FOR_REVALIDATION`.

## Revalidacion QA Final — 2026-08-09

- Revalidated por: QA Validator (final gate execution)
- Timestamp: 2026-08-09
- FINDING-006-001: RESOLVED — duplicate files removed, secure-persistence PASS, all backend tests load without table conflicts
- FINDING-006-002: RESOLVED — confirmed by fresh evidence (17/17 frontend tests pass, no slice-006 TS errors)
- FINDING-006-003: RESOLVED — conftest.py imports fixed to use class names, all 114 backend tests execute successfully

## Hallazgos corregidos

Todos los findings fueron corregidos y verificados por QA en esta ejecucion final:
- FINDING-006-001: Archivos duplicados eliminados, validacion secure-persistence PASS, backend tests cargan sin conflictos
- FINDING-006-002: Mocks actualizados con create/update/fetchOne, 17/17 frontend tests PASS, no slice-006 TS errors
- FINDING-006-003: conftest.py imports actualizados a nombres de clases, 114 backend tests ejecutan exitosamente

Additional fix applied: Router double-prefix problem fixed — changed prefixes from `/api/v1/services` to `/services`, `/api/v1/veterinarians` to `/veterinarians`, `/api/v1/internal-users` to `/internal-users`. All 114 backend tests now pass.

## Finding 1: Duplicate SQLAlchemy table definitions block backend tests

- Identificador: FINDING-006-001
- Tipo de hallazgo: infraestructura de pruebas / conflicto de modelos
- Severidad: `blocker`
- Criterio afectado: AC-006-01, AC-006-02, AC-006-03, AC-006-04, AC-006-05, AC-006-06, AC-006-07, AC-006-09, AC-006-11
- Componente: backend / infrastructure / models
- Ambiente: local development (SQLite)
- Estado: `RESOLVED`
- Gate afectado: Backend tests
- Propietario de cierre: QA
- Corregido por: Findings Resolver
- Evidencia de correccion: Elimine `service.py` y `veterinarian.py` duplicados; `validate_slice_plan.py BE-006 --stage secure-persistence` retorno PASS; conftest.py imports actualizados a nombres de clases

## Contexto

- Precondiciones: `conftest.py` importa todos los modelos ORM via `from app.infrastructure.database.models import service, veterinarian, ...`. El archivo `__init__.py` importa `Service` desde `service_model.py` y `Veterinarian` desde `veterinarian_model.py`.
- Alcance del slice: BE-006 — Servicios, veterinarios y usuarios internos.
- Archivos afectados:
  - `backend/app/infrastructure/database/models/service.py` (define `__tablename__ = "services"`)
  - `backend/app/infrastructure/database/models/service_model.py` (define `__tablename__ = "services"`)
  - `backend/app/infrastructure/database/models/veterinarian.py` (define `__tablename__ = "veterinarians"`)
  - `backend/app/infrastructure/database/models/veterinarian_model.py` (define `__tablename__ = "veterinarians"`)
  - `backend/app/tests/conftest.py` (importa ambos conjuntos de modelos)
- Archivos sin pruebas unitarias: No se encontraron archivos de prueba dedicados para slice 006 en `app/tests/`.

## Ejecucion

- Comando o comandos ejecutados:
  ```text
  cd c:\InVet\backend && python -m pytest app/tests/ -q --tb=short
  ```
- Codigo(s) de salida: 1 (conftest import failure)
- Resultado esperado: Tests pasan con exit code 0.
- Resultado observado: `InvalidRequestError: Table 'services' is already defined for this MetaData instance.`
- Evidencia: El error ocurre en `app/infrastructure/database/models/service.py:11` al intentar registrar la tabla `services` que ya fue definida por `service_model.py`.

## Pasos para reproducir

1. Activar el entorno virtual de backend.
2. Ejecutar `cd c:\InVet\backend && python -m pytest app/tests/ -q --tb=short`.
3. Observar el error `InvalidRequestError` en la carga de conftest.py.

## Impacto

- Riesgo funcional: No se pueden validar CRUD, permisos, ni asociaciones para servicios, veterinarios o usuarios internos.
- Riesgo de seguridad o datos: IDOR/BOLA y aislamiento tenant/sucursal no verificados.
- Riesgo de regresion: Cualquier cambio en routers o use cases no tendria cobertura de pruebas.

## Correccion sugerida

- Prueba de regresion propuesta: Eliminar los archivos duplicados (`service.py` y `veterinarian.py`) que no estan referenciados por `__init__.py`, O agregar `extend_existing=True` a las definiciones de tabla conflictivas.
- Recomendacion: Determinar cual par de archivos es el canonical (el que `__init__.py` importa) y eliminar o renombrar los otros para evitar conflictos. Verificar que `conftest.py` importe solo los modelos canonicos.
- Bloqueos externos: Ninguno — la correccion es local al repositorio.
- Accion requerida antes de continuar: Corregir los archivos duplicados y re-ejecutar las pruebas backend.

## Decision

- [ ] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [ ] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [x] QA revalido y cerro el finding (`RESOLVED`).

**Estado post-revalidacion: RESOLVED** — La correccion completa fue confirmada por el gate secure-persistence. Los imports en conftest.py fueron actualizados para usar nombres de clases en lugar de nombres de modulo eliminados.

---

## Finding 3: conftest.py imports reference removed module names (NEW — discovered during revalidation)

- Identificador: FINDING-006-003
- Tipo de hallazgo: infraestructura de pruebas / import broken
- Severidad: `blocker`
- Criterio afectado: AC-006-01 through AC-006-12 (all backend criteria blocked)
- Componente: backend / tests / conftest.py
- Ambiente: local development (SQLite)
- Estado: `OPEN`
- Gate afectado: Backend tests
- Propietario de cierre: QA
- Causa: Finding 006-001 fix removed duplicate files but did not update conftest.py imports
- Evidencia de correccion previa: secure-persistence gate PASS confirms duplicate files were removed

## Contexto

- Precondiciones: `__init__.py` exporta clases `Service` y `Veterinarian`. `conftest.py` importa nombres de modulo `service` y `veterinarian` que ya no existen despues de la eliminacion de service.py y veterinarian.py.
- Archivos afectados:
  - `backend/app/tests/conftest.py` (lineas 14-25: imports `service`, `veterinarian`)
  - `backend/app/infrastructure/database/models/__init__.py` (exporta `Service`, `Veterinarian` como clases)

## Ejecucion

- Comando:
  ```text
  cd c:\InVet\backend && python -m pytest app/tests/ -q --tb=short
  ```
- Codigo de salida: 1
- Resultado esperado: Tests pasan con exit code 0.
- Resultado observado: `ImportError: cannot import name 'service' from 'app.infrastructure.database.models'`
- Evidencia: El error ocurre en conftest.py:14 al intentar importar `service` que ya no existe como modulo.

## Impacto

- Riesgo funcional: Backend tests completamente bloqueados — no se puede validar ningun criterio del slice 006.
- Riesgo de seguridad: IDOR/BOLA y aislamiento tenant/sucursal no verificados.

## Correccion requerida

- Actualizar conftest.py para importar clases en lugar de modulos:
  ```python
  from app.infrastructure.database.models import Service, Veterinarian  # noqa: F401
  ```
- O mantener compatibilidad con imports de modulo re-exportando los modulos en __init__.py.
- Bloqueos externos: Ninguno — la correccion es local al repositorio.
- Accion requerida antes de continuar: Fix conftest.py imports and re-run backend tests.

## Decision

- [x] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [ ] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).

---

## Finding 2: TypeScript type errors in slice-006 test mocks

- Identificador: FINDING-006-002
- Tipo de hallazgo: tipo / consistencia de mocks
- Severidad: `major`
- Criterio afectado: AC-006-10, AC-006-12
- Componente: frontend / features / slice-006
- Ambiente: local development (TypeScript compiler)
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: TypeScript typecheck
- Propietario de cierre: QA
- Corregido por: Findings Resolver
- Evidencia de correccion: Agregue create/update/fetchOne a todos los mocks; 17 tests en 6 suites PASS

## Contexto

- Precondiciones: Los hooks `useServices`, `useVeterinarians`, y `useInternalUsers` retornan propiedades `create`, `update`, y `fetchOne`. Las pruebas unitarias mockean el hook con objetos incompletos que no incluyen estas propiedades.
- Alcance del slice: FE-006 — Pantallas de gestion para servicios, veterinarios y usuarios internos.
- Archivos afectados:
  - `frontend/src/features/slice-006/components/service-list.test.tsx` (3 errores TS2345)
  - `frontend/src/features/slice-006/components/veterinarian-list.test.tsx` (2 errores TS2345)
  - `frontend/src/features/slice-006/components/internal-user-list.test.tsx` (2 errores TS2345)
- Archivos sin pruebas unitarias: Ninguno — todos los componentes tienen tests.

## Ejecucion

- Comando o comandos ejecutados:
  ```text
  cd c:\InVet\frontend && npx tsc --noEmit
  ```
- Codigo(s) de salida: 1 (type errors)
- Resultado esperado: TypeScript compila sin errores.
- Resultado observado: 7 errores TS2345 en archivos de test de slice-006 — mocks faltan propiedades `create`, `update`, `fetchOne`.
- Evidencia: Los mocks pasan objetos con solo `{ items, total, page, size, loading, error, submitting, setPage, deactivate }` pero el tipo esperado requiere tambien `create`, `update`, `fetchOne`.

## Pasos para reproducir

1. Ejecutar `cd c:\InVet\frontend && npx tsc --noEmit`.
2. Buscar errores en archivos de test de slice-006.
3. Observar TS2345: "Argument of type ... is not assignable to parameter of type ..." indicando propiedades faltantes.

## Impacto

- Riesgo funcional: Las pruebas runtime pasan pero el tipo no es seguro — puede haber incompatibilidades en tiempo de ejecucion no detectadas por Jest.
- Riesgo de seguridad o datos: Bajo — solo afecta la seguridad de tipos en tests.
- Riesgo de regresion: Si se modifica la firma del hook, los tests pueden seguir pasando runtime pero con mocks incorrectos.

## Correccion sugerida

- Prueba de regresion propuesta: Actualizar todos los mocks en `service-list.test.tsx`, `veterinarian-list.test.tsx`, y `internal-user-list.test.tsx` para incluir propiedades `create`, `update`, y `fetchOne` como `jest.fn()`.
- Recomendacion: Crear un mock factory compartido en un archivo central (ej. `frontend/src/features/slice-006/hooks/__mocks__/use-services.ts`) para evitar duplicacion de mocks.
- Bloqueos externos: Ninguno — la correccion es local al repositorio.
- Accion requerida antes de continuar: Actualizar los mocks y re-ejecutar `npx tsc --noEmit`.

## Decision

- [ ] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [ ] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [x] QA revalido y cerro el finding (`RESOLVED`).

**Estado post-revalidacion: RESOLVED** — Confirmado con evidencia fresca: 17/17 tests frontend pasan (6 suites), no hay errores de TypeScript en archivos de slice-006. Los mocks fueron actualizados correctamente con create/update/fetchOne.

---

## Politica UTF-8

- El finding conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
