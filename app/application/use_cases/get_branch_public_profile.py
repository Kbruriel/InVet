from uuid import UUID
from typing import Optional
from app.domain.entities.branch import BranchProfile
from app.domain.repositories.branch_repository import BranchRepository
from app.core.errors import BranchNotFoundError

class GetBranchPublicProfileUseCase:
    def __init__(self, branch_repository: BranchRepository):
        self.branch_repository = branch_repository

    async def execute(self, branch_id: int) -> BranchProfile:
        branch = await self.branch_repository.get_by_id(branch_id)
        if not branch:
            raise BranchNotFoundError(f"Branch with id {branch_id} not found")
        
        # Return only public data
        return BranchProfile(
            id=branch.id,
            name=branch.name,
            address=branch.address,
            phone=branch.phone,
            email=branch.email,
            schedules=branch.schedules,
            services=branch.services,
            rating_summary=branch.rating_summary,
            is_available=branch.is_available
        )