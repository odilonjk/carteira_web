"""Pytest fixtures for the backend tests."""
from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture(autouse=True)
def tinydb_environment(monkeypatch, tmp_path_factory):
    """Force the app to use a temporary TinyDB file during tests."""

    db_path = tmp_path_factory.mktemp("tinydb") / "test_db.json"
    monkeypatch.setenv("DATA_BACKEND", "tinydb")
    monkeypatch.setenv("TINYDB_FILE", str(db_path))
    yield


@pytest.fixture()
def app():
    """Yield an app instance configured for testing."""
    application = create_app("testing")
    yield application


@pytest.fixture()
def client(app):
    """Return a test client bound to the app fixture."""
    return app.test_client()
