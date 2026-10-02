"""
Tests for History endpoints and repository functionality:
  GET /api/v1/math/history
  GET /api/v1/math/history/stats
  DELETE /api/v1/math/history/{id}
  DELETE /api/v1/math/history
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def clean_history_before_and_after():
    """Ensure a clean history table for tests."""
    with TestClient(app) as client:
        client.delete("/api/v1/math/history")
        yield
        client.delete("/api/v1/math/history")


def test_history_flow_save_and_retrieve():
    with TestClient(app) as client:
        # Solve a problem which saves to history
        solve_resp = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ 2x + 4 = 10"},
        )
        assert solve_resp.status_code == 200
        assert solve_resp.json()["success"] is True

        # Fetch history
        history_resp = client.get("/api/v1/math/history")
        assert history_resp.status_code == 200
        data = history_resp.json()["data"]

        assert data["pagination"]["total_count"] == 1
        assert len(data["items"]) == 1
        entry = data["items"][0]
        assert entry["question"] == "ដោះស្រាយ 2x + 4 = 10"
        assert entry["problem_type"] == "linear_equation"
        assert entry["answer"] == "3"
        assert entry["is_verified"] is True
        assert len(entry["steps"]) > 0


def test_history_pagination_and_filtering():
    with TestClient(app) as client:
        # Create 3 entries: 2 linear, 1 quadratic
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve x + 1 = 3"})
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve 2*x + 2 = 6"})
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve x^2 - 4 = 0"})

        # Check total
        all_resp = client.get("/api/v1/math/history")
        assert all_resp.json()["data"]["pagination"]["total_count"] == 3

        # Test limit and offset pagination
        paged_resp = client.get("/api/v1/math/history?limit=2&offset=0")
        paged_data = paged_resp.json()["data"]
        assert len(paged_data["items"]) == 2
        assert paged_data["pagination"]["has_more"] is True

        paged_resp2 = client.get("/api/v1/math/history?limit=2&offset=2")
        paged_data2 = paged_resp2.json()["data"]
        assert len(paged_data2["items"]) == 1
        assert paged_data2["pagination"]["has_more"] is False

        # Filter by problem_type
        filtered_resp = client.get("/api/v1/math/history?problem_type=quadratic_equation")
        filtered_data = filtered_resp.json()["data"]
        assert filtered_data["pagination"]["total_count"] == 1
        assert filtered_data["items"][0]["problem_type"] == "quadratic_equation"

        # Search query filter
        search_resp = client.get("/api/v1/math/history?search=x%5E2")
        search_data = search_resp.json()["data"]
        assert search_data["pagination"]["total_count"] == 1
        assert "x^2" in search_data["items"][0]["question"]


def test_history_stats():
    with TestClient(app) as client:
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve 3x = 9"})
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve x^2 - 9 = 0"})

        stats_resp = client.get("/api/v1/math/history/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()["data"]

        assert stats["total_count"] == 2
        assert stats["by_problem_type"].get("linear_equation") == 1
        assert stats["by_problem_type"].get("quadratic_equation") == 1


def test_delete_single_entry_and_not_found():
    with TestClient(app) as client:
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve x + 5 = 10"})
        items = client.get("/api/v1/math/history").json()["data"]["items"]
        entry_id = items[0]["id"]

        # Delete existing
        del_resp = client.delete(f"/api/v1/math/history/{entry_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["data"]["deleted_id"] == entry_id

        # Verify deletion
        empty_resp = client.get("/api/v1/math/history")
        assert empty_resp.json()["data"]["pagination"]["total_count"] == 0

        # Delete non-existent ID -> should return failure
        del_fail_resp = client.delete(f"/api/v1/math/history/{entry_id}")
        assert del_fail_resp.status_code == 200
        assert del_fail_resp.json()["success"] is False
        assert "not found" in del_fail_resp.json()["error"]


def test_clear_all_history():
    with TestClient(app) as client:
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve x + 1 = 2"})
        client.post("/api/v1/math/solve", json={"language": "en", "question": "solve x + 2 = 4"})

        clear_resp = client.delete("/api/v1/math/history")
        assert clear_resp.status_code == 200
        assert clear_resp.json()["data"]["deleted_count"] == 2

        count_after = client.get("/api/v1/math/history").json()["data"]["pagination"]["total_count"]
        assert count_after == 0
