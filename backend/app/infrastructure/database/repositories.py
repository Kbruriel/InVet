"""
Repositorios concretos para acceso a datos
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.models import UserCreate, UserUpdate
from app.infrastructure.database.models import Clinic, Pet, User


class UserRepository:
    """Repositorio para operaciones de usuario"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por correo electrónico"""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene múltiples usuarios con paginación"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_create: UserCreate) -> User:
        """Crea un nuevo usuario"""
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=user_create.password,  # Este debería ser hasheado antes
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Actualiza un usuario existente"""
        db_user = self.get_user(user_id)
        if db_user:
            for key, value in user_update.dict(exclude_unset=True).items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario"""
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False


class ClinicRepository:
    """Repositorio para operaciones de clínica"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_clinic(self, clinic_id: int) -> Optional[Clinic]:
        """Obtiene una clínica por ID"""
        return self.db.query(Clinic).filter(Clinic.id == clinic_id).first()

    def get_clinics(self, skip: int = 0, limit: int = 100) -> List[Clinic]:
        """Obtiene múltiples clínicas con paginación"""
        return self.db.query(Clinic).offset(skip).limit(limit).all()

    def create_clinic(self, clinic_data) -> Clinic:
        """Crea una nueva clínica"""
        db_clinic = Clinic(**clinic_data)
        self.db.add(db_clinic)
        self.db.commit()
        self.db.refresh(db_clinic)
        return db_clinic


class PetRepository:
    """Repositorio para operaciones de mascota"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Obtiene una mascota por ID"""
        return self.db.query(Pet).filter(Pet.id == pet_id).first()

    def get_pets(self, skip: int = 0, limit: int = 100) -> List[Pet]:
        """Obtiene múltiples mascotas con paginación"""
        return self.db.query(Pet).offset(skip).limit(limit).all()

    def create_pet(self, pet_data) -> Pet:
        """Crea una nueva mascota"""
        db_pet = Pet(**pet_data)
        self.db.add(db_pet)
        self.db.commit()
        self.db.refresh(db_pet)
        return db_pet
