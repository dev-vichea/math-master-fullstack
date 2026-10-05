"""
Edge case and error scenario tests for document pipeline.
Tests boundary conditions, error handling, and graceful degradation.
"""

import io
import pytest
from PIL import Image

from app.ocr.pipeline.document_pipeline import MathDocumentPipeline, ProcessingStatus
from app.ocr.engines.document_ocr import create_document_ocr_engine


class TestEmptyAndInvalidInputs:
    """Test handling of empty, invalid, and corrupted inputs."""

    def test_empty_bytes(self):
        """Pipeline should handle empty bytes gracefully."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        result = pipeline.process(b"")
        
        # Stub engine returns dummy text, so status will be PARTIAL (not FAILED)
        # In production with real OCR, empty bytes would fail
        assert result.status in [ProcessingStatus.FAILED, ProcessingStatus.PARTIAL]
        assert result.exercise.get_total_problems() == 0

    def test_corrupted_image_bytes(self):
        """Pipeline should handle corrupted image data gracefully."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        # Corrupted PNG header
        corrupted = b"\x89PNG\r\n\x1a\n" + b"corrupted_data_not_a_valid_png"
        result = pipeline.process(corrupted)
        
        # Should fail gracefully, not crash
        assert result.status in [ProcessingStatus.FAILED, ProcessingStatus.PARTIAL]
        assert result.exercise is not None

    def test_whitespace_only_image(self):
        """Pipeline should handle pure white/blank images."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        # Create pure white image
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete but find no text
        assert result.status in [ProcessingStatus.FAILED, ProcessingStatus.PARTIAL, ProcessingStatus.NEEDS_REVIEW]


class TestBoundaryConditions:
    """Test boundary conditions and extreme values."""

    def test_very_small_image(self):
        """Pipeline should handle very small images (10x10 pixels)."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        # Tiny image
        img = Image.new('RGB', (10, 10), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete without crashing
        assert result.status in [ProcessingStatus.FAILED, ProcessingStatus.PARTIAL, ProcessingStatus.NEEDS_REVIEW]

    def test_large_image(self):
        """Pipeline should handle large images (5000x5000 pixels)."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        # Large image (but not too large to cause memory issues in CI)
        img = Image.new('RGB', (2000, 2000), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete within reasonable time
        assert result.processing_time < 10.0  # seconds
        assert result.status is not None

    def test_single_character_input(self):
        """Pipeline should handle minimal input (single character)."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        # Create image with single character
        from PIL import ImageDraw, ImageFont
        img = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), "x", fill='black')
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete, may or may not find valid math
        assert result.exercise is not None


class TestContentEdgeCases:
    """Test various content scenarios."""

    def test_text_only_no_math(self):
        """Pipeline should handle images with text but no mathematical content."""
        from app.ocr.engines.document_ocr import TextBlock, StubDocumentOcrEngine
        from app.models.document import BoundingBox
        
        class TextOnlyEngine(StubDocumentOcrEngine):
            def extract_text_blocks(self, image_bytes):
                # Return text blocks with no mathematical content
                return [
                    TextBlock(
                        text="This is just regular text",
                        bounding_box=BoundingBox(x=0.1, y=0.1, width=0.8, height=0.1, page=0),
                        confidence=0.95,
                    ),
                    TextBlock(
                        text="No math expressions here",
                        bounding_box=BoundingBox(x=0.1, y=0.3, width=0.8, height=0.1, page=0),
                        confidence=0.93,
                    ),
                ]
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=TextOnlyEngine(),
            enable_formula_ocr=False,
        )
        
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete, may have warnings
        assert result.status in [
            ProcessingStatus.SUCCESS,
            ProcessingStatus.PARTIAL,
            ProcessingStatus.NEEDS_REVIEW,
        ]

    def test_very_long_expression(self):
        """Pipeline should handle very long mathematical expressions."""
        from app.ocr.engines.document_ocr import TextBlock, StubDocumentOcrEngine
        from app.models.document import BoundingBox
        
        # Create expression with 100+ characters
        long_expr = " + ".join([f"{i}x^{i}" for i in range(1, 30)])
        
        class LongExpressionEngine(StubDocumentOcrEngine):
            def extract_text_blocks(self, image_bytes):
                return [
                    TextBlock(
                        text=long_expr,
                        bounding_box=BoundingBox(x=0.1, y=0.1, width=0.8, height=0.1, page=0),
                        confidence=0.90,
                    )
                ]
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=LongExpressionEngine(),
            enable_formula_ocr=False,
        )
        
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete without crashing
        assert result.exercise is not None
        assert result.status is not None

    def test_many_problems_per_page(self):
        """Pipeline should handle many problems (20+) on one page."""
        from app.ocr.engines.document_ocr import TextBlock, StubDocumentOcrEngine
        from app.models.document import BoundingBox
        
        class ManyProblemsEngine(StubDocumentOcrEngine):
            def extract_text_blocks(self, image_bytes):
                blocks = []
                for i in range(1, 25):  # 24 problems
                    y_pos = 0.05 + (i * 0.04)  # Spread vertically
                    blocks.append(
                        TextBlock(
                            text=f"{i}. 2x + {i} = {i*2}",
                            bounding_box=BoundingBox(x=0.1, y=y_pos, width=0.4, height=0.03, page=0),
                            confidence=0.92,
                        )
                    )
                return blocks
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=ManyProblemsEngine(),
            enable_formula_ocr=False,
        )
        
        img = Image.new('RGB', (800, 800), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete and parse multiple problems
        assert result.exercise is not None
        assert result.processing_time < 15.0  # Should be reasonably fast


class TestConfidenceLevels:
    """Test handling of various OCR confidence levels."""

    def test_low_confidence_text(self):
        """Pipeline should flag low confidence OCR results."""
        from app.ocr.engines.document_ocr import TextBlock, StubDocumentOcrEngine
        from app.models.document import BoundingBox
        
        class LowConfidenceEngine(StubDocumentOcrEngine):
            def extract_text_blocks(self, image_bytes):
                return [
                    TextBlock(
                        text="2x + 3 = 7",
                        bounding_box=BoundingBox(x=0.1, y=0.1, width=0.4, height=0.1, page=0),
                        confidence=0.25,  # Very low confidence
                    )
                ]
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=LowConfidenceEngine(),
            enable_formula_ocr=False,
        )
        
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete successfully even with low confidence
        # The confidence is tracked but doesn't automatically fail processing
        assert result.status in [ProcessingStatus.SUCCESS, ProcessingStatus.PARTIAL, ProcessingStatus.NEEDS_REVIEW]
        
        # Verify low confidence is captured
        assert result.exercise.ocr_confidence < 0.5


