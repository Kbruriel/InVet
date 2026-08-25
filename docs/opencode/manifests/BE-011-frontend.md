---
manifest_version: 1
slice: "011"
layer: frontend
generated_at: 2026-08-25T17:32:05+00:00
source_plan: docs/opencode/plans/BE-011-plan.md
source_plan_sha256: 91a3f6f70e23aa02c6a0037099a49513d1a5d802457596628d9e22a0ef287d3c
source_task: docs/opencode/tasks/frontend/FE-011.md
source_task_sha256: c9a4c551eadc9ba1faaf0725a019f610a92400dcedb36f07cbff455c654abf9b
---

# BE-011 - manifiesto compacto frontend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/frontend/FE-011.md`

## Archivos permitidos

- `docs/opencode/checkpoints/BE-011-frontend.json`
- `docs/opencode/manifests/BE-011-frontend.md`
- `docs/opencode/plans/BE-011-plan.md`
- `frontend/**/*.spec.*`
- `frontend/**/*.test.*`
- `frontend/src/app/clinic/payments/**`
- `frontend/src/app/clinic/payments/[id]/**`
- `frontend/src/app/clinic/payments/[id]/page.tsx`
- `frontend/src/app/clinic/payments/history/**`
- `frontend/src/app/clinic/payments/history/page.tsx`
- `frontend/src/app/clinic/payments/page.tsx`
- `frontend/src/shared/api/payment.ts`

## Tareas

### FE-011-T01 - COMPLETADA
- Tipo: cliente api
- Criterio: FE-011: consumo API
- Objetivo: Implementar cliente API tipado para operaciones de pagos.
- Depende de: BE-011-T05
- Contexto: `frontend/src/shared/api/consultation.ts` (referencia), contrato del plan
- Contratos: AC-011-01, AC-011-04
- Entregables: `frontend/src/shared/api/payment.ts`
- Aceptacion: Funciones createPayment, getPayment, listPayments, cancelPayment con manejo centralizado de errores HTTP. Typecheck sin errores.
- Validacion: `cd frontend && npx tsc --noEmit` sin errores.
- Resultado: Cliente API disponible para componentes.

### FE-011-T02 - COMPLETADA
- Tipo: componente
- Criterio: FE-011: formulario operativo
- Objetivo: Implementar el formulario de registro de pago por el staff.
- Depende de: FE-011-T01
- Contexto: `docs/opencode/tasks/frontend/FE-011.md`; flujo UX del plan
- Contratos: AC-011-01, AC-011-02
- Entregables: `frontend/src/app/clinic/payments/page.tsx`, componente `PaymentForm`
- Aceptacion: Campos appointment, service, amount, method, amount_received (condicion CASH) con validacion inline; estados submitting, error, success; calculo de cambio visible.
- Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
- Resultado: Formulario usable por el staff para crear pago.

### FE-011-T03 - COMPLETADA
- Tipo: componente
- Criterio: FE-011: listado y filtros
- Objetivo: Implementar listado paginado de pagos con filtro por periodo.
- Depende de: FE-011-T01
- Contexto: `docs/opencode/tasks/frontend/FE-011.md`; contrato GET /payments
- Contratos: AC-011-04
- Entregables: `frontend/src/app/clinic/payments/history/page.tsx`, componente `PaymentList`
- Aceptacion: Listado paginado con meta; estados loading, success, empty, error; responsive mobile-first; typecheck sin errores.
- Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
- Resultado: Historial paginado visible por el staff.

### FE-011-T04 - COMPLETADA
- Tipo: componente
- Criterio: FE-011: recibo y cancelacion
- Objetivo: Mostrar el detalle del pago, permitir su cancelacion.
- Depende de: FE-011-T01
- Contexto: `docs/opencode/tasks/frontend/FE-011.md`; contrato GET /payments/{id} y POST /{id}/cancel
- Contratos: AC-011-03, AC-011-05
- Entregables: `frontend/src/app/clinic/payments/[id]/page.tsx`, componente `PaymentDetail`
- Aceptacion: Secciones datos, importe, metodo, cambio legibles; boton Cancelar con confirmacion; estado CANCELLED visible; accesibilidad minima.
- Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
- Resultado: Recibo no fiscal y operacion de cancelacion.

### FE-011-T05 - COMPLETADA
- Tipo: estado ux
- Criterio: FE-011: estados UX
- Objetivo: Implementar estados loading, submitting, empty, success, error.
- Depende de: FE-011-T02, FE-011-T03, FE-011-T04
- Contexto: `frontend/src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast)
- Contratos: AC-011-08
- Entregables: Estados en `PaymentForm`, `PaymentList`, `PaymentDetail`
- Aceptacion: Los cinco estados observables por componente; banner de error legible; CTA en empty; tipografia consistente con tokens UI del proyecto.
- Validacion: `cd frontend && npm run lint && npx tsc --noEmit` sin errores.
- Resultado: Estados UX completos del flujo de pagos.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
