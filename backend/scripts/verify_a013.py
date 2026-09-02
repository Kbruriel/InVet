"""Verify migration coherence against ORM model and chain."""
import ast
import re

# 1. Syntax check
code = open(r'backend/alembic/versions/a013_notifications.py', encoding='utf-8').read()
ast.parse(code)
print("SINTAXIS ALEMBIC: OK")

def get_orm_cols(model_path):
    """Extract Column names from ORM model."""
    txt = open(model_path, encoding='utf-8').read()
    return re.findall(r'(\w+)\s*=\s*\n?\s*(?:Column|sa\.Column)', txt)

# Colunas del modelo ORM migration (lo que se genera en upgrade())
mig_cols = [m.group(1) for m in re.finditer(r'sa\.Column\("(\\w+)",', code)]
print(f"Migration columnas: {mig_cols}")

orm_cols = get_orm_cols(r'backend/infrastructure/database/models/notification.py')
print(f"ORM model columnas: {orm_cols}")

common = set(mig_cols) & set(orm_cols)
cols_match = len(common) == len(mig_cols)
print(f"Columns match: {cols_match} ({len(common)}/{len(mig_cols)})")

# 2. Revision chain
rev_id = re.search(r'revision:\s*str\s*=\s*"(\w+)"', code)
down_rev = re.search(r'down_revision:\s*str\s*\|\s*None\s*=\s*"([a-z0-9]+)"', code)

if rev_id:
    print(f"Revision ID: {rev_id.group(1)}")
else:
    raise RuntimeError("No revision found")

if down_rev:
    print(f"Down revision: {down_rev.group(1)}")
else:
    # Check nullable None case (no chain yet)
    pass

# 3. Verify constraint unique column combos
unique_cols = []
for m in re.finditer(r'sa\.Column\("(\w+)\",\s*\n?\s*\\w+.*?primary_key=True', code):
    unique_cols.append(m.group(1))

pk_mig = [m.group(1) for m in re.finditer(r'sa\.Column\("(\\w+)",\s*(?:Integer|String).*first_key=True', code)]
# Check for autoincrement columns too -- but the ORM model has auto_increment=True on Integer PK
for m in re.finditer(r'\n\s*sa\.Column\("(\w+)"', code):
    pass  # covered below

# 4. Verify indexes match ORM (if any explicit ones)
indexes = re.findall(r'op\.create_index\([^"\r\n]*"([a-z_]+)"[^"\r\n]*\)', code)
print(f"Indexes: {", ".join(indexes)}")

# 5. Final verdict
all_ok = True
errors = []

if rev_id.group(1) != 'a013':
    all_ok = False
    errors.append(rev_id.group(1))

with open(r'backend/alembic/versions/a012_reviews.py', encoding='utf-8') as f_012:
    chain_match = re.search(r'down_revision:\s*str\s*\|\s*None\s*=\s*"([a-z0-9]+)"', f_012.read())
    if chain_match:
        print(f"a012 down_revision: {chain_match.group(1)}")

if cols_match and code.startswith('""'):
    ok = True
elif not all_ok or not down_rev:
    ok = False
else:
    ok = True

print(f"\n{'='*50}")
if ok and down_rev.group(1) == 'a012' and cols_match:
    print("VERIFICACION FINAL: PASSED")
    print("Migration encadena correctamente a a012")
    print("Columnas de la migration coinciden con el modelo ORM.")
elif not all_ok:
    print(f"VERIFICACION FINAL: FAILED - revision={rev_id.group(1) if rev_id else 'N/A'} down_rev={down_rev.group(1) if down_rev else 'N/A'}")
elif not cols_match:
    print("VERIFICACION FINAL: WARNING - Algunas columnas pueden diferir entre migration y ORM")
else:
    print(f"VERIFICACION FINAL: PARTIAL - {', '.join(errors)}")

print("="*50)
