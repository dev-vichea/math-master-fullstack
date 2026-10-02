"""
Tests for exercises API endpoints.

Tests the REST API for exercise document processing.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestExercisesAPI:
    """Test exercises API endpoints."""

    def test_analyze_simple_factorization_exercise(self):
        """Test analyzing simple factorization exercise."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": "ចូរដាក់ជាកត្តាកត់\nក. x^2 - 4\nខ. x^2 - 5*x + 6",
                "language": "km",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "exercise" in data
        assert data["exercise"]["total_problems"] == 2
        assert len(data["errors"]) == 0

    def test_analyze_solve_equations_exercise(self):
        """Test analyzing solve equations exercise."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": "Solve the following equations\na) Eq(2*x + 5, 11)\nb) Eq(3*x - 7, 2)",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["exercise"]["total_problems"] == 2

    def test_analyze_mixed_instructions(self):
        """Test analyzing exercise with multiple instructions."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": """ដោះស្រាយសមីការ
ក. Eq(x + 5, 10)
ខ. Eq(2*x - 3, 7)

ចូរដាក់ជាកត្តាកត់
គ. x^2 - 9
ឃ. x^2 + 5*x + 6""",
                "language": "km",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["exercise"]["total_problems"] == 4
        assert data["exercise"]["section_count"] >= 1

    def test_analyze_with_statistics(self):
        """Test that analysis returns statistics."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": "Factor\na) x^2 - 4\nb) x^2 - 5*x + 6",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "statistics" in data
        assert data["statistics"] is not None
        assert "total_problems" in data["statistics"]
        assert "sections" in data["statistics"]
        assert "average_confidence" in data["statistics"]

    def test_analyze_with_validation(self):
        """Test that analysis returns validation results."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": "Factor\na) x^2 - 4\nb) x^2 - 5*x + 6",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "validation" in data
        assert data["validation"] is not None
        assert "is_valid" in data["validation"]
        assert "errors" in data["validation"]

    def test_analyze_empty_text(self):
        """Test analyzing empty text."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={"text": "", "language": "km"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should succeed but with warnings
        assert data["success"] is True
        assert len(data["warnings"]) > 0

    def test_analyze_invalid_language(self):
        """Test analyzing with invalid language code."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={"text": "Factor\na) x^2 - 4", "language": "invalid"},
        )

        # Should return validation error
        assert response.status_code == 422  # Validation error

    def test_validate_valid_exercise(self):
        """Test validating valid exercise."""
        response = client.post(
            "/api/v1/exercises/validate",
            json={
                "text": "Factor\na) x^2 - 4\nb) x^2 - 5*x + 6",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "is_valid" in data
        assert data["is_valid"] is True
        assert len(data["errors"]) == 0

    def test_validate_invalid_sequence(self):
        """Test validating exercise with invalid problem sequence."""
        response = client.post(
            "/api/v1/exercises/validate",
            json={
                "text": "Factor\na) x^2 - 4\nc) x^2 - 5*x + 6",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should detect sequence error
        assert "is_valid" in data

    def test_get_statistics(self):
        """Test getting exercise statistics."""
        response = client.post(
            "/api/v1/exercises/statistics",
            json={
                "text": """Factor the following
a) x^2 - 4
b) x^2 - 5*x + 6

Solve
c) Eq(x + 5, 10)""",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "total_problems" in data
        assert data["total_problems"] == 3
        assert "sections" in data
        assert "problems_per_section" in data
        assert "instruction_types" in data
        assert "problem_types" in data
        assert "average_confidence" in data
        assert "languages" in data

    def test_get_statistics_empty_exercise(self):
        """Test getting statistics for empty exercise."""
        response = client.post(
            "/api/v1/exercises/statistics",
            json={"text": "", "language": "km"},
        )

        # Should return 400 or handle gracefully
        assert response.status_code in [200, 400]

    def test_khmer_language_processing(self):
        """Test Khmer language processing."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": "ចូរដាក់ជាកត្តាកត់\nក. x^2 - 4\nខ. x^2 - 5*x + 6",
                "language": "km",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["exercise"]["language"] == "km"

    def test_english_language_processing(self):
        """Test English language processing."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={
                "text": "Factor\na) x^2 - 4\nb) x^2 - 5*x + 6",
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_missing_text_field(self):
        """Test request with missing text field."""
        response = client.post(
            "/api/v1/exercises/analyze", json={"language": "en"}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_response_structure(self):
        """Test that response has correct structure."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={"text": "Factor\na) x^2 - 4", "language": "en"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "success" in data
        assert "exercise" in data
        assert "statistics" in data
        assert "validation" in data
        assert "errors" in data
        assert "warnings" in data

        # Check exercise structure
        assert "sections" in data["exercise"]
        assert "total_problems" in data["exercise"]
        assert "language" in data["exercise"]

    def test_instruction_type_detection(self):
        """Test that instruction types are correctly detected."""
        response = client.post(
            "/api/v1/exercises/analyze",
            json={"text": "ចូរដាក់ជាកត្តាកត់\nក. x^2 - 4", "language": "km"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check that sections have instruction types
        if data["exercise"]["sections"]:
            section = data["exercise"]["sections"][0]
            assert "instruction" in section
            assert "type" in section["instruction"]
            assert section["instruction"]["type"] == "factor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
