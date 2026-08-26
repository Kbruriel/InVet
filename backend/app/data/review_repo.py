"""Repositorio de reseñas y respuestas clinicas para BE-012.

Concentra la interface (ABC) y la implementacion SQLAlchemy para mantener el
acceso a datos tipado y testeable sin logica de negocio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.review import Review, ReviewResponse
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.review import (
    Review as ReviewModel,
    ReviewResponse as ReviewResponseModel,
)


def _response_from_model(model: ReviewResponseModel | None) -> ReviewResponse | None:
    """Convierte el ORM de respuesta a entidad de dominio (None-safe)."""
    if model is None:
        return None
    return ReviewResponse(
        id=model.id,
        review_id=model.review_id,
        branch_id=model.branch_id,
        user_id=model.user_id,
        body=model.body,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _domain_from_model(
    model: ReviewModel, response: ReviewResponseModel | None = None
) -> Review:
    """Convierte un modelo ORM de reseña a entidad de dominio."""
    return Review(
        id=model.id,
        appointment_id=model.appointment_id,
        branch_id=model.branch_id,
        clinic_id=model.clinic_id,
        user_id=model.user_id,
        rating=model.rating,
        comment=model.comment,
        response=_response_from_model(response),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class ReviewRepository(ABC):
    """Interface para el repositorio de reseñas."""

    @abstractmethod
    async def create(self, review: Review) -> Review:
        """Crear y persistir una reseña (unica por cita)."""
        pass

    @abstractmethod
    async def exists_by_appointment(
        self, appointment_id: int
    ) -> bool:
        """Verificar si la cita ya tiene una reseña."""
        pass

    @abstractmethod
    async def get_by_id(
        self, review_id: int, clinic_id: int
    ) -> Review | None:
        """Obtener reseña por ID con aislamiento de tenant (clinic_id)."""
        pass

    @abstractmethod
    async def exists_by_id(
        self, review_id: int, clinic_id: int
    ) -> bool:
        """Verificar si la reseña existe en el tenant."""
        pass

    @abstractmethod
    async def list_by_branch(
        self,
        branch_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int]:
        """Listado publico paginado de reseñas por sucursal (mas recientes primero)."""
        pass

    @abstractmethod
    async def list_by_clinic(
        self,
        clinic_id: int,
        branch_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int]:
        """Listado clinico paginado por tenant, opcionalmente filtrado por sucursal."""
        pass

    @abstractmethod
    async def create_response(self, response: ReviewResponse) -> ReviewResponse:
        """Crear y persistir una respuesta clínica (unica por reseña)."""
        pass

    @abstractmethod
    async def get_response_by_review(
        self, review_id: int
    ) -> ReviewResponse | None:
        """Obtener la respuesta clínica de una reseña (unica)."""
        pass

    @abstractmethod
    async def get_review_stats(
        self, branch_id: int
    ) -> tuple[int, dict[int, int]]:
        """Obtener total de reseñas y distribucion por calificacion de una sucursal."""
        pass

    @abstractmethod
    async def get_owner_id_by_user(
        self, user_id: int
    ) -> int | None:
        """Devolver el ID del propietario asociado al usuario (si existe)."""
        pass

    @abstractmethod
    async def get_internal_user_id_by_user(
        self, user_id: int
    ) -> int | None:
        """Devolver el ID de la fila `internal_users` asociada al usuario."""
        pass


class ReviewRepositoryImpl(ReviewRepository):
    """Implementacion SQLAlchemy del repositorio de reseñas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def create(self, review: Review) -> Review:
        """Crear y persistir una reseña; devuelve la entidad con ID asignado."""
        model = ReviewModel(
            appointment_id=review.appointment_id,
            branch_id=review.branch_id,
            clinic_id=review.clinic_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model, self._load_response(model.id))

    async def exists_by_appointment(self, appointment_id: int) -> bool:
        """True si la cita ya fue califica (unique appointment_id)."""
        stmt = (
            select(ReviewModel.id)
            .where(ReviewModel.appointment_id == appointment_id)
            .limit(1)
        )
        return self.db.execute(stmt).first() is not None

    async def get_by_id(
        self, review_id: int, clinic_id: int
    ) -> Review | None:
        """Obtener reseña por ID y clinic_id (tenant isolation)."""
        stmt = (
            select(ReviewModel)
            .where(ReviewModel.id == review_id)
            .where(ReviewModel.clinic_id == clinic_id)
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return _domain_from_model(model, self._load_response(model.id))

    async def exists_by_id(
        self, review_id: int, clinic_id: int
    ) -> bool:
        """True si la reseña existe en el tenant."""
        stmt = (
            select(ReviewModel.id)
            .where(ReviewModel.id == review_id)
            .where(ReviewModel.clinic_id == clinic_id)
            .limit(1)
        )
        return self.db.execute(stmt).first() is not None

    async def list_by_branch(
        self,
        branch_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int]:
        """Listado publico paginado de reseñas de una sucursal."""
        base_stmt = select(ReviewModel).where(ReviewModel.branch_id == branch_id)
        base_stmt = base_stmt.order_by(ReviewModel.id.desc())

        total = (
            self.db.execute(
                select(func.count()).select_from(base_stmt.subquery())
            ).scalar()
            or 0
        )

        offset = (page - 1) * page_size
        results = (
            self.db.execute(base_stmt.offset(offset).limit(page_size)).scalars().all()
        )
        items = [
            _domain_from_model(r, self._load_response(r.id)) for r in results
        ]
        return items, total

    async def list_by_clinic(
        self,
        clinic_id: int,
        branch_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int]:
        """Listado clinico por tenant, opcionalemente filtrado por sucursal."""
        base_stmt = select(ReviewModel).where(ReviewModel.clinic_id == clinic_id)
        if branch_id is not None:
            base_stmt = base_stmt.where(ReviewModel.branch_id == branch_id)
        base_stmt = base_stmt.order_by(ReviewModel.id.desc())

        total = (
            self.db.execute(
                select(func.count()).select_from(base_stmt.subquery())
            ).scalar()
            or 0
        )

        offset = (page - 1) * page_size
        results = (
            self.db.execute(base_stmt.offset(offset).limit(page_size)).scalars().all()
        )
        items = [
            _domain_from_model(r, self._load_response(r.id)) for r in results
        ]
        return items, total

    async def create_response(self, response: ReviewResponse) -> ReviewResponse:
        """Crear y persistir una respuesta clínica unica por reseña."""
        model = ReviewResponseModel(
            review_id=response.review_id,
            branch_id=response.branch_id,
            user_id=response.user_id,
            body=response.body,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return ReviewResponse(
            id=model.id,
            review_id=model.review_id,
            branch_id=model.branch_id,
            user_id=model.user_id,
            body=model.body,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_response_by_review(
        self, review_id: int
    ) -> ReviewResponse | None:
        """Obtener la respuesta clínica (unica) de una reseña."""
        stmt = (
            select(ReviewResponseModel)
            .where(ReviewResponseModel.review_id == review_id)
            .limit(1)
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        return _response_from_model(model)

    async def get_review_stats(
        self, branch_id: int
    ) -> tuple[int, dict[int, int]]:
        """Total de reseñas y distribucion por calificacion de la sucursal."""
        stmt = select(ReviewModel.rating).where(
            ReviewModel.branch_id == branch_id
        )
        ratings = self.db.execute(stmt).scalars().all()

        distribution: dict[int, int] = {i: 0 for i in range(1, 6)}
        for rating in ratings:
            if isinstance(rating, int) and rating in distribution:
                distribution[rating] += 1
        return len(ratings), distribution

    async def get_owner_id_by_user(self, user_id: int) -> int | None:
        """Devolver el ID del propietario asociado al usuario (si existe)."""
        stmt = (
            select(OwnerModel.id)
            .where(
                OwnerModel.user_id == user_id,
                OwnerModel.is_active.is_(True),
            )
            .limit(1)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    async def get_internal_user_id_by_user(self, user_id: int) -> int | None:
        """Devolver el ID de la fila `internal_users` asociada al usuario."""
        from app.infrastructure.database.models.internal_user_model import (
            InternalUser as InternalUserModel,
        )

        stmt = (
            select(InternalUserModel.id)
            .where(
                InternalUserModel.user_id == user_id,
                InternalUserModel.is_active.is_(True),
            )
            .limit(1)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    def _load_response(self, review_id: int) -> ReviewResponseModel | None:
        """Cargar la respuesta ORM (unica) asociada a una reseña."""
        stmt = (
            select(ReviewResponseModel)
            .where(ReviewResponseModel.review_id == review_id)
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()


def get_review_repo(db: Session) -> ReviewRepository:
    """Obtener una instancia concreta del repositorio de reseñas."""
    return ReviewRepositoryImpl(db)
