---
schema_version: 2
slice: "004"
canonical_plan: BE-004
---

# BE-004 Plan - Perfil público de clínica/sucursal

## Objetivo del slice

Implementar y validar el perfil público de clínica/sucursal con datos públicos, servicios, horarios, resumen de calificación, disponibilidad básica y separación segura entre información pública y protegida.

## Alcance MVP

- Endpoint público bajo `/api/v1` para consultar el perfil público de una sucursal sin autenticación.
- Endpoint protegido bajo `/api/v1` para consultar el perfil de sucursal con validación de autenticación y acceso.
- Respuestas que incluyan solo datos públicos: datos de clínica/sucursal, servicios ofrecidos, horarios públicos, rating summary y disponibilidad básica.
- Frontend público para listado/detalle de clínicas y sucursales usando cliente API centralizado.
- CTA visible para solicitud de cita sin implementar checkout, pago ni agenda avanzada.
- QA reproducible sobre happy path, negative path, permisos, IDOR/BOLA y estados UI.

## Fuera de alcance

- Marketplace, carrito, checkout, pasarela de pago, inventario o facturación.
- Administración completa de clínicas y sucursales; corresponde a slices posteriores.
- CRUD completo de servicios, horarios o calificaciones.
- Recomendaciones médicas automáticas.
- Integración externa con mapas, calendario o pasarelas.

## Suposiciones

- Los datos públicos permitidos son nombre, dirección, ciudad, teléfono público, horarios públicos, servicios publicados, rating summary y disponibilidad básica.
- Los datos administrativos, ownership interno, auditoría, tokens, usuarios y configuraciones sensibles no deben aparecer en respuestas públicas.
- El frontend activo vive en `src`, no en `frontend/src`, según la estructura actual del repositorio.
- El backend activo para este plan vive en `backend/app`.
- Si el equipo decide conservar también el árbol raíz `app`, se debe documentar explícitamente como legacy o runtime alterno antes de implementar.

## Entidades y reglas de negocio

- **Clinic**: organización veterinaria con datos públicos y administrativos.
- **Branch**: sucursal perteneciente a una clínica; expone datos públicos y conserva datos protegidos para administración.
- **Service**: servicio publicado por una sucursal, con nombre, descripción corta y estado activo.
- **BranchSchedule**: horario público por día y rango horario.
- **RatingSummary**: promedio, total de opiniones y distribución básica sin exponer información personal de usuarios.
- **AvailabilitySummary**: señal pública de disponibilidad básica, sin prometer agenda transaccional.

Reglas:
- El perfil público no requiere autenticación.
- El perfil público no expone IDs internos sensibles, datos de usuarios, tokens, auditoría ni configuración privada.
- El perfil protegido requiere usuario autenticado y validación de acceso a la clínica/sucursal.
- Un usuario autenticado sin acceso a la sucursal recibe `403`.
- Una sucursal inexistente recibe `404`.
- Errores de validación reciben `400` o `422` sin detalles internos.
- El backend no debe exponer modelos ORM directamente.

## Endpoints esperados

- `GET /api/v1/clinics/branches/{branch_id}`
  - Público.
  - No requiere autenticación.
  - Devuelve perfil público de sucursal, servicios activos, horarios públicos, rating summary y disponibilidad básica.

- `GET /api/v1/clinics/{clinic_id}/{branch_id}`
  - Protegido.
  - Requiere autenticación.
  - Valida que la sucursal pertenece a la clínica indicada y que el usuario tiene acceso cuando aplique.
  - Devuelve el contrato permitido para vista protegida sin exponer datos administrativos innecesarios.

- `GET /api/v1/clinics`
  - Público o protegido según configuración del producto.
  - Sirve como soporte para listado público si el frontend necesita descubrir clínicas.

