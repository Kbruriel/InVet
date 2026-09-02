"""Funciones de seguridad y manejo de tokens."""

from datetime import datetime, timedelta
from typing import Any, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.database.models.internal_user_model import (
    InternalUser as InternalUserModel,
)
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.user import User as UserModel
from app.infrastructure.database.session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
MIN_SECRET_KEY_LENGTH = 16


def _require_secret_key() -> str:
    """Obtener la clave secreta configurada o fallar con un error claro."""
    secret_key = settings.SECRET_KEY
    if not secret_key:
        raise RuntimeError("SECRET_KEY must be configured before using token helpers.")
    return secret_key


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return cast(
        str, jwt.encode(to_encode, _require_secret_key(), algorithm=settings.ALGORITHM)
    )


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return cast(
        str, jwt.encode(to_encode, _require_secret_key(), algorithm=settings.ALGORITHM)
    )


def create_reset_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(hours=1)
    )
    to_encode.update({"exp": expire, "type": "reset"})
    return cast(
        str, jwt.encode(to_encode, _require_secret_key(), algorithm=settings.ALGORITHM)
    )


def verify_token(token: str) -> dict[str, Any]:
    try:
        return cast(
            dict[str, Any],
            jwt.decode(token, _require_secret_key(), algorithms=[settings.ALGORITHM]),
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def verify_access_token(token: str) -> dict[str, Any]:
    """Valida un JWT de acceso."""
    payload = verify_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_access_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Devuelve la identidad del usuario autenticado con un token de acceso."""
    payload = verify_access_token(token)
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    db_user = None
    if isinstance(db, Session):
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado para el token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    role = payload.get("role") or ("admin" if db_user and db_user.is_admin else "user")
    current_user: dict[str, Any] = {
        "id": user_id,
        "user_id": user_id,
        "email": db_user.email if db_user else payload.get("email", ""),
        "role": role,
    }

    clinic_id: int | None = (
        payload.get("clinic_id") if isinstance(payload.get("clinic_id"), int) else None
    )
    if clinic_id is None and isinstance(db, Session):
        owner = (
            db.query(OwnerModel)
            .filter(
                OwnerModel.user_id == user_id,
                OwnerModel.is_active.is_(True),
            )
            .first()
        )
        if owner and owner.clinic_id is not None:
            clinic_id = int(owner.clinic_id)
        else:
            internal_user = (
                db.query(InternalUserModel)
                .filter(
                    InternalUserModel.user_id == user_id,
                    InternalUserModel.is_active.is_(True),
                )
                .first()
            )
            if internal_user and internal_user.clinic_id is not None:
                clinic_id = int(internal_user.clinic_id)
                if role == "user":
                    role = "veterinarian"
                    current_user["role"] = role

    if clinic_id is not None:
        current_user["clinic_id"] = clinic_id
        current_user["tenant_id"] = clinic_id

    return current_user
