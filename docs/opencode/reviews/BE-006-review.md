# Hallazgos de revision de slice BE-006

## Resumen

Revision enfocada en el backend del slice BE-006: servicios, veterinarios y usuarios internos.
Se detectaron hallazgos de codigo y de contrato que si entran en el alcance de `/implement-findings`, sin requerir intervencion externa ni expansion del MVP.

## Alcance revisado

- Backend: routers, use cases, repositorios, modelos ORM y tests del slice.
- Frontend: no revisado en este reporte.
- QA: se tomo como referencia documental, pero este reporte solo deja hallazgos de backend corregibles por `/implement-findings`.

## Hallazgos por severidad

### Blocker
- El modulo de dependencias importado por los routers de BE-006 no existe en la ruta usada por el codigo. Los tres routers del slice importan `app.core.dependencies`, pero el repositorio solo expone dependencias en `app.api.dependencies`. Esto bloquea el arranque de la API y puede resolverse dentro de `/implement-findings` ajustando imports o creando un adapter delgado de compatibilidad. Ver [service_router.py](C:/InVet/backend/app/api/v1/service_router.py:9), [veterinarian_router.py](C:/InVet/backend/app/api/v1/veterinarian_router.py:9), [internal_user_router.py](C:/InVet/backend/app/api/v1/internal_user_router.py:9), [api/dependencies.py](C:/InVet/backend/app/api/dependencies.py:1).

### Critical
- No se registraron hallazgos criticos adicionales.

### Major
- El control de acceso de `GET /services/{service_id}` compara `service_id` contra la lista de sucursales del usuario, en vez de comparar `existing.branch_id`. Eso rompe la autorizacion por ownership y puede producir falsos positivos o falsos negativos en IDOR/BOLA. El ajuste es local al router y entra en `/implement-findings`. Ver [service_router.py](C:/InVet/backend/app/api/v1/service_router.py:54).
- El repositorio de veterinarios no coincide con el ORM: el modelo persiste `first_name`, pero el repositorio crea y actualiza usando `name`. Ademas, la conversion de vuelta al dominio tambien depende de ese mapeo incorrecto. Este desajuste hace que el CRUD de veterinarios no sea confiable y se corrige dentro de `/implement-findings`. Ver [veterinarian.py](C:/InVet/backend/app/infrastructure/database/models/veterinarian.py:17), [veterinarian_repository_impl.py](C:/InVet/backend/app/infrastructure/database/repositories/veterinarian_repository_impl.py:20), [veterinarian_repository_impl.py](C:/InVet/backend/app/infrastructure/database/repositories/veterinarian_repository_impl.py:50).
- El repositorio de usuarios internos usa `password` en claro contra un ORM que espera `password_hash`, y no aplica el helper de hash antes de persistir. Eso deja el flujo de alta y actualizacion inconsistente y potencialmente inseguro, pero el arreglo es local y entra en el alcance de `/implement-findings`. Ver [internal_user.py](C:/InVet/backend/app/infrastructure/database/models/internal_user.py:20), [internal_user_repository_impl.py](C:/InVet/backend/app/infrastructure/database/repositories/internal_user_repository_impl.py:20), [security.py](C:/InVet/backend/app/core/security.py:19).

### Minor
- Los tests API del slice importan `app.main`, pero el entrypoint real esta en `app.api.main`. Eso hace que el set de pruebas no sea ejecutable tal como esta escrito, y el fix es simple y esta dentro del alcance de `/implement-findings`. Ver [test_service_api.py](C:/InVet/backend/app/tests/api/test_service_api.py:7), [test_veterinarian_api.py](C:/InVet/backend/app/tests/api/test_veterinarian_api.py:8), [test_internal_user_api.py](C:/InVet/backend/app/tests/api/test_internal_user_api.py:8), [test_main.py](C:/InVet/backend/app/tests/test_main.py:4).

## Archivos afectados

- [service_router.py](C:/InVet/backend/app/api/v1/service_router.py)
- [veterinarian_router.py](C:/InVet/backend/app/api/v1/veterinarian_router.py)
- [internal_user_router.py](C:/InVet/backend/app/api/v1/internal_user_router.py)
- [api/dependencies.py](C:/InVet/backend/app/api/dependencies.py)
- [service_repository_impl.py](C:/InVet/backend/app/infrastructure/database/repositories/service_repository_impl.py)
- [veterinarian_repository_impl.py](C:/InVet/backend/app/infrastructure/database/repositories/veterinarian_repository_impl.py)
- [internal_user_repository_impl.py](C:/InVet/backend/app/infrastructure/database/repositories/internal_user_repository_impl.py)
- [veterinarian.py](C:/InVet/backend/app/infrastructure/database/models/veterinarian.py)
- [internal_user.py](C:/InVet/backend/app/infrastructure/database/models/internal_user.py)
- [security.py](C:/InVet/backend/app/core/security.py)
- [test_service_api.py](C:/InVet/backend/app/tests/api/test_service_api.py)
- [test_veterinarian_api.py](C:/InVet/backend/app/tests/api/test_veterinarian_api.py)
- [test_internal_user_api.py](C:/InVet/backend/app/tests/api/test_internal_user_api.py)
- [test_main.py](C:/InVet/backend/app/tests/test_main.py)

## Correcciones requeridas

- Unificar la capa de dependencias usada por los routers de BE-006 con el modulo realmente disponible en el backend.
- Corregir el chequeo de ownership de servicios para usar `existing.branch_id`.
- Alinear el mapeo ORM/dominio de veterinarios (`first_name` vs `name`).
- Hashar y persistir correctamente la contrasena de usuarios internos.
- Ajustar los imports de los tests al entrypoint real de la aplicacion.

## Checklist de revision

- [x] Contrato BE validado.
- [ ] Contrato FE validado.
- [ ] Casos QA validados.
- [x] Arquitectura revisada.
- [x] Permisos e IDOR/BOLA revisados.
- [x] Evidencia documentada.

## Decision final

- [ ] Aprobado
- [x] Rechazado

Los hallazgos anteriores estan dentro del alcance de `/implement-findings` y pueden cerrarse con cambios de codigo y pruebas en el propio slice, sin ampliar funcionalidad ni tocar dependencias externas.
