"""
Automatic Math-Image Preprocessor.

Generates multiple image variants for multi-candidate OCR without requiring
manual cropping from the user.
- Auto-trims surrounding margins while preserving a safe padding
- Detects and tightens bounding box around mathematical ink
- Generates contrast-enhanced and binarized variants
- Preserves the original image bytes untouched
"""

from __future__ import annotations

import io
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageOps


def auto_trim_math_region(img: Image.Image, margin: int = 15) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """
    Detects the ink bounding box of mathematical content and crops with a safe margin.
    Returns (cropped_pil_image, (x, y, w, h)).
    If no ink is found or image is uniform, returns original image and full bbox.
    """
    w, h = img.size
    gray = np.array(img.convert("L"))

    # Adaptive binarization to detect dark ink on light background
    # (or light chalk on dark blackboard)
    mean_val = np.mean(gray)
    if mean_val < 127:
        # Inverted image (white chalk on dark board)
        ink_mask = gray > 100
    else:
        # Normal paper (dark ink on light paper)
        ink_mask = gray < 210

    coords = np.argwhere(ink_mask)
    if coords.size == 0:
        return img, (0, 0, w, h)

    # coords gives [row, col] -> [y, x]
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    # Add safe margins
    x_min = max(0, int(x0) - margin)
    y_min = max(0, int(y0) - margin)
    x_max = min(w, int(x1) + margin)
    y_max = min(h, int(y1) + margin)

    crop_w = x_max - x_min
    crop_h = y_max - y_min

    # Ensure crop has minimum viable dimensions
    if crop_w < 20 or crop_h < 15:
        return img, (0, 0, w, h)

    cropped = img.crop((x_min, y_min, x_max, y_max))
    return cropped, (x_min, y_min, crop_w, crop_h)


def enhance_contrast(img: Image.Image) -> Image.Image:
    """Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) to improve ink visibility."""
    gray = np.array(img.convert("L"))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return Image.fromarray(enhanced)


def adaptive_threshold(img: Image.Image) -> Image.Image:
    """Applies adaptive Gaussian thresholding for clean black-and-white ink separation."""
    gray = np.array(img.convert("L"))
    # Otsu + Gaussian
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=15, C=4
    )
    return Image.fromarray(binary)


def pil_to_bytes(img: Image.Image, format: str = "PNG") -> bytes:
    """Converts a PIL image to bytes."""
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def generate_preprocessing_variants(image_bytes: bytes) -> list[dict[str, Any]]:
    """
    Produces multiple image preprocessing variants from raw bytes:
    1. "original": original unmodified image
    2. "trimmed": ink-tightened region with safe margin
    3. "contrast": contrast-enhanced ink (CLAHE)
    4. "adaptive_binary": binarized variant for high-contrast OCR

    Returns list of dicts with:
    - variant_name: str
    - image_bytes: bytes
    - pil_image: Image.Image
    - bounding_box: tuple | None
    """
    variants: list[dict[str, Any]] = []

    try:
        orig_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_pil = ImageOps.exif_transpose(orig_pil)
    except Exception:
        # If image cannot be read, return original bytes only
        return [{"variant_name": "original", "image_bytes": image_bytes, "pil_image": None, "bounding_box": None}]

    # 1. Original
    variants.append({
        "variant_name": "original",
        "image_bytes": image_bytes,
        "pil_image": orig_pil,
        "bounding_box": (0, 0, orig_pil.width, orig_pil.height),
    })

    # 2. Trimmed / Tightened
    try:
        trimmed_pil, bbox = auto_trim_math_region(orig_pil, margin=15)
        # Only add if noticeably different from original
        if (trimmed_pil.width, trimmed_pil.height) != (orig_pil.width, orig_pil.height):
            variants.append({
                "variant_name": "trimmed",
                "image_bytes": pil_to_bytes(trimmed_pil),
                "pil_image": trimmed_pil,
                "bounding_box": bbox,
            })
    except Exception:
        pass

    # 3. Contrast Enhanced
    try:
        contrast_pil = enhance_contrast(orig_pil)
        variants.append({
            "variant_name": "contrast",
            "image_bytes": pil_to_bytes(contrast_pil),
            "pil_image": contrast_pil,
            "bounding_box": (0, 0, orig_pil.width, orig_pil.height),
        })
    except Exception:
        pass

    # 4. Adaptive Binary
    try:
        binary_pil = adaptive_threshold(orig_pil)
        variants.append({
            "variant_name": "adaptive_binary",
            "image_bytes": pil_to_bytes(binary_pil),
            "pil_image": binary_pil,
            "bounding_box": (0, 0, orig_pil.width, orig_pil.height),
        })
    except Exception:
        pass

    return variants
