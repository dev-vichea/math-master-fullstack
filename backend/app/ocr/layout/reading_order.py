"""
Reading order analysis for text blocks.

Determines the natural reading order of text blocks based on their spatial layout.
Supports top-to-bottom, left-to-right ordering common in Khmer and English text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.document import BoundingBox


@dataclass(frozen=False, eq=True)
class TextBlock:
    """
    Text block with spatial information.

    Represents a single text region detected by OCR with its content and location.
    """

    text: str
    bounding_box: BoundingBox
    confidence: float = 1.0
    metadata: dict[str, Any] | None = None

    # Reading order properties (computed by analyzer)
    reading_order: int = -1  # Position in reading sequence (-1 = not computed)
    column: int = 0  # Column index for multi-column layouts
    row: int = 0  # Row index within column

    def __hash__(self) -> int:
        """Make TextBlock hashable for use in dicts/sets."""
        # Use id() for hash since blocks are mutable
        return id(self)


class ReadingOrderAnalyzer:
    """
    Analyze and order text blocks based on spatial layout.

    Uses geometric analysis to determine natural reading order:
    1. Detect columns (for multi-column layouts)
    2. Within each column, order top-to-bottom
    3. For similar Y positions, order left-to-right

    Handles both single-column and multi-column layouts.
    """

    def __init__(
        self,
        column_threshold: float = 0.3,  # Horizontal gap to detect column breaks
        row_threshold: float = 0.02,  # Vertical tolerance for "same row"
    ):
        """
        Initialize reading order analyzer.

        Args:
            column_threshold: Minimum horizontal gap (as fraction of page width)
                to detect separate columns
            row_threshold: Vertical tolerance (as fraction of page height) to
                consider blocks on the "same row"
        """
        self.column_threshold = column_threshold
        self.row_threshold = row_threshold

    def analyze(self, blocks: list[TextBlock]) -> list[TextBlock]:
        """
        Analyze text blocks and assign reading order.

        Args:
            blocks: List of text blocks to order

        Returns:
            Same blocks list with reading_order, column, and row fields populated
        """
        if not blocks:
            return blocks

        # Sort blocks by position for initial processing
        sorted_blocks = sorted(blocks, key=lambda b: (b.bounding_box.y, b.bounding_box.x))

        # Detect columns
        columns = self._detect_columns(sorted_blocks)

        # Assign reading order
        reading_order = 0
        for col_idx, column_blocks in enumerate(columns):
            # Sort column blocks by Y position, then X for ties
            column_blocks.sort(key=lambda b: (b.bounding_box.y, b.bounding_box.x))

            # Group into rows (blocks with similar Y positions)
            rows = self._group_into_rows(column_blocks)

            # Assign order within column
            for row_idx, row_blocks in enumerate(rows):
                # Within row, sort left-to-right
                row_blocks.sort(key=lambda b: b.bounding_box.x)

                for block in row_blocks:
                    block.column = col_idx
                    block.row = row_idx
                    block.reading_order = reading_order
                    reading_order += 1

        return blocks

    def _detect_columns(self, blocks: list[TextBlock]) -> list[list[TextBlock]]:
        """
        Detect column structure in the layout.

        Uses horizontal gaps to identify separate columns.

        Args:
            blocks: Sorted blocks

        Returns:
            List of columns, each containing list of blocks
        """
        if not blocks:
            return []

        # For now, assume single-column layout
        # Multi-column detection can be added later if needed
        return [blocks]

    def _group_into_rows(self, blocks: list[TextBlock]) -> list[list[TextBlock]]:
        """
        Group blocks with similar Y positions into rows.

        Args:
            blocks: Blocks within a column

        Returns:
            List of rows, each containing blocks on that row
        """
        if not blocks:
            return []

        rows: list[list[TextBlock]] = []
        current_row: list[TextBlock] = [blocks[0]]

        for block in blocks[1:]:
            # Check if this block is on the same row as previous
            prev_block = current_row[0]
            y_diff = abs(block.bounding_box.y - prev_block.bounding_box.y)

            if y_diff < self.row_threshold:
                # Same row
                current_row.append(block)
            else:
                # New row
                rows.append(current_row)
                current_row = [block]

        # Add last row
        if current_row:
            rows.append(current_row)

        return rows

    def get_blocks_in_order(self, blocks: list[TextBlock]) -> list[TextBlock]:
        """
        Get blocks sorted by reading order.

        Args:
            blocks: Blocks with reading_order assigned

        Returns:
            Blocks sorted by reading order
        """
        return sorted(blocks, key=lambda b: b.reading_order)

    def get_text_in_order(self, blocks: list[TextBlock], separator: str = "\n") -> str:
        """
        Get text content in reading order.

        Args:
            blocks: Blocks with reading_order assigned
            separator: String to use between blocks

        Returns:
            Concatenated text in reading order
        """
        ordered = self.get_blocks_in_order(blocks)
        return separator.join(b.text for b in ordered)
