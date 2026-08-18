"""
Unit tests for GET /activities endpoint.

Tests verify that:
- The endpoint returns all activities
- Response structure is correct
- Participant counts are accurate
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, test_client, activities_fixture):
        """
        Test that GET /activities returns all activities in the database.
        
        Arrange: Set up test client and activities fixture
        Act: Make GET request to /activities
        Assert: Response includes all test activities
        """
        # Act
        response = test_client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_response_structure(self, test_client, activities_fixture):
        """
        Test that each activity in the response has the correct structure.
        
        Arrange: Set up test client and activities fixture
        Act: Make GET request to /activities
        Assert: Each activity has required fields with correct types
        """
        # Act
        response = test_client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert isinstance(activity_data["description"], str)
            assert "schedule" in activity_data
            assert isinstance(activity_data["schedule"], str)
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participant_count(self, test_client, activities_fixture):
        """
        Test that participant lists contain the correct number of students.
        
        Arrange: Set up test client and activities fixture
        Act: Make GET request to /activities
        Assert: Each activity shows correct participant count
        """
        # Act
        response = test_client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2
        assert len(data["Gym Class"]["participants"]) == 1
    
    def test_get_activities_participants_are_emails(self, test_client, activities_fixture):
        """
        Test that participants are stored as email addresses.
        
        Arrange: Set up test client and activities fixture
        Act: Make GET request to /activities
        Assert: Each participant is a valid email string
        """
        # Act
        response = test_client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_data in data.values():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
                assert ".edu" in participant
