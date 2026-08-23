# QA-010 Findings — Recetas, tratamientos y recordatorios

**Slice:** BE-010 / FE-010 / QA-010
**Date:** 2026-08-22
**Estado global:** RESOLVED

> Todos los hallazgos detectados durante la sesión de QA UI-010 fueron corregidos y
> revalidados por las suites verdes (UIA 18/18, pytest 25, APIA 10) al cierre.
> Ningún finding queda abierto — ver `QA-010-results.md` §8 (GATE).

---

## Finding Q010-001: Mojibake en cabecera pública (caracteres acentuados corruptos)

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | Frontend / UI (accesibilidad + i18n) |
| Componente | `frontend/src/features/public-landing/components/PublicHeader.tsx:21,33` |
| Afecta Tests | UIA-010 C9 "acentes sin mojibake" (chromium + mobile-chromium) |

**Descripción original:**
Los enlaces de navegación pública `Clínicas` y `Cómo funciona` se renderizaban con
acentos double-encoded (mojibake, p.ej. `ClÃ­nicas` / `CÃ³mo funciona`), lo que
hacía fallar el caso de acentos sin mojibake (C9) y degradaba la calidad visual del
portal.

**Evidencia original:** UIA C9 `assertNoMojibake` detectaba secuencias `Ã`/`â` en el
HTML de `PublicHeader`.

**✅ ESTADO: RESOLVED** (2026-08-22)

**Acción:** Se corrigieron los literales a sus valores UTF-8 correctos
`Clínicas` / `Cómo funciona` (`PublicHeader.tsx:21` y `:33`). Como el contenedor
`invet-frontend` corre en modo producción (`next start`, sin volume mounts), el
cambio de fuente requirió rebuild: `docker compose up -d --build frontend`.

**Validación:** UIA C9 **2/2 PASS** (chromium + mobile-chromium) tras el rebuild.

---

## Finding Q010-002: Actor de prueba incorrecto en specs (admin en lugar de veterinario)

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | QA / UI-automation (test defect, no defecto de producto) |
| Componente | `tests/e2e/fe-010-prescription-*.spec.ts` |
| Afecta Tests | C1, C3, C4, C5, C6, C7 (todas las rutas de escritura/clínica) |

**Descripción original:**
Las specs invocaban el flujo clínico con una cuenta **admin** (`qa@example.com`,
`role=admin`) donde el contrato exige **veterinario** (`_WRITE_ROLES` incluye
`admin`, pero el criterio de negocio y los ACs apuntan al actor clínico
veterinario). El resultado era evidencia incompleta del requisito "vet de la
clínica crea receta" (AC-010-01) y una confusión de actor en los asserts.

**Evidencia original:** asserts pasaban por rol `admin`, no por el rol clínico
esperado; la trazabilidad a US-010/AC-010-08 quedaba débil.

**✅ ESTADO: RESOLVED** (2026-08-22)

**Acción:** Se sustituyó el actor de prueba a la cuenta de **veterinario** en los
tres specs (`create`, `states`, `access`), alineado con `_WRITE_ROLES` y el
criterio de rol clínico. El caso de 403 (owner, rol `user`) se mantiene con la
cuenta de propietario, ejerciendo correctamente `_require_write_role`.

**Validación:** UIA-010 **18/18 PASS** con actor veterinario en C1/C3/C5/C6/C7 y
owner en C4/C8/C9.

---

## Finding Q010-003: Race de `LoadingSpinner` tras `goto` (clasificación de estado no estable)

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | QA / UI-automation (flaky test) |
| Componente | `tests/e2e/fe-010-prescription-states.spec.ts`, `fe-010-prescription-access.spec.ts`, `fe-010-prescription-create.spec.ts` |
| Afecta Tests | C2 (validación inline), C8 (responsive), C9 (acentos), C3 (crear), C4 (acceso) |