- `GET /api/v1/clinics/{clinic_id}`
  - Público o protegido según configuración del producto.
  - Sirve como soporte para detalle de clínica si el frontend conserva la ruta actual `src/app/clinics/[id]/page.tsx`.

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /clinics` muestra el listado público de clínicas.
- `GET /clinics/[id]` muestra el detalle público de clínica existente en el frontend actual.
- Si se implementa perfil por sucursal, agregar ruta pública `GET /clinics/[clinicId]/branches/[branchId]` o documentar por qué el detalle de clínica cubre el MVP.
- Las rutas públicas no requieren sesión.
- Acciones administrativas o protegidas no deben mostrarse a usuarios sin permiso.

### Flujos y estados UX

- Loading: skeleton o indicador claro mientras se consulta el API.
- Error: mensaje seguro y acción de reintento sin filtrar trazas internas.
- Empty: mensaje cuando no hay clínicas, sucursales, servicios u horarios disponibles.
- Success: datos públicos de clínica/sucursal, servicios, horarios, rating summary y CTA de cita.
- Submitting: estado visual para el CTA de solicitud de cita si se conecta a un flujo futuro o formulario simple.

### Contratos API por accion

- Listar clínicas:
  - Endpoint: `GET /api/v1/clinics?page={page}&size={size}&search={search}&city={city}`
  - Response: `{ data: Clinic[], pagination: { page, size, total, total_pages } }`
  - Errores: `400`, `500`.
  - Autenticación: no requerida para listado público.

- Consultar detalle de clínica:
  - Endpoint: `GET /api/v1/clinics/{clinic_id}`
  - Response: `Clinic` con sucursales públicas si aplica.
  - Errores: `404`, `500`.
  - Autenticación: no requerida si el detalle es público.

- Consultar perfil público de sucursal:
  - Endpoint: `GET /api/v1/clinics/branches/{branch_id}`
  - Response: `BranchPublicProfile`.
  - Errores: `404`, `500`.
  - Autenticación: no requerida.

- Consultar perfil protegido de sucursal:
  - Endpoint: `GET /api/v1/clinics/{clinic_id}/{branch_id}`
  - Response: `BranchProtectedProfile`.
  - Errores: `401`, `403`, `404`, `500`.
  - Autenticación: requerida.

### Formularios y validacion

- Búsqueda por texto: recortar espacios, tolerar búsqueda vacía y no enviar caracteres de control.
- Filtro por ciudad: aceptar valores conocidos o dejar sin filtro.
- CTA de cita: si solo es enlace, no debe usar `#`; si abre formulario, validar nombre, teléfono/correo y motivo.
- Mensajes de error deben ser útiles para el usuario y no revelar detalles internos.

### Arquitectura de componentes

- Páginas en `src/app/clinics` y, si aplica, `src/app/clinics/[clinicId]/branches/[branchId]`.
- Cliente API en `src/shared/api/index.ts`.
- Tipos en `src/shared/api/types.ts`.
- Componentes reutilizables en `src/shared/ui/components`.
- Si crece la lógica de perfil, crear feature `src/features/public-clinic-profile`.

### Responsive y accesibilidad

- La vista debe ser usable en mobile, tablet y desktop.
- CTA y enlaces deben tener nombres accesibles.
- Estados de error, empty y loading deben ser perceptibles sin depender solo del color.
- Mantener contraste suficiente en tarjetas, rating y mensajes.

### Estrategia de pruebas frontend

- Pruebas de componente para listado, detalle, empty, error y loading.
- Pruebas de cliente API para endpoints y manejo de errores.
- Prueba de accesibilidad básica para CTA y enlaces principales.
- Build y typecheck del frontend antes de QA.

## Pruebas QA

- Happy path público: perfil público de sucursal responde con datos permitidos.
- Happy path protegido: usuario con acceso consulta perfil protegido.
- Negative path: sucursal inexistente devuelve `404` seguro.
- Permisos: sin token en endpoint protegido devuelve `401`.
- Permisos: usuario sin acceso devuelve `403`.
- IDOR/BOLA: sucursal ajena no devuelve datos protegidos.
- Frontend: listado/detalle renderizan loading, error, empty y success.
- Regresión: no se rompen auth, healthcheck ni pruebas existentes.

