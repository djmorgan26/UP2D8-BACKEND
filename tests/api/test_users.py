import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

def test_create_user(test_client):
    response = test_client.post("/api/users", json={"email": "test@example.com", "topics": ["testing"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Subscription confirmed."
    assert "user_id" in response.json()

def test_create_user_invalid_email(test_client):
    response = test_client.post("/api/users", json={"email": "not-an-email", "topics": ["testing"]})
    assert response.status_code == 422

def test_update_user(test_client):
    # First, create a user
    response = test_client.post("/api/users", json={"email": "test_update@example.com", "topics": ["testing"]})
    assert response.status_code == 200
    user_id = response.json()["user_id"]

    # Now, update the user
    response = test_client.put(f"/api/users/{user_id}", json={"topics": ["new_topic"], "preferences": {"newsletter_format": "detailed"}})
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
