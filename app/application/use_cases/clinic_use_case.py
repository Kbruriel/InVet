from typing import List, Optional
from app.domain.entities.clinic import BranchProfileResponse, ClinicProfileResponse, BranchProfile
from app.infrastructure.repositories.clinic_repository_impl import ClinicRepository

class ClinicUseCase:
    def __init__(self, repository: ClinicRepository):
        self.repository = repository
    
    async def get_branch_profile(self, branch_id: int) -> BranchProfileResponse:
        """Get public profile for a branch"""
        result = await self.repository.get_branch_profile(branch_id)
        return BranchProfileResponse(**result)
    
    async def get_clinic_branch_profile(self, clinic_id: int, branch_id: int) -> ClinicProfileResponse:
        """Get protected profile for a clinic branch with access control"""
        result = await self.repository.get_clinic_branch_profile(clinic_id, branch_id)
        return ClinicProfileResponse(**result)