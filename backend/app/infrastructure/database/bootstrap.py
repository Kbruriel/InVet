"""Bootstrap helpers for additive runtime schema fixes."""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection, Engine

from app.core.security import get_password_hash


def _ensure_consultation_seed(connection: Connection) -> None:
    """Drop a stale ``appointments`` table (missing ``pet_id``) and seed the
    minimum consultation happy-path fixtures: pet 1 owned by the QA owner and
    a completed appointment 1 for that pet.

    ``create_all`` (checkfirst) never alters an existing table, so when a legacy
    ``appointments`` schema is present we drop it and let the current ORM model
    recreate the correct shape. Idempotent: all INSERTs use ON CONFLICT guards.
    """
    inspector = inspect(connection)
    if not inspector.has_table("pets"):
        return

    pet_columns = {column["name"] for column in inspector.get_columns("pets")}
    if "has_medical_history" not in pet_columns:
        connection.execute(
            text("ALTER TABLE pets ADD COLUMN IF NOT EXISTS has_medical_history BOOLEAN")
        )

    needs_recreate = False
    if inspector.has_table("appointments"):
        appointment_columns = {
            column["name"] for column in inspector.get_columns("appointments")
        }
        needs_recreate = "pet_id" not in appointment_columns
    else:
        needs_recreate = True

    if needs_recreate:
        connection.execute(
            text("DROP TABLE IF EXISTS appointments CASCADE")
        )
        # Import the appointment model here so its table is registered in the
        # current process metadata before asking SQLAlchemy to create it.
        from app.infrastructure.database.models.appointment import (
            Appointment,  # noqa: F401
        )
        from app.infrastructure.database.models.base import Base
        from app.infrastructure.database.models.pet import Pet  # noqa: F401

        Base.metadata.create_all(
            bind=connection, tables=[Appointment.__table__, Pet.__table__]
        )

    # Seed pet 1 -> clinic owner (owner of user 'clinic@test.com'). The
    # Playwright owner tests use the seeded clinic account, so bind
    # pet 1 to the clinic owner account instead of the lowest-id owner. Fall back
    # to the lowest owner row if the clinic account is absent.
    connection.execute(
        text(
            """
            INSERT INTO pets (
                id, owner_id, name, species, breed, color, gender, weight,
                date_of_birth, has_medical_history, is_active, created_at, updated_at
            )
            SELECT 1, o.id, 'Firulais', 'gato', 'domestico', 'gris', 'macho', '4',
                   NOW() - INTERVAL '3 years', false, true, NOW(), NOW()
            FROM owners o
            WHERE NOT EXISTS (SELECT 1 FROM pets p WHERE p.id = 1)
              AND (
                o.id = (
                    SELECT o2.id FROM owners o2
                    JOIN users u2 ON u2.id = o2.user_id
                    WHERE u2.email = 'clinic@test.com'
                    LIMIT 1
                )
                OR NOT EXISTS (
                    SELECT 1 FROM owners o2 JOIN users u2 ON u2.id = o2.user_id
                    WHERE u2.email = 'clinic@test.com'
                )
              )
            ORDER BY o.id
            LIMIT 1
            """
        )
    )

    # Rebind pet 1 to the clinic owner if it was bound to a stale/qa owner.
    connection.execute(
        text(
            """
            UPDATE pets SET owner_id = (
                SELECT o.id FROM owners o
                JOIN users u ON u.id = o.user_id
                WHERE u.email = 'clinic@test.com' LIMIT 1
            )
            WHERE id = 1
            AND EXISTS (
                SELECT 1 FROM owners o JOIN users u ON u.id = o.user_id
                WHERE u.email = 'clinic@test.com'
            )
            AND owner_id <> (
                SELECT o.id FROM owners o
                JOIN users u ON u.id = o.user_id
                WHERE u.email = 'clinic@test.com' LIMIT 1
            )
            """
        )
    )

    # Ensure pet 1 weight is a numeric string (domain model does float(weight)).
    connection.execute(
        text(
            "UPDATE pets SET weight = '4' WHERE id = 1 AND weight IS NOT NULL "
            "AND weight !~ '^[0-9.]+$'"
        )
    )

    pet_owner_id = connection.execute(
        text("SELECT owner_id FROM pets WHERE id = 1")
    ).scalar_one_or_none()
    if pet_owner_id is None:
        return

    # Seed completed appointment 1 for pet 1 (vet 17, clinic 1, branch 1).
    connection.execute(
        text(
            """
            INSERT INTO appointments (
                id, owner_id, pet_id, veterinarian_id, clinic_id, branch_id,
                appointment_type, status, scheduled_start, scheduled_end,
                duration_minutes, reason, notes, created_by, updated_at
            )
            VALUES (
                1, :owner_id, 1, 17, 1, 1,
                'consultation', 'completed',
                NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '30 minutes',
                30, 'chequeo general', 'cita de prueba', 50, NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                owner_id = EXCLUDED.owner_id,
                pet_id = EXCLUDED.pet_id
            """
        ),
        {"owner_id": pet_owner_id},
    )

    connection.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('appointments', 'id'), "
            "(SELECT COALESCE(MAX(id), 1) FROM appointments), true)"
        )
    )


