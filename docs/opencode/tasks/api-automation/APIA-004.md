# APIA-004 - API Automation for Public Clinic/Branch Profile

## Metadata

| Campo | Valor |
|---|---|
| ID | APIA-004 |
| Slice vertical | BE-004 / FE-004 / QA-004 |
| Capa | Backend/API |
| Estado | READY_FOR_EXECUTION |
| Framework | Playwright APIRequestContext |

## Alcance MVP

- Validar endpoint público de perfil de sucursal sin autenticación.
- Validar endpoint protegido con validación de acceso (401/403).
- Confirmar que el DTO público no expone campos sensibles.
- Verificar IDOR/BOLA: datos privados no se exponen en endpoints protegidos.
- Comprobar errores 404 para IDs inexistentes sin filtrado de información interna.
- Validar estructura de respuestas DTOs públicos (sin ORM models expuestos).

## Fuera de alcance

- Pruebas de carga o rendimiento.
- Endpoints separados de servicios/horarios/rating/availability (van embebidos en el perfil).
- Pruebas de autenticación/autorización detalladas (solo validación básica 401/403).
- Validación detallada de schemas response complejos más allá de campos clave.

## Endpoints BE-004

| Ruta | Auth | Descripción |
|---|---|---|
| GET /api/v1/clinics/branches/{branch_id} | Ninguna | Perfil público de sucursal |
| GET /api/v1/clinics/branches/{clinic_id}/{branch_id} | Bearer token | Perfil protegido con validación de acceso |

## DTOs embebidos (dentro del perfil)

- `services`: lista de servicios ofrecidos por la sucursal
- `schedules`: lista de horarios de atención
- `rating_summary`: resumen de calificaciones (promedio, conteo)
- `availability_summary`: disponibilidad básica

## Pruebas API planificadas

| ID | Criterio | Método | Ruta | Expected HTTP | Estado | Comentario |
|---|---|---|---|---|---|---|
| APIA-004-01 | Perfil público retorna 200 sin auth | GET | /api/v1/clinics/branches/{valid_branch_id} | 200 | PENDING | DTO limpio, sin campos sensibles |
| APIA-004-02 | Perfil protegido retorna 401 sin token | GET | /api/v1/clinics/branches/{clinic_id}/{branch_id} | 401 | PENDING | Sin Authorization header |
| APIA-004-03 | Perfil protegido retorna 403 con token inválido | GET | /api/v1/clinics/branches/{clinic_id}/{branch_id} | 403 | PENDING | Token válido pero sin acceso |
| APIA-004-04 | Perfil protegido retorna 404 para ID inexistente | GET | /api/v1/clinics/branches/999999 | 404 | PENDING | Sin leak de información interna |
| APIA-004-05 | Servicios embebidos en perfil público | GET | /api/v1/clinics/branches/{valid_branch_id} | 200 | PENDING | services es lista con campos válidos |
| APIA-004-06 | Horarios embebidos en perfil público | GET | /api/v1/clinics/branches/{valid_branch_id} | 200 | PENDING | schedules es lista con campos válidos |
| APIA-004-07 | Rating summary embebido válido | GET | /api/v1/clinics/branches/{valid_branch_id} | 200 | PENDING | average y count son números válidos |
| APIA-004-08 | Availability summary embebido válido | GET | /api/v1/clinics/branches/{valid_branch_id} | 200 | PENDING | status es string claro |
| APIA-004-09 | ID inexistente no filtra información interna | GET | /api/v1/clinics/branches/999999 | 404 | PENDING | detail genérico, sin stack trace |
| APIA-004-10 | Campos sensibles no expuestos en DTO público | GET | /api/v1/clinics/branches/{valid_branch_id} | 200 | PENDING | Verificar keys del response |

## Criterios de aprobación

- [ ] Todas las pruebas listadas tienen estado PASSED o JUSTIFIED_SKIP.
- [ ] No hay bloqueos de entorno (DB no levanta, servicios caídos).
- [ ] Evidencia escrita en Sección Evidencia abajo.
- [ ] IDOR/BOLA verificado: ningún endpoint expone datos privados.

## Evidencia

| ID | Resultado | Response Status | Latencia (ms) | Notas |
|---|---|---|---|---|
| APIA-004-01 | — | — | — | Pendiente ejecución |
| APIA-004-02 | — | — | — | Pendiente ejecución |
| APIA-004-03 | — | — | — | Pendiente ejecución |
| APIA-004-04 | — | — | — | Pendiente ejecución |
| APIA-004-05 | — | — | — | Pendiente ejecución |
| APIA-004-06 | — | — | — | Pendiente ejecución |
| APIA-004-07 | — | — | — | Pendiente ejecución |
| APIA-004-08 | — | — | — | Pendiente ejecución |
| APIA-004-09 | — | — | — | Pendiente ejecución |
| APIA-004-10 | — | — | — | Pendiente ejecución |

## Hallazgos

No hay hallazgos registrados.
