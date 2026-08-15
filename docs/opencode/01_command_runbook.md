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
/implement-ui-automation-task FE-001
/implement-api-automation-task BE-001
/qa-task QA-001
/review-slice BE-00X
/clean-architecture-review BE-001
/security-review BE-001
/implement-findings BE-001
/qa-task QA-001
/run-ui-checks FE-001
/run-checks BE-001
/update-docs BE-001
/final-gate BE-001
```

## Reglas

1. `plan-task` acepta `BE-00X`, `FE-00X` o `QA-00X`, informa la normalizacion y conserva el mismo indice vertical.
2. `plan-task` genera un unico `docs/opencode/plans/BE-00X-plan.md` schema v3 con contrato frontend, trazabilidad, Docker, UTF-8 y tareas atomicas.
   Nunca implementa codigo de backend ni frontend.
   Ademas debe crear o actualizar `US-00X`, `UIA-00X` y `APIA-00X`.
3. Cada comando mutable ejecuta `backend/scripts/validate_slice_plan.py` antes de editar.
4. Backend y frontend implementan sus pruebas unitarias y registran evidencia por tarea.
5. `implement-ui-automation-task` recibe el slice frontend equivalente, lee `US-00X` y `UIA-00X`, e implementa E2E en `InVet_UI_Automation/tests/e2e`.
6. `implement-api-automation-task` recibe el slice backend equivalente, lee `US-00X` y `APIA-00X`, e implementa pruebas HTTP en `InVet_UI_Automation/tests/api`.
7. `qa-task` recibe el ID QA equivalente `QA-00X`, valida usando objetivos y criterios del plan, y marca tareas QA o de validacion completadas.
8. `qa-task` documenta evidencia, rechaza gaps unitarios y no repara pruebas unitarias de producto.
9. Si una corrida necesita PostgreSQL, el flujo canonico es levantar `docker compose up -d db` y ejecutar la suite dentro del contenedor de backend con `docker compose run --rm backend pytest ...`; la ejecucion en host solo es fallback documentado cuando Docker no esta disponible. Antes de cerrar QA o checks, confirmar que los contenedores Docker aplicables fueron actualizados o recreados cuando correspondia.
10. `review-slice` acepta `BE-00X` o `FE-00X` y siempre deja `docs/opencode/reviews/BE-00X-review.md` con decision.
11. `clean-architecture-review BE-00X` siempre deja `docs/opencode/reviews/BE-00X-clean-architecture-review.md`.
12. `security-review BE-00X` siempre deja `docs/opencode/reviews/BE-00X-security-review.md`.
13. `run-ui-checks FE-00X` ejecuta `npm run test:e2e` y `npm run test:regression` dentro de `InVet_UI_Automation`.
14. `implement-findings` acepta `BE-00X` o `FE-00X`, toma el reporte de hallazgos, el archivo de bloqueo de QA o los archivos de review del slice y cierra correcciones sobre el mismo slice vertical.
15. `/implement-findings` deja findings QA en `READY_FOR_REVALIDATION`; QA es el unico que puede declarar `RESOLVED`.
16. Las revisiones reciben un ID explicito y siempre escriben decision `APPROVED|REJECTED`.
17. `run-checks BE-00X` deja evidencia Markdown antes de `update-docs BE-00X`.
18. `final-gate BE-00X` deja un reporte final de release cuando se usa una segunda opinion de alta capacidad.
19. Si una tarea se posterga o se transfiere desde otro slice, registrar el carryover en `docs/opencode/carryovers/BE-00X-carryovers.md`, reflejar la misma evidencia en el plan origen y el destino, y validar el registro antes de aprobar `qa`, `review`, `checks` o `docs`.

## Ejemplo: busqueda publica

```text
/plan-task BE-003
/implement-backend-task BE-003
/implement-frontend-task FE-003
/implement-ui-automation-task FE-003
/implement-api-automation-task BE-003
/qa-task QA-003
/review-slice BE-003
/implement-findings BE-003
/qa-task QA-003
/clean-architecture-review BE-003
/security-review BE-003
/run-ui-checks FE-003
/run-checks BE-003
/update-docs BE-003
/final-gate BE-003
```

## Resultado esperado por slice

- Plan de implementacion generado en `docs/opencode/plans/BE-00X-plan.md`.
- Historias `US-00X` y coberturas `UIA-00X` / `APIA-00X` actualizadas.
- Codigo backend implementado o explicitamente no requerido.
- Codigo frontend implementado o explicitamente no requerido.
- Checklist del plan actualizado con tareas completadas verificadas.
- QA ejecutado con evidencia trazada por tarea.
- Hallazgos revisados o cerrados si aplicaba.
- Revision arquitectura aprobada.
- Revision seguridad aprobada.
- Checks verdes o fallos documentados.
- Documentacion actualizada.
- Gate final de release aprobado cuando se active.
