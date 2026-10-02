"""
Verification Layer - Solution verification with problem-type-specific strategies.

Never trusts solutions without verification. Each problem type has specialized
verification logic:
- Equations: Substitution verification
- Inequalities: Trust SymPy with confidence scoring
- Expressions: Direct evaluation
- Systems: Substitution (TODO: full implementation)
- Calculus: Trust SymPy with lower confidence

Refactored from app/core/verification/ for better organization.
"""

from app.verification.verifier import (
    SolutionVerifier,
    VerificationResult,
    get_verifier,
    verify_solution,
)

__all__ = [
    "SolutionVerifier",
    "VerificationResult",
    "verify_solution",
    "get_verifier",
]
