"""
Real worksheet test using Kiri OCR.

This script tests the complete pipeline with an actual worksheet image:
1. Raw Kiri OCR output
2. Parsed document structure
3. Detected instruction
4. Detected problems
5. Instruction → problem relationships
6. Classification for each problem
7. Solver input
8. Final solutions
"""

import json
import sys
from pathlib import Path

from app.classifier.problem_classifier.classifier import classify_problem
from app.ocr.factory import create_vision_engine
from app.parser.math_parser.expression_parser import parse_math_text
from app.services.exercise_service import ExerciseService
from app.services.worksheet_service import WorksheetProcessor
from app.solvers import solve


def print_section(title: str, content: str = ""):
    """Print a formatted section."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    if content:
        print(content)


def main():
    # Load the factorization worksheet image
    image_path = Path("training/test_exercises/factorization.jpg")
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print(f"📄 Testing with: {image_path}")
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    # ========================================================================
    # STAGE 1: Raw OCR Output (Kiri OCR - Fixed)
    # ========================================================================
    print_section("STAGE 1: Raw OCR Output (Kiri OCR - Fixed)")
    
    # Use Kiri OCR (now with v0.2.15 which auto-infers model architecture)
    print("Using Kiri OCR v0.2.15...")
    vision_engine = create_vision_engine("kiri")
    print(f"✓ OCR engine: {type(vision_engine).__name__}")
    
    ocr_result = vision_engine.detect(image_bytes)
    
    print(f"\n✓ OCR Confidence: {ocr_result.confidence}")
    print(f"✓ Error: {ocr_result.error_message}")
    print(f"\n--- Raw Detected Text ---")
    print(ocr_result.detected_text)
    
    if ocr_result.exercise_metadata:
        print(f"\n--- OCR Metadata ---")
        print(json.dumps(ocr_result.exercise_metadata, indent=2, ensure_ascii=False))
    
    if ocr_result.error_message or not ocr_result.detected_text:
        print("\n❌ OCR failed, cannot continue")
        sys.exit(1)
    
    # ========================================================================
    # STAGE 2: Parsed Document Structure
    # ========================================================================
    print_section("STAGE 2: Parsed Document Structure")
    
    exercise_service = ExerciseService()
    
    try:
        processing_result = exercise_service.process_text(ocr_result.detected_text)
        exercise = processing_result.exercise
        
        print(f"✓ Success: {processing_result.success}")
        print(f"✓ Sections: {len(exercise.sections)}")
        print(f"✓ Language: {exercise.language}")
        
        if processing_result.errors:
            print(f"\n⚠️  Errors:")
            for error in processing_result.errors:
                print(f"  - {error}")
        
        if processing_result.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in processing_result.warnings:
                print(f"  - {warning}")
                
    except Exception as e:
        print(f"\n❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ========================================================================
    # STAGE 3: Detected Instruction
    # ========================================================================
    print_section("STAGE 3: Detected Instruction")
    
    for i, section in enumerate(exercise.sections):
        print(f"\n--- Section {i} ---")
        if section.instruction:
            inst = section.instruction
            print(f"✓ Text: {inst.text}")
            print(f"✓ Type: {inst.instruction_type.value}")
            print(f"✓ Language: {inst.language}")
            print(f"✓ Confidence: {inst.confidence}")
            print(f"✓ Keywords: {inst.detected_keywords}")
        else:
            print("⚠️  No instruction detected")
    
    # ========================================================================
    # STAGE 4: Detected Problems
    # ========================================================================
    print_section("STAGE 4: Detected Problems")
    
    total_problems = 0
    for i, section in enumerate(exercise.sections):
        print(f"\n--- Section {i} ({len(section.problems)} problems) ---")
        for j, problem in enumerate(section.problems):
            total_problems += 1
            print(f"\nProblem {j+1}:")
            print(f"  Label: {problem.label}")
            print(f"  Label Type: {problem.label_type.value}")
            print(f"  Expression: {problem.problem.expression or problem.problem.raw_input}")
            print(f"  Reading Order: {problem.reading_order}")
    
    print(f"\n✓ Total problems detected: {total_problems}")
    
    # ========================================================================
    # STAGE 5: Instruction → Problem Relationships
    # ========================================================================
    print_section("STAGE 5: Instruction → Problem Relationships")
    
    for i, section in enumerate(exercise.sections):
        print(f"\n--- Section {i} ---")
        if section.instruction:
            print(f"Instruction: {section.instruction.text}")
            print(f"Linked Problems:")
            for j, problem in enumerate(section.problems):
                has_context = problem.instruction_context is not None
                context_match = (
                    problem.instruction_context == section.instruction
                    if problem.instruction_context
                    else False
                )
                print(f"  {problem.label}: has_context={has_context}, matches={context_match}")
        else:
            print("⚠️  No instruction to link")
    
    # ========================================================================
    # STAGE 6: Classification for Each Problem
    # ========================================================================
    print_section("STAGE 6: Classification for Each Problem")
    
    classifications = []
    for i, section in enumerate(exercise.sections):
        print(f"\n--- Section {i} ---")
        for j, problem in enumerate(section.problems):
            expr = problem.problem.expression or problem.problem.raw_input
            print(f"\nProblem {problem.label}: {expr}")
            
            try:
                # Parse the expression
                parsed = parse_math_text(expr)
                print(f"  ✓ Parsed: {parsed.sympy_expr}")
                
                # Classify (basic classifier for now)
                problem_type = classify_problem(parsed)
                print(f"  ✓ Type: {problem_type}")
                print(f"  ✓ Variables: {parsed.symbols}")
                
                classifications.append({
                    "label": problem.label,
                    "expression": expr,
                    "parsed": str(parsed.sympy_expr),
                    "problem_type": problem_type,
                    "parsed_obj": parsed,
                })
                
            except Exception as e:
                print(f"  ❌ Classification failed: {e}")
                classifications.append({
                    "label": problem.label,
                    "expression": expr,
                    "error": str(e),
                })
    
    # ========================================================================
    # STAGE 7: Solver Input
    # ========================================================================
    print_section("STAGE 7: Solver Input")
    
    for item in classifications:
        if "error" in item:
            print(f"\n{item['label']}: SKIPPED (parse error)")
            continue
        
        print(f"\n{item['label']}: {item['expression']}")
        print(f"  Parsed: {item['parsed']}")
        print(f"  Type: {item['problem_type']}")
        print(f"  Ready for solver: ✓")
    
    # ========================================================================
    # STAGE 8: Final Solutions
    # ========================================================================
    print_section("STAGE 8: Final Solutions")
    
    for item in classifications:
        if "error" in item:
            print(f"\n{item['label']}: SKIPPED")
            continue
        
        print(f"\n{item['label']}: {item['expression']}")
        
        try:
            solution = solve(item["parsed_obj"], item["problem_type"])
            
            print(f"  ✓ Answer: {solution.answer}")
            print(f"  ✓ Variable: {solution.variable}")
            print(f"  ✓ Verified: {solution.is_verified}")
            print(f"  ✓ Steps: {len(solution.steps)} steps")
            
            # Show first and last step
            if solution.steps:
                first = solution.steps[0]
                print(f"\n  First step:")
                print(f"    KM: {first.description_km}")
                print(f"    EN: {first.description_en}")
                
                if len(solution.steps) > 1:
                    last = solution.steps[-1]
                    print(f"\n  Last step:")
                    print(f"    KM: {last.description_km}")
                    print(f"    EN: {last.description_en}")
                    
        except Exception as e:
            print(f"  ❌ Solving failed: {e}")
            import traceback
            traceback.print_exc()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("SUMMARY")
    
    print(f"\n✓ OCR: {type(vision_engine).__name__}")
    print(f"✓ Sections: {len(exercise.sections)}")
    print(f"✓ Problems detected: {total_problems}")
    print(f"✓ Successfully parsed: {sum(1 for c in classifications if 'error' not in c)}")
    print(f"✓ Parse errors: {sum(1 for c in classifications if 'error' in c)}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
