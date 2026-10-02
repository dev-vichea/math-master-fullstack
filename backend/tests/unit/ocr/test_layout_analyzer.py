"""
Tests for layout analysis module.

Tests reading order analysis, region classification, and spatial clustering.
"""

import pytest

from app.models.document import BoundingBox
from app.ocr.layout import ReadingOrderAnalyzer, RegionClassifier, RegionType, SpatialClusterer
from app.ocr.layout.reading_order import TextBlock


class TestReadingOrderAnalyzer:
    """Test reading order analysis."""

    def test_basic_top_to_bottom_order(self):
        """Test basic top-to-bottom reading order."""
        analyzer = ReadingOrderAnalyzer()

        blocks = [
            TextBlock(text="Third", bounding_box=BoundingBox(x=0.1, y=0.6, width=0.2, height=0.05)),
            TextBlock(text="First", bounding_box=BoundingBox(x=0.1, y=0.1, width=0.2, height=0.05)),
            TextBlock(text="Second", bounding_box=BoundingBox(x=0.1, y=0.3, width=0.2, height=0.05)),
        ]

        analyzer.analyze(blocks)

        assert blocks[0].reading_order == 2  # "Third" is third
        assert blocks[1].reading_order == 0  # "First" is first
        assert blocks[2].reading_order == 1  # "Second" is second

    def test_left_to_right_same_row(self):
        """Test left-to-right ordering within same row."""
        analyzer = ReadingOrderAnalyzer(row_threshold=0.02)

        blocks = [
            TextBlock(text="Right", bounding_box=BoundingBox(x=0.6, y=0.1, width=0.2, height=0.05)),
            TextBlock(text="Left", bounding_box=BoundingBox(x=0.1, y=0.1, width=0.2, height=0.05)),
            TextBlock(text="Middle", bounding_box=BoundingBox(x=0.35, y=0.105, width=0.2, height=0.05)),
        ]

        analyzer.analyze(blocks)

        assert blocks[0].reading_order == 2  # "Right" is third
        assert blocks[1].reading_order == 0  # "Left" is first
        assert blocks[2].reading_order == 1  # "Middle" is second

    def test_get_text_in_order(self):
        """Test getting text content in reading order."""
        analyzer = ReadingOrderAnalyzer()

        blocks = [
            TextBlock(text="ចូរដាក់ជាកត្តាកត់", bounding_box=BoundingBox(x=0.1, y=0.1, width=0.5, height=0.05)),
            TextBlock(text="ក. x² - 4", bounding_box=BoundingBox(x=0.1, y=0.2, width=0.3, height=0.05)),
            TextBlock(text="ខ. x² - 5x + 6", bounding_box=BoundingBox(x=0.1, y=0.3, width=0.4, height=0.05)),
        ]

        analyzer.analyze(blocks)
        text = analyzer.get_text_in_order(blocks)

        assert "ចូរដាក់ជាកត្តាកត់" in text
        assert text.index("ចូរដាក់ជាកត្តាកត់") < text.index("ក. x² - 4")
        assert text.index("ក. x² - 4") < text.index("ខ. x² - 5x + 6")


