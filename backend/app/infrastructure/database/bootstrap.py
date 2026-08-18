"""Bootstrap helpers for additive runtime schema fixes."""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection, Engine

from app.core.security import get_password_hash


def _seed_default_clinic_branch(connection: Connection) -> None:
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


def _seed_default_auth_accounts(connection: Connection) -> None:
    """Ensure the default QA/admin accounts exist for browser and API checks."""
    password_hash = get_password_hash("secret123")

    connection.execute(
        text(
            """
            INSERT INTO users (
                email, username, hashed_password, first_name, last_name, is_active, is_admin,
                created_at, updated_at
            )
            VALUES
                ('qa@example.com', 'qa@example.com', :password_hash, 'QA', 'Admin', true, true, NOW(), NOW()),
                ('admin@example.com', 'admin@example.com', :password_hash, 'Admin', 'InVet', true, true, NOW(), NOW()),
                ('clinic@example.com', 'clinic@example.com', :password_hash, 'Clinic', 'Viewer', true, false, NOW(), NOW()),
                ('vet@example.com', 'vet@example.com', :password_hash, 'Vet', 'Viewer', true, false, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET
                username = EXCLUDED.username,
                hashed_password = EXCLUDED.hashed_password,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                is_active = EXCLUDED.is_active,
                is_admin = EXCLUDED.is_admin,
                created_at = COALESCE(users.created_at, EXCLUDED.created_at),
                updated_at = EXCLUDED.updated_at
            """
        ),
        {"password_hash": password_hash},
    )

    connection.execute(
        text(
            """
            INSERT INTO owners (
                user_id, first_name, last_name, email, phone, address,
                city, state, country, postal_code, is_active, clinic_id
            )
            SELECT u.id, 'QA', 'Admin', u.email, '555-0101', 'Calle QA 1',
                   'Ciudad de pruebas', 'Estado de pruebas', 'MX', '00000', true, 1
            FROM users u
            WHERE u.email = 'qa@example.com'
              AND NOT EXISTS (
                  SELECT 1 FROM owners o WHERE o.user_id = u.id
              )
            """
        )
    )

    connection.execute(
        text(
            """
            INSERT INTO owners (
                user_id, first_name, last_name, email, phone, address,
                city, state, country, postal_code, is_active, clinic_id
            )
            SELECT u.id, 'Admin', 'InVet', u.email, '555-0102', 'Calle Admin 1',
                   'Ciudad de pruebas', 'Estado de pruebas', 'MX', '00000', true, 1
            FROM users u
            WHERE u.email = 'admin@example.com'
              AND NOT EXISTS (
                  SELECT 1 FROM owners o WHERE o.user_id = u.id
              )
            """
        )
    )

    connection.execute(
        text(
            """
            INSERT INTO owners (
                user_id, first_name, last_name, email, phone, address,
                city, state, country, postal_code, is_active, clinic_id
            )
            SELECT u.id, 'Clinic', 'Viewer', u.email, '555-0103', 'Calle Clinic 1',
                   'Ciudad de pruebas', 'Estado de pruebas', 'MX', '00000', true, 1
            FROM users u
            WHERE u.email = 'clinic@example.com'
              AND NOT EXISTS (
                  SELECT 1 FROM owners o WHERE o.user_id = u.id
              )
            """
        )
    )

    connection.execute(
        text(
            """
            INSERT INTO internal_users (
                user_id, clinic_id, branch_id, nombre, name, last_name, email, rol, role,
                password_hash, branch_ids, is_active
            )
            SELECT
                u.id,
                1,
                1,
                'Vet Viewer',
                'Vet',
                'Viewer',
                u.email,
                'manager',
                'manager',
                :password_hash,
                '[]',
                true
            FROM users u
            WHERE u.email = 'vet@example.com'
              AND NOT EXISTS (
                  SELECT 1 FROM internal_users i WHERE i.user_id = u.id
              )
            """
        ),
        {"password_hash": password_hash},
    )


def ensure_runtime_schema(engine: Engine) -> None:
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
        if inspector.has_table("internal_users"):
            internal_user_columns = {
                column["name"] for column in inspector.get_columns("internal_users")
            }
            internal_user_alters = [
                ("user_id", "INTEGER"),
                ("clinic_id", "INTEGER"),
                ("nombre", "VARCHAR(200)"),
                ("rol", "VARCHAR(50)"),
                ("branch_ids", "TEXT"),
                ("is_active", "BOOLEAN"),
                ("created_at", "TIMESTAMP"),
                ("updated_at", "TIMESTAMP"),
            ]
            for column_name, column_type in internal_user_alters:
                if column_name not in internal_user_columns:
                    connection.execute(
                        text(
                            f"ALTER TABLE internal_users ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                        )
                    )
        if inspector.has_table("clinics") and inspector.has_table("branches"):
            _seed_default_clinic_branch(connection)
        if (
            inspector.has_table("users")
            and inspector.has_table("owners")
            and inspector.has_table("internal_users")
        ):
            _seed_default_auth_accounts(connection)


def ensure_test_branch_seed(engine: Engine) -> None:
    """Seed branch-dependent tables in isolated test schemas."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if inspector.has_table("clinics") and inspector.has_table("branches"):
            _seed_default_clinic_branch(connection)
