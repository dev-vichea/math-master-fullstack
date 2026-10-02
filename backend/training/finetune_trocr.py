"""
Fine-tunes a pretrained OCR model (TrOCR) on your synthetic + real math
expression images.

╔══════════════════════════════════════════════════════════════════════╗
║  RUN THIS ON GOOGLE COLAB, NOT YOUR MAC.                              ║
║  Training needs a GPU. Colab gives you one for free.                  ║
║  Go to https://colab.research.google.com, upload this file's code    ║
║  cell-by-cell (each "# %% CELL" marker below = one Colab cell), and   ║
║  set Runtime -> Change runtime type -> GPU before running.            ║
╚══════════════════════════════════════════════════════════════════════╝

You do NOT need to understand the model internals to run this. Follow the
cells in order. Where you need to change something, it's marked "EDIT ME".
"""

# %% CELL 1 — install dependencies (Colab only, takes ~1 minute)
"""
!pip install -q transformers datasets torch torchvision jiwer accelerate
"""

# %% CELL 2 — upload your dataset
"""
From your Mac, zip your training/data folder:
    cd khmer-math-lab-backend/training
    zip -r data.zip data

Then in Colab, run:

from google.colab import files
uploaded = files.upload()   # choose data.zip from the file picker

!unzip -q data.zip
"""

# %% CELL 3 — load the manifest and split train/val
import csv
import random
from pathlib import Path

DATA_DIR = Path("data")            # EDIT ME if your folder name differs
MANIFEST = DATA_DIR / "manifest.csv"

with open(MANIFEST, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

random.seed(42)
random.shuffle(rows)

split_idx = int(len(rows) * 0.9)
train_rows = rows[:split_idx]
val_rows = rows[split_idx:]

print(f"train: {len(train_rows)}  val: {len(val_rows)}")

# %% CELL 4 — build a Hugging Face Dataset from the manifest
from datasets import Dataset
from PIL import Image


def load_examples(rows: list[dict]) -> dict:
    return {
        "image_path": [str(DATA_DIR / r["image_path"]) for r in rows],
        "text": [r["text"] for r in rows],
    }


train_dataset = Dataset.from_dict(load_examples(train_rows))
val_dataset = Dataset.from_dict(load_examples(val_rows))

# %% CELL 5 — load the pretrained model + processor
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# "microsoft/trocr-base-printed" is a good starting checkpoint for printed
# text; swap to "microsoft/trocr-base-handwritten" once you're training
# mostly on real handwritten photos rather than synthetic printed-font data.
MODEL_CHECKPOINT = "microsoft/trocr-base-printed"  # EDIT ME later

processor = TrOCRProcessor.from_pretrained(MODEL_CHECKPOINT)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_CHECKPOINT)

model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.vocab_size = model.config.decoder.vocab_size

# %% CELL 6 — preprocessing function (image + text -> model input tensors)
MAX_LABEL_LENGTH = 32


def preprocess(batch):
    images = [Image.open(p).convert("RGB") for p in batch["image_path"]]
    pixel_values = processor(images=images, return_tensors="pt").pixel_values

    labels = processor.tokenizer(
        batch["text"],
        padding="max_length",
        max_length=MAX_LABEL_LENGTH,
        truncation=True,
    ).input_ids
    # Replace pad token id with -100 so it's ignored in the loss.
    labels = [
        [(token if token != processor.tokenizer.pad_token_id else -100) for token in label]
        for label in labels
    ]
    batch["pixel_values"] = pixel_values
    batch["labels"] = labels
    return batch


train_dataset = train_dataset.map(preprocess, batched=True, batch_size=8, remove_columns=["image_path", "text"])
val_dataset = val_dataset.map(preprocess, batched=True, batch_size=8, remove_columns=["image_path", "text"])

train_dataset.set_format(type="torch", columns=["pixel_values", "labels"])
val_dataset.set_format(type="torch", columns=["pixel_values", "labels"])

# %% CELL 7 — evaluation metric: Character Error Rate (the standard OCR metric)
import numpy as np
from jiwer import cer


def compute_metrics(eval_pred):
    pred_ids, label_ids = eval_pred
    pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)

    label_ids = np.where(label_ids != -100, label_ids, processor.tokenizer.pad_token_id)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    return {"cer": cer(label_str, pred_str)}


# %% CELL 8 — train
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments

training_args = Seq2SeqTrainingArguments(
    output_dir="./trocr-khmer-math",
    predict_with_generate=True,
    per_device_train_batch_size=8,   # EDIT ME: lower to 4 if you hit an out-of-memory error
    per_device_eval_batch_size=8,
    num_train_epochs=10,              # EDIT ME: start small, increase once the pipeline works
    fp16=True,                        # faster training on Colab's GPU
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=20,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="cer",
    greater_is_better=False,
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

# %% CELL 9 — save the fine-tuned model and download it
model.save_pretrained("./trocr-khmer-math-final")
processor.save_pretrained("./trocr-khmer-math-final")

"""
!zip -r trocr-khmer-math-final.zip trocr-khmer-math-final

from google.colab import files
files.download("trocr-khmer-math-final.zip")
"""

# %% CELL 10 — quick sanity check on one image before you trust it
"""
import torch

test_image = Image.open("data/images/000000.png").convert("RGB")
pixel_values = processor(images=test_image, return_tensors="pt").pixel_values
generated_ids = model.generate(pixel_values)
print(processor.batch_decode(generated_ids, skip_special_tokens=True))
"""
