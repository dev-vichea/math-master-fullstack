"""
Fine-tuning script for pix2tex (LaTeX-OCR) ViT + ResNet model.

Runs locally (CPU / Apple Silicon MPS) or on Google Colab (CUDA GPU).
Loads pretrained official weights (~85MB) and fine-tunes on your math dataset.

Usage:
    python backend/training/pix2tex/finetune.py --config backend/training/pix2tex/config.yaml
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
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
        default=None,
        help="Path to training config.yaml",
    )
    parser.add_argument("--epochs", type=int, default=None, help="Override number of epochs")
    parser.add_argument("--batchsize", type=int, default=None, help="Override batch size")
    parser.add_argument("--lr", type=float, default=None, help="Override learning rate")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda, mps, cpu)")
    args_cmd = parser.parse_args()

    default_config = Path(__file__).resolve().parent / "config.yaml"
    config_path = Path(args_cmd.config) if args_cmd.config else default_config
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    base_dir = config_path.parent.resolve()

    with open(config_path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    # Resolve paths relative to base_dir if not absolute
    for p_key, default_rel in [
        ("data", "data/train.pkl"),
        ("valdata", "data/val.pkl"),
        ("model_path", "models"),
        ("output_path", "outputs"),
    ]:
        val = config_dict.get(p_key, default_rel)
        p = Path(val)
        if not p.is_absolute():
            p = (base_dir / default_rel).resolve()
        config_dict[p_key] = str(p)

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
    print(f"  Train Data:   {config_dict.get('data')}")
    print(f"  Val Data:     {config_dict.get('valdata')}")
    print(f"  Model Output: {config_dict.get('model_path')}")
    print(f"==================================================\n")

    os.makedirs(config_dict["model_path"], exist_ok=True)
    os.makedirs(config_dict["output_path"], exist_ok=True)

    try:
        from pix2tex.utils import parse_args, in_model_path
        from pix2tex.train import train

        # Load official defaults first so all parameters (pad_token, etc.) are present
        with in_model_path():
            with open("settings/config.yaml", "r") as f:
                base_params = yaml.load(f, Loader=yaml.FullLoader)
            default_chkpt = os.path.realpath("checkpoints/weights.pth")

        merged_params = Munch(base_params)
        merged_params.update(config_dict)
        train_args = parse_args(merged_params)
        train_args.device = str(device)
        train_args.no_cuda = (device.type != "cuda")
        train_args.wandb = False  # Disable wandb for local runs

        # Automatically start from official pretrained weights (~85MB) if no checkpoint specified
        if not train_args.load_chkpt and os.path.exists(default_chkpt):
            train_args.load_chkpt = default_chkpt
            print(f"Fine-tuning from base pretrained weights: {default_chkpt}")

        print("Starting training session via pix2tex engine...")
        train(train_args)
        print("\nTraining completed successfully!")

        # Sync latest checkpoint to weights.pth for backend inference
        run_name = config_dict.get("name", "pix2tex_khmer_math")
        checkpoints_dir = Path(config_dict["model_path"]) / run_name
        saved_pths = sorted(checkpoints_dir.glob(f"{run_name}_e*.pth"))
        if saved_pths:
            latest_ckpt = saved_pths[-1]
            dest_weights = Path(config_dict["model_path"]) / "weights.pth"
            shutil.copyfile(latest_ckpt, dest_weights)
            print(f"\nSynced latest checkpoint to active weights:")
            print(f"  Source: {latest_ckpt}")
            print(f"  Active: {dest_weights} ({os.path.getsize(dest_weights) / (1024*1024):.1f} MB)")

        print(f"Checkpoints directory: {checkpoints_dir}")

    except ImportError as e:
        print(f"\nMissing training dependencies: {e}")
        print("Please install required dependencies:")
        print("  pip install -r backend/training/pix2tex/requirements.txt")
    except Exception as e:
        print(f"\nTraining encountered error: {e}")
        raise


if __name__ == "__main__":
    main()
