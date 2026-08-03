"""Bootstrap helpers for additive runtime schema fixes."""

from __future__ import annotations

from sqlalchemy import inspect, text


def _seed_default_clinic_branch(connection) -> None:
    """Ensure the default clinic/branch pair exists for branch-scoped tests."""
    connection.execute(
        text(
            """
            INSERT INTO clinics (
                id, name, address, city, state, country, postal_code, is_active
            )
            VALUES (
                1, 'Clinica de pruebas', 'Calle de pruebas 123',
                'Ciudad de pruebas', 'Estado de pruebas', 'MX', '00000', true
            )
            ON CONFLICT (id) DO NOTHING
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO branches (
                id, clinic_id, name, address, city, state, country, postal_code, is_active
            )
            VALUES (
                1, 1, 'Sucursal principal', 'Calle de pruebas 123',
                'Ciudad de pruebas', 'Estado de pruebas', 'MX', '00000', true
            )
            ON CONFLICT (id) DO NOTHING
            """
        )
    )
    connection.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('clinics', 'id'), "
            "(SELECT COALESCE(MAX(id), 1) FROM clinics), true)"
        )
    )
    connection.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('branches', 'id'), "
            "(SELECT COALESCE(MAX(id), 1) FROM branches), true)"
        )
    )


def ensure_runtime_schema(engine) -> None:
    """Apply tiny additive schema fixes needed by the current runtime."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("users"):
            return

        connection.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR")
        )
        connection.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR")
        )
        if inspector.has_table("clinics") and inspector.has_table("branches"):
            _seed_default_clinic_branch(connection)


def ensure_test_branch_seed(engine) -> None:
    """Seed branch-dependent tables in isolated test schemas."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if inspector.has_table("clinics") and inspector.has_table("branches"):
            _seed_default_clinic_branch(connection)
