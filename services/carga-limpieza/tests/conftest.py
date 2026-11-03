import pytest


@pytest.fixture(autouse=True)
def sin_postgres(monkeypatch):

    monkeypatch.delenv("DATABASE_URL", raising=False)
