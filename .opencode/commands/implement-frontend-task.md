---
description: Implementa una tarea frontend InVet, por ejemplo FE-001.
agent: invet-frontend-implementer
---

Implementa la tarea frontend indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta solo si falta informacion bloqueante, hay una decision critica de alcance/UX o se requiere una accion destructiva.
1. Valida el argumento `FE-00X` e identifica `BE-00X` y `QA-00X` del mismo indice.
2. Identifica el plan canonico `docs/opencode/plans/BE-00X-plan.md`.
3. Ejecuta `python backend/scripts/validate_slice_plan.py FE-00X --stage frontend` antes de editar codigo.
   - Si falla, deten la implementacion y reporta cada gap.
   - Si el plan es legacy o incompleto, indica `/plan-task FE-00X`.
4. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
5. Verifica que `Contrato de implementacion frontend` defina rutas, flujos, API, formularios, componentes, accesibilidad y pruebas.
6. Si falta `frontend/package.json` y el slice requiere base tecnica, crea un workspace ejecutable antes de implementar UI.
   - Para `FE-001`, deja Next.js, TypeScript, Tailwind local, scripts `lint`, `typecheck`, `test`, `build`, estructura `src/` y pruebas verificables.
7. Selecciona solo tareas pendientes con `Capa: frontend`.
8. Verifica los IDs de `Depende de`; cada dependencia debe estar `- [x]` y tener evidencia.
   - Si el backend aun no existe, solo continua cuando el plan documente un mock aprobado como entregable.
9. Implementa usando `Objetivo`, `Entregables` y `Criterios de aceptacion` como contrato.
10. Usa Next.js, TypeScript, React y Tailwind local.
11. Aplica `docs/opencode/references/frontend_visual_alignment.md`.
12. Implementa estados loading, submitting, error, empty y success, responsive y accesibilidad segun el contrato.
13. Centraliza el consumo API en `src/shared/api`.
14. Agrega pruebas unitarias o de componente para todo archivo productivo nuevo o modificado y pruebas de integracion cuando el flujo lo requiera.
15. No delegues a QA las pruebas unitarias frontend.
16. No agregues checkout, productos, marketplace, inventario ni facturacion.
17. Marca `- [x]` solo tras ejecutar `Validacion`; reemplaza `Evidencia: pending` con archivos, comandos y resultado.
18. Si una tarea no se completa, conserva `- [ ]`, `Evidencia: pending` y documenta el bloqueo.
19. Resume tareas completadas, rutas, componentes, contratos y pruebas ejecutadas.

Hook de cierre:
- Si Docker Compose esta disponible y el usuario no pidió omitirlo, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.
- Si Docker Compose no esta disponible, registrar el skip con la causa exacta.
