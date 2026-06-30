"""Router para endpoints de clínicas y sucursales."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.use_cases.clinic_use_case import GetBranchProfileUseCase, GetBranchProfileWithPermissionUseCase
from app.infrastructure.repositories.clinic_repository_impl import BranchRepositoryImpl, ServiceRepositoryImpl, ScheduleRepositoryImpl, RatingRepositoryImpl
from app.infrastructure.database import get_db
from app.core.security import get_current_user


# Crear el router
router = APIRouter(prefix="/clinics", tags=["Clinics and Branches"])

# Endpoint para obtener perfil público de una sucursal
@router.get("/branches/{branch_id}", response_model=Dict[str, Any])
async def get_branch_profile(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Obtiene el perfil público de una sucursal con sus servicios, horarios y calificaciones."""
    
    # Crear los repositorios necesarios
    branch_repo = BranchRepositoryImpl(db)
    service_repo = ServiceRepositoryImpl(db)
    schedule_repo = ScheduleRepositoryImpl(db)
    rating_repo = RatingRepositoryImpl(db)
    
    # Crear el caso de uso
    use_case = GetBranchProfileUseCase(
        branch_repo=branch_repo,
        service_repo=service_repo,
        schedule_repo=schedule_repo,
        rating_repo=rating_repo
    )
    
    try:
        # Ejecutar el caso de uso  
        result = await use_case.execute(branch_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# Endpoint para obtener perfil público con validación de permisos
@router.get("/branches/{clinic_id}/{branch_id}", response_model=Dict[str, Any])
async def get_branch_profile_with_permissions(
    clinic_id: int,
    branch_id: int,
    db: Session = Depends(get_db),
    current_user=None  # Puede ser None para usuarios no autenticados
):
    """Obtiene el perfil público de una sucursal con validación de permisos."""
    
    # Crear los repositorios necesarios
    branch_repo = BranchRepositoryImpl(db)
    service_repo = ServiceRepositoryImpl(db)
    schedule_repo = ScheduleRepositoryImpl(db)
    rating_repo = RatingRepositoryImpl(db)
    
    # Crear el caso de uso
    use_case = GetBranchProfileWithPermissionUseCase(
        branch_repo=branch_repo,
        service_repo=service_repo,
        schedule_repo=schedule_repo,
        rating_repo=rating_repo
    )
    
    try:
        # Ejecutar el caso de uso  
        result = await use_case.execute(clinic_id, branch_id, current_user.id if current_user else None)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )