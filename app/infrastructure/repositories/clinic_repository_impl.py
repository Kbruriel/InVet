from typing import List, Optional
from sqlalchemy.orm import Session
from app.infrastructure.models.clinic_models import ClinicBranch, BranchSchedule, BranchService

class ClinicRepository:
    """Interface for clinic repository"""
    
    def get_branch_profile(self, branch_id: int):
        raise NotImplementedError
    
    def get_clinic_branch_profile(self, clinic_id: int, branch_id: int):
        raise NotImplementedError
        
    def create_branch(self, branch_data):
        raise NotImplementedError

class ClinicRepositoryImpl(ClinicRepository):
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_branch_profile(self, branch_id: int):
        branch = self.db.query(ClinicBranch).filter(ClinicBranch.id == branch_id).first()
        if not branch:
            raise ValueError("Branch not found")
        
        # Gather related data
        schedules = self.db.query(BranchSchedule).filter(BranchSchedule.branch_id == branch_id).all()
        services = self.db.query(BranchService).filter(BranchService.branch_id == branch_id).all()
        
        return {
            "id": branch.id,
            "name": branch.name,
            "address": branch.address,
            "phone": branch.phone,
            "email": branch.email,
            "schedules": [
                {
                    "day_of_week": s.day_of_week,
                    "open_time": s.open_time,
                    "close_time": s.close_time
                } for s in schedules
            ],
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "duration_minutes": s.duration_minutes
                } for s in services
            ],
            "rating_summary": {"average_rating": 4.5, "total_reviews": 120},
            "is_available": branch.is_available
        }
    
    def get_clinic_branch_profile(self, clinic_id: int, branch_id: int):
        # Check access (in a real implementation this would verify the authenticated user's permissions)
        branch = self.db.query(ClinicBranch).filter(ClinicBranch.id == branch_id).first()
        if not branch or branch.clinic_id != clinic_id:
            raise ValueError("Branch not found")
        
        # Gather related data
        schedules = self.db.query(BranchSchedule).filter(BranchSchedule.branch_id == branch_id).all()
        services = self.db.query(BranchService).filter(BranchService.branch_id == branch_id).all()
        
        return {
            "id": branch.id,
            "clinic_name": f"Clinic {clinic_id}",
            "branch": {
                "id": branch.id,
                "name": branch.name,
                "address": branch.address,
                "phone": branch.phone,
                "email": branch.email,
                "schedules": [
                    {
                        "day_of_week": s.day_of_week,
                        "open_time": s.open_time,
                        "close_time": s.close_time
                    } for s in schedules
                ],
                "services": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "description": s.description,
                        "duration_minutes": s.duration_minutes
                    } for s in services
                ],
                "rating_summary": {"average_rating": 4.5, "total_reviews": 120},
                "is_available": branch.is_available
            }
        }
    
    def create_branch(self, branch_data):
        # Create new branch in the database
        db_branch = ClinicBranch(**branch_data)
        self.db.add(db_branch)
        self.db.commit()
        self.db.refresh(db_branch)
        
        return db_branch