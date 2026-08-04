---
encoding: UTF-8
artifact: qa_results
---

# QA-00X Results

## Metadata

- commit:
- branch:
- timestamp:
- ambiente:
- versiones relevantes:

## Alcance

- alcance:
- fuera de alcance:

## Matriz de trazabilidad

| criterio | riesgo | caso de prueba | nivel | suite o archivo | comando | resultado | evidencia | estado |
|---|---|---|---|---|---|---|---|---|
| AC-001 | riesgo principal | caso principal | integration | backend/app/tests/... | python -m pytest ... | pass | ruta o reporte | PASS |

La matriz debe incorporar `Historia o criterio`, `Contexto necesario`, `Contratos usados` y `Resultado esperado` cuando provengan del plan schema v3.

## Criterios y estados

- `PASS`:
- `FAIL`:
- `BLOCKED`:
- `NOT_APPLICABLE`:

## Comandos ejecutados

```text
python -m pytest ...
python -m ruff check .
python -m black --check .
python -m mypy app
```

## Codigos de salida

- suite:
- codigo:
- reporte:

## Resumen por nivel de prueba

- unit:
- integration:
- contract:
- end-to-end:
- regression:
- security:
- frontend:
- models-and-data:

## Cobertura

- cobertura global:
- cobertura de archivos modificados:
- thresholds existentes:
- disminuciones detectadas:

## Gate de pruebas unitarias

- archivos backend sin pruebas unitarias:
- archivos frontend sin pruebas unitarias:
- hallazgo documentado en:
- accion requerida antes de continuar:

## Comparacion contra baseline

- baseline usada:
- fallos preexistentes:
- regresiones nuevas:
- fallos de ambiente:
- flakiness:

## Pruebas omitidas y bloqueos

- omitidas:
- bloqueos:
- riesgos residuales:

## Defects

- identificador:
- severidad:
- criterio afectado:
- evidencia:

## Decision final

- decision: `APPROVED|REJECTED|BLOCKED`
- justificacion:
- continuar con nuevas tareas: `SI|NO`

## Política UTF-8

- Resultados, hallazgos y outcomes conservan UTF-8.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
