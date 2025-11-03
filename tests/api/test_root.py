import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

from unittest.mock import patch, MagicMock

from main import app

@patch("main.genai.configure")
def test_read_root(mock_configure, test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}