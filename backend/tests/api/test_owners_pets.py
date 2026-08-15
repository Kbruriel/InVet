"""Pruebas básicas para propietarios y mascotas (slice 007)."""

import pytest


class TestEntityImports:
    """Verificar que las entidades se importan correctamente."""

    def test_import_owner_entity(self):
        from app.domain.entities.owner import Owner, OwnerCreate, OwnerUpdate
        assert Owner is not None
        assert OwnerCreate is not None
        assert OwnerUpdate is not None

    def test_import_pet_entity(self):
        from app.domain.entities.owner import Pet, PetCreate, PetUpdate
        assert Pet is not None
        assert PetCreate is not None
        assert PetUpdate is not None


class TestRepositoryInterfaces:
    """Verificar que las interfaces de repositorio se importan correctamente."""

    def test_import_owner_repository_interface(self):
        from app.domain.repositories.owner_repository import OwnerRepository
        assert OwnerRepository is not None

    def test_import_pet_repository_interface(self):
        from app.domain.repositories.owner_repository import PetRepository
        assert PetRepository is not None


class TestUseCases:
    """Verificar que los casos de uso se importan correctamente."""

    def test_import_owner_use_cases(self):
        from app.application.use_cases.owner_pets_use_cases import (
            CreateOwnerUseCase,
            GetOwnerUseCase,
            UpdateOwnerUseCase,
        )
        assert CreateOwnerUseCase is not None
        assert GetOwnerUseCase is not None
        assert UpdateOwnerUseCase is not None

    def test_import_pet_use_cases(self):
        from app.application.use_cases.owner_pets_use_cases import (
            CreatePetUseCase,
            GetPetUseCase,
            ListPetsByOwnerUseCase,
            DeletePetUseCase,
        )
        assert CreatePetUseCase is not None
        assert GetPetUseCase is not None
        assert ListPetsByOwnerUseCase is not None
        assert DeletePetUseCase is not None


class TestSchemas:
    """Verificar que los schemas Pydantic se importan correctamente."""

    def test_import_owner_schemas(self):
        from app.api.v1.schemas.owner_pets_schemas import (
            OwnerCreateSchema,
            OwnerReadSchema,
            OwnerUpdateSchema,
        )
        assert OwnerCreateSchema is not None
        assert OwnerReadSchema is not None
        assert OwnerUpdateSchema is not None

    def test_import_pet_schemas(self):
        from app.api.v1.schemas.owner_pets_schemas import (
            PetCreateSchema,
            PetReadSchema,
            PetUpdateSchema,
            PetListSchema,
        )
        assert PetCreateSchema is not None
        assert PetReadSchema is not None
        assert PetUpdateSchema is not None
        assert PetListSchema is not None


class TestRouters:
    """Verificar que los routers se importan correctamente."""

    def test_import_owners_router(self):
        from app.api.v1.routers.owners import router
        assert router is not None
        assert len(router.routes) > 0

    def test_import_pets_router(self):
        from app.api.v1.routers.pets import router
        assert router is not None
        assert len(router.routes) > 0


class TestMainRouter:
    """Verificar que los routers están registrados en el router principal."""

    def test_routers_registered_in_main_router(self):
        from app.api.v1.router import router
        route_paths = [str(route.path) for route in router.routes]
        
        # Verificar que los endpoints de owners están registrados
        assert any('/owners' in path for path in route_paths), "Owners routes not registered"
        
        # Verificar que los endpoints de pets están registrados
        assert any('/pets' in path for path in route_paths), "Pets routes not registered"


class TestRepositoryImpl:
    """Verificar que las implementaciones de repositorio se importan correctamente."""

    def test_import_owner_repository_impl(self):
        from app.infrastructure.database.repositories.owner_repository_impl import (
            OwnerRepositoryImpl,
        )
        assert OwnerRepositoryImpl is not None

    def test_import_pet_repository_impl(self):
        from app.infrastructure.database.repositories.pet_repository_impl import (
            PetRepositoryImpl,
        )
        assert PetRepositoryImpl is not None


class TestORMModels:
    """Verificar que los modelos ORM se importan correctamente."""

    def test_import_owner_model(self):
        from app.infrastructure.database.models.owner import Owner
        assert Owner is not None
        assert Owner.__tablename__ == "owners"

    def test_import_pet_model(self):
        from app.infrastructure.database.models.pet import Pet
        assert Pet is not None
        assert Pet.__tablename__ == "pets"


class TestAlembicMigration:
    """Verificar que la migración Alembic existe."""

    def test_migration_file_exists(self):
        import os
        migration_path = r"c:\InVet\backend\alembic\versions\a007_owners_pets.py"
        assert os.path.exists(migration_path), f"Alembic migration file not found at {migration_path}"

    def test_migration_has_upgrade_and_downgrade(self):
        import os
        import importlib.util
        migration_path = r"c:\InVet\backend\alembic\versions\a007_owners_pets.py"
        
        assert os.path.exists(migration_path), "Migration file not found"
        
        spec = importlib.util.spec_from_file_location("migration", migration_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        assert hasattr(module, 'upgrade'), "Migration missing upgrade function"
        assert hasattr(module, 'downgrade'), "Migration missing downgrade function"
        assert module.revision == "a007_owners_pets", "Migration revision ID incorrect"
