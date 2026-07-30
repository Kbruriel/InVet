# 01 - Runbook de comandos secuenciales

## Secuencia obligatoria

```text
/plan-task BE-001
/implement-backend-task BE-001
/implement-frontend-task FE-001
/qa-task QA-001
/review-slice BE-001
/review-slice FE-001
/implement-findings BE-001
/implement-findings FE-001
/clean-architecture-review
/security-review
/run-checks
/update-docs
```

## Reglas

1. `plan-task` siempre recibe un ID backend `BE-00X`.
   Si el usuario envia `FE-00X` o `QA-00X`, el flujo correcto es redirigirlo a `/implement-frontend-task FE-00X` o `/qa-task QA-00X`; `plan-task` no debe remapear silenciosamente el argumento.
2. `plan-task` genera `docs/opencode/plans/BE-00X-plan.md` con checklist numerado, objetivos, criterios de aceptacion y `Paralelismo[P]`.
   Nunca implementa codigo de backend ni frontend.
3. `implement-backend-task` implementa solo tareas backend pendientes del plan y marca `- [x]` cuando los criterios quedaron verificados.
4. `implement-frontend-task` recibe el ID frontend equivalente `FE-00X`, implementa solo tareas frontend pendientes del plan y marca `- [x]` cuando los criterios quedaron verificados.
5. `qa-task` recibe el ID QA equivalente `QA-00X`, valida usando objetivos y criterios del plan, y marca tareas QA o de validacion completadas.
6. `qa-task` documenta evidencia y, si no puede ejecutar pruebas por ambiente/configuracion, genera `docs/opencode/qa/QA-00X-findings.md`.
7. `review-slice` acepta `BE-00X` o `FE-00X`, revisa el plan y la implementacion del mismo slice vertical y deja hallazgos en Markdown si los hay.
8. `implement-findings` acepta `BE-00X` o `FE-00X`, toma el reporte de hallazgos, el archivo de bloqueo de QA o los archivos de review del slice y cierra correcciones sobre el mismo slice vertical.
9. Las revisiones globales se ejecutan despues de QA.
10. `run-checks` debe ejecutarse antes de `update-docs`.
11. `update-docs` cierra el slice.

## Ejemplo: busqueda publica

```text
/plan-task BE-003
/implement-backend-task BE-003
/implement-frontend-task FE-003
/qa-task QA-003
/review-slice BE-003
/review-slice FE-003
/implement-findings BE-003
/implement-findings FE-003
/clean-architecture-review
/security-review
/run-checks
/update-docs
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