class TestRegionClassifier:
    """Test region classification."""

    def test_problem_label_khmer(self):
        """Test Khmer problem label detection."""
        classifier = RegionClassifier()

        # Test Khmer labels
        assert classifier._is_problem_label("ក។")
        assert classifier._is_problem_label("ខ.")
        assert classifier._is_problem_label("គ)")

    def test_problem_label_latin(self):
        """Test Latin problem label detection."""
        classifier = RegionClassifier()

        # Test Latin labels
        assert classifier._is_problem_label("a)")
        assert classifier._is_problem_label("b.")
        assert classifier._is_problem_label("A)")
        assert classifier._is_problem_label("B.")

    def test_problem_label_numeric(self):
        """Test numeric problem label detection."""
        classifier = RegionClassifier()

        # Test numeric labels
        assert classifier._is_problem_label("1)")
        assert classifier._is_problem_label("2.")
        assert classifier._is_problem_label("10)")

    def test_instruction_detection_khmer(self):
        """Test Khmer instruction detection."""
        classifier = RegionClassifier()

        # Test Khmer instructions
        assert classifier._is_instruction("ចូរដាក់ជាកត្តាកត់")
        assert classifier._is_instruction("ដោះស្រាយសមីការខាងក្រោម")
        assert classifier._is_instruction("គណនាតម្លៃ")
        assert classifier._is_instruction("ចូររកតម្លៃ x")

    def test_instruction_detection_english(self):
        """Test English instruction detection."""
        classifier = RegionClassifier()

        # Test English instructions
        assert classifier._is_instruction("Solve the following equations")
        assert classifier._is_instruction("Factor the polynomials")
        assert classifier._is_instruction("Calculate the value")
        assert classifier._is_instruction("Find x")

    def test_math_content_detection(self):
        """Test mathematical content detection."""
        classifier = RegionClassifier()

        # Test math expressions
        assert classifier._is_math_content("x² - 4")
        assert classifier._is_math_content("2x + 5 = 11")
        assert classifier._is_math_content("3x² - 9x + x³")
        assert classifier._is_math_content("x² - 5x + 6 = 0")

        # Test non-math content
        assert not classifier._is_math_content("ចូរដាក់ជាកត្តាកត់")
        assert not classifier._is_math_content("Solve the equation")

    def test_extract_label(self):
        """Test label extraction from text."""
        classifier = RegionClassifier()

        # Test label extraction
        assert classifier.extract_label("ក។") == "ក។"
        assert classifier.extract_label("a)") == "a)"
        assert classifier.extract_label("1.") == "1."
        assert classifier.extract_label("ខ. x² - 4") == "ខ."

    def test_classify_full_workflow(self):
        """Test full classification workflow."""
        classifier = RegionClassifier()

        # Instruction
        block1 = TextBlock(
            text="ចូរដាក់ជាកត្តាកត់",
            bounding_box=BoundingBox(x=0.1, y=0.1, width=0.5, height=0.05),
        )
        assert classifier.classify(block1) == RegionType.INSTRUCTION

        # Problem label
        block2 = TextBlock(
            text="ក.",
            bounding_box=BoundingBox(x=0.1, y=0.2, width=0.05, height=0.05),
        )
        assert classifier.classify(block2) == RegionType.PROBLEM_LABEL

        # Math content
        block3 = TextBlock(
            text="x² - 4",
            bounding_box=BoundingBox(x=0.2, y=0.2, width=0.3, height=0.05),
        )
        assert classifier.classify(block3) == RegionType.PROBLEM_CONTENT


class TestSpatialClusterer:
    """Test spatial clustering."""

    def test_is_spatially_close(self):
        """Test spatial proximity detection."""
        clusterer = SpatialClusterer(horizontal_threshold=0.1, vertical_threshold=0.05)

        # Adjacent blocks (should be close)
        block1 = TextBlock(
            text="ក.",
            bounding_box=BoundingBox(x=0.1, y=0.2, width=0.05, height=0.05),
        )
        block2 = TextBlock(
            text="x² - 4",
            bounding_box=BoundingBox(x=0.16, y=0.2, width=0.3, height=0.05),
        )

        assert clusterer._is_spatially_close(block1, block2)

        # Distant blocks (should not be close)
        block3 = TextBlock(
            text="ខ. x² - 5x + 6",
            bounding_box=BoundingBox(x=0.1, y=0.5, width=0.4, height=0.05),
        )

        assert not clusterer._is_spatially_close(block1, block3)

    def test_cluster_problems(self):
        """Test clustering problem labels with content."""
        clusterer = SpatialClusterer(horizontal_threshold=0.1, vertical_threshold=0.05)
        classifier = RegionClassifier()

        blocks = [
            TextBlock(text="ក.", bounding_box=BoundingBox(x=0.1, y=0.2, width=0.05, height=0.05)),
            TextBlock(text="x² - 4", bounding_box=BoundingBox(x=0.16, y=0.2, width=0.3, height=0.05)),
            TextBlock(text="ខ.", bounding_box=BoundingBox(x=0.1, y=0.3, width=0.05, height=0.05)),
            TextBlock(text="x² - 5x + 6", bounding_box=BoundingBox(x=0.16, y=0.3, width=0.4, height=0.05)),
        ]

        # Classify blocks
        region_types = {block: classifier.classify(block) for block in blocks}

        # Cluster
        clusters = clusterer.cluster_problems(blocks, region_types)

        assert len(clusters) == 2
        assert len(clusters[0].blocks) == 2  # Label + content
        assert len(clusters[1].blocks) == 2  # Label + content
        assert "ក." in clusters[0].get_text()
        assert "x² - 4" in clusters[0].get_text()
        assert "ខ." in clusters[1].get_text()
        assert "x² - 5x + 6" in clusters[1].get_text()

    def test_merge_inline_blocks(self):
        """Test merging blocks on same line."""
        clusterer = SpatialClusterer()
        classifier = RegionClassifier()

        blocks = [
            TextBlock(text="ក.", bounding_box=BoundingBox(x=0.1, y=0.2, width=0.05, height=0.05)),
            TextBlock(text="x² - 4", bounding_box=BoundingBox(x=0.16, y=0.2, width=0.3, height=0.05)),
        ]

        region_types = {block: classifier.classify(block) for block in blocks}
        merged = clusterer.merge_inline_blocks(blocks, region_types)

        assert len(merged) == 1
        assert "ក." in merged[0].text
        assert "x² - 4" in merged[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
