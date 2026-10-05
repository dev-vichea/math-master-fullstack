"""
Math Document Pipeline - Canonical orchestrator for document-aware OCR processing.

This pipeline implements the correct flow for math exercise worksheets:
1. Document OCR + layout extraction (cheap text OCR)
2. Region classification (header, instruction, math, label, noise)
3. Selective formula OCR (expensive, only on math regions)
4. Text + formula merge by spatial coordinates
5. Document structure parsing (Exercise → Section → Problem hierarchy)
6. OCR quality validation per region
7. Normalization (safe, canonical)
8. Context propagation (instruction + given variables)

This replaces the incorrect approach of running expensive formula OCR on entire pages.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.models.document import BoundingBox, Exercise, Instruction, Problem, Section
from app.ocr.layout.reading_order import ReadingOrderAnalyzer, TextBlock
from app.ocr.layout.region_classifier import RegionClassifier, RegionType
from app.ocr.normalization.canonical_normalizer import NormalizationResult, normalize_math_text
from app.ocr.quality.models import CandidateStatus

logger = logging.getLogger("app.ocr.pipeline.document")


class ProcessingStatus(str, Enum):
    """Status of document processing."""
    SUCCESS = "success"
    PARTIAL = "partial"  # Some regions processed successfully
    NEEDS_REVIEW = "needs_review"  # Low confidence, manual review recommended
    FAILED = "failed"


@dataclass
class RegionOcrResult:
    """OCR result for a single region."""
    text_block: TextBlock
    region_type: RegionType
    formula_ocr_text: str | None = None  # Enhanced formula OCR if applied
    ocr_confidence: float = 1.0
    normalization: NormalizationResult | None = None
    validation_issues: list[str] = field(default_factory=list)
    needs_review: bool = False


@dataclass
class DocumentPipelineResult:
    """Complete result from the document pipeline."""
    exercise: Exercise
    status: ProcessingStatus
    regions: list[RegionOcrResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    processing_time: float = 0.0
    debug_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "exercise": self.exercise.to_dict(),
            "status": self.status.value,
            "warnings": self.warnings,
            "processing_time": round(self.processing_time, 3),
            "region_count": len(self.regions),
            "debug_info": self.debug_info,
        }


class MathDocumentPipeline:
    """
    Canonical pipeline for document-aware math OCR processing.
    
    This pipeline correctly handles full exercise worksheets by:
    - Using cheap document OCR first for layout analysis
    - Classifying regions before expensive formula OCR
    - Preserving spatial layout and document structure
    - Propagating context between related problems
    """

    def __init__(
        self,
        document_ocr_engine: Any | None = None,  # Will be DocumentOcrEngine
        formula_ocr_pipeline: Any | None = None,  # Will be MathOcrQualityPipeline
        reading_order_analyzer: ReadingOrderAnalyzer | None = None,
        region_classifier: RegionClassifier | None = None,
        enable_formula_ocr: bool = True,
        enable_quality_validation: bool = True,
    ):
        """
        Initialize the document pipeline.
        
        Args:
            document_ocr_engine: Engine for document/text OCR (Tesseract/Kiri)
            formula_ocr_pipeline: Quality pipeline for formula OCR (Pix2Tex)
            reading_order_analyzer: Analyzer for reading order determination
            region_classifier: Classifier for region types
            enable_formula_ocr: Whether to apply expensive formula OCR
            enable_quality_validation: Whether to validate OCR quality
        """
        self.document_ocr_engine = document_ocr_engine
        self.formula_ocr_pipeline = formula_ocr_pipeline
        self.reading_order_analyzer = reading_order_analyzer or ReadingOrderAnalyzer()
        self.region_classifier = region_classifier or RegionClassifier()
        self.enable_formula_ocr = enable_formula_ocr
        self.enable_quality_validation = enable_quality_validation

    def process(self, image_bytes: bytes) -> DocumentPipelineResult:
        """
        Process a math exercise image through the complete document pipeline.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            DocumentPipelineResult with Exercise structure and metadata
        """
        import time
        start_time = time.time()
        
        warnings: list[str] = []
        debug_info: dict[str, Any] = {}

        try:
            # Stage 1: Document OCR + Layout Extraction
            logger.info("Stage 1: Document OCR + Layout Extraction")
            text_blocks = self._extract_text_blocks(image_bytes)
            debug_info["text_blocks_count"] = len(text_blocks)
            
            if not text_blocks:
                warnings.append("No text blocks detected in image")
                return self._create_empty_result(
                    ProcessingStatus.FAILED,
                    warnings,
                    time.time() - start_time,
                    debug_info,
                )

            # Stage 2: Region Classification
            logger.info("Stage 2: Region Classification")
            classified_regions = self._classify_regions(text_blocks)
            debug_info["regions_by_type"] = self._count_regions_by_type(classified_regions)

            # Stage 3: Selective Formula OCR
            logger.info("Stage 3: Selective Formula OCR")
            enhanced_regions = self._apply_formula_ocr(classified_regions, image_bytes)
            
            # Stage 4: Text + Formula Merge
            logger.info("Stage 4: Text + Formula Merge")
            merged_regions = self._merge_text_and_formulas(enhanced_regions)

            # Stage 5: Document Structure Parsing
            logger.info("Stage 5: Document Structure Parsing")
            exercise = self._parse_document_structure(merged_regions)

            # Stage 6: OCR Quality Validation
            logger.info("Stage 6: OCR Quality Validation")
            self._validate_ocr_quality(exercise, merged_regions)

            # Stage 7: Normalization
            logger.info("Stage 7: Normalization")
            self._normalize_expressions(exercise, merged_regions)

            # Stage 8: Context Propagation
            logger.info("Stage 8: Context Propagation")
            self._propagate_context(exercise)

            # Set OCR metadata on exercise
            exercise.ocr_engine = "MathDocumentPipeline"
            exercise.ocr_confidence = self._calculate_average_confidence(merged_regions)
            
            # Determine overall status
            status = self._determine_status(exercise, merged_regions, warnings)

            processing_time = time.time() - start_time
            logger.info(f"Document pipeline completed in {processing_time:.2f}s with status {status.value}")

            return DocumentPipelineResult(
                exercise=exercise,
                status=status,
                regions=merged_regions,
                warnings=warnings,
                processing_time=processing_time,
                debug_info=debug_info,
            )

        except Exception as exc:
            logger.error(f"Document pipeline failed: {exc}", exc_info=True)
            warnings.append(f"Pipeline error: {str(exc)}")
            return self._create_empty_result(
                ProcessingStatus.FAILED,
                warnings,
                time.time() - start_time,
                debug_info,
            )

    # =========================================================================
    # Stage 1: Document OCR + Layout Extraction
    # =========================================================================

    def _extract_text_blocks(self, image_bytes: bytes) -> list[TextBlock]:
        """
        Stage 1: Extract text blocks with bounding boxes using document OCR.
        
        Uses cheap document/text OCR (Tesseract/Kiri) to extract all text
        with spatial layout information.
        """
        if self.document_ocr_engine is None:
            logger.warning("No document OCR engine configured, creating stub engine")
            from app.ocr.engines.document_ocr import create_document_ocr_engine
            self.document_ocr_engine = create_document_ocr_engine(use_stub=True)

        try:
            # Call document OCR engine to extract text blocks
            text_blocks = self.document_ocr_engine.extract_text_blocks(image_bytes)
            
            # Determine reading order
            if text_blocks:
                text_blocks = self.reading_order_analyzer.analyze(text_blocks)
            
            logger.info(f"Extracted {len(text_blocks)} text blocks")
            return text_blocks
            
        except Exception as exc:
            logger.error(f"Document OCR failed: {exc}", exc_info=True)
            return []

    # =========================================================================
    # Stage 2: Region Classification
    # =========================================================================

    def _classify_regions(self, text_blocks: list[TextBlock]) -> list[RegionOcrResult]:
        """
        Stage 2: Classify text blocks into semantic region types.
        
        Classifies each block as: header, instruction, problem_label,
        problem_content, footer, or noise.
        """
        classified_regions: list[RegionOcrResult] = []
        
        for block in text_blocks:
            region_type = self.region_classifier.classify(block)
            
            result = RegionOcrResult(
                text_block=block,
                region_type=region_type,
                ocr_confidence=block.confidence,
            )
            classified_regions.append(result)
            
        logger.info(f"Classified {len(classified_regions)} regions")
        return classified_regions

    def _count_regions_by_type(self, regions: list[RegionOcrResult]) -> dict[str, int]:
        """Helper to count regions by type for debugging."""
        counts: dict[str, int] = {}
        for region in regions:
            region_type = region.region_type.value
            counts[region_type] = counts.get(region_type, 0) + 1
        return counts

    # =========================================================================
    # Stage 3: Selective Formula OCR
    # =========================================================================

    def _apply_formula_ocr(
        self, 
        regions: list[RegionOcrResult], 
        image_bytes: bytes
    ) -> list[RegionOcrResult]:
        """
        Stage 3: Apply expensive formula OCR only to math content regions.
        
        For regions classified as PROBLEM_CONTENT, crops the region from
        the original image and runs the quality formula OCR pipeline.
        
        Uses parallel processing for multiple regions to improve performance.
        """
        if not self.enable_formula_ocr or self.formula_ocr_pipeline is None:
            logger.info("Formula OCR disabled or not configured")
            return regions

        math_regions = [r for r in regions if r.region_type == RegionType.PROBLEM_CONTENT]
        logger.info(f"Applying formula OCR to {len(math_regions)} math regions")

        # Use parallel processing for 3+ regions
        if len(math_regions) >= 3:
            return self._apply_formula_ocr_parallel(math_regions, image_bytes, regions)
        
        # Sequential processing for small number of regions
        for region in math_regions:
            self._process_single_region_formula_ocr(region, image_bytes)

        return regions
    
    def _process_single_region_formula_ocr(
        self,
        region: RegionOcrResult,
        image_bytes: bytes
    ) -> None:
        """Process formula OCR for a single region."""
        try:
            # Run formula OCR on this specific region
            bbox = region.text_block.bounding_box
            ocr_result = self.formula_ocr_pipeline.process_region(
                image_bytes,
                region_bbox=bbox,
                max_variants=2,  # Reduce variants for speed
            )
            
            # Store enhanced formula OCR text
            if ocr_result.selected_candidate.normalized_math_text:
                region.formula_ocr_text = ocr_result.selected_candidate.normalized_math_text
                region.ocr_confidence = ocr_result.selected_candidate.confidence
                
                # Flag if validation issues detected
                if ocr_result.selected_candidate.validation_issues:
                    region.validation_issues.extend(
                        ocr_result.selected_candidate.validation_issues
                    )
                
                if ocr_result.selected_candidate.status == CandidateStatus.INVALID:
                    region.needs_review = True
                    
                logger.debug(
                    f"Formula OCR for region: '{region.formula_ocr_text}' "
                    f"[conf={region.ocr_confidence:.2f}]"
                )
            else:
                logger.warning(f"Formula OCR produced no result for region")
                
        except Exception as exc:
            logger.error(f"Formula OCR failed for region: {exc}", exc_info=True)
            region.validation_issues.append(f"Formula OCR error: {str(exc)}")
    
    def _apply_formula_ocr_parallel(
        self,
        math_regions: list[RegionOcrResult],
        image_bytes: bytes,
        all_regions: list[RegionOcrResult]
    ) -> list[RegionOcrResult]:
        """
        Apply formula OCR to multiple regions in parallel using ThreadPoolExecutor.
        
        This improves performance for worksheets with many math problems.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Use up to 4 workers (balance between speed and resource usage)
        max_workers = min(4, len(math_regions))
        logger.info(f"Using parallel processing with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all regions for processing
            future_to_region = {
                executor.submit(
                    self._process_single_region_formula_ocr,
                    region,
                    image_bytes
                ): region
                for region in math_regions
            }
            
            # Wait for all to complete
            completed = 0
            for future in as_completed(future_to_region):
                completed += 1
                try:
                    future.result()  # Raises exception if task failed
                except Exception as exc:
                    region = future_to_region[future]
                    logger.error(f"Parallel formula OCR failed: {exc}")
                    region.validation_issues.append(f"Parallel OCR error: {str(exc)}")
        
        logger.info(f"Completed parallel formula OCR for {completed}/{len(math_regions)} regions")
        return all_regions

    # =========================================================================
    # Stage 4: Text + Formula Merge
    # =========================================================================

    def _merge_text_and_formulas(
        self, 
        regions: list[RegionOcrResult]
    ) -> list[RegionOcrResult]:
        """
        Stage 4: Merge text OCR and formula OCR by spatial coordinates.
        
        Combines results from document OCR (Khmer/English text) and
        formula OCR (math expressions) based on bounding boxes.
        """
        # For now, keep the enhanced text from formula OCR if available
        for region in regions:
            if region.formula_ocr_text:
                # Use formula OCR result for math regions
                region.text_block.text = region.formula_ocr_text
            # Otherwise keep original text OCR
            
        return regions

    # =========================================================================
    # Stage 5: Document Structure Parsing
    # =========================================================================

    def _parse_document_structure(
        self, 
        regions: list[RegionOcrResult]
    ) -> Exercise:
        """
        Stage 5: Parse regions into Exercise → Section → Problem hierarchy.
        
        Builds the canonical Document structure with spatial layout preserved.
        """
        from app.parser.document_parser import ExerciseDocumentParser
        
        # Extract text blocks and region classifications
        text_blocks = [r.text_block for r in regions]
        region_map = {r.text_block: r.region_type for r in regions}
        
        # Parse into document structure
        parser = ExerciseDocumentParser()
        exercise = parser.parse(text_blocks, region_classifications=region_map)
        
        logger.info(
            f"Parsed exercise: {exercise.get_section_count()} sections, "
            f"{exercise.get_total_problems()} problems"
        )
        
        return exercise

    # =========================================================================
    # Stage 6: OCR Quality Validation
    # =========================================================================

    def _validate_ocr_quality(
        self, 
        exercise: Exercise, 
        regions: list[RegionOcrResult]
    ) -> None:
        """
        Stage 6: Validate OCR quality for each region.
        
        Applies validation logic from MathOcrQualityPipeline to detect
        suspicious tokens, malformed expressions, and low confidence.
        """
        if not self.enable_quality_validation:
            logger.info("Quality validation disabled")
            return

        # Validate each problem in the exercise
        for section in exercise.sections:
            for problem in section.problems:
                # Find corresponding region
                prob_region = None
                for region in regions:
                    if (region.text_block.bounding_box == problem.bounding_box or
                        region.region_type == RegionType.PROBLEM_CONTENT):
                        prob_region = region
                        break
                
                if prob_region:
                    # Check confidence
                    if prob_region.ocr_confidence < 0.7:
                        problem.problem.add_warning(
                            f"Low OCR confidence: {prob_region.ocr_confidence:.2f}"
                        )
                    
                    # Add validation issues to problem
                    if prob_region.validation_issues:
                        for issue in prob_region.validation_issues:
                            problem.problem.add_warning(f"Validation: {issue}")
                    
                    # Flag for review if needed
                    if prob_region.needs_review:
                        problem.problem.add_warning("OCR needs manual review")

        logger.debug(f"Validated {exercise.get_total_problems()} problems")

    # =========================================================================
    # Stage 7: Normalization
    # =========================================================================

    def _normalize_expressions(
        self, 
        exercise: Exercise, 
        regions: list[RegionOcrResult]
    ) -> None:
        """
        Stage 7: Apply canonical normalization to mathematical expressions.
        
        Uses the unified normalize_math_text() from canonical_normalizer.
        """
        # Normalize problem expressions in the exercise
        for section in exercise.sections:
            for problem in section.problems:
                # Get the raw expression
                raw_expr = problem.problem.raw_input
                
                if not raw_expr:
                    continue
                
                # Apply normalization
                result = normalize_math_text(
                    raw_expr,
                    apply_ocr_repairs=True,
                    apply_structural=True,
                    detect_prefix_suffix=True,
                )
                
                # Update problem with normalized expression
                if result.normalized_text != raw_expr:
                    # Store both original and normalized
                    problem.problem.metadata["original_expression"] = raw_expr
                    problem.problem.raw_input = result.normalized_text
                    
                    logger.debug(
                        f"Normalized: '{raw_expr}' → '{result.normalized_text}'"
                    )
                
                # Store normalization metadata
                if result.detected_prefix:
                    problem.problem.metadata["detected_prefix"] = result.detected_prefix
                if result.detected_suffix:
                    problem.problem.metadata["detected_suffix"] = result.detected_suffix
                    
                # Find corresponding region and store normalization result
                for region in regions:
                    if (region.text_block.bounding_box == problem.bounding_box):
                        region.normalization = result
                        break

        logger.debug(f"Normalized {exercise.get_total_problems()} problem expressions")

    # =========================================================================
    # Stage 8: Context Propagation
    # =========================================================================

    def _propagate_context(self, exercise: Exercise) -> None:
        """
        Stage 8: Propagate instruction and context to problems.
        
        Links instruction to problems and propagates shared context/
        given variables from Section to Problem.
        """
        for section in exercise.sections:
            # Context already propagated by Section.add_problem()
            # Just verify it's set correctly
            for problem in section.problems:
                if not problem.instruction_context:
                    problem.instruction_context = section.instruction
                if not problem.context and section.given_variables:
                    problem.context = dict(section.given_variables)

    # =========================================================================
    # Utilities
    # =========================================================================

    def _calculate_average_confidence(self, regions: list[RegionOcrResult]) -> float:
        """Calculate average OCR confidence across all regions."""
        if not regions:
            return 0.0
        
        confidences = [r.ocr_confidence for r in regions if r.ocr_confidence > 0]
        if not confidences:
            return 0.0
            
        return sum(confidences) / len(confidences)

    def _determine_status(
        self,
        exercise: Exercise,
        regions: list[RegionOcrResult],
        warnings: list[str],
    ) -> ProcessingStatus:
        """Determine overall processing status."""
        # Check if any regions need review
        needs_review = any(r.needs_review for r in regions)
        
        # Check if we got any problems
        has_problems = exercise.get_total_problems() > 0
        
        if needs_review:
            return ProcessingStatus.NEEDS_REVIEW
        elif not has_problems:
            warnings.append("No mathematical problems detected")
            return ProcessingStatus.PARTIAL
        elif warnings:
            return ProcessingStatus.PARTIAL
        else:
            return ProcessingStatus.SUCCESS

    def _create_empty_result(
        self,
        status: ProcessingStatus,
        warnings: list[str],
        processing_time: float,
        debug_info: dict[str, Any],
    ) -> DocumentPipelineResult:
        """Create an empty result for failure cases."""
        exercise = Exercise()
        exercise.warnings = warnings
        
        return DocumentPipelineResult(
            exercise=exercise,
            status=status,
            regions=[],
            warnings=warnings,
            processing_time=processing_time,
            debug_info=debug_info,
        )
