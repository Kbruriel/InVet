"""Correct seeds in all 7 notification test files.
Fixes:
- UserModel fields: remove clinic_id/role/full_name, use email+username+hashed_password+first_name+last_name
- OwnerModel fields: replace pet_name/pet_type/birth_date with first_name+last_name+email+clinic_id (if applicable)
"""

import re
import pathlib

TESTS_DIR = pathlib.Path("C:/InVet/backend/app/tests/api")
FILES_TO_FIX = [
    "test_notifications_auth.py",
    "test_notifications_mark_read.py",
    "test_notifications_dedup.py",
    "test_notifications_idor_bola.py",
    "test_notifications_read_all.py",
    "test_notifications_unread_count.py",
]

# Correct UserModel seed — matches the canonical test_notification_api.py
USER_CORRECTION = '''        # Usuario 1 de clinica 1
        u1 = UserModel(
            email="user1@example.com",
            username="user1",
            hashed_password="hashed1",
            first_name="Usuario",
            last_name="Uno",
        )'''

# Owner correction — use real fields from SQLAlchemy model:
# Owner(id, user_id, first_name, last_name, email, phone, address, city, state, country, postal_code, is_active, created_at, updated_at, clinic_id)
OWNER_CORRECTION = '''        # Owner 1
        o1 = OwnerModel(
            user_id=u1.id,
            first_name="Juan",
            last_name="Perez",
            email="juan@example.com",
            clinic_id=c1.id,
        )
        # Owner 2
        o2 = OwnerModel(
            user_id=u2.id,
            first_name="Maria",
            last_name="Gomez",
            email="maria@example.com",
            clinic_id=c2.id,
        )'''

OWNER_CORRECTION_SINGLE = '''        # Owner 1
        o1 = OwnerModel(
            user_id=u1.id,
            first_name="Juan",
            last_name="Perez",
            email="juan@example.com",
            clinic_id=c1.id,
        )'''


def patch_file(filepath: pathlib.Path):
    content = filepath.read_text("utf-8")

    # Step 1: Fix u1 UserModel — pattern that starts with "u1 = UserModel(" and has bad fields
    # Match the multi-line bad u1 block
    old_u1_pattern = r'(        # Usuario 1 de clinica 1\n)        u1 = UserModel\(\n\s+clinic_id=c1\.id,\n\s+role="owner",\n\s+email="user1@example\.com",\n\s+full_name="Usuario Uno",\n\s+phone="P1",\n\s+\)'
    content = re.sub(old_u1_pattern, r'\g<1>' + USER_CORRECTION.lstrip('\n'), content)

    # Step 2: Fix OwnerModel pet_name pattern (both two and single owner variants)
    old_owner2_pattern = (r'# Owner 1\n'
                          r'        o1 = OwnerModel\(\n'
                          r'            user_id=u1\.id,\n'
                          r'            pet_name="Mascota Uno",\n'
                          r'            pet_type="perro",\n'
                          r'            birth_date="20\d{2}-\d{2}-\d{2}",\n'
                          r'        \)\n'
                          r'\s*db\.add(?:_all)*\(o1\)\n'
                          r'\n'
                          r'        # Owner 2\n'
                          r'        o2 = OwnerModel\(\n'
                          r'            user_id=u2\.id,\n'
                          r'            pet_name="Mascota Dos",\s*\n'
                          r'            pet_type="gato",\n'
                          r'            birth_date="20\d{2}-\d{2}-\d{2}",\n'
                          r'        \)')
    content = re.sub(old_owner2_pattern, OWNER_CORRECTION.lstrip('\n'), content)

    # Step 3: Fix single owner (dedup)
    old_owner1_pattern = (r'# Owner 1\n'
                          r'        o1 = OwnerModel\(\n'
                          r'            user_id=u1\.id,\n'
                          r'            pet_name="Mascota Uno",\n'
                          r'            pet_type="perro",\n'
                          r'            birth_date="20\d{2}-\d{2}-\d{2}",\n'
                          r'        \)')
    content = re.sub(old_owner1_pattern, OWNER_CORRECTION_SINGLE.lstrip('\n'), content)

    filepath.write_text(content, "utf-8")
    print(f"  Patched: {filepath.name}")


if __name__ == "__main__":
    for fname in FILES_TO_FIX:
        fpath = TESTS_DIR / fname
        if fpath.exists():
            patch_file(fpath)
        else:
            print(f"SKIP (not found): {fpath}")
    print("Done patching seeds.")
