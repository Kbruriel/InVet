---
description: Ejecuta QA funcional y tecnico para una tarea QA InVet, por ejemplo QA-001.
agent: invet-qa-validator
---

Valida la tarea QA indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de aceptacion/alcance o se requiere una accion destructiva.
1. Normaliza el argumento a `QA-00X` e identifica `BE-00X` y `FE-00X`.
2. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
3. Usa los `Objetivo` y `Criterios de aceptacion` de cada tarea del plan para disenar la validacion QA.
4. Verifica que las tareas backend/frontend marcadas como `- [x]` tengan evidencia suficiente contra sus criterios de aceptacion.
5. Disena o ajusta pruebas automatizadas necesarias para cubrir criterios de aceptacion no cubiertos.
6. Ejecuta las pruebas disponibles si el entorno lo permite.
7. Marca como completadas en `docs/opencode/plans/BE-00X-plan.md` solo las tareas QA o de validacion cuyos criterios quedaron verificados, cambiando `- [ ]` por `- [x]`.
8. Documenta trazabilidad por tarea, comandos, resultados esperados vs obtenidos y defectos en `docs/opencode/qa/QA-00X-results.md`.
9. Si existen problemas para ejecutar pruebas o problemas de configuracion del entorno, crea `docs/opencode/qa/QA-00X-findings.md` siguiendo `docs/opencode/templates/qa_findings_template.md` para que luego lo consuma `/implement-findings`.
10. No apruebes si hay blockers de seguridad, arquitectura, criterios de aceptacion incumplidos o datos privados expuestos.
