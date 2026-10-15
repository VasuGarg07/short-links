import os

import pytest
from fastapi.testclient import TestClient

from main import app
from utils import get_db_conn


@pytest.fixture(autouse=True)
def use_test_database(monkeypatch: pytest.MonkeyPatch) -> None:
    test_url = os.environ["TEST_DATABASE_URL"]
    assert test_url.endswith("_test")
    monkeypatch.setenv("DATABASE_URL", test_url)
    with get_db_conn() as conn:
        conn.execute("TRUNCATE links RESTART IDENTITY")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
