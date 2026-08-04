from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_clinic_repository
from app.application.use_cases.clinic_use_case import ClinicUseCase
from app.core.security import verify_token
from app.domain.entities.clinic import ClinicProfileResponse, BranchProfileResponse
from app.infrastructure.repositories.clinic_repository_impl import ClinicRepositoryImpl

router = APIRouter(prefix="/clinics", tags=["Clinics"])

@router.get("/branches/{branch_id}", response_model=BranchProfileResponse)
async def get_branch_profile(
    branch_id: int,
    clinic_use_case: ClinicUseCase = Depends(ClinicUseCase),
):
    """
    Get public profile for a branch
    """
    try:
        return await clinic_use_case.get_branch_profile(branch_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{clinic_id}/{branch_id}", response_model=ClinicProfileResponse)
async def get_clinic_branch_profile(
    clinic_id: int,
    branch_id: int,
    token: str,
    clinic_use_case: ClinicUseCase = Depends(ClinicUseCase),
):
    """
    Get protected profile for a clinic branch
    """
    try:
        # Verify the token (this is a simple example)
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return await clinic_use_case.get_clinic_branch_profile(clinic_id, branch_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))