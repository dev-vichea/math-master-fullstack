"""
Vision service orchestrating OCR detection, exercise parsing, and mathematical solving.

Now uses the canonical MathDocumentPipeline for document-aware processing.
"""

from __future__ import annotations

from typing import Any

from app.models.problem import MathProblem, MultiProblemSet, ProblemSource
from app.ocr.engines.base import BaseVisionEngine, VisionResult
from app.ocr.engines.document_ocr import create_document_ocr_engine
from app.ocr.pipeline.document_pipeline import MathDocumentPipeline, ProcessingStatus
from app.ocr.quality import CandidateStatus, MathOcrQualityPipeline
from app.parser.exercise_parser.exercise_parser import parse_exercise
from app.reasoning.solution_builder.problem_builder import ProblemBuilder
from app.services.math_service import MathService
from app.utils.exceptions import MathProcessingError, VisionProcessingError
from app.utils.logging import get_logger

logger = get_logger("app.services.vision")


class VisionService:
    """
    Service encapsulating the image OCR to math solution workflow.
    
    Now uses MathDocumentPipeline for proper document-aware processing.
    """

    def __init__(
        self,
        vision_engine: BaseVisionEngine,
        math_service: MathService | None = None,
        problem_builder: ProblemBuilder | None = None,
        quality_pipeline: MathOcrQualityPipeline | None = None,
        use_document_pipeline: bool = False,
    ) -> None:
        self.vision_engine = vision_engine
        self.math_service = math_service or MathService()
        self.problem_builder = problem_builder or ProblemBuilder()
        self.quality_pipeline = quality_pipeline or MathOcrQualityPipeline(formula_engine=self.vision_engine)
        self.use_document_pipeline = use_document_pipeline
        
        # Initialize document pipeline if enabled
        self._document_pipeline: MathDocumentPipeline | None = None
        if use_document_pipeline:
            self._init_document_pipeline()

    def process_image(self, image_bytes: bytes) -> dict[str, Any]:
        """
        Executes OCR detection with quality validation, parses exercise structure,
        and solves the verified math.
        
        Now uses MathDocumentPipeline for document-aware processing when enabled.
        """
        # Use document pipeline if available and enabled
        if self.use_document_pipeline and self._document_pipeline:
            return self._process_with_document_pipeline(image_bytes)
        
        # Fallback to legacy quality pipeline (backward compatible)
        return self._process_with_quality_pipeline(image_bytes)

    def _process_with_document_pipeline(self, image_bytes: bytes) -> dict[str, Any]:
        """Process image using the new MathDocumentPipeline."""
        logger.info("Processing image with MathDocumentPipeline")
        
        try:
            # Run document pipeline
            pipeline_result = self._document_pipeline.process(image_bytes)
            exercise = pipeline_result.exercise
            
            # If document pipeline failed or got no problems, fall back to legacy
            if pipeline_result.status == ProcessingStatus.FAILED or exercise.get_total_problems() == 0:
                logger.warning(
                    f"Document pipeline didn't extract problems (status={pipeline_result.status.value}), "
                    "falling back to legacy pipeline"
                )
                return self._process_with_quality_pipeline(image_bytes)
        except Exception as exc:
            logger.warning(f"Document pipeline error: {exc}, falling back to legacy pipeline")
            return self._process_with_quality_pipeline(image_bytes)
        
        # For single problem, solve it
        if exercise.get_total_problems() == 1:
            problem = exercise.get_all_problems()[0]
            
            try:
                # Build solve input from instruction + expression
                instruction_text = problem.instruction_context.text if problem.instruction_context else ""
                expression = problem.problem.raw_input
                
                text_to_solve = f"{instruction_text} {expression}".strip()
                solve_data = self.math_service.process_question(text_to_solve)
                
                # Build response
                solve_data_dict = solve_data.model_dump()
                solve_data_dict["ocr_detected_text"] = expression
                solve_data_dict["ocr_confidence"] = problem.problem.ocr_confidence
                solve_data_dict["ocr_status"] = pipeline_result.status.value
                solve_data_dict["exercise_title"] = exercise.title
                solve_data_dict["instruction"] = instruction_text
                solve_data_dict["cleaned_math_expression"] = expression
                solve_data_dict["document_structure"] = {
                    "sections": exercise.get_section_count(),
                    "total_problems": exercise.get_total_problems(),
                }
                solve_data_dict["warnings"] = pipeline_result.warnings
                solve_data_dict["processing_time"] = pipeline_result.processing_time
                
                return solve_data_dict
                
            except MathProcessingError as exc:
                partial_data = {
                    "ocr_detected_text": expression,
                    "ocr_confidence": problem.problem.ocr_confidence,
                    "ocr_status": pipeline_result.status.value,
                    "exercise_title": exercise.title,
                    "instruction": instruction_text,
                    "cleaned_math_expression": expression,
                }
                raise MathProcessingError(
                    message=f"OCR detected '{expression}' but failed to solve: {exc}",
                    details=partial_data,
                ) from exc
        
        # For multiple problems, return structure without solving
        # (use process_image_batch for multi-problem solving)
        return {
            "exercise": exercise.to_dict(),
            "status": pipeline_result.status.value,
            "warnings": pipeline_result.warnings,
            "message": f"Detected {exercise.get_total_problems()} problems. Use /math/vision/batch for multi-problem solving.",
        }

    def _process_with_quality_pipeline(self, image_bytes: bytes) -> dict[str, Any]:
        """Legacy processing using quality pipeline (backward compatible)."""
        logger.info("Processing image with legacy quality pipeline")
        pipeline_result = self.quality_pipeline.process_image(image_bytes)
        candidate = pipeline_result.selected_candidate

        if candidate.status == CandidateStatus.INVALID and not candidate.is_parseable:
            issues = "; ".join(candidate.validation_issues) if candidate.validation_issues else "Invalid mathematical syntax"
            raise VisionProcessingError(f"Scanned image could not be verified as valid mathematics: {issues}")

        vision_result = VisionResult(
            detected_text=candidate.raw_ocr_text,
            confidence=candidate.confidence,
        )

        parsed_ex = parse_exercise(candidate.normalized_math_text or candidate.raw_ocr_text)
        cand_meta = candidate.exercise_metadata or {}
        
        exercise_title = parsed_ex.exercise_title or cand_meta.get("exercise_title")
        instruction = parsed_ex.instruction or cand_meta.get("instruction")
        primary_expr = cand_meta.get("primary_expression") or parsed_ex.primary_expression or candidate.normalized_math_text
        
        sub_exercises = [
            {
                "label": sub.label,
                "raw_text": sub.raw_text,
                "expression": sub.expression,
                "intent": sub.intent,
            }
            for sub in parsed_ex.sub_exercises
        ] if parsed_ex.sub_exercises else cand_meta.get("sub_exercises", [])

        exercise_meta = {
            "exercise_title": exercise_title,
            "instruction": instruction,
            "primary_expression": primary_expr,
            "sub_exercises": sub_exercises,
        }

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
                    "raw_text": candidate.raw_ocr_text,
                    "normalized": candidate.normalized_math_text,
                    "status": candidate.status.value,
                    "confidence": candidate.confidence,
                    "score": candidate.score,
                    "variant": candidate.variant_name,
                }
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

        Now uses MathDocumentPipeline for proper document-aware multi-problem extraction.

        Args:
            image_bytes: Raw image bytes

        Returns:
            MultiProblemSet containing all detected problems

        Raises:
            VisionProcessingError: If OCR fails or no text is detected
        """
        # Use document pipeline if available
        if self.use_document_pipeline and self._document_pipeline:
            return self._process_batch_with_document_pipeline(image_bytes)
        
        # Fallback to legacy method
        return self._process_batch_legacy(image_bytes)

    def _process_batch_with_document_pipeline(self, image_bytes: bytes) -> MultiProblemSet:
        """Process batch using MathDocumentPipeline."""
        logger.info("Processing batch with MathDocumentPipeline")
        
        try:
            # Run document pipeline
            pipeline_result = self._document_pipeline.process(image_bytes)
            exercise = pipeline_result.exercise
            
            # If document pipeline failed or got no problems, fall back to legacy
            if pipeline_result.status == ProcessingStatus.FAILED or exercise.get_total_problems() == 0:
                logger.warning(
                    f"Document pipeline didn't extract problems (status={pipeline_result.status.value}), "
                    "falling back to legacy batch processing"
                )
                return self._process_batch_legacy(image_bytes)
        except Exception as exc:
            logger.warning(f"Document pipeline error: {exc}, falling back to legacy batch processing")
            return self._process_batch_legacy(image_bytes)
        
        # Create MultiProblemSet from Exercise
        problem_set = MultiProblemSet(
            exercise_title=exercise.title,
            instruction=exercise.sections[0].instruction.text if exercise.sections else None,
            source_metadata={
                "ocr_engine": "MathDocumentPipeline",
                "ocr_confidence": exercise.ocr_confidence,
                "processing_status": pipeline_result.status.value,
                "sections": exercise.get_section_count(),
                "processing_time": pipeline_result.processing_time,
            },
        )
        
        # Add all problems from all sections
        for section in exercise.sections:
            for problem in section.problems:
                problem_set.add_problem(problem.problem)
        
        logger.info(f"Created MultiProblemSet with {problem_set.problem_count} problems")
        return problem_set

    def _process_batch_legacy(self, image_bytes: bytes) -> MultiProblemSet:
        """
        Legacy batch processing (backward compatible).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            MultiProblemSet containing all detected problems
            
        Raises:
            VisionProcessingError: If OCR fails or no text is detected
        """
        logger.info("Processing batch with legacy method")
        
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

    def _init_document_pipeline(self) -> None:
        """Initialize the MathDocumentPipeline with appropriate engines."""
        try:
            document_ocr_engine = create_document_ocr_engine(lang="eng+khm")
            
            self._document_pipeline = MathDocumentPipeline(
                document_ocr_engine=document_ocr_engine,
                formula_ocr_pipeline=self.quality_pipeline,
                enable_formula_ocr=True,
                enable_quality_validation=True,
            )
            
            logger.info("MathDocumentPipeline initialized successfully")
        except Exception as exc:
            logger.warning(f"Failed to initialize document pipeline: {exc}, will use fallback")
            self._document_pipeline = None
