import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self):
        """Test that activities endpoint returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_duplicate_participant(self):
        """Test that signing up twice returns an error"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup - should fail
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_updates_participant_list(self):
        """Test that signup updates the participant list"""
        email = "verify@mergington.edu"
        activity = "Art Club"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Sign up new participant
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get updated participant count
        response2 = client.get("/activities")
        updated_count = len(response2.json()[activity]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in response2.json()[activity]["participants"]


class TestRemoveParticipantEndpoint:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_existing_participant(self):
        """Test removing an existing participant"""
        email = "remove@mergington.edu"
        activity = "Music Ensemble"
        
        # First sign up the participant
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then remove them
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
    
    def test_remove_nonexistent_participant(self):
        """Test removing a participant that doesn't exist"""
        response = client.delete(
            "/activities/Math Club/participants/notfound@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_from_nonexistent_activity(self):
        """Test removing from a non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_updates_participant_list(self):
        """Test that removal updates the participant list"""
        email = "willberemoved@mergington.edu"
        activity = "Science Club"
        
        # Sign up participant
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify signup
        response1 = client.get("/activities")
        assert email in response1.json()[activity]["participants"]
        
        # Remove participant
        client.delete(f"/activities/{activity}/participants/{email}")
        
        # Verify removal
        response2 = client.get("/activities")
        assert email not in response2.json()[activity]["participants"]


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
