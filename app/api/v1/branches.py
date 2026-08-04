from fastapi import APIRouter, Depends, HTTPException
from app.application.use_cases.get_branch_public_profile import GetBranchPublicProfileUseCase
from app.infrastructure.repositories.branch_repository_impl import BranchRepositoryImpl
from app.api.v1.schemas.branch import BranchPublicProfile
from app.api.v1.schemas.requests import BranchReadRequest

router = APIRouter(prefix="/clinics/branches", tags=["branches"])

@router.get("/{branch_id}", response_model=BranchPublicProfile)
async def get_branch_public_profile(
    branch_id: int,
    use_case: GetBranchPublicProfileUseCase = Depends()
):
    try:
        profile = await use_case.execute(branch_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail="Branch not found")