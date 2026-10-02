"""
Spatial clustering for grouping related text blocks.

Groups text blocks that are spatially close and semantically related,
such as a problem label (a)) with its mathematical expression.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.document import BoundingBox
from app.ocr.layout.reading_order import TextBlock
from app.ocr.layout.region_classifier import RegionType


@dataclass
class BlockCluster:
    """
    Cluster of related text blocks.

    Represents a group of spatially and semantically related blocks,
    such as a problem label + expression, or an instruction + its problems.
    """

    blocks: list[TextBlock]
    cluster_type: str  # "problem", "section", "header"
    bounding_box: BoundingBox | None = None

    def get_text(self, separator: str = " ") -> str:
        """Get concatenated text from all blocks."""
        return separator.join(b.text for b in self.blocks)

    def compute_bounding_box(self) -> BoundingBox:
        """Compute bounding box that encompasses all blocks."""
        if not self.blocks:
            return BoundingBox(x=0, y=0, width=0, height=0)

        # Find min/max coordinates
        min_x = min(b.bounding_box.x for b in self.blocks)
        min_y = min(b.bounding_box.y for b in self.blocks)
        max_x = max(b.bounding_box.x + b.bounding_box.width for b in self.blocks)
        max_y = max(b.bounding_box.y + b.bounding_box.height for b in self.blocks)

        self.bounding_box = BoundingBox(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )
        return self.bounding_box


class SpatialClusterer:
    """
    Cluster text blocks based on spatial proximity and semantic relationships.

    Uses distance thresholds and region types to group related blocks:
    - Problem labels with their expressions
    - Instructions with their problem groups
    - Headers with metadata
    """

    def __init__(
        self,
        horizontal_threshold: float = 0.1,  # Max horizontal distance to cluster
        vertical_threshold: float = 0.05,  # Max vertical distance to cluster
    ):
        """
        Initialize spatial clusterer.

        Args:
            horizontal_threshold: Maximum horizontal distance (as fraction of page width)
                to consider blocks as related
            vertical_threshold: Maximum vertical distance (as fraction of page height)
                to consider blocks as related
        """
        self.horizontal_threshold = horizontal_threshold
        self.vertical_threshold = vertical_threshold

    def cluster_problems(
        self,
        blocks: list[TextBlock],
        region_types: dict[TextBlock, RegionType],
    ) -> list[BlockCluster]:
        """
        Cluster problem labels with their content.

        Args:
            blocks: Text blocks in reading order
            region_types: Mapping of blocks to their region types

        Returns:
            List of problem clusters (label + content)
        """
        clusters: list[BlockCluster] = []
        i = 0

        while i < len(blocks):
            block = blocks[i]
            region_type = region_types.get(block, RegionType.UNKNOWN)

            # Look for problem labels
            if region_type == RegionType.PROBLEM_LABEL:
                # Try to find associated content
                cluster_blocks = [block]

                # Check next blocks for content
                j = i + 1
                while j < len(blocks):
                    next_block = blocks[j]
                    next_type = region_types.get(next_block, RegionType.UNKNOWN)

                    # Stop if we hit another label or instruction
                    if next_type in (RegionType.PROBLEM_LABEL, RegionType.INSTRUCTION):
                        break

                    # Check spatial proximity
                    if self._is_spatially_close(block, next_block):
                        if next_type == RegionType.PROBLEM_CONTENT:
                            cluster_blocks.append(next_block)
                            j += 1
                        else:
                            j += 1
                            continue
                    else:
                        break

                # Create cluster
                cluster = BlockCluster(blocks=cluster_blocks, cluster_type="problem")
                cluster.compute_bounding_box()
                clusters.append(cluster)
                i = j
            else:
                i += 1

        return clusters

    def cluster_sections(
        self,
        blocks: list[TextBlock],
        region_types: dict[TextBlock, RegionType],
    ) -> list[BlockCluster]:
        """
        Cluster instructions with their problem groups.

        Args:
            blocks: Text blocks in reading order
            region_types: Mapping of blocks to their region types

        Returns:
            List of section clusters (instruction + problems)
        """
        clusters: list[BlockCluster] = []
        i = 0

        while i < len(blocks):
            block = blocks[i]
            region_type = region_types.get(block, RegionType.UNKNOWN)

            # Look for instructions
            if region_type == RegionType.INSTRUCTION:
                cluster_blocks = [block]

                # Collect all following blocks until next instruction
                j = i + 1
                while j < len(blocks):
                    next_block = blocks[j]
                    next_type = region_types.get(next_block, RegionType.UNKNOWN)

                    # Stop at next instruction
                    if next_type == RegionType.INSTRUCTION:
                        break

                    # Add relevant blocks
                    if next_type in (
                        RegionType.PROBLEM_LABEL,
                        RegionType.PROBLEM_CONTENT,
                        RegionType.PROBLEM,
                    ):
                        cluster_blocks.append(next_block)

                    j += 1

                # Create cluster
                cluster = BlockCluster(blocks=cluster_blocks, cluster_type="section")
                cluster.compute_bounding_box()
                clusters.append(cluster)
                i = j
            else:
                i += 1

        return clusters

    def _is_spatially_close(self, block1: TextBlock, block2: TextBlock) -> bool:
        """
        Check if two blocks are spatially close enough to be related.

        Args:
            block1: First block
            block2: Second block

        Returns:
            True if blocks are close enough to be clustered
        """
        bb1 = block1.bounding_box
        bb2 = block2.bounding_box

        # Calculate horizontal distance (gap between blocks)
        if bb1.x + bb1.width < bb2.x:
            # block2 is to the right
            h_distance = bb2.x - (bb1.x + bb1.width)
        elif bb2.x + bb2.width < bb1.x:
            # block1 is to the right
            h_distance = bb1.x - (bb2.x + bb2.width)
        else:
            # Blocks overlap horizontally
            h_distance = 0

        # Calculate vertical distance (gap between blocks)
        if bb1.y + bb1.height < bb2.y:
            # block2 is below
            v_distance = bb2.y - (bb1.y + bb1.height)
        elif bb2.y + bb2.height < bb1.y:
            # block1 is below
            v_distance = bb1.y - (bb2.y + bb2.height)
        else:
            # Blocks overlap vertically
            v_distance = 0

        # Check if within thresholds
        return h_distance <= self.horizontal_threshold and v_distance <= self.vertical_threshold

    def merge_inline_blocks(
        self,
        blocks: list[TextBlock],
        region_types: dict[TextBlock, RegionType],
    ) -> list[TextBlock]:
        """
        Merge blocks that appear on the same line.

        Useful for combining a problem label like "a)" with its expression "x² - 4"
        when they appear on the same line.

        Args:
            blocks: Text blocks in reading order
            region_types: Mapping of blocks to their region types

        Returns:
            List of merged blocks
        """
        if not blocks:
            return []

        merged: list[TextBlock] = []
        current_group: list[TextBlock] = [blocks[0]]

        for block in blocks[1:]:
            prev_block = current_group[-1]

            # Check if on same line (similar Y position)
            y_diff = abs(block.bounding_box.y - prev_block.bounding_box.y)

            if y_diff < 0.01 and self._is_spatially_close(prev_block, block):
                # Same line, merge
                current_group.append(block)
            else:
                # New line, finalize previous group
                merged.append(self._merge_block_group(current_group, region_types))
                current_group = [block]

        # Add last group
        if current_group:
            merged.append(self._merge_block_group(current_group, region_types))

        return merged

    def _merge_block_group(
        self,
        blocks: list[TextBlock],
        region_types: dict[TextBlock, RegionType],
    ) -> TextBlock:
        """Merge multiple blocks into one."""
        if len(blocks) == 1:
            return blocks[0]

        # Combine text
        combined_text = " ".join(b.text for b in blocks)

        # Compute combined bounding box
        min_x = min(b.bounding_box.x for b in blocks)
        min_y = min(b.bounding_box.y for b in blocks)
        max_x = max(b.bounding_box.x + b.bounding_box.width for b in blocks)
        max_y = max(b.bounding_box.y + b.bounding_box.height for b in blocks)

        combined_bbox = BoundingBox(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )

        # Average confidence
        avg_confidence = sum(b.confidence for b in blocks) / len(blocks)

        # Merge metadata
        combined_metadata = {}
        for block in blocks:
            if block.metadata:
                combined_metadata.update(block.metadata)

        return TextBlock(
            text=combined_text,
            bounding_box=combined_bbox,
            confidence=avg_confidence,
            metadata=combined_metadata if combined_metadata else None,
        )
