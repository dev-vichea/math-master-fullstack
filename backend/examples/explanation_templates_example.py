"""
Example demonstrating the template-based explanation generator.

This shows how to generate bilingual (Khmer/English) mathematical explanations
without using any LLM APIs.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.engine.operations import OperationType
from app.core.localization.templates import ExplanationGenerator, generate_bilingual_step


def demonstrate_basic_operations():
    """Show basic arithmetic operation explanations."""
    print("=" * 70)
    print("BASIC ARITHMETIC OPERATIONS")
    print("=" * 70)
    
    gen = ExplanationGenerator()
    
    operations = [
        (OperationType.ADD, {"value": "5", "side": "both"}),
        (OperationType.SUBTRACT, {"value": "3", "side": "both"}),
        (OperationType.MULTIPLY, {"value": "2", "side": "both"}),
        (OperationType.DIVIDE, {"value": "4", "side": "both"}),
    ]
    
    for op, kwargs in operations:
        km = gen.generate_step_description(op, "km", **kwargs)
        en = gen.generate_step_description(op, "en", **kwargs)
        print(f"\n{op.value}:")
        print(f"  KM: {km}")
        print(f"  EN: {en}")


def demonstrate_algebraic_operations():
    """Show algebraic operation explanations."""
    print("\n" + "=" * 70)
    print("ALGEBRAIC OPERATIONS")
    print("=" * 70)
    
    gen = ExplanationGenerator()
    
    # Move term
    print("\n1. Move term:")
    km = gen.generate_step_description(
        OperationType.MOVE_TERM,
        "km",
        variable="x",
        move_all_left=True,
    )
    en = gen.generate_step_description(
        OperationType.MOVE_TERM,
        "en",
        variable="x",
        move_all_left=True,
    )
    print(f"  KM: {km}")
    print(f"  EN: {en}")
    
    # Combine like terms
    print("\n2. Combine like terms:")
    km = gen.generate_step_description(
        OperationType.COMBINE_LIKE_TERMS,
        "km",
        from_expr="3x + 2x",
        to_expr="5x",
        variant="simplify",
    )
    en = gen.generate_step_description(
        OperationType.COMBINE_LIKE_TERMS,
        "en",
        from_expr="3x + 2x",
        to_expr="5x",
        variant="simplify",
    )
    print(f"  KM: {km}")
    print(f"  EN: {en}")
    
    # Isolate variable
    print("\n3. Isolate variable:")
    km = gen.generate_step_description(
        OperationType.ISOLATE_VARIABLE,
        "km",
        variable="x",
    )
    en = gen.generate_step_description(
        OperationType.ISOLATE_VARIABLE,
        "en",
        variable="x",
    )
    print(f"  KM: {km}")
    print(f"  EN: {en}")


def demonstrate_solving_linear_equation():
    """Show a complete linear equation solution with explanations."""
    print("\n" + "=" * 70)
    print("COMPLETE LINEAR EQUATION SOLUTION: 2x + 5 = 15")
    print("=" * 70)
    
    # Step 1: Subtract 5 from both sides
    step1 = generate_bilingual_step(
        OperationType.SUBTRACT,
        "2x = 10",
        value="5",
        side="both",
    )
    print(f"\nStep 1:")
    print(f"  KM: {step1['description_km']}")
    print(f"  EN: {step1['description_en']}")
    print(f"  Result: {step1['expression']}")
    
    # Step 2: Divide both sides by 2
    step2 = generate_bilingual_step(
        OperationType.DIVIDE,
        "x = 5",
        value="2",
        side="both",
    )
    print(f"\nStep 2:")
    print(f"  KM: {step2['description_km']}")
    print(f"  EN: {step2['description_en']}")
    print(f"  Result: {step2['expression']}")
    
    # Step 3: Final answer
    step3 = generate_bilingual_step(
        OperationType.FINAL_ANSWER,
        "x = 5",
        answer="x = 5",
    )
    print(f"\nStep 3:")
    print(f"  KM: {step3['description_km']}")
    print(f"  EN: {step3['description_en']}")
    print(f"  Result: {step3['expression']}")


def demonstrate_quadratic_operations():
    """Show quadratic-specific operations."""
    print("\n" + "=" * 70)
    print("QUADRATIC EQUATION OPERATIONS")
    print("=" * 70)
    
    gen = ExplanationGenerator()
    
    # Quadratic formula
    print("\n1. Quadratic formula:")
    km = gen.generate_step_description(
        OperationType.APPLY_QUADRATIC_FORMULA,
        "km",
        variant="full",
    )
    en = gen.generate_step_description(
        OperationType.APPLY_QUADRATIC_FORMULA,
        "en",
        variant="full",
    )
    print(f"  KM: {km}")
    print(f"  EN: {en}")
    
    # Complete the square
    print("\n2. Complete the square:")
    km = gen.generate_step_description(OperationType.COMPLETE_SQUARE, "km")
    en = gen.generate_step_description(OperationType.COMPLETE_SQUARE, "en")
    print(f"  KM: {km}")
    print(f"  EN: {en}")
    
    # Factoring
    print("\n3. Factor:")
    km = gen.generate_step_description(
        OperationType.FACTOR,
        "km",
        from_expr="x² + 5x + 6",
    )
    en = gen.generate_step_description(
        OperationType.FACTOR,
        "en",
        from_expr="x² + 5x + 6",
    )
    print(f"  KM: {km}")
    print(f"  EN: {en}")


def demonstrate_number_formatting():
    """Show number formatting in Khmer."""
    print("\n" + "=" * 70)
    print("KHMER NUMBER FORMATTING")
    print("=" * 70)
    
    gen = ExplanationGenerator()
    
    test_numbers = [
        ("5", "Integer"),
        ("1/2", "Fraction"),
        ("0.5", "Decimal"),
        ("-3", "Negative"),
        ("2.718", "Multi-digit decimal"),
    ]
    
    for num, desc in test_numbers:
        km = gen.formatter.format_km(num)
        en = gen.formatter.format_en(num)
        print(f"\n{desc} ({num}):")
        print(f"  Khmer: {km}")
        print(f"  English: {en}")


def demonstrate_operation_summaries():
    """Show operation summaries for documentation."""
    print("\n" + "=" * 70)
    print("OPERATION SUMMARIES")
    print("=" * 70)
    
    gen = ExplanationGenerator()
    
    operations = [
        OperationType.ADD,
        OperationType.SUBTRACT,
        OperationType.MULTIPLY,
        OperationType.DIVIDE,
        OperationType.ISOLATE_VARIABLE,
        OperationType.SIMPLIFY,
        OperationType.FACTOR,
        OperationType.APPLY_QUADRATIC_FORMULA,
    ]
    
    print("\n{:<25} {:<35} {:<35}".format("Operation", "Khmer Summary", "English Summary"))
    print("-" * 95)
    
    for op in operations:
        km = gen.generate_operation_summary(op, "km")
        en = gen.generate_operation_summary(op, "en")
        print(f"{op.value:<25} {km:<35} {en:<35}")


def main():
    """Run all demonstrations."""
    print("\n" + "🔷" * 35)
    print("TEMPLATE-BASED EXPLANATION GENERATOR DEMONSTRATION")
    print("No LLM APIs - 100% Deterministic Templates")
    print("🔷" * 35)
    
    demonstrate_basic_operations()
    demonstrate_algebraic_operations()
    demonstrate_solving_linear_equation()
    demonstrate_quadratic_operations()
    demonstrate_number_formatting()
    demonstrate_operation_summaries()
    
    print("\n" + "=" * 70)
    print("BENEFITS OF TEMPLATE-BASED APPROACH:")
    print("=" * 70)
    print("✅ No LLM API costs or latency")
    print("✅ 100% deterministic and reproducible")
    print("✅ Guaranteed grammatically correct output")
    print("✅ Easy to maintain and extend")
    print("✅ Supports offline operation")
    print("✅ No hallucination or incorrect math explanations")
    print("✅ Consistent terminology across all problems")
    print("=" * 70)


if __name__ == "__main__":
    main()
