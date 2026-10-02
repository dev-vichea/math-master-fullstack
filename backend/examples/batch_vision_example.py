"""
Example demonstrating batch vision processing for multi-exercise images.

This shows how the new process_image_batch() method works with images containing
multiple sub-problems like:
    Exercise 1:
    a) 2x + 3 = 7
    b) 3x - 5 = 10
    c) x/2 + 4 = 9
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.problem_builder import ProblemBuilder
from app.models.problem import MultiProblemSet, MathProblem, ProblemSource


def simulate_multi_exercise_ocr() -> MultiProblemSet:
    """
    Simulate OCR result from an image with multiple sub-exercises.
    
    In real usage, this would come from vision_service.process_image_batch()
    which calls OCR -> exercise_parser -> problem_builder for each sub-problem.
    """
    
    # Simulate parsed sub-exercises from OCR
    sub_exercises = [
        ("a", "2x + 3 = 7", "solve"),
        ("b", "3x - 5 = 10", "solve"),
        ("c", "x/2 + 4 = 9", "solve"),
    ]
    
    # Create MultiProblemSet container
    problem_set = MultiProblemSet(
        exercise_title="លំហាត់ទី ១",  # Exercise 1 in Khmer
        instruction="ដោះស្រាយសមីការ",  # Solve the equations in Khmer
        source_metadata={
            "ocr_confidence": 0.92,
            "ocr_provider": "SimulatedOCR",
            "image_source": "textbook_page_42.jpg",
        },
    )
    
    # Build each sub-problem using ProblemBuilder
    builder = ProblemBuilder()
    
    for label, expression, intent in sub_exercises:
        try:
            problem = builder.build_from_text(
                text=expression,
                language="en",  # English expressions
                source=ProblemSource.OCR,
            )
            
            # Add sub-exercise metadata
            problem.ocr_confidence = 0.92
            problem.metadata.update({
                "sub_exercise_label": label,
                "detected_intent": intent,
            })
            
            problem_set.add_problem(problem)
            
        except Exception as e:
            print(f"Error processing sub-exercise {label}: {e}")
            # In real code, we'd still add an error placeholder
    
    return problem_set


def main():
    """Demonstrate batch processing workflow."""
    
    print("=" * 70)
    print("BATCH VISION PROCESSING EXAMPLE")
    print("=" * 70)
    
    # Step 1: Simulate OCR + parsing of multi-exercise image
    problem_set = simulate_multi_exercise_ocr()
    
    # Step 2: Display structured results
    print(f"\n📋 Exercise Title: {problem_set.exercise_title}")
    print(f"📝 Instruction: {problem_set.instruction}")
    print(f"🔢 Total Problems: {problem_set.get_problem_count()}")
    print(f"🎯 Average Confidence: {problem_set.get_average_confidence():.2%}")
    
    # Step 3: Display each problem's details
    print("\n" + "=" * 70)
    print("DETECTED PROBLEMS:")
    print("=" * 70)
    
    for i, problem in enumerate(problem_set.problems, 1):
        label = problem.metadata.get("sub_exercise_label", i)
        print(f"\n📌 Sub-exercise {label}:")
        print(f"   Raw Input: {problem.raw_input}")
        print(f"   Normalized Expression: {problem.expression or 'N/A'}")
        print(f"   Problem Type: {problem.problem_type or 'Not classified'}")
        print(f"   Overall Confidence: {problem.overall_confidence:.2%}")
        
        if problem.characteristics:
            char = problem.characteristics
            print(f"   Characteristics:")
            print(f"      - Has equation: {char.has_equation}")
            print(f"      - Has fractions: {char.has_fractions}")
            print(f"      - Variable count: {char.variable_count}")
            print(f"      - Max degree: {char.max_polynomial_degree}")
        
        if problem.warnings:
            print(f"   ⚠️  Warnings: {', '.join(problem.warnings)}")
    
    # Step 4: Convert to API response format
    print("\n" + "=" * 70)
    print("API RESPONSE FORMAT:")
    print("=" * 70)
    
    response_dict = problem_set.to_dict()
    
    import json
    print(json.dumps(response_dict, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("Each problem can now be:")
    print("1. Reviewed by user for OCR accuracy (via POST /math/review endpoint)")
    print("2. Solved individually (via POST /math/solve with problem.expression)")
    print("3. Verified after solving (via built-in verification engine)")
    print("=" * 70)


if __name__ == "__main__":
    main()
