"""
Evaluate TrOCR on ALL test exercises and report accuracy + improvement suggestions.
"""

from __future__ import annotations

import os
from pathlib import Path
from PIL import Image
import torch

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

SCRIPT_DIR = Path(__file__).resolve().parent
TRAINING_DIR = SCRIPT_DIR.parent
MODELS_DIR = TRAINING_DIR / "models"
EXERCISES_DIR = TRAINING_DIR / "test_exercises"

# Ground truth for all individual crops
ALL_GROUND_TRUTH: list[dict[str, str]] = [
    # Integrals
    {"category": "Integrals", "file": "integrals/crop_ka.png", "text": "int_0^2 3x dx"},
    {"category": "Integrals", "file": "integrals/crop_kha.png", "text": "int_2^4 4x dx"},
    {"category": "Integrals", "file": "integrals/crop_ko.png", "text": "int_0^2 x^2 dx"},
    {"category": "Integrals", "file": "integrals/crop_kho.png", "text": "int_0^2 (x^2 - 5x) dx"},
    {"category": "Integrals", "file": "integrals/crop_ngo.png", "text": "int_1^2 x^2 dx"},
    {"category": "Integrals", "file": "integrals/image5.png", "text": "int_0^2 3x dx"},
    {"category": "Integrals", "file": "integrals/image6.png", "text": "int_0^2 (x^2 - 5x) dx"},

    # Differentials - Ex 1
    {"category": "Differentials (1)", "file": "differentials/crop_ex1_ka.png", "text": "y' = 2x^2 - x + 1"},
    {"category": "Differentials (1)", "file": "differentials/crop_ex1_kha.png", "text": "y' = e^(-2x)"},
    {"category": "Differentials (1)", "file": "differentials/crop_ex1_kho.png", "text": "y' = x/(x^2 - 1)"},

    # Differentials - Ex 2
    {"category": "Differentials (2)", "file": "differentials/crop_ex2_ka.png", "text": "y'/y = cos x, y(pi/2) = e"},
    {"category": "Differentials (2)", "file": "differentials/crop_ex2_kha.png", "text": "y' = e^(2x), y(0) = 5"},
    {"category": "Differentials (2)", "file": "differentials/crop_ex2_ko.png", "text": "(3x^2 - 2)y' = 6, y(1) = 4"},

    # Differentials - Ex 3
    {"category": "Differentials (3)", "file": "differentials/crop_ex3_ka.png", "text": "dy/dx + 2y = 0"},
    {"category": "Differentials (3)", "file": "differentials/crop_ex3_kha.png", "text": "3 dy/dx + y = 0"},
    {"category": "Differentials (3)", "file": "differentials/crop_ex3_ko.png", "text": "2y' - 3y = 0"},

    # Differentials - Ex 4
    {"category": "Differentials (4)", "file": "differentials/crop_ex4_ka.png", "text": "-y' + 2y = 0, y(3) = -2"},
    {"category": "Differentials (4)", "file": "differentials/crop_ex4_kha.png", "text": "2y' + y = 0, y(ln 4) = 1/5"},
    {"category": "Differentials (4)", "file": "differentials/crop_ex4_kho.png", "text": "2y' - 5y = 0, y(1) = -3"},

    # Differentials - Ex 5
    {"category": "Differentials (5)", "file": "differentials/crop_ex5_ka.png", "text": "y = x + e^x, y' - y = 1 - x"},
    {"category": "Differentials (5)", "file": "differentials/crop_ex5_kha.png", "text": "y = e^(3x) - x - 1, y' - 3y = 3x + 2"},
    {"category": "Differentials (5)", "file": "differentials/crop_ex5_ko.png", "text": "y = sin x + cos x, y' + y = 2 cos x"},

    # Differentials - Ex 6
    {"category": "Differentials (6)", "file": "differentials/crop_ex6_ka.png", "text": "f(x) = (x + 1)e^(-2x)"},
    {"category": "Differentials (6)", "file": "differentials/crop_ex6_kha.png", "text": "f(x) = 2e^(-x) + 3e^(3x)"},
    {"category": "Differentials (6)", "file": "differentials/crop_ex6_ko.png", "text": "f(x) = (2 cos 3x - 3 sin 3x)e^x"},

    # Differentials - Ex 7
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_ka.png", "text": "y'' - y = 0, y(0) = 1, y'(0) = -2"},
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_kha.png", "text": "y'' - 2y' + 3y = 0, y(0) = 2, y'(0) = 1"},
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_kho.png", "text": "y'' - 3y' + 2y = 0, y(0) = 1, y'(0) = 3"},
    {"category": "Differentials (7)", "file": "differentials/crop_ex7_ko.png", "text": "y'' + y = 0, y(pi/2) = 3, y'(pi/2) = 2"},

    # Derivatives
    {"category": "Derivatives", "file": "derivatives/image.png", "text": "y = sqrt(x^2 - 1)"},
    {"category": "Derivatives", "file": "derivatives/image1.png", "text": "f(x) = e^x + 3 - e^x/(e^x + 3)"},
    {"category": "Derivatives", "file": "derivatives/image2.png", "text": "f(x) = x ln x / (x + 1)"},

    # Sequences
    {"category": "Sequences", "file": "sequences/image.png", "text": "lim (n^2 + 3n - 1)/(8n^2 - n + 1)"},
    {"category": "Sequences", "file": "sequences/image2.png", "text": "lim (n^2 + sin n)/(5n^2 + cos(pi*n))"},

    # Roots
    {"category": "Roots/Algebra", "file": "image.png", "text": "A = sqrt(128y) - sqrt(2y)"},
]


