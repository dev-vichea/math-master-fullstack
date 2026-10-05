"""
Vision service orchestrating OCR detection, exercise parsing, and mathematical solving.
"""

from __future__ import annotations

from typing import Any

from app.models.problem import MathProblem, MultiProblemSet, ProblemSource
from app.ocr.engines.base import BaseVisionEngine, VisionResult
from app.ocr.quality import CandidateStatus, MathOcrQualityPipeline
from app.parser.exercise_parser.exercise_parser import parse_exercise
from app.reasoning.solution_builder.problem_builder import ProblemBuilder
from app.services.math_service import MathService
from app.utils.exceptions import MathProcessingError, VisionProcessingError
from app.utils.logging import get_logger

logger = get_logger("app.services.vision")


class VisionService:
    """Service encapsulating the image OCR to math solution workflow."""

    def __init__(
        self,
        vision_engine: BaseVisionEngine,
        math_service: MathService | None = None,
        problem_builder: ProblemBuilder | None = None,
        quality_pipeline: MathOcrQualityPipeline | None = None,
    ) -> None:
        self.vision_engine = vision_engine
        self.math_service = math_service or MathService()
        self.problem_builder = problem_builder or ProblemBuilder()
        self.quality_pipeline = quality_pipeline or MathOcrQualityPipeline(formula_engine=self.vision_engine)

    def process_image(self, image_bytes: bytes) -> dict[str, Any]:
        """
        Executes OCR detection with quality validation, parses exercise structure,
        and solves the verified math.
        """
        pipeline_result = self.quality_pipeline.process_image(image_bytes)
        candidate = pipeline_result.selected_candidate

        if candidate.status == CandidateStatus.INVALID and not candidate.is_parseable:
            issues = "; ".join(candidate.validation_issues) if candidate.validation_issues else "Invalid mathematical syntax"
            raise VisionProcessingError(f"Scanned image could not be verified as valid mathematics: {issues}")

        vision_result = VisionResult(
            detected_text=candidate.raw_ocr_text,
            confidence=candidate.confidence,
        )

        exercise_meta = None
        parsed_ex = parse_exercise(candidate.normalized_math_text or candidate.raw_ocr_text)
        exercise_meta = {
            "exercise_title": parsed_ex.exercise_title,
            "instruction": parsed_ex.instruction,
            "primary_expression": candidate.normalized_math_text or parsed_ex.primary_expression,
            "sub_exercises": [
                {
                    "label": sub.label,
                    "raw_text": sub.raw_text,
                    "expression": sub.expression,
                    "intent": sub.intent,
                }
                for sub in parsed_ex.sub_exercises
            ],
        }

        instruction = exercise_meta.get("instruction")
        primary_expr = candidate.normalized_math_text or exercise_meta.get("primary_expression")
        if instruction and primary_expr:
            text_to_solve = f"{instruction} {primary_expr}"
        else:
            text_to_solve = primary_expr or candidate.raw_ocr_text

        try:
            try:
                solve_data = self.math_service.process_question(text_to_solve)
            except MathProcessingError:
                if text_to_solve != candidate.normalized_math_text and candidate.normalized_math_text:
                    solve_data = self.math_service.process_question(candidate.normalized_math_text)
                else:
                    raise

            # If top candidate produced no valid answer, try alternative candidates from variants
            if (solve_data.answer is None or not solve_data.is_verified) and len(pipeline_result.all_candidates) > 1:
                for alt in pipeline_result.all_candidates[1:]:
                    if alt.status != CandidateStatus.INVALID:
                        try:
                            alt_solve = self.math_service.process_question(alt.normalized_math_text or alt.raw_ocr_text)
                            if alt_solve.answer is not None and alt_solve.is_verified:
                                candidate = alt
                                solve_data = alt_solve
                                break
                        except Exception:
                            pass

            solve_data_dict = solve_data.model_dump()
            solve_data_dict["ocr_detected_text"] = candidate.raw_ocr_text
            solve_data_dict["ocr_confidence"] = candidate.confidence
            solve_data_dict["ocr_status"] = candidate.status.value
            solve_data_dict["suspicious_tokens"] = candidate.suspicious_tokens
            solve_data_dict["validation_issues"] = candidate.validation_issues
            solve_data_dict["detected_prefix"] = candidate.detected_prefix
            solve_data_dict["detected_suffix"] = candidate.detected_suffix
            solve_data_dict["exercise_title"] = exercise_meta.get("exercise_title")
            solve_data_dict["instruction"] = exercise_meta.get("instruction")
            solve_data_dict["sub_exercises"] = exercise_meta.get("sub_exercises", [])
            solve_data_dict["cleaned_math_expression"] = candidate.normalized_math_text
            solve_data_dict["candidates"] = [
                {
                    "raw_text": c.raw_ocr_text,
                    "normalized": c.normalized_math_text,
                    "status": c.status.value,
                    "confidence": c.confidence,
                    "score": c.score,
                    "variant": c.variant_name,
                }
                for c in pipeline_result.all_candidates
            ]

            return solve_data_dict

        except MathProcessingError as exc:
            partial_data = {
                "ocr_detected_text": candidate.raw_ocr_text,
                "ocr_confidence": candidate.confidence,
                "ocr_status": candidate.status.value,
                "suspicious_tokens": candidate.suspicious_tokens,
                "exercise_title": exercise_meta.get("exercise_title"),
                "instruction": exercise_meta.get("instruction"),
                "sub_exercises": exercise_meta.get("sub_exercises", []),
                "cleaned_math_expression": candidate.normalized_math_text,
            }
            raise MathProcessingError(
                message=f"OCR detected '{candidate.raw_ocr_text}' but failed to solve: {exc}",
                details=partial_data,
            ) from exc

    def process_image_batch(self, image_bytes: bytes) -> MultiProblemSet:
        """
        Process an image containing multiple sub-exercises into a structured MultiProblemSet.

        This method:
        1. Runs OCR detection
        2. Parses exercise structure (title, instruction, sub-problems)
        3. Creates MathProblem instances for each sub-exercise
        4. Returns a MultiProblemSet with all problems

        Args:
            image_bytes: Raw image bytes

        Returns:
            MultiProblemSet containing all detected problems

        Raises:
            VisionProcessingError: If OCR fails or no text is detected
        """
        # Step 1: Run OCR
        vision_result: VisionResult = self.vision_engine.detect(image_bytes)

        if vision_result.error_message or not vision_result.detected_text:
            err = vision_result.error_message or "No mathematical text detected in image"
            raise VisionProcessingError(err)

        # Step 2: Parse exercise structure
        parsed_exercise = parse_exercise(vision_result.detected_text)

        # Step 3: Create MultiProblemSet container
        problem_set = MultiProblemSet(
            exercise_title=parsed_exercise.exercise_title,
            instruction=parsed_exercise.instruction,
            source_metadata={
                "ocr_detected_text": vision_result.detected_text,
                "ocr_confidence": vision_result.confidence,
                "ocr_provider": self.vision_engine.__class__.__name__,
                "detected_intent": parsed_exercise.detected_intent,
            },
        )

        # Step 4: Process sub-exercises or single primary expression
        if parsed_exercise.sub_exercises:
            # Multiple sub-problems detected (e.g., a), b), c))
            for sub_ex in parsed_exercise.sub_exercises:
                try:
                    # Build MathProblem using new pipeline
                    problem = self.problem_builder.build_from_text(
                        text=sub_ex.expression,
                        language="km",  # Default to Khmer, could be detected
                        source=ProblemSource.OCR,
                    )

                    # Enhance with OCR metadata
                    problem.ocr_confidence = vision_result.confidence
                    problem.metadata.update(
                        {
                            "sub_exercise_label": sub_ex.label,
                            "sub_exercise_raw_text": sub_ex.raw_text,
                            "detected_intent": sub_ex.intent,
                        }
                    )

                    # Add low confidence warning if needed
                    if vision_result.confidence < 0.9:
                        problem.add_warning(
                            f"OCR confidence for sub-exercise {sub_ex.label} is low "
                            f"({vision_result.confidence:.2f}). Review recommended."
                        )

                    problem_set.add_problem(problem)

                except Exception as exc:
                    # Log error but continue processing other sub-exercises
                    logger.warning(
                        f"Failed to build problem for sub-exercise {sub_ex.label}: {exc}"
                    )
                    # Create a placeholder problem with error info
                    error_problem = MathProblem(
                        source=ProblemSource.OCR,
                        language="km",
                        raw_input=sub_ex.expression,
                        ocr_confidence=vision_result.confidence,
                    )
                    error_problem.add_warning(f"Failed to parse: {str(exc)}")
                    error_problem.metadata.update(
                        {
                            "sub_exercise_label": sub_ex.label,
                            "sub_exercise_raw_text": sub_ex.raw_text,
                            "error": str(exc),
                        }
                    )
                    problem_set.add_problem(error_problem)

        elif parsed_exercise.primary_expression:
            # Single problem detected
            try:
                problem = self.problem_builder.build_from_text(
                    text=parsed_exercise.primary_expression,
                    language="km",
                    source=ProblemSource.OCR,
                )

                problem.ocr_confidence = vision_result.confidence
                problem.metadata.update(
                    {
                        "detected_intent": parsed_exercise.detected_intent,
                        "original_ocr_text": vision_result.detected_text,
                    }
                )

                if vision_result.confidence < 0.9:
                    problem.add_warning(
                        f"OCR confidence is low ({vision_result.confidence:.2f}). "
                        "Review recommended."
                    )

                problem_set.add_problem(problem)

            except Exception as exc:
                logger.error(f"Failed to build problem from primary expression: {exc}")
                raise MathProcessingError(
                    message=f"OCR detected '{parsed_exercise.primary_expression}' "
                    f"but failed to parse: {exc}",
                    details={
                        "ocr_detected_text": vision_result.detected_text,
                        "ocr_confidence": vision_result.confidence,
                        "primary_expression": parsed_exercise.primary_expression,
                    },
                ) from exc
        else:
            # No math expression found at all
            raise VisionProcessingError(
                "OCR detected text but could not extract any mathematical expressions"
            )

        return problem_set