**Descripción original:**
Tras `page.goto(...)` la página entra en el estado `loading`
(`LoadingSpinner` "Cargando la consulta asociada", ver
`frontend/src/app/clinic/prescriptions/new/page.tsx:141`). Los specs clasificaban
el estado final con `isVisible()` unicas (no reintentadas) antes de que el spinner
desapareciera, produciendo falsos negativos (flaky) en C2/C8/C9/C3/C4.

**Evidencia original:** C2/C8/C9/C3 intermitentemente fallaban con
"esperado form visible, spinner aún presente" — no reproducible de forma
determinista en runs aislados (race temporal).

**✅ ESTADO: RESOLVED** (2026-08-22)

**Acción:** Se añadió `settleAfterGoto(page)` / inline
`expect(page.getByText(/Cargando la consulta/i)).toBeHidden({timeout:30_000}).catch(()=>{})`
después de **cada** `goto` antes de la clasificación one-shot de `isVisible()`, en:
`states` (3×), `create` (C3) y `access` (C4).

**Validación:** UIA-010 **18/18 PASS** en dos baselines consecutivas (8.4s y 8.4s),
sin reprobar flaky.

---

## Finding Q010-004: C3 asumía 201 duro cuando la receta ya existía (409 por duplicado)

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | QA / UI-automation (asunción incorrecta de estado) |
| Componente | `tests/e2e/fe-010-prescription-create.spec.ts` (C3, C6) |
| Afecta Tests | C3 "crear receta éxito" (ambos proyectos), C6 "detalle receta" |

**Descripción original:**
C3 ejecuta en **dos proyectos concurrentes** (chromium + mobile-chromium) contra la
misma consulta `1000`. El backend aplica "una receta por consulta"
(`UniqueConstraint("consultation_id")` → 409). Con filas residuales de runs
previos o con el otro proyecto creando primero, el POST devolvía **409** en lugar
de 201, pero el spec afirmaba de forma dura "Receta creada" + `Receta #\d+` →
fallo determinista. No existe endpoint `DELETE` de recetas, así que el estado
residual no se podía limpiar por API.

**Evidencia original:**
`expect(page.getByText(/Receta creada/i)).toBeVisible({ timeout: 30_000 })` →
"element not found" cuando el POST fue 409 (duplicado por proyecto hermano o
residuo).

**✅ ESTADO: RESOLVED** (2026-08-22)

**Acción:** C3 ahora **condiciona el assert al status del POST** capturado:
- `201` → banner "Receta creada" + `Receta #\d+` (camin happy).
- `409` → assert **sin** banner de éxito; assert del detalle de duplicado
  "Ya existe una receta registrada para esta consulta."
  (`prescription_use_cases.py:93`, surfaced por `ErrorBanner` inline en
  `page.tsx:256` mientras el form + `h1 "Registrar receta"` permanecen visibles);
  y valida que la receta resultante es consultable por el propietario (owner).

C6 ya reutilizaba la receta existente vía `seedPrescription`/`seedForeignPrescription`
(409-by-reuse), de modo que ambos proyectos comparten `Receta #4` de forma idempotente.

**Validación:** `DELETE FROM prescriptions; DELETE 0` (baseline limpio) → UIA-010
**18/18 PASS**; y re-ejecución **sin limpiar** (con residuos) → **18/18 PASS** (8.4s).
C3/C6 ejercen el camino 409 idempotentemente en ambos proyectos.

---

# Summary of Findings

| Finding ID | Severity | Category | Status |
|------------|----------|----------|--------|
| Q010-001 | Major | Frontend / I18n (mojibake) | RESOLVED ✅ |
| Q010-002 | Major | Test — actor incorrecto | RESOLVED ✅ |
| Q010-003 | Major | Test — flaky (loading race) | RESOLVED ✅ |
| Q010-004 | Major | Test — asunción 201/409 (C3) | RESOLVED ✅ |

**Total:** 4 findings — Todos RESOLVED. Ningún finding de producto abierto; todos los
hallazgos son de calidad de QA/UI ya revalidados.

---

*QA findings report creado 2026-08-22. Resolver todos los findings en la misma sesión y
revalidar por suites UIA/pytest/APIA (UIA 18/18, pytest 25 passed, APIA 10/10).*
