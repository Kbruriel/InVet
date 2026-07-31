# 01 - Runbook de comandos secuenciales

## Secuencia obligatoria

La forma recomendada es:

```text
/execute-slice BE-001
```

La secuencia manual equivalente es:

```text
/plan-task BE-001
/implement-backend-task BE-001
/implement-frontend-task FE-001
/qa-task QA-001
/review-slice BE-001
/clean-architecture-review BE-001
/security-review BE-001
/implement-findings BE-001
/qa-task QA-001
/run-checks BE-001
/update-docs BE-001
```

## Reglas

1. `plan-task` acepta `BE-00X`, `FE-00X` o `QA-00X`, informa la normalizacion y conserva el mismo indice vertical.
2. `plan-task` genera un unico `docs/opencode/plans/BE-00X-plan.md` schema v2 con contrato frontend y tareas atomicas.
   Nunca implementa codigo de backend ni frontend.
3. Cada comando mutable ejecuta `backend/scripts/validate_slice_plan.py` antes de editar.
4. Backend y frontend implementan sus pruebas unitarias y registran evidencia por tarea.
5. `qa-task` recibe el ID QA equivalente `QA-00X`, valida usando objetivos y criterios del plan, y marca tareas QA o de validacion completadas.
6. `qa-task` documenta evidencia, rechaza gaps unitarios y no repara pruebas unitarias de producto.
7. `review-slice` acepta `BE-00X` o `FE-00X` y siempre deja `docs/opencode/reviews/BE-00X-review.md` con decision.
8. `clean-architecture-review BE-00X` siempre deja `docs/opencode/reviews/BE-00X-clean-architecture-review.md`.
9. `security-review BE-00X` siempre deja `docs/opencode/reviews/BE-00X-security-review.md`.
10. `implement-findings` acepta `BE-00X` o `FE-00X`, toma el reporte de hallazgos, el archivo de bloqueo de QA o los archivos de review del slice y cierra correcciones sobre el mismo slice vertical.
11. `/implement-findings` deja findings QA en `READY_FOR_REVALIDATION`; QA es el unico que puede declarar `RESOLVED`.
12. Las revisiones reciben un ID explicito y siempre escriben decision `APPROVED|REJECTED`.
13. `run-checks BE-00X` deja evidencia Markdown antes de `update-docs BE-00X`.

## Ejemplo: busqueda publica

```text
/plan-task BE-003
/implement-backend-task BE-003
/implement-frontend-task FE-003
/qa-task QA-003
/review-slice BE-003
/implement-findings BE-003
/qa-task QA-003
/clean-architecture-review BE-003
/security-review BE-003
/run-checks BE-003
/update-docs BE-003
```

## Resultado esperado por slice

- Plan de implementacion generado en `docs/opencode/plans/BE-00X-plan.md`.
- Codigo backend implementado o explicitamente no requerido.
- Codigo frontend implementado o explicitamente no requerido.
- Checklist del plan actualizado con tareas completadas verificadas.
- QA ejecutado con evidencia trazada por tarea.
- Hallazgos revisados o cerrados si aplicaba.
- Revision arquitectura aprobada.
- Revision seguridad aprobada.
- Checks verdes o fallos documentados.
- Documentacion actualizada.
