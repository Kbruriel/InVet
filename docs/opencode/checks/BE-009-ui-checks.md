---
encoding: UTF-8
artifact: ui_checks
slice: BE-009/FE-009/QA-009
review_date: 2026-08-21T00:00:00Z
reviewer: Check Runner (UI checks)
---

# BE-009 UI Checks - Consultas médicas

## Decision final

**APPROVED**

## Preflight

| Validacion | Resultado |
|---|---|
| QA-009 results (QA-009-results.md) | APPROVED |
| UIA-009 sidecar | Presente (docs/opencode/tasks/ui-automation/UIA-009.md) |
| FE-009 / BE-009 implementados | Completados |

## Stack Docker (pre-check)

| Servicio | Puerto | Estado |
|---|---|---|
| db | 5432 | healthy |
| backend (FastAPI) | 8000 | healthy |
| frontend (Next.js) | 3000 | healthy |

Variable: `PLAYWRIGHT_START_FRONTEND=false` (frontend se consume publicado en `http://localhost:3000`).

## Resultados ejecutados

### `npm run test:e2e` (chromium)

```
75 passed / 7 skipped / 0 failed (16.1s)
```

### `npm run test:regression` (chromium)

```
63 passed / 2 skipped / 0 failed (12.5s)
```

### Cobertura del slice 009 (fe-009-consultation.spec.ts)

| Test | US/CA | Resultado |
|---|---|---|
| TC-UIA-009-01 veterinario registra consulta | US-009-01 AC-009-01 | PASS |
| TC-UIA-009-02 bloquea cita no completada | US-009-02 AC-009-02 | PASS |
| TC-UIA-009-03 propietario ve historial | US-009-01 AC-009-03 | PASS |
| TC-UIA-009-04 detalle solo-lectura | US-009-02 AC-009-04 | PASS |
| TC-UIA-009-05 no ve mascotas ajenas | US-009-03 AC-009-05 (negativo) | PASS |

## Correcciones aplicadas fuera de slice (fuera del alcance BE-009, pero necesarias para suite verde)

Durante la ejecucion inicial se detectaron 2 fallos en tests de **otros slices** que bloqueaban la verificacion suite. Se corrigieron para dejar el gate verde y documentar el cambio.

### 1. `InVet_UI_Automation/tests/e2e/slice-006.spec.ts:103` (slice 006)

- **Fallo**: `expect(locator).toBeVisible() failed` en `thead th` con regex `/Duracion|Duration/i`.
- **Causa**: el frontend renderiza `Duración (min)` con acento (`ó`), y la regex `/Duracion|Duration/i` no coincide (comparación byte a byte; la `i` no normaliza acentos).
- **Correccion**: regex cambiada a `/Duraci[óo]n|Duration/i` (`slice-006.spec.ts:103`).
- **Impacto**: slice-006 test `servicios listado con paginacion` ahora pasa.

### 2. `InVet_UI_Automation/tests/e2e/fe-005-deactivate-clinic.spec.ts` (slice 005)

- **Fallo inicial (run 1)**: fallo de suite concurrente (no reproducible en aislamiento).
- **Verificacion**: 5 ejecuciones consecutivas en aislamiento → 5/5 PASS; en la corrida final de `test:e2e` (75 passed / 0 failed) el test pasa.
- **Diagnostico**: flake de aislamiento de estado bajo paralelismo (crea/inactiva clínica con nombre `Date.now()`; no es defecto de producto 005 ni 009).
- **Accion**: no se modifica el producto; el test pasa de forma consistente tras el re-run.

## Decision final

- **UI checks**: APPROVED - los 5 tests de slice 009 pasan en `test:e2e` y `test:regression`; la suite completa queda verde (75/63 passed, 0 failed).
- **Fuera de slice**: 1 fix de regex en `slice-006.spec.ts`; 1 flake en `fe-005` documentado como transitorio (consistente verde en re-run).

## Estado de ejecucion

**Estado de ejecucion: APPROVED**

**Siguiente paso recomendado: `/run-checks BE-009`** (checks tech-formales contra el stack Docker).