def find_best_model_dir() -> Path:
    """Find final model or latest checkpoint."""
    final_dir = MODELS_DIR / "trocr-khmer-math-final"
    if final_dir.exists() and (final_dir / "model.safetensors").exists():
        return final_dir

    checkpoints_dir = MODELS_DIR / "trocr-checkpoints"
    if checkpoints_dir.exists():
        ckpts = sorted(checkpoints_dir.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
        if ckpts:
            return ckpts[-1]

    raise FileNotFoundError("No trained TrOCR model or checkpoint found!")


def load_model(model_dir: Path):
    from transformers import (
        TrOCRProcessor,
        VisionEncoderDecoderModel,
        RobertaTokenizer,
        ViTImageProcessor,
    )

    print(f"Loading model from: {model_dir.name}")
    try:
        tok = RobertaTokenizer.from_pretrained(str(model_dir))
        img_proc = ViTImageProcessor.from_pretrained(str(model_dir))
        processor = TrOCRProcessor(image_processor=img_proc, tokenizer=tok)
    except Exception:
        tok = RobertaTokenizer.from_pretrained("roberta-large")
        img_proc = ViTImageProcessor.from_pretrained("microsoft/trocr-base-printed")
        processor = TrOCRProcessor(image_processor=img_proc, tokenizer=tok)

    model = VisionEncoderDecoderModel.from_pretrained(str(model_dir))

    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    model.to(device)
    model.eval()
    return processor, model, device


def compute_char_error(expected: str, predicted: str) -> tuple[int, int]:
    """Compute (errors, total_chars)."""
    r, h = expected.strip(), predicted.strip()
    total = max(len(r), 1)
    errors = 0
    for i in range(max(len(r), len(h))):
        rc = r[i] if i < len(r) else ""
        hc = h[i] if i < len(h) else ""
        if rc != hc:
            errors += 1
    return errors, total


def main():
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║     TrOCR Testing on ALL Exercise Images                     ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    import sys
    sys.path.insert(0, str(TRAINING_DIR.parent))
    from app.ocr.engines.trocr import TrOCRVisionEngine

    engine = TrOCRVisionEngine()
    print(f"Loaded engine on device: {engine.device}")
    print()

    results = []
    total_samples = 0
    exact_matches = 0
    total_char_errors = 0
    total_chars = 0

    print(f"{'Category':<18} | {'File':<25} | {'Match':<5} | {'Predicted':<35} | {'Expected'}")
    print("-" * 115)

    for item in ALL_GROUND_TRUTH:
        img_path = EXERCISES_DIR / item["file"]
        if not img_path.exists():
            continue

        total_samples += 1
        with open(img_path, "rb") as f:
            ocr_res = engine.detect(f.read())

        pred = (ocr_res.detected_text or "").strip()
        expected = item["text"].strip()

        is_exact = (pred == expected)
        if is_exact:
            exact_matches += 1
            match_str = "✅ YES"
        else:
            match_str = "❌ NO "

        errors, chars = compute_char_error(expected, pred)
        total_char_errors += errors
        total_chars += chars

        filename = Path(item["file"]).name
        print(f"{item['category']:<18} | {filename:<25} | {match_str} | {pred:<35} | {expected}")

        results.append({
            "category": item["category"],
            "file": item["file"],
            "expected": expected,
            "predicted": pred,
            "is_exact": is_exact,
            "errors": errors,
        })

    em_rate = (exact_matches / total_samples * 100) if total_samples else 0.0
    cer = (total_char_errors / total_chars * 100) if total_chars else 0.0

    print("-" * 115)
    print()
    print("📊 SUMMARY RESULTS:")
    print(f"   Total Tested Exercises: {total_samples}")
    print(f"   Exact Match Accuracy:   {exact_matches}/{total_samples} ({em_rate:.1f}%)")
    print(f"   Character Error Rate:   {cer:.2f}%")
    print(f"   Model Accuracy:         {(100.0 - cer):.2f}%")
    print()

    # Identify any errors
    failures = [r for r in results if not r["is_exact"]]
    if failures:
        print("🔍 Exercises Needing Improvement:")
        for f in failures:
            print(f"   - [{f['category']}] {f['file']}")
            print(f"       Expected:  {f['expected']}")
            print(f"       Predicted: {f['predicted']}")
    else:
        print("🎉 ALL EXERCISES RECOGNIZED WITH 100% ACCURACY!")
    print()


if __name__ == "__main__":
    main()
