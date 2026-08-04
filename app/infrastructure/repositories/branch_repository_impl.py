from typing import Optional
from sqlalchemy.orm import Session
from app.domain.repositories.branch_repository import BranchRepository
from app.domain.entities.branch import BranchProfile
from app.infrastructure.database.models import BranchModel

class BranchRepositoryImpl(BranchRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, branch_id: int) -> Optional[BranchProfile]:
        branch_model = self.db.query(BranchModel).filter(BranchModel.id == branch_id).first()
        if not branch_model:
            return None
        
        # Map to domain entity
        return BranchProfile(
            id=branch_model.id,
            name=branch_model.name,
            address=branch_model.address,
            phone=branch_model.phone,
            email=branch_model.email,
            schedules=branch_model.schedules,
            services=branch_model.services,
            rating_summary=branch_model.rating_summary,
            is_available=branch_model.is_available
        )