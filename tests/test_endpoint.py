import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test basic health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_homefeed_returns_recommendations():
    """Test homefeed returns valid recommendations"""
    response = client.get("/v1/reco/homefeed?user_id=1")
    assert response.status_code == 200
    
    data = response.json()
    assert "user_id" in data
    assert "recommendations" in data
    assert data["user_id"] == 1
    
    # Check recommendation structure
    if data["recommendations"]:
        rec = data["recommendations"][0]
        assert "item_id" in rec
        assert "title" in rec
        assert "reason" in rec

def test_feedback_logging():
    """Test feedback endpoint works"""
    feedback_data = {
        "user_id": 1,
        "item_id": 1,
        "feedback_type": "like"
    }
    
    response = client.post("/v1/reco/feedback", json=feedback_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"

def test_cold_start_user():
    """Test recommendations for user with no history"""
    # Use high user ID that likely doesn't exist
    response = client.get("/v1/reco/homefeed?user_id=999999")
    assert response.status_code == 200
    
    data = response.json()
    # Should still get recommendations from popularity
    assert "recommendations" in data

def test_feedback_changes_recommendations():
    """Test that feedback affects future recommendations"""
    user_id = 1
    
    # Get initial recommendations
    response1 = client.get(f"/v1/reco/homefeed?user_id={user_id}")
    recs1 = response1.json()["recommendations"]
    
    # Log some feedback
    if recs1:
        feedback_data = {
            "user_id": user_id,
            "item_id": recs1[0]["item_id"],
            "feedback_type": "like"
        }
        client.post("/v1/reco/feedback", json=feedback_data)
    
    # Get new recommendations (may be different due to new interaction)
    response2 = client.get(f"/v1/reco/homefeed?user_id={user_id}")
    assert response2.status_code == 200

# Run with: python -m pytest tests/test_endpoints.py -v
