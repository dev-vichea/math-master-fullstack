# AI Training for Khmer Math Lab

This directory contains everything needed for training and evaluating AI models.

## Quick Start

### 1. Install Training Dependencies

```bash
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

### 4. Train Your First Model

```bash
# Intent classification
python scripts/train_intent_classifier.py

# Or use notebooks for interactive training
jupyter notebook notebooks/02_intent_classifier_training.ipynb
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
