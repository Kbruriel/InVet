# Gobernanza de carryovers

Este documento define como InVet maneja tareas postergadas de forma justificada y tareas que pasan de un slice a otro sin perder evidencia.

## Objetivo

Evitar que una tarea quede pendiente sin ruta de cierre; que un slice cierre trabajo heredado sin rastreo, o que el plan original y el plan destino queden desincronizados.

## Registro canonico

Cuando una tarea se posterga con justificacion valida, el agente responsable debe crear o actualizar un registro por slice en:

- `docs/opencode/carryovers/BE-00X-carryovers.md`

Si el archivo no existe, debe crearse al primer carryover del slice.

## Campos minimos del registro

- `source_plan`
- `source_task`
- `destination_plan`
- `destination_task`
- `reason_postponed`
- `status`
- `owner`
- `updated_at`
- `closure_evidence`
- `source_reference`
- `destination_reference`

## Estados permitidos

- `OPEN`: la tarea sigue pendiente en su plan origen.
- `TRANSFERRED`: la tarea paso al plan destino y aun no tiene cierre completo.
- `CLOSED`: el plan origen y el plan destino reflejan la misma evidencia de cierre.
- `CANCELLED`: la tarea ya no aplica y quedo justificada con evidencia.

## Reglas operativas

- El planner debe leer este registro antes de generar o reparar un `BE-00X-plan.md`.
- Si una tarea se posterga por una razon justificada, el agente que detecto la postergacion debe registrar el motivo y el enlace al plan origen antes de cerrar su trabajo.
- Si una tarea proviene de otro slice, el plan destino debe conservar el enlace al plan origen y el plan origen debe quedar actualizado con la misma evidencia o con una referencia explicita al cierre.
- Una tarea transferida no se considera cerrada hasta que el plan actual, el plan original y el registro de carryover coinciden.
- QA, reviewers, docs y final gate deben tratar carryovers abiertos o desalineados como bloqueo.
- Un carryover nunca debe ocultarse como `pending` anonimo; debe dejar rastro del origen y del destino.
- Si el plan destino completa el trabajo, el agente responsable debe cerrar tambien la traza del plan origen.
- Si la tarea queda postergada de nuevo, se actualiza el mismo registro; no se crean carryovers paralelos sin justificacion.

## Criterio de cierre

El carryover queda realmente cerrado solo cuando:

1. El plan destino muestra la tarea con evidencia reproducible.
2. El plan origen refleja el mismo cierre, la misma decision o una referencia explicita al resultado.
3. El registro de carryover queda en `CLOSED` o `CANCELLED`.

## Plantilla y validacion

- Plantilla canonica: `docs/opencode/templates/carryovers_registry_template.md`.
- El validador `backend/scripts/validate_slice_plan.py` bloquea `qa`, `review`, `checks` y `docs` cuando el registro contiene estados `OPEN` o `TRANSFERRED`.
- Si un plan menciona una tarea heredada o postergada y el registro no existe, el preflight del plan falla hasta crear el archivo canonico.
