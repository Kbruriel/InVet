# Hallazgos de revisión de slice BE-009

## Resumen

La implementación de `BE-009` en `app/` no está lista para aprobarse. Hay bloqueos en autenticación, wiring de infraestructura y en el flujo de creación de consultas que impiden ejecutar el slice de forma confiable.

## Alcance revisado

- Backend: `app/api/consulta_medica_router.py`, `app/application/consulta_medica_use_cases.py`, `app/core/security.py`, `app/infrastructure/models/consulta_medica.py`, `app/infrastructure/repositories/consulta_medica_repository.py`.
- Frontend: no encontré implementación FE-009 en `frontend/` más allá de `node_modules`.
- QA: no encontré evidencia ejecutada para QA-009.

## Hallazgos por severidad

### Blocker

- La autenticación está rota por diseño. `get_current_user` ignora el token recibido y hace `jwt.decode("fake_token", "SECRET_KEY", ...)`, así que siempre falla con `JWTError` y devuelve 401. Eso deja inaccesibles los endpoints protegidos. Archivo: `app/core/security.py:47-68`.

- El flujo de creación de consulta no es ejecutable. El router pasa un `dict` a `CrearConsultaMedicaUseCase.execute`, pero el caso de uso espera un DTO con atributos. Además, el caso de uso usa `uuid4()` sin importarlo. Archivo: `app/api/consulta_medica_router.py:47-57`, `app/application/consulta_medica_use_cases.py:54-66`.

- La capa de infraestructura no carga completa. `ConsultaMedicaModel` referencia `uuid4` sin importarlo y además importa `app.infrastructure.database`, pero ese módulo no existe en el árbol raíz `app/`. El modelo y el repositorio no se pueden importar de forma confiable. Archivo: `app/infrastructure/models/consulta_medica.py:1-25`, `app/infrastructure/repositories/consulta_medica_repository.py:1-76`.

### Major

- No encontré implementación FE-009 en `frontend/`, por lo que la slice no está cerrada a nivel BE/FE/QA. El contrato del slice pide una UI para consulta, historial y detalle, pero el directorio frontend no contiene código fuente del flujo.

- El listado `GET /mascotas/{mascota_id}/consultas` devuelve una lista cruda y no una respuesta paginada con `total`, aunque el contrato de BE-009 lo pide para listados. Archivo: `app/api/consulta_medica_router.py:117-147`.

## Archivos afectados

- `app/core/security.py`
- `app/api/consulta_medica_router.py`
- `app/application/consulta_medica_use_cases.py`
- `app/infrastructure/models/consulta_medica.py`
- `app/infrastructure/repositories/consulta_medica_repository.py`

## Correcciones requeridas

- Reemplazar el `get_current_user` de prueba por validación real del bearer token y devolver contexto de usuario consistente.
- Hacer coincidir el contrato API/application al crear consultas: usar el DTO definido o ajustar el caso de uso para recibir el formato correcto.
- Arreglar el wiring de infraestructura del módulo `app/` para que el modelo importe dependencias existentes y el repositorio cargue sin errores.
- Implementar FE-009 o documentar explícitamente que queda fuera del alcance, si esa fue la decisión.
- Paginar el listado de consultas y exponer `total`.

## Checklist de revisión

- [x] Contrato BE validado.
- [ ] Contrato FE validado.
- [ ] Casos QA validados.
- [x] Arquitectura revisada.
- [x] Permisos e IDOR/BOLA revisados.
- [x] Evidencia documentada.

## Decision final

- [ ] Aprobado
- [x] Rechazado
