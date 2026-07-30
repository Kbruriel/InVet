---
description: Implementa una tarea frontend InVet, por ejemplo FE-001.
agent: invet-frontend-implementer
---

Implementa la tarea frontend indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de alcance/UX o se requiere una accion destructiva.
1. Normaliza el argumento a `FE-00X` e identifica el backend equivalente `BE-00X`.
2. Identifica el plan generado por `/plan-task`: `docs/opencode/plans/BE-00X-plan.md`.
3. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
4. Si el slice requiere base tecnica frontend y aun no existe `frontend/package.json`, inicializa primero la base ejecutable del workspace antes de implementar UI de producto.
   - Esto aplica especialmente a `FE-001`: debes dejar Next.js + TypeScript + Tailwind local, scripts `lint`, `typecheck`, `test`, `build`, estructura `src/` y al menos una prueba automatizada verificable.
5. Selecciona solo tareas pendientes `- [ ]` del plan que correspondan a frontend, UI, rutas, componentes, cliente API, validacion cliente, estados UX o pruebas frontend.
6. Respeta `Paralelismo[P]`: si una tarea marca `No`, verifica que sus dependencias previas esten completas antes de implementarla.
7. Implementa cada tarea usando su `Objetivo` y `Criterios de aceptacion` como contrato de alcance.
8. Usa Next.js, TypeScript, React y Tailwind local.
9. Aplica tokens y lineamientos de `docs/opencode/references/frontend_visual_alignment.md`.
10. Implementa estados loading/error/empty/success cuando apliquen.
11. Centraliza consumo API en `src/shared/api`.
12. No agregues checkout, productos, marketplace, inventario ni facturacion.
13. Marca como completadas en `docs/opencode/plans/BE-00X-plan.md` solo las tareas frontend cuyos criterios de aceptacion quedaron verificados, cambiando `- [ ]` por `- [x]`.
14. Si una tarea no se puede completar, dejala como `- [ ]` y documenta el bloqueo debajo de la tarea o en el resumen final.
15. Resume tareas completadas, rutas, componentes, contratos y pruebas ejecutadas.
