$ErrorActionPreference = "Continue"
$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/invet_alembic_test"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="postgres"
$env:POSTGRES_DB="invet_alembic_test"
$env:POSTGRES_SERVER="localhost"

Push-Location backend
Write-Output "=== STAMP a008 ==="
alembic -c alembic/alembic.ini stamp a008 2>&1 | Select-Object -Last 3
Write-Output "=== UPGRADE a009 ==="
alembic -c alembic/alembic.ini upgrade a009 2>&1 | Select-Object -Last 3
Write-Output "=== TABLE (expect consultations) ==="
docker exec invet-db psql -U postgres -d invet_alembic_test -t -c "SELECT to_regclass('public.consultations');" 2>&1
Write-Output "=== DOWNGRADE a008 ==="
alembic -c alembic/alembic.ini downgrade a008 2>&1 | Select-Object -Last 3
Write-Output "=== TABLE GONE (expect empty) ==="
docker exec invet-db psql -U postgres -d invet_alembic_test -t -c "SELECT to_regclass('public.consultations');" 2>&1
Write-Output "=== UPGRADE a009 again ==="
alembic -c alembic/alembic.ini upgrade a009 2>&1 | Select-Object -Last 3
Write-Output "=== FINAL TABLE (expect consultations) ==="
docker exec invet-db psql -U postgres -d invet_alembic_test -t -c "SELECT to_regclass('public.consultations');" 2>&1
Pop-Location
