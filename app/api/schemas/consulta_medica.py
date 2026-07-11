from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.api.schemas.base import UUIDModel


class ConsultaMedicaCreate(BaseModel):
    """Schema para crear una consulta médica."""
    
    cita_id: str = Field(..., description="ID de la cita asociada")
    mascota_id: str = Field(..., description="ID de la mascota consultada")
    veterinario_id: str = Field(..., description="ID del veterinario que realiza la consulta")
    fecha_consulta: datetime = Field(..., description="Fecha y hora de la consulta")
    diagnostico: str = Field(..., description="Diagnóstico de la consulta")
    tratamiento: str = Field(..., description="Tratamiento recomendado")


class ConsultaMedicaRead(UUIDModel):
    """Schema para leer una consulta médica."""
    
    cita_id: str
    mascota_id: str
    veterinario_id: str
    fecha_consulta: datetime
    diagnostico: str
    tratamiento: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConsultaMedicaReadPublic(UUIDModel):
    """Schema para leer una consulta médica en modo público."""
    
    cita_id: str
    mascota_id: str
    veterinario_id: str
    fecha_consulta: datetime
    diagnostico: str
    tratamiento: str


class ConsultaMedicaList(BaseModel):
    """Schema para listar consultas médicas."""
    
    id: str
    cita_id: str
    mascota_id: str
    veterinario_id: str
    fecha_consulta: datetime
    diagnostico: str
    
    class Config:
        orm_mode = True


class ConsultaMedicaListPublic(BaseModel):
    """Schema para listar consultas médicas (modo público)."""
    
    id: str
    cita_id: str
    mascota_id: str
    veterinario_id: str
    fecha_consulta: datetime
    diagnostico: str
    
    class Config:
        orm_mode = True