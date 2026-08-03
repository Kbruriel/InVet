---
schema_version: 2
slice: "009"
canonical_plan: BE-009
status: DONE
---

# BE-009 Plan - Consulta medica basica

## Objetivo del slice

Implementar el registro de consultas medicas asociadas a citas completadas y mascotas, con control de permisos por rol veterinario.

## Alcance MVP

- Crear y consultar consultas medicas.
- Asociacion obligatoria a cita completada y mascota.
- Control de acceso por rol y ownership.
- Frontend para captura y consulta historica.
- QA con permisos, errores y seguridad.

## Fuera de alcance

- Flujo clinico avanzado, diagnosticos asistidos o analitica.
- Edicion masiva o versionado complejo.
- Integraciones externas de historico medico.

## Revision de gaps

- El plan estaba definido, pero faltaba el formato V2 completo.
- Se aclara que la consulta debe ser inmutable salvo correcciones permitidas.
- La UI solo puede mostrar acciones si el rol lo autoriza.

## Entidades y reglas de negocio

- **ConsultaMedica**: cita, mascota, veterinario, fecha, diagnostico y tratamiento.
- Solo puede existir sobre una cita completada.
- Solo veterinarios pueden crear consultas.
- Propietario o veterinario de la mascota pueden visualizar.
- Las consultas son inmutables salvo correccion autorizada.

## Endpoints esperados

- `POST /api/v1/consultas`
- `GET /api/v1/consultas/{id}`
- `GET /api/v1/mascotas/{mascota_id}/consultas`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /consultas`
- `GET /consultas/nueva`
- `GET /consultas/[id]`
- Acceso limitado por rol veterinario y ownership.

### Flujos y estados UX

- Formulario para registrar consulta.
- Vista detalle de consulta.
- Lista historica por mascota.
- Estados loading, error, empty y success.

### Contratos API por accion

- Crear usa `POST /api/v1/consultas`.
- Detalle usa `GET /api/v1/consultas/{id}`.
- Historico usa `GET /api/v1/mascotas/{mascota_id}/consultas`.

### Formularios y validacion

- Cita completada y mascota requeridas.
- Diagnostico y tratamiento validados.
- Error claro si el rol no es veterinario.

### Arquitectura de componentes

- Feature clinica en `frontend/src/features/consultas`.
- Cliente API compartido en `frontend/src/shared/api`.
- Componentes reutilizables de detalle e historial.

### Responsive y accesibilidad

- Formularios y vistas legibles en mobile.
- Estados vacio y error accesibles.
- Navegacion clara entre mascota y consulta.

### Estrategia de pruebas frontend

- Pruebas de formulario, detalle e historial.
- Smoke de permisos y navegacion.

## Pruebas QA

- Happy path: crear consulta correctamente.
- Negative path: datos invalidos o cita inexistente.
- Permisos: veterinario puede crear, otros roles no.
- IDOR/BOLA: no se exponen consultas ajenas.

## Riesgos de seguridad/IDOR/BOLA

- Acceso a consultas de mascotas ajenas.
- Fugas de informacion sensible en errores.
- Permisos mal definidos por rol o tenant.

## Checklist tecnico

- [x] Contrato backend de consultas definido.
- [x] Reglas de permisos y ownership documentadas.
- [x] Frontend clinico base descrito.
- [x] QA del slice trazable.

## Checklist de tareas

### Backend

- [x] BE-009-T01 - Normalizar el CRUD de consulta medica
  Capa: backend
  Objetivo: Exponer el registro y consulta de consultas medicas.
  Depende de: Ninguna
  Entregables: routers, schemas, casos de uso y pruebas.
  Criterios de aceptacion: Se valida cita completada, mascota y rol veterinario antes de crear.
  Validacion: python -m pytest app/tests/test_consulta_medica_api.py -q
  Evidencia: Backend del slice 009 validado
  Paralelismo[P]: No

- [x] BE-009-T02 - Reforzar permisos e inmutabilidad clinica
  Capa: backend
  Objetivo: Evitar accesos cruzados y ediciones no autorizadas.
  Depende de: BE-009-T01
  Entregables: validaciones de dominio y tests de acceso.
  Criterios de aceptacion: Solo veterinarios crean consultas y el acceso a recursos ajenos es bloqueado.
  Validacion: python -m pytest app/tests/test_consulta_medica_rules.py -q
  Evidencia: Reglas de consulta y permisos cubiertas
  Paralelismo[P]: No

### Frontend

- [x] FE-009-T01 - Construir UI de consulta medica e historico
  Capa: frontend
  Objetivo: Permitir capturar y revisar consultas medicas.
  Depende de: BE-009-T01
  Entregables: paginas, formularios, detalle e historial por mascota.
  Criterios de aceptacion: La UI consume la API real y respeta permisos por rol.
  Validacion: npm test -- --run
  Evidencia: UI del slice 009 con regresion estable
  Paralelismo[P]: Si

### QA

- [x] QA-009-T01 - Verificar consulta medica con seguridad
  Capa: qa
  Objetivo: Confirmar happy path, negative path y control de acceso.
  Depende de: BE-009-T01, BE-009-T02, FE-009-T01
  Entregables: reporte QA y evidencia funcional.
  Criterios de aceptacion: La consulta se crea solo con permisos y los recursos ajenos no son visibles.
  Validacion: python backend/scripts/validate_slice_plan.py BE-009 --stage plan
  Evidencia: Plan V2 validado para el slice 009
  Paralelismo[P]: No

## Definition of Done

- [x] Consulta medica descrita en V2 con contratos completos.
- [x] Frontend y QA del slice 009 quedaron trazables.
- [x] El plan pasa validacion de esquema.
