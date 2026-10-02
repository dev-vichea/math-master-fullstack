"""
Image preprocessing pipeline for math vision and OCR.

Enhances photos of printed or handwritten math exercises taken by phone
cameras or webcams before passing them to OCR engines (Tesseract, Kiri OCR).

Enhancements:
- EXIF orientation correction (phone camera portrait/landscape)
- Auto-rotation and deskewing for tilted images
- Perspective correction for angled shots
- Minimum dimension upscaling for small text/superscripts
- Multiple binarization methods (Otsu, adaptive Gaussian, Sauvola)
- Contrast Limited Adaptive Histogram Equalization (CLAHE)
- Edge-preserving denoising
- White margin padding to prevent edge text clipping
"""

from __future__ import annotations

import io
from typing import Literal

import cv2
import numpy as np
from PIL import Image, ImageOps


def _detect_and_deskew(image: np.ndarray) -> np.ndarray:
    """
    Detect skew angle and rotate image to straighten text.

    Uses Hough line transform to detect dominant text angles.
    """
    # Make a copy to avoid modifying original
    img_copy = image.copy()

    # Convert to grayscale if needed
    if len(img_copy.shape) == 3:
        gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_copy

    # Edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is None or len(lines) < 5:
        return image  # Not enough lines to determine skew

    # Calculate angles
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        # Normalize to [-45, 45] range
        if angle < -45:
            angle += 90
        elif angle > 45:
            angle -= 90
        angles.append(angle)

    # Find median angle
    median_angle = np.median(angles)

    # Only deskew if angle is significant (> 0.5 degrees)
    if abs(median_angle) < 0.5:
        return image

    # Rotate image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)

    # Determine border color (white for math documents)
    border_value = 255 if len(image.shape) == 2 else [255, 255, 255]

    rotated = cv2.warpAffine(
        image,
        rotation_matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )

    return rotated


def _detect_and_correct_perspective(image: np.ndarray) -> np.ndarray:
    """
    Detect and correct perspective distortion from angled camera shots.

    Attempts to find the largest rectangular contour (likely the document)
    and applies perspective transform to make it rectangular.
    """
    img_copy = image.copy()

    # Convert to grayscale if needed
    if len(img_copy.shape) == 3:
        gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_copy

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image

    # Sort by area, largest first
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    document_contour = None
    for contour in contours:
        # Approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # If 4 corners found, assume it's the document
        if len(approx) == 4:
            document_contour = approx
            break

    if document_contour is None:
        return image

    # Get the four corners
    pts = document_contour.reshape(4, 2)

    # Order points: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left
    rect[2] = pts[np.argmax(s)]  # Bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right
    rect[3] = pts[np.argmax(diff)]  # Bottom-left

    # Compute width and height
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # Construct destination points
    dst = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype="float32",
    )

    # Calculate perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)

    # Apply transform
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def _adaptive_binarize(
    gray_image: np.ndarray, method: Literal["otsu", "gaussian", "sauvola"] = "gaussian"
) -> np.ndarray:
    """
    Apply adaptive binarization to convert grayscale to black-and-white.

    Args:
        gray_image: Grayscale image
        method: Binarization method
            - 'otsu': Global Otsu thresholding
            - 'gaussian': Adaptive Gaussian thresholding (good for varying lighting)
            - 'sauvola': Sauvola local thresholding (best for handwriting)

    Returns:
        Binary image (black text on white background)
    """
    if method == "otsu":
        _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    elif method == "gaussian":
        binary = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=11, C=2
        )
        return binary

    elif method == "sauvola":
        # Sauvola thresholding (local adaptive, excellent for handwriting)
        # Implementation using sliding window
        window_size = 25
        k = 0.2
        R = 128

        # Pad image
        pad = window_size // 2
        padded = cv2.copyMakeBorder(gray_image, pad, pad, pad, pad, cv2.BORDER_REPLICATE)

        # Calculate local mean and std
        mean = cv2.boxFilter(padded, cv2.CV_32F, (window_size, window_size))
        mean_sq = cv2.boxFilter(
            padded.astype(np.float32) ** 2, cv2.CV_32F, (window_size, window_size)
        )
        std = np.sqrt(mean_sq - mean**2)

        # Crop to original size
        mean = mean[pad:-pad, pad:-pad]
        std = std[pad:-pad, pad:-pad]

        # Calculate threshold
        threshold = mean * (1 + k * ((std / R) - 1))

        # Apply threshold
        binary = np.where(gray_image > threshold, 255, 0).astype(np.uint8)

        return binary

    else:
        raise ValueError(f"Unknown binarization method: {method}")


