# BE-005 — Correcciones Checklist Clean Architecture

## Resumen breve
Se aplicaron 4 correcciones a la revisión de clean architecture enfocadas en: inyección de interfaces (M1), eliminación de código residual sin tracking git (M2), transacciones acotadas con rollback (O3), y documentación del criterio `_clean_payload` (O6). Sin cambios ampliadores fuera del slice.

## Correcciones realizadas

1. **M1 — Inyección de dependencias via factory helper**
   - Antes: `dependencies.py` importaba `ClinicRepositoryImpl`, `BranchRepositoryImpl` etc. directamente (`from app.infrastructure.repositories.clinic_repository_impl import BranchRepositoryImpl, ...`) e instanciaba las concretas en cada función dependencia (llíneas 54-68).
   - Despues: Se crearon funciones `_make_*_repo()` privadas que encapsulan la instanciación de concretos. El módulo expone solo interfaces abstractas (`BranchRepository`, `ClinicRepository`, etc.) y los routers nunca ven clases concretas. FastAPI sigue funcionando porque `Depends` es agnóstico al tipo. La importación de concretos se hace *lazy* dentro de cada helper, rompiendo el ciclo dependiente en la capa superior.
   - Archivos tocados: `backend/app/api/dependencies.py`

2. **M2 — Eliminación del directorio `/app/` residual (sin tracking git)**
   - Antes: Existía un directorio `\app\` en la raíz del repositorio (`C:\InVet\app\`) sin tracking git con routers, use-cases y modelos duplicados que importaban desde `app.core.security` rompiendo Clean Architecture.
   - Despues: Se eliminó completamente el directorio `C:\InVet\app\` y todos sus archivos (17 entries). El proyecto queda limpio de código sin seguimiento.
   - Archivos tocados: Eliminación total de `\app\**` en raíz del repositorio

3. **O3 — Transacciones no acotadas con rollback explícito**
   - Antes: Múltiples métodos `commit()` inline sin control de errores (en `clinic_repository_impl.py`). En caso de excepción, la session quedaba en estado inconsistente.
   - Despues: Se envolvió todo `commit()` en `try/except` con `rollback()` en el except para los siguientes métodos: `create_clinic`, `update_clinic`, `deactivate_clinic`, `create_branch`, `update_branch`, `deactivate_branch`, `create_schedule`, `update_schedule`, `delete_schedule`.
   - Archivos tocados: `backend/app/infrastructure/repositories/clinic_repository_impl.py`

4. **O6 — Documentación de `_clean_payload`**
   - Antes: Función `_clean_payload` sin docstring que explicara por qué filtra valores None.
   - Despues: Se añadió docstring extenso documentando la regla de negocio (semántica partial-update), la razón técnica (Pydantic exclude_unset produce keys con valor None), y por qué reside en la capa use-case (escuda infraestructura de artefactos de serialización HTTP).
   - Archivos tocados: `backend/app/application/use_cases/clinic_use_case.py`

## Hallazgos no corregidos (y por qué)
- Ninguno — los 4 hallazgos fueron completamente cerrados.

## Archivos modificados

| Archivo | Acción |
|---------|--------|
| `backend/app/api/dependencies.py` | Modificado: reemplazo de importaciones concretas por factory helper |
| `backend/app/application/use_cases/clinic_use_case.py` | Modificado: documentación extensa de `_clean_payload` |
| `backend/app/infrastructure/repositories/clinic_repository_impl.py` | Modificado: try/rollback en 9 métodos write |
| `\app\**` (raíz repositorio) | Eliminación total de directorio no versionado |

## Validaciones ejecutadas

- [x] Verificación de sintaxis Python con `python -m py_compile` en todos los archivos modificados.
- [x] Ejecución de `pytest backend/app/tests/` — tests de use-cases y API pasando correctamente (los tests mockan dependencias por lo que las firmas abstractas son compatibles).

## Documentación actualizada

- Docstring de `_clean_payload` documenta el criterio de negocio (O6 cerrado).
- Este archivo BE-005-corrections.md documenta todas las acciones.

## Pendientes o riesgos residuales

- Riesgo mínimo introducido por los bloques `try/except` en repositorios: cualquier llamada existente que *espere* una excepción concreta debe seguir recibéndola (solo se añade rollback antes de re-lanzar, sin cambio de semántica).
- Las pruebas unitarias usan mocks y no tocan la infraestructura real con DB, por lo que el rollback es validado sintácticamente pero no ejecutado sobre datos reales. En producción se valida con pytest-integration o tests de integración.

## Cierre

- [x] M1 cerrado — interfaces abstractas en dependencias.
- [x] M2 cerrado — directorio residual eliminado.
- [x] O3 cerrado — rollback explícito en todas las operaciones write.
- [x] O6 cerrado — documentación de criterio `_clean_payload`.
- [x] Sin alcance ampliado fuera del slice BE-005.
