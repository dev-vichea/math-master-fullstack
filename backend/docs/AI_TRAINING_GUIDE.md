# AI Training Guide for Khmer Math Lab

## Overview

This guide explains how to train and integrate AI models into Khmer Math Lab for enhanced capabilities beyond the current rule-based system.

**Current Status:** The backend uses **deterministic algorithms** (SymPy) for solving, which is intentional and should remain. AI/ML should be used for:
1. **Understanding** - Better intent classification, NLP for word problems
2. **Vision** - Handwriting recognition, diagram understanding
3. **Explanation** - More natural Khmer language generation
4. **NOT for solving** - Keep SymPy for actual math computation (reliability)

## Architecture Principle

```
User Input → AI Understanding → Deterministic Math Engine → AI Explanation → User
             ↑ Train this          ↓ Never train this      ↑ Train this
```

---

## 🎯 What to Train AI For

### 1. Enhanced Intent Classification (High Priority)

**Current:** Rule-based keyword matching in `app/core/khmer/intent.py`
**Goal:** ML model that understands natural Khmer mathematical language

**Why Train:**
- Handle variations in phrasing
- Understand context and intent better
- Support conversational queries
- Handle typos and informal language

**Approach:**

#### Option A: Fine-tune BERT for Khmer
```python
# Recommended: khmer-nlp/bert-base-khmer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "khmer-nlp/bert-base-khmer"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=4  # solve, evaluate, simplify, unknown
)
```

**Training Data Needed:**
- 1,000+ labeled examples per intent class
- Mix of formal and informal Khmer
- Various mathematical topics

**Example Dataset:**
```json
[
  {"text": "ដោះស្រាយ 2x + 5 = 15", "intent": "solve_equation"},
  {"text": "ជួយគណនា ២០% នៃ ១៥០", "intent": "evaluate_expression"},
  {"text": "តើ x ស្មើប៉ុន្មាន បើ 3x = 12", "intent": "solve_equation"},
  {"text": "ធ្វើឲ្យសាមញ្ញ 4/8", "intent": "simplify_expression"}
]
```

#### Option B: Few-shot Learning with GPT
```python
# Use OpenAI API with Khmer examples
import openai

def classify_intent_with_gpt(question: str) -> str:
    prompt = f"""You are a Khmer math teacher. Classify this question:

Examples:
"ដោះស្រាយ 2x + 5 = 15" → solve_equation
"គណនា 5 + 3" → evaluate_expression
"ធ្វើឲ្យសាមញ្ញ 4/8" → simplify_expression

Question: "{question}"
Intent: """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
```

### 2. Handwriting Recognition (Medium Priority)

**Current:** OCR providers (Tesseract, Google Vision, Mathpix)
**Goal:** Custom model trained specifically on Khmer mathematical handwriting

**Why Train:**
- Better accuracy for Khmer numerals (០-៩)
- Understand student handwriting variations
- Handle mathematical notation in Khmer context
- Offline capability

**Approach:**

#### Option A: Fine-tune TrOCR
```python
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

# Start with pre-trained TrOCR
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Fine-tune on your Khmer math dataset
```

**Training Data Needed:**
- 10,000+ images of handwritten Khmer math
- Collected from real students
- Various handwriting styles
- Different lighting conditions

**Data Collection Strategy:**
1. Create a data collection app where students write math problems
2. Ask teachers to contribute student work (anonymized)
3. Use existing Khmer handwriting datasets + math symbols
4. Synthetic data generation (augmentation)

#### Option B: Custom CNN + LSTM
```python
import tensorflow as tf

def build_handwriting_model():
    # CNN for feature extraction
    cnn_model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(64, 256, 1)),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2))
    ])
    
    # LSTM for sequence modeling
    lstm_model = tf.keras.Sequential([
        tf.keras.layers.LSTM(128, return_sequences=True),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.Dense(vocab_size, activation='softmax')
    ])
    
    return tf.keras.Model(...)
```

### 3. Word Problem Understanding (High Priority)

**Current:** Not implemented
**Goal:** Extract equations from Khmer word problems

