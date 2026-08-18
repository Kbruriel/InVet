"""Utilidades compartidas para validación de query params públicos."""

from __future__ import annotations

from fastapi import HTTPException, Request, status


def reject_unknown_query_params(request: Request, allowed: set[str]) -> None:
    """Rechaza query params que no formen parte del contrato público."""
    invalid = [key for key in request.query_params.keys() if key not in allowed]
    if not invalid:
        return

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=[
            {
                "loc": ["query", key],
                "msg": "Parámetro de consulta no permitido",
                "type": "value_error.extra",
            }
            for key in invalid
        ],
    )


def resolve_public_page_size(
    size: int,
    limit: int | None = None,
    page_size: int | None = None,
) -> int:
    """Normaliza aliases públicos del tamaño de página.

    Prioridad:
    1. limit
    2. page_size
    3. size
    """
    if limit is not None:
        return limit
    if page_size is not None:
        return page_size
    return size
