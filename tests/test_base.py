"""Tests for the base.py module"""

import pytest

import stack_overflow_importer.base
from stack_overflow_importer.auth import retrieve_key, retrieve_token
from stack_overflow_importer.base import query_method


@pytest.mark.live
def test_query_method_live_call():
    """It returns the JSOn response from a live call to SO 'Site' API endpoint."""
    key = retrieve_key()
    token = retrieve_token()
    response = query_method("info", key, token, {"site": "stackoverflow"})
    assert "items" in response.keys()
    assert "api_revision" in response.get("items")[0].keys()


class MockResponse:
    """A mock response to be returned by requests.get."""

    @staticmethod
    def json():
        """Mock JSON response for the info method"""
        return {
            "items": [
                {
                    "new_active_users": 4,
                    "total_users": 18016180,
                    "badges_per_minute": 6.17,
                    "total_badges": 45063710,
                    "total_votes": 188678141,
                    "total_comments": 108391207,
                    "answers_per_minute": 4.6,
                    "questions_per_minute": 3.11,
                    "total_answers": 33582623,
                    "total_accepted": 11609395,
                    "total_unanswered": 6906986,
                    "total_questions": 22683027,
                    "api_revision": "2022.5.24.471",
                }
            ],
            "has_more": False,
            "quota_max": 10000,
            "quota_remaining": 9985,
        }


def test_query_method(monkeypatch):
    """It returns the API JSON response."""
    # pylint: disable=unused-argument
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(stack_overflow_importer.base.requests, "get", mock_get)
    response = query_method("info", "key", "token", {"site": "stackoverflow"})
    assert "items" in response.keys()
    assert "api_revision" in response.get("items")[0].keys()
