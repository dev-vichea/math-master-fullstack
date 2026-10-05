# Fine-Tuning pix2tex (LaTeX-OCR) for Khmer Math Lab

This guide explains how to fine-tune the **`pix2tex` (ViT + ResNet)** vision model on Cambodian mathematics curriculum problems (Algebra, Calculus, Trigonometry, BacII exams) and integrate the resulting lightweight model into the Math Lab application.

---

## 1. Why pix2tex (ViT + ResNet)?

Earlier experiments with `microsoft/trocr-base-printed` resulted in a **1.2 GB** model with **7.5 GB** checkpoints, slow CPU inference, and frequent character hallucinations due to missing Khmer math tokens.

`pix2tex` solves this problem:
* **Model Size:** Only **~85 MB** (over 90% smaller than TrOCR).
* **Speed:** 5x faster inference; runs easily on laptop CPUs or mobile backends.
* **Accuracy:** Specifically trained to decode mathematical visual structures (fractions, powers, radicals, matrices, limits, integrals) directly into clean LaTeX tokens.
* **Division of Labor:**
  $$\text{Cropped Image} \xrightarrow{\text{pix2tex (ViT + ResNet)}} \text{Raw LaTeX} \xrightarrow{\text{exercise\_parser.py}} \text{Isolated Formula} \xrightarrow{} \text{MathLive UI}$$

---

## 2. Directory Structure

