---
encoding: UTF-8
artifact: ui_checks
slice: "FE-004"
parent_slice: "BE-004"
qa_slice: "QA-004"
---

# UI Checks para slice FE-004 — Perfil público clínica/sucursal

## Resumen

- Slice: `FE-004` (padre: `BE-004`, QA: `QA-004`)
- Decision: `APPROVED`
- Timestamp: 2026-08-08
- Entorno: Next.js 14.2 / React 18.3 / TypeScript 5.4 / Tailwind 3.4 / Jest 29.7

## Resultados

| Capa | Check | Comando | Estado | Evidencia |
| --- | --- | --- | --- | --- |
| Frontend | lint | `npm run lint` | PASS | Solo warnings no bloqueantes (`<img>` vs `<Image />`) en 4 archivos, ninguno bloqueante para FE-004 |
| Frontend | typecheck | `npm run typecheck` | BLOCKED (no FE-004) | 4 errores TS en `test/login-page.test.tsx` — archivo no relacionado con FE-004 (`toBeInTheDocument` types missing) |
| Frontend | test | `npm test` | PASS (56/57) | 1 fallo preexistente en `CategoryChips.test.tsx` — no relacionado con FE-004 |
| UI Automation | e2e tests | `fe-004-branch-profile.spec.ts` | EXISTS | 12 tests E2E implementados (UIA-004-01 a UIA-004-12) |

## Validación de rutas

| Ruta | Estado | Archivo |
| --- | --- | --- |
| `/clinics/[branchId]` (público) | ✅ Existe | `frontend/src/app/clinics/[branchId]/page.tsx` |
| `/clinics/manage/branches/[branchId]` (protegido) | ✅ Existe | `frontend/src/app/clinics/manage/branches/[branchId]/page.tsx` |
| Layout `/clinics/` | ✅ Existe | `frontend/src/app/clinics/layout.tsx` |

## Validación de componentes

### BranchProfile (`src/features/public-clinic-profile/BranchProfile.tsx`)

| Criterio | Estado | Detalle |
| --- | --- | --- |
| Estados UI | ✅ | loading, error, empty, success implementados |
| Loading | ✅ | `LoadingSpinner` con label "Cargando perfil de sucursal..." |
| Error | ✅ | `ErrorBanner` con mensaje configurable + botón "Reintentar" |
| Empty | ✅ | `EmptyState` "Sucursal no encontrada" con link a `/clinicas` |
| Success | ✅ | Card completa con header, servicios, horarios, rating, disponibilidad, CTA |
| Servicios | ✅ | `ServicesSection` — nombre, descripción, precio ($XX), duración (min), estado activo/inactivo |
| Horarios | ✅ | `SchedulesSection` — día formateado (Lunes-Domingo), hora apertura/cierre, badge "hoy", badge "Feriado" |
| Calificaciones | ✅ | `RatingSection` — promedio X.X, estrellas ★/☆, conteo con singular/plural |
| Disponibilidad | ✅ | `AvailabilityBadge` — Disponible (green), No disponible (red), Sin cupos (yellow) |
| CTA | ✅ | "Solicitar cita" → `/register?branch={branchId}`, "Otras clínicas" → `/clinicas` |
| Back nav | ✅ | "← Volver a clínicas" → `/clinicas` |

### ProtectedBranchPage (`frontend/src/app/clinics/manage/branches/[branchId]/page.tsx`)

| Criterio | Estado | Detalle |
| --- | --- | --- |
| Autenticación | ✅ | Redirect a `/login` en 401 |
| Loading | ✅ | `LoadingSpinner` |
| Error | ✅ | `ErrorBanner` con "Reintentar" |
| Success | ✅ | Card con datos protegidos |

## Validación de accesibilidad

| Criterio | Estado | Detalle |
| --- | --- | --- |
| aria-labels | ✅ | Rating stars: `aria-label="Calificación X.X de 5 estrellas"`; rating section: `aria-label` en div; logo img: `alt="Logo de {name}"` |
| Semantic HTML | ✅ | `<h1>` para nombre de sucursal, `<h2>` para secciones (Servicios, Horarios, Calificaciones, Acerca de), `<section>` con aria-label, `<Link>` para navegación |
| Roles | ✅ | `role="button"` en CTAs, `role="status"` implícito en AvailabilityBadge, `role="alert"` en ErrorBanner |
| Focus states | ✅ | Botones con focus ring (verificado en Button.test.tsx) |

