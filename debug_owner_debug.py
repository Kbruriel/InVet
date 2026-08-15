import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
sys.path.insert(0, 'backend')

engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
from app.infrastructure.database.models.base import Base
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

from app.api.main import app
from app.api.v1.routers.owners import get_current_db as get_owners_db
from app.core.security import get_current_access_user
from app.infrastructure.database import get_db

def override_get_db():
    try:
        yield session
    finally:
        pass

def fake_auth():
    return {'id': 11, 'role': 'owner'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_owners_db] = override_get_db
app.dependency_overrides[get_current_access_user] = fake_auth

client = TestClient(app)
resp = client.post('/api/v1/owners', json={'nombre':'Ana Perez','email':'ana@example.com','telefono':'809-555-0100','direccion':'Calle 1'})
print('STATUS:', resp.status_code)
print('BODY:', resp.json())
