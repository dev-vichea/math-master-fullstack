"""
Script to download real handwritten math images and labels from Hugging Face
(deepcopy/MathWriting-human) directly into your local training folder.

Usage:
    python scripts/download_hf_dataset.py --count 1000 --out data/handwriting
"""

import argparse
import csv
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm


def download_dataset(count: int, out_dir: Path, split: str = "train") -> None:
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.csv"

    print(f"Connecting to Hugging Face (deepcopy/MathWriting-human, split={split})...")
    # Stream dataset so you do not have to download all 10+ GB to disk
    ds = load_dataset("deepcopy/MathWriting-human", split=split, streaming=True)

    rows = []
    print(f"Downloading and saving {count} images to {images_dir}...")

    idx = 0
    pbar = tqdm(total=count, desc="Downloading")
    for sample in ds:
        img = sample.get("image")
        latex = sample.get("latex", "").strip()

        if not img or not latex:
            continue

        filename = f"{idx:06d}.png"
        img_path = images_dir / filename
        img.convert("RGB").save(img_path)

        rows.append({
            "image_path": f"images/{filename}",
            "text": latex,
            "sample_id": sample.get("sample_id", f"sample_{idx}"),
        })

        idx += 1
        pbar.update(1)

        if idx >= count:
            break

    pbar.close()

    # Save manifest.csv
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_path", "text", "sample_id"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Successfully saved {idx} images to {images_dir}")
    print(f"✅ Manifest written to {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=500, help="Number of images to download")
    parser.add_argument("--out", type=Path, default=Path("data/handwriting"), help="Output directory")
    parser.add_argument("--split", type=str, default="train", help="Dataset split (train, val, test)")
    args = parser.parse_args()

    download_dataset(args.count, args.out, args.split)


if __name__ == "__main__":
    main()
