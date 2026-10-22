"""
UniMERNet Vision Engine for Mathematical Expression Recognition.

Universal Network for Real-World Mathematical Expression Recognition (UniMERNet),
supporting complex printed and real-world handwritten expressions.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image

from app.ocr.engines.base import MathVisionEngine, VisionResult
from app.utils.logging import get_logger

logger = get_logger("app.ocr.engines.unimernet")

# Ensure internal unimernet module is importable
_OCR_DIR = str(Path(__file__).resolve().parent.parent)
if _OCR_DIR not in sys.path:
    sys.path.insert(0, _OCR_DIR)

try:
    import torch
    from unimernet.common.config import Config
    import unimernet.tasks as tasks
    from unimernet.processors import load_processor

    UNIMERNET_AVAILABLE = True
except ImportError as e:
    logger.warning("UniMERNet dependencies not fully available: %s", e)
    UNIMERNET_AVAILABLE = False


def clean_unimernet_output(latex_code: str) -> str:
    """Clean and normalize raw LaTeX output from UniMERNet."""
    if not latex_code:
        return ""

    t = latex_code.strip()

    # Normalize excessive internal spacing
    t = re.sub(r"[ \t]+", " ", t)

    # Clean up outer brackets or display markers if generated
    t = re.sub(r"^\\\[\s*", "", t)
    t = re.sub(r"\s*\\\]$", "", t)
    t = re.sub(r"^\$\$\s*", "", t)
    t = re.sub(r"\s*\$\$$", "", t)

    # Normalize TeX limit artifacts for parser compatibility
    t = re.sub(r"\\limits\b", "", t)
    t = re.sub(r"\\rightarrow\b", r"\\to", t)
    t = re.sub(r"\\operatorname\*?\s*\{\s*l\s*i\s*m\s*\}", r"\\lim", t)
    t = re.sub(r"^(?:[≈~]|\\approx\b)\s*", "", t)

    return t.strip()



class UniMERNetVisionEngine(MathVisionEngine):
    """
    In-process neural OCR engine powered by UniMERNet.
    
    Excels at handwritten expressions (HWE), complex formulas (CPE),
    screen captures (SCE), and printed expressions (SPE).
    """

    _instance = None  # Singleton pattern to prevent multiple 1.3GB model loads

    def __init__(
        self,
        config_path: str | Path | None = None,
        models_dir: str | Path | None = None,
        device: str | None = None,
    ):
        if not UNIMERNET_AVAILABLE:
            raise ImportError(
                "UniMERNet dependencies missing. Install: pip install torch transformers timm "
                "fairscale omegaconf ftfy iopath webdataset albumentations"
            )

        backend_dir = Path(__file__).resolve().parent.parent.parent.parent

        if config_path is None:
            config_path = (
                Path(__file__).resolve().parent.parent
                / "unimernet"
                / "configs"
                / "unimernet.yaml"
            )

        if models_dir is None:
            # Check local backend models directory first, fallback to external if needed
            local_models = backend_dir / "models" / "unimernet_base"
            if local_models.exists():
                models_dir = local_models
            else:
                models_dir = Path("/Users/kiddd/Development/UniMERNet/models/unimernet_base")

        self.models_dir = Path(models_dir)
        self.config_path = Path(config_path)

        if not self.models_dir.exists():
            raise FileNotFoundError(f"UniMERNet model directory not found: {self.models_dir}")

        # Device selection: Apple Silicon MPS -> CUDA -> CPU
        if device is None:
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        logger.info("Initializing UniMERNet engine on %s (model: %s)", self.device, self.models_dir)

        # Build configuration with dynamic paths
        pretrained_path = self.models_dir / "unimernet_base.pth"
        if not pretrained_path.exists():
            # Alternative weight name
            alt_path = self.models_dir / "pytorch_model.pth"
            if alt_path.exists():
                pretrained_path = alt_path

        opts = [
            f"model.model_config.model_name={self.models_dir}",
            f"model.pretrained={pretrained_path}",
            f"model.tokenizer_config.path={self.models_dir}",
        ]

        args = argparse.Namespace(cfg_path=str(self.config_path), options=opts)
        self.cfg = Config(args)
        task = tasks.setup_task(self.cfg)

        self.model = task.build_model(self.cfg).to(self.device)
        self.model.eval()

        self.vis_processor = load_processor(
            "formula_image_eval",
            self.cfg.config.datasets.formula_rec_eval.vis_processor.eval,
        )
        logger.info("UniMERNet engine ready.")

    def detect_image(self, pil_image: Image.Image) -> VisionResult:
        """Process PIL Image and return recognized LaTeX formula."""
        try:
            rgb_image = pil_image.convert("RGB")
            image_tensor = self.vis_processor(rgb_image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model.generate({"image": image_tensor})

            raw_latex = output["pred_str"][0] if output and "pred_str" in output else ""
            cleaned_latex = clean_unimernet_output(raw_latex)

            return VisionResult(
                detected_text=cleaned_latex,
                confidence=0.96 if cleaned_latex else 0.0,
                exercise_metadata={
                    "engine": "unimernet",
                    "device": str(self.device),
                    "model_dir": str(self.models_dir),
                    "raw_output": raw_latex,
                },
            )
        except Exception as e:
            logger.error("UniMERNet inference error: %s", e, exc_info=True)
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"UniMERNet error: {str(e)}",
            )

    def detect(self, image_bytes: bytes) -> VisionResult:
        """Standard MathVisionEngine interface method for raw image bytes."""
        try:
            image = Image.open(BytesIO(image_bytes))
            return self.detect_image(image)
        except Exception as e:
            logger.error("Failed to decode image bytes: %s", e)
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"Image decoding error: {str(e)}",
            )

    def detect_file(self, image_path: str | Path) -> VisionResult:
        """Recognize math from an image file path."""
        img_p = Path(image_path)
        if not img_p.exists():
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"File not found: {image_path}",
            )
        image = Image.open(img_p)
        return self.detect_image(image)
