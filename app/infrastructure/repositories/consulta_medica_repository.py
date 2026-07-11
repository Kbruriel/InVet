import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.domain.consulta_medica import ConsultaMedica
from app.domain.value_objects import Id
from app.infrastructure.models.consulta_medica import ConsultaMedicaModel
from app.application.consulta_medica_use_cases import ConsultaMedicaRepository


class ConsultaMedicaSQLAlchemyRepository(ConsultaMedicaRepository):
    """Repositorio SQLAlchemy para consulta médica."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def crear_consulta(self, consulta: ConsultaMedica) -> ConsultaMedica:
        try:
            # Convertir el objeto de dominio a modelo SQLAlchemy
            consulta_model = ConsultaMedicaModel(
                id=consulta.id.value,
                cita_id=consulta.cita_id.value,
                mascota_id=consulta.mascota_id.value,
                veterinario_id=consulta.veterinario_id.value,
                fecha_consulta=consulta.fecha_consulta,
                diagnostico=consulta.diagnostico,
                tratamiento=consulta.tratamiento,
                created_at=consulta.created_at,
                updated_at=consulta.updated_at
            )
            
            self.db_session.add(consulta_model)
            self.db_session.commit()
            self.db_session.refresh(consulta_model)
            
            # Volver a convertir a objeto de dominio
            return ConsultaMedica(
                id=Id(consulta_model.id),
                cita_id=Id(consulta_model.cita_id),
                mascota_id=Id(consulta_model.mascota_id),
                veterinario_id=Id(consulta_model.veterinario_id),
                fecha_consulta=consulta_model.fecha_consulta,
                diagnostico=consulta_model.diagnostico,
                tratamiento=consulta_model.tratamiento,
                created_at=consulta_model.created_at,
                updated_at=consulta_model.updated_at
            )
        except IntegrityError as e:
            self.db_session.rollback()
            raise ValueError(f"Error de integridad al crear consulta médica: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            raise RuntimeError(f"Error al crear consulta médica: {str(e)}")
    
    def obtener_por_id(self, id: Id) -> Optional[ConsultaMedica]:
        consulta_model = self.db_session.query(ConsultaMedicaModel).filter(
            ConsultaMedicaModel.id == id.value
        ).first()
        
        if not consulta_model:
            return None
            
        return ConsultaMedica(
            id=Id(consulta_model.id),
            cita_id=Id(consulta_model.cita_id),
            mascota_id=Id(consulta_model.mascota_id),
            veterinario_id=Id(consulta_model.veterinario_id),
            fecha_consulta=consulta_model.fecha_consulta,
            diagnostico=consulta_model.diagnostico,
            tratamiento=consulta_model.tratamiento,
            created_at=consulta_model.created_at,
            updated_at=consulta_model.updated_at
        )
    
    def listar_por_mascota(self, mascota_id: Id) -> List[ConsultaMedica]:
        consulta_models = self.db_session.query(ConsultaMedicaModel).filter(
            ConsultaMedicaModel.mascota_id == mascota_id.value
        ).all()
        
        return [
            ConsultaMedica(
                id=Id(consulta_model.id),
                cita_id=Id(consulta_model.cita_id),
                mascota_id=Id(consulta_model.mascota_id),
                veterinario_id=Id(consulta_model.veterinario_id),
                fecha_consulta=consulta_model.fecha_consulta,
                diagnostico=consulta_model.diagnostico,
                tratamiento=consulta_model.tratamiento,
                created_at=consulta_model.created_at,
                updated_at=consulta_model.updated_at
            )
            for consulta_model in consulta_models
        ]