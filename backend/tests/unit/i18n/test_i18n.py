"""
Unit tests for app.i18n language management, translations, formatters, and endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.i18n import (
    DEFAULT_LANGUAGE,
    FALLBACK_LANGUAGE,
    LANGUAGE_INFO,
    SUPPORTED_LANGUAGES,
    Language,
    create_bilingual_step,
    detect_language,
    format_bilingual,
    get_all_translations,
    get_bilingual,
    get_bilingual_term,
    get_current_language,
    get_language_info,
    is_bilingual_text,
    is_english_text,
    is_khmer_char,
    is_khmer_text,
    khmer_digits_to_arabic,
    localize_solution_step,
    normalize_bilingual_text,
    normalize_english_text,
    normalize_khmer_text,
    normalize_language,
    set_current_language,
    t,
    translate,
    translate_math_term,
    use_language,
)
from app.main import app


class TestLanguageCore:
    def test_language_enum_values(self):
        assert Language.KM.value == "km"
        assert Language.EN.value == "en"
        assert Language.KHMER == Language.KM
        assert Language.ENGLISH == Language.EN
        assert Language.KM.code == "km"
        assert Language.KM.label == "ភាសាខ្មែរ"
        assert Language.EN.label == "English"

    def test_supported_languages(self):
        assert Language.KM in SUPPORTED_LANGUAGES
        assert Language.EN in SUPPORTED_LANGUAGES
        assert DEFAULT_LANGUAGE == Language.KM
        assert FALLBACK_LANGUAGE == Language.EN

    def test_normalize_language(self):
        assert normalize_language("km") == Language.KM
        assert normalize_language("khmer") == Language.KM
        assert normalize_language("ភាសាខ្មែរ") == Language.KM
        assert normalize_language("en") == Language.EN
        assert normalize_language("english") == Language.EN
        assert normalize_language("ENG") == Language.EN
        assert normalize_language(None) == DEFAULT_LANGUAGE
        assert normalize_language("unknown_lang") == DEFAULT_LANGUAGE
        assert normalize_language(Language.EN) == Language.EN

    def test_script_detection(self):
        assert is_khmer_char("ក") is True
        assert is_khmer_char("a") is False
        assert is_khmer_char("") is False

        assert is_khmer_text("ដោះស្រាយសមីការ 2x + 5 = 15") is True
        assert is_khmer_text("Solve for x: 2x + 5 = 15") is False

        assert is_english_text("Solve for x: 2x + 5 = 15") is True
        assert is_english_text("123 + 456") is False

        assert is_bilingual_text("លំហាត់ (Exercise): 2x + 5 = 15") is True
        assert is_bilingual_text("2x + 5 = 15") is False

    def test_detect_language(self):
        assert detect_language("ដោះស្រាយ 2x + 5 = 15") == Language.KM
        assert detect_language("Solve the equation 2x + 5 = 15") == Language.EN
        assert detect_language("Exercise 1: 3x - 9 = 0") == Language.EN
        assert detect_language("លំហាត់ទី១ ៖ 3x - 9 = 0") == Language.KM
        assert detect_language("2x + 5 = 15", default=Language.KM) == Language.KM

    def test_language_info(self):
        km_info = get_language_info(Language.KM)
        assert km_info["code"] == "km"
        assert km_info["name"] == "Khmer"
        assert km_info["native_name"] == "ភាសាខ្មែរ"
        assert km_info["is_default"] is True

        en_info = get_language_info(Language.EN)
        assert en_info["code"] == "en"
        assert en_info["name"] == "English"
        assert en_info["is_default"] is False

    def test_language_context(self):
        orig = get_current_language()
        set_current_language(Language.EN)
        assert get_current_language() == Language.EN

        with use_language(Language.KM):
            assert get_current_language() == Language.KM

        assert get_current_language() == Language.EN
        set_current_language(orig)


class TestTranslations:
    def test_basic_translation(self):
        assert translate("status.success", "km") == "ជោគជ័យ"
        assert translate("status.success", "en") == "Success"
        assert translate("type.linear_equation", "en") == "Linear equation"
        assert "សមីការ" in translate("type.linear_equation", "km")

    def test_translation_interpolation(self):
        assert t("step.order", "km", order=2) == "ជំហានទី 2"
        assert t("step.order", "en", order=2) == "Step 2"

    def test_translation_fallback(self):
        assert translate("nonexistent.key.xyz", "km", default="Fallback") == "Fallback"
        assert translate("nonexistent.key.xyz", "en") == "nonexistent.key.xyz"

    def test_get_bilingual_and_format(self):
        bi = get_bilingual("status.success")
        assert bi["km"] == "ជោគជ័យ"
        assert bi["en"] == "Success"

        formatted = format_bilingual("status.success")
        assert formatted == "ជោគជ័យ / Success"

    def test_get_all_translations(self):
        all_trans = get_all_translations()
        assert "status.success" in all_trans
        assert "km" in all_trans["status.success"]
        assert "en" in all_trans["status.success"]

        km_trans = get_all_translations(Language.KM)
        assert km_trans["status.success"] == "ជោគជ័យ"


class TestDigitInputNormalizer:
    def test_digit_conversion(self):
        # Conversion from Khmer digits in student/OCR input to standard Arabic math digits
        assert khmer_digits_to_arabic("២x + ៥ = ១៥") == "2x + 5 = 15"
        assert khmer_digits_to_arabic("10 + 20") == "10 + 20"
        assert khmer_digits_to_arabic("") == ""


class TestGlossaryAndNormalizer:
    def test_glossary_term_translation(self):
        assert translate_math_term("derivative", "km") == "ដេរីវេ"
        assert translate_math_term("ដេរីវេ", "en") == "derivative"
        assert translate_math_term("integral", "km") == "អាំងតេក្រាល"
        assert translate_math_term("matrix", "km") == "ម៉ាទ្រីស"

    def test_get_bilingual_term(self):
        bi = get_bilingual_term("derivative")
        assert bi is not None
        assert bi["km"] == "ដេរីវេ"
        assert bi["en"] == "derivative"

    def test_normalizer(self):
        text_km = "២០ភាគរយ នៃ 100"
        normalized = normalize_khmer_text(text_km)
        assert "(20/100)" in normalized

        text_bilingual = "Exercise (លំហាត់ទី 1)៖ 2x + 5 = 15"
        norm_bi = normalize_bilingual_text(text_bilingual)
        assert ":" in norm_bi


class TestBilingualSteps:
    def test_create_bilingual_step(self):
        step = create_bilingual_step(
            order=1,
            expression="2x + 5 = 15",
            description_km="សមីការដើម",
            description_en="Initial equation",
            title_km="ជំហានដំបូង",
            title_en="Initial step",
        )
        assert step.order == 1
        assert step.description_km == "សមីការដើម"
        assert step.description_en == "Initial equation"
        assert step.expression == "2x + 5 = 15"

        km_localized = localize_solution_step(step, "km")
        assert km_localized["description"] == "សមីការដើម"

        en_localized = localize_solution_step(step, "en")
        assert en_localized["description"] == "Initial equation"


class TestI18nApiEndpoints:
    def test_list_languages_endpoint(self):
        with TestClient(app) as client:
            res = client.get("/api/v1/i18n/languages")
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["data"]["default_language"] == "km"
            codes = [lang["code"] for lang in data["data"]["supported_languages"]]
            assert "km" in codes
            assert "en" in codes

    def test_get_translations_endpoint(self):
        with TestClient(app) as client:
            res = client.get("/api/v1/i18n/translations?lang=km")
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["data"]["translations"]["status.success"] == "ជោគជ័យ"

            res_en = client.get("/api/v1/i18n/translations?lang=en")
            assert res_en.status_code == 200
            data_en = res_en.json()
            assert data_en["data"]["translations"]["status.success"] == "Success"

    def test_detect_language_endpoint(self):
        with TestClient(app) as client:
            res_km = client.post(
                "/api/v1/i18n/detect",
                json={"text": "ដោះស្រាយសមីការ 2x + 5 = 15"},
            )
            assert res_km.status_code == 200
            assert res_km.json()["data"]["detected_language"] == "km"

            res_en = client.post(
                "/api/v1/i18n/detect",
                json={"text": "Solve the equation 2x + 5 = 15"},
            )
            assert res_en.status_code == 200
            assert res_en.json()["data"]["detected_language"] == "en"

    def test_translate_term_endpoint(self):
        with TestClient(app) as client:
            res = client.get("/api/v1/i18n/terms/translate?term=derivative&target_lang=km")
            assert res.status_code == 200
            assert res.json()["data"]["translated_term"] == "ដេរីវេ"
