# Carryovers de BE-005

Este registro documenta el trabajo que quedo abierto al cierre del slice BE-005. Se mantiene separado para que QA, reviews, docs y futuras planificaciones no traten como cerrado el trabajo aplazado.

## Registro

| source_plan | source_task | destination_plan | destination_task | reason_postponed | status | owner | updated_at | closure_evidence | source_reference | destination_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| docs/opencode/plans/BE-005-plan.md | APIA-005 | docs/opencode/plans/BE-005-plan.md | APIA-005 | La automatizacion API quedo abierta al cierre de QA; los criterios AC-005-05/06/07/08/09/14 permanecen bloqueados hasta completar autenticacion/autorizacion e IDOR/BOLA con evidencia reproducible. | OPEN | APIA | 2026-08-15 | pending | docs/opencode/plans/BE-005-plan.md#L72-L75 | docs/opencode/reviews/BE-005-final-review.md#L89-L92 |
| docs/opencode/plans/BE-005-plan.md | SEC-005-M01 | docs/opencode/plans/BE-006-plan.md | BE-006 | El token en localStorage sin expiracion se transfirio a BE-006 para cerrar la transicion a refresh token y dejar trazabilidad de la correccion en la review final. | TRANSFERRED | security | 2026-08-15 | pending | docs/opencode/reviews/BE-005-security-review.md#L146-L150 | docs/opencode/reviews/BE-006-security-review.md#L145-L151 |

## Criterio de cierre

El carryover se considerara cerrado cuando APIA-005 tenga evidencia reproducible, el plan origen refleje la misma decision y el cierre de QA/reviews deje de mostrar criterios bloqueados.