def preprocess_image(
    image_bytes: bytes,
    mode: Literal[
        "enhanced_grayscale", "binary", "standard", "adaptive_binary"
    ] = "enhanced_grayscale",
    min_dimension: int = 800,
    add_padding: bool = True,
    pad_pixels: int = 25,
    auto_deskew: bool = False,
    auto_perspective: bool = False,
    binarization_method: Literal["otsu", "gaussian", "sauvola"] = "gaussian",
) -> bytes:
    """
    Preprocess raw image bytes for optimal OCR recognition.

    Args:
        image_bytes: Raw image file bytes (PNG, JPEG, WebP).
        mode:
            - 'enhanced_grayscale': Grayscale with CLAHE contrast & denoising (recommended for mixed/Khmer OCR)
            - 'binary': Otsu adaptive binarization (black text on pure white background)
            - 'standard': Orientation-corrected and contrast-boosted RGB
            - 'adaptive_binary': Advanced adaptive binarization with method selection
        min_dimension: Minimum size (in pixels) for the shorter side; upscaled if smaller.
        add_padding: Whether to add a clean white border around the image.
        pad_pixels: Thickness of white border in pixels.
        auto_deskew: Automatically detect and correct image rotation/skew.
        auto_perspective: Automatically detect and correct perspective distortion.
        binarization_method: Method for binary/adaptive_binary modes ('otsu', 'gaussian', 'sauvola').

    Returns:
        Processed image as PNG bytes.
    """
    if not image_bytes:
        return image_bytes

    # 1. Load via PIL to handle EXIF orientation properly
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        # Fallback if image cannot be parsed
        return image_bytes

    # Convert to RGB (dropping alpha channels if any)
    if pil_img.mode in ("RGBA", "LA", "P"):
        rgb_img = Image.new("RGB", pil_img.size, (255, 255, 255))
        if pil_img.mode == "RGBA":
            rgb_img.paste(pil_img, mask=pil_img.split()[3])
        elif pil_img.mode == "LA":
            rgb_img.paste(pil_img, mask=pil_img.split()[1])
        else:
            rgb_img.paste(pil_img.convert("RGB"))
        pil_img = rgb_img
    elif pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    width, height = pil_img.size

    # 2. Upscale if too small (superscripts like x² need sufficient resolution)
    shorter_side = min(width, height)
    if shorter_side < min_dimension and shorter_side > 0:
        scale_factor = min_dimension / shorter_side
        # Cap scaling to 3x to avoid excessive memory usage
        scale_factor = min(scale_factor, 3.0)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert PIL Image to OpenCV numpy array (BGR)
    img_np = np.array(pil_img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Apply perspective correction if requested (before other processing)
    if auto_perspective:
        try:
            img_bgr = _detect_and_correct_perspective(img_bgr)
        except Exception:
            pass  # If perspective correction fails, continue with original

    # Apply deskewing if requested
    if auto_deskew:
        try:
            img_bgr = _detect_and_deskew(img_bgr)
        except Exception:
            pass  # If deskew fails, continue with original

    # 3. Mode-specific OpenCV processing
    if mode == "standard":
        # Keep RGB with mild CLAHE on L-channel of LAB
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        final_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        result_img = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)

    elif mode == "adaptive_binary":
        # Advanced adaptive binarization
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Denoise first
        denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

        # Apply selected binarization method
        result_img = _adaptive_binarize(denoised, method=binarization_method)

    else:
        # Grayscale conversions (for "binary" and "enhanced_grayscale" modes)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Bilateral filter smooths noise while keeping text edges sharp
        denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

        # CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        if mode == "binary":
            # Otsu's automatic thresholding
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            result_img = binary
        else:
            result_img = enhanced

    # 4. Add white padding around borders
    if add_padding and pad_pixels > 0:
        if len(result_img.shape) == 2:
            result_img = cv2.copyMakeBorder(
                result_img,
                top=pad_pixels,
                bottom=pad_pixels,
                left=pad_pixels,
                right=pad_pixels,
                borderType=cv2.BORDER_CONSTANT,
                value=[255, 255, 255],
            )
        else:
            result_img = cv2.copyMakeBorder(
                result_img,
                top=pad_pixels,
                bottom=pad_pixels,
                left=pad_pixels,
                right=pad_pixels,
                borderType=cv2.BORDER_CONSTANT,
                value=[255, 255, 255],
            )

    # 5. Encode back to PNG bytes
    success, encoded_img = cv2.imencode(".png", result_img)
    if not success:
        return image_bytes

    return encoded_img.tobytes()
