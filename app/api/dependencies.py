from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.repositories.clinic_repository_impl import ClinicRepositoryImpl

def get_clinic_repository(db: Session = Depends(get_db)):
    return ClinicRepositoryImpl(db)