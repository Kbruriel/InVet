"""Routers for public profile and clinic administration endpoints."""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import (
    get_branch_admin_use_case,
    get_branch_hours_admin_use_case,
    get_branch_profile_use_case,
    get_branch_profile_with_permission_use_case,
    get_clinic_admin_use_case,
)
from app.api.schemas.clinic_schemas import (
    BranchCreate,
    BranchRead,
    BranchUpdate,
    ClinicCreate,
    ClinicRead,
    ClinicUpdate,
    PaginatedBranchesResponse,
    PaginatedClinicsResponse,
    ScheduleAdminRead,
    ScheduleCreate,
    ScheduleUpdate,
)
from app.application.use_cases.clinic_use_case import (
    BranchAdminUseCase,
    BranchHoursAdminUseCase,
    ClinicAdminUseCase,
    GetBranchProfileUseCase,
    GetBranchProfileWithPermissionUseCase,
)

router = APIRouter(prefix="/clinics", tags=["Clinics"])
branch_router = APIRouter(prefix="/branches", tags=["Branches"])
bearer_scheme = HTTPBearer(auto_error=False)


def _translate_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)
    if "Access denied" in message:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)
    if "not found" in message:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    if "Invalid" in message:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
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


@router.get("", response_model=PaginatedClinicsResponse)
async def list_clinics(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    use_case: ClinicAdminUseCase = Depends(get_clinic_admin_use_case),
):
    """Return a paginated clinic list for administration."""
    try:
        return await use_case.list_clinics(
            user_id=current_user.get("id"),
            skip=skip,
            limit=limit,
            status=status_filter,
            search=search,
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@router.post("", response_model=ClinicRead, status_code=status.HTTP_201_CREATED)
async def create_clinic(
    payload: ClinicCreate,
    current_user: dict = Depends(get_current_user),
    use_case: ClinicAdminUseCase = Depends(get_clinic_admin_use_case),
):
    """Create a clinic."""
    try:
        return await use_case.create_clinic(
            payload.model_dump(), current_user.get("id")
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


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


@router.get("/{clinic_id}", response_model=ClinicRead)
async def get_clinic(
    clinic_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: ClinicAdminUseCase = Depends(get_clinic_admin_use_case),
):
    """Return a clinic for administration."""
    try:
        return await use_case.get_clinic(clinic_id, current_user.get("id"))
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@router.put("/{clinic_id}", response_model=ClinicRead)
async def update_clinic(
    clinic_id: int,
    payload: ClinicUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: ClinicAdminUseCase = Depends(get_clinic_admin_use_case),
):
    """Update a clinic."""
    try:
        return await use_case.update_clinic(
            clinic_id,
            payload.model_dump(exclude_unset=True),
            current_user.get("id"),
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinic(
    clinic_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: ClinicAdminUseCase = Depends(get_clinic_admin_use_case),
):
    """Logically delete a clinic."""
    try:
        await use_case.deactivate_clinic(clinic_id, current_user.get("id"))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


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


@branch_router.get("", response_model=PaginatedBranchesResponse)
async def list_branches(
    skip: int = 0,
    limit: int = 100,
    clinic_id: Optional[int] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    current_user: dict = Depends(get_current_user),
    use_case: BranchAdminUseCase = Depends(get_branch_admin_use_case),
):
    """Return a paginated branch list for administration."""
    try:
        return await use_case.list_branches(
            user_id=current_user.get("id"),
            skip=skip,
            limit=limit,
            clinic_id=clinic_id,
            status=status_filter,
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.post("", response_model=BranchRead, status_code=status.HTTP_201_CREATED)
async def create_branch(
    payload: BranchCreate,
    current_user: dict = Depends(get_current_user),
    use_case: BranchAdminUseCase = Depends(get_branch_admin_use_case),
):
    """Create a branch."""
    try:
        return await use_case.create_branch(
            payload.model_dump(), current_user.get("id")
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.get("/{branch_id}", response_model=BranchRead)
async def get_branch(
    branch_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: BranchAdminUseCase = Depends(get_branch_admin_use_case),
):
    """Return a branch for administration."""
    try:
        return await use_case.get_branch(branch_id, current_user.get("id"))
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.put("/{branch_id}", response_model=BranchRead)
async def update_branch(
    branch_id: int,
    payload: BranchUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: BranchAdminUseCase = Depends(get_branch_admin_use_case),
):
    """Update a branch."""
    try:
        return await use_case.update_branch(
            branch_id,
            payload.model_dump(exclude_unset=True),
            current_user.get("id"),
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: BranchAdminUseCase = Depends(get_branch_admin_use_case),
):
    """Logically delete a branch."""
    try:
        await use_case.deactivate_branch(branch_id, current_user.get("id"))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.get("/{branch_id}/hours", response_model=list[ScheduleAdminRead])
async def list_branch_hours(
    branch_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: BranchHoursAdminUseCase = Depends(get_branch_hours_admin_use_case),
):
    """Return branch hours for administration."""
    try:
        return await use_case.list_hours(branch_id, current_user.get("id"))
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.post(
    "/{branch_id}/hours",
    response_model=ScheduleAdminRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_branch_hour(
    branch_id: int,
    payload: ScheduleCreate,
    current_user: dict = Depends(get_current_user),
    use_case: BranchHoursAdminUseCase = Depends(get_branch_hours_admin_use_case),
):
    """Create branch hours."""
    try:
        return await use_case.create_hour(
            branch_id,
            payload.model_dump(),
            current_user.get("id"),
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.put("/{branch_id}/hours/{hour_id}", response_model=ScheduleAdminRead)
async def update_branch_hour(
    branch_id: int,
    hour_id: int,
    payload: ScheduleUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: BranchHoursAdminUseCase = Depends(get_branch_hours_admin_use_case),
):
    """Update branch hours."""
    try:
        return await use_case.update_hour(
            branch_id,
            hour_id,
            payload.model_dump(exclude_unset=True),
            current_user.get("id"),
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc


@branch_router.delete(
    "/{branch_id}/hours/{hour_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_branch_hour(
    branch_id: int,
    hour_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: BranchHoursAdminUseCase = Depends(get_branch_hours_admin_use_case),
):
    """Delete branch hours."""
    try:
        await use_case.delete_hour(branch_id, hour_id, current_user.get("id"))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
