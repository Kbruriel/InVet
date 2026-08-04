---
encoding: UTF-8
artifact: checks_results
---

# Checks tecnicos para slice BE-XXX

## Resumen

- Slice: `BE-XXX`
- Decision: `APPROVED|REJECTED`
- Timestamp:
- Entorno:

## Resultados

| Capa | Check | Comando | Estado | Evidencia |
| --- | --- | --- | --- | --- |
| Backend | tests |  | `PASS|FAIL|SKIPPED` |  |
| Backend | lint |  | `PASS|FAIL|SKIPPED` |  |
| Backend | format |  | `PASS|FAIL|SKIPPED` |  |
| Backend | types |  | `PASS|FAIL|SKIPPED` |  |
| Frontend | test |  | `PASS|FAIL|SKIPPED` |  |
| Frontend | lint |  | `PASS|FAIL|SKIPPED` |  |
| Frontend | typecheck |  | `PASS|FAIL|SKIPPED` |  |
| Frontend | build |  | `PASS|FAIL|SKIPPED` |  |

## Skips

Cada `SKIPPED` debe indicar por que el check no aplica. Un entorno roto no es un skip.

## Fallos

## Decision final

- Decision: `APPROVED|REJECTED`
- Evidencia:

## Politica UTF-8

- Resultados y outcomes conservan UTF-8.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
