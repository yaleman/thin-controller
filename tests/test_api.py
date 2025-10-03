"""test API things"""

import os
import sys

from fastapi.testclient import TestClient
import pytest
from loguru import logger
from thin_controller import app

logger.remove()
logger.add(sys.stderr, level="DEBUG")


@pytest.fixture(scope="function")
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_index(client: TestClient) -> None:
    """Test the main endpoint."""

    response = client.get("/")
    assert response.status_code == 200
    assert "Thin Controller" in response.content.decode()


def test_up(client: TestClient) -> None:
    """Test the /up endpoint."""

    response = client.get("/up")
    assert response.status_code == 200
    assert response.content.decode() == '"OK"'


def test_css(client: TestClient) -> None:
    """Test the main endpoint."""

    for url in ["/css/styles.css", "/css/simple.min.css"]:
        response = client.get(url)
        assert response.status_code == 200

    assert client.get("/css/doesnotexist.css").status_code == 404


def test_favicon(client: TestClient) -> None:
    """Test the favicon endpoint."""

    response = client.get("/img/favicon.png")
    assert response.status_code == 200

    assert client.get("/img/doesnotexist.png").status_code == 404


def test_api_config(client: TestClient) -> None:
    """Test the config endpoint."""

    response = client.get("/api/config")
    assert response.status_code == 200
    assert "regions" in response.json()


def test_read_instance(client: TestClient) -> None:
    """Test the instance read endpoint."""

    response = client.get("/api/instances")
    print(response.content)
    if os.getenv("AWS_ACCESS_KEY_ID") is None:
        assert response.status_code == 500
    else:
        assert response.status_code == 200
    assert isinstance(response.json(), dict)
