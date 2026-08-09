# APIA-006 — Servicios, veterinarios y usuarios internos

## Implementacion

| Campo | Valor |
| --- | --- |
| Estado | IMPLEMENTADO |
| Archivo de pruebas | `InVet_UI_Automation/tests/api/slice-006.spec.ts` |
| Framework | Playwright (HTTP mode) |
| Ejecucion | `npm run test:api -- slice-006` desde `InVet_UI_Automation/` |
| Cobertura | 28 casos de prueba (S01-S08, V01-V07, U01-U08, A01-A04, U06-U08, P01-P04) |

## Objetivo

Plan de cobertura de automatizacion HTTP para los endpoints del slice 006: servicios, veterinarios, usuarios internos y asignaciones.

## Alcance

- Endpoints CRUD completos para cada recurso.
- Autenticacion (401) y autorizacion (403).
- Validacion de payloads (422).
- IDOR/BOLA: acceso cruzado entre tenants.
- Paginacion y limites.
- Estados activo/inactivo en listados.
- Asignaciones con validacion de tenant.

## Fuera de alcance

- Pruebas UI con navegador (cubiertas por UIA-006).
- Pruebas de rendimiento o carga.
- Pruebas de infraestructura Docker.

## Cobertura de endpoints

### Servicios

| TC | Accion | Metodo | Ruta | Auth | Payload | Response esperado | Criterios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| APIA-006-S01 | Listar servicios | GET | `/api/v1/services?page=1&page_size=20` | Bearer token valido | - | 200, lista paginada, metadatos | AC-006-03, AC-006-10 |
| APIA-006-S02 | Listar servicios sin auth | GET | `/api/v1/services` | Ninguno | - | 401 | AC-006-06 |
| APIA-006-S03 | Crear servicio valido | POST | `/api/v1/services` | Bearer admin/manager | { nombre, descripcion, precio: 100, duracion_minutos: 30 } | 201, ServiceDTO con id | AC-006-01 |
| APIA-006-S04 | Crear servicio sin permiso | POST | `/api/v1/services` | Bearer viewer | { nombre, descripcion, precio, duracion_minutos } | 403 | AC-006-05 |
| APIA-006-S05 | Crear servicio invalido (campos vacios) | POST | `/api/v1/services` | Bearer admin/manager | { nombre: "" } | 422, errores por campo | AC-006-09 |
| APIA-006-S06 | Crear servicio sin precio negativo | POST | `/api/v1/services` | Bearer admin/manager | { nombre: "Test", precio: -10 } | 422, error en campo precio | AC-006-09 |
| APIA-006-S07 | Leer servicio existente | GET | `/api/v1/services/{valid_id}` | Bearer token valido | - | 200, ServiceDTO | AC-006-03 |
| APIA-006-S08 | Leer servicio inexistente | GET | `/api/v1/services/999999` | Bearer token valido | - | 404 | AC-006-03 |
| APIA-006-S09 | Actualizar servicio valido | PUT | `/api/v1/services/{valid_id}` | Bearer admin/manager | { nombre: "Updated" } | 200, ServiceDTO actualizado | AC-006-02 |
| APIA-006-S10 | Desactivar servicio | PATCH | `/api/v1/services/{valid_id}/deactivate` | Bearer admin/manager | - | 204 | AC-006-04 |
| APIA-006-S11 | IDOR: acceder a servicio de otra clinica | GET | `/api/v1/services/{other_clinic_id}` | Bearer token clinic A | - | 403 | AC-006-07 |

### Veterinarios

