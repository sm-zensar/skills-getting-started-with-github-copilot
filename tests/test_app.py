"""
Unit tests for the Mergington High School Activities API.

Tests cover all endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/unregister
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to default state before each test."""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball league and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and friendly matches",
            "schedule": "Tuesdays and Saturdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and artistic expression",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater rehearsals and stage performances",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through experiments and projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_chess_club_structure(self, client, reset_activities):
        """Test that activity data includes required fields."""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activity participants list is included."""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_email_rejected(self, client, reset_activities):
        """Test that duplicate signup for same activity is rejected."""
        # Try to sign up with email already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_invalid_activity_returns_404(self, client, reset_activities):
        """Test that signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_same_email_different_activities(self, client, reset_activities):
        """Test that same student can sign up for multiple different activities."""
        email = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        email = "michael@mergington.edu"
        
        # Verify email is in Chess Club
        assert email in activities["Chess Club"]["participants"]
        
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_not_signed_up_returns_400(self, client, reset_activities):
        """Test that unregistering a non-participant returns 400."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_invalid_activity_returns_404(self, client, reset_activities):
        """Test that unregister for non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_then_can_signup_again(self, client, reset_activities):
        """Test that student can sign up again after unregistering."""
        email = "testuser@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response3 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        assert email in activities["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_signup_and_verify_in_activities_list(self, client, reset_activities):
        """Test that newly signed up participant appears in activities list."""
        email = "integration@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Get activities and verify
        response = client.get("/activities")
        data = response.json()
        
        assert email in data["Programming Class"]["participants"]
    
    def test_unregister_and_verify_in_activities_list(self, client, reset_activities):
        """Test that unregistered participant no longer appears in activities list."""
        email = "michael@mergington.edu"
        
        # Verify initial state
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify in updated activities list
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