**Example:**
```
Input: "មាន​អំបិល​២​កីឡូក្រាម​ និង​ស្ករ​៣​កីឡូក្រាម។ តើ​សរុប​ទម្ងន់​ប៉ុន្មាន?"
       (There are 2kg of salt and 3kg of sugar. What's the total weight?)

Output: "2 + 3"
```

**Approach:**

#### Use GPT-4 with Khmer Prompt Engineering
```python
def extract_equation_from_word_problem(problem: str) -> str:
    prompt = f"""You are a Khmer math teacher. Extract the mathematical equation from this word problem.

Examples:
Problem: "មាន​សិស្ស​២០​នាក់។ ប្រសិនបើ​មក​ថែម​៥​នាក់​ទៀត តើ​មាន​សរុប​ប៉ុន្មាន?"
Equation: "20 + 5"

Problem: "x ធំជាង 5 ឲ្យ 3។ តើ x ស្មើប៉ុន្មាន?"
Equation: "x - 5 = 3"

Problem: "{problem}"
Equation: """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
```

### 4. Natural Khmer Explanation Generation (Medium Priority)

**Current:** Template-based step descriptions
**Goal:** More natural, contextual Khmer explanations

**Why Train:**
- More engaging for students
- Adapt language level to student
- Add helpful tips and insights
- More conversational tone

**Approach:**

#### Fine-tune mT5 for Khmer
```python
from transformers import MT5ForConditionalGeneration, MT5Tokenizer

model = MT5ForConditionalGeneration.from_pretrained("google/mt5-base")
tokenizer = MT5Tokenizer.from_pretrained("google/mt5-base")

# Fine-tune on Khmer math explanations
```

**Training Data:**
```json
{
  "step": "2x = 10",
  "technical": "ចែកភាគីទាំងពីរដោយ 2",
  "natural": "ឥឡូវ យើងចែក​ទាំង​សងខាង​ដោយ​២ ដើម្បី​រក​តម្លៃ x។ នេះ​ដូចជា​យើង​មាន​កែវ​ទឹក​២​កែវ​ហើយ​ចង់​ដឹង​ថា​កែវ​មួយ​មាន​ទឹក​ប៉ុន្មាន។"
}
```

---

## 🛠️ Implementation Guide

### Step 1: Set Up Training Infrastructure

Create a new `training/` directory:

```
training/
├── data/
│   ├── intent_classification/
│   │   ├── labeled_questions.jsonl
│   │   └── validation_set.jsonl
│   ├── handwriting/
│   │   ├── images/
│   │   └── labels.csv
│   └── word_problems/
│       └── problems_with_equations.jsonl
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_intent_classifier_training.ipynb
│   └── 03_evaluation.ipynb
├── scripts/
│   ├── train_intent_classifier.py
│   ├── train_handwriting_model.py
│   └── evaluate_model.py
└── models/
    └── checkpoints/
```

### Step 2: Collect Training Data

#### Data Collection App (React/Flutter)
```python
# Simple Flask app for data collection
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/api/collect', methods=['POST'])
def collect_data():
    data = request.json
    # Store: question, user_intent, correct_answer
    with open('collected_data.jsonl', 'a') as f:
        f.write(json.dumps(data) + '\n')
    return jsonify({'status': 'success'})
```

#### Synthetic Data Generation
```python
import random

templates = [
    "ដោះស្រាយ {var} + {num1} = {num2}",
    "រក {var} ពី {num1}{var} = {num2}",
    "គណនា {num1} + {num2}",
    "តើ {num1} ភាគរយ នៃ {num2} ស្មើប៉ុន្មាន"
]

def generate_synthetic_data(n=1000):
    data = []
    for _ in range(n):
        template = random.choice(templates)
        question = template.format(
            var=random.choice(['x', 'y', 'n']),
            num1=random.randint(1, 100),
            num2=random.randint(1, 100)
        )
        data.append({
            'question': question,
            'intent': classify_template(template)
        })
    return data
```

### Step 3: Train Models