All training assets and scripts live in [`backend/training/pix2tex/`](file:///Users/kiddd/Development/math-lab/backend/training/pix2tex):

```text
backend/training/pix2tex/
├── config.yaml               # Training hyperparameters (batch size, learning rate, ViT layers)
├── prepare_dataset.py        # Generates synthetic curriculum images & builds train/val datasets
├── finetune.py               # Fine-tuning script (supports Colab CUDA GPU, Apple Silicon MPS, CPU)
├── requirements.txt          # Python dependencies required for training
├── data/
│   ├── train_images/         # Rendered training equation images (0.png, 1.png, ...)
│   ├── val_images/           # Rendered validation equation images
│   ├── train_equations.txt   # Ground truth LaTeX formulas for training
│   ├── val_equations.txt     # Ground truth LaTeX formulas for validation
│   ├── train.pkl             # (Compiled binary dataset)
│   └── val.pkl               # (Compiled binary dataset)
└── models/                   # Fine-tuned checkpoint output directory (~85MB weights.pth)
```

---

## 3. Step 1: Install Training Dependencies

From the repository root or `backend` folder:

```bash
# In your virtual environment:
pip install -r backend/training/pix2tex/requirements.txt
```

> [!NOTE]
> If you are training on **Google Colab**, simply run:
> ```bash
> !pip install -q "pix2tex[train]" albumentations imagesize matplotlib pyyaml tqdm
> ```

---

## 4. Step 2: Prepare Training Data

Math OCR requires pairs of `(Image, LaTeX String)`. You can train using:
1. **Synthetic data** (rendered mathematically using Matplotlib mathtext).
2. **Real exam crops** (scans of Cambodian Grade 10-12 / BacII exam sheets).

### Option A: Generate Synthetic Curriculum Dataset
Run [`prepare_dataset.py`](file:///Users/kiddd/Development/math-lab/backend/training/pix2tex/prepare_dataset.py):

```bash
python backend/training/pix2tex/prepare_dataset.py --count 1000 --out backend/training/pix2tex/data
```

This generates:
* Fractions & rational expressions: $\frac{ax+b}{c} = d$
* Radicals & square roots: $\sqrt{ax+b} = c$, quadratic formula
* Limits: $\lim_{x \to 0} \frac{\sin ax}{ax}$, rational limits
* Integrals & derivatives: $\int_0^a (bx^2 - cx) dx$, $f'(x) = ax + b$
* Quadratic & polynomial equations: $ax^2 + bx + c = 0$

### Option B: Adding Real Exam Photos
If you have real cropped formulas from school worksheets:
1. Save your cropped PNG images into `backend/training/pix2tex/data/train_images/`.
2. Add the corresponding ground-truth LaTeX line into `backend/training/pix2tex/data/train_equations.txt`.

### Option C: Handwritten Math with Data Augmentation
Handwritten notes written in pencil or ink have variations in handwriting slant, stroke thickness, and lighting.
To train on handwritten photos:
1. Store raw handwritten photos in `backend/training/pix2tex/data/images/` using clear naming (`handwritten_01.png`, `handwritten_02.png`, etc.).
2. Run [`prepare_handwrite_dataset.py`](file:///Users/kiddd/Development/math-lab/backend/training/pix2tex/prepare_handwrite_dataset.py):
   ```bash
   python backend/training/pix2tex/prepare_handwrite_dataset.py
   ```
   This automatically:
   - Proportionally scales images so they never exceed pix2tex dimensions (`672x192`).
   - Generates realistic handwriting augmentations (forward/backward slant, bold gel pen, thin ballpoint, contrast, paper lighting).
   - Compiles binary `train.pkl` and `val.pkl` with integer index filenames (`0.png`, `1.png`, ...).

---

## 5. Step 3: Run Fine-Tuning

### Running Locally (Mac M-Series or CPU)
Use [`finetune.py`](file:///Users/kiddd/Development/math-lab/backend/training/pix2tex/finetune.py):

```bash
python backend/training/pix2tex/finetune.py --config backend/training/pix2tex/config.yaml --epochs 5 --batchsize 8
```

### Running on Google Colab (Recommended for Free T4 GPU)
Training takes only **~15–20 minutes** on Google Colab's free GPU:

1. Open a new notebook on [Google Colab](https://colab.research.google.com).
2. Set Runtime: **Runtime $\rightarrow$ Change runtime type $\rightarrow$ T4 GPU**.
3. Zip your prepared data and upload it:
   ```bash
   zip -r pix2tex_data.zip backend/training/pix2tex/data
   ```
4. Run the Colab training cell:
   ```python
   !pip install -q "pix2tex[train]" albumentations imagesize

   # Run fine-tuning on GPU
   !python -m pix2tex.train --config backend/training/pix2tex/config.yaml --device cuda
   ```
5. Download the output file: `models/pix2tex_khmer_math/weights.pth` (**~85 MB**).

---

## 6. Step 4: Plug the Fine-Tuned Model into the Backend

Once training finishes, copy your new `weights.pth` to:
`backend/training/pix2tex/models/weights.pth`

In [`backend/app/ocr/engines/pix2tex_engine.py`](file:///Users/kiddd/Development/math-lab/backend/app/ocr/engines/pix2tex_engine.py#L216-L226), the engine automatically checks for this file:

```python
class Pix2TexVisionEngine(MathVisionEngine):
    def __init__(self, model_instance: Any | None = None, weights_path: str | Path | None = None):
        self._model = model_instance
        self.weights_path = weights_path or (
            Path(__file__).resolve().parent.parent.parent / "training" / "pix2tex" / "models" / "weights.pth"
        )

    @property
    def model(self) -> Any:
        if self._model is None:
            from pix2tex.cli import LatexOCR
            if self.weights_path and Path(self.weights_path).exists():
                logger.info(f"Loading custom fine-tuned pix2tex weights from {self.weights_path}")
                self._model = LatexOCR(checkpoint_path=str(self.weights_path))
            else:
                logger.info("Loading default pretrained pix2tex weights")
                self._model = LatexOCR()
        return self._model
```

Ensure [`backend/.env`](file:///Users/kiddd/Development/math-lab/backend/.env#L24) has:
```env
VISION_PROVIDER=pix2tex
```

---

## 7. Step 5: Verification & Testing

### 1. Test via CLI / Python
```bash
python -c "
from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine
engine = Pix2TexVisionEngine()
with open('backend/training/pix2tex/data/train_images/0.png', 'rb') as f:
    res = engine.detect(f.read())
print('Detected LaTeX:', res.detected_text)
"
```

### 2. Test in the Web UI
1. Start backend: `uvicorn app.main:app --reload --port 8000`
2. Start frontend: `npm run dev`
3. Drag and drop any formula image onto the problem uploader in the frontend.
4. Verify that:
   - The formula renders immediately in **MathLive**.
   - Any Khmer instructions (e.g. `ដោះស្រាយ`, `គណនា`) are separated by [`exercise_parser.py`](file:///Users/kiddd/Development/math-lab/backend/app/parser/exercise_parser/exercise_parser.py).
   - Clicking **"Cook It"** sends the problem to SymPy and returns the step-by-step math solution.
