"""
Complete training pipeline for Khmer Math Lab OCR model.

This script does EVERYTHING:
  1. Labels all your cropped test_exercises images (I read them for you)
  2. Generates 500 extra synthetic math images
  3. Combines them with existing sample_data
  4. Fine-tunes the TrOCR model
  5. Saves the final model to training/models/trocr-khmer-math-final

Run:
    python scripts/prepare_and_train.py
"""
from __future__ import annotations

import csv
import os
import random
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
TRAINING_DIR = SCRIPT_DIR.parent          # training/
BACKEND_DIR = TRAINING_DIR.parent         # backend/

TEST_EXERCISES = TRAINING_DIR / "test_exercises"
SAMPLE_DATA = TRAINING_DIR / "sample_data"
OUTPUT_DATA = TRAINING_DIR / "data"       # combined training data goes here
MODELS_DIR = TRAINING_DIR / "models"

# ---------------------------------------------------------------------------
# 1. Hand-labeled manifest for YOUR cropped test_exercises images.
#    I read every single image and wrote down the math expression.
#    The Khmer prefixes (ក., ខ., គ., etc.) are stripped because
#    the TrOCR model only needs to output the math symbols.
# ---------------------------------------------------------------------------
LABELED_CROPS: list[tuple[str, str]] = [
    # === Integrals ===
    ("integrals/crop_ka.png",  "int_0^2 3x dx"),
    ("integrals/crop_kha.png", "int_2^4 4x dx"),
    ("integrals/crop_ko.png",  "int_0^2 x^2 dx"),
    ("integrals/crop_kho.png", "int_0^2 (x^2 - 5x) dx"),
    ("integrals/crop_ngo.png", "int_1^2 x^2 dx"),
    ("integrals/image5.png",   "int_0^2 3x dx"),
    ("integrals/image6.png",   "int_0^2 (x^2 - 5x) dx"),

    # === Differentials – Exercise 1 (find y') ===
    ("differentials/crop_ex1_ka.png",  "y' = 2x^2 - x + 1"),
    ("differentials/crop_ex1_kha.png", "y' = e^(-2x)"),
    ("differentials/crop_ex1_kho.png", "y' = x/(x^2 - 1)"),

    # === Differentials – Exercise 2 (ODE with initial condition) ===
    ("differentials/crop_ex2_ka.png",  "y'/y = cos x, y(pi/2) = e"),
    ("differentials/crop_ex2_kha.png", "y' = e^(2x), y(0) = 5"),
    ("differentials/crop_ex2_ko.png",  "(3x^2 - 2)y' = 6, y(1) = 4"),

    # === Differentials – Exercise 3 (first-order linear ODE) ===
    ("differentials/crop_ex3_ka.png",  "dy/dx + 2y = 0"),
    ("differentials/crop_ex3_kha.png", "3 dy/dx + y = 0"),
    ("differentials/crop_ex3_ko.png",  "2y' - 3y = 0"),

    # === Differentials – Exercise 4 (ODE + initial condition) ===
    ("differentials/crop_ex4_ka.png",  "-y' + 2y = 0, y(3) = -2"),
    ("differentials/crop_ex4_kha.png", "2y' + y = 0, y(ln 4) = 1/5"),
    ("differentials/crop_ex4_kho.png", "2y' - 5y = 0, y(1) = -3"),

    # === Differentials – Exercise 5 (verify solution) ===
    ("differentials/crop_ex5_ka.png",  "y = x + e^x, y' - y = 1 - x"),
    ("differentials/crop_ex5_kha.png", "y = e^(3x) - x - 1, y' - 3y = 3x + 2"),
    ("differentials/crop_ex5_ko.png",  "y = sin x + cos x, y' + y = 2 cos x"),

    # === Differentials – Exercise 6 (find derivative of function) ===
    ("differentials/crop_ex6_ka.png",  "f(x) = (x + 1)e^(-2x)"),
    ("differentials/crop_ex6_kha.png", "f(x) = 2e^(-x) + 3e^(3x)"),
    ("differentials/crop_ex6_ko.png",  "f(x) = (2 cos 3x - 3 sin 3x)e^x"),

    # === Differentials – Exercise 7 (second-order ODE) ===
    ("differentials/crop_ex7_ka.png",  "y'' - y = 0, y(0) = 1, y'(0) = -2"),
    ("differentials/crop_ex7_kha.png", "y'' - 2y' + 3y = 0, y(0) = 2, y'(0) = 1"),
    ("differentials/crop_ex7_kho.png", "y'' - 3y' + 2y = 0, y(0) = 1, y'(0) = 3"),
    ("differentials/crop_ex7_ko.png",  "y'' + y = 0, y(pi/2) = 3, y'(pi/2) = 2"),

    # === Derivatives (single-expression crops) ===
    ("derivatives/image.png",  "y = sqrt(x^2 - 1)"),
    ("derivatives/image1.png", "f(x) = e^x + 3 - e^x/(e^x + 3)"),
    ("derivatives/image2.png", "f(x) = x ln x / (x + 1)"),

    # === Sequences (limits) ===
    ("sequences/image.png",  "lim (n^2 + 3n - 1)/(8n^2 - n + 1)"),
    ("sequences/image2.png", "lim (n^2 + sin n)/(5n^2 + cos(pi*n))"),

    # === Root-level single-expression images ===
    ("image.png", "A = sqrt(128y) - sqrt(2y)"),
]


