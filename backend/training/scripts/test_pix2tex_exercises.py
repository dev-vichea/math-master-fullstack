"""
Benchmark LaTeX-OCR (pix2tex) on all test exercises and evaluate end-to-end solving.
"""

from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine
from app.parser.exercise_parser.exercise_parser import parse_exercise
from app.services.math_service import MathService
from app.services.vision_service import VisionService

EXERCISES_DIR = BACKEND_DIR / "training" / "test_exercises"

ALL_GROUND_TRUTH = [
    # Integrals
    {"category": "Integrals", "file": "integrals/crop_ka.png", "target": "\\int_0^2 3x dx"},
    {"category": "Integrals", "file": "integrals/crop_kha.png", "target": "\\int_2^4 4x dx"},
    {"category": "Integrals", "file": "integrals/crop_ko.png", "target": "\\int_0^2 x^2 dx"},
    {"category": "Integrals", "file": "integrals/crop_kho.png", "target": "\\int_0^2 (x^2 - 5x) dx"},
    {"category": "Integrals", "file": "integrals/crop_ngo.png", "target": "\\int_1^2 x^2 dx"},
    {"category": "Integrals", "file": "integrals/image5.png", "target": "\\int_0^2 3x dx"},
    {"category": "Integrals", "file": "integrals/image6.png", "target": "\\int_0^2 (x^2 - 5x) dx"},

    # Differentials - Ex 1
    {"category": "Differentials (1)", "file": "differentials/crop_ex1_ka.png", "target": "y' = 2x^2 - x + 1"},
    {"category": "Differentials (1)", "file": "differentials/crop_ex1_kha.png", "target": "y' = e^(-2x)"},
    {"category": "Differentials (1)", "file": "differentials/crop_ex1_kho.png", "target": "y' = x/(x^2 - 1)"},

    # Differentials - Ex 2
    {"category": "Differentials (2)", "file": "differentials/crop_ex2_ka.png", "target": "y'/y = \\cos x, y(\\pi/2) = e"},
    {"category": "Differentials (2)", "file": "differentials/crop_ex2_kha.png", "target": "y' = e^(2x), y(0) = 5"},
    {"category": "Differentials (2)", "file": "differentials/crop_ex2_ko.png", "target": "(3x^2 - 2)y' = 6, y(1) = 4"},

    # Differentials - Ex 3
    {"category": "Differentials (3)", "file": "differentials/crop_ex3_ka.png", "target": "dy/dx + 2y = 0"},
    {"category": "Differentials (3)", "file": "differentials/crop_ex3_kha.png", "target": "3 dy/dx + y = 0"},
    {"category": "Differentials (3)", "file": "differentials/crop_ex3_ko.png", "target": "2y' - 3y = 0"},

    # Differentials - Ex 4
    {"category": "Differentials (4)", "file": "differentials/crop_ex4_ka.png", "target": "-y' + 2y = 0, y(3) = -2"},
    {"category": "Differentials (4)", "file": "differentials/crop_ex4_kha.png", "target": "2y' + y = 0, y(\\ln 4) = 1/5"},
    {"category": "Differentials (4)", "file": "differentials/crop_ex4_kho.png", "target": "2y' - 5y = 0, y(1) = -3"},

    # Differentials - Ex 5
    {"category": "Differentials (5)", "file": "differentials/crop_ex5_ka.png", "target": "y = x + e^x, y' - y = 1 - x"},
    {"category": "Differentials (5)", "file": "differentials/crop_ex5_kha.png", "target": "y = e^(3x) - x - 1, y' - 3y = 3x + 2"},
    {"category": "Differentials (5)", "file": "differentials/crop_ex5_ko.png", "target": "y = \\sin x + \\cos x, y' + y = 2 \\cos x"},

    # Differentials - Ex 6
    {"category": "Differentials (6)", "file": "differentials/crop_ex6_ka.png", "target": "f(x) = (x + 1)e^(-2x)"},
    {"category": "Differentials (6)", "file": "differentials/crop_ex6_kha.png", "target": "f(x) = 2e^(-x) + 3e^(3x)"},
    {"category": "Differentials (6)", "file": "differentials/crop_ex6_ko.png", "target": "f(x) = (2 \\cos 3x - 3 \\sin 3x)e^x"},

    # Differentials - Ex 7
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_ka.png", "target": "y'' - y = 0, y(0) = 1, y'(0) = -2"},
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_kha.png", "target": "y'' - 2y' + 3y = 0, y(0) = 2, y'(0) = 1"},
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_kho.png", "target": "y'' - 3y' + 2y = 0, y(0) = 1, y'(0) = 3"},
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_ko.png", "target": "y'' + y = 0, y(\\pi/2) = 3, y'(\\pi/2) = 2"},

    # Derivatives
    {"category": "Derivatives", "file": "derivatives/image.png", "target": "y = \\sqrt{x^2 - 1}"},
    {"category": "Derivatives", "file": "derivatives/image1.png", "target": "f(x) = e^x + 3 - e^x/(e^x + 3)"},
    {"category": "Derivatives", "file": "derivatives/image2.png", "target": "f(x) = x \\ln x / (x + 1)"},

    # Sequences
    {"category": "Sequences", "file": "sequences/image.png", "target": "\\lim (n^2 + 3n - 1)/(8n^2 - n + 1)"},
    {"category": "Sequences", "file": "sequences/image2.png", "target": "\\lim (n^2 + \\sin n)/(5n^2 + \\cos(\\pi n))"},

    # Roots
    {"category": "Roots/Algebra", "file": "image.png", "target": "A = \\sqrt{128y} - \\sqrt{2y}"},
]


