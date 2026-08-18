"""
Unit tests for DELETE /activities/{activity_name}/participants/{email} endpoint.

Tests verify that:
- Existing participants can be successfully removed
- Removing non-existent participant returns 404
- Removing from non-existent activity returns 404
- Response messages are correct
- Participant count decreases appropriately
"""

import pytest


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_remove_participant_happy_path(self, test_client, activities_fixture, sample_emails):
        """
        Test successful removal of an existing participant.
        
        Arrange: Use existing participant in activity
        Act: DELETE request to remove participant
        Assert: Response is 200, participant is removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = sample_emails["existing"]["chess_1"]
        initial_count = len(activities_fixture[activity_name]["participants"])
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email_to_remove not in activities_fixture[activity_name]["participants"]
        assert len(activities_fixture[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_participant_response_message_format(self, test_client, activities_fixture, sample_emails):
        """
        Test that remove response message has correct format.
        
        Arrange: Use existing participant in activity
        Act: DELETE request to remove participant
        Assert: Response message contains email and activity name
        """
        # Arrange
        activity_name = "Programming Class"
        email_to_remove = sample_emails["existing"]["programming_1"]
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]
    
    def test_remove_nonexistent_participant_returns_404(self, test_client, activities_fixture, sample_emails):
        """
        Test that removing non-existent participant returns 404 error.
        
        Arrange: Use email not in activity participants list
        Act: DELETE request to remove participant
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = sample_emails["new"]["student_1"]
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_from_invalid_activity_returns_404(self, test_client, activities_fixture, sample_emails):
        """
        Test that removing from non-existent activity returns 404 error.
        
        Arrange: Use activity name that doesn't exist
        Act: DELETE request to remove participant
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = sample_emails["existing"]["chess_1"]
        
        # Act
        response = test_client.delete(
            f"/activities/{invalid_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_multiple_participants_sequentially(self, test_client, activities_fixture, sample_emails):
        """
        Test removing multiple participants from same activity one by one.
        
        Arrange: Use activity with multiple participants
        Act: DELETE requests for each participant
        Assert: All participants are removed correctly
        """
        # Arrange
        activity_name = "Chess Club"
        email_1 = sample_emails["existing"]["chess_1"]
        email_2 = sample_emails["existing"]["chess_2"]
        
        # Act - remove first participant
        response_1 = test_client.delete(
            f"/activities/{activity_name}/participants/{email_1}"
        )
        
        # Act - remove second participant
        response_2 = test_client.delete(
            f"/activities/{activity_name}/participants/{email_2}"
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        assert email_1 not in activities_fixture[activity_name]["participants"]
        assert email_2 not in activities_fixture[activity_name]["participants"]
        assert len(activities_fixture[activity_name]["participants"]) == 0
    
    def test_remove_same_participant_twice_returns_404(self, test_client, activities_fixture, sample_emails):
        """
        Test that removing the same participant twice returns 404 on second attempt.
        
        Arrange: Use existing participant in activity
        Act: DELETE request twice for same participant
        Assert: First succeeds (200), second fails (404)
        """
        # Arrange
        activity_name = "Gym Class"
        email = sample_emails["existing"]["gym"]
        
        # Act - first removal
        response_1 = test_client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Act - second removal (should fail)
        response_2 = test_client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 404
        assert email not in activities_fixture[activity_name]["participants"]
