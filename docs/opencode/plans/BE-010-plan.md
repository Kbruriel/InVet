---
schema_version: 2
slice: "010"
canonical_plan: BE-010
status: DONE
---

# BE-010 Plan - Recetas, tratamientos y recordatorios

## Objetivo del slice

Implementar el registro de recetas medicas, tratamientos asociados y recordatorios para dueños de mascotas vinculados a una consulta ya realizada.

## Alcance MVP

- Crear, consultar y relacionar recetas, tratamientos y recordatorios.
- Asociacion a consulta medica y mascota.
- Permisos para staff veterinario y visualizacion para dueños cuando aplique.
- Frontend para crear prescripciones y consultar historial.
- QA sobre flujo completo, ownership y seguridad.

## Fuera de alcance

- PDFs legales o plantillas de impresion final.
- Integraciones de SMS, WhatsApp o notificaciones push en tiempo real.
- Marketplace o venta de medicamentos.

## Revision de gaps

- El plan tenia contenido extenso pero no seguia V2.
- Se normalizan endpoints, frontend, QA y criterios de cierre.
- Los recordatorios quedan como persistencia base para una etapa posterior de notificacion.

## Entidades y reglas de negocio

- **Receta**: vinculada a una consulta y con instrucciones generales.
- **Tratamiento**: vinculado a una receta o consulta y con duracion/dosificacion.
- **Recordatorio**: ligado a una receta o tratamiento con fecha, hora y estado.
- Solo el staff autorizado puede crear o editar recetas.
- Los dueños pueden ver, pero no editar.

## Endpoints esperados

- `POST /api/v1/consultas/{consulta_id}/recetas`
- `GET /api/v1/consultas/{consulta_id}/recetas`
- `GET /api/v1/recetas/{receta_id}`
- `POST /api/v1/recetas/{receta_id}/tratamientos`
- `POST /api/v1/recetas/{receta_id}/recordatorios`
- `GET /api/v1/staff/mis-recordatorios`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /consultas/[id]/prescripciones`
- `GET /recetas/[id]`
- Rutas protegidas para staff autorizado.

### Flujos y estados UX

- Formulario de receta.
- Lista de tratamientos dentro de una receta.
- Selector de recordatorio.
- Estados loading, error, empty y success.

### Contratos API por accion

- Crear receta usa `POST /api/v1/consultas/{consulta_id}/recetas`.
- Agregar tratamiento usa `POST /api/v1/recetas/{receta_id}/tratamientos`.
- Programar recordatorio usa `POST /api/v1/recetas/{receta_id}/recordatorios`.
- Consultar historial usa `GET /api/v1/consultas/{consulta_id}/recetas`.

### Formularios y validacion

- Consulta y mascota requeridas.
- Campos de dosificacion y fecha con validacion estricta.
- Mensajes claros si el usuario no tiene permiso.

### Arquitectura de componentes

- Feature clinica en `frontend/src/features/prescriptions`.
- Componentes de detalle, lista y selector de fecha.
- Cliente API compartido en `frontend/src/shared/api`.

### Responsive y accesibilidad

- Formularios y paneles adaptables a mobile.
- Interaccion por teclado y labels correctos.
- Errores visibles sin depender de color solamente.

### Estrategia de pruebas frontend

- Pruebas de formulario, lista y detalle.
- Smoke de permisos y flujo de prescripcion.

## Pruebas QA

- Happy path: crear receta, tratamiento y recordatorio.
- Negative path: consulta inexistente o acceso de otra clinic.
- Permisos: solo staff autorizado crea o edita.
- IDOR/BOLA: no se muestran recetas ajenas.

## Riesgos de seguridad/IDOR/BOLA

- Acceso a recetas de otra clinic.
- Dosificacion o instrucciones con contenido malicioso.
- Fuga de datos sensibles en respuestas de error.

## Checklist tecnico

- [x] Contrato backend de recetas, tratamientos y recordatorios definido.
- [x] Reglas de ownership y seguridad documentadas.
- [x] Frontend de prescripciones descrito.
- [x] QA del slice trazable.

## Checklist de tareas

### Backend

- [x] BE-010-T01 - Normalizar el flujo de prescripciones
  Capa: backend
  Objetivo: Exponer recetas, tratamientos y recordatorios de forma segura.
  Depende de: Ninguna
  Entregables: routers, schemas, casos de uso y pruebas.
  Criterios de aceptacion: El flujo completo se relaciona con una consulta y respeta permisos.
  Validacion: python -m pytest app/tests/test_prescriptions_api.py -q
  Evidencia: Backend del slice 010 validado
  Paralelismo[P]: No

- [x] BE-010-T02 - Reforzar ownership y validacion de instrucciones
  Capa: backend
  Objetivo: Evitar acceso cruzado y contenido invalido.
  Depende de: BE-010-T01
  Entregables: validaciones de dominio y tests negativos.
  Criterios de aceptacion: Las recetas ajenas no son accesibles y los campos de dosificacion se validan.
  Validacion: python -m pytest app/tests/test_prescriptions_rules.py -q
  Evidencia: Reglas clinicas y seguridad cubiertas
  Paralelismo[P]: No

### Frontend

- [x] FE-010-T01 - Construir UI de recetas y recordatorios
  Capa: frontend
  Objetivo: Permitir gestionar prescripciones desde la UI.
  Depende de: BE-010-T01
  Entregables: paginas, formularios y componentes de detalle.
  Criterios de aceptacion: La UI maneja estados y consume la API real.
  Validacion: npm test -- --run
  Evidencia: UI del slice 010 con regresion estable
  Paralelismo[P]: Si

### QA

- [x] QA-010-T01 - Verificar flujo completo de prescripciones
  Capa: qa
  Objetivo: Confirmar happy path, negative path y seguridad.
  Depende de: BE-010-T01, BE-010-T02, FE-010-T01
  Entregables: reporte QA y evidencia funcional.
  Criterios de aceptacion: El flujo completo es reproducible y las rutas ajenas fallan de forma segura.
  Validacion: python backend/scripts/validate_slice_plan.py BE-010 --stage plan
  Evidencia: Plan V2 validado para el slice 010
  Paralelismo[P]: No

## Definition of Done

- [x] El flujo de prescripciones quedo descrito en V2.
- [x] Frontend y QA del slice 010 quedaron trazables.
- [x] El plan pasa validacion de esquema.
