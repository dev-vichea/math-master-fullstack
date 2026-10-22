"""
Comprehensive Test Runner for UniMERNet Vision Engine on Math Lab Test Exercises.
"""

import os
import sys
import time
from pathlib import Path
from PIL import Image

# Ensure math-lab backend is on path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ocr.engines.unimernet_engine import UniMERNetVisionEngine

def run_tests():
    print("=" * 70)
    print("Initializing UniMERNet Vision Engine in Math Lab...")
    print("=" * 70)
    start_init = time.time()
    engine = UniMERNetVisionEngine()
    print(f"Engine ready on {engine.device} (loaded in {time.time() - start_init:.2f}s)\n")

    base_dir = backend_dir / "training" / "test_exercises"

    categories = [
        ("Handwritten Notebooks (handwrites/)", sorted(list((base_dir / "handwrites").glob("*.png")))),
        ("Handwritten Single Images (root test_exercises/)", [
            base_dir / "handwrite.jpg",
            base_dir / "image.png",
            base_dir / "image copy.png",
            base_dir / "image copy 2.png",
            base_dir / "image copy 3.png",
            base_dir / "image copy 4.png",
            base_dir / "image copy 5.png",
            base_dir / "factorization.jpg",
        ]),
        ("UniMERNet Benchmark Handwritten Samples (hwe_*.png)", sorted(list((base_dir / "unimernet_samples").glob("hwe_*.png")))),
        ("Limit Test Exercises (limit/)", sorted(list((base_dir / "limit").glob("*.png")))[:6]),
    ]

    for category_name, file_list in categories:
        valid_files = [p for p in file_list if p.exists() and p.stat().st_size > 1000]
        if not valid_files:
            continue

        print("\n" + "=" * 70)
        print(f"CATEGORY: {category_name} ({len(valid_files)} images)")
        print("=" * 70)

        for img_path in valid_files:
            rel_name = img_path.relative_to(base_dir)
            t0 = time.time()
            res = engine.detect_file(img_path)
            elapsed = time.time() - t0

            status = "SUCCESS" if res.detected_text else "FAILED"
            print(f"\n[File]: {rel_name} ({elapsed:.2f}s) -> {status}")
            if res.detected_text:
                print(f"LaTeX:\n  {res.detected_text}")
            else:
                print(f"Error: {res.error_message}")

if __name__ == "__main__":
    run_tests()
