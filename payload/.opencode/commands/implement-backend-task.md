---
description: Implementa una tarea backend InVet, por ejemplo BE-001.
agent: invet-backend-implementer
subtask: false
---

Implementa la tarea backend indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de alcance/seguridad o se requiere una accion destructiva/migracion irreversible.
1. Acepta `BE-00X`, `FE-00X` o `QA-00X`; normaliza el indice a `BE-00X` para ejecutar la responsabilidad backend.
2. Identifica el plan generado por `/plan-task`: `docs/opencode/plans/BE-00X-plan.md`.
   - Para BE-008, el router canónico vive en `backend/app/api/v1/routers/appointment_router.py` y los schemas en `backend/app/api/v1/schemas/appointment_schemas.py`.
   - La API base del repo es `http://localhost:8000/api/v1` y la UI de referencia corre en `http://localhost:3000`.
3. Ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage backend` antes de editar codigo.
   - Si falla, deten la implementacion y reporta cada gap.
   - Si el plan es legacy o incompleto, indica `/plan-task BE-00X`.
4. Ejecuta `python backend/scripts/manage_slice_task.py manifest BE-00X --layer backend` y `python backend/scripts/manage_slice_task.py verify BE-00X --layer backend`; lee `docs/opencode/manifests/BE-00X-backend.md` y consulta el plan completo unicamente ante una contradiccion verificable.
5. Revisa `docs/opencode/checkpoints/BE-00X-backend.json` y omite tareas ya completadas con evidencia.
6. Para cada tarea pendiente, una por vez:
   - inicia con `python backend/scripts/manage_slice_task.py start BE-00X --task BE-00X-TNN`;
   - publica el estado con `state --set reading|editing|testing|waiting-permission` antes de cada fase;
   - modifica solo la allowlist derivada de `Entregables`;
   - ejecuta comandos, pruebas y logs directamente, sin subagentes;
   - cierra con `finish --task BE-00X-TNN --evidence "comando y resultado"`.
7. No elimines archivos, lineas existentes ni registros `include_router(...)`. Si una eliminacion es indispensable, usa `--allow-deletions "justificacion verificable"`; el control de routers nunca se omite.
8. Si una llamada se acerca a 30 minutos, permanece varios minutos sin avance operativo o repite la misma accion tres veces, registra `state --set cancelled`, conserva el checkpoint y termina la llamada.
9. Selecciona solo tareas pendientes con `Capa: backend`.
10. Verifica los IDs de `Depende de`; cada dependencia debe estar `- [x]` y tener evidencia.
11. Implementa usando `Objetivo`, `Entregables` y `Criterios de aceptacion` como contrato.
   - Usa tambien `Tipo`, `Historia o criterio`, `Contexto necesario`, `Contratos usados` y `Resultado esperado`.
   - Si `Responsabilidad unica` no es `Si`, detente y pide regenerar el plan con `/plan-task BE-00X`.
   - Si una tarea mezcla contrato, persistencia, API, seguridad, pruebas, Docker o documentacion, no la implementes como bloque compuesto; pide dividirla.
12. Manten Clean Architecture:
   - router/adapters en `app/api`.
   - use cases en `app/application`.
   - entidades/reglas/ports en `app/domain`.
   - ORM/repositorios/proveedores en `app/infrastructure`.
   - config/security/errors en `app/core`.
13. Agrega o actualiza migraciones Alembic si aplica.
14. Agrega pruebas unitarias Pytest para todo archivo productivo nuevo o modificado y pruebas HTTPX cuando el criterio sea de API.
15. No delegues a QA las pruebas unitarias backend.
16. No expongas modelos ORM.
17. Valida permisos y pertenencia de tenant/propietario/clinica/sucursal.
18. Para tareas de ORM, repositorios, migraciones, base de datos, permisos, ownership, IDOR/BOLA o auditoria, ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage secure-persistence` antes de entregar backend.
19. Marca `- [x]` solo tras ejecutar `Validacion`; reemplaza `Evidencia: pending` con archivos, comandos y resultado.
20. Si una tarea no se completa, conserva `- [ ]`, `Evidencia: pending` y documenta el bloqueo.
21. Resume tareas completadas, archivos modificados, endpoints y pruebas ejecutadas.
22. Escribe comentarios, evidencias y outcomes en UTF-8. Corrige mojibake como `Ã`, `Â` o `â` antes de cerrar.

Hook de cierre:
- Si Docker Compose esta disponible y el usuario no pidió omitirlo, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.
- Si Docker Compose no esta disponible, registrar el skip con la causa exacta.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
