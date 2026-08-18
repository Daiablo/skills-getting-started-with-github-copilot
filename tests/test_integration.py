"""
Integration tests for cross-endpoint workflows.

Tests verify that endpoints work correctly together:
- Sign up → GET reflects new participant → remove → verify removed
- Multiple signups across different activities
- Error recovery (attempt duplicate, then try different activity)
"""

import pytest


class TestIntegrationWorkflows:
    """Integration tests for API workflows involving multiple endpoints."""
    
    def test_signup_get_remove_workflow(self, test_client, activities_fixture, sample_emails):
        """
        Test complete workflow: signup → GET → remove → GET.
        
        Arrange: New student email and activity name
        Act: 
            1. POST signup
            2. GET activities to verify new participant
            3. DELETE participant
            4. GET activities to verify removal
        Assert: All operations succeed and state is correct at each step
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = sample_emails["new"]["student_1"]
        initial_count = len(activities_fixture[activity_name]["participants"])
        
        # Act 1: Signup
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Act 2: GET to verify signup
        get_response_1 = test_client.get("/activities")
        data_1 = get_response_1.json()
        
        # Act 3: Remove participant
        remove_response = test_client.delete(
            f"/activities/{activity_name}/participants/{new_email}"
        )
        
        # Act 4: GET to verify removal
        get_response_2 = test_client.get("/activities")
        data_2 = get_response_2.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert get_response_1.status_code == 200
        assert new_email in data_1[activity_name]["participants"]
        assert len(data_1[activity_name]["participants"]) == initial_count + 1
        
        assert remove_response.status_code == 200
        assert get_response_2.status_code == 200
        assert new_email not in data_2[activity_name]["participants"]
        assert len(data_2[activity_name]["participants"]) == initial_count
    
    def test_multiple_signups_across_activities(self, test_client, activities_fixture, sample_emails):
        """
        Test multiple signups across different activities.
        
        Arrange: Multiple student emails and activities
        Act: POST signup requests for same student, different activities
        Assert: Student appears in all activities
        """
        # Arrange
        student_email = sample_emails["new"]["student_1"]
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        responses = []
        for activity_name in activities_to_join:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            responses.append(response)
        
        # Assert
        for response in responses:
            assert response.status_code == 200
        
        get_response = test_client.get("/activities")
        data = get_response.json()
        
        for activity_name in activities_to_join:
            assert student_email in data[activity_name]["participants"]
    
    def test_error_recovery_duplicate_then_different_activity(self, test_client, activities_fixture, sample_emails):
        """
        Test error recovery: attempt duplicate signup, then successfully signup for different activity.
        
        Arrange: Existing participant and multiple activities
        Act:
            1. Try to signup for activity they're already in (should fail)
            2. Signup for different activity (should succeed)
        Assert: First fails with 400, second succeeds with 200
        """
        # Arrange
        activity_1 = "Chess Club"
        activity_2 = "Programming Class"
        existing_email = sample_emails["existing"]["chess_1"]
        
        # Act 1: Try duplicate signup (should fail)
        duplicate_response = test_client.post(
            f"/activities/{activity_1}/signup",
            params={"email": existing_email}
        )
        
        # Act 2: Signup for different activity (should succeed)
        different_response = test_client.post(
            f"/activities/{activity_2}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert duplicate_response.status_code == 400
        assert different_response.status_code == 200
        assert existing_email in activities_fixture[activity_1]["participants"]  # Still in original
        assert existing_email in activities_fixture[activity_2]["participants"]  # Now in new one
    
    def test_concurrent_operations_multiple_students(self, test_client, activities_fixture, sample_emails):
        """
        Test multiple students signing up and different operations occurring.
        
        Arrange: Multiple student emails and activities
        Act:
            1. Student 1 signs up for Activity A
            2. Student 2 signs up for Activity A
            3. Student 1 removes from Activity A
            4. Verify final state
        Assert: Final participant list is correct
        """
        # Arrange
        activity_name = "Gym Class"
        student_1 = sample_emails["new"]["student_1"]
        student_2 = sample_emails["new"]["student_2"]
        initial_count = len(activities_fixture[activity_name]["participants"])
        
        # Act 1: Student 1 signs up
        signup_1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_1}
        )
        
        # Act 2: Student 2 signs up
        signup_2 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_2}
        )
        
        # Act 3: Student 1 removes
        remove_1 = test_client.delete(
            f"/activities/{activity_name}/participants/{student_1}"
        )
        
        # Assert
        assert signup_1.status_code == 200
        assert signup_2.status_code == 200
        assert remove_1.status_code == 200
        
        final_participants = activities_fixture[activity_name]["participants"]
        assert student_1 not in final_participants
        assert student_2 in final_participants
        assert len(final_participants) == initial_count + 1
    
    def test_signup_remove_signup_same_student(self, test_client, activities_fixture, sample_emails):
        """
        Test that a student can re-signup after being removed.
        
        Arrange: New student and activity
        Act:
            1. Student signs up
            2. Student is removed
            3. Student signs up again
        Assert: All operations succeed and student is in activity
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = sample_emails["new"]["student_1"]
        
        # Act 1: First signup
        signup_1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act 2: Remove
        remove = test_client.delete(
            f"/activities/{activity_name}/participants/{student_email}"
        )
        
        # Act 3: Sign up again
        signup_2 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert signup_1.status_code == 200
        assert remove.status_code == 200
        assert signup_2.status_code == 200
        assert student_email in activities_fixture[activity_name]["participants"]
