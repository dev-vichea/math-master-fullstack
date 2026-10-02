"""
Shared test fixtures and configuration for the Khmer Math Lab test suite.

Usage:
    Fixtures defined here are automatically available to all test files
    in all subdirectories without explicit imports.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client for API endpoint tests."""
    return TestClient(app)


@pytest.fixture
def sample_expressions() -> dict[str, str]:
    """Common math expressions used across multiple test modules."""
    return {
        "linear": "2x + 3 = 7",
        "quadratic": "x^2 - 5x + 6 = 0",
        "polynomial": "x^3 - 6x^2 + 11x - 6 = 0",
        "derivative": "d/dx(x^3 + 2x)",
        "integral": "∫(2x + 1)dx",
        "limit": "lim(x→0) sin(x)/x",
        "khmer_linear": "ដោះស្រាយ 2x + 3 = 7",
    }