def _ensure_owner_consultation_fixtures(connection: Connection) -> None:
    """Seed dedicated owner accounts + pet/appointment/consultation fixtures for
    the BE-009 owner UIA tests (UIA-009 TC-03/04/05).

    Existing seed data binds pet 1 to the *clinic* owner, so the generic
    ``qa@test.com`` login (an owner with no pets) hits the BOLA guard and can
    never exercise the owner happy-path. These fixtures give the specs a real
    owner who owns a pet with a completed appointment and a registered
    consultation, plus a second owner whose pet is used to assert cross-owner
    isolation. Fixed high IDs + ON CONFLICT guards make this idempotent.
    """
    if not inspect(connection).has_table("consultations"):
        return

    password_hash = get_password_hash("Pruebas")

    connection.execute(
        text(
            """
            INSERT INTO users (
                email, username, hashed_password, first_name, last_name,
                is_active, is_admin, created_at, updated_at
            )
            VALUES
                ('owner1@test.com', 'owner1@test.com', :password_hash,
                 'Due', 'Uno', true, false, NOW(), NOW()),
                ('owner2@test.com', 'owner2@test.com', :password_hash,
                 'Due', 'Dos', true, false, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET
                username = EXCLUDED.username,
                hashed_password = EXCLUDED.hashed_password,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                is_active = true,
                updated_at = EXCLUDED.updated_at
            """
        ),
        {"password_hash": password_hash},
    )

    for email in ("owner1@test.com", "owner2@test.com"):
        connection.execute(
            text(
                """
                INSERT INTO owners (
                    user_id, first_name, last_name, email, phone, address,
                    city, state, country, postal_code, is_active, clinic_id,
                    created_at, updated_at
                )
                SELECT u.id, 'Due', 'Owner', u.email, '555-0110', 'Calle Due 1',
                       'Ciudad de pruebas', 'Estado de pruebas', 'MX', '00000',
                       true, 1, NOW(), NOW()
                FROM users u
                WHERE u.email = :email
                  AND NOT EXISTS (
                      SELECT 1 FROM owners o WHERE o.user_id = u.id
                  )
                """
            ),
            {"email": email},
        )

    connection.execute(
        text("UPDATE owners SET clinic_id = 1 WHERE clinic_id IS NULL")
    )

    fixtures = (
        # (pet_id, owner_email, appt_id, consultation_id, day_offset)
        (1000, "owner1@test.com", 1000, 1000, 1),
        (1001, "owner2@test.com", 1001, 1001, 2),
    )

    for pet_id, owner_email, appt_id, consultation_id, day_offset in fixtures:
        connection.execute(
            text(
                """
                INSERT INTO pets (
                    id, owner_id, name, species, breed, color, gender, weight,
                    date_of_birth, has_medical_history, is_active,
                    created_at, updated_at
                )
                SELECT :id, o.id, 'Mascota PRUEBA', 'gato', 'domestico', 'gris',
                       'macho', '4', NOW() - INTERVAL '2 years', false, true,
                       NOW(), NOW()
                FROM owners o
                JOIN users u ON u.id = o.user_id
                WHERE u.email = :owner_email
                  AND NOT EXISTS (SELECT 1 FROM pets p WHERE p.id = :id)
                """
            ),
            {"id": pet_id, "owner_email": owner_email},
        )

        connection.execute(
            text(
                """
                INSERT INTO appointments (
                    id, owner_id, pet_id, veterinarian_id, clinic_id, branch_id,
                    appointment_type, status, scheduled_start, scheduled_end,
                    duration_minutes, reason, notes, created_by, updated_at
                )
                SELECT :appt_id, o.id, :pet_id, 17, 1, 1,
                       'consultation', 'completed',
                       NOW() - (INTERVAL '1 day' * :day_offset),
                       NOW() - (INTERVAL '1 day' * :day_offset) + INTERVAL '30 minutes',
                       30, 'chequeo general', 'cita de prueba', 50, NOW()
                FROM owners o
                JOIN users u ON u.id = o.user_id
                WHERE u.email = :owner_email
                  AND NOT EXISTS (SELECT 1 FROM appointments a WHERE a.id = :appt_id)
                """
            ),
            {
                "appt_id": appt_id,
                "pet_id": pet_id,
                "owner_email": owner_email,
                "day_offset": day_offset,
            },
        )

        connection.execute(
            text(
                """
                INSERT INTO consultations (
                    id, appointment_id, pet_id, clinic_id, branch_id,
                    veterinarian_id, history, diagnosis, recommendations,
                    created_by, updated_at
                )
                VALUES (
                    :cid, :appt_id, :pet_id, 1, 1, 17,
                    'Mascota de prueba sin novedades significativas.',
                    'Chequeo general satisfactorio.',
                    'Continuar con control de peso y refuerzo de vacunas.',
                    50, NOW()
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "cid": consultation_id,
                "appt_id": appt_id,
                "pet_id": pet_id,
            },
        )

    for table in ("pets", "appointments", "consultations"):
        connection.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"(SELECT COALESCE(MAX(id), 1) FROM {table}), true)"
            )
        )


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
    password_hash = get_password_hash("Pruebas")

    connection.execute(
        text(
            """
            INSERT INTO users (
                email, username, hashed_password, first_name, last_name, is_active, is_admin,
                created_at, updated_at
            )
            VALUES
                ('qa@test.com', 'qa@test.com', :password_hash, 'QA', 'Admin', true, true, NOW(), NOW()),
                ('admin@test.com', 'admin@test.com', :password_hash, 'Admin', 'InVet', true, true, NOW(), NOW()),
                ('clinic@test.com', 'clinic@test.com', :password_hash, 'Clinic', 'Viewer', true, false, NOW(), NOW()),
                ('vet@test.com', 'vet@test.com', :password_hash, 'Vet', 'Viewer', true, false, NOW(), NOW())
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
            WHERE u.email = 'qa@test.com'
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
            WHERE u.email = 'admin@test.com'
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
            WHERE u.email = 'clinic@test.com'
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
            WHERE u.email = 'vet@test.com'
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
        if inspector.has_table("pets") and inspector.has_table("veterinarians"):
            _ensure_consultation_seed(connection)
            _ensure_owner_consultation_fixtures(connection)


def ensure_test_branch_seed(engine: Engine) -> None:
    """Seed branch-dependent tables in isolated test schemas."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if inspector.has_table("clinics") and inspector.has_table("branches"):
            _seed_default_clinic_branch(connection)