#### Intent Classifier Training Script
```python
# training/scripts/train_intent_classifier.py
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset

# Load data
dataset = load_dataset('json', data_files={
    'train': 'data/intent_classification/labeled_questions.jsonl',
    'validation': 'data/intent_classification/validation_set.jsonl'
})

# Load model
model_name = "khmer-nlp/bert-base-khmer"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=4
)

# Tokenize
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir='./models/intent_classifier',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['validation'],
)

trainer.train()
trainer.save_model('./models/intent_classifier/final')
```

### Step 4: Integrate Trained Models

#### Create ML Intent Classifier
```python
# app/core/khmer/ml_intent.py
from transformers import pipeline
from app.core.khmer.intent import IntentClassifier, MathIntent

class MLIntentClassifier(IntentClassifier):
    """ML-based intent classifier using fine-tuned BERT."""
    
    def __init__(self, model_path: str = "./models/intent_classifier/final"):
        self.classifier = pipeline(
            "text-classification",
            model=model_path,
            tokenizer=model_path
        )
        
        # Map model labels to MathIntent enum
        self.label_map = {
            "LABEL_0": MathIntent.SOLVE_EQUATION,
            "LABEL_1": MathIntent.EVALUATE_EXPRESSION,
            "LABEL_2": MathIntent.SIMPLIFY_EXPRESSION,
            "LABEL_3": MathIntent.UNKNOWN,
        }
    
    def classify(self, normalized_text: str) -> MathIntent:
        result = self.classifier(normalized_text)[0]
        label = result['label']
        confidence = result['score']
        
        # Fall back to rule-based if confidence is low
        if confidence < 0.7:
            from app.core.khmer.intent import RuleBasedIntentClassifier
            fallback = RuleBasedIntentClassifier()
            return fallback.classify(normalized_text)
        
        return self.label_map.get(label, MathIntent.UNKNOWN)
```

#### Update Config
```python
# app/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # ML Model Settings
    use_ml_intent_classifier: bool = False  # Toggle ML vs rule-based
    ml_intent_model_path: str = "./models/intent_classifier/final"
    
    use_ml_handwriting: bool = False
    ml_handwriting_model_path: str = "./models/handwriting/final"
```

#### Plug into Service
```python
# app/services/math_service.py
from app.config import get_settings
from app.core.khmer.intent import RuleBasedIntentClassifier
from app.core.khmer.ml_intent import MLIntentClassifier

settings = get_settings()

# Choose classifier based on config
if settings.use_ml_intent_classifier:
    _intent_classifier = MLIntentClassifier(settings.ml_intent_model_path)
else:
    _intent_classifier = RuleBasedIntentClassifier()
```

---

## 📊 Evaluation & Metrics

### Model Performance Metrics

```python
# training/scripts/evaluate_model.py
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

def evaluate_intent_classifier(model, test_data):
    predictions = []
    ground_truth = []
    
    for item in test_data:
        pred = model.classify(item['text'])
        predictions.append(pred.value)
        ground_truth.append(item['intent'])
    
    # Classification report
    print(classification_report(ground_truth, predictions))
    
    # Confusion matrix
    cm = confusion_matrix(ground_truth, predictions)
    print("Confusion Matrix:")
    print(cm)
    
    # Calculate accuracy
    accuracy = np.mean(np.array(predictions) == np.array(ground_truth))
    print(f"Accuracy: {accuracy:.2%}")
    
    return {
        'accuracy': accuracy,
        'confusion_matrix': cm.tolist()
    }
```

### Target Metrics
- **Intent Classification:** >95% accuracy
- **Handwriting Recognition:** >90% character accuracy
- **Word Problem Extraction:** >85% correct equations
- **Explanation Generation:** Human evaluation (naturalness score)

---

## 🗂️ Dataset Resources

### Existing Datasets You Can Use

1. **Khmer Language:**
   - KhmerNLP Corpus
   - Khmer Wikipedia dump
   - Open Subtitles Khmer

2. **Mathematical:**
   - MATH dataset (translated to Khmer)
   - GSM8K word problems (translated)
   - ARC challenge (math subset)

3. **Handwriting:**
   - MNIST (for digits 0-9)
   - Create custom Khmer numerals (០-៩) dataset
   - MathWriting dataset

### Data Labeling Tools
- **Label Studio** - Open-source labeling tool
- **Prodigy** - Annotation tool with active learning
- **Amazon SageMaker Ground Truth** - Managed labeling

