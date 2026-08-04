from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.domain.entities.branch import BranchProfile

class BranchRepository(ABC):
    @abstractmethod
    async def get_by_id(self, branch_id: int) -> Optional[BranchProfile]:
        pass