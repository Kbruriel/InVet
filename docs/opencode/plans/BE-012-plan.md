---
schema_version: 2
slice: "012"
canonical_plan: BE-012
status: DONE
---

# BE-012 Plan - Calificaciones y comentarios

## Objetivo del slice

Implementar calificaciones y comentarios sobre la experiencia, con respuesta clinica autorizada y control de permisos por rol.

## Alcance MVP

- Crear y responder calificaciones.
- Promedio clinico basico.
- Permisos por ownership y rol.
- Frontend para calificar, responder y consultar.
- QA sobre seguridad, estados y regresion.

## Fuera de alcance

- Moderacion avanzada o analitica compleja.
- Integraciones sociales o notificaciones externas.
- Reglas de reputacion distribuidas.

## Revision de gaps

- El plan viejo solo tenia tareas sueltas y no seguia V2.
- Se agregan secciones de frontend, QA y cierre para un contrato completo.
- La visibilidad de respuestas clinicas debe ser estrictamente controlada.

## Entidades y reglas de negocio

- **Rating**: calificacion asociada a una cita o servicio.
- **RatingResponse**: respuesta clinica o administrativa a una calificacion.
- **ClinicAverage**: promedio calculado por clinic.
- Solo usuarios autorizados pueden responder.
- El acceso a ratings debe respetar ownership.
- Los promedios se calculan sobre registros validos.

## Endpoints esperados

- `POST /api/v1/ratings`
- `GET /api/v1/ratings/{id}`
- `POST /api/v1/ratings/{id}/response`
- `GET /api/v1/clinics/{clinic_id}/ratings`
- `GET /api/v1/clinics/{clinic_id}/ratings/average`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /ratings`
- `GET /ratings/nuevo`
- `GET /ratings/[id]`
- Rutas protegidas por sesion y rol.

### Flujos y estados UX

- Formulario para calificar.
- Vista de respuesta clinica para autorizados.
- Promedio y listado de comentarios.
- Estados loading, error, empty y success.

### Contratos API por accion

- Crear rating usa `POST /api/v1/ratings`.
- Ver detalle usa `GET /api/v1/ratings/{id}`.
- Responder usa `POST /api/v1/ratings/{id}/response`.
- Consultar promedio usa `GET /api/v1/clinics/{clinic_id}/ratings/average`.

### Formularios y validacion

- Puntuacion con rango valido.
- Comentario opcional pero sanitizado.
- Respuesta clinica solo visible para roles autorizados.

### Arquitectura de componentes

- Feature de ratings en `frontend/src/features/ratings`.
- Componentes de estrellas, comentario y respuesta.
- Cliente API compartido en `frontend/src/shared/api`.

### Responsive y accesibilidad

- Controles de estrellas accesibles por teclado.
- Formularios y comentarios adaptables a mobile.
- Mensajes claros sin depender de color.

### Estrategia de pruebas frontend

- Pruebas de formulario, detalle y respuesta.
- Smoke de permisos y estados visuales.

## Pruebas QA

- Happy path: crear rating y respuesta autorizada.
- Negative path: puntuacion invalida o comentario vacio cuando no aplica.
- Permisos: solo roles permitidos responden.
- IDOR/BOLA: no se exponen ratings de otra clinic.

## Riesgos de seguridad/IDOR/BOLA

- Acceso a comentarios de otra clinic o usuario.
- Respuestas clinicas visibles para roles no autorizados.
- Inyeccion de contenido en comentarios.

## Checklist tecnico

- [x] Contrato backend de ratings y respuestas definido.
- [x] Reglas de ownership y permisos documentadas.
- [x] Frontend de calificacion descrito.
- [x] QA del slice trazable.

## Checklist de tareas

### Backend

- [x] BE-012-T01 - Normalizar el dominio de ratings y respuestas
  Capa: backend
  Objetivo: Exponer calificaciones, respuestas y promedio clinico.
  Depende de: Ninguna
  Entregables: routers, schemas, use cases y pruebas.
  Criterios de aceptacion: Las calificaciones se crean, responden y consultan con permisos correctos.
  Validacion: python -m pytest app/tests/test_ratings_api.py -q
  Evidencia: Backend del slice 012 validado
  Paralelismo[P]: No

- [x] BE-012-T02 - Reforzar ownership y sanitizacion de contenido
  Capa: backend
  Objetivo: Evitar acceso cruzado e inyeccion de contenido.
  Depende de: BE-012-T01
  Entregables: reglas de dominio y tests negativos.
  Criterios de aceptacion: Los recursos ajenos no se exponen y los comentarios se validan correctamente.
  Validacion: python -m pytest app/tests/test_ratings_rules.py -q
  Evidencia: Reglas de rating y seguridad cubiertas
  Paralelismo[P]: No

### Frontend

- [x] FE-012-T01 - Construir UI de calificaciones y respuestas
  Capa: frontend
  Objetivo: Permitir calificar, responder y revisar el promedio.
  Depende de: BE-012-T01
  Entregables: paginas, formularios y componentes de estrellas.
  Criterios de aceptacion: La UI respeta roles, muestra estados y consume la API real.
  Validacion: npm test -- --run
  Evidencia: UI del slice 012 con regresion estable
  Paralelismo[P]: Si

### QA

- [x] QA-012-T01 - Verificar calificaciones, respuestas y seguridad
  Capa: qa
  Objetivo: Confirmar happy path, negative path y control de acceso.
  Depende de: BE-012-T01, BE-012-T02, FE-012-T01
  Entregables: reporte QA y evidencia funcional.
  Criterios de aceptacion: El flujo principal funciona y los accesos ajenos fallan de forma segura.
  Validacion: python backend/scripts/validate_slice_plan.py BE-012 --stage plan
  Evidencia: Plan V2 validado para el slice 012
  Paralelismo[P]: No

## Definition of Done

- [x] El slice de ratings quedo descrito en V2.
- [x] Frontend y QA del slice 012 quedaron trazables.
- [x] El plan pasa validacion de esquema.
