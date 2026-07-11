from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UUID as SQUUID
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class ConsultaMedicaModel(Base):
    """Modelo SQLAlchemy para consulta médica."""
    
    __tablename__ = "consultas_medicas"
    
    id = Column(SQUUID(as_uuid=True), primary_key=True, default=uuid4)
    cita_id = Column(SQUUID(as_uuid=True), ForeignKey("citas.id"), nullable=False)
    mascota_id = Column(SQUUID(as_uuid=True), ForeignKey("mascotas.id"), nullable=False)
    veterinario_id = Column(SQUUID(as_uuid=True), nullable=False)
    fecha_consulta = Column(DateTime, nullable=False)
    diagnostico = Column(Text, nullable=False)
    tratamiento = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    cita = relationship("CitaModel", back_populates="consultas_medicas")
    mascota = relationship("MascotaModel", back_populates="consultas_medicas")