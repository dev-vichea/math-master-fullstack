"""
Worksheet processing service that orchestrates:
  Image → OCR → Exercise parsing → Problem solving

This service provides end-to-end processing of math worksheet images,
automatically detecting instructions, extracting problems, and solving them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.api.schemas.responses import SolveData
from app.classifier.context_aware_classifier import ContextAwareClassifier
from app.classifier.problem_classifier.classifier import classify_problem
from app.core.logging import get_logger
from app.core.tasks import TaskStatus, get_task, submit_task, update_task_progress
from app.ocr.engines.base import MathVisionEngine, VisionResult
from app.ocr.factory import create_vision_engine

from sympy import Integral

logger = get_logger("app.services.worksheet")
from app.models.document import Exercise, Problem
from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text
from app.parser.math_parser.expression_parser import ExpressionParseError, parse_math_text
from app.services.exercise_service import ExerciseService, ProcessingResult
from app.services.math_service import MathService
from app.solvers import solve
from app.solvers.base import SolveResult


@dataclass
class SolvedProblem:
    """Result of solving a single problem from a worksheet."""

    label: str
    expression: str
    problem_type: str
    solution: SolveResult | None
    error: str | None = None
    context: dict[str, str] = field(default_factory=dict)
    relationships: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "label": self.label,
            "expression": self.expression,
            "problem_type": self.problem_type,
            "answer": self.solution.answer if self.solution else None,
            "variable": self.solution.variable if self.solution else None,
            "is_verified": self.solution.is_verified if self.solution else False,
            "context": self.context,
            "relationships": self.relationships,
            "steps": [
                {
                    "order": step.order,
                    "description_km": step.description_km,
                    "description_en": step.description_en,
                    "expression": step.expression,
                }
                for step in self.solution.steps
            ]
            if self.solution
            else [],
            "error": self.error,
        }


@dataclass
class WorksheetResult:
    """Complete result of processing a worksheet image."""

    ocr_result: VisionResult
    exercise: Exercise
    solved_problems: list[SolvedProblem]
    statistics: dict[str, Any]
    validation_errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "ocr": {
                "detected_text": self.ocr_result.detected_text,
                "confidence": self.ocr_result.confidence,
                "error": self.ocr_result.error_message,
            },
            "exercise": {
                "sections": [
                    {
                        "instruction": section.instruction.to_dict() if section.instruction else None,
                        "context_text": getattr(section, "context_text", None),
                        "given_variables": getattr(section, "given_variables", {}),
                        "problems": [
                            {
                                "label": problem.label,
                                "label_type": problem.label_type.value,
                                "expression": problem.problem.expression or problem.problem.raw_input,
                                "context": getattr(problem, "context", {}),
                                "relationships": getattr(problem, "relationships", []),
                            }
                            for problem in section.problems
                        ],
                    }
                    for section in self.exercise.sections
                ],
            },
            "solutions": [prob.to_dict() for prob in self.solved_problems],
            "statistics": self.statistics,
            "validation": {
                "is_valid": len(self.validation_errors) == 0,
                "errors": self.validation_errors,
            },
        }


class WorksheetProcessor:
    """
    Orchestrates complete worksheet processing pipeline.

    Pipeline:
    1. OCR: Extract text from image using configured vision engine (Kiri OCR for full worksheets)
    2. Parse: Detect structure (instructions, given context, problems) using ExerciseService
    3. Classify: Determine problem type for each problem (with instruction context)
    4. Solve: Apply appropriate solver to each problem (propagating given context)
    5. Validate: Check structure and flag issues
    """

    def __init__(
        self,
        vision_engine: MathVisionEngine | None = None,
        exercise_service: ExerciseService | None = None,
        math_service: MathService | None = None,
    ):
        """
        Initialize worksheet processor.

        Full worksheets require Kiri OCR (Khmer-aware OCR) by default,
        ensuring full document text and instructions are properly read.
        """
        self.vision_engine = vision_engine or create_vision_engine("kiri")
        self.exercise_service = exercise_service or ExerciseService()
        self.math_service = math_service or MathService()
        self.context_classifier = ContextAwareClassifier()

    async def process_image_async(self, image_bytes: bytes) -> str:
        """
        Submit worksheet processing as a background task.

        Returns a task_id that can be polled for results. Use this for
        large worksheets to avoid blocking the HTTP request.

        Args:
            image_bytes: Raw image bytes (PNG, JPEG, etc.)

        Returns:
            task_id: Unique identifier for polling the result
        """

        async def _process() -> dict[str, Any]:
            result = self.process_image(image_bytes)
            return result.to_dict()

        task_id = await submit_task(_process)
        logger.info(f"Worksheet processing submitted as task {task_id}")
        return task_id

    def process_image(self, image_bytes: bytes) -> WorksheetResult:
        """
        Process a worksheet image end-to-end.

        Args:
            image_bytes: Raw image bytes (PNG, JPEG, etc.)

        Returns:
            WorksheetResult with OCR output, parsed exercise, and solutions
        """
        # Step 1: Run OCR
        ocr_result = self.vision_engine.detect(image_bytes)

        if ocr_result.error_message or not ocr_result.detected_text:
            # OCR failed - return minimal result
            return WorksheetResult(
                ocr_result=ocr_result,
                exercise=Exercise(sections=[]),
                solved_problems=[],
                statistics={},
                validation_errors=[ocr_result.error_message or "OCR failed to detect text"],
            )

        # Step 2: Parse exercise structure
        try:
            detected_text = sanitize_ocr_math_text(ocr_result.detected_text)
            processing_result = self.exercise_service.process_text(detected_text)
            exercise = processing_result.exercise
        except Exception as e:
            # Parsing failed - return error
            return WorksheetResult(
                ocr_result=ocr_result,
                exercise=Exercise(sections=[]),
                solved_problems=[],
                statistics={},
                validation_errors=[f"Exercise parsing failed: {str(e)}"],
            )

        # Step 3: Validate structure
        is_valid, validation_errors = self.exercise_service.validate_exercise(exercise)

        # Step 4: Get statistics
        statistics = self.exercise_service.get_statistics(exercise)

        # Step 5: Solve each problem
        solved_problems: list[SolvedProblem] = []

        for section in exercise.sections:
            for problem in section.problems:
                solved = self._solve_problem(
                    problem=problem,
                    section=section,
                    solved_history=solved_problems,
                )
                solved_problems.append(solved)

        return WorksheetResult(
            ocr_result=ocr_result,
            exercise=exercise,
            solved_problems=solved_problems,
            statistics=statistics,
            validation_errors=validation_errors,
        )

    def _solve_problem(
        self,
        problem: Problem,
        section: Section | None = None,
        solved_history: list[SolvedProblem] | None = None,
    ) -> SolvedProblem:
        """
        Solve a single problem from the worksheet with context propagation.
        """
        label = problem.label if problem.label else "Unknown"
        expression = problem.problem.expression or problem.problem.raw_input
        if expression:
            expression = sanitize_ocr_math_text(expression)
        relationships: list[str] = list(getattr(problem, "relationships", []))
        context_dict = dict(getattr(problem, "context", {}))
        if not context_dict and section and getattr(section, "given_variables", None):
            context_dict = dict(section.given_variables)

        # 1. Context-aware evaluation: check if expression uses variables defined in context
        if context_dict:
            try:
                solved_with_context = self._try_solve_with_context(
                    label=label,
                    expression=expression,
                    context=context_dict,
                    section=section,
                    solved_history=solved_history,
                )
                if solved_with_context:
                    return solved_with_context
            except Exception:
                pass

        # 2. Try standard expression parsing
        try:
            parsed = parse_math_text(expression)
        except ExpressionParseError as e:
            return SolvedProblem(
                label=label,
                expression=expression,
                problem_type="unknown",
                solution=None,
                error=f"Parse error: {str(e)}",
                context=context_dict,
                relationships=relationships,
            )
        except Exception as e:
            return SolvedProblem(
                label=label,
                expression=expression,
                problem_type="unknown",
                solution=None,
                error=f"Unexpected parse error: {str(e)}",
                context=context_dict,
                relationships=relationships,
            )

        # 3. Classify problem type with instruction context
        section_instruction = section.instruction if section else None
        try:
            if (
                isinstance(parsed.sympy_expr, Integral)
                or (hasattr(parsed, "raw_text") and any(k in str(parsed.raw_text) for k in (r"\int", "∫")))
                or any(k in expression for k in (r"\int", "∫"))
            ):
                problem_type = "calculus_integral"
            elif section_instruction and problem.instruction_context:
                classification = self.context_classifier.classify(
                    parsed, instruction=problem.instruction_context
                )
                problem_type = classification.problem_type
            else:
                problem_type = classify_problem(parsed)
        except Exception as e:
            return SolvedProblem(
                label=label,
                expression=expression,
                problem_type="unknown",
                solution=None,
                error=f"Classification error: {str(e)}",
                context=context_dict,
                relationships=relationships,
            )

        # 4. Solve the problem
        if section_instruction and not relationships:
            relationships.append(f"ស្ថិតក្រោមការណែនាំ (Under instruction): {section_instruction.text}")

        try:
            solution = solve(parsed, problem_type)
            return SolvedProblem(
                label=label,
                expression=expression,
                problem_type=problem_type,
                solution=solution,
                error=None,
                context=context_dict,
                relationships=relationships,
            )
        except Exception as e:
            return SolvedProblem(
                label=label,
                expression=expression,
                problem_type=problem_type,
                solution=None,
                error=f"Solving error: {str(e)}",
                context=context_dict,
                relationships=relationships,
            )

    def _try_solve_with_context(
        self,
        label: str,
        expression: str,
        context: dict[str, str],
        section: Section | None,
        solved_history: list[SolvedProblem] | None,
    ) -> SolvedProblem | None:
        """Attempt to solve expression by substituting given context values."""
        import sympy
        from app.api.schemas.responses import SolutionStep

        clean_expr = expression.strip()
        target = None
        body = clean_expr

        if "=" in clean_expr:
            parts = clean_expr.split("=", 1)
            target = parts[0].strip()
            body = parts[1].strip()

        # Parse given variables into SymPy expressions
        given_syms = {}
        for var_name, val_str in context.items():
            try:
                norm_val = val_str.replace("v^", r"\sqrt").replace("v~", r"\sqrt")
                p = parse_math_text(norm_val)
                given_syms[sympy.Symbol(var_name)] = p.sympy_expr
            except Exception:
                continue

        if not given_syms:
            return None

        # Parse body expression
        parsed_body = parse_math_text(body)
        body_symbols = set(parsed_body.symbols)

        # Check if body references previous computed targets
        history_syms = {}
        if solved_history:
            for prev in solved_history:
                prev_var = prev.solution.variable if prev.solution else None
                if prev_var and prev.solution and prev.solution.answer:
                    try:
                        ans_val = prev.solution.answer
                        if "=" in ans_val:
                            ans_val = ans_val.split("=", 1)[1].strip()
                        p_prev = parse_math_text(ans_val)
                        history_syms[sympy.Symbol(prev_var)] = p_prev.sympy_expr
                    except Exception:
                        pass

        # Check if any symbol in body can be substituted
        relevant_vars = [s for s in body_symbols if s in given_syms or s in history_syms]
        if not relevant_vars:
            return None

        combined_syms = {**history_syms, **given_syms}
        sub_expr = parsed_body.sympy_expr.subs(combined_syms)
        ans = sympy.simplify(sympy.expand(sub_expr))
        ans_latex = sympy.latex(ans)
        ans_str = f"{target} = {ans_latex}" if target else ans_latex
        sub_expr_latex = sympy.latex(sub_expr)

        # Build relationships list
        relationships = []
        if section and getattr(section, "context_text", None):
            relationships.append(f"អាស្រ័យលើតម្លៃដែលបានផ្ដល់ (Depends on given values): {section.context_text}")
        else:
            vars_fmt = ", ".join(f"{k} = {v}" for k, v in context.items())
            relationships.append(f"អាស្រ័យលើតម្លៃដែលបានផ្ដល់ (Depends on given values): {vars_fmt}")

        if solved_history:
            for prev in solved_history:
                prev_var = prev.solution.variable if prev.solution else None
                if prev_var and sympy.Symbol(prev_var) in body_symbols:
                    relationships.append(f"ទាក់ទងនឹងលទ្ធផលលំហាត់ {prev.label} ({prev_var} = {prev.solution.answer if prev.solution else ''})")

        steps = [
            SolutionStep(
                order=1,
                description_km="ជំនួសតម្លៃអថេរដែលបានផ្ដល់ចូលក្នុងកន្សោម៖",
                description_en="Substitute given variable values into the expression:",
                expression=f"{target} = {sub_expr_latex}" if target else f"{sub_expr_latex}",
            ),
            SolutionStep(
                order=2,
                description_km="គណនាតម្លៃ និងសម្រួលកន្សោមចុងក្រោយ៖",
                description_en="Evaluate and simplify the final expression:",
                expression=ans_str,
            ),
        ]

        solution = SolveResult(
            answer=ans_str,
            variable=target,
            is_verified=True,
            steps=steps,
        )

        return SolvedProblem(
            label=label,
            expression=expression,
            problem_type="algebraic_substitution",
            solution=solution,
            error=None,
            context=context,
            relationships=relationships,
        )


def get_worksheet_processor() -> WorksheetProcessor:
    """FastAPI dependency for WorksheetProcessor singleton."""
    return WorksheetProcessor()
