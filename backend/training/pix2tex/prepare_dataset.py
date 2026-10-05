"""
Dataset Preparation & Synthetic Formula Generator for pix2tex (LaTeX-OCR).

Generates high-quality mathematical formula images from Cambodian curriculum templates
(Algebra, Fractions, Radicals, Derivatives, Integrals, Limits, Trigonometry)
and formats them for pix2tex training.

Usage:
    python backend/training/pix2tex/prepare_dataset.py --count 1000 --out backend/training/pix2tex/data
"""

from __future__ import annotations

import argparse
import io
import math
import os
import random
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageOps


# Templates covering Grade 10-12 Cambodian Curriculum Math:
TEMPLATES = [
    # 1. Quadratic & Polynomial Equations
    r"{a}x^2 + {b}x + {c} = 0",
    r"{a}x^2 - {b}x - {c} = 0",
    r"x^2 - {b}x + {c} = 0",
    r"(x - {a})(x + {b}) = 0",
    r"2x^3 - 3x^2 + 4x - 5 = 0",

    # 2. Fractions & Rational Expressions
    r"\frac{{{a}x + {b}}}{{{c}}} = {d}",
    r"\frac{{{a}}}{{x + {b}}} + \frac{{{c}}}{{x - {d}}} = {e}",
    r"\frac{{x^2 - {a}}}{{x + {b}}}",
    r"\frac{{{a}x^2 + {b}x + {c}}}{{{d}x + {e}}}",

    # 3. Radicals / Square Roots
    r"\sqrt{{{a}x + {b}}} = {c}",
    r"\sqrt{{x^2 - {a}}} = {b}",
    r"x = \frac{{-{b} \pm \sqrt{{{b}^2 - 4({a})({c})}}}{{2({a})}}",
    r"\sqrt{{{a}}} + \sqrt{{{b}x}} = {c}",

    # 4. Limits
    r"\lim_{{x \to {a}}} \frac{{x^2 - {b}}}{{x - {c}}}",
    r"\lim_{{x \to 0}} \frac{{\sin({a}x)}}{{{a}x}} = 1",
    r"\lim_{{x \to \infty}} \frac{{{a}x^2 + {b}}}{{{c}x^2 - {d}}}",
    r"\lim_{{x \to {a}}} ({b}x^2 - {c}x + {d})",

    # 5. Integrals & Derivatives
    r"\int ({a}x^2 + {b}x + {c}) dx",
    r"\int_{{0}}^{{{a}}} ({b}x^2 - {c}x) dx",
    r"\int_{{1}}^{{{a}}} \frac{{1}}{{x}} dx",
    r"\frac{{d}}{{dx}} ({a}x^3 - {b}x^2 + {c}) = {d}x^2 - {e}x",
    r"f'(x) = {a}x + {b}",

    # 6. Trigonometry
    r"\sin^2 x + \cos^2 x = 1",
    r"\tan x = \frac{{\sin x}}{{\cos x}}",
    r"2\cos({a}x) - 1 = 0",
    r"\sin({a}x) = \frac{{\sqrt{{{b}}}}}{{2}}",

    # 7. Linear Systems & Simple Algebra
    r"{a}x + {b}y = {c}",
    r"3x - 5y = 12",
    r"y = {a}x + {b}",
]


def render_latex_to_image(latex_expr: str, dpi: int = 150) -> Image.Image:
    """Render LaTeX formula to a PIL Grayscale Image using Matplotlib Mathtext."""
    fig = plt.figure(figsize=(8, 2), dpi=dpi)
    math_text = f"${latex_expr}$"
    
    fig.text(0.5, 0.5, math_text, fontsize=20, ha="center", va="center")
    plt.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.15, transparent=False, facecolor="white")
    plt.close(fig)

    buf.seek(0)
    img = Image.open(buf).convert("L")
    
    # Invert to find tight bounding box
    inv = ImageOps.invert(img)
    bbox = inv.getbbox()
    if bbox:
        img = img.crop(bbox)
        # Pad with clean white border
        img = ImageOps.expand(img, border=12, fill=255)
    
    return img


def generate_sample_formula() -> str:
    """Generate a randomized formula from templates."""
    tmpl = random.choice(TEMPLATES)
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    d = random.randint(1, 9)
    e = random.randint(1, 9)
    return tmpl.format(a=a, b=b, c=c, d=d, e=e)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic LaTeX math dataset for pix2tex")
    parser.add_argument("--count", type=int, default=500, help="Number of formulas to generate")
    parser.add_argument("--out", type=str, default="backend/training/pix2tex/data", help="Output directory")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio")
    args = parser.parse_args()

    out_dir = Path(args.out)
    train_img_dir = out_dir / "train_images"
    val_img_dir = out_dir / "val_images"

    train_img_dir.mkdir(parents=True, exist_ok=True)
    val_img_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.count} synthetic formula images into {out_dir}...")

    formulas = [generate_sample_formula() for _ in range(args.count)]
    random.seed(42)
    random.shuffle(formulas)

    split_idx = int(len(formulas) * (1.0 - args.val_ratio))
    train_formulas = formulas[:split_idx]
    val_formulas = formulas[split_idx:]

    # Write train images (0.png, 1.png, ...) & train_equations.txt
    train_eq_file = out_dir / "train_equations.txt"
    with open(train_eq_file, "w", encoding="utf-8") as f:
        for i, formula in enumerate(train_formulas):
            f.write(f"{formula}\n")
            img = render_latex_to_image(formula)
            img.save(train_img_dir / f"{i}.png")
            if (i + 1) % 50 == 0:
                print(f"  [Train: {i+1}/{len(train_formulas)}] rendered {i}.png")

    # Write val images (0.png, 1.png, ...) & val_equations.txt
    val_eq_file = out_dir / "val_equations.txt"
    with open(val_eq_file, "w", encoding="utf-8") as f:
        for i, formula in enumerate(val_formulas):
            f.write(f"{formula}\n")
            img = render_latex_to_image(formula)
            img.save(val_img_dir / f"{i}.png")

    print("\nDataset generation complete!")
    print(f"  Train: {len(train_formulas)} images in {train_img_dir} (equations: {train_eq_file})")
    print(f"  Val:   {len(val_formulas)} images in {val_img_dir} (equations: {val_eq_file})")

    # Compile pkl if pix2tex is available
    try:
        from pix2tex.dataset.dataset import Im2LatexDataset
        from pix2tex.utils import in_model_path

        tok_path = in_model_path("dataset/tokenizer.json")
        print("\nCompiling into pix2tex binary dataset (.pkl)...")
        train_ds = Im2LatexDataset(equations=str(train_eq_file), images=str(train_img_dir), tokenizer=tok_path)
        train_ds.save(str(out_dir / "train.pkl"))

        val_ds = Im2LatexDataset(equations=str(val_eq_file), images=str(val_img_dir), tokenizer=tok_path)
        val_ds.save(str(out_dir / "val.pkl"))

        print(f"Successfully compiled:")
        print(f"  - {out_dir / 'train.pkl'}")
        print(f"  - {out_dir / 'val.pkl'}")
    except Exception as exc:
        print(f"Note: Could not automatically compile .pkl ({exc}).")
        print("Run `python -m pix2tex.dataset.dataset` after installing pix2tex[train].")


if __name__ == "__main__":
    main()
