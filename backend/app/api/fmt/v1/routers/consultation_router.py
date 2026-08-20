# ---------------------------------------------------------------------------
# GET /consultations/{id} — obtener detalle
# ---------------------------------------------------------------------------
@router.get(
    "/{consultation_id}",
    response_model=ConsultationRead,
    summary="Obtener detalle de una consulta",
)
async def get_consultation(
    consultation_id: int,
    current_user: dict = Depends(get_current_access_user),
    consultation_repo: ConsultationRepository = Depends(get_consultation_repo),
) -> ConsultationRead:
    """Obtener detalle de una consulta específica.

    - Solo usuarios de la misma clínica pueden verla (403/404).
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    use_case = GetConsultationUseCase(consultation_repo)

    try:
        result = await use_case.execute(consultation_id, clinic_id)
        return ConsultationRead.model_validate(result)
    except ConsultationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from None


# ---------------------------------------------------------------------------
# GET /consultations — listar consultas (con paginación y filtro)
# ---------------------------------------------------------------------------
@router.get(
    "",
    response_model=ConsultationPage,
    summary="Listar consultas de la clínica",
)
async def list_consultations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    pet_id: int | None = Query(None),
    current_user: dict = Depends(get_current_access_user),
    consultation_repo: ConsultationRepository = Depends(get_consultation_repo),
    use_case: ListConsultationsUseCase = Depends(
        lambda repo: ListConsultationsUseCase(repo)
    ),
) -> ConsultationPage:
    """Listar las consultas de la clínica con paginación.

    - Solo usuarios de la misma clínica pueden verlas.
    - Permite filtrar por `pet_id`.
    """
    clinic_id = _get_clinic_id_from_user(current_user)

    items, total = await use_case.execute(
        clinic_id=clinic_id, page=page, size=size, pet_id=pet_id
    )

    return ConsultationPage(
        items=[ConsultationRead.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )
