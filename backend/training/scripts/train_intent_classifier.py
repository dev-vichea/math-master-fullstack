"""
Khmer & English Math Intent Classifier Training Script
"""
import argparse
from pathlib import Path
import random
import torch
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)

INTENT_LABELS = [
    "solve_equation",
    "evaluate_expression",
    "simplify_expression",
    "unknown",
]
label2id = {name: idx for idx, name in enumerate(INTENT_LABELS)}
id2label = {idx: name for idx, name in enumerate(INTENT_LABELS)}

DEFAULT_SAMPLES = [
    # SOLVE_EQUATION
    ("ដោះស្រាយ 2x + 5 = 15", "solve_equation"),
    ("រកតម្លៃ x នៃសមីការ 3x - 9 = 0", "solve_equation"),
    ("ជួយដោះស្រាយ x^2 - 4 = 0", "solve_equation"),
    ("solve for x: 5x + 10 = 25", "solve_equation"),
    ("find the root of 2x = 8", "solve_equation"),
    ("solve 4x - 7 = 3x + 2", "solve_equation"),
    ("កំណត់តម្លៃ y ពី 2y + 1 = 7", "solve_equation"),
    ("solve equation x + 3 = 10", "solve_equation"),
    # EVALUATE_EXPRESSION
    ("គណនា 25 + 40 * 2", "evaluate_expression"),
    ("គិតតម្លៃ 3/4 + 1/2", "evaluate_expression"),
    ("តើ 15 ភាគរយ នៃ 200 ស្មើប៉ុន្មាន", "evaluate_expression"),
    ("evaluate 12 * (5 + 3)", "evaluate_expression"),
    ("calculate 100 / 4 + 7", "evaluate_expression"),
    ("compute 2^3 + 5", "evaluate_expression"),
    ("what is 50% of 80", "evaluate_expression"),
    ("គណនាតម្លៃ 10 - 3 * 2", "evaluate_expression"),
    # SIMPLIFY_EXPRESSION
    ("សម្រួលកន្សោម 2(x + 3) + 4x", "simplify_expression"),
    ("បង្រួមកន្សោម 3x + 5x - 2x", "simplify_expression"),
    ("simplify 4x + 7x - 2", "simplify_expression"),
    ("reduce the fraction 18/24", "simplify_expression"),
    ("simplify (x^2 - 4)/(x - 2)", "simplify_expression"),
    ("សម្រួល (x + 1)(x - 1)", "simplify_expression"),
    # UNKNOWN
    ("សួស្តី តើអ្នកសុខសប្បាយជាទេ?", "unknown"),
    ("តើអ្នកជានរណា?", "unknown"),
    ("hello how are you", "unknown"),
    ("who created this math app", "unknown"),
]


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=1)
    acc = np.mean(preds == labels)
    return {"accuracy": float(acc)}


def main():
    parser = argparse.ArgumentParser(description="Train Intent Classifier")
    parser.add_argument("--model-name", default="bert-base-multilingual-cased", help="Base pretrained model checkpoint")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--output-dir", default="./models/intent_classifier", help="Directory to save model")
    args = parser.parse_args()

    print(f"Preparing dataset with {len(DEFAULT_SAMPLES)} examples...")
    samples = [{"text": text, "label": label2id[intent]} for text, intent in DEFAULT_SAMPLES]
    random.seed(42)
    random.shuffle(samples)

    split = int(len(samples) * 0.8)
    train_dataset = Dataset.from_list(samples[:split])
    val_dataset = Dataset.from_list(samples[split:])

    print(f"Loading tokenizer & model: {args.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=len(INTENT_LABELS),
        id2label=id2label,
        label2id=label2id,
    )

    def tokenize_fn(batch):
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=64)

    tokenized_train = train_dataset.map(tokenize_fn, batched=True)
    tokenized_val = val_dataset.map(tokenize_fn, batched=True)

    training_args = TrainingArguments(
        output_dir=f"{args.output_dir}_checkpoints",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        logging_steps=5,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        compute_metrics=compute_metrics,
    )

    print("Training intent classifier...")
    trainer.train()

    final_dir = Path(args.output_dir) / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    print(f"Model saved successfully to: {final_dir}")


if __name__ == "__main__":
    main()
