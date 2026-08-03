from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# Schemas para creación y actualización
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "client"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Schemas para respuestas de la API
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool

class UserPublic(UserBase):
    id: int
    created_at: datetime

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        orm_mode = True

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        orm_mode = True

class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    
    class Config:
        orm_mode = True