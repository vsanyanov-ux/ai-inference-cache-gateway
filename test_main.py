from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_endpoint():
    test_text = "Hello world, this is a test"
    response = client.post("/predict", json={"text": test_text})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == test_text
    assert "label" in data
    assert "score" in data
    # Note: cached might be True or False depending on if a previous run left breadcrumbs,
    # but since it's a new test.db it should be False.
    assert data["cached"] is False
