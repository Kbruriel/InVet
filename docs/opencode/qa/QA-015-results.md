# QA-015 - Resultados de validaci[oó]n del slice BE-015 (reportes agregados)

## Resumen ejecutivo

Se validó contra **PostgreSQL real** (en el contenedor QA `invet-backend-qa015`,
puerto `8215`) el slice BE-015 de reportes agregados: 6 endpoints
read-only bajo `/api/v1/reports/*`. Se verificaron las tres áreas del
checklist QA: agregación happy path, paginación determinista y
autenticación/BOLA. Se detectó y corrigió un defecto real de **paginación
no determinista** (overlap/missing rows entre páginas) en los 5
use-cases paginados.

- decision: `APPROVED`
- resultado de validaci[oó]n: `APPROVED`

## Entorno de ejecución

| Componente | Detalle |
|---|---|
| DB | PostgreSQL 16 (`invet-db`), compartido a través de la red de compose |
| Backend QA | `invet-backend-qa015`, code montado `:ro`, puerto `8215`, `healthy` |
| Token | JWT owner `clinic_id=1`, emitido dentro del contenedor (`/tmp/qa015_tok2.txt`) |
| Script | `qa_scripts/qa015_verify.py` (copiado a `/tmp/qa015v2.py`) |
| Salida JSON | `qa_scripts/qa015_results.json` |

## Evidencia

### T01 - Happy path / agregaciones (`pass: true`, 8/8)

| Check | Status | Evidencia |
|---|---|---|
| appointments_global_200 | 200 | `total=12`, `items_returned=5` |
| appointments_period | 200 | `total=12` |
| appointments_period_2020 | 200 | `total_2020=0` (periodo sin datos) |
| services_global | 200 | `total=18` |
| pets_count | 200 | `clinic_id=1`, `active_count=3` |
| consultations_global | 200 | `total=3` |
| ratings_avg | 200 | `clinic_avg=4.11`, `n_veterinarians=1` |
| payments_global | 200 | `total=202`, `total_amount=1250.0` |

### T02 - Paginación determinista (`pass: true`, 6/6)

| Check | Status | Evidencia |
|---|---|---|
| appointments_p1p2 | 200/200 | `overlap=0`, `n_p1=5`, `n_p2=5` |
| appointments_size_limits | 200 | `size=100→12`, `size=1→1` |
| appointments_invalid_size | 422 | `size=0/101/page=0 → 422` |
| services_p1p2 | 200 | `n_p1=10`, `n_p2=8`, `union=18` (cobertura completa) |
| consultations_p1p2 | 200 | `n_p1=2`, `n_p2=1`, `total=3` |
| payments_disjoint | 200/200/200 | `pages=1..3`, `disjoint=true`, `total=202` |

### T03 - Autenticación / BOLA / validaciones (`pass: true`, 6/6)

| Check | Status | Evidencia |
|---|---|---|
| no_token | 401 | `Not authenticated` en todos los endpoints |
| bad_tokens | 401/401 | token basura y bare rechazados |
| bola_clinic_id_query | 200 (ignored) | `clinic_id=999` en query no amplía el alcance; el alcance proviene de `clinic_id` del JWT |
| bola_pets_faked | 200 (ignored) | `/pets?clinic_id=999` no devuelve datos ajenos |
| dates_validation | 422/422/422/200 | fecha inválida, mes inválido y rango incoherente → 422; rango válido → 200 |

## Defectos detectados y corregidos

- **Paginación no determinista (bloqueo resuelto).** Los 5 use-cases
  paginados (`report_appointments`, `report_services`,
  `report_consultations`, `report_payments`, `report_ratings_summary`)
  ordenaban por una única columna (`scheduled_start`, `name`, `updated_at`,
  `paid_at`, `created_at`) **sin tiebreaker**. Con datos que comparten el
  mismo valor de esa columna, PostgreSQL devolvía un orden arbitrario entre
  peticiones, produciendo **overlap** y **rows ausentes** entre páginas
  (T02 `appointments_p1p2` falló en la primera ejecución). Corregido añadiendo
  `id` como segundo criterio de ordenación en cada use-case. Ver detalles en
  `QA-015-findings.md`.

## Regresiones

- Suite unitaria reports: `56 passed`.
- Suite global: `627 passed, 1 skipped`. Los 3 fallos observados
  (`test_agentic_plan_schema_v3`, `test_automation_agentic_flow`,
  `test_vscode_agent_controls`) son **preexistentes y ajenos a BE-015**
  (infraestructura de agente/planning), no reportes; no alteran este slice.
- Gate `--stage secure-persistence` → **PASS** post-corrección.

## Mapeo de cierre del checklist QA

| Tarea | Evidencia verificable | Resultado |
|---|---|---|
| QA-015-T01 | 8/8 checks happy path contra PG real (T01 `pass:true`) | PASS |
| QA-015-T02 | 6/6 checks paginación, overlap=0, cobertura completa (T02 `pass:true`) | PASS |
| QA-015-T03 | 6/6 checks auth/BOLA/validaciones, 401/422 correctos (T03 `pass:true`) | PASS |

Los 3 fallos del primer arranque de T02 y el key-mismatch de T03 se corrigieron
(defecto backend + script) y se re-ejecutó el script hasta `ok:true` completo.

## Comentarios finales

El slice BE-015 quedó validado contra base real de datos. El único defecto
bloqueante (paginación no determinista) se corrigió en los 5 use-cases con
tiebreaker por `id` y se protegió con 5 tests de regresión que asercionan el
orden `(columna, id)`. Todos los criterios QA del manifiesto quedaron
cumplidos; se emite **decision: `APPROVED`**.
