"""
Fine-tuning script for pix2tex (LaTeX-OCR) ViT + ResNet model.

Runs locally (CPU / Apple Silicon MPS) or on Google Colab (CUDA GPU).
Loads pretrained official weights (~85MB) and fine-tunes on your math dataset.

Usage:
    python backend/training/pix2tex/finetune.py --config backend/training/pix2tex/config.yaml
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import torch
import yaml
from munch import Munch


def get_device(requested: str | None = None) -> torch.device:
    if requested:
        if requested == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        if requested == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        if requested == "cpu":
            return torch.device("cpu")

    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune pix2tex on custom math dataset")
    parser.add_argument(
        "--config",
        type=str,
        default="backend/training/pix2tex/config.yaml",
        help="Path to training config.yaml",
    )
    parser.add_argument("--epochs", type=int, default=None, help="Override number of epochs")
    parser.add_argument("--batchsize", type=int, default=None, help="Override batch size")
    parser.add_argument("--lr", type=float, default=None, help="Override learning rate")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda, mps, cpu)")
    args_cmd = parser.parse_args()

    config_path = Path(args_cmd.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    if args_cmd.epochs is not None:
        config_dict["epochs"] = args_cmd.epochs
    if args_cmd.batchsize is not None:
        config_dict["batchsize"] = args_cmd.batchsize
    if args_cmd.lr is not None:
        config_dict["lr"] = args_cmd.lr

    device = get_device(args_cmd.device or config_dict.get("device"))
    config_dict["device"] = str(device)
    config_dict["no_cuda"] = (device.type != "cuda")

    print(f"==================================================")
    print(f"  pix2tex (ViT + ResNet) Fine-Tuning Pipeline     ")
    print(f"==================================================")
    print(f"  Device:       {device}")
    print(f"  Epochs:       {config_dict.get('epochs')}")
    print(f"  Batch Size:   {config_dict.get('batchsize')}")
    print(f"  Learning Rate:{config_dict.get('lr')}")
    print(f"  Model Output: {config_dict.get('model_path')}")
    print(f"==================================================\n")

    os.makedirs(config_dict.get("model_path", "backend/training/pix2tex/models"), exist_ok=True)
    os.makedirs(config_dict.get("output_path", "backend/training/pix2tex/outputs"), exist_ok=True)

    # Convert dictionary to Munch object expected by pix2tex train module
    train_args = Munch(config_dict)

    try:
        from pix2tex.train import train
        print("Starting training session via pix2tex engine...")
        train(train_args)
        print("\nTraining completed successfully!")
        print(f"Checkpoints saved to: {config_dict.get('model_path')}")
    except ImportError as e:
        print(f"\nMissing training dependencies: {e}")
        print("Please install required dependencies:")
        print("  pip install -r backend/training/pix2tex/requirements.txt")
    except Exception as e:
        print(f"\nTraining encountered error: {e}")
        raise


if __name__ == "__main__":
    main()