## Riesgos de seguridad/IDOR/BOLA

- Exponer datos administrativos en endpoint público.
- Permitir acceso cruzado a sucursales de otra clínica mediante `clinic_id` y `branch_id`.
- Reusar respuestas protegidas en la UI pública.
- Reportar trazas internas en errores HTTP.
- Marcar QA como aprobado con evidencia histórica que no coincide con el código actual.

## Checklist tecnico

- [x] Rutas backend bajo `/api/v1` definidas y registradas en el router activo.
- [x] Schemas request/response documentados y sin exposición ORM.
- [x] Permisos y ownership definidos por endpoint.
- [x] Estados `400`, `401`, `403`, `404` y `500` definidos.
- [x] Modelos, migraciones o seeds necesarios identificados.
- [x] Cliente API frontend centralizado y alineado con endpoints.
- [x] Estados UI loading, error, empty, success y submitting cubiertos.
- [x] Pruebas backend, frontend y QA trazadas a criterios.
- [x] `run-checks.ps1` definido como cierre integral cuando los gates anteriores estén aprobados.
- [x] Documentación y reportes BE/FE/QA actualizados sin usar evidencia stale.

## Checklist de tareas

### Backend

- [ ] BE-004-T01 - Definir persistencia y contratos públicos de perfil
  Capa: backend
  Objetivo: Modelar los datos necesarios para perfil público de sucursal sin exponer información administrativa.
  Depende de: Ninguna
  Entregables: `backend/app/domain/entities`; `backend/app/infrastructure/database/models`; schemas bajo `backend/app/api/v1/schemas`; migraciones o bootstrap si aplican.
  Criterios de aceptacion: Clinic y Branch contienen campos públicos necesarios; servicios, horarios, rating summary y disponibilidad básica tienen representación verificable; no se exponen modelos ORM en respuestas.
  Validacion: Revisar modelos/schemas y ejecutar pruebas unitarias de serialización y mapeo.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-004-T02 - Implementar endpoint público de perfil de sucursal
  Capa: backend
  Objetivo: Exponer `GET /api/v1/clinics/branches/{branch_id}` con datos públicos seguros.
  Depende de: BE-004-T01
  Entregables: Router bajo `backend/app/api/v1`; caso de uso en `backend/app/application`; repositorio en `backend/app/domain/repositories` e implementación en infraestructura.
  Criterios de aceptacion: El endpoint no requiere autenticación; devuelve solo datos públicos; sucursal inexistente devuelve `404`; errores no filtran detalles internos.
  Validacion: `python -m pytest backend/app/tests -q` o suite específica del endpoint público.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-004-T03 - Implementar endpoint protegido y controles IDOR/BOLA
  Capa: backend
  Objetivo: Exponer `GET /api/v1/clinics/{clinic_id}/{branch_id}` con autenticación, ownership y permisos.
  Depende de: BE-004-T01, BE-004-T02
  Entregables: Dependencias de autenticación/autorización; caso de uso protegido; pruebas de `401`, `403`, `404` e IDOR/BOLA.
  Criterios de aceptacion: Sin token devuelve `401`; usuario sin acceso devuelve `403`; branch que no pertenece a clinic devuelve `404` o `403` seguro; no se devuelve información protegida en casos no autorizados.
  Validacion: `python -m pytest backend/app/tests/api -q` con casos de permisos.
  Evidencia: pending (pytest collection FAIL — import path rotas)
  Paralelismo[P]: No

### Frontend