def run_benchmark():
    engine = Pix2TexVisionEngine()
    vision_service = VisionService(vision_engine=engine)

    total = 0
    ocr_success = 0
    solve_success = 0

    results = []

    print("=" * 80)
    print("LaTeX-OCR (pix2tex) Benchmark on Test Exercises")
    print("=" * 80)

    for item in ALL_GROUND_TRUTH:
        img_path = EXERCISES_DIR / item["file"]
        if not img_path.exists():
            continue

        total += 1
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        res = engine.detect(img_bytes)
        detected_text = res.detected_text or ""

        parsed = parse_exercise(detected_text)
        expr_to_solve = parsed.primary_expression or detected_text

        # Try end-to-end solving through VisionService
        solved = False
        solution_str = ""
        error_msg = ""
        try:
            process_res = vision_service.process_image(img_bytes)
            ans = process_res.get("answer")
            if ans is not None and str(ans).strip():
                solved = True
                solution_str = str(ans)
            elif process_res.get("steps"):
                solved = True
                solution_str = "Solved with steps"
        except Exception as e:
            error_msg = str(e)

        if detected_text:
            ocr_success += 1
        if solved:
            solve_success += 1

        print(f"\n[{item['category']}] {item['file']}")
        print(f"  Target  : {item['target']}")
        print(f"  Detected: {detected_text}")
        print(f"  Parsed  : {expr_to_solve}")
        print(f"  Solved  : {'✓ ' + solution_str if solved else '✗ ' + error_msg[:60]}")

        results.append({
            "category": item["category"],
            "file": item["file"],
            "target": item["target"],
            "detected": detected_text,
            "parsed": expr_to_solve,
            "solved": solved,
            "result": solution_str if solved else None,
        })

    print("\n" + "=" * 80)
    print(f"BENCHMARK SUMMARY:")
    print(f"Total Images Evaluated : {total}")
    print(f"OCR Detections         : {ocr_success}/{total} ({ocr_success/total*100:.1f}%)")
    print(f"End-to-End Solved      : {solve_success}/{total} ({solve_success/total*100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
