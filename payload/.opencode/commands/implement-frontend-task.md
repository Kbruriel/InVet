---
description: Implementa la responsabilidad frontend de un slice InVet.
agent: invet-frontend-implementer
subtask: false
---

Implementa la tarea frontend indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta solo si falta informacion bloqueante, hay una decision critica de alcance/UX o se requiere una accion destructiva.
1. Acepta `BE-00X`, `FE-00X` o `QA-00X`; identifica los tres IDs del mismo indice y ejecuta la responsabilidad frontend.
2. Identifica el plan canonico `docs/opencode/plans/BE-00X-plan.md`.
   - Para FE-008, las rutas canónicas son `frontend/src/app/portal/owner/appointments`, `frontend/src/app/portal/owner/appointments/new` y `frontend/src/app/clinic/appointments`.
   - La UI base corre en `http://localhost:3000` y consume la API en `http://localhost:8000/api/v1`.
3. Ejecuta `python backend/scripts/validate_slice_plan.py FE-00X --stage frontend` antes de editar codigo.
   - Si falla, deten la implementacion y reporta cada gap.
   - Si el plan es legacy o incompleto, indica `/plan-task FE-00X`.
4. Ejecuta `python backend/scripts/manage_slice_task.py manifest BE-00X --layer frontend` y `python backend/scripts/manage_slice_task.py verify BE-00X --layer frontend`; lee `docs/opencode/manifests/BE-00X-frontend.md` y abre el plan completo solo ante contradicciones.
5. Revisa `docs/opencode/checkpoints/BE-00X-frontend.json` y procesa una tarea pendiente a la vez con `start`, estados visibles y `finish` del controlador.
6. Ejecuta comandos, pruebas y logs directamente; no inicies subagentes. Respeta la allowlist de `Entregables`, bloquea eliminaciones no justificadas y cancela ciclos de 30 minutos o tres acciones repetidas.
7. Verifica que `Contrato de implementacion frontend` defina rutas, flujos, API, formularios, componentes, accesibilidad y pruebas.
8. Si falta `frontend/package.json` y el slice requiere base tecnica, crea un workspace ejecutable antes de implementar UI.
   - Para `FE-001`, deja Next.js, TypeScript, Tailwind local, scripts `lint`, `typecheck`, `test`, `build`, estructura `src/` y pruebas verificables.
9. Selecciona solo tareas pendientes con `Capa: frontend`.
10. Verifica los IDs de `Depende de`; cada dependencia debe estar `- [x]` y tener evidencia.
   - Si el backend aun no existe, solo continua cuando el plan documente un mock aprobado como entregable.
11. Implementa usando `Objetivo`, `Entregables` y `Criterios de aceptacion` como contrato.
   - Usa tambien `Tipo`, `Historia o criterio`, `Contexto necesario`, `Contratos usados` y `Resultado esperado`.
   - Si `Responsabilidad unica` no es `Si`, detente y pide regenerar el plan con `/plan-task FE-00X`.
   - Si una tarea mezcla cliente API, ruta, componente, estado UX, pruebas, Docker o documentacion, no la implementes como bloque compuesto; pide dividirla.
12. Usa Next.js, TypeScript, React y Tailwind local.
13. Aplica `docs/opencode/references/frontend_visual_alignment.md`.
14. Implementa estados loading, submitting, error, empty y success, responsive y accesibilidad segun el contrato.
15. Centraliza el consumo API en `src/shared/api`.
16. Agrega pruebas unitarias o de componente para todo archivo productivo nuevo o modificado y pruebas de integracion cuando el flujo lo requiera.
17. No delegues a QA las pruebas unitarias frontend.
18. No agregues checkout, productos, marketplace, inventario ni facturacion.
19. Ante un fallo de lint, tipos o Docker, aplica `docs/opencode/references/docker_frontend_build_troubleshooting.md`.
   - Reproduce con `docker compose build --no-cache frontend` y conserva el primer error bloqueante.
   - No declares un error preexistente o ajeno sin linea base o historial reproducible. Un error del build limpio en un entregable del slice mantiene la tarea incompleta.
   - Reporta por separado errores, advertencias y cache generada; no elimines funcionalidad requerida ni conviertas pruebas en placeholders para obtener un build verde.
20. Marca `- [x]` solo tras ejecutar `Validacion`; reemplaza `Evidencia: pending` con archivos, comandos y resultado.
21. Si una tarea no se completa, conserva `- [ ]`, `Evidencia: pending` y documenta el bloqueo.
22. Resume tareas completadas, rutas, componentes, contratos y pruebas ejecutadas.
23. Escribe comentarios, evidencias y outcomes en UTF-8. Corrige mojibake como `Ã`, `Â` o `â` antes de cerrar.

Hook de cierre:
- Si Docker Compose esta disponible y el usuario no pidió omitirlo, ejecutar primero `docker compose build --no-cache frontend`.
- Solo tras un build limpio exitoso, ejecutar `docker compose up -d --build --force-recreate db backend frontend` cuando el slice requiera integración en ejecución.
- Si Docker Compose no esta disponible, registrar el skip con la causa exacta.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
