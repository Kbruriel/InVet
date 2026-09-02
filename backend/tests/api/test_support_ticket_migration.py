"""Validacion de la migracion de soporte basico (BE-014-T01, AC-01/02/06/10).

Validacion declarada en el plan: "Aplicar migración en base aislada."

Por que Postgres: a014 usa `op.create_unique_constraint`, que el dialecto
SQLite no soporta sin batch mode. Si el server no esta disponible o psycopg2
no existe, la prueba se omite (skip) y NO se trata como fail.

Estrategia (reproduce el estado real del despliegue `invet` y prueba SOLO a014;
nunca toca `invet`):
  1. Crea una base PostgreSQL aislada `beat_be014_<8hex>` y la elimina al
     terminar.
  2. Apunta `settings.DATABASE_URL` a la aislada ANTES de lanzar Alembic
     (`alembic/env.py` lo lee en tiempo de llamada y SOBRESCRIBE
     `sqlalchemy.url`, de modo que stamp/upgrade/downgrade corren contra la
     aislada).
  3. Crea el esquema base del paquete `app.infrastructure.database.models`
     (igual que `docker-compose` con `Base.metadata.create_all`) y fija
     `alembic_version = a013`, la revision actual del despliegue. Los modelos
     de soporte sí están registrados en `models/__init__.py`, por lo que
     `create_all` puede crear sus tablas; la prueba las elimina explícitamente
     para garantizar un pre-state a013 independiente del orden de importación
     de otras pruebas.
  4. `alembic upgrade a014` debe crear SOLO las tablas de soporte:
     - `ticket_categories` (unicidad por (clinic_id, name), indice por clinic,
       FK a clinics con CASCADE, seed de 3 categorias activas idempotente)
     - `support_tickets` (indices owner/clinic/status, FKs con CASCADE)
  5. `alembic downgrade a013` debe revertir ambas tablas (reversion funcional).
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

# Asegurar raiz de import (backend) para `app.*`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import sqlalchemy as sa  # noqa: E402

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

# The test is located at ``backend/tests/api`` on the host and at
# ``/app/tests/api`` in the backend image.  Resolving from the test package
# keeps both executions portable; relying on a hard-coded ``/backend`` path
# breaks Docker because Compose uses ``/app`` as its workdir.
BACKEND_DIR = Path(__file__).resolve().parents[2]
MIGRATION_PATH = BACKEND_DIR / "alembic" / "versions" / "a014_support.py"
EXPECTED_CATEGORIES = {"Fattura", "Comportamiento", "Veterinaria"}

try:
    import psycopg2  # noqa: F401

    _HAS_PSYCOPG2 = True
except ImportError:  # pragma: no cover
    psycopg2 = None  # type: ignore[assignment]
    _HAS_PSYCOPG2 = False

pytestmark = [
    pytest.mark.skipif(
        os.environ.get("RUN_BE014_ISOLATED_MIGRATION", "1") not in ("1", "true"),
        reason="Validacion de migracion deshabilitada por RUN_BE014_ISOLATED_MIGRATION.",
    ),
    pytest.mark.skipif(not _HAS_PSYCOPG2, reason="psycopg2 no disponible."),
]


def _reachable(url: str) -> bool:
    """True si el endpoint PostgreSQL responde con SELECT 1 dentro del timeout."""
    from sqlalchemy import create_engine  # noqa: PLC0415

    engine = create_engine(url, connect_args={"connect_timeout": 4})
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        engine.dispose()


def _pg_base() -> str:
    """Devuelve el BASE_URL (psycopg2) del Postgres disponible o omite la prueba."""
    from app.core.config import settings  # noqa: PLC0415

    base = (settings.DATABASE_URL or "").strip()
    if not base:
        pytest.skip("DATABASE_URL no esta configurada.")
    base = base.replace("postgresql://", "postgresql+psycopg2://", 1)
    if not _reachable(base):
        pytest.skip("No hay Postgres disponible para validar a014 en base aislada.")
    return base


def _alembic_cfg(url: str) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic" / "alembic.ini"))
    cfg.file_config.set("alembic", "script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def _register_base_models() -> type[object]:
    """Registra el paquete base y devuelve Base (metadatos de modelos base)."""
    import app.infrastructure.database.models  # noqa: F401  (registra la base)
    from app.infrastructure.database.models.base import Base  # noqa: PLC0415

    return Base


@pytest.fixture()
def isolated_pg():
    """Base PostgreSQL aislada + estado previo (base + a013); se elimina al terminar."""
    base = _pg_base()
    Base = _register_base_models()
    assert Base.metadata.tables, "Base.metadata vacio: no hay modelos base registrados."

    from sqlalchemy import text  # noqa: PLC0415

    from app.core.config import settings  # noqa: PLC0415

    original_url = settings.DATABASE_URL
    server = base[: base.rfind("/")]
    iso_db = f"beat_be014_{uuid.uuid4().hex[:8]}"
    iso_url = f"{server}/{iso_db}"

    # CRITICO: alembic/env.py sobrescribe sqlalchemy.url con settings.DATABASE_URL,
    # por lo que la aislada se fija ANTES de cualquier comando alembic.
    settings.DATABASE_URL = iso_url

    admin_engine = sa.create_engine(server, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            conn.execute(sa.text(f'CREATE DATABASE "{iso_db}"'))
    except sa.exc.ProgrammingError as exc:
        admin_engine.dispose()
        settings.DATABASE_URL = original_url
        pytest.skip(f"No se pudo crear base aislada: {exc}")

    engine = sa.create_engine(iso_url)

    # Estado previo equivalente al despliegue: esquema base + alembic_version a013.
    Base.metadata.create_all(engine)
    with engine.begin() as c:
        # Garantiza el pre-state en la BD aunque otra prueba haya registrado el
        # modelo de soporte en los metadatos globales (el orden de import no debe
        # invalidar la validez de esta prueba): elimina tablas de soporte si existieran.
        c.execute(text('DROP TABLE IF EXISTS "support_tickets" CASCADE'))
        c.execute(text('DROP TABLE IF EXISTS "ticket_categories" CASCADE'))
        c.execute(
            text("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)")
        )
        c.execute(text("INSERT INTO alembic_version (version_num) VALUES ('a013')"))

    try:
        yield iso_url, engine, iso_db
    finally:
        try:
            engine.dispose()
        finally:
            settings.DATABASE_URL = original_url
            try:
                with admin_engine.connect() as conn:
                    conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{iso_db}"'))
            except Exception:  # pragma: no cover
                pass
            admin_engine.dispose()


def _insert_clinic(engine: sa.Engine, name: str) -> int:
    with engine.begin() as c:
        c.execute(
            sa.text(
                "INSERT INTO clinics (name, address, city, state, country, postal_code) "
                "VALUES (:n,'A','B','C','P','1')"
            ),
            {"n": name},
        )
        return c.execute(sa.text("SELECT id FROM clinics WHERE name = :n"), {"n": name}).scalar()  # type: ignore[return-value]


def _insert_owner(engine: sa.Engine, email: str, clinic_id: int) -> int:
    with engine.begin() as c:
        c.execute(
            sa.text(
                "INSERT INTO owners (first_name, last_name, email, clinic_id) "
                "VALUES ('Juan','Perez',:e,:cid)"
            ),
            {"e": email, "cid": clinic_id},
        )
        return c.execute(sa.text("SELECT id FROM owners WHERE email = :e"), {"e": email}).scalar()  # type: ignore[return-value]


class TestA014MigrationFile:
    """La migracion a014 existe con hooks de upgrade/downgrade (precondicion)."""

    def test_migration_file_exists_with_hooks(self):
        assert MIGRATION_PATH.exists(), f"Falta la migracion en {MIGRATION_PATH}"
        import importlib.util

        spec = importlib.util.spec_from_file_location("a014_support", MIGRATION_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert getattr(module, "revision", None) == "a014"
        assert getattr(module, "down_revision", None) == "a013"
        assert callable(getattr(module, "upgrade", None))
        assert callable(getattr(module, "downgrade", None))


class TestA014MigrationOnIsolatedDatabase:
    """Validacion declarada: aplicar (y revertir) la migracion en base aislada."""

    def test_upgrade_a014_creates_schema_and_seed(self, isolated_pg):
        url, engine, _db = isolated_pg
        from sqlalchemy import text

        pre = sa.inspect(engine).get_table_names()
        assert "clinics" in pre and "owners" in pre, f"faltan tablas base: {pre}"
        assert (
            "ticket_categories" not in pre
        ), "pre-state no debe incluir ticket_categories"
        assert "support_tickets" not in pre, "pre-state no debe incluir support_tickets"

        _insert_clinic(engine, "Clinica T01")  # dispara el seed de a014

        command.upgrade(_alembic_cfg(url), "a014")

        with engine.connect() as c:
            assert (
                c.execute(text("SELECT version_num FROM alembic_version")).scalar()
                == "a014"
            )

        insp = sa.inspect(engine)
        tables = insp.get_table_names()
        assert "ticket_categories" in tables
        assert "support_tickets" in tables

        unique = [u["name"] for u in insp.get_unique_constraints("ticket_categories")]
        tc_idx = [i["name"] for i in insp.get_indexes("ticket_categories")]
        st_idx = [i["name"] for i in insp.get_indexes("support_tickets")]
        tc_fk = insp.get_foreign_keys("ticket_categories")
        st_fk = insp.get_foreign_keys("support_tickets")

        assert "uq_ticket_category_clinic" in unique, f"unicidad ausente: {unique}"
        assert "ix_ticket_categories_clinic_id" in tc_idx, tc_idx
        for expected in (
            "ix_support_tickets_owner_id",
            "ix_support_tickets_clinic_id",
            "ix_support_tickets_status",
        ):
            assert expected in st_idx, f"indice faltante {expected} en {st_idx}"

        assert any(
            f["referred_table"] == "clinics" for f in tc_fk
        ), "falta FK ticket_categories->clinics"
        assert any(
            f["referred_table"] == "clinics"
            and f.get("options", {}).get("ondelete") == "CASCADE"
            for f in tc_fk
        ), "falta CASCADE en ticket_categories->clinics"

        st_referred = {f["referred_table"] for f in st_fk}
        assert st_referred == {"ticket_categories", "owners", "clinics"}, st_referred
        for target in ("owners", "clinics"):
            fk = next(f for f in st_fk if f["referred_table"] == target)
            assert (
                fk.get("options", {}).get("ondelete") == "CASCADE"
            ), f"CASCADE falta hacia {target}"

        with engine.connect() as c:
            rows = c.execute(
                text(
                    "SELECT name, active, description FROM ticket_categories ORDER BY name"
                )
            ).fetchall()
        assert {r[0] for r in rows} == EXPECTED_CATEGORIES, [r[0] for r in rows]
        assert all(bool(r[1]) for r in rows), "categorias no estan activas"
        assert all(r[2] for r in rows), "categorias sin descripcion"

        # Idempotencia: reaplicar upgrade no duplica categorias.
        command.upgrade(_alembic_cfg(url), "a014")
        with engine.connect() as c:
            n = c.execute(text("SELECT count(*) FROM ticket_categories")).scalar()
        assert n == 3, f"seed no idempotente: {n}"

    def test_unique_per_clinic_enforced(self, isolated_pg):
        url, engine, _db = isolated_pg
        clinic_id = _insert_clinic(engine, "Clinica U")
        command.upgrade(_alembic_cfg(url), "a014")

        # 'Cat Unica T01' NO pertenece al seed: permite probar la unicidad por
        # (clinic_id, name) de forma aislada insertando dos veces el mismo nombre.
        with engine.begin() as c:
            c.execute(
                sa.text(
                    "INSERT INTO ticket_categories (clinic_id, name) VALUES (:cid, 'Cat Unica T01')"
                ),
                {"cid": clinic_id},
            )
        try:
            with engine.begin() as c:
                c.execute(
                    sa.text(
                        "INSERT INTO ticket_categories (clinic_id, name) VALUES (:cid, 'Cat Unica T01')"
                    ),
                    {"cid": clinic_id},
                )
            pytest.fail(
                "UNIQUE (clinic_id, name) no aplico: se duplico la categoria en la misma clinica."
            )
        except sa.exc.IntegrityError as exc:
            assert "unique" in str(exc).lower()

    def test_downgrade_a014_reverts_schema(self, isolated_pg):
        url, engine, _db = isolated_pg
        from sqlalchemy import text

        clinic_id = _insert_clinic(engine, "Clinica D")
        owner_id = _insert_owner(engine, "owner.t01@invet.test", clinic_id)
        command.upgrade(_alembic_cfg(url), "a014")

        assert "ticket_categories" in sa.inspect(engine).get_table_names()
        assert "support_tickets" in sa.inspect(engine).get_table_names()

        # Un ticket sobre la categoria sembrada (owner_id es NOT NULL): el
        # downgrade debe poder revertir ambas tablas sin filas orfanas.
        with engine.begin() as c:
            c.execute(
                sa.text(
                    "INSERT INTO support_tickets (title, description, status, category_id, owner_id, clinic_id) "
                    "VALUES ('T01','D','iniciado',(SELECT id FROM ticket_categories WHERE name='Fattura'),:oid,:cid)"
                ),
                {"oid": owner_id, "cid": clinic_id},
            )

        command.downgrade(_alembic_cfg(url), "a013")

        after = sa.inspect(engine).get_table_names()
        assert (
            "ticket_categories" not in after
        ), "downgrade no elimino ticket_categories"
        assert "support_tickets" not in after, "downgrade no elimino support_tickets"
        with engine.connect() as c:
            assert (
                c.execute(text("SELECT version_num FROM alembic_version")).scalar()
                == "a013"
            )