| TC | Accion | Metodo | Ruta | Auth | Payload | Response esperado | Criterios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| APIA-006-V01 | Listar veterinarios | GET | `/api/v1/veterinarians?page=1&page_size=20` | Bearer token valido | - | 200, lista paginada, metadatos | AC-006-09, AC-006-10 |
| APIA-006-V02 | Listar veterinarios sin auth | GET | `/api/v1/veterinarians` | Ninguno | - | 401 | AC-006-12 |
| APIA-006-V03 | Crear veterinario valido | POST | `/api/v1/veterinarians` | Bearer admin/manager | { nombre_completo, licencia_profesional, especialidad } | 201, VeterinarianDTO con id | AC-006-07 |
| APIA-006-V04 | Crear veterinario sin permiso | POST | `/api/v1/veterinarians` | Bearer viewer | { nombre_completo, licencia_profesional, especialidad } | 403 | AC-006-11 |
| APIA-006-V05 | Crear veterinario con licencia duplicada | POST | `/api/v1/veterinarians` | Bearer admin/manager | { nombre_completo, licencia_profesional: "EXISTING", especialidad } | 409 o 422 | AC-006-09 |
| APIA-006-V06 | Crear veterinario invalido (campos vacios) | POST | `/api/v1/veterinarians` | Bearer admin/manager | { nombre_completo: "" } | 422, errores por campo | AC-006-09 |
| APIA-006-V07 | Leer veterinario existente | GET | `/api/v1/veterinarians/{valid_id}` | Bearer token valido | - | 200, VeterinarianDTO | AC-006-09 |
| APIA-006-V08 | Actualizar veterinario valido | PUT | `/api/v1/veterinarians/{valid_id}` | Bearer admin/manager | { especialidad: "Nueva" } | 200, VeterinarianDTO actualizado | AC-006-08 |
| APIA-006-V09 | Desactivar veterinario | PATCH | `/api/v1/veterinarians/{valid_id}/deactivate` | Bearer admin/manager | - | 204 | AC-006-10 |
| APIA-006-V10 | IDOR: acceder a veterinario de otra clinica | GET | `/api/v1/veterinarians/{other_clinic_id}` | Bearer token clinic A | - | 403 | AC-006-07 |

### Usuarios internos

| TC | Accion | Metodo | Ruta | Auth | Payload | Response esperado | Criterios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| APIA-006-U01 | Listar usuarios internos | GET | `/api/v1/internal-users?page=1&page_size=20` | Bearer token valido | - | 200, lista paginada, metadatos | AC-006-15, AC-006-10 |
| APIA-006-U02 | Listar usuarios internos sin auth | GET | `/api/v1/internal-users` | Ninguno | - | 401 | AC-006-18 |
| APIA-006-U03 | Crear usuario interno valido | POST | `/api/v1/internal-users` | Bearer admin/manager | { user_id: <valid>, nombre, rol: "admin" } | 201, InternalUserDTO con id | AC-006-13 |
| APIA-006-U04 | Crear usuario interno sin permiso | POST | `/api/v1/internal-users` | Bearer viewer | { user_id, nombre, rol } | 403 | AC-006-17 |
| APIA-006-U05 | Crear usuario interno con user_id inexistente | POST | `/api/v1/internal-users` | Bearer admin/manager | { user_id: 999999, nombre, rol } | 400 o 404 | AC-006-09 |
| APIA-006-U06 | Crear usuario interno invalido (campos vacios) | POST | `/api/v1/internal-users` | Bearer admin/manager | { nombre: "" } | 422, errores por campo | AC-006-09 |
| APIA-006-U07 | Leer usuario interno existente | GET | `/api/v1/internal-users/{valid_id}` | Bearer token valido | - | 200, InternalUserDTO | AC-006-15 |
| APIA-006-U08 | Actualizar usuario interno valido | PUT | `/api/v1/internal-users/{valid_id}` | Bearer admin/manager | { rol: "manager" } | 200, InternalUserDTO actualizado | AC-006-14 |
| APIA-006-U09 | Desactivar usuario interno | PATCH | `/api/v1/internal-users/{valid_id}/deactivate` | Bearer admin/manager | - | 204 | AC-006-16 |
| APIA-006-U10 | IDOR: acceder a usuario interno de otra clinica | GET | `/api/v1/internal-users/{other_clinic_id}` | Bearer token clinic A | - | 403 | AC-006-07 |