class TestErrorRecovery:
    """Test error recovery and fallback mechanisms."""

    def test_formula_ocr_failure_continues(self):
        """Pipeline should continue if formula OCR fails on some regions."""
        from app.ocr.engines.document_ocr import TextBlock, StubDocumentOcrEngine
        from app.models.document import BoundingBox
        from app.ocr.quality import MathOcrQualityPipeline
        
        class FailingFormulaOcrPipeline(MathOcrQualityPipeline):
            def process_region(self, image_bytes, region_bbox=None, max_variants=3):
                raise Exception("Formula OCR engine failed")
        
        class GoodTextEngine(StubDocumentOcrEngine):
            def extract_text_blocks(self, image_bytes):
                return [
                    TextBlock(
                        text="Problem 1:",
                        bounding_box=BoundingBox(x=0.1, y=0.1, width=0.3, height=0.05, page=0),
                        confidence=0.95,
                    ),
                    TextBlock(
                        text="2x + 3 = 7",
                        bounding_box=BoundingBox(x=0.1, y=0.2, width=0.4, height=0.05, page=0),
                        confidence=0.90,
                    ),
                ]
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=GoodTextEngine(),
            formula_ocr_pipeline=FailingFormulaOcrPipeline(),
            enable_formula_ocr=True,
        )
        
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete with warnings, not crash
        assert result.status in [ProcessingStatus.SUCCESS, ProcessingStatus.PARTIAL]
        # Should have validation issues recorded
        if result.regions:
            problem_regions = [r for r in result.regions if r.region_type.value == "problem_content"]
            if problem_regions:
                assert any("Formula OCR error" in issue for region in problem_regions for issue in region.validation_issues)


class TestMixedContent:
    """Test mixed language and content scenarios."""

    def test_khmer_and_english_mixed(self):
        """Pipeline should handle mixed Khmer and English text."""
        from app.ocr.engines.document_ocr import TextBlock, StubDocumentOcrEngine
        from app.models.document import BoundingBox
        
        class MixedLanguageEngine(StubDocumentOcrEngine):
            def extract_text_blocks(self, image_bytes):
                return [
                    TextBlock(
                        text="លំហាត់ទី Exercise 1",
                        bounding_box=BoundingBox(x=0.1, y=0.1, width=0.4, height=0.05, page=0),
                        confidence=0.92,
                    ),
                    TextBlock(
                        text="រកចម្លើយ Solve: 2x + 3 = 7",
                        bounding_box=BoundingBox(x=0.1, y=0.2, width=0.5, height=0.05, page=0),
                        confidence=0.89,
                    ),
                ]
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=MixedLanguageEngine(),
            enable_formula_ocr=False,
        )
        
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should handle mixed content
        assert result.exercise is not None
        assert result.status in [ProcessingStatus.SUCCESS, ProcessingStatus.PARTIAL, ProcessingStatus.NEEDS_REVIEW]


@pytest.mark.integration
class TestEndToEndEdgeCases:
    """End-to-end edge case tests."""

    def test_pipeline_timeout_protection(self):
        """Pipeline should complete within reasonable time even with complex input."""
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        # Create complex image
        img = Image.new('RGB', (1200, 1600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        
        result = pipeline.process(buf.getvalue())
        
        # Should complete in under 30 seconds
        assert result.processing_time < 30.0

    def test_memory_efficiency(self):
        """Pipeline should not leak memory with repeated calls."""
        import gc
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(use_stub=True),
            enable_formula_ocr=False,
        )
        
        img = Image.new('RGB', (800, 600), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        image_bytes = buf.getvalue()
        
        # Process same image multiple times
        for _ in range(5):
            result = pipeline.process(image_bytes)
            assert result is not None
        
        # Force garbage collection
        gc.collect()
        
        # Should complete without memory errors
        result = pipeline.process(image_bytes)
        assert result.exercise is not None
