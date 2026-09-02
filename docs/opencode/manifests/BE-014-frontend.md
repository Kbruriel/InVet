---
manifest_version: 1
slice: "014"
layer: frontend
generated_at: 2026-09-02T01:17:03+00:00
source_plan: docs/opencode/plans/BE-014-plan.md
source_plan_sha256: 9e3e90dab12778e6b744a7c181f6e11a8ba381f82567ebce75e6d6f1dbe3b00c
source_task: docs/opencode/tasks/frontend/FE-014.md
source_task_sha256: 34e88d59e2097f92627028b06b10ba6f047733b57d0ea024caaf7c7eeadb6392
---

# BE-014 - manifiesto compacto frontend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/frontend/FE-014.md`

## Archivos permitidos

- `docs/opencode/checkpoints/BE-014-frontend.json`
- `docs/opencode/manifests/BE-014-frontend.md`
- `docs/opencode/plans/BE-014-plan.md`
- `frontend/**/*.spec.*`
- `frontend/**/*.test.*`
- `frontend/src/app/support/[ticketId]/**`
- `frontend/src/app/support/[ticketId]/page.tsx`
- `frontend/src/app/support/page.tsx`
- `frontend/src/features/support/ui/ticket-form.tsx`
- `frontend/src/features/support/ui/ticket-list-filtered.tsx`
- `frontend/src/features/support/ui/ticket-list.tsx`
- `frontend/src/shared/api/client.ts`
- `frontend/src/shared/api/support.test.ts`
- `frontend/src/shared/api/support.ts`

## Tareas

### FE-014-T01 - COMPLETADA
- Tipo: cliente api
- Criterio: AC-02, AC-07
- Objetivo: Tipar llamadas de soporte.
- Depende de: BE-014-T04
- Contexto: Endpoints y envoltura API existente.
- Contratos: Contratos API por accion.
- Entregables: `frontend/src/shared/api/client.ts`, `frontend/src/shared/api/support.ts` y `frontend/src/shared/api/support.test.ts`.
- Aceptacion: Cada llamada conserva parámetros y errores relevantes.
- Validacion: Pruebas del cliente con respuestas simuladas.
- Resultado: Cliente reutilizable para pantallas de soporte.

### FE-014-T02 - COMPLETADA
- Tipo: componente
- Criterio: AC-01, AC-03, AC-08, AC-09
- Objetivo: Construir pantalla de soporte.
- Depende de: FE-014-T01
- Contexto: Cliente tipado y ruta protegida.
- Contratos: Crear ticket y listar tickets.
- Entregables: `frontend/src/app/support/page.tsx`, `frontend/src/features/support/ui/ticket-form.tsx`, `frontend/src/features/support/ui/ticket-list.tsx`, `frontend/src/features/support/ui/ticket-list-filtered.tsx` y sus pruebas.
- Aceptacion: La pantalla valida, envía y muestra todos los estados UX.
- Validacion: Pruebas de componente e integración.
- Resultado: Flujo principal disponible en /support.

### FE-014-T03 - COMPLETADA
- Tipo: ruta
- Criterio: AC-04, AC-05
- Objetivo: Presentar detalle autorizado.
- Depende de: FE-014-T01
- Contexto: Cliente tipado y navegación existente.
- Contratos: Consultar detalle y cambiar estado.
- Entregables: `frontend/src/app/support/[ticketId]/page.tsx`, `ticket-status-updater.tsx` y sus pruebas.
- Aceptacion: El detalle no revela datos ante respuesta 404.
- Validacion: Pruebas de ruta con 200, 404 y error.
- Resultado: Consulta segura de tickets desde la interfaz.

## Brief de capa

## Objetivo
Formulario soporte y vista de solicitudes por usuario/admin.
## Dependencias
- Backend relacionado: `BE-014`.
- QA relacionado: `QA-014`.
- Tokens y reglas visuales en `docs/opencode/references/frontend_visual_alignment.md`.
## Alcance MVP
- Implementar UI y consumo API del slice `014`.
- Mantener arquitectura Next.js/TypeScript/React/Tailwind.
- Reutilizar componentes desde `src/shared/ui`.
- Centralizar API en `src/shared/api`.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
