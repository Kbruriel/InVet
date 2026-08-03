# Backend Clean Architecture InVet

## Estructura base

```text
app/
  api/
  application/
  domain/
  infrastructure/
  core/
  tests/
```

## Reglas obligatorias

- Routers solo manejan HTTP, dependencias, validación de entrada y respuesta.
- La lógica de negocio vive en casos de uso, entidades o servicios de dominio.
- El dominio no importa FastAPI, SQLAlchemy ni proveedores externos.
- Infraestructura implementa repositorios definidos como interfaces/ports.
- No se retornan modelos ORM desde endpoints.
- Schemas separados: create, update, read, public read, admin read.
- Permisos y pertenencia se validan en backend.
- Transacciones no se dispersan en routers.

## Revisión por slice

Cada `BE-00X` debe cerrar con:
- Use case claro.
- Tests de éxito y fallo.
- Validación de permisos cuando aplique.
- Validación tenant/owner/branch cuando aplique.
- Auditoría en acciones críticas.
