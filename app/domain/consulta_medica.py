from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.value_objects import Id


@dataclass(frozen=True)
class ConsultaMedica:
    """Entidad de consulta médica vinculada a una cita y mascota."""
    
    id: Id
    cita_id: Id
    mascota_id: Id
    veterinario_id: Id
    fecha_consulta: datetime
    diagnostico: str
    tratamiento: str
    
    # Campos que pueden ser nulos en ciertos casos
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Validaciones básicas de los campos
        if not self.diagnostico or not self.diagnostico.strip():
            raise ValueError("El diagnóstico no puede estar vacío")
        
        if not self.tratamiento or not self.tratamiento.strip():
            raise ValueError("El tratamiento no puede estar vacío")