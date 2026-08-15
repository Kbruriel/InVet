# Carryovers de BE-006

Este registro documenta el trabajo heredado del slice BE-005 que quedo cerrado dentro del slice BE-006. Se mantiene separado para que QA, reviews, docs y futuras planificaciones no traten como abierto el trabajo ya resuelto.

## Registro

| source_plan | source_task | destination_plan | destination_task | reason_postponed | status | owner | updated_at | closure_evidence | source_reference | destination_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| docs/opencode/plans/BE-005-plan.md | SEC-005-M01 | docs/opencode/plans/BE-006-plan.md | BE-006 | BE-005 dejo pendiente la transicion a access/refresh tokens con expiracion; BE-006 la cerro con refresh tokens rotativos y verificacion de tipo. | CLOSED | security | 2026-08-15 | docs/opencode/reviews/BE-006-security-review.md#L145-L151 | docs/opencode/reviews/BE-005-security-review.md#L146-L150 | docs/opencode/reviews/BE-006-security-review.md#L145-L151 |

## Criterio de cierre

El carryover se considera cerrado cuando el plan destino y la security review de BE-006 documentan la misma politica de tokens con expiracion y refresh rotativo, y el plan origen conserva la referencia a la continuidad.
