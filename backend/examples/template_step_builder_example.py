"""
Example showing how to use StepBuilder with template-based explanations.

This demonstrates the integration between operation metadata tracking and
the bilingual explanation template system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.engine.operations import OperationType, StepBuilder, TransformationType
from app.models.schemas import SolutionStep


def solve_linear_equation_with_templates():
    """
    Solve 2x + 5 = 15 using template-based step generation.
    
    This shows the NEW way of generating steps - using templates instead
    of manual Khmer/English strings.
    """
    print("=" * 70)
    print("SOLVING: 2x + 5 = 15")
    print("Using template-based step generation")
    print("=" * 70)
    
    builder = StepBuilder()
    steps_data = []
    
    # Step 1: Initial equation
    steps_data.append(
        builder.create_initial_step(expression="2x + 5 = 15")
    )
    
    # Step 2: Subtract 5 from both sides (using templates!)
    steps_data.append(
        builder.create_step_from_template(
            operation=OperationType.SUBTRACT,
            expression="2x = 10",
            equation_side="both",
            value="5",
            side="both",  # Template variable
        )
    )
    
    # Step 3: Divide both sides by 2 (using templates!)
    steps_data.append(
        builder.create_step_from_template(
            operation=OperationType.DIVIDE,
            expression="x = 5",
            equation_side="both",
            value="2",
            side="both",
        )
    )
    
    # Step 4: Final answer (using templates!)
    steps_data.append(
        builder.create_step_from_template(
            operation=OperationType.FINAL_ANSWER,
            expression="x = 5",
            answer="x = 5",
        )
    )
    
    # Convert to SolutionStep objects
    steps = [SolutionStep(**data) for data in steps_data]
    
    # Display results
    for step in steps:
        print(f"\nStep {step.order}:")
        print(f"  KM: {step.description_km}")
        print(f"  EN: {step.description_en}")
        print(f"  Expression: {step.expression}")
        print(f"  Operation: {step.operation}")
        if step.operands:
            print(f"  Operands: {', '.join(step.operands)}")
        if step.equation_side:
            print(f"  Side: {step.equation_side}")
    
    return steps


def solve_quadratic_with_templates():
    """
    Demonstrate quadratic solving steps with templates.
    """
    print("\n" + "=" * 70)
    print("SOLVING: x² - 5x + 6 = 0")
    print("Using template-based step generation")
    print("=" * 70)
    
    builder = StepBuilder()
    steps_data = []
    
    # Initial equation
    steps_data.append(
        builder.create_initial_step(expression="x² - 5x + 6 = 0")
    )
    
    # Factor the quadratic
    steps_data.append(
        builder.create_step_from_template(
            operation=OperationType.FACTOR,
            expression="(x - 2)(x - 3) = 0",
            transformation=TransformationType.FACTORIZATION,
            from_expr="x² - 5x + 6",
        )
    )
    
    # Final answers
    steps_data.append(
        builder.create_step_from_template(
            operation=OperationType.FINAL_ANSWER,
            expression="x = 2 or x = 3",
            answer="x = 2, 3",
        )
    )
    
    # Convert and display
    steps = [SolutionStep(**data) for data in steps_data]
    
    for step in steps:
        print(f"\nStep {step.order}:")
        print(f"  KM: {step.description_km}")
        print(f"  EN: {step.description_en}")
        print(f"  Expression: {step.expression}")
        print(f"  Operation: {step.operation}")
        if step.transformation:
            print(f"  Transformation: {step.transformation}")


def demonstrate_various_operations():
    """Show various operation types with templates."""
    print("\n" + "=" * 70)
    print("VARIOUS OPERATIONS WITH TEMPLATES")
    print("=" * 70)
    
    builder = StepBuilder()
    
    operations_demo = [
        {
            "op": OperationType.MOVE_TERM,
            "expr": "5x = 3x + 10",
            "kwargs": {"variable": "x", "move_all_left": True},
        },
        {
            "op": OperationType.COMBINE_LIKE_TERMS,
            "expr": "5x = 10",
            "kwargs": {"from_expr": "5x - 3x", "to_expr": "2x", "variant": "simplify"},
        },
        {
            "op": OperationType.MULTIPLY,
            "expr": "x = 10",
            "kwargs": {"value": "1/2", "side": "both"},
        },
        {
            "op": OperationType.ISOLATE_VARIABLE,
            "expr": "x = 10",
            "kwargs": {"variable": "x"},
        },
    ]
    
    for demo in operations_demo:
        step_data = builder.create_step_from_template(
            operation=demo["op"],
            expression=demo["expr"],
            **demo["kwargs"],
        )
        step = SolutionStep(**step_data)
        
        print(f"\n{demo['op'].value}:")
        print(f"  KM: {step.description_km}")
        print(f"  EN: {step.description_en}")
        print(f"  Expression: {step.expression}")


def compare_old_vs_new_approach():
    """Compare manual strings vs template-based approach."""
    print("\n" + "=" * 70)
    print("OLD VS NEW APPROACH COMPARISON")
    print("=" * 70)
    
    print("\n📝 OLD APPROACH (Manual strings):")
    print("```python")
    print('step = builder.create_step(')
    print('    description_km="ដក ៥ ពីភាគីទាំងពីរ",')
    print('    description_en="Subtract 5 from both sides",')
    print('    expression="2x = 10",')
    print('    operation=OperationType.SUBTRACT,')
    print('    operands=["5"],')
    print('    equation_side="both",')
    print(')')
    print("```")
    
    print("\n✨ NEW APPROACH (Template-based):")
    print("```python")
    print('step = builder.create_step_from_template(')
    print('    operation=OperationType.SUBTRACT,')
    print('    expression="2x = 10",')
    print('    value="5",')
    print('    side="both",')
    print(')')
    print("```")
    
    print("\n✅ Benefits:")
    print("  - No manual Khmer/English duplication")
    print("  - Consistent phrasing across all problems")
    print("  - Easy to update all explanations at once")
    print("  - Number formatting handled automatically")
    print("  - Guaranteed grammatically correct")
    print("  - 100% deterministic (no LLM)")


def main():
    """Run all demonstrations."""
    print("\n" + "🔷" * 35)
    print("STEPBUILDER + TEMPLATE INTEGRATION DEMONSTRATION")
    print("🔷" * 35)
    
    solve_linear_equation_with_templates()
    solve_quadratic_with_templates()
    demonstrate_various_operations()
    compare_old_vs_new_approach()
    
    print("\n" + "=" * 70)
    print("MIGRATION PATH:")
    print("=" * 70)
    print("1. Current solvers (linear.py, quadratic.py) work as-is")
    print("2. Gradually migrate to create_step_from_template()")
    print("3. Remove manual Khmer/English strings over time")
    print("4. All explanations become template-driven")
    print("=" * 70)


if __name__ == "__main__":
    main()
