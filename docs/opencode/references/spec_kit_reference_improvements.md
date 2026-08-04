# Referencia Spec Kit aplicada a InVet

## Objetivo

Usar `github/spec-kit` como referencia de proceso para que InVet genere tareas mas pequenas, mejor documentadas, con responsabilidad unica y con evidencia consumible por agentes posteriores.

## Observaciones utiles de Spec Kit

- Separa el flujo en fases: principios, especificacion, plan tecnico, tareas, analisis de consistencia e implementacion.
- Trata la documentacion como artefactos ejecutables: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` y `tasks.md`.
- Genera tareas por historia de usuario o incremento independiente, con dependencias y oportunidades de paralelismo.
- Incluye un paso de analisis no destructivo para detectar duplicaciones, ambiguedades, huecos de cobertura e inconsistencias antes de implementar.
- Usa templates, presets y overrides para adaptar el flujo sin cambiar el nucleo.

## Gaps detectados en InVet

| Gap | Riesgo | Mejora introducida |
| --- | --- | --- |
| Planes con contexto disperso | Implementadores interpretan tareas sin saber que fuentes leer | Seccion `Fuentes y artefactos de contexto` |
| Tareas demasiado grandes | Una tarea mezcla contrato, persistencia, API, UI o pruebas | Campos `Tipo`, `Responsabilidad unica`, `Contexto necesario`, `Contratos usados` y `Resultado esperado` |
| Criterios no trazados a tareas | QA descubre huecos tarde | Seccion `Matriz de trazabilidad` |
| Docker documentado de forma parcial | QA o implementacion corren pruebas en entorno no equivalente | Seccion `Contrato de ejecucion Docker y pruebas` |
| Reportes/finding sin contrato previo | Un agente no sabe que archivo consumir o producir | Seccion `Plan de reportes y findings` |
| Encoding no normado | Outcomes con mojibake o redacciones rotas | `encoding: UTF-8`, politica UTF-8 y validacion de mojibake |
| Analisis de gaps dependiente del criterio del agente | Planes incompletos llegan a implementacion | Validador schema v3 con secciones y campos obligatorios |

## Decisiones para InVet

- Mantener un unico plan canonico por slice: `docs/opencode/plans/BE-00X-plan.md`.
- No copiar la estructura completa `specs/[feature]/` de Spec Kit, porque InVet ya organiza trabajo por BE/FE/QA y payload instalable.
- Adoptar los principios practicos: trazabilidad, tareas independientes, contratos explicitos, quickstart tecnico y analisis de gaps.
- Mantener `payload` sincronizado con `.opencode`, `docs/opencode` y `backend/scripts`.
- Usar schema v3 para planes nuevos. Los planes schema v2 pasan a considerarse legacy y deben regenerarse con `/plan-task`.

## Reglas para el planner

- Una tarea debe tener un solo tipo de trabajo.
- Una tarea debe pertenecer a una sola capa.
- Una tarea debe apuntar a un resultado observable.
- Una tarea debe listar contexto y contratos suficientes para que el agente implementador no dependa de memoria conversacional.
- Si el trabajo requiere varios entregables independientes, dividir en tareas consecutivas.
- Si el criterio no se puede validar con comando, prueba o inspeccion reproducible, documentar el gap o preguntar.

## Reglas para implementadores y QA

- Implementadores consumen `Contexto necesario`, `Contratos usados` y `Resultado esperado` antes de editar.
- Implementadores rechazan tareas con `Responsabilidad unica` distinta de `Si`.
- QA valida la matriz de trazabilidad, no solo que existan pruebas.
- QA usa el contrato Docker cuando el criterio requiere PostgreSQL, backend runtime o runtime completo.
- Findings y reportes deben escribirse en UTF-8 y enlazarse desde la evidencia del plan.

## Resultado esperado

El siguiente `/plan-task` debe producir planes schema v3 con tareas mas pequeñas y ejecutables por agentes independientes, reportes previstos antes de la ejecucion y evidencia que cierre los huecos entre plan, implementacion, QA y documentacion.
