"""
Generates synthetic images of math expressions + a manifest mapping each
image to its ground-truth text. This is Phase B, step 1 of the Math Vision
training plan: it gets you thousands of labeled (image, text) pairs for
free, to bootstrap a fine-tune before you invest time collecting and
labeling real handwritten photos.

WHY THIS EXISTS: training an OCR model needs paired (image, correct_text)
examples. Real ones are slow and expensive to collect. Rendering the text
yourself as an image is a very standard way to get a first working dataset.

WHAT IT DOES, IN PLAIN TERMS:
  1. Randomly builds a simple math expression as a string, e.g. "2x+5=15".
  2. Draws it onto an image using a random font, size, position, and a bit
     of rotation/noise, to imitate the variation real photos have.
  3. Saves the image + writes a manifest.csv row: (filename, ground_truth).

You do NOT need to understand machine learning to run this file. You just
need Python and Pillow installed:

    pip install pillow

Then:

    python training/generate_synthetic_data.py --count 2000 --out training/data

That's it — Phase B step 1 is generating usable training data by running
one command.
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# 1. Expression generation: build random, valid-looking math expressions.
#    Kept intentionally simple and aligned with what your backend's
#    expression_parser.py already understands (implicit multiplication,
#    '^' for powers) — there's no point generating training data your
#    parser downstream can't consume anyway.
# ---------------------------------------------------------------------------

_TEMPLATES = [
    # Basic linear equations
    "{a}x + {b} = {c}",
    "{a}x - {b} = {c}",
    "{a}x = {b}",
    "x + {a} = {b}",
    "x - {a} = {b}",
    # Variables on both sides
    "{a}x + {b} = {c}x + {d}",
    "{a}x - {b} = {c}x + {d}",
    # Basic arithmetic
    "{a} + {b} = {c}",
    "{a} - {b} = {c}",
    "{a} * {b} = {c}",
    "{a}/{b} + {c} = {d}",
    # Fraction addition/subtraction (NEW)
    "{a}/{b} + {c}/{d}",
    "{a}/{b} - {c}/{d}",
    "{a}/{b} + {c}",
    "{small}/{big} + {small2}/{big2}",
    # Fraction multiplication/division (NEW)
    "{a}/{b} * {c}/{d}",
    "({a}/{b}) / ({c}/{d})",
    # Percentage expressions (NEW)
    "{pct}% of {n}",
    "{pct}% + {pct2}%",
    # Quadratic equations (NEW)
    "x^2 + {b}x + {c} = 0",
    "x^2 - {b}x + {c} = 0",
    "{a}x^2 + {b}x = {c}",
    "{a}x^2 + {b}x + {c} = 0",
    "x^2 = {a}",
    # Mixed operations (NEW)
    "{a}x + {b}/{c} = {d}",
    "{a}/{b}x + {c} = {d}",
    "({a} + {b}) * {c}",
    "{a} * ({b} + {c})",
]


def random_expression() -> str:
    template = random.choice(_TEMPLATES)
    values = {
        "a": random.randint(1, 12),
        "b": random.randint(1, 30),
        "c": random.randint(1, 50),
        "d": random.randint(1, 50),
        "n": random.randint(50, 500),  # For percentage calculations
        "pct": random.randint(5, 150),  # Percentage values
        "pct2": random.randint(5, 95),  # Second percentage
        "small": random.randint(1, 9),  # Numerators for fractions
        "small2": random.randint(1, 9),
        "big": random.randint(2, 12),  # Denominators for fractions
        "big2": random.randint(2, 12),
    }
    return template.format(**values)


# ---------------------------------------------------------------------------
# 2. Rendering: turn a text string into a realistic-ish image.
# ---------------------------------------------------------------------------


def _find_fonts(fonts_dir: Path) -> list[Path]:
    """Collect .ttf/.otf files from a user-supplied fonts folder, plus a
    couple of common system fonts as a fallback so this runs out of the
    box even before you've added any handwriting-style fonts."""
    fonts = list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.otf"))

    system_fallbacks = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/freefont/FreeSerif.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),  # macOS
        Path("/System/Library/Fonts/Supplemental/Chalkboard.ttc"),  # macOS, handwriting-ish
    ]
    fonts += [f for f in system_fallbacks if f.exists()]

    if not fonts:
        raise RuntimeError(
            "No fonts found. Put some .ttf/.otf font files in the --fonts-dir "
            "folder (e.g. download free handwriting fonts from Google Fonts: "
            "'Kalam', 'Caveat', 'Patrick Hand', 'Shadows Into Light')."
        )
    return fonts


def render_expression_image(
    text: str,
    font_path: Path,
    image_size: tuple[int, int] = (400, 120),
) -> Image.Image:
    width, height = image_size

    # Light, slightly varied background — real photos are never pure white.
    bg_shade = random.randint(235, 255)
    image = Image.new("RGB", (width, height), (bg_shade, bg_shade, bg_shade))
    draw = ImageDraw.Draw(image)

    font_size = random.randint(28, 44)
    font = ImageFont.truetype(str(font_path), font_size)

    # Dark, slightly varied ink color.
    ink_shade = random.randint(0, 40)
    fill = (ink_shade, ink_shade, ink_shade)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = max(4, (width - text_w) // 2 + random.randint(-10, 10))
    y = max(4, (height - text_h) // 2 + random.randint(-8, 8))
    draw.text((x, y), text, font=font, fill=fill)

    # Small random rotation, like a photo taken at a slight angle.
    angle = random.uniform(-4, 4)
    image = image.rotate(angle, expand=False, fillcolor=(bg_shade, bg_shade, bg_shade))

    # Light blur sometimes, to imitate an out-of-focus phone photo.
    if random.random() < 0.3:
        image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))

    return image


# ---------------------------------------------------------------------------
# 3. Dataset generation: loop, save images, write the manifest.
# ---------------------------------------------------------------------------


def generate_dataset(count: int, out_dir: Path, fonts_dir: Path, seed: int | None = None) -> None:
    if seed is not None:
        random.seed(seed)

    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    fonts = _find_fonts(fonts_dir)
    manifest_path = out_dir / "manifest.csv"

    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "text"])

        for i in range(count):
            text = random_expression()
            font_path = random.choice(fonts)
            image = render_expression_image(text, font_path)

            image_filename = f"{i:06d}.png"
            image.save(images_dir / image_filename)
            writer.writerow([f"images/{image_filename}", text])

            if (i + 1) % max(1, count // 10) == 0:
                print(f"  generated {i + 1}/{count}")

    print(f"\nDone. {count} images written to {images_dir}")
    print(f"Manifest written to {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=1000, help="How many images to generate.")
    parser.add_argument("--out", type=Path, default=Path("training/data"), help="Output folder.")
    parser.add_argument(
        "--fonts-dir",
        type=Path,
        default=Path("training/fonts"),
        help="Folder to look for .ttf/.otf fonts in (optional — falls back to system fonts).",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = parser.parse_args()

    generate_dataset(args.count, args.out, args.fonts_dir, args.seed)


if __name__ == "__main__":
    main()
