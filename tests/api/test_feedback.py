import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

def test_create_feedback(test_client):
    response = test_client.post("/api/feedback", json={"message_id": "some_message_id", "user_id": "some_user_id", "rating": "thumbs_up"})
    assert response.status_code == 201
    assert response.json()["message"] == "Feedback received."
