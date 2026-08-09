# APIA-005 - Pruebas de API: Administración de clínica y sucursales

## Objetivo

Validar mediante pruebas HTTP los endpoints CRUD del slice BE-005.

## Dependencias

- Backend BE-005 en ejecución con datos de prueba.
- Autenticación BE-002 configurada.

## Alcance

- Happy path de todos los endpoints CRUD.
- Negative paths (input inválido, permisos insuficientes).
- IDOR/BOLA validation.
- Paginación y filtros.
- Consistencia de respuestas HTTP.

## Casos de prueba

### TC-005-A01 - POST /api/v1/clinics (crear clínica)
- Dado que soy un usuario con rol `clinic_admin`
- Cuando envío POST con body válido
- Entonces recibo 201 con ClinicDTO
- Y la clínica existe en la base de datos

### TC-005-A02 - POST /api/v1/clinics (sin auth)
- Dado que no estoy autenticado
- Cuando envío POST a /api/v1/clinics
- Entonces recibo 401

### TC-005-A03 - POST /api/v1/clinics (sin rol admin)
- Dado que soy un usuario con rol regular
- Cuando envío POST a /api/v1/clinics
- Entonces recibo 403

### TC-005-A04 - POST /api/v1/clinics (duplicado)
- Dado que existe una clínica con ese RFC
- Cuando envío POST con RFC duplicado
- Entonces recibo 409 Conflict

### TC-005-A05 - PUT /api/v1/clinics/{clinic_id} (actualizar)
- Dado que soy owner/admin de la clínica
- Cuando envío PUT con datos válidos
- Entonces recibo 200 con ClinicDTO actualizado

### TC-005-A06 - PATCH /api/v1/clinics/{clinic_id}/status (inactivar)
- Dado que soy admin de la clínica
- Cuando envío PATCH con {active: false}
- Entonces recibo 200 y la clínica está inactiva

### TC-005-A07 - GET /api/v1/clinics (listar paginado)
- Dado que estoy autenticado como admin
- Cuando envío GET con page=1&limit=20
- Entonces recibo 200 con PaginatedClinicDTO
- Y el total coincide con el conteo real

### TC-005-A08 - POST /api/v1/clinics/{clinic_id}/branches (crear sucursal)
- Dado que soy owner/admin de la clínica
- Cuando envío POST con body válido
- Entonces recibo 201 con BranchDTO
- Y la sucursal tiene clinic_id correcto

### TC-005-A09 - PUT /api/v1/branches/{branch_id} (actualizar)
- Dado que soy owner/admin de la sucursal
- Cuando envío PUT con datos válidos
- Entonces recibo 200 con BranchDTO actualizado

### TC-005-A10 - CRUD /api/v1/branches/{branch_id}/schedules
- Dado que soy owner/admin de la sucursal
- Cuando creo, actualizo y elimino horarios
- Entonces cada operación responde correctamente
- Y los horarios no se solapan para el mismo día

### TC-005-A11 - PUT /api/v1/branches/{branch_id}/contact-location
- Dado que soy owner/admin de la sucursal
- Cuando envío PUT con contacto y coordenadas válidas
- Entonces recibo 200 con datos actualizados

### TC-005-A12 - IDOR: Acceso cruzado por clinic_id
- Dado que soy admin de la clínica A
- Cuando intento acceder a recursos de la clínica B
- Entonces recibo 403 en todos los endpoints

### TC-005-A13 - Input inválido (400/422)
- Dado que estoy autenticado como admin
- Cuando envío requests con datos inválidos (email, teléfono, coordenadas)
- Entonces recibo 400 o 422 con mensajes de error claros

### TC-005-A14 - GET /api/v1/clinics/{invalid_id} (404)
- Dado que estoy autenticado como admin
- Cuando envío GET con un ID inexistente
- Entonces recibo 404 sin datos internos en la respuesta

## Evidencia requerida

- Comandos curl o scripts de prueba ejecutados.
- Status codes esperados vs obtenidos.
- Payloads de request/response.
- Resultados: PASS o FAIL con descripción del defecto.
