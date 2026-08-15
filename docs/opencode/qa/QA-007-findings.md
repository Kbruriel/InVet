# QA-007 Findings - Propietarios y mascotas

## Estado global del archivo

- Estado global: `RESOLVED` (todos los findings del slice fueron revalidados y cerrados).

## Hallazgos resueltos

### Finding QA-007-F01 (severidad: critical, estado: RESOLVED)

- **Criterio(s) afectado(s):** AC-007-01, AC-007-02
- **Descripcion original:** POST /api/v1/owners devolvia 422 en vez de 201 con payload valido. PUT /api/v1/owners/me tambien respondia 422 al actualizar datos validos.
- **Estado actual:** RESOLVED - El producto corrige ambos endpoints para devolver status codes correctos (201 y 200 respectivamente).
- **Evidencia de resolucion:** Backend integration tests `test_create_owner_profile_returns_created_owner` y `test_update_own_profile_success` ahora pasan. Fresh pytest: 10 passed, 0 failed.

### Finding QA-007-F02 (severidad: major, estado: RESOLVED)

- **Criterio(s) afectado(s):** AC-007-06
- **Descripcion original:** Tras DELETE exitoso de una mascota, un GET subsecuente al mismo pet_id retorna 200 en vez de 404.
- **Estado actual:** RESOLVED - El delete ahora marca correctamente el recurso como inexistente (hard delete o soft-delete con filtro activo).
- **Evidencia de resolucion:** Test `test_create_pet_update_and_delete_flow` pasa con `assert get_after_delete_response.status_code == 404`. Fresh pytest: 10 passed, 0 failed.

### Finding QA-007-F03 (severidad: major, estado: RESOLVED)

- **Criterio(s) afectado(s):** AC-007-15
- **Descripcion original:** El query param `page_size` en GET /api/v1/owners/me/pets es ignorado por la implementacion. Siempre devuelve meta.page_size=20 (valor default).
- **Estado actual:** RESOLVED - El endpoint respeta correctamente el parametro page_size solicitado.
- **Evidencia de resolucion:** Test `test_list_my_pets_paginates_results` pasa con `assert data["meta"]["page_size"] == 5`. Fresh pytest: 10 passed, 0 failed.
### Finding QA-007-F04 (severidad: major, estado: RESOLVED, tipo: gap de cobertura)

- **Criterio(s) afectado(s):** Gate unitario frontend para archivos productivos del slice.
- **Descripcion:** Los archivos `frontend/src/shared/api/owner-portal.ts` y `frontend/src/features/owners/hooks/use-pets.ts` son parte del entregable funcional del slice 007 y anteriormente carecian de pruebas unitarias; se adicionaron pruebas y se validó su correcto funcionamiento.
- **Impacto:** El gate unitario FE exige que TODOS los archivos productivos nuevos o modificados del slice tengan pruebas unitarias explicitas. La ausencia previa generaba un gap de cobertura que ahora fue mitigado.
- **Evidencia:** 
  - `frontend/src/shared/api/owner-portal.test.ts` agregado y ejecutado con éxito (mocked fetch)
  - `frontend/src/features/owners/hooks/use-pets.test.tsx` actualizado y ejecutado; el test previamente fallido fue corregido y pasa
  - `pytest app/tests/api/test_owners_pets.py` → 10 passed (c:\temp\be007_junit.xml)
  - Correcciones documentadas en `docs/opencode/reviews/BE-007-corrections.md`
- **Correccion aplicada:** Se agregaron tests unitarios y se removieron logs de diagnostico temporales; se re-ejecutaron las suites relevantes y QA revalidó el cierre.

### Finding QA-007-F05 (severidad: major, estado: RESOLVED, tipo: flakiness de suite)

- **Criterio(s) afectado(s):** Gate unitario FE para el slice 007.
- **Descripcion:** La suite `frontend/src/features/owners/hooks/use-pets.test.tsx` quedaba sensible al contexto por un mock sobrante que contaminaba `editPet > deberia actualizar el pet en la lista` cuando corria la bateria completa.
- **Impacto:** El gate unitario FE quedaba bloqueado hasta estabilizar la prueba y validar que el fix no rompia la suite completa.
- **Evidencia:**
  - `npm run test -- --runInBand --no-cache src/features/owners/hooks/use-pets.test.tsx` -> PASS (27 tests)
  - `npm run test -- --runInBand --no-cache` -> PASS (25 suites, 138 tests)
  - `python backend/scripts/validate_slice_plan.py QA-007 --stage qa` -> PASS
  - El fix removio el mock sobrante en `addPet` y sincronizo mejor las esperas en el test de `editPet`
- **Estado actual:** RESOLVED. QA revalido la correccion y cerro el finding.

## Verificacion Docker

- Docker Compose disponible: No
- Contenedores aplicables actualizados o recreados: No aplica; la corrida de revalidacion se ejecuto sin Docker
- Estado saludable verificado: No aplica
- Skip justificado, si aplica: Docker no estuvo disponible en esta corrida local


## Decision sobre nuevas tareas

No quedan hallazgos abiertos ni pendientes de revalidacion en el slice 007.

**Hallazgos abiertos pendientes:** ninguno.

**Siguiente paso recomendado:** `/review-slice BE-007`

## Historial de estados de findings

| Finding | Fecha creacion | Estado | Resuelto por |
|---|---|---|---|
| QA-007-F01 | 2026-08-11 | RESOLVED | Bug fix en codigo del producto (POST/PUT owners) |
| QA-007-F02 | 2026-08-11 | RESOLVED | Bug fix en codigo del producto (pet delete + soft-filter) |
| QA-007-F03 | 2026-08-11 | RESOLVED | Bug fix en codigo del producto (page_size query param) |
| QA-007-F04 | 2026-08-11 | RESOLVED | Archivos de test creados y correcciones aplicadas; QA revalido el cierre |
| QA-007-F05 | 2026-08-13 | RESOLVED | Mock sobrante en `use-pets.test.tsx` estabilizado; QA revalido el cierre |

---
Fin de QA-007-findings.md.
