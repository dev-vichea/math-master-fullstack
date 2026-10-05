# AI Training for Khmer Math Lab

This directory contains everything needed for training and evaluating AI models.

## Quick Start

### 1. Activate Environment & Dependencies

From the backend root:
```bash
source .venv/bin/activate
cd training
pip install -r training_requirements.txt
```

### 2. Collect Data

Start the data collection server:
```bash
python scripts/data_collection_server.py
```

### 3. Run Khmer OCR
Test Khmer OCR on an image and solve it:
```bash
# Run OCR using Kiri OCR:
python scripts/run_khmer_ocr.py --image sample_data/images/000001.png --solve
```

### 4. Train Models (CLI or Jupyter Notebook)

**Option A: Using Jupyter Notebooks (Recommended)**
Open notebooks directly in VS Code / Antigravity IDE (Kernel: `Python (Math Lab .venv)`) or launch Jupyter Lab:
```bash
jupyter lab
```
Available notebooks:
- [01_trocr_finetuning.ipynb](file:///Users/kiddd/Development/math-lab/backend/training/notebooks/01_trocr_finetuning.ipynb) — Fine-tune TrOCR model on math expression images.
- [02_intent_classifier_training.ipynb](file:///Users/kiddd/Development/math-lab/backend/training/notebooks/02_intent_classifier_training.ipynb) — Train bilingual Khmer/English math intent classifier.

**Option B: Using Python CLI**
```bash
# Train intent classifier script
python scripts/train_intent_classifier.py
```

## Directory Structure

```
training/
├── data/                    # Training datasets
│   ├── intent_classification/
│   ├── handwriting/
│   └── word_problems/
├── notebooks/              # Jupyter notebooks for exploration
├── scripts/                # Training and evaluation scripts
├── models/                 # Saved model checkpoints
└── README.md              # This file
```

## See Also

- `docs/AI_TRAINING_GUIDE.md` - Comprehensive training guide
- `notebooks/` - Interactive training examples