---

## 💰 Cost Estimate

### One-Time Costs
- **Data Collection:** $2,000 - $5,000 (if hiring labelers)
- **GPU Training:** $500 - $2,000 (cloud GPUs for 2-4 weeks)
- **Model Development:** Your time or $10,000 - $30,000 (if hiring ML engineer)

### Ongoing Costs
- **Model Hosting:** $50 - $200/month (GPU inference)
- **API Calls (if using GPT):** $0.01 - $0.10 per request
- **Data Storage:** $10 - $50/month

### Free/Low-Cost Options
- Use Google Colab for training (free GPU)
- Start with GPT-4 API (pay per use, no training needed)
- Use rule-based system until you have enough data

---

## 🚀 Recommended Roadmap

### Phase 1: Quick Wins (1-2 weeks)
✅ **Use GPT-4 API** for word problem understanding (no training needed)
- Implement as optional feature
- Collect real user data
- Use for data labeling

### Phase 2: Data Collection (1-2 months)
- Build data collection interface
- Partner with Khmer schools for handwriting samples
- Generate synthetic data for intent classification
- Target: 5,000+ labeled examples

### Phase 3: First Model Training (2-4 weeks)
- Fine-tune BERT for intent classification
- Evaluate against rule-based system
- A/B test with real users

### Phase 4: Advanced Features (3-6 months)
- Custom handwriting recognition
- Word problem NLP
- Natural explanation generation

---

## 📝 Best Practices

### 1. Start Simple
- Use rule-based systems first
- Add ML only when you have data and clear improvement
- Keep deterministic solving (never replace SymPy)

### 2. Hybrid Approach
```python
def classify_with_fallback(text: str) -> MathIntent:
    # Try ML model first
    ml_result = ml_classifier.classify(text)
    
    # If confidence is low, use rules
    if ml_result.confidence < 0.8:
        return rule_based_classifier.classify(text)
    
    return ml_result.intent
```

### 3. Continuous Learning
- Log all predictions and corrections
- Periodically retrain with new data
- Monitor model performance in production

### 4. User Feedback Loop
- Add "Was this helpful?" buttons
- Collect corrections from users
- Use feedback for next training iteration

---

## 🔧 Tools & Libraries

### Training
- **Transformers (Hugging Face)** - Pre-trained models
- **PyTorch/TensorFlow** - Deep learning frameworks
- **Scikit-learn** - Traditional ML algorithms

### Data Processing
- **Khmer-nltk** - Khmer NLP utilities
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations

### Deployment
- **FastAPI** - Already using for API
- **TorchServe** - Model serving
- **ONNX** - Model optimization

### Monitoring
- **Weights & Biases** - Experiment tracking
- **MLflow** - ML lifecycle management
- **TensorBoard** - Visualization

---

## ⚠️ Important Warnings

### DO NOT Train AI For:
❌ **Solving equations** - Use SymPy (deterministic)
❌ **Verification** - Use substitution (deterministic)
❌ **Calculating** - Use SymPy (accurate)

### DO Train AI For:
✅ **Understanding questions** - Intent, NLP
✅ **Reading handwriting** - OCR, vision
✅ **Generating explanations** - Natural language
✅ **Detecting problem types** - Classification

---

## 📞 Next Steps

1. **Decide priority:** What do you want to improve first?
2. **Assess data:** Do you have training data or need to collect?
3. **Choose approach:** Rule-based, fine-tuning, or API-based?
4. **Start small:** Implement one feature at a time
5. **Measure impact:** Compare before/after with real users

---

## 📚 Additional Resources

- [Hugging Face Course](https://huggingface.co/course)
- [Fast.ai Practical Deep Learning](https://course.fast.ai/)
- [Khmer NLP Resources](https://github.com/khmer-nlp)
- [TrOCR Paper](https://arxiv.org/abs/2109.10282)
- [BERT for Sequence Classification](https://huggingface.co/docs/transformers/tasks/sequence_classification)

---

**Remember:** The current deterministic approach is a STRENGTH, not a weakness. Only add AI where it improves understanding, not computation!
