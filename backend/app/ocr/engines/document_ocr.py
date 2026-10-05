"""
Document OCR Engine - Wrapper for extracting text with layout information.

This engine is specifically designed for full-page document OCR with spatial
layout extraction. Unlike formula OCR engines (Pix2Tex), this engine:
- Extracts text blocks with bounding boxes
- Preserves spatial layout and reading order
- Handles both Khmer and English text
- Is optimized for speed (not math precision)

Use this for Stage 1 of the document pipeline (layout extraction),
then use formula OCR engines for Stage 3 (selective math region enhancement).
"""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Any

from app.models.document import BoundingBox
from app.ocr.layout.reading_order import TextBlock

logger = logging.getLogger("app.ocr.engines.document_ocr")

try:
    import pytesseract
    from PIL import Image

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract not available for document OCR")


class DocumentOcrEngine:
    """
    Extract text blocks with bounding boxes from document images.
    
    This is a lightweight wrapper around Tesseract for document/text OCR.
    It returns structured TextBlock[] with spatial coordinates rather than
    just flat text.
    """

    def __init__(
        self,
        lang: str = "eng+khm",
        psm_mode: int | None = None,  # None = auto-detect
        use_preprocessing: bool = True,
    ):
        """
        Initialize document OCR engine.
        
        Args:
            lang: Tesseract language codes (e.g., "eng+khm" for English + Khmer)
            psm_mode: Page segmentation mode (None=auto-detect, 3=fully automatic, 
                     6=uniform block, 11=sparse text, 4=single column)
            use_preprocessing: Whether to preprocess images for better OCR
        """
        if not TESSERACT_AVAILABLE:
            logger.error("Tesseract not available - document OCR will fail")
            
        self.lang = lang
        self.psm_mode = psm_mode  # None means auto-detect
        self.use_preprocessing = use_preprocessing

    def extract_text_blocks(self, image_bytes: bytes) -> list[TextBlock]:
        """
        Extract text blocks with bounding boxes from an image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            List of TextBlock objects with text, bounding boxes, and confidence
        """
        if not TESSERACT_AVAILABLE:
            logger.error("Cannot extract text blocks: Tesseract not installed")
            return []

        if not image_bytes:
            logger.warning("Empty image bytes provided")
            return []

        try:
            # Preprocess if enabled
            if self.use_preprocessing:
                processed_bytes = self._preprocess_image(image_bytes)
            else:
                processed_bytes = image_bytes

            # Load image
            image = Image.open(BytesIO(processed_bytes))
            img_width, img_height = image.size
            
            # Auto-detect PSM mode if not specified
            psm_mode = self.psm_mode
            if psm_mode is None:
                psm_mode = self._detect_optimal_psm_mode(image)
                logger.debug(f"Auto-detected PSM mode: {psm_mode}")

            # Extract text with bounding box data
            config = f"--oem 3 --psm {psm_mode}"
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                config=config,
                output_type=pytesseract.Output.DICT,
            )

            # Build text blocks from Tesseract output
            text_blocks = self._build_text_blocks(data, img_width, img_height)
            
            logger.info(f"Extracted {len(text_blocks)} text blocks from document")
            return text_blocks

        except Exception as exc:
            logger.error(f"Failed to extract text blocks: {exc}", exc_info=True)
            return []
    
    def _detect_optimal_psm_mode(self, image: Image.Image) -> int:
        """
        Auto-detect optimal PSM mode based on image characteristics.
        
        Returns:
            PSM mode: 3 (fully auto), 4 (single column), 6 (uniform block), or 11 (sparse)
        """
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1.0
        
        # Convert to numpy for analysis if available
        try:
            import numpy as np
            img_array = np.array(image.convert('L'))
            
            # Calculate text density (rough estimate)
            threshold = 127
            text_pixels = np.sum(img_array < threshold)
            total_pixels = img_array.size
            text_density = text_pixels / total_pixels if total_pixels > 0 else 0
            
            # Decision logic
            if text_density < 0.05:
                # Sparse text - use sparse mode
                return 11
            elif aspect_ratio > 2.0 or aspect_ratio < 0.5:
                # Wide or tall - likely single column
                return 4
            elif 0.15 < text_density < 0.35:
                # Dense, structured text - uniform block
                return 6
            else:
                # Default - fully automatic
                return 3
                
        except ImportError:
            # No numpy - use aspect ratio only
            if aspect_ratio > 2.0 or aspect_ratio < 0.5:
                return 4
            else:
                return 3

    def _preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Preprocess image for better OCR results.
        
        Applies: grayscale, deskew, denoise, contrast enhancement.
        """
        try:
            from PIL import ImageEnhance, ImageFilter, ImageOps
            import numpy as np

            image = Image.open(BytesIO(image_bytes))
            
            # Convert to grayscale
            if image.mode != "L":
                image = image.convert("L")
            
            # Deskew (rotate to correct orientation)
            image = self._deskew_image(image)
            
            # Auto-level (improve contrast)
            image = ImageOps.autocontrast(image)
            
            # Additional contrast enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)
            
            # Sharpen slightly
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Denoise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Convert back to bytes
            output = BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()
            
        except Exception as exc:
            logger.warning(f"Image preprocessing failed, using original: {exc}")
            return image_bytes
    
    def _deskew_image(self, image: Image.Image) -> Image.Image:
        """
        Detect and correct image skew/rotation.
        
        Returns:
            Deskewed image
        """
        try:
            import numpy as np
            from scipy import ndimage
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Detect skew angle
            angle = self._detect_skew_angle(img_array)
            
            # Rotate if angle is significant (> 0.5 degrees)
            if abs(angle) > 0.5:
                logger.debug(f"Deskewing image by {angle:.2f} degrees")
                rotated = ndimage.rotate(img_array, angle, reshape=False, cval=255)
                return Image.fromarray(rotated.astype(np.uint8))
            
            return image
            
        except ImportError:
            # scipy not available - skip deskewing
            return image
        except Exception as exc:
            logger.debug(f"Deskew failed: {exc}")
            return image
    
    def _detect_skew_angle(self, image_array: Any) -> float:
        """
        Detect skew angle using projection profile method.
        
        Returns:
            Angle in degrees (positive = counter-clockwise)
        """
        try:
            import numpy as np
            
            # Binarize
            threshold = np.mean(image_array)
            binary = image_array < threshold
            
            # Try angles from -5 to +5 degrees
            angles = np.arange(-5.0, 5.0, 0.5)
            scores = []
            
            for angle in angles:
                # Rotate and sum columns
                from scipy import ndimage
                rotated = ndimage.rotate(binary, angle, reshape=False)
                col_sums = np.sum(rotated, axis=0)
                # Score is variance of column sums (higher = more aligned)
                score = np.var(col_sums)
                scores.append(score)
            
            # Best angle has highest score
            best_idx = np.argmax(scores)
            return angles[best_idx]
            
        except Exception:
            return 0.0

    def _build_text_blocks(
        self,
        tesseract_data: dict[str, Any],
        img_width: int,
        img_height: int,
    ) -> list[TextBlock]:
        """
        Build TextBlock objects from Tesseract's image_to_data output.
        
        Tesseract returns data at word level. We group words into lines
        based on their Y coordinates.
        """
        text_blocks: list[TextBlock] = []
        
        # Extract fields
        n_boxes = len(tesseract_data["text"])
        texts = tesseract_data["text"]
        lefts = tesseract_data["left"]
        tops = tesseract_data["top"]
        widths = tesseract_data["width"]
        heights = tesseract_data["height"]
        confs = tesseract_data["conf"]
        levels = tesseract_data["level"]  # 1=page, 2=block, 3=para, 4=line, 5=word

        # Group words into lines (level 4)
        current_line_words: list[dict[str, Any]] = []
        current_line_num = -1
        
        for i in range(n_boxes):
            level = levels[i]
            text = texts[i].strip()
            conf = confs[i]
            
            # Skip empty text or low-level elements
            if not text or conf == -1:
                continue
            
            # Tesseract provides hierarchical levels
            # We want to group at line level (level 4) or word level (level 5)
            left = lefts[i]
            top = tops[i]
            width = widths[i]
            height = heights[i]
            
            word_data = {
                "text": text,
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "conf": conf,
                "level": level,
            }
            
            # Group words that are close together vertically into lines
            # Using a threshold of 10 pixels for Y position difference
            if current_line_words and abs(top - current_line_words[0]["top"]) > 10:
                # Start new line
                if current_line_words:
                    line_block = self._merge_words_into_line(
                        current_line_words,
                        img_width,
                        img_height,
                    )
                    if line_block:
                        text_blocks.append(line_block)
                current_line_words = [word_data]
            else:
                current_line_words.append(word_data)

        # Add last line
        if current_line_words:
            line_block = self._merge_words_into_line(
                current_line_words,
                img_width,
                img_height,
            )
            if line_block:
                text_blocks.append(line_block)

        return text_blocks

    def _merge_words_into_line(
        self,
        words: list[dict[str, Any]],
        img_width: int,
        img_height: int,
    ) -> TextBlock | None:
        """Merge a list of word dictionaries into a single TextBlock (line)."""
        if not words:
            return None

        # Combine text with spaces
        text = " ".join(w["text"] for w in words)
        
        # Calculate bounding box that encompasses all words
        min_left = min(w["left"] for w in words)
        max_right = max(w["left"] + w["width"] for w in words)
        min_top = min(w["top"] for w in words)
        max_bottom = max(w["top"] + w["height"] for w in words)
        
        # Normalize to 0.0-1.0 range
        bbox = BoundingBox(
            x=min_left / img_width,
            y=min_top / img_height,
            width=(max_right - min_left) / img_width,
            height=(max_bottom - min_top) / img_height,
            page=0,
        )
        
        # Average confidence
        confidences = [w["conf"] for w in words if w["conf"] > 0]
        avg_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.85
        
        return TextBlock(
            text=text,
            bounding_box=bbox,
            confidence=avg_conf,
        )


class StubDocumentOcrEngine:
    """
    Stub document OCR engine for testing without Tesseract.
    
    Returns mock text blocks for development/testing.
    """

    def extract_text_blocks(self, image_bytes: bytes) -> list[TextBlock]:
        """Return stub text blocks for testing."""
        logger.warning("Using stub document OCR engine - no real OCR performed")
        
        # Create a simple stub text block
        stub_block = TextBlock(
            text="Stub OCR: No Tesseract available",
            bounding_box=BoundingBox(x=0.1, y=0.1, width=0.8, height=0.2, page=0),
            confidence=0.5,
        )
        
        return [stub_block]


def create_document_ocr_engine(
    lang: str = "eng+khm",
    use_stub: bool = False,
) -> DocumentOcrEngine | StubDocumentOcrEngine:
    """
    Factory function to create a document OCR engine.
    
    Args:
        lang: Language codes for Tesseract
        use_stub: Force use of stub engine (for testing)
        
    Returns:
        DocumentOcrEngine or StubDocumentOcrEngine
    """
    if use_stub or not TESSERACT_AVAILABLE:
        logger.warning("Creating stub document OCR engine")
        return StubDocumentOcrEngine()
    
    try:
        # Verify Tesseract is actually installed
        pytesseract.get_tesseract_version()
        logger.info(f"Creating document OCR engine with lang={lang}")
        return DocumentOcrEngine(lang=lang)
    except Exception as exc:
        logger.warning(f"Tesseract not available ({exc}), using stub engine")
        return StubDocumentOcrEngine()
