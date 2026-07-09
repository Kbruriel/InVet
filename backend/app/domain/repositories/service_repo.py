"""
Interfaz de repositorio para Servicios
"""
from typing import List, Optional

from app.domain.entities.service import Service, ServiceCreate, ServiceUpdate


class ServiceRepository:
    """Interfaz de repositorio para servicios"""
    
    def create_service(self, service: ServiceCreate) -> Service:
        raise NotImplementedError
    
    def get_service(self, service_id: int) -> Optional[Service]:
        raise NotImplementedError
    
    def get_services(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        raise NotImplementedError
    
    def update_service(self, service_id: int, service_data: ServiceUpdate) -> Optional[Service]:
        raise NotImplementedError
    
    def delete_service(self, service_id: int) -> bool:
        raise NotImplementedError