# InVet - Backend

## Arquitectura

Este proyecto sigue el patrón de arquitectura limpia (Clean Architecture) con las siguientes capas:

1. **app/domain/** - Entidades y reglas de negocio
2. **app/application/** - Casos de uso y DTOs
3. **app/infrastructure/** - Implementación de repositorios y ORM
4. **app/api/** - Routers, dependencias y schemas HTTP
5. **app/core/** - Configuración, seguridad y errores

## Estructura del proyecto

- `app/domain/`: Entidades y objetos de valor del dominio
- `app/application/`: Casos de uso (use cases)
- `app/infrastructure/`: Repositorios, modelos SQLAlchemy
- `app/api/`: Routers REST, dependencias y schemas Pydantic
- `app/core/`: Configuración centralizada, seguridad
- `app/tests/`: Tests automatizados

## Tests

Para ejecutar los tests:

```bash
pytest app/tests/
```

Los tests cubren:
- Creación de consultas médicas válidas e inválidas
- Casos de uso para crear, obtener y listar consultas
- Validación de errores y excepciones
- Funcionalidad de permisos por rol

## Endpoints expuestos

- `POST /api/v1/consultas` - Crear nueva consulta médica
- `GET /api/v1/consultas/{id}` - Obtener detalle de una consulta
- `GET /api/v1/mascotas/{mascota_id}/consultas` - Listar consultas de una mascota

## Requisitos

- Python 3.12+
- PostgreSQL (para producción)
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pytest + HTTPX