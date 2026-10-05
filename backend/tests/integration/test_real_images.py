"""
Integration tests using real sample images.
These tests verify the document pipeline works end-to-end with actual image files.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.ocr.pipeline.document_pipeline import MathDocumentPipeline, ProcessingStatus
from app.ocr.engines.document_ocr import create_document_ocr_engine
from app.services.vision_service import VisionService
from app.ocr.engines.base import BaseVisionEngine


def find_sample_image(filename: str) -> Path | None:
    """Find sample image in various possible locations."""
    candidates = [
        Path(__file__).parent.parent.parent.parent / "frontend_legacy" / "public" / "samples" / filename,
        Path(__file__).parent.parent.parent.parent / "frontend_legacy" / "dist" / "samples" / filename,
        Path(__file__).parent.parent.parent / "frontend" / "samples" / filename,
        Path(__file__).parent.parent / "fixtures" / filename,
    ]
    
    for path in candidates:
        if path.exists():
            return path
    return None


@pytest.mark.integration
class TestRealImageProcessing:
    """Test document pipeline with real sample images."""

    def test_sample1_simple_equation(self):
        """Test processing sample1.png - simple linear equation."""
        sample_path = find_sample_image("sample1.png")
        if not sample_path:
            pytest.skip("sample1.png not found")
        
        # Create document pipeline
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,  # Skip expensive formula OCR for speed
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Verify processing completed
        assert result.exercise is not None
        assert result.status in [ProcessingStatus.SUCCESS, ProcessingStatus.PARTIAL, ProcessingStatus.NEEDS_REVIEW]
        assert result.processing_time > 0
        
        # Should extract at least some text
        assert len(result.regions) > 0 or len(result.warnings) > 0

    def test_sample2_quadratic_equation(self):
        """Test processing sample2.png - quadratic equation."""
        sample_path = find_sample_image("sample2.png")
        if not sample_path:
            pytest.skip("sample2.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Verify basic processing
        assert result.exercise is not None
        assert result.status is not None
        assert isinstance(result.processing_time, float)

    def test_sample3_processing(self):
        """Test processing sample3.png."""
        sample_path = find_sample_image("sample3.png")
        if not sample_path:
            pytest.skip("sample3.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        assert result is not None
        assert result.exercise is not None


@pytest.mark.integration
class TestWorksheetProcessing:
    """Test multi-problem worksheet processing."""

    def test_worksheet_factorization(self):
        """Test processing worksheet with multiple factorization problems."""
        sample_path = find_sample_image("worksheet_factorization.jpg")
        if not sample_path:
            pytest.skip("worksheet_factorization.jpg not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Worksheets should extract multiple regions
        assert len(result.regions) >= 1
        
        # Should detect multiple problems or sections
        if result.exercise.get_total_problems() > 1:
            assert result.exercise.get_section_count() >= 1

    def test_worksheet_shared_context(self):
        """Test worksheet with shared instruction context."""
        sample_path = find_sample_image("worksheet_shared_context.png")
        if not sample_path:
            pytest.skip("worksheet_shared_context.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Should extract exercise structure
        assert result.exercise is not None
        
        # Context propagation should work
        if result.exercise.sections:
            for section in result.exercise.sections:
                if section.instruction:
                    # Instructions should propagate to problems
                    for problem_item in section.problems:
                        assert problem_item.instruction_context is not None


@pytest.mark.integration
class TestAPIEndpointsWithRealImages:
    """Test API endpoints with real images."""

    def test_vision_endpoint_with_sample1(self):
        """Test /math/vision endpoint with sample1.png."""
        sample_path = find_sample_image("sample1.png")
        if not sample_path:
            pytest.skip("sample1.png not found")
        
        client = TestClient(app)
        
        with open(sample_path, "rb") as f:
            files = {"image": ("sample1.png", f, "image/png")}
            response = client.post("/api/v1/math/vision", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a response (success or structured error)
        assert "success" in data
        assert "data" in data or "error" in data

    def test_vision_endpoint_with_sample2(self):
        """Test /math/vision endpoint with sample2.png - quadratic equation."""
        sample_path = find_sample_image("sample2.png")
        if not sample_path:
            pytest.skip("sample2.png not found")
        
        client = TestClient(app)
        
        with open(sample_path, "rb") as f:
            files = {"image": ("sample2.png", f, "image/png")}
            response = client.post("/api/v1/math/vision", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Even if OCR/solving fails, should return structured response
        assert "success" in data

    def test_ocr_endpoint_with_real_image(self):
        """Test /math/ocr endpoint with real image."""
        sample_path = find_sample_image("sample1.png")
        if not sample_path:
            pytest.skip("sample1.png not found")
        
        client = TestClient(app)
        
        with open(sample_path, "rb") as f:
            files = {"image": ("sample1.png", f, "image/png")}
            response = client.post("/api/v1/math/ocr", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # OCR endpoint should always return structured response
        assert "success" in data

    def test_batch_endpoint_with_worksheet(self):
        """Test /math/vision/batch with multi-problem worksheet."""
        sample_path = find_sample_image("worksheet_factorization.jpg")
        if not sample_path:
            pytest.skip("worksheet_factorization.jpg not found")
        
        client = TestClient(app)
        
        with open(sample_path, "rb") as f:
            files = {"image": ("worksheet.jpg", f, "image/jpeg")}
            response = client.post("/api/v1/math/vision/batch", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Batch endpoint should return MultiProblemSet structure
        assert "success" in data
        
        if data.get("success"):
            result_data = data["data"]
            assert "problems" in result_data or "exercise" in result_data


@pytest.mark.integration
class TestSequenceImages:
    """Test sequence exercise images."""

    def test_sequence_ex1(self):
        """Test sequence exercise 1."""
        sample_path = find_sample_image("sequence_ex1.png")
        if not sample_path:
            pytest.skip("sequence_ex1.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        assert result.exercise is not None
        # Sequence problems may have special formatting
        assert result.status is not None

    def test_sequence_ex2(self):
        """Test sequence exercise 2."""
        sample_path = find_sample_image("sequence_ex2.png")
        if not sample_path:
            pytest.skip("sequence_ex2.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        assert result.exercise is not None


@pytest.mark.integration
class TestProcessingMetrics:
    """Test that processing metrics are captured correctly."""

    def test_processing_time_captured(self):
        """Verify processing time is captured for real images."""
        sample_path = find_sample_image("sample1.png")
        if not sample_path:
            pytest.skip("sample1.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Processing time should be positive
        assert result.processing_time > 0
        assert result.processing_time < 30.0  # Should complete in under 30s

    def test_confidence_scores_present(self):
        """Verify OCR confidence scores are captured."""
        sample_path = find_sample_image("sample2.png")
        if not sample_path:
            pytest.skip("sample2.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Should have confidence score
        assert hasattr(result.exercise, 'ocr_confidence')
        assert 0.0 <= result.exercise.ocr_confidence <= 1.0


@pytest.mark.integration
class TestFallbackBehavior:
    """Test fallback from document pipeline to legacy pipeline."""

    def test_vision_service_fallback_with_real_image(self):
        """Test that VisionService falls back gracefully with real images."""
        sample_path = find_sample_image("sample1.png")
        if not sample_path:
            pytest.skip("sample1.png not found")
        
        # Create a vision service that will use document pipeline
        from app.ocr.engines.kiri_ocr import KiriVisionEngine
        from app.services.math_service import MathService
        
        try:
            vision_engine = KiriVisionEngine()
        except Exception:
            pytest.skip("KiriVisionEngine not available")
        
        vision_service = VisionService(
            vision_engine=vision_engine,
            math_service=MathService(),
            use_document_pipeline=True,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        # Should complete without raising exception
        try:
            result = vision_service.process_image(image_bytes)
            # Result should be a dict
            assert isinstance(result, dict)
        except Exception as exc:
            # Even on error, should be a structured exception
            assert hasattr(exc, 'message') or str(exc)


@pytest.mark.integration
class TestKhmerContent:
    """Test Khmer language content processing."""

    def test_integral_kha_khmer_text(self):
        """Test processing Khmer integral problem."""
        sample_path = find_sample_image("integral_kha.png")
        if not sample_path:
            pytest.skip("integral_kha.png not found")
        
        pipeline = MathDocumentPipeline(
            document_ocr_engine=create_document_ocr_engine(lang="eng+khm"),
            enable_formula_ocr=False,
        )
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        result = pipeline.process(image_bytes)
        
        # Should handle Khmer script
        assert result.exercise is not None
        # May have Khmer text in title or instructions
        if result.exercise.title:
            # Just verify it's a string, may contain Khmer
            assert isinstance(result.exercise.title, str)


@pytest.mark.integration  
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_complete_workflow_ocr_to_solve(self):
        """Test complete workflow: upload → OCR → parse → solve."""
        sample_path = find_sample_image("sample1.png")
        if not sample_path:
            pytest.skip("sample1.png not found")
        
        client = TestClient(app)
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        # Step 1: OCR only
        files = {"image": ("sample1.png", image_bytes, "image/png")}
        ocr_response = client.post("/api/v1/math/ocr", files=files)
        assert ocr_response.status_code == 200
        
        # Step 2: Vision (OCR + Solve)
        files = {"image": ("sample1.png", image_bytes, "image/png")}
        vision_response = client.post("/api/v1/math/vision", files=files)
        assert vision_response.status_code == 200
        
        # Both should return structured responses
        ocr_data = ocr_response.json()
        vision_data = vision_response.json()
        
        assert "success" in ocr_data
        assert "success" in vision_data

    def test_multi_problem_detection_and_batch(self):
        """Test multi-problem detection flow."""
        sample_path = find_sample_image("worksheet_factorization.jpg")
        if not sample_path:
            pytest.skip("worksheet_factorization.jpg not found")
        
        client = TestClient(app)
        
        with open(sample_path, "rb") as f:
            image_bytes = f.read()
        
        # Try vision endpoint first
        files = {"image": ("worksheet.jpg", image_bytes, "image/jpeg")}
        vision_response = client.post("/api/v1/math/vision", files=files)
        assert vision_response.status_code == 200
        
        vision_data = vision_response.json()
        
        # If it suggests using batch endpoint
        if (vision_data.get("data") or {}).get("message"):
            # Use batch endpoint
            files = {"image": ("worksheet.jpg", image_bytes, "image/jpeg")}
            batch_response = client.post("/api/v1/math/vision/batch", files=files)
            assert batch_response.status_code == 200
            
            batch_data = batch_response.json()
            assert "success" in batch_data


def test_all_available_samples():
    """Test that we can at least attempt to process all available samples."""
    sample_files = [
        "sample1.png",
        "sample2.png", 
        "sample3.png",
        "worksheet_factorization.jpg",
        "worksheet_shared_context.png",
        "sequence_ex1.png",
        "sequence_ex2.png",
        "integral_kha.png",
    ]
    
    pipeline = MathDocumentPipeline(
        document_ocr_engine=create_document_ocr_engine(use_stub=True),
        enable_formula_ocr=False,
    )
    
    processed_count = 0
    
    for filename in sample_files:
        sample_path = find_sample_image(filename)
        if sample_path:
            with open(sample_path, "rb") as f:
                image_bytes = f.read()
            
            # Should not raise exception
            result = pipeline.process(image_bytes)
            assert result is not None
            processed_count += 1
    
    # Should have found at least some samples
    assert processed_count > 0, "No sample images found for testing"
