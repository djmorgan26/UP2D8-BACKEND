import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

import sys
sys.path.append("/Users/davidmorgan/Documents/Repositories/UP2D8-BACKEND")

def test_create_analytics(test_client):
    response = test_client.post("/api/analytics", json={"user_id": "some_user_id", "event_type": "some_event", "details": {}})
    assert response.status_code == 202
    assert response.json()["message"] == "Event logged."
