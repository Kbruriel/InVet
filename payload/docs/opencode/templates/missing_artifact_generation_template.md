# Solicitud para generar artefactos faltantes

Usa esta plantilla cuando un gate falle porque falta un artefacto canonico y existe contexto parcial en `payload/` o en archivos legacy.

## Entrada

| Campo | Valor |
| --- | --- |
| Slice solicitado | `BE-00X` |
| Artefacto faltante | `docs/opencode/plans/BE-00X-plan.md` |
| Gate fallido | `plan` |
| Backup disponible | `payload/docs/opencode/plans/BE-00X-plan.md` |
| Schema requerido | `3` |
| Schema del backup | `2` |

## Instrucciones para el agente

1. Normaliza el slice solicitado a `BE-00X`, `FE-00X` y `QA-00X`.
2. Lee `docs/opencode/references/missing_artifact_generation.md`.
3. Lee `backend/scripts/validate_slice_plan.py` para confirmar el contrato activo.
4. Lee `docs/opencode/templates/slice_plan_template.md`.
5. Lee la matriz BE/FE/QA, las tres tareas del slice y `slice_task_context.md`.
6. Lee el backup legacy solo como fuente historica.
7. Genera el archivo faltante en la ruta canonica activa.
8. Mantén o restaura `- [x]` solo cuando exista evidencia reproducible.
9. No crees reportes aprobados de QA, reviews o checks sin ejecutar su gate.
10. Ejecuta el validador del gate fallido y corrige hasta `PASS`.

## Checklist de salida

- [ ] Ruta canonica creada o corregida.
- [ ] Frontmatter schema v3 presente.
- [ ] Secciones obligatorias presentes.
- [ ] Tareas BE/FE/QA atomicas presentes.
- [ ] Evidencia completada solo cuando es verificable.
- [ ] Mojibake ausente.
- [ ] `python backend/scripts/validate_slice_plan.py BE-00X --stage plan` termina en `PASS`.
- [ ] Resumen final incluye fuentes usadas y decisiones de migracion.

## Prompt reusable

```text
Regenera el artefacto faltante del slice BE-00X.

Fallo actual:
- Gate: plan
- Falta: docs/opencode/plans/BE-00X-plan.md
- Backup legacy: payload/docs/opencode/plans/BE-00X-plan.md
- Backup schema: v2
- Schema requerido: v3

Sigue docs/opencode/references/missing_artifact_generation.md.
Usa docs/opencode/templates/slice_plan_template.md como contrato activo.
Usa el backup solo como contexto historico, no como copia directa.
Lee matriz, tasks BE/FE/QA y slice_task_context.md antes de escribir.
Genera el plan canonico en UTF-8.
Ejecuta python backend/scripts/validate_slice_plan.py BE-00X --stage plan.
Corrige hasta PASS y reporta decisiones de migracion.
```
