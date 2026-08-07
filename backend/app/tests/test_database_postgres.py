"""Pruebas de integracion reales contra PostgreSQL cuando el driver esta disponible."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

from app.core.config import settings

pytest.importorskip("psycopg2")


def _postgres_url() -> str:
    """Devuelve una URL PostgreSQL util para la validacion del slice."""
    return os.getenv(
        "INVET_TEST_DATABASE_URL",
        settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1),
    )


def test_postgres_round_trip_query() -> None:
    engine = create_engine(_postgres_url(), poolclass=NullPool)

    try:
        with engine.begin() as connection:
            server_version = connection.execute(text("SELECT version()")).scalar_one()
            connection.execute(
                text(
                    """
                    CREATE TEMP TABLE qf_006_probe (
                        id SERIAL PRIMARY KEY,
                        label TEXT NOT NULL
                    )
                    """
                )
            )
            connection.execute(
                text("INSERT INTO qf_006_probe (label) VALUES (:label)"),
                {"label": "postgres-ok"},
            )
            rows = connection.execute(
                text("SELECT label FROM qf_006_probe ORDER BY id")
            ).fetchall()
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL no disponible para este entorno: {exc}")

    assert "PostgreSQL" in server_version
    assert [row[0] for row in rows] == ["postgres-ok"]
