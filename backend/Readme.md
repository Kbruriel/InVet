# InVet - Sistema Veterinario y Estéticas

## Backend Setup

### Base de Datos

La aplicación usa PostgreSQL como base de datos principal con una arquitectura basada en Clean Architecture:

- **SQLAlchemy 2.0** para el ORM
- **Alembic** para migraciones de base de datos 
- **Base de datos en capa Infrastructure**

### Estructura de Modelos

Los modelos se encuentran en `app/infrastructure/database/models/` y están organizados siguiendo Clean Architecture:

- `User`: Usuarios del sistema (clientes, veterinarios, administradores)
- `Clinic`: Clínicas o sucursales
- `Veterinarian`: Veterinarios que trabajan en clínicas
- `Owner`: Propietarios de mascotas
- `Pet`: Mascotas registradas

### Base de Datos

Configuración de base de datos:

```python
# Ejemplo de conexión desde app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Migraciones

Para crear nuevas migraciones:

```bash
# Generar nueva migración (auto-generar desde modelos existentes)
alembic revision --autogenerate -m "Descripción de la migración"

# Aplicar migraciones
alembic upgrade head
```

### Pruebas de Base de Datos

Las pruebas unitarias para la base de datos se encuentran en `app/tests/` y usan SQLite en memoria:

```bash
pytest app/tests/test_database.py
```