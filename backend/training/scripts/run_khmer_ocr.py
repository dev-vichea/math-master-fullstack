"""
Run Khmer OCR on an image and optionally solve the detected math expression.

Usage:
    # Run OCR with Kiri OCR (default):
    python training/scripts/run_khmer_ocr.py --image path/to/image.png

    # Run OCR and pass detected text through the math solver:
    python training/scripts/run_khmer_ocr.py --image path/to/image.png --solve

    # Use a different provider (e.g. tesseract, google, mathpix):
    python training/scripts/run_khmer_ocr.py --image path/to/image.png --provider tesseract
"""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path so app imports work
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.ocr.factory import create_vision_engine, list_available_providers
from app.services.math_service import MathProcessingError, process_question


def main():
    parser = argparse.ArgumentParser(description="Khmer OCR Runner & Math Solver")
    parser.add_argument(
        "--image",
        type=str,
        default="training/sample_data/images/000001.png",
        help="Path to the image file to run OCR on",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="kiri",
        help="OCR provider to use ('kiri', 'tesseract', 'mathpix', 'google')",
    )
    parser.add_argument(
        "--solve",
        action="store_true",
        help="If set, solves the detected math expression and outputs step-by-step solution",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading OCR provider '{args.provider}'...")
    try:
        engine = create_vision_engine(args.provider)
    except Exception as e:
        print(f"Error initializing provider '{args.provider}': {e}", file=sys.stderr)
        print("\nAvailable providers on this system:")
        for name, available in list_available_providers().items():
            status = "✓ Available" if available else "✗ Not installed / configured"
            print(f"  - {name}: {status}")
        sys.exit(1)

    print(f"Processing image: {image_path}")
    image_bytes = image_path.read_bytes()
    result = engine.detect(image_bytes)

    if result.error_message or not result.detected_text:
        print(f"OCR Error: {result.error_message or 'No text detected'}", file=sys.stderr)
        sys.exit(1)

    print(f"\n================ OCR RESULT ================")
    print(f"Detected Text : {result.detected_text}")
    print(f"Confidence    : {result.confidence * 100:.1f}%")
    print(f"============================================")

    if args.solve:
        print("\nSolving detected expression...")
        try:
            solution = process_question(result.detected_text)
            print(f"Problem Type : {solution.problem_type}")
            print(f"Answer       : {solution.answer}")
            print(f"Verified     : {'✓ Yes' if solution.is_verified else '✗ No'}")
            print("\nSteps:")
            for step in solution.steps:
                print(f"  Step {step.order}: {step.description_km}")
                if step.description_en:
                    print(f"          ({step.description_en})")
                if step.expression:
                    print(f"          {step.expression}")
        except MathProcessingError as e:
            print(f"Math solver error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
