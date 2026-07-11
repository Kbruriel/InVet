from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.domain.consulta_medica import ConsultaMedica
from app.domain.value_objects import Id


@dataclass(frozen=True)
class CrearConsultaMedicaDTO:
    """DTO para crear una nueva consulta médica."""
    cita_id: Id
    mascota_id: Id
    veterinario_id: Id
    fecha_consulta: datetime
    diagnostico: str
    tratamiento: str


@dataclass(frozen=True)
class ConsultaMedicaDTO:
    """DTO para leer una consulta médica."""
    id: Id
    cita_id: Id
    mascota_id: Id
    veterinario_id: Id
    fecha_consulta: datetime
    diagnostico: str
    tratamiento: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConsultaMedicaRepository:
    """Interfaz para el repositorio de consultas médicas."""
    
    def crear_consulta(self, consulta: ConsultaMedica) -> ConsultaMedica:
        raise NotImplementedError
    
    def obtener_por_id(self, id: Id) -> Optional[ConsultaMedica]:
        raise NotImplementedError
    
    def listar_por_mascota(self, mascota_id: Id) -> List[ConsultaMedica]:
        raise NotImplementedError


class CrearConsultaMedicaUseCase:
    """Caso de uso para crear una consulta médica."""
    
    def __init__(self, repository: ConsultaMedicaRepository):
        self.repository = repository
    
    def execute(self, dto: CrearConsultaMedicaDTO) -> ConsultaMedica:
        # Aquí iría la lógica de negocio
        consulta = ConsultaMedica(
            id=Id(uuid4()),
            cita_id=dto.cita_id,
            mascota_id=dto.mascota_id,
            veterinario_id=dto.veterinario_id,
            fecha_consulta=dto.fecha_consulta,
            diagnostico=dto.diagnostico,
            tratamiento=dto.tratamiento
        )
        
        return self.repository.crear_consulta(consulta)


class ObtenerConsultaMedicaUseCase:
    """Caso de uso para obtener una consulta médica por su ID."""
    
    def __init__(self, repository: ConsultaMedicaRepository):
        self.repository = repository
    
    def execute(self, id: Id) -> Optional[ConsultaMedica]:
        return self.repository.obtener_por_id(id)


class ListarConsultasPorMascotaUseCase:
    """Caso de uso para listar consultas médicas por mascota."""
    
    def __init__(self, repository: ConsultaMedicaRepository):
        self.repository = repository
    
    def execute(self, mascota_id: Id) -> List[ConsultaMedica]:
        return self.repository.listar_por_mascota(mascota_id)