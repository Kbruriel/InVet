---
description: Implementa una tarea frontend InVet, por ejemplo FE-001.
agent: invet-frontend-implementer
---

Implementa la tarea frontend indicada por `$ARGUMENTS`.

Instrucciones:
1. Normaliza el argumento a `FE-00X`.
2. Lee `docs/opencode/tasks/frontend/FE-00X.md`.
3. Lee la tarea backend equivalente `docs/opencode/tasks/backend/BE-00X.md` para contrato API.
4. Implementa solo el alcance del slice.
5. Usa Next.js, TypeScript, React y Tailwind local.
6. Aplica tokens y lineamientos de `docs/opencode/references/frontend_visual_alignment.md`.
7. Implementa estados loading/error/empty/success.
8. Centraliza consumo API en `src/shared/api`.
9. No agregues checkout, productos, marketplace, inventario ni facturación.
10. Resume rutas, componentes, contratos y pruebas.