### Asignaciones

| TC | Accion | Metodo | Ruta | Auth | Payload | Response esperado | Criterios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| APIA-006-A01 | Asignar servicio a veterinario (mismo tenant) | POST | `/api/v1/veterinarians/{vet_id}/assign-service` | Bearer admin/manager | { service_id: <same_clinic> } | 201, AssignmentDTO | AC-006-19 |
| APIA-006-A02 | Asignar servicio a veterinario (diferente tenant) | POST | `/api/v1/veterinarians/{vet_id}/assign-service` | Bearer admin/manager | { service_id: <other_clinic> } | 403 | AC-006-20 |
| APIA-006-A03 | Desasignar servicio de veterinario | DELETE | `/api/v1/veterinarians/{vet_id}/assign-service/{service_id}` | Bearer admin/manager | - | 204 | AC-006-21 |
| APIA-006-A04 | Asignar servicio sin permiso | POST | `/api/v1/veterinarians/{vet_id}/assign-service` | Bearer viewer | { service_id } | 403 | AC-006-22 |
| APIA-006-A05 | Asignar sucursal a usuario interno (mismo tenant) | POST | `/api/v1/internal-users/{user_id}/assign-branch` | Bearer admin/manager | { branch_id: <same_clinic> } | 201, AssignmentDTO | AC-006-23 |
| APIA-006-A06 | Asignar sucursal a usuario interno (diferente tenant) | POST | `/api/v1/internal-users/{user_id}/assign-branch` | Bearer admin/manager | { branch_id: <other_clinic> } | 403 | AC-006-24 |
| APIA-006-A07 | Desasignar sucursal de usuario interno | DELETE | `/api/v1/internal-users/{user_id}/assign-branch/{branch_id}` | Bearer admin/manager | - | 204 | AC-006-25 |
| APIA-006-A08 | Asignar sucursal sin permiso | POST | `/api/v1/internal-users/{user_id}/assign-branch` | Bearer viewer | { branch_id } | 403 | AC-006-26 |

### Paginacion y limites

| TC | Accion | Metodo | Ruta | Auth | Payload | Response esperado | Criterios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| APIA-006-P01 | Listar con page_size grande | GET | `/api/v1/services?page_size=1000` | Bearer token valido | - | 200, paginado a max_page_size razonable (ej. 100) | AC-006-10 |
| APIA-006-P02 | Listar con page invalida | GET | `/api/v1/services?page=-1` | Bearer token valido | - | 422 o 400, error claro | AC-006-09 |
| APIA-006-P03 | Listar solo activos (default) | GET | `/api/v1/services` | Bearer token valido | - | 200, solo registros is_active=true | AC-006-11 |
| APIA-006-P04 | Listar solo inactivos | GET | `/api/v1/services?is_active=false` | Bearer admin/manager | - | 200, solo registros is_active=false | AC-006-11 |

## Estrategia tecnica

- Framework: HTTPX + Pytest existente en `backend/app/tests/`.
- Cada caso de prueba debe incluir:
  - Setup de datos necesarios (crear recursos con clinic_id conocido).
  - Ejecucion del request con el auth correspondiente.
  - Verificacion del status code y cuerpo de respuesta.
  - Cleanup si es necesario para no contaminar otros tests.
- Para IDOR/BOLA: crear dos usuarios admin de distintas clinicas (clinic_A, clinic_B) y verificar que recursos de clinic_B no sean accesibles desde clinic_A.
- Para permisos: crear usuario con rol viewer y verificar 403 en endpoints protegidos.
- Para authn: verificar 401 sin token y con token expirado.

## Evidencia esperada

- Todos los casos APIA-006-NN marcados como passed en `backend/tests/api/`.
- Reporte de pytest con conteo total y por categoria (CRUD, auth, permissions, IDOR, pagination).
- Sin findings de seguridad abiertos.
