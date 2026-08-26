---
manifest_version: 1
slice: "012"
layer: frontend
generated_at: 2026-08-26T22:28:54+00:00
source_plan: docs/opencode/plans/BE-012-plan.md
source_plan_sha256: 65260d71a32cd8c0276f060281ad2f3b6915736c0db0a2921ef8786ad41c26da
source_task: docs/opencode/tasks/frontend/FE-012.md
source_task_sha256: f219468744f20f8fd249e87b400a17a995ce824bf9901df0231b8c18e06ece02
---

# BE-012 - manifiesto compacto frontend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/frontend/FE-012.md`

## Archivos permitidos

- `docs/opencode/checkpoints/BE-012-frontend.json`
- `docs/opencode/manifests/BE-012-frontend.md`
- `docs/opencode/plans/BE-012-plan.md`
- `frontend/**/*.spec.*`
- `frontend/**/*.test.*`
- `frontend/src/features/reviews/RatingForm.test.tsx`
- `frontend/src/features/reviews/RatingForm.tsx`
- `frontend/src/features/reviews/ReviewPublicList.test.tsx`
- `frontend/src/features/reviews/ReviewPublicList.tsx`
- `frontend/src/features/reviews/ReviewRespondForm.test.tsx`
- `frontend/src/features/reviews/ReviewRespondForm.tsx`
- `frontend/src/features/reviews/ReviewStaffList.tsx`
- `frontend/src/shared/api/review.test.ts`
- `frontend/src/shared/api/review.ts`

## Tareas

### FE-012-T01 - COMPLETADA
- Tipo: cliente api
- Criterio: AC-012-07, AC-012-13
- Objetivo: Implementar cliente API tipado para operaciones de reseñas.
- Depende de: BE-012-T05
- Contexto: `frontend/src/shared/api/payment.ts` (referencia), contrato del plan
- Contratos: AC-012-07, AC-012-13
- Entregables: `frontend/src/shared/api/review.ts`, `frontend/src/shared/api/review.test.ts`
- Aceptacion: Funciones createReview, getReview, listPublicReviews, listClinicReviews, respondReview con manejo centralizado de errores HTTP. Typecheck sin errores.
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/shared/api/review.test.ts`.
- Resultado: Cliente API disponible para componentes.

### FE-012-T02 - COMPLETADA
- Tipo: componente
- Criterio: AC-012-01, AC-012-11
- Objetivo: Implementar la sección Calificar cita en el detalle de cita.
- Depende de: FE-012-T01
- Contexto: `frontend/src/features/appointments/components/AppointmentDetail.tsx`, flujo UX del plan
- Contratos: AC-012-01, AC-012-11
- Entregables: `frontend/src/features/reviews/RatingForm.tsx`, `frontend/src/features/reviews/RatingForm.test.tsx`
- Aceptacion: Estrellas 1..5 con label asociado; textarea comment max 2048; botón Calificar cita; estados submitting, error (422/409/404 inline), success (toast); tras crear se deshabilita la sección mostrando "ya calificó esta cita".
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews/RatingForm.test.tsx`.
- Resultado: Formulario calificación usable por el propietario.

### FE-012-T03 - COMPLETADA
- Tipo: componente
- Criterio: AC-012-07, AC-012-08
- Objetivo: Mostrar el listado paginado de reseñas en el perfil publico.
- Depende de: FE-012-T01
- Contexto: `frontend/src/features/public-clinic-profile/BranchProfile.tsx`, contrato GET /reviews/public/{branchId}
- Contratos: AC-012-07, AC-012-08
- Entregables: `frontend/src/features/reviews/ReviewPublicList.tsx`, `frontend/src/features/reviews/ReviewPublicList.test.tsx`
- Aceptacion: Tarjeta promedio, distribucion 5-1, listado paginado con meta; muestra respuesta clinica cuando existe; estados loading, success, empty, error; responsive mobile-first; typecheck sin errores.
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews/ReviewPublicList.test.tsx`.
- Resultado: Sección Reseñas visible al anónimo en el perfil publico.

### FE-012-T04 - COMPLETADA
- Tipo: componente
- Criterio: AC-012-05, AC-012-06
- Objetivo: Implementar el formulario de respuesta clinica a reseñas.
- Depende de: FE-012-T01
- Contexto: `docs/opencode/tasks/frontend/FE-012.md`; contratos GET /reviews?branch_id= y POST /{id}/respond
- Contratos: AC-012-05, AC-012-06
- Entregables: `frontend/src/features/reviews/ReviewStaffList.tsx`, `frontend/src/features/reviews/ReviewRespondForm.tsx`, `frontend/src/features/reviews/ReviewRespondForm.test.tsx`
- Aceptacion: Listado por sucursal con estado respondida; formulario de respuesta con body max 2048; 403 y 404 mapeados a banners legibles; toast de exito; 409 visualizado como "ya respondida".
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews/ReviewRespondForm.test.tsx`.
- Resultado: Flujo clinico de respuesta completo.

### FE-012-T05 - COMPLETADA
- Tipo: estado ux
- Criterio: AC-012-10
- Objetivo: Implementar los cinco estados en los cuatro componentes del slice.
- Depende de: FE-012-T02, FE-012-T03, FE-012-T04
- Contexto: `frontend/src/shared/ui` (EmptyState, LoadingSpinner, ErrorBanner, SuccessToast)
- Contratos: AC-012-10
- Entregables: Estados en `RatingForm`, `ReviewPublicList`, `ReviewStaffList`, `ReviewRespondForm`
- Aceptacion: Los cinco estados observables por componente; banner de error legible; CTA en empty; tipografia consistente con tokens UI del proyecto.
- Validacion: `cd frontend && npx tsc --noEmit && npx jest src/features/reviews`.
- Resultado: Estados UX completos del flujo de reseñas.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
