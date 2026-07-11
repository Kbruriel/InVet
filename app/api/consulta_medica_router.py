from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.application.consulta_medica_use_cases import (
    CrearConsultaMedicaUseCase,
    ObtenerConsultaMedicaUseCase,
    ListarConsultasPorMascotaUseCase,
)
from app.infrastructure.repositories.consulta_medica_repository import ConsultaMedicaSQLAlchemyRepository
from app.api.schemas.consulta_medica import ConsultaMedicaCreate, ConsultaMedicaRead, ConsultaMedicaListPublic
from app.core.security import get_current_user
from app.domain.value_objects import Id

router = APIRouter(prefix="/consultas", tags=["Consultas Médicas"])


@router.post("/", response_model=ConsultaMedicaRead, status_code=status.HTTP_201_CREATED)
async def crear_consulta_medica(
    consulta_data: ConsultaMedicaCreate,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """
    Crear una nueva consulta médica.
    
    Solo usuarios con rol veterinario pueden crear consultas.
    """
    # Verificamos que el usuario tenga rol veterinario
    if not current_user.is_veterinario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: solo usuarios veterinarios pueden crear consultas médicas"
        )
    
    # Obtenemos el repositorio
    repository = ConsultaMedicaSQLAlchemyRepository(db)
    
    # Creamos el caso de uso
    use_case = CrearConsultaMedicaUseCase(repository)
    
    # Ejecutamos el caso de uso
    try:
        dto = use_case.execute(
            dto={
                "cita_id": Id(consulta_data.cita_id),
                "mascota_id": Id(consulta_data.mascota_id),
                "veterinario_id": Id(current_user.id),
                "fecha_consulta": consulta_data.fecha_consulta,
                "diagnostico": consulta_data.diagnostico,
                "tratamiento": consulta_data.tratamiento
            }
        )
        
        # Convertimos a modelo Pydantic para respuesta
        return ConsultaMedicaRead(
            id=str(dto.id.value),
            cita_id=str(dto.cita_id.value),
            mascota_id=str(dto.mascota_id.value),
            veterinario_id=str(dto.veterinario_id.value),
            fecha_consulta=dto.fecha_consulta,
            diagnostico=dto.diagnostico,
            tratamiento=dto.tratamiento,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{id}", response_model=ConsultaMedicaRead)
async def obtener_consulta_medica(
    id: str,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Obtener detalle de una consulta médica."""
    
    repository = ConsultaMedicaSQLAlchemyRepository(db)
    use_case = ObtenerConsultaMedicaUseCase(repository)
    
    consulta = use_case.execute(Id(id))
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta médica no encontrada"
        )
    
    # Verificamos que el usuario tenga permiso para acceder a esta consulta
    # (puede ser el veterinario que realizó la consulta o el propietario)
    if (str(consulta.veterinario_id.value) != current_user.id and 
        str(consulta.mascota_id.value) != str(current_user.mascota_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: no tienes permiso para ver esta consulta"
        )
    
    return ConsultaMedicaRead(
        id=str(consulta.id.value),
        cita_id=str(consulta.cita_id.value),
        mascota_id=str(consulta.mascota_id.value),
        veterinario_id=str(consulta.veterinario_id.value),
        fecha_consulta=consulta.fecha_consulta,
        diagnostico=consulta.diagnostico,
        tratamiento=consulta.tratamiento,
        created_at=consulta.created_at,
        updated_at=consulta.updated_at
    )


@router.get("/mascotas/{mascota_id}/consultas", response_model=List[ConsultaMedicaListPublic])
async def listar_consultas_por_mascota(
    mascota_id: str,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Listar consultas médicas por mascota."""
    
    # Verificamos que el usuario tenga permiso para acceder a estas consultas
    if str(current_user.mascota_id) != mascota_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: no puedes ver las consultas de esta mascota"
        )
    
    repository = ConsultaMedicaSQLAlchemyRepository(db)
    use_case = ListarConsultasPorMascotaUseCase(repository)
    
    consultas = use_case.execute(Id(mascota_id))
    
    return [
        ConsultaMedicaListPublic(
            id=str(consulta.id.value),
            cita_id=str(consulta.cita_id.value),
            mascota_id=str(consulta.mascota_id.value),
            veterinario_id=str(consulta.veterinario_id.value),
            fecha_consulta=consulta.fecha_consulta,
            diagnostico=consulta.diagnostico
        )
        for consulta in consultas
    ]