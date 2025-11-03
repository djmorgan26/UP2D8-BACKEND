import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session", autouse=True)
def mock_key_vault_and_mongo():
    with (
        patch('main.initialize_secrets') as mock_initialize_secrets,
        patch('main.get_mongo_client_instance') as mock_get_mongo_client_instance,
    ):
        mock_initialize_secrets.return_value = None

        mock_mongo_instance = MagicMock()
        mock_get_mongo_client_instance.return_value = mock_mongo_instance

        yield

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client
