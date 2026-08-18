# Contexto de tasks por slice MVP

## Uso

Este archivo complementa `docs/opencode/02_be_fe_qa_task_matrix.md` y los archivos
`docs/opencode/tasks/backend`, `docs/opencode/tasks/frontend` y `docs/opencode/tasks/qa`.

Cada task BE, FE y QA debe poder derivar de aqui:

- Titulo del slice.
- Descripcion funcional.
- Entregables esperados por capa.
- Criterios de aceptacion observables.
- Contexto minimo para no salir del MVP.

Reglas:

- El plan canonico `docs/opencode/plans/BE-00X-plan.md` debe convertir estos briefs en tareas atomicas con `Entregables`, `Criterios de aceptacion`, `Validacion` y `Resultado esperado`.
- Si el brief no alcanza para definir endpoint, permiso, entidad, flujo UI o criterio QA, registrar el gap en `Revision de gaps`.
- No agregar Stage 1, Stage 2 ni fuera de alcance al MVP sin decision explicita.

## Briefs MVP

| Slice | Titulo | Descripcion funcional | Entregables BE | Entregables FE | Criterios de aceptacion QA |
| --- | --- | --- | --- | --- | --- |
| 001 | Base tecnica y design system | Preparar la base verificable del monolito backend, frontend Next.js y reglas visuales compartidas. | Healthcheck, configuracion, estructura Clean Architecture, seed inicial de roles cuando aplique y pruebas de arranque. | App base, layout inicial, Tailwind local, componentes UI base, estados comunes y pruebas/configuracion frontend. | Backend y frontend arrancan; healthcheck responde; no hay dependencias CDN criticas; estructura base queda trazable. |
| 002 | Autenticacion y sesion | Permitir registro, login, logout, recuperacion de password y sesion segura para roles MVP. | Modelos/repositorios de usuario y sesion, hashing seguro, tokens, endpoints auth, validaciones y pruebas de seguridad. | Formularios de registro/login/recuperacion, manejo de sesion, errores 401/403, redirecciones y cliente API tipado. | Flujos auth pasan; credenciales invalidas fallan; tokens no se filtran; roles iniciales quedan aplicables. |
| 003 | Landing publica y busqueda | Permitir busqueda anonima de clinicas, sucursales y servicios con filtros publicos. | Endpoints publicos de busqueda, filtros, paginacion, DTOs publicos, repositorios y pruebas de listados. | Landing, buscador, filtros/chips, resultados, estados loading/error/empty/success y query params. | Busqueda anonima funciona; filtros y paginacion son consistentes; datos privados no se exponen; UI responde en mobile/desktop. |
| 004 | Perfil publico clinica/sucursal | Mostrar perfil publico de clinica o sucursal con servicios, horarios, rating y CTA de cita. | Endpoints publicos de perfil, servicios, horarios y rating summary con DTOs sin datos sensibles. | Ruta de perfil, secciones publicas, CTA de cita, estados de carga/error y componentes reutilizables. | Perfil renderiza datos publicos; IDs inexistentes devuelven error seguro; CTA navega al flujo correcto; no hay filtrado de datos internos. |
| 005 | Administracion de clinica y sucursales | Permitir a administradores crear y mantener datos basicos de clinica y sucursales. | CRUD protegido, ownership por clinica/sucursal, validaciones, auditoria cuando aplique y pruebas de permisos. | Pantallas y formularios de administracion, tablas/listados, estados de guardado y manejo 403/404/422. | Admin autorizado opera su clinica; acceso cruzado falla; validaciones muestran errores claros; cambios persisten. |
| 006 | Servicios, veterinarios y usuarios internos | Gestionar servicios, veterinarios y usuarios internos asociados a clinica/sucursal. | Entidades, repositorios y endpoints protegidos para servicios, veterinarios, usuarios internos y asignaciones. | Pantallas de gestion, formularios, listados, permisos visibles y cliente API para recursos internos. | CRUD autorizado pasa; usuarios sin permiso fallan; asignaciones respetan tenant/sucursal; UI no ofrece acciones indebidas. |
| 007 | Propietarios y mascotas | Registrar y consultar propietarios, mascotas e historial basico dentro del MVP. | Modelos y endpoints de propietarios/mascotas, ownership, busqueda interna y pruebas de acceso. | Portal o vistas de propietario, formularios de mascota, historial basico y estados vacios. | Propietario gestiona sus mascotas; clinica accede solo cuando corresponde; datos personales se protegen. |
| 008 | Solicitud y gestion de citas | Crear, confirmar, cancelar, reprogramar, marcar no-show y completar citas. | Modelo de cita, estados, disponibilidad basica, router FastAPI `backend/app/api/v1/routers/appointment_router.py`, schemas `backend/app/api/v1/schemas/appointment_schemas.py`, endpoints `/api/v1/appointments` y pruebas de estado/permisos. | Flujo de solicitud desde perfil, agenda propietario y agenda clinica en `frontend/src/app/portal/owner/appointments`, `frontend/src/app/portal/owner/appointments/new` y `frontend/src/app/clinic/appointments`, con consumo centralizado en `src/features/appointments` y `src/shared/api`. | Transiciones validas pasan; transiciones invalidas fallan; disponibilidad y permisos se respetan; la UI se valida en `http://localhost:3000` y la API en `http://localhost:8000/api/v1`. |
| 009 | Consulta medica basica | Registrar consulta basica asociada a cita completada y mascota. | Entidad de consulta, endpoints protegidos, reglas de cita completada, ownership clinica/mascota y pruebas. | Formulario de consulta, historial, detalle de consulta y estados de edicion/lectura. | Solo citas completadas aceptan consulta; veterinario autorizado registra; propietario ve lo permitido; datos clinicos no se filtran. |
| 010 | Recetas, tratamientos y recordatorios | Registrar recetas, tratamientos y recordatorios ligados a consultas medicas completadas. | Modelos y endpoints de receta/tratamiento/recordatorio, validaciones, permisos y pruebas. | Formularios y vistas asociadas a consulta, recordatorios visibles y estados de error. | Registros quedan ligados a consulta valida; acceso no autorizado falla; fechas y campos requeridos se validan. |
| 011 | Registro operativo de pagos de servicios | Registrar pagos operativos de servicios sin checkout, pasarela ni efectos fiscales. | Modelo y endpoints de registro de pago, metodo/estado/importe, relacion con cita/servicio y pruebas. | Pantallas/formularios de registro de pago, listado por periodo y estados de guardado/error. | Pago operativo se registra; no existe checkout online; importes invalidos fallan; permisos y alcance fiscal se respetan. |
| 012 | Calificaciones y comentarios | Permitir calificaciones y comentarios de propietarios, y respuesta basica de clinica. | Endpoints de rating/comentario, restricciones por propietario/servicio, moderacion basica si aplica y summary. | UI de calificacion, comentarios en perfil, respuesta clinica y estados de permisos. | Solo usuarios habilitados califican; rating summary se actualiza; contenido invalido se rechaza; datos sensibles no se exponen. |
| 013 | Notificaciones internas y correo | Soportar notificaciones internas y correo para eventos MVP relevantes. | Modelo de notificacion, proveedor de correo abstracto, eventos MVP y pruebas con mocks. | Centro/listado de notificaciones, badges/estados leido-no leido y manejo de errores. | Eventos generan notificacion esperada; correo se mockea en pruebas; no se loggean datos sensibles. |
| 014 | Soporte basico | Registrar solicitudes de soporte, categorias, estados y consulta por usuario/admin. | Entidad y endpoints de tickets, categorias, estados, ownership y pruebas. | Formulario de soporte, listado por usuario/admin, detalle y cambio de estado permitido. | Usuario crea y consulta sus tickets; admin gestiona; acceso cruzado falla; estados son consistentes. |
| 015 | Reportes operativos basicos | Mostrar reportes basicos de citas, servicios, mascotas, consultas, ratings y pagos por periodo. | Endpoints agregados por periodo, filtros, paginacion/limites y pruebas de permisos. | Pantallas de reportes, filtros, tablas/resumenes y estados de carga/sin datos. | Reportes calculan datos esperados; filtros funcionan; tenant se respeta; no hay datos de otras clinicas. |
| 016 | Administracion inicial del sistema | Operar administracion inicial de usuarios, clinicas, terminos, privacidad, soporte y reportes globales basicos. | Endpoints admin, roles/permisos, activacion/desactivacion, configuraciones basicas y pruebas. | Panel admin inicial, formularios/listados, permisos visibles y manejo de errores. | Solo admin sistema accede; acciones criticas quedan auditadas si aplica; cambios no rompen alcance MVP. |
| 017 | Hardening E2E MVP | Cerrar regresion vertical del MVP, seguridad, arquitectura, documentacion y checks finales. | Ajustes de hardening backend, cobertura faltante, rate limits/logs/permisos y evidencia. | Ajustes UI de regresion, accesibilidad, estados, errores y build limpio. | Flujo MVP completo pasa; findings criticos cerrados; checks y gates quedan aprobados; no se agrega alcance fuera del MVP. |

## Campos requeridos por task source

Cada archivo `BE-00X.md`, `FE-00X.md` y `QA-00X.md` debe conservar o derivar estos campos:

- `Titulo`: nombre estable del slice segun matriz.
- `Descripcion`: contexto funcional y usuario/rol principal.
- `Entregables`: artefactos concretos esperados para esa capa.
- `Criterios de aceptacion`: condiciones observables, medibles y verificables por QA.
- `Fuera de alcance`: exclusiones MVP aplicables.
- `Dependencias`: slices o contratos que deben existir antes de ejecutar.
- `Validacion`: comandos, inspecciones o evidencias esperadas.
