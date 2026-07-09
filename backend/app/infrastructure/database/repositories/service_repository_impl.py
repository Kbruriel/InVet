"""
Implementación del repositorio de servicios
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.service import Service, ServiceCreate, ServiceUpdate
from app.infrastructure.database.models.service import Service as ServiceDB


class ServiceRepositoryImpl:
    """Implementación del repositorio de servicios"""

    def __init__(self, db: Session):
        self.db = db

    def create_service(self, service_data: ServiceCreate) -> Service:
        """Crea un nuevo servicio"""
        db_service = ServiceDB(**service_data.model_dump())
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        return self._db_to_domain(db_service)

    def get_service(self, service_id: int) -> Optional[Service]:
        """Obtiene un servicio por ID"""
        db_service = self.db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
        return self._db_to_domain(db_service) if db_service else None

    def get_services(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """Obtiene una lista de servicios para una sucursal"""
        db_services = (
            self.db.query(ServiceDB)
            .filter(ServiceDB.branch_id == branch_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._db_to_domain(db_service) for db_service in db_services]

    def update_service(self, service_id: int, service_data: ServiceUpdate) -> Optional[Service]:
        """Actualiza un servicio existente"""
        db_service = self.db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
        if not db_service:
            return None

        # Update fields
        for key, value in service_data.model_dump(exclude_unset=True).items():
            setattr(db_service, key, value)

        self.db.commit()
        self.db.refresh(db_service)
        return self._db_to_domain(db_service)

    def delete_service(self, service_id: int) -> bool:
        """Elimina un servicio"""
        db_service = self.db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
        if not db_service:
            return False

        self.db.delete(db_service)
        self.db.commit()
        return True

    def _db_to_domain(self, db_service: ServiceDB) -> Service:
        """Convierte un modelo de base de datos a entidad de dominio"""
        return Service(
            id=db_service.id,
            branch_id=db_service.branch_id,
            name=db_service.name,
            description=db_service.description,
            duration=db_service.duration,
            price=db_service.price,
            is_active=db_service.is_active,
            created_at=db_service.created_at,
            updated_at=db_service.updated_at
        )