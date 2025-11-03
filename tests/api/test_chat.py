import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

from unittest.mock import patch, MagicMock

# Mock the Gemini API
genai_mock = MagicMock()
with patch.dict('sys.modules', {'google.generativeai': genai_mock}):
    from main import app

@patch("main.genai.GenerativeModel")
def test_chat(mock_generative_model, test_client):
    mock_model = mock_generative_model.return_value
    mock_model.generate_content.return_value.text = "This is a mocked response."

    response = test_client.post("/api/chat", json={"prompt": "Hello"})
    assert response.status_code == 200
    assert response.json()["text"] == "This is a mocked response."

def test_get_sessions(test_client):
    # First, create a user
    response = test_client.post("/api/users", json={"email": "test_sessions@example.com", "topics": ["testing"]})
    assert response.status_code == 200
    user_id = response.json()["user_id"]

    # Create a session
    response = test_client.post(f"/api/sessions", json={"user_id": user_id, "title": "Test Session"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Get sessions for the user
    response = test_client.get(f"/api/users/{user_id}/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["session_id"] == session_id

@patch("main.genai.GenerativeModel")
def test_get_messages(mock_generative_model, test_client):
    mock_model = mock_generative_model.return_value
    mock_model.generate_content.return_value.text = "This is a mocked response."

    # First, create a user and a session
    response = test_client.post("/api/users", json={"email": "test_messages@example.com", "topics": ["testing"]})
    user_id = response.json()["user_id"]
    response = test_client.post(f"/api/sessions", json={"user_id": user_id, "title": "Test Session"})
    session_id = response.json()["session_id"]

    # Post a message
    response = test_client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    assert response.status_code == 200

    # Get messages for the session
    response = test_client.get(f"/api/sessions/{session_id}/messages")
    assert response.status_code == 200
    assert len(response.json()) == 2 # User and model message
