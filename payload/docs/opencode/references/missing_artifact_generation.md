# Generacion de artefactos faltantes

## Objetivo

Permitir que un agente reconstruya artefactos canonicos faltantes sin saltarse gates, reutilizando backups de `payload/` solo como fuente legacy y validando siempre contra los contratos activos del repositorio.

## Caso principal: plan canonico ausente

Si falla el gate con un mensaje como:

```text
No existe docs/opencode/plans/BE-00X-plan.md. Ejecuta /plan-task BE-00X.
```

el agente debe generar `docs/opencode/plans/BE-00X-plan.md` en schema v3. Un archivo legacy en `payload/docs/opencode/plans/BE-00X-plan.md` no desbloquea el gate por si mismo: solo sirve como contexto historico.

## Caso secundario: artefactos auxiliares ausentes

Si falta alguno de estos artefactos:

- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`

el comando responsable tambien es `/plan-task BE-00X`. No existen comandos separados para crear solo `US`, `UIA` o `APIA`.

Reglas:

- `US-00X.md` debe derivar historias y criterios `AC-00X-NN` desde matriz, BE, FE, QA y `slice_task_context.md`.
- `UIA-00X.md` debe planear cobertura de navegador desde FE, QA, criterios `AC-00X-NN`, rutas, formularios, estados UX y responsive.
- `APIA-00X.md` debe planear cobertura HTTP desde BE, QA, criterios `AC-00X-NN`, endpoints, authn/authz, payloads, errores e IDOR/BOLA.
- Los artefactos auxiliares nuevos quedan con evidencia pendiente; no deben declarar ejecuciones `PASSED` sin que el gate correspondiente las haya producido.
- Si un artefacto auxiliar existe pero queda desactualizado frente a las fuentes activas, el mismo `/plan-task BE-00X` debe regenerarlo; no se reutiliza evidencia heredada sin revalidacion.
- Si existe un artefacto auxiliar en `payload/`, usarlo solo como contexto historico y no copiar aprobaciones sin evidencia vigente.

## Fuentes obligatorias

Antes de escribir el artefacto faltante, leer:

- `backend/scripts/validate_slice_plan.py`
- `docs/opencode/templates/slice_plan_template.md`
- `docs/opencode/02_be_fe_qa_task_matrix.md`
- `docs/opencode/tasks/backend/BE-00X.md`
- `docs/opencode/tasks/frontend/FE-00X.md`
- `docs/opencode/tasks/qa/QA-00X.md`
- `docs/opencode/tasks/user-stories/US-00X.md`, si existe
- `docs/opencode/tasks/ui-automation/UIA-00X.md`, si existe
- `docs/opencode/tasks/api-automation/APIA-00X.md`, si existe
- `docs/opencode/references/slice_task_context.md`
- `docs/opencode/references/spec_kit_reference_improvements.md`
- `payload/docs/opencode/plans/BE-00X-plan.md`, si existe

Si una fuente canonica falta pero existe en `payload/`, copiar su contenido conceptual al artefacto nuevo solo despues de verificar que no contradice las fuentes activas.

## Reglas de reconstruccion

- El archivo generado debe vivir en la ruta canonica activa, no solo en `payload/`.
- El frontmatter debe declarar `schema_version: 3`, `slice: "00X"`, `canonical_plan: BE-00X`, `status` y `encoding: UTF-8`.
- El plan debe conservar el indice vertical BE/FE/QA del slice.
- El plan debe incluir al menos una tarea backend, una frontend y una QA.
- Toda tarea debe tener una sola capa, un solo tipo y `Responsabilidad unica: Si`.
- Las tareas completadas solo pueden quedar en `- [x]` si tienen evidencia reproducible y vigente.
- Si el backup legacy marca una tarea como completa pero no tiene evidencia suficiente, regenerarla como `- [ ]` con `Evidencia: pending`.
- No copiar mojibake desde backups legacy. Corregir texto roto antes de validar.
- No inventar endpoints, permisos, persistencia ni criterios QA si no aparecen en las fuentes.

## Procedimiento

1. Normalizar el ID recibido a `BE-00X`, `FE-00X` y `QA-00X`.
2. Confirmar que el plan canonico activo falta o no cumple schema v3.
3. Leer la plantilla schema v3 y las fuentes obligatorias.
4. Leer el backup en `payload/` cuando exista y clasificarlo como `legacy`.
5. Construir un plan nuevo desde la plantilla activa, no por copia directa del backup.
6. Migrar objetivo, alcance, fuera de alcance, entidades, endpoints, riesgos y evidencias del backup que sigan siendo validos.
7. Completar las secciones nuevas de schema v3: brief operativo, fuentes de contexto, matriz de trazabilidad, contrato Docker, reportes/findings y politica UTF-8.
8. Dividir tareas legacy compuestas en tareas atomicas con todos los campos obligatorios.
9. Guardar en UTF-8 en `docs/opencode/plans/BE-00X-plan.md`.
10. Ejecutar `python backend/scripts/validate_slice_plan.py BE-00X --stage plan`.
11. Corregir hasta obtener `PASS`.

## Archivos de gate posteriores

Cuando falten reportes de QA, reviews o checks, no fabricarlos como aprobados. El agente responsable debe ejecutar el gate correspondiente y escribir el archivo desde su plantilla:

| Artefacto faltante | Comando/agente responsable | Plantilla |
| --- | --- | --- |
| `docs/opencode/qa/QA-00X-results.md` | `/qa-task QA-00X` | `docs/opencode/templates/qa_results_template.md` |
| `docs/opencode/qa/QA-00X-findings.md` | `/qa-task QA-00X` o review | `docs/opencode/templates/qa_findings_template.md` |
| `docs/opencode/reviews/BE-00X-review.md` | `/review-slice BE-00X` | `docs/opencode/templates/review_findings_template.md` |
| `docs/opencode/reviews/BE-00X-clean-architecture-review.md` | `/clean-architecture-review BE-00X` | `docs/opencode/templates/review_findings_template.md` |
| `docs/opencode/reviews/BE-00X-security-review.md` | `/security-review BE-00X` | `docs/opencode/templates/review_findings_template.md` |
| `docs/opencode/checks/BE-00X-checks.md` | `/run-checks BE-00X` | `docs/opencode/templates/checks_results_template.md` |

La unica excepcion recuperable desde `payload/` es un plan legacy usado como entrada para regenerar el plan schema v3. Las aprobaciones de QA, reviews y checks requieren evidencia nueva o vigente.

## Criterio de cierre

El agente puede declarar el artefacto recuperado solo si:

- El archivo existe en la ruta canonica activa.
- El contenido esta en UTF-8.
- El validador determinista termina en `PASS`.
- El resumen explica que fuentes legacy se usaron y que decisiones de migracion se tomaron.
