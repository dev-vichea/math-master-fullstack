"""
Tests for expanded Khmer keyword recognition in intent classifier.

Covers:
  - New solve keywords (ស្វែងរក, ណា, គណនា, គិត, etc.)
  - New simplify keywords (សាមញ្ញ, បង្រួម, កាត់)
  - New evaluate keywords (ផ្ដល់ជូន, លទ្ធផល, ចម្លើយ)
  - Word problem keywords (បញ្ហា, សំណួរ, លំហាត់, តើ)
  - Natural Khmer phrasings
"""
from fastapi.testclient import TestClient

from app.main import app


def test_solve_keyword_sveng_rok():
    """Test 'ស្វែងរក' (search/find) triggers solve intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ស្វែងរក x ពី 2x + 5 = 15"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"
        assert body["data"]["answer"] == "5"


def test_solve_keyword_rok():
    """Test short form 'រក' (find) triggers solve intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "រក x នៅពេល x + 10 = 25"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"


def test_solve_keyword_na():
    """Test 'ណា' (what) in questions triggers solve intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "x ណា បើ 3x = 12"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"
        assert body["data"]["answer"] == "4"


def test_solve_keyword_konan():
    """Test 'គណនា' (calculate/compute) with equation triggers solve"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គណនា x ពី 5x - 3 = 17"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"
        assert body["data"]["answer"] == "4"


def test_solve_keyword_kit():
    """Test 'គិត' (think/calculate) with equation triggers solve"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គិត x ក្នុង x^2 = 16"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"


def test_solve_keyword_sveng_yok():
    """Test 'ស្វែងយក' (seek/obtain) triggers solve"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ស្វែងយក x ពី 4x + 2 = 18"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"


def test_solve_keyword_douh_short():
    """Test short form 'ដោះ' (solve) triggers solve intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះ 2x = 10"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"
        assert body["data"]["answer"] == "5"


def test_simplify_keyword_samany():
    """Test 'សាមញ្ញ' (simple) triggers simplify intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "សាមញ្ញ 2x + 3x"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "simplify_expression"


def test_simplify_keyword_bongrum():
    """Test 'បង្រួម' (condense/reduce) triggers simplify intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "បង្រួម 4/8"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "simplify_expression"


def test_simplify_keyword_kat():
    """Test 'កាត់' (cut/reduce) triggers simplify intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "កាត់ 6/9"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "simplify_expression"


def test_evaluate_keyword_pdal_jun():
    """Test 'ផ្ដល់ជូន' (provide/give) triggers evaluate"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ផ្ដល់ជូន លទ្ធផល 5 + 3 * 2"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_evaluate_keyword_lotthaphal():
    """Test 'លទ្ធផល' (result) triggers evaluate"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "លទ្ធផល 10 - 3"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_evaluate_keyword_chhamlei():
    """Test 'ចម្លើយ' (answer) triggers evaluate"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ចម្លើយ 25 / 5"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_word_problem_keyword_bonha():
    """Test 'បញ្ហា' (problem) triggers evaluate when numbers present"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "បញ្ហា៖ 15 + 20"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_word_problem_keyword_somnoua():
    """Test 'សំណួរ' (question) triggers evaluate when numbers present"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "សំណួរ៖ 100 - 45"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_word_problem_keyword_lomhat():
    """Test 'លំហាត់' (exercise) triggers evaluate when numbers present"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "លំហាត់ 7 * 8"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_word_problem_keyword_tae():
    """Test 'តើ' (question marker) triggers evaluate when numbers present"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "តើ 12 + 8 ស្មើនឹងប៉ុន្មាន"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_natural_phrasing_help_solve():
    """Test 'ជួយដោះស្រាយ' (help solve) works"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ជួយដោះស្រាយ 3x - 7 = 8"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"
        assert body["data"]["answer"] == "5"


def test_natural_phrasing_what_value():
    """Test 'តម្លៃ' (value) alone triggers solve with equation"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "តម្លៃ x នៅក្នុង x + 5 = 12"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "solve_equation"


def test_multiple_keywords_priority():
    """Test that solve keywords have priority over evaluate keywords"""
    with TestClient(app) as client:
        # Both 'ដោះស្រាយ' (solve) and 'គណនា' (calculate) present
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គណនា និង ដោះស្រាយ 2x = 8"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Solve should take priority
        assert body["data"]["detected_intent"] == "solve_equation"


def test_extended_fraction_keyword():
    """Test 'ប្រភាគធម្មតា' (common fraction) keyword"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ប្រភាគធម្មតា 3/4 + 1/4"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_extended_percentage_keyword():
    """Test 'ចំនួនភាគរយ' (percentage amount) keyword"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ចំនួនភាគរយ 25 នៃ 200"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["detected_intent"] == "evaluate_expression"
