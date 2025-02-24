# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust if your main app is in a different path
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker

# Create a separate DB for testing if desired
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Creates all tables at test start and drops them at the end
    if you want a clean test DB. If you prefer ephemeral in-memory DB,
    adjust your DATABASE_URL in .env or override in code.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """
    Returns a SQLAlchemy session to be used in tests.
    """
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    """
    Override the 'get_db' dependency to use our test session.
    Returns a TestClient for making requests to the FastAPI app.
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    return TestClient(app)