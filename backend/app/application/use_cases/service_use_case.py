"""
Casos de uso para Servicios
"""

from typing import List, Optional

from app.domain.entities.service import Service, ServiceCreate, ServiceUpdate
from app.domain.repositories.service_repo import ServiceRepository


class ServiceUseCase:
    """Casos de uso para gestión de servicios"""

    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository

    def create_service(self, service_data: ServiceCreate) -> Service:
        """Crea un nuevo servicio"""
        return self.service_repository.create_service(service_data)

    def get_service(self, service_id: int) -> Optional[Service]:
        """Obtiene un servicio por ID"""
        return self.service_repository.get_service(service_id)

    def get_services(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Service]:
        """Obtiene una lista de servicios para una sucursal"""
        return self.service_repository.get_services(branch_id, skip, limit)

    def update_service(
        self, service_id: int, service_data: ServiceUpdate
    ) -> Optional[Service]:
        """Actualiza un servicio existente"""
        return self.service_repository.update_service(service_id, service_data)

    def delete_service(self, service_id: int) -> bool:
        """Elimina un servicio"""
        return self.service_repository.delete_service(service_id)