def step1_prepare_labeled_data():
    """Copy cropped test exercise images into data/ with labels."""
    print("=" * 60)
    print("STEP 1: Preparing labeled data from test_exercises")
    print("=" * 60)

    images_dir = OUTPUT_DATA / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    idx = 0

    # --- A: Copy labeled test exercise crops ---
    for rel_path, label_text in LABELED_CROPS:
        src = TEST_EXERCISES / rel_path
        if not src.exists():
            print(f"  [SKIP] {rel_path} (file missing)")
            continue

        dest_name = f"ex_{idx:04d}.png"
        dest = images_dir / dest_name
        shutil.copy2(src, dest)
        rows.append((f"images/{dest_name}", label_text))
        idx += 1

    print(f"  Labeled {idx} cropped exercise images")

    # --- B: Copy existing sample_data images ---
    sample_manifest = SAMPLE_DATA / "manifest.csv"
    if sample_manifest.exists():
        with open(sample_manifest, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sample_count = 0
            for row in reader:
                src = SAMPLE_DATA / row["image_path"]
                if src.exists():
                    dest_name = f"syn_{idx:04d}.png"
                    dest = images_dir / dest_name
                    shutil.copy2(src, dest)
                    rows.append((f"images/{dest_name}", row["text"]))
                    idx += 1
                    sample_count += 1
        print(f"  Copied {sample_count} existing sample_data images")

    return rows, idx


def step2_generate_synthetic(start_idx: int, count: int = 500):
    """Generate synthetic math expression images."""
    print()
    print("=" * 60)
    print(f"STEP 2: Generating {count} synthetic training images")
    print("=" * 60)

    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    images_dir = OUTPUT_DATA / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Templates covering all math types the app handles
    templates = [
        # Basic linear
        "{a}x + {b} = {c}",
        "{a}x - {b} = {c}",
        "{a}x = {b}",
        "x + {a} = {b}",
        "x - {a} = {b}",
        # Both sides
        "{a}x + {b} = {c}x + {d}",
        "{a}x - {b} = {c}x + {d}",
        # Arithmetic
        "{a} + {b}",
        "{a} - {b}",
        "{a} * {b}",
        # Fractions
        "{a}/{b} + {c}/{d}",
        "{a}/{b} - {c}/{d}",
        "{a}/{b} * {c}/{d}",
        "({a}/{b}) / ({c}/{d})",
        # Quadratic
        "x^2 + {b}x + {c} = 0",
        "x^2 - {b}x + {c} = 0",
        "{a}x^2 + {b}x + {c} = 0",
        "x^2 = {a}",
        # Powers
        "{a}x^2 + {b}x = {c}",
        "{a}x^2 - {b} = 0",
        # Percentage
        "{pct}% of {n}",
        "{pct}% + {pct2}%",
        # Parentheses
        "({a} + {b}) * {c}",
        "{a} * ({b} + {c})",
        # Derivatives (the new types in your exercises!)
        "y' = {a}x^2 - {b}x + {c}",
        "y' = e^({a}x)",
        "y' = e^(-{a}x)",
        "f(x) = {a}e^({b}x)",
        "f(x) = {a}e^(-{b}x) + {c}e^({d}x)",
        "dy/dx + {a}y = 0",
        "{a}y' - {b}y = 0",
        "{a}y' + {b}y = 0",
        "y'' - {a}y' + {b}y = 0",
        "y'' + {a}y = 0",
        "y'' - y = 0",
        # Integrals
        "int_0^{a} {b}x dx",
        "int_{a}^{b} x^2 dx",
        "int_0^{a} (x^2 - {b}x) dx",
        "int_{a}^{b} {c}x dx",
        # Limits
        "lim (n^2 + {a}n)/(n^2 - {b})",
        "lim ({a}n + {b})/({c}n - {d})",
        # Square roots
        "sqrt({a})",
        "sqrt(x^2 - {a})",
        "y = sqrt(x^2 + {a})",
        "{a}*sqrt({b})",
        # Trig
        "sin x + cos x",
        "y = sin x + cos x",
        "f(x) = sin({a}x)",
        "f(x) = cos({a}x) + sin({b}x)",
        # Logarithm
        "y = ln(x + {a})",
        "y = x ln x",
        "y = ln({a} + e^x)",
        "f(x) = x ln x / (x + {a})",
    ]

    # Find system fonts
    system_fonts = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
        Path("/System/Library/Fonts/Supplemental/Courier New.ttf"),
        Path("/System/Library/Fonts/Supplemental/Georgia.ttf"),
        Path("/System/Library/Fonts/Supplemental/Trebuchet MS.ttf"),
        Path("/System/Library/Fonts/Supplemental/Chalkboard.ttc"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    fonts = [f for f in system_fonts if f.exists()]
    if not fonts:
        # Ultimate fallback
        fonts = list(Path("/System/Library/Fonts").glob("*.ttf"))[:3]
    if not fonts:
        print("  WARNING: No fonts found, using default")
        fonts = [None]

    random.seed(42)
    rows = []
    idx = start_idx

    for i in range(count):
        template = random.choice(templates)
        values = {
            "a": random.randint(1, 12),
            "b": random.randint(1, 30),
            "c": random.randint(1, 50),
            "d": random.randint(1, 50),
            "n": random.randint(50, 500),
            "pct": random.randint(5, 150),
            "pct2": random.randint(5, 95),
        }
        text = template.format(**values)

        # Render
        width, height = 400, 120
        bg = random.randint(235, 255)
        image = Image.new("RGB", (width, height), (bg, bg, bg))
        draw = ImageDraw.Draw(image)

        font_size = random.randint(26, 42)
        font_path = random.choice(fonts)
        try:
            if font_path:
                font = ImageFont.truetype(str(font_path), font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        ink = random.randint(0, 40)
        fill = (ink, ink, ink)

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = max(4, (width - tw) // 2 + random.randint(-10, 10))
        y = max(4, (height - th) // 2 + random.randint(-8, 8))
        draw.text((x, y), text, font=font, fill=fill)

        # Random rotation
        angle = random.uniform(-4, 4)
        image = image.rotate(angle, expand=False, fillcolor=(bg, bg, bg))

        # Occasional blur
        if random.random() < 0.25:
            image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))

        dest_name = f"gen_{idx:04d}.png"
        image.save(images_dir / dest_name)
        rows.append((f"images/{dest_name}", text))
        idx += 1

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{count} images")

    print(f"  Total synthetic: {count}")
    return rows


def step3_write_manifest(all_rows: list[tuple[str, str]]):
    """Write the combined manifest.csv."""
    print()
    print("=" * 60)
    print(f"STEP 3: Writing manifest ({len(all_rows)} total examples)")
    print("=" * 60)

    manifest = OUTPUT_DATA / "manifest.csv"
    with open(manifest, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "text"])
        for row in all_rows:
            writer.writerow(row)

    print(f"  Manifest saved to: {manifest}")
    return manifest


def step4_train(manifest_path: Path, epochs: int = 5, batch_size: int = 4):
    """Fine-tune TrOCR on the combined dataset."""
    print()
    print("=" * 60)
    print("STEP 4: Fine-tuning TrOCR model")
    print("=" * 60)

    import csv as csv_mod
    import numpy as np
    import torch
    from datasets import Dataset
    import os
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    from PIL import Image
    from transformers import (
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        TrOCRProcessor,
        VisionEncoderDecoderModel,
        RobertaTokenizer,
        ViTImageProcessor,
    )

    # Device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"  Device: CUDA GPU ({torch.cuda.get_device_name(0)})")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("  Device: Apple Silicon MPS")
    else:
        device = torch.device("cpu")
        print("  Device: CPU (will be slow)")

    # Load manifest
    data_dir = manifest_path.parent
    with open(manifest_path, encoding="utf-8") as f:
        rows = list(csv_mod.DictReader(f))

    random.seed(42)
    random.shuffle(rows)
    split = int(len(rows) * 0.9)
    train_rows, val_rows = rows[:split], rows[split:]
    print(f"  Train: {len(train_rows)} examples, Val: {len(val_rows)} examples")

    def make_ds(rs):
        return Dataset.from_dict({
            "image_path": [str(data_dir / r["image_path"]) for r in rs],
            "text": [r["text"] for r in rs],
        })

    train_ds = make_ds(train_rows)
    val_ds = make_ds(val_rows)

    # Load model
    MODEL = "microsoft/trocr-base-printed"
    print(f"  Loading pretrained model: {MODEL}")
    tokenizer = RobertaTokenizer.from_pretrained("roberta-large")
    image_processor = ViTImageProcessor.from_pretrained(MODEL)
    processor = TrOCRProcessor(image_processor=image_processor, tokenizer=tokenizer)
    model = VisionEncoderDecoderModel.from_pretrained(MODEL)

    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.eos_token_id = processor.tokenizer.eos_token_id
    model.config.vocab_size = model.config.decoder.vocab_size
    model.config.decoder.pad_token_id = processor.tokenizer.pad_token_id
    model.config.decoder.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.decoder.eos_token_id = processor.tokenizer.eos_token_id

    if hasattr(model, "generation_config") and model.generation_config is not None:
        model.generation_config.max_length = 64
        model.generation_config.pad_token_id = processor.tokenizer.pad_token_id
        model.generation_config.eos_token_id = processor.tokenizer.eos_token_id
        model.generation_config.decoder_start_token_id = processor.tokenizer.cls_token_id

    # Preprocessing
    MAX_LEN = 64

    def preprocess(batch):
        images = [Image.open(p).convert("RGB") for p in batch["image_path"]]
        pixel_values = processor(images=images, return_tensors="pt").pixel_values
        labels = processor.tokenizer(
            batch["text"], padding="max_length", max_length=MAX_LEN, truncation=True
        ).input_ids
        labels = [
            [(t if t != processor.tokenizer.pad_token_id else -100) for t in lbl]
            for lbl in labels
        ]
        batch["pixel_values"] = pixel_values
        batch["labels"] = labels
        return batch

    print("  Preprocessing training data...")
    train_ds = train_ds.map(preprocess, batched=True, batch_size=8, remove_columns=["image_path", "text"])
    print("  Preprocessing validation data...")
    val_ds = val_ds.map(preprocess, batched=True, batch_size=8, remove_columns=["image_path", "text"])

    train_ds.set_format(type="torch", columns=["pixel_values", "labels"])
    val_ds.set_format(type="torch", columns=["pixel_values", "labels"])

    # Metric
    def compute_metrics(eval_pred):
        pred_ids, label_ids = eval_pred
        if isinstance(pred_ids, tuple):
            pred_ids = pred_ids[0]
        pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        label_ids = np.where(label_ids != -100, label_ids, processor.tokenizer.pad_token_id)
        label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)

        # Simple character error rate
        total_chars = 0
        total_errors = 0
        for ref, hyp in zip(label_str, pred_str):
            total_chars += max(len(ref), 1)
            errors = 0
            for i in range(max(len(ref), len(hyp))):
                r = ref[i] if i < len(ref) else ""
                h = hyp[i] if i < len(hyp) else ""
                if r != h:
                    errors += 1
            total_errors += errors
        cer = total_errors / max(total_chars, 1)
        return {"cer": cer}

    # Training
    output_dir = str(MODELS_DIR / "trocr-checkpoints")
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        predict_with_generate=True,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=10,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="cer",
        greater_is_better=False,
        report_to="none",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )

    print()
    print("  🚀 Starting training...")
    print(f"  Epochs: {epochs}, Batch size: {batch_size}")
    print(f"  Total training steps: ~{len(train_ds) * epochs // batch_size}")
    print()
    trainer.train()

    # Save final model
    final_dir = MODELS_DIR / "trocr-khmer-math-final"
    final_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(final_dir))
    processor.save_pretrained(str(final_dir))
    print()
    print(f"  ✅ Model saved to: {final_dir}")
    return final_dir