- [ ] FE-004-T01 - Alinear cliente API y tipos con perfil público
  Capa: frontend
  Objetivo: Extender el cliente y los tipos frontend para consumir listado, detalle de clínica y perfil público/protegido de sucursal.
  Depende de: BE-004-T02
  Entregables: `frontend/src/shared/api/branch-client.ts`; `frontend/src/shared/api/branch-client-protected.ts`; `frontend/src/shared/api/types.ts`.
  Criterios de aceptacion: El cliente expone métodos para listado, detalle y perfil público/protegido de sucursal; los tipos incluyen servicios, horarios, rating summary y disponibilidad básica; los errores HTTP se propagan de forma controlada con código numérico en `.status`.
  Validacion: `npm run typecheck` debe pasar sin errores TS antes de marcar como completado — FALLS actual (ERROR module resolution).
  Evidencia: pending (typecheck FAIL: 7 TS2307 errors in module paths)
  Paralelismo[P]: No

- [ ] FE-004-T02 - Completar UI pública de perfil y estados
  Capa: frontend
  Objetivo: Renderizar perfil público con datos de clínica/sucursal, servicios, horarios, rating summary, disponibilidad básica y CTA de cita.
  Depende de: FE-004-T01
  Entregables: `frontend/src/app/clinics/[id]/page.tsx`; `frontend/src/app/clinics/[clinicId]/branches/[branchId]/page.tsx`; componentes en `frontend/src/features/public-clinic-profile/BranchProfile.tsx` y `frontend/src/shared/ui/components/Loading,ErrorBanner,EmptyState`.
  Criterios de aceptacion: La UI muestra loading (spinner CSS), error con banner rojo y botón reintento, empty state svg, y success con datos completos; el CTA usa enlace funcional a /booking?branch=... (no #); la vista es responsive (grid sm/md); no muestra acciones privadas a usuarios públicos.
  Validacion: `npm run typecheck` debe pasar sin errores TS — FALLS actual (ERROR compile time errors).
  Evidencia: pending (typecheck FAIL: 7 module resolution errors in tsconfig paths)
  Paralelismo[P]: No

### QA

- [ ] QA-004-T01 - Validar contrato backend público y protegido
  Capa: qa
  Objetivo: Ejecutar validación reproducible de endpoints, permisos, errores e IDOR/BOLA del slice.
  Depende de: BE-004-T02, BE-004-T03
  Entregables: `docs/opencode/qa/QA-004-results.md`; `docs/opencode/qa/QA-004-findings.md` si hay hallazgos.
  Criterios de aceptacion: Happy path público aprobado; endpoint protegido cubre `401`, `403`, `404`; no hay exposición de datos sensibles; evidencia usa comandos actuales.
  Validacion: `python backend/scripts/validate_slice_plan.py QA-004 --stage qa`; suite backend específica.
  Evidencia: pending (PYTEST COLLECTION FAIL — import path rotas en test file)
  Paralelismo[P]: No

- [ ] QA-004-T02 - Validar UI, regresión y documentación de cierre
  Capa: qa
  Objetivo: Confirmar que el frontend y la documentación del slice reflejan el comportamiento real implementado.
  Depende de: FE-004-T01, FE-004-T02, QA-004-T01
  Entregables: Reporte QA actualizado; evidencias de frontend; lista de gaps o findings.
  Criterios de aceptacion: Listado/detalle muestran estados esperados; no hay enlaces `#`; responsive básico validado; reportes históricos stale quedan corregidos o reemplazados antes de reviews.
  Validacion: `run-checks.ps1` cuando QA backend y frontend estén listos.
  Evidencia: pending (typecheck FAIL)
  Paralelismo[P]: No

# Definition of Done

- [x] El plan canónico `BE-004-plan.md` valida como schema v2.
- [x] El gate previo de `QA-003` esta en formato aceptado por el validador antes de iniciar implementación.
- [ ] Backend implementa endpoints público y protegido bajo `/api/v1`.
- [ ] Frontend consume el contrato real desde `src/shared/api`.
- [ ] QA-004 se ejecuta con evidencia actual, no histórica.
- [ ] No quedan findings bloqueantes.
- [ ] Existen revisiones funcional, clean architecture y seguridad con `Decision: APPROVED`.
- [ ] Checks formales declaran `Decision: APPROVED`.
