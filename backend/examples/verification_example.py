"""
Example demonstrating the enhanced verification system.

Shows how different problem types are verified with specialized strategies.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import sympy
from sympy import Eq, symbols

from app.verification.verifier import SolutionVerifier, VerificationResult


def demonstrate_equation_verification():
    """Show equation verification with substitution."""
    print("=" * 70)
    print("EQUATION VERIFICATION")
    print("=" * 70)
    
    verifier = SolutionVerifier()
    x = symbols("x")
    
    # Test 1: Correct solution
    eq1 = Eq(2*x + 5, 15)
    result1 = verifier.verify(eq1, "5", x, "linear_equation")
    
    print("\nTest 1: 2x + 5 = 15, solution x = 5")
    print(f"  Verified: {result1.is_verified}")
    print(f"  Confidence: {result1.confidence:.2%}")
    print(f"  Method: {result1.method}")
    print(f"  Details: {result1.details}")
    
    # Test 2: Incorrect solution
    result2 = verifier.verify(eq1, "3", x, "linear_equation")
    
    print("\nTest 2: 2x + 5 = 15, solution x = 3 (WRONG)")
    print(f"  Verified: {result2.is_verified}")
    print(f"  Confidence: {result2.confidence:.2%}")
    print(f"  Method: {result2.method}")
    if result2.warnings:
        print(f"  Warnings: {result2.warnings}")
    
    # Test 3: Quadratic with multiple solutions
    eq3 = Eq(x**2 - 5*x + 6, 0)
    result3 = verifier.verify(eq3, "2, 3", x, "quadratic_equation")
    
    print("\nTest 3: x² - 5x + 6 = 0, solutions x = 2, 3")
    print(f"  Verified: {result3.is_verified}")
    print(f"  Confidence: {result3.confidence:.2%}")
    print(f"  Method: {result3.method}")
    print(f"  Verified solutions: {result3.details.get('verified_solutions', [])}")
    
    # Test 4: Partial verification (one wrong solution)
    result4 = verifier.verify(eq3, "2, 5", x, "quadratic_equation")
    
    print("\nTest 4: x² - 5x + 6 = 0, solutions x = 2, 5 (one wrong)")
    print(f"  Verified: {result4.is_verified}")
    print(f"  Confidence: {result4.confidence:.2%}")
    print(f"  Verified solutions: {result4.details.get('verified_solutions', [])}")
    print(f"  Failed solutions: {result4.details.get('failed_solutions', [])}")
    if result4.warnings:
        print(f"  Warnings: {result4.warnings}")


def demonstrate_expression_verification():
    """Show expression evaluation verification."""
    print("\n" + "=" * 70)
    print("EXPRESSION EVALUATION VERIFICATION")
    print("=" * 70)
    
    verifier = SolutionVerifier()
    
    # Test 1: Simple arithmetic
    expr1 = sympy.sympify("1/2 + 3/4")
    result1 = verifier.verify(expr1, "5/4", None, "arithmetic_expression")
    
    print("\nTest 1: 1/2 + 3/4 = 5/4")
    print(f"  Verified: {result1.is_verified}")
    print(f"  Confidence: {result1.confidence:.2%}")
    print(f"  Computed: {result1.details.get('computed')}")
    print(f"  Expected: {result1.details.get('expected')}")
    
    # Test 2: Wrong result
    result2 = verifier.verify(expr1, "1", None, "arithmetic_expression")
    
    print("\nTest 2: 1/2 + 3/4 = 1 (WRONG)")
    print(f"  Verified: {result2.is_verified}")
    print(f"  Confidence: {result2.confidence:.2%}")
    print(f"  Computed: {result2.details.get('computed')}")
    print(f"  Expected: {result2.details.get('expected')}")


def demonstrate_inequality_verification():
    """Show inequality verification."""
    print("\n" + "=" * 70)
    print("INEQUALITY VERIFICATION")
    print("=" * 70)
    
    verifier = SolutionVerifier()
    x = symbols("x")
    
    # Inequality verification is complex - current implementation trusts SymPy
    ineq = sympy.sympify("2*x + 3 > 7")
    result = verifier.verify(ineq, "x > 2", x, "inequality")
    
    print("\nTest: 2x + 3 > 7, solution x > 2")
    print(f"  Verified: {result.is_verified}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Method: {result.method}")
    print(f"  Note: {result.details.get('note')}")
    if result.warnings:
        print(f"  Warnings: {result.warnings}")


def demonstrate_verification_result_dict():
    """Show VerificationResult conversion to dict for API responses."""
    print("\n" + "=" * 70)
    print("VERIFICATION RESULT FOR API RESPONSES")
    print("=" * 70)
    
    verifier = SolutionVerifier()
    x = symbols("x")
    eq = Eq(2*x + 5, 15)
    result = verifier.verify(eq, "5", x, "linear_equation")
    
    # Convert to dict for API
    result_dict = result.to_dict()
    
    print("\nVerificationResult.to_dict():")
    import json
    print(json.dumps(result_dict, indent=2))


def demonstrate_confidence_scoring():
    """Show how confidence scoring works."""
    print("\n" + "=" * 70)
    print("CONFIDENCE SCORING")
    print("=" * 70)
    
    verifier = SolutionVerifier()
    x = symbols("x")
    
    scenarios = [
        ("Correct single solution", Eq(2*x + 5, 15), "5", "linear_equation"),
        ("Correct multiple solutions", Eq(x**2 - 5*x + 6, 0), "2, 3", "quadratic_equation"),
        ("One correct, one wrong", Eq(x**2 - 5*x + 6, 0), "2, 5", "quadratic_equation"),
        ("All wrong solutions", Eq(x**2 - 5*x + 6, 0), "1, 4", "quadratic_equation"),
        ("Inequality (trust SymPy)", sympy.sympify("x > 2"), "x > 2", "inequality"),
    ]
    
    print("\n{:<30} {:<12} {:<12}".format("Scenario", "Verified", "Confidence"))
    print("-" * 54)
    
    for desc, eq, sol, ptype in scenarios:
        result = verifier.verify(eq, sol, x, ptype)
        status = "✓ Yes" if result.is_verified else "✗ No"
        print(f"{desc:<30} {status:<12} {result.confidence:>10.0%}")


def demonstrate_integration_with_solve_result():
    """Show how to integrate VerificationResult with existing SolveResult."""
    print("\n" + "=" * 70)
    print("INTEGRATION WITH SOLVERESULT")
    print("=" * 70)
    
    print("\nOLD WAY (boolean only):")
    print("```python")
    print("is_verified = verify_solution(eq, symbol, solution)")
    print("# Result: True or False")
    print("```")
    
    print("\nNEW WAY (rich verification result):")
    print("```python")
    print("verification = verify_solution(eq, solution, symbol, problem_type)")
    print("# Result: VerificationResult with:")
    print("#   - is_verified: bool")
    print("#   - confidence: float (0.0-1.0)")
    print("#   - method: str (which verification was used)")
    print("#   - details: dict (what was checked)")
    print("#   - warnings: list[str]")
    print("```")
    
    print("\nBenefits:")
    print("  ✓ Know WHY verification succeeded/failed")
    print("  ✓ Confidence scoring for partial verification")
    print("  ✓ Problem-type-specific verification strategies")
    print("  ✓ Detailed debugging information")
    print("  ✓ Warnings for edge cases")


def main():
    """Run all demonstrations."""
    print("\n" + "🔷" * 35)
    print("ENHANCED VERIFICATION SYSTEM DEMONSTRATION")
    print("Problem-Type-Specific Verification Strategies")
    print("🔷" * 35)
    
    demonstrate_equation_verification()
    demonstrate_expression_verification()
    demonstrate_inequality_verification()
    demonstrate_verification_result_dict()
    demonstrate_confidence_scoring()
    demonstrate_integration_with_solve_result()
    
    print("\n" + "=" * 70)
    print("KEY IMPROVEMENTS:")
    print("=" * 70)
    print("✅ Problem-type-specific verification strategies")
    print("✅ Confidence scoring (0.0 to 1.0)")
    print("✅ Detailed verification results with explanations")
    print("✅ Warning system for edge cases")
    print("✅ Backward compatible with existing code")
    print("✅ Works with MathProblem representation")
    print("=" * 70)


if __name__ == "__main__":
    main()
