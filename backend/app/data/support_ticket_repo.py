"""Repositorio de soporte basico (BE-014).

Port ABC + implementacion sqlalchemy para la tabla support_tickets con
aislamiento por tenant (clinic_id) y owner isolation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.support_ticket_model import (
    SupportTicket as SupportTicketModel,
)
from app.infrastructure.database.models.support_ticket_model import (
    TicketCategory as TicketCategoryModel,
)

# ---- Domain entities -------------------------------------------------- #


class _SupportTicketDomain:
    """Vista minimal del ticket usado por use-cases (DDD-lite)."""

    def __init__(
        self,
        id: int,
        title: str,
        description: str | None,
        status: str,
        category_id: int | None,
        owner_id: int,
        clinic_id: int,
        created_at: datetime,
        updated_at: datetime,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.category_id = category_id
        self.owner_id = owner_id
        self.clinic_id = clinic_id
        self.created_at = created_at
        self.updated_at = updated_at


class _TicketCategoryDomain:
    """Vista minimal de la categoria."""

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


# ---- Helper ----------------------------------------------------------- #


def _to_domain(
    ticket_model: SupportTicketModel,
) -> tuple[_SupportTicketDomain, _TicketCategoryDomain | None]:
    cat_domain: _TicketCategoryDomain | None = None
    if ticket_model.category is not None:
        cat_domain = _TicketCategoryDomain(
            id=ticket_model.category.id, name=ticket_model.category.name
        )
    return (
        _SupportTicketDomain(
            id=ticket_model.id,
            title=ticket_model.title,
            description=ticket_model.description,
            status=ticket_model.status,
            category_id=ticket_model.category_id,
            owner_id=ticket_model.owner_id,
            clinic_id=ticket_model.clinic_id,
            created_at=ticket_model.created_at or datetime.now(UTC),
            updated_at=ticket_model.updated_at or datetime.now(UTC),
        ),
        cat_domain,
    )


# ---- Port ------------------------------------------------------------- #


class SupportTicketRepository(ABC):
    """Port para operaciones de soporte basico."""

    @abstractmethod
    async def create_ticket(
        self,
        title: str,
        description: str | None,
        category_id: int | None,
        owner_id: int,
        clinic_id: int,
    ) -> tuple[_SupportTicketDomain, _TicketCategoryDomain | None]: ...

    @abstractmethod
    async def find_recent_duplicate(
        self,
        title: str,
        owner_id: int,
        clinic_id: int,
        created_since: datetime,
    ) -> bool:
        """Indica si el owner ya creo el mismo titulo desde el limite dado."""
        ...

    @abstractmethod
    async def list_by_owner(
        self,
        owner_id: int,
        clinic_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> tuple[
        list[tuple[_SupportTicketDomain, _TicketCategoryDomain | None]], int
    ]: ...

    @abstractmethod
    async def get_by_id_for_owner(
        self, ticket_id: int, owner_id: int, clinic_id: int
    ) -> tuple[_SupportTicketDomain, _TicketCategoryDomain | None] | None:
        """Retorna None si no existe o es ajeno al tenant (BOLA seguro)."""
        ...

    @abstractmethod
    async def update_status(
        self, ticket_id: int, owner_id: int, clinic_id: int, new_status: str
    ) -> tuple[str, str] | None:
        """Retorna (old_status, new_status) o None si no existe/ajeno."""
        ...

    @abstractmethod
    async def list_by_clinic(
        self, clinic_id: int, page: int, page_size: int, status: str | None = None
    ) -> tuple[list[tuple[_SupportTicketDomain, _TicketCategoryDomain | None]], int]:
        """Listar por clinica (admin)."""
        ...

    @abstractmethod
    async def list_active_categories(
        self, clinic_id: int
    ) -> list[_TicketCategoryDomain]:
        """Categorias activas de una clinica."""
        ...


# ---- Implementation --------------------------------------------------- #


class SupportTicketRepositoryImpl(SupportTicketRepository):
    """Implementacion sqlalchemy del port de soporte basico."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def create_ticket(
        self,
        title: str,
        description: str | None,
        category_id: int | None,
        owner_id: int,
        clinic_id: int,
    ) -> tuple[_SupportTicketDomain, _TicketCategoryDomain | None]:
        model = SupportTicketModel(
            title=title.strip(),
            description=description.strip() if description else None,
            status="iniciado",
            category_id=category_id,
            owner_id=owner_id,
            clinic_id=clinic_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        domain, cat = _to_domain(model)
        return domain, cat

    async def find_recent_duplicate(
        self,
        title: str,
        owner_id: int,
        clinic_id: int,
        created_since: datetime,
    ) -> bool:
        normalized_title = title.strip().lower()
        stmt = (
            select(SupportTicketModel.id)
            .where(SupportTicketModel.owner_id == owner_id)
            .where(SupportTicketModel.clinic_id == clinic_id)
            .where(func.lower(func.trim(SupportTicketModel.title)) == normalized_title)
            .where(SupportTicketModel.created_at >= created_since)
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    async def list_by_owner(
        self,
        owner_id: int,
        clinic_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> tuple[list[tuple[_SupportTicketDomain, _TicketCategoryDomain | None]], int]:
        base_stmt = (
            select(SupportTicketModel)
            .where(SupportTicketModel.owner_id == owner_id)
            .where(SupportTicketModel.clinic_id == clinic_id)
        )
        if status:
            base_stmt = base_stmt.where(SupportTicketModel.status == status)

        total_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        paginated_stmt = (
            base_stmt.order_by(SupportTicketModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.db.execute(paginated_stmt).scalars().all()
        return [(_to_domain(r)) for r in rows], total

    async def get_by_id_for_owner(
        self,
        ticket_id: int,
        owner_id: int,
        clinic_id: int,
    ) -> tuple[_SupportTicketDomain, _TicketCategoryDomain | None] | None:
        stmt = (
            select(SupportTicketModel)
            .where(SupportTicketModel.id == ticket_id)
            .where(SupportTicketModel.owner_id == owner_id)
            .where(SupportTicketModel.clinic_id == clinic_id)
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return _to_domain(model)

    async def update_status(
        self,
        ticket_id: int,
        owner_id: int,
        clinic_id: int,
        new_status: str,
    ) -> tuple[str, str] | None:
        stmt = (
            select(SupportTicketModel)
            .where(SupportTicketModel.id == ticket_id)
            .where(SupportTicketModel.owner_id == owner_id)
            .where(SupportTicketModel.clinic_id == clinic_id)
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        old_status = model.status
        model.status = new_status
        model.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return (old_status, new_status)

    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> tuple[list[tuple[_SupportTicketDomain, _TicketCategoryDomain | None]], int]:
        base_stmt = select(SupportTicketModel).where(
            SupportTicketModel.clinic_id == clinic_id
        )
        if status:
            base_stmt = base_stmt.where(SupportTicketModel.status == status)

        total_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        paginated_stmt = (
            base_stmt.order_by(SupportTicketModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.db.execute(paginated_stmt).scalars().all()
        return [(_to_domain(r)) for r in rows], total

    async def list_active_categories(
        self, clinic_id: int
    ) -> list[_TicketCategoryDomain]:
        stmt = (
            select(TicketCategoryModel)
            .where(
                TicketCategoryModel.clinic_id == clinic_id,
                TicketCategoryModel.active == True,  # noqa: E712
            )
            .order_by(TicketCategoryModel.name)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [_TicketCategoryDomain(id=r.id, name=r.name) for r in rows]


def get_support_ticket_repo(db: Session) -> SupportTicketRepository:
    """Factory del repositorio de soporte basico."""
    return SupportTicketRepositoryImpl(db)