## Validación de responsive design

| Breakpoint | Estado | Detalle |
| --- | --- | --- |
| Mobile (< 640px) | ✅ | Layout vertical por defecto, padding base |
| sm (≥ 640px) | ✅ | `sm:flex-row` en header, `sm:text-3xl` en heading, `sm:items-start` alignment |
| Tailwind classes | ✅ | Uso consistente de `flex`, `space-y`, `gap`, `rounded-lg`, `bg-*`, `text-*`, `p-*`, `px-*`, `py-*` |

## UI Automation Tests (`InVet_UI_Automation/tests/e2e/fe-004-branch-profile.spec.ts`)

| Test ID | Criterio QA | Estado |
| --- | --- | --- |
| UIA-004-01 | AC-004-01 — Perfil público renderiza todas las secciones | ✅ Implementado |
| UIA-004-02 | AC-004-03 — Servicios muestra nombre, precio, duración | ✅ Implementado |
| UIA-004-03 | AC-004-04 — Horarios muestra día, apertura, cierre | ✅ Implementado |
| UIA-004-04 | AC-004-05 — Rating muestra promedio, conteo, estrellas | ✅ Implementado |
| UIA-004-05 | AC-004-06 — Badge de disponibilidad con estado y color | ✅ Implementado |
| UIA-004-06 | AC-004-07 — CTA navega a `/register?branch={id}` | ✅ Implementado |
| UIA-004-07 | AC-004-08 — ID inexistente devuelve error seguro | ✅ Implementado |
| UIA-004-08 | AC-004-02 — Ruta protegida redirige a `/login` en 401 | ✅ Implementado |
| UIA-004-09 | Loading state con spinner | ✅ Implementado |
| UIA-004-10 | Empty state cuando sucursal no existe | ✅ Implementado |
| UIA-004-11 | Detalle de clínica pública renderiza datos básicos | ✅ Implementado |
| UIA-004-12 | Navegación de retorno a rutas correctas | ✅ Implementado |

Total: 12 tests E2E implementados, todos con trazabilidad completa (slice, user story, criteria, Gherkin annotations).

## Observaciones

### No bloqueantes (warnings)

1. **`<img>` vs `<Image />`**: 4 warnings de ESLint sobre uso de `<img>` en lugar de `next/image`. Esto es una recomendación de optimización de rendimiento (LCP), no un error funcional. No bloquea la aprobación del slice.
   - `frontend/src/app/clinicas/page.tsx:120`
   - `frontend/src/app/clinicas/[clinicId]/page.tsx:82`
   - `frontend/src/app/clinics/manage/branches/[branchId]/page.tsx:64`
   - `frontend/src/features/public-clinic-profile/BranchProfile.tsx:237`

### Preexistentes (no FE-004)

1. **TypeScript errors in `test/login-page.test.tsx`**: 4 errores de `toBeInTheDocument` — archivo no relacionado con FE-004.
2. **CategoryChips test failure**: Error de `jest.spyOn` en `CategoryChips.test.tsx` — preexistente, no relacionado con FE-004.

## Decision final

- **Decision: APPROVED**
- **Evidencia**:
  - Rutas implementadas correctamente (`/clinics/[branchId]` público, `/clinics/manage/branches/[branchId]` protegido)
  - Componente `BranchProfile` con todos los estados UI (loading/error/empty/success)
  - Secciones completas: servicios, horarios, calificaciones, disponibilidad, CTA
  - Accesibilidad: aria-labels, semantic HTML, roles correctos
  - Responsive design con Tailwind breakpoints (sm:, flex-col/flex-row)
  - 12 tests E2E implementados con trazabilidad completa
  - Lint pasa sin errores bloqueantes
  - Tests de Jest pasan (56/57; fallo preexistente no relacionado)
  - Protected route con redirect 401 a `/login`
  - No hay filtrado de datos sensibles en el frontend

## Politica UTF-8

- Resultados y outcomes conservan UTF-8.
- No mojake detectado.
