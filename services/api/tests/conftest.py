import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from main import app

# Base SQLite en mémoire — pas besoin de PostgreSQL
SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite ne supporte pas les UUIDs natifs — on active le mode string
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def created_user(client):
    payload = {
        "email": "test@healthai.com",
        "username": "testuser",
        "password": "secret123",
        "age": 30,
        "gender": "male",
    }
    r = client.post("/api/v1/users/", json=payload)
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def created_exercise(client):
    payload = {"name": "Squat", "difficulty": "beginner"}
    r = client.post("/api/v1/exercises/", json=payload)
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def created_nutrition_item(client):
    payload = {"name": "Riz blanc", "calories": 130, "proteins_g": 2.7}
    r = client.post("/api/v1/nutrition-items/", json=payload)
    assert r.status_code == 201
    return r.json()
