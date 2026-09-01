---
manifest_version: 1
slice: "013"
layer: frontend
generated_at: 2026-08-31T23:55:16+00:00
source_plan: docs/opencode/plans/BE-013-plan.md
source_plan_sha256: 642c5f6278818acb924edc251bd441cb236522a3b33398f4d0b9908df3289a42
source_task: docs/opencode/tasks/frontend/FE-013.md
source_task_sha256: 34cab1e759a35aa7febe742b9e6d7c783018c32144fda59363aa04eeaa52b9d7
---

# BE-013 - manifiesto compacto frontend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/frontend/FE-013.md`

## Archivos permitidos

- `docs/opencode/checkpoints/BE-013-frontend.json`
- `docs/opencode/manifests/BE-013-frontend.md`
- `docs/opencode/plans/BE-013-plan.md`
- `frontend/**/*.spec.*`
- `frontend/**/*.test.*`
- `frontend/src/app/portal/notifications/page.tsx`
- `frontend/src/features/notifications/NotificationBadge.tsx`
- `frontend/src/features/notifications/NotificationCenter.tsx`
- `frontend/src/shared/api/notification.test.ts`
- `frontend/src/shared/api/notification.ts`

## Tareas

### FE-013-T01 - COMPLETADA
- Tipo: cliente api
- Criterio: AC-013-05, AC-013-04
- Objetivo: Implementar operaciones tipadas sobre el endpoint del slice.
- Depende de: BE-013-T05
- Contexto: `frontend/src/shared/api/` (estructura); contratos API del plan; manejo centralizado de errores reusando instancia base.
- Contratos: AC-013-04, AC-013-05
- Entregables: `frontend/src/shared/api/notification.ts` (funciones listNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead), `frontend/src/shared/api/notification.test.ts`.
- Aceptacion: Funciones tipadas con typescript; manejo unificado de errores HTTP reusando instancia base; typecheck sin errores `npx tsc --noEmit`; Jest pasa los cuatro contratos.
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/shared/api/notification.test.ts`.
- Resultado: Cliente tipado operativo, listo para consumo por componentes.

### FE-013-T02 - COMPLETADA
- Tipo: componente
- Criterio: AC-013-07, AC-013-04
- Objetivo: Implementar lista paginada del usuario con filtros.
- Depende de: FE-013-T01
- Contexto: `frontend/src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner), ruta `/portal/notifications/page.tsx`.
- Contratos: AC-013-04, AC-013-07
- Entregables: `frontend/src/features/notifications/NotificationCenter.tsx`, `NotificationCenter.test.tsx` (Jest).
- Aceptacion: Tabs **Todas** y **No leidas**; paginacion visual con botones; cada item clickeable actualiza mark read inmediatamente; EmptyState centrado ("Sin notificaciones recientes") cuando no hay registros.
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/notifications/NotificationCenter.test.tsx`.
- Resultado: Listado usable e informativo para el usuario final del portal.

### FE-013-T03 - COMPLETADA
- Tipo: componente
- Criterio: AC-013-08
- Objetivo: Integrar conteo de notificaciones en la barra superior.
- Depende de: FE-013-T01
- Contexto: `frontend/src/app/layout.tsx` o componente nav existente; endpoint unread-count del plan.
- Contratos: AC-013-08
- Entregables: `frontend/src/features/notifications/NotificationBadge.tsx`, `NotificationBadge.test.tsx`, integration en layout/nav.
- Aceptacion: Badge muestra numero > 0 entre parentesis o badge rojo visible; oculto si count == 0; se refresca tras cada marcacion individual o leer todo; accesible con aria-label "X notificaciones sin leer" y foco visible.
- Validacion: `cd frontend && npx tsc --noEmit` + Jest renderizado del componente en ambos estados (vacío y con conteo).
- Resultado: Badge visible e informativo sobre el header del portal.

### FE-013-T04 - COMPLETADA
- Tipo: ruta
- Criterio: AC-013-07, AC-013-09
- Objetivo: Crear la pagina portal que aloja el centro de notificaciones.
- Depende de: FE-013-T02, FE-013-T03
- Contexto: `frontend/src/app/portal/` (estructura); estructura Next.js pages routing (app dir).
- Contratos: AC-013-07, AC-013-09
- Entregables: `frontend/src/app/portal/notifications/page.tsx`.
- Aceptacion: Pagina que redirige a `/login?returnUrl=/portal/notifications` si no hay sesion. Renderiza NotificationCenter dentro del layout existente sin breaks visuales en mobile ni desktop. Sin links `#` en flujos implementados.
- Validacion: `cd frontend && npx tsc --noEmit`; navegacion autentificada muestra panel; no-auth produce redirect verificado en tests Jest.
- Resultado: Pagina accesible por usuarios internos con el centro de notificaciones integrado.

## Brief de capa

## Objetivo
Centro de notificaciones y badges básicos.
## Dependencias
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
