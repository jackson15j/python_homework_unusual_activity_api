"""Stock pytest fixtures to support unit testing of the API Endpoints."""
import pytest

from src.unusual_activity.main import (
    create_app,
    EventStore,
)


@pytest.fixture()
def app():
    app = create_app(EventStore())
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_client()
