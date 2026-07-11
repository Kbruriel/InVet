from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class UUIDModel(BaseModel):
    """Modelo base que contiene un campo ID con tipo UUID."""
    
    id: str
    
    class Config:
        # Permitir que los UUIDs sean serializados como strings en vez de bytes
        json_encoders = {
            UUID: lambda v: str(v)
        }