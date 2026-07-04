---
description: Implementa hallazgos de revision y documenta el cierre de correcciones.
agent: invet-findings-implementer
---

Implementa los hallazgos indicados por `$ARGUMENTS`.

Instrucciones:
1. Acepta un indice `BE-00X` o la ruta de un archivo de hallazgos.
2. Lee `docs/opencode/reviews/BE-00X-review.md` y las tareas relacionadas.
3. Corrige la implementacion necesaria en backend, frontend o QA.
4. Documenta el cierre en `docs/opencode/reviews/BE-00X-corrections.md` siguiendo `docs/opencode/templates/corrections_checklist_template.md`.
5. Incluye un checklist de correcciones completadas.
6. Reejecuta checks relevantes si estan disponibles.
7. No amplie el alcance fuera del slice ni inventes funcionalidad nueva.
