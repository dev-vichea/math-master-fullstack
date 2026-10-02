"""
Problem Classifier - Classify mathematical problems by type.

Supported problem types:
- Linear equations
- Quadratic equations
- Polynomial equations
- Systems of equations
- Inequalities
- Calculus (limits, derivatives, integrals)
- Trigonometric equations
- Rational and radical equations
- Arithmetic expressions
"""

from app.classifier.problem_classifier.classifier import classify_problem
from app.classifier.problem_classifier.classifier_enhanced import (
    ProblemClassifier,
    classify_with_characteristics,
)
from app.classifier.problem_classifier.intent_classifier import (
    MathIntent,
    RuleBasedIntentClassifier,
)

__all__ = [
    "classify_problem",
    "ProblemClassifier",
    "classify_with_characteristics",
    "MathIntent",
    "RuleBasedIntentClassifier",
]
