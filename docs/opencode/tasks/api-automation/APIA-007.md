# APIA-007 — Pruebas de API Automation para Propietarios y Mascotas

## Objetivo

Automatizar la validacion de los endpoints de propietarios y mascotas, cubriendo autenticacion, authorization, ownership, IDOR/BOLA, validacion de datos y paginacion.

## Endpoints a cubrir

| Accion | Metodo | Ruta | Auth esperado |
| --- | --- | --- | --- |
| Crear perfil owner | POST | `/api/v1/owners` | Bearer (propietario) |
| Obtener perfil propio | GET | `/api/v1/owners/me` | Bearer (propietario) |
| Actualizar perfil propio | PUT | `/api/v1/owners/me` | Bearer (propietario) |
| Listar mascotas | GET | `/api/v1/owners/me/pets` | Bearer (propietario) |
| Registrar mascota | POST | `/api/v1/owners/me/pets` | Bearer (propietario) |
| Obtener mascota | GET | `/api/v1/pets/{pet_id}` | Bearer (propietario/clinica) |
| Actualizar mascota | PUT | `/api/v1/pets/{pet_id}` | Bearer (propietario del pet) |
| Eliminar mascota | DELETE | `/api/v1/pets/{pet_id}` | Bearer (propietario del pet) |
| Historial basico | GET | `/api/v1/pets/{pet_id}/history` | Bearer (propietario/clinica autorizada) |

## Casos de prueba

### Authn — Autenticacion

| ID | Descripcion | Metodo | Ruta | Esperado |
| --- | --- | --- | --- | --- |
| APIA-007-01 | Sin token en endpoint protegido | GET | `/api/v1/owners/me` | 401 |
| APIA-007-02 | Token expirado | GET | `/api/v1/owners/me` | 401 |
| APIA-007-03 | Token invalido | GET | `/api/v1/owners/me` | 401 |

### Authz — Authorization y Ownership

| ID | Descripcion | Metodo | Ruta | Esperado |
| --- | --- | --- | --- | --- |
| APIA-007-04 | Owner crea su perfil | POST | `/api/v1/owners` | 201 con datos del owner |
| APIA-007-05 | Owner actualiza su perfil | PUT | `/api/v1/owners/me` | 200 con datos actualizados |
| APIA-007-06 | Owner registra mascota propia | POST | `/api/v1/owners/me/pets` | 201 con pet.owner_id = user_id |
| APIA-007-07 | Owner lista sus mascotas | GET | `/api/v1/owners/me/pets` | 200 con solo sus mascotas |
| APIA-007-08 | Owner actualiza su mascota | PUT | `/api/v1/pets/{own_pet_id}` | 200 |
| APIA-007-09 | Owner elimina su mascota | DELETE | `/api/v1/pets/{own_pet_id}` | 204 |

### IDOR / BOLA — Acceso cruzado

| ID | Descripcion | Metodo | Ruta | Esperado |
| --- | --- | --- | --- | --- |
| APIA-007-10 | Owner A accede a perfil de Owner B | GET | `/api/v1/owners/{other_owner_id}` | 403 o 404 |
| APIA-007-11 | Owner A accede a mascota de Owner B | GET | `/api/v1/pets/{other_pet_id}` | 403 o 404 |
| APIA-007-12 | Owner A actualiza mascota de Owner B | PUT | `/api/v1/pets/{other_pet_id}` | 403 o 404 |
| APIA-007-13 | Owner A elimina mascota de Owner B | DELETE | `/api/v1/pets/{other_pet_id}` | 403 o 404 |
| APIA-007-14 | Clinica accede a owner no asignado | GET | `/api/v1/owners/{random_owner_id}` | 403 o 404 |

### Validacion de datos

| ID | Descripcion | Metodo | Ruta | Esperado |
| --- | --- | --- | --- | --- |
| APIA-007-15 | Nombre vacio en registro de mascota | POST | `/api/v1/owners/me/pets` con `{especie: "perro"}` | 422 |
| APIA-007-16 | Especie invalida en registro de mascota | POST | `/api/v1/owners/me/pets` con `{nombre: "Max", especie: "xyz"}` | 422 |
| APIA-007-17 | Edad negativa en registro de mascota | POST | `/api/v1/owners/me/pets` con `{edad: -1}` | 422 |
| APIA-007-18 | Email invalido en creacion de owner | POST | `/api/v1/owners` con `{email: "invalido"}` | 422 |
| APIA-007-19 | Pet ID inexistente | GET | `/api/v1/pets/{nonexistent_id}` | 404 |

### Paginacion

| ID | Descripcion | Metodo | Ruta | Esperado |
| --- | --- | --- | --- | --- |
| APIA-007-20 | Listado con page=1, page_size=10 | GET | `/api/v1/owners/me/pets?page=1&page_size=10` | 200, items.length <= 10, meta.total correcto |
| APIA-007-21 | Listado con page=2 | GET | `/api/v1/owners/me/pets?page=2&page_size=10` | 200, items sin duplicados con page=1 |
| APIA-007-22 | page_size negativo | GET | `/api/v1/owners/me/pets?page_size=-1` | 422 o 400 |

### Historial basico

| ID | Descripcion | Metodo | Ruta | Esperado |
| --- | --- | --- | --- | --- |
| APIA-007-23 | Historial con registros | GET | `/api/v1/pets/{pet_with_history}/history` | 200, items con datos de consultas |
| APIA-007-24 | Historial sin registros | GET | `/api/v1/pets/{pet_no_history}/history` | 200, items vacio [] |

## Payloads de prueba

### Crear owner (POST /api/v1/owners)
```json
{
  "nombre": "Juan Perez",
  "email": "juan@ejemplo.com",
  "telefono": "555-1234",
  "direccion": "Calle 123, Ciudad"
}
```

### Registrar mascota (POST /api/v1/owners/me/pets)
```json
{
  "nombre": "Max",
  "especie": "perro",
  "raza": "Labrador",
  "edad": 5,
  "peso": 28.5,
  "fecha_nacimiento": "2021-01-15"
}
```

### Actualizar mascota (PUT /api/v1/pets/{id})
```json
{
  "nombre": "Max actualizado",
  "peso": 30.0
}
```

## Errores esperados por endpoint

| Endpoint | 400 | 401 | 403 | 404 | 422 |
| --- | --- | --- | --- | --- | --- |
| POST /owners | X | X | — | — | X |
| GET /owners/me | — | X | — | X | — |
| PUT /owners/me | X | X | X | — | X |
| GET /owners/me/pets | — | X | — | X | — |
| POST /owners/me/pets | X | X | X | — | X |
| GET /pets/{id} | — | X | X | X | — |
| PUT /pets/{id} | X | X | X | X | X |
| DELETE /pets/{id} | — | X | X | X | — |
| GET /pets/{id}/history | — | X | X | X | — |

## Comando de ejecucion

```bash
cd InVet_UI_Automation
npx playwright test tests/api/test_owners_api.spec.ts tests/api/test_pets_api.spec.ts --reporter=html
```

## Criterios de salida

- Todos los casos APIA-007-NN pasan o tienen findings documentados.
- No hay endpoints que respondan con 500 en flujos validos.
- IDOR/BOLA siempre fallan con 403 o 404, nunca con datos expuestos.
- Paginacion consistente: no duplicados, no saltos, meta correcto.
- Errores de validacion claros y sin informacion interna del sistema.
