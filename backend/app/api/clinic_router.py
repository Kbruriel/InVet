"""Router for clinic and branch profile endpoints."""
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import (
    get_branch_profile_use_case,
    get_branch_profile_with_permission_use_case,
)
from app.application.use_cases.clinic_use_case import (
    GetBranchProfileUseCase,
    GetBranchProfileWithPermissionUseCase,
)

router = APIRouter(prefix="/clinics", tags=["Clinics and Branches"])
bearer_scheme = HTTPBearer(auto_error=False)


def _translate_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)
    if "Access denied" in message:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)
    if "not found" in message:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """Extract a minimal authenticated user context from a bearer token."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return {"id": int(credentials.credentials)}
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/branches/{branch_id}", response_model=Dict[str, Any])
async def get_branch_profile(
    branch_id: int,
    use_case: GetBranchProfileUseCase = Depends(get_branch_profile_use_case),
):
    """Return the public branch profile."""
    try:
        return await use_case.execute(branch_id)
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        ) from exc


@router.get("/{clinic_id}/{branch_id}", response_model=Dict[str, Any])
async def get_branch_profile_with_permissions(
    clinic_id: int,
    branch_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: GetBranchProfileWithPermissionUseCase = Depends(
        get_branch_profile_with_permission_use_case
    ),
):
    """Return the protected branch profile for authenticated owners."""
    try:
        return await use_case.execute(clinic_id, branch_id, current_user.get("id"))
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        ) from exc
