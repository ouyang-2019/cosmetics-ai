import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")


client = TestClient(app)


def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"


def test_register_duplicate_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "anotherpass"},
    )
    assert response.status_code == 400


def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpass"},
    )
    assert response.status_code == 401
