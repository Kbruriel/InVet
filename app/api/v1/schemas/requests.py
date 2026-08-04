from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class BranchRequest(BaseModel):
    """Branch request schema"""
    clinic_id: UUID
    name: str
    address: str
    phone: str
    email: str
    
class BranchReadRequest(BaseModel):
    """Branch read request schema"""
    branch_id: int