def step5_test(model_dir: Path):
    """Quick sanity test on a sample image."""
    print()
    print("=" * 60)
    print("STEP 5: Testing the trained model")
    print("=" * 60)

    from PIL import Image
    import torch
    from transformers import (
        TrOCRProcessor,
        VisionEncoderDecoderModel,
        RobertaTokenizer,
        ViTImageProcessor,
    )

    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    try:
        processor = TrOCRProcessor.from_pretrained(str(model_dir))
    except Exception:
        tok = RobertaTokenizer.from_pretrained(str(model_dir))
        img_proc = ViTImageProcessor.from_pretrained(str(model_dir))
        processor = TrOCRProcessor(image_processor=img_proc, tokenizer=tok)
    model = VisionEncoderDecoderModel.from_pretrained(str(model_dir))
    model.to(device)
    model.eval()

    # Test on a few images
    test_images = [
        (SAMPLE_DATA / "images" / "000001.png", "12x = 25"),
        (TEST_EXERCISES / "integrals" / "crop_ka.png", "int_0^2 3x dx"),
        (TEST_EXERCISES / "differentials" / "crop_ex1_ka.png", "y' = 2x^2 - x + 1"),
    ]

    for img_path, expected in test_images:
        if not img_path.exists():
            continue
        image = Image.open(img_path).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
        with torch.no_grad():
            generated_ids = model.generate(pixel_values, max_new_tokens=40)
        prediction = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        match = "✅" if prediction.strip() == expected.strip() else "❌"
        print(f"  {match} Expected: {expected:40s} | Predicted: {prediction}")


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Khmer Math Lab — TrOCR Training Pipeline            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Step 1: Label + copy exercise images
    real_rows, next_idx = step1_prepare_labeled_data()

    # Step 2: Generate synthetic data
    synth_rows = step2_generate_synthetic(start_idx=next_idx, count=500)

    # Step 3: Write combined manifest
    all_rows = real_rows + synth_rows
    random.seed(42)
    random.shuffle(all_rows)
    manifest = step3_write_manifest(all_rows)

    # Step 4: Train
    model_dir = step4_train(manifest, epochs=3, batch_size=4)

    # Step 5: Quick test
    step5_test(model_dir)

    print()
    print("=" * 60)
    print("🎉 DONE! Training complete.")
    print(f"   Model saved to: {MODELS_DIR / 'trocr-khmer-math-final'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
