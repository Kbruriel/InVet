---
manifest_version: 1
slice: "015"
layer: frontend
generated_at: 2026-09-07T23:29:16+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: 2e65b3a8c877e97da8639d617e56613f701fa37ee145127a0da81ace38c52823
source_task: docs/opencode/tasks/frontend/FE-015.md
source_task_sha256: 31985546bffba827da012947532c712334d44c620367f8bdb1a5e8a1c7de4780
---

# BE-015 - manifiesto compacto frontend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/frontend/FE-015.md`

## Archivos permitidos

- `docs/opencode/checkpoints/BE-015-frontend.json`
- `docs/opencode/manifests/BE-015-frontend.md`
- `docs/opencode/plans/BE-015-plan.md`
- `frontend/**/*.spec.*`
- `frontend/**/*.test.*`
- `frontend/src/app/portal/admin/reports/page.tsx`
- `frontend/src/features/reports/api.ts`
- `frontend/src/features/reports/components/**`
- `frontend/src/features/reports/components/FilterBar.tsx`
- `frontend/src/features/reports/components/ReportTable.tsx`
- `frontend/src/features/reports/hooks/useReports.ts`

## Tareas

### FE-015-T01 - COMPLETADA
- Tipo: cliente api
- Criterio: AC-015-01, AC-015-03
- Objetivo: Centralizar llamadas HTTP en capa cliente.
- Depende de: Ninguna
- Contexto: `docs/opencode/tasks/frontend/FE-015.md`; estructura API client existente en frontend/src/shared/api.
- Contratos: contratos GET /api/v1/reports/* del plan.
- Entregables: archivo `frontend/src/features/reports/api.ts` con seis funciones tipadas exportando tipos TypeScript para cada respuesta de endpoint.
- Aceptacion: Cada funcion recibe params correctos y retorna tipo especificado. Sin errores TypeScript al importar.
- Validacion: `npx tsc --noEmit --project frontend/tsconfig.json`.
- Resultado: Client API tipado listo para consumo por el hook useReports.

### FE-015-T02 - COMPLETADA
- Tipo: componente
- Criterio: AC-015-01, AC-015-03, AC-015-05
- Objetivo: Orquestar llamadas HTTP a clientes API reportes desde un hook.
- Depende de: FE-015-T01
- Contexto: `docs/opencode/tasks/frontend/FE-015.md`; api.ts; tipado contratos plan.
- Contratos: contrato GET /api/v1/reports/* del plan; estructura response paginada con items total page page_size.
- Entregables: archivo `frontend/src/features/reports/hooks/useReports.ts` exponiendo data, total, page, error, e isLoading con fetch solo tras aplicar filtro.
- Aceptacion: Hook expone todos los estados listados. Fetch se ejecuta solo tras llamda de aplicacion manual (Apply). Tipos TypeScript completos para respuestas. Manejode errores HTTP mapeado a estado error en el hook.
- Validacion: `npm run typecheck`.
- Resultado: Hook useReports consumible por cualquier componente del modulo reportes.

### FE-015-T03 - COMPLETADA
- Tipo: componente
- Criterio: AC-015-01
- Objetivo: Construir barra de filtros para consultas de reportes.
- Depende de: FE-015-T02
- Contexto: `docs/opencode/tasks/frontend/FE-015.md`; frontend_visual_alignment.md tokens; componentes select y datepicker ya disponibles en shared UI.
- Contratos: formulario y reglas validacion contract del plan (period_start, period_end, type, clinic_id).
- Entregables: archivo `frontend/src/features/reports/components/FilterBar.tsx` con selector tipo, dos inputs de fecha, y boton Apply.
- Aceptacion: Select despliega las seis opciones de reporte. Validacion interna rechaza period_start mayor que period_end antes Enviar. Campos opcionales se manejan correctamente.
- Validacion: `npm test -- FilterBar.test.tsx` si hay framework; visual inspection responsive.
- Resultado: Barra de filtros con validacion integrada lista para integracion en pagina.

### FE-015-T04 - COMPLETADA
- Tipo: componente
- Criterio: AC-015-02, AC-015-03
- Objetivo: Construir componente tabla reutilizable con soporte de pagination.
- Depende de: FE-015-T01
- Contexto: `docs/opencode/tasks/frontend/FE-015.md`; design system de tablas ya existente en shared UI.
- Contratos: estructura response paginada `{items, total, page, page_size}` del plan.
- Entregables: archivo `frontend/src/features/reports/components/ReportTable.tsx` parametrizable por columns y data source.
- Aceptacion: Componente acepta data array paginado con interface pagina como props. Estado loading muestra spinner. Estado empty muestra mensaje sin datos. Pagination navega correctamente entre paginas sin perder filtros.
- Validacion: `npm test -- ReportTable.test.tsx`.
- Resultado: Tabla generica lista para usar en cualquier tipo de reporte.

### FE-015-T05 - COMPLETADA
- Tipo: ruta
- Criterio: AC-015-01..AC-015-08
- Objetivo: Construir pagina admin-reports con filtros.
- Depende de: FE-015-T02, FE-015-T03, FE-015-T04
- Contexto: `docs/opencode/tasks/frontend/FE-015.md`; contrat frontend del plan con flujos y estados UX.
- Contratos: flujos seleccion de tipo mas filtros mas paginacion; estados loading error empty success.
- Entregables: archivo `frontend/src/app/portal/admin/reports/page.tsx` montando FilterBar, useReports, ReportTable en columna vertical responsive.
- Aceptacion: Selecciona tipo y aplico filtro muestra datos correctos. Cambio de pagina no pierde filtros activos. Error red se muestra con banner con opcion de reintentar. Estado empty visible cuando total igual cero. Build limpio sin errores criticos ni warnings.
- Validacion: `npm run build` desde frontend/ sin errores de compilation.
- Resultado: Pagina admin/reports completa lista para QA E2E y UI Automation.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
