"""
Context-aware classifier that uses instruction context to improve classification.

This module enhances the standard problem classifier by incorporating instruction
context (e.g., "Factor the following" → factorization problem) to provide more
accurate classification, especially for ambiguous expressions.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.classifier.problem_classifier.classifier_enhanced import ProblemClassifier
from app.models.document import Instruction, InstructionType
from app.models.problem import ProblemCharacteristics
from app.parser.math_parser.expression_parser import ParsedMath


@dataclass
class ContextualClassification:
    """Result of context-aware classification."""

    problem_type: str  # e.g., "polynomial_factorization", "linear_equation"
    characteristics: ProblemCharacteristics
    confidence: float  # 0.0 to 1.0
    used_instruction_context: bool  # Whether instruction context influenced result
    reasoning: str  # Human-readable explanation


class ContextAwareClassifier:
    """
    Classifier that uses instruction context to improve accuracy.

    When an instruction is provided (e.g., "Factor the following polynomials"),
    it guides the classification process to prioritize problem types that match
    the instruction's intent.

    Example:
        Expression: "x² - 4"
        Without context: Could be "evaluate", "solve", or "factor"
        With context "Factor": Confident classification as "polynomial_factorization"
    """

    # Mapping from instruction types to expected problem types
    INSTRUCTION_TO_PROBLEM_TYPE = {
        InstructionType.FACTOR: [
            "polynomial_factorization",
            "expression_factorization",
        ],
        InstructionType.SOLVE: [
            "linear_equation",
            "quadratic_equation",
            "polynomial_equation",
            "system_of_equations",
            "inequality",
        ],
        InstructionType.SIMPLIFY: [
            "expression_simplification",
            "fraction_simplification",
            "radical_simplification",
        ],
        InstructionType.EXPAND: [
            "polynomial_expansion",
            "expression_expansion",
        ],
        InstructionType.EVALUATE: [
            "arithmetic_evaluation",
            "expression_evaluation",
        ],
        InstructionType.FIND: [
            "linear_equation",
            "quadratic_equation",
            "polynomial_equation",
        ],
        InstructionType.COMPARE: [
            "comparison",
            "inequality",
        ],
        InstructionType.DERIVATIVE: [
            "calculus_derivative",
        ],
        InstructionType.INTEGRAL: [
            "calculus_integral",
        ],
        InstructionType.CONVERGENCE: [
            "sequence_convergence",
            "sequence",
            "sequence_limit",
        ],
        InstructionType.SEQUENCE: [
            "sequence",
            "sequence_limit",
            "sequence_recurrence",
            "sequence_convergence",
        ],
    }

    def __init__(self):

        """Initialize context-aware classifier."""
        self.base_classifier = ProblemClassifier()

    def classify(
        self,
        parsed: ParsedMath,
        instruction: Instruction | None = None,
    ) -> ContextualClassification:
        """
        Classify a problem using instruction context if available.

        Args:
            parsed: ParsedMath object
            instruction: Optional instruction context

        Returns:
            ContextualClassification with problem type and reasoning
        """
        # First, get base classification without context
        base_type, characteristics = self.base_classifier.classify(parsed)

        # If no instruction context, return base classification
        if instruction is None or instruction.instruction_type == InstructionType.UNKNOWN:
            return ContextualClassification(
                problem_type=base_type,
                characteristics=characteristics,
                confidence=0.7,  # Lower confidence without context
                used_instruction_context=False,
                reasoning=f"Classified as '{base_type}' based on expression analysis alone.",
            )

        # Get expected problem types from instruction
        expected_types = self.INSTRUCTION_TO_PROBLEM_TYPE.get(
            instruction.instruction_type, []
        )

        # Check if base classification matches instruction
        if base_type in expected_types:
            # Perfect match - high confidence
            return ContextualClassification(
                problem_type=base_type,
                characteristics=characteristics,
                confidence=0.95,
                used_instruction_context=True,
                reasoning=f"Classified as '{base_type}' - matches instruction '{instruction.instruction_type.value}' with high confidence.",
            )

        # If no match, override with instruction-guided classification
        refined_type = self._refine_with_instruction(
            base_type, instruction.instruction_type, characteristics
        )

        confidence = 0.85 if refined_type != base_type else 0.75

        return ContextualClassification(
            problem_type=refined_type,
            characteristics=characteristics,
            confidence=confidence,
            used_instruction_context=True,
            reasoning=f"Refined from '{base_type}' to '{refined_type}' based on instruction '{instruction.instruction_type.value}'.",
        )

    def _refine_with_instruction(
        self,
        base_type: str,
        instruction_type: InstructionType,
        characteristics: ProblemCharacteristics,
    ) -> str:
        """
        Refine classification based on instruction context.

        Args:
            base_type: Base classification from standard classifier
            instruction_type: Type of instruction
            characteristics: Problem characteristics

        Returns:
            Refined problem type
        """
        # Factor instruction: prioritize factorization
        if instruction_type == InstructionType.FACTOR:
            if characteristics.has_exponents or characteristics.max_polynomial_degree >= 2:
                return "polynomial_factorization"
            return "expression_factorization"

        # Solve instruction: prioritize equation solving
        if instruction_type == InstructionType.SOLVE:
            if characteristics.has_equation:
                if characteristics.has_system:
                    return "system_of_equations"
                elif characteristics.max_polynomial_degree == 1:
                    return "linear_equation"
                elif characteristics.max_polynomial_degree == 2:
                    return "quadratic_equation"
                elif characteristics.max_polynomial_degree >= 3:
                    return "polynomial_equation"
            elif characteristics.has_inequality:
                return "inequality"
            # Expression without equation - treat as equation set to 0
            return "equation_solving"

        # Simplify instruction: prioritize simplification
        if instruction_type == InstructionType.SIMPLIFY:
            if characteristics.has_fractions:
                return "fraction_simplification"
            elif characteristics.has_radicals:
                return "radical_simplification"
            return "expression_simplification"

        # Expand instruction: prioritize expansion
        if instruction_type == InstructionType.EXPAND:
            if characteristics.max_polynomial_degree >= 2:
                return "polynomial_expansion"
            return "expression_expansion"

        # Evaluate instruction: treat as evaluation
        if instruction_type == InstructionType.EVALUATE:
            return "expression_evaluation"

        # Find instruction: similar to solve
        if instruction_type == InstructionType.FIND:
            if characteristics.max_polynomial_degree == 1:
                return "linear_equation"
            elif characteristics.max_polynomial_degree == 2:
                return "quadratic_equation"
            return "polynomial_equation"

        # Compare instruction: comparison problem
        if instruction_type == InstructionType.COMPARE:
            if characteristics.has_inequality:
                return "inequality"
            return "comparison"

        # Graph instruction: graphing problem
        if instruction_type == InstructionType.GRAPH:
            return "graphing"

        # Prove instruction: proof/verification
        if instruction_type == InstructionType.PROVE:
            return "proof_verification"

        # Derivative instruction: calculus derivative
        if instruction_type == InstructionType.DERIVATIVE:
            return "calculus_derivative"

        # Default: return base type
        return base_type

    def classify_batch(
        self,
        parsed_list: list[ParsedMath],
        instruction: Instruction | None = None,
    ) -> list[ContextualClassification]:
        """
        Classify multiple problems with shared instruction context.

        Args:
            parsed_list: List of ParsedMath objects
            instruction: Optional shared instruction context

        Returns:
            List of ContextualClassification results
        """
        return [self.classify(parsed, instruction) for parsed in parsed_list]

    def get_expected_types(
        self, instruction_type: InstructionType
    ) -> list[str]:
        """
        Get expected problem types for an instruction type.

        Args:
            instruction_type: Type of instruction

        Returns:
            List of expected problem types
        """
        return self.INSTRUCTION_TO_PROBLEM_TYPE.get(instruction_type, [])

    def is_compatible(
        self, problem_type: str, instruction_type: InstructionType
    ) -> bool:
        """
        Check if a problem type is compatible with an instruction type.

        Args:
            problem_type: Problem type string
            instruction_type: Instruction type

        Returns:
            True if compatible
        """
        expected = self.get_expected_types(instruction_type)
        return problem_type in expected if expected else True
