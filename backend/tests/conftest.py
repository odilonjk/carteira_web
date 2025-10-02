"""Pytest fixtures for the backend tests."""
from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app():
    """Yield an app instance configured for testing."""
    application = create_app("testing")
    yield application


@pytest.fixture()
def client(app):
    """Return a test client bound to the app fixture."""
    return app.test_client()
