"""
Unit tests for POST /activities/{activity_name}/signup endpoint.

Tests verify that:
- New students can successfully sign up
- Duplicate signups are prevented (400 error)
- Invalid activities return 404 error
- Response messages are correct
- Participant count increases appropriately
"""

import pytest


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_happy_path(self, test_client, activities_fixture, sample_emails):
        """
        Test successful signup for a new participant.
        
        Arrange: Prepare new student email and activity name
        Act: POST request to signup endpoint
        Assert: Response is 200, participant is added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = sample_emails["new"]["student_1"]
        initial_count = len(activities_fixture[activity_name]["participants"])
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert new_email in activities_fixture[activity_name]["participants"]
        assert len(activities_fixture[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_response_message_format(self, test_client, activities_fixture, sample_emails):
        """
        Test that signup response message has correct format.
        
        Arrange: Prepare new student email and activity name
        Act: POST request to signup endpoint
        Assert: Response message contains email and activity name
        """
        # Arrange
        activity_name = "Programming Class"
        new_email = sample_emails["new"]["student_2"]
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_duplicate_email_returns_400(self, test_client, activities_fixture, sample_emails):
        """
        Test that signing up with same email twice returns 400 error.
        
        Arrange: Use an email already registered for activity
        Act: POST request to signup endpoint
        Assert: Response is 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = sample_emails["existing"]["chess_1"]
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_invalid_activity_returns_404(self, test_client, activities_fixture, sample_emails):
        """
        Test that signup to non-existent activity returns 404 error.
        
        Arrange: Use an activity name that doesn't exist
        Act: POST request to signup endpoint
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        new_email = sample_emails["new"]["student_1"]
        
        # Act
        response = test_client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_different_students_same_activity(self, test_client, activities_fixture, sample_emails):
        """
        Test that multiple different students can sign up for the same activity.
        
        Arrange: Prepare two different student emails
        Act: POST signup requests for both students
        Assert: Both students are added to activity
        """
        # Arrange
        activity_name = "Gym Class"
        student_1 = sample_emails["new"]["student_1"]
        student_2 = sample_emails["new"]["student_2"]
        initial_count = len(activities_fixture[activity_name]["participants"])
        
        # Act - first student
        response_1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_1}
        )
        
        # Act - second student
        response_2 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_2}
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        assert student_1 in activities_fixture[activity_name]["participants"]
        assert student_2 in activities_fixture[activity_name]["participants"]
        assert len(activities_fixture[activity_name]["participants"]) == initial_count + 2
    
    def test_signup_same_student_different_activities(self, test_client, activities_fixture, sample_emails):
        """
        Test that a student can sign up for multiple different activities.
        
        Arrange: Prepare one student email and multiple activities
        Act: POST signup requests for same student, different activities
        Assert: Student is added to all activities
        """
        # Arrange
        student_email = sample_emails["new"]["student_3"]
        activity_1 = "Chess Club"
        activity_2 = "Programming Class"
        
        # Act
        response_1 = test_client.post(
            f"/activities/{activity_1}/signup",
            params={"email": student_email}
        )
        
        response_2 = test_client.post(
            f"/activities/{activity_2}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        assert student_email in activities_fixture[activity_1]["participants"]
        assert student_email in activities_fixture[activity_2]["participants"]
