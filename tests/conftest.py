"""
Pytest configuration and shared fixtures for API tests.

Fixtures provide:
- Clean activities database (deep copy per test)
- FastAPI TestClient instance
- Sample test data (student emails, activity names)
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def activities_fixture():
    """
    Provides a clean copy of the activities database for each test.
    
    This ensures test isolation - modifications to activities in one test
    won't affect other tests.
    
    Returns:
        dict: Deep copy of the activities database with test data
    """
    # Create a clean copy with subset of activities for testing
    test_activities = {
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
            "participants": ["john@mergington.edu"]
        }
    }
    
    # Replace the global activities dict with our test data
    activities.clear()
    activities.update(test_activities)
    
    # Yield the activities dict so tests can access it
    yield activities
    
    # Cleanup: restore original data (though it will be reset next test anyway)
    activities.clear()


@pytest.fixture
def test_client(activities_fixture):
    """
    Provides a TestClient instance for making HTTP requests to the API.
    
    This fixture depends on activities_fixture to ensure clean state before each test.
    
    Returns:
        TestClient: FastAPI test client for making requests
    """
    return TestClient(app)


@pytest.fixture
def sample_emails():
    """
    Provides predefined test email addresses for use in tests.
    
    Returns:
        dict: Dictionary of sample email addresses organized by category
    """
    return {
        "existing": {
            "chess_1": "michael@mergington.edu",
            "chess_2": "daniel@mergington.edu",
            "programming_1": "emma@mergington.edu",
            "programming_2": "sophia@mergington.edu",
            "gym": "john@mergington.edu",
        },
        "new": {
            "student_1": "alex@mergington.edu",
            "student_2": "jessica@mergington.edu",
            "student_3": "ryan@mergington.edu",
        },
        "invalid": {
            "no_domain": "notanemail",
            "empty": "",
        }
    }
