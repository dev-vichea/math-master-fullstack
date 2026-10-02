"""
OCR evaluation and testing utilities.

Provides tools for:
- Comparing OCR results against ground truth
- Calculating accuracy metrics (CER, WER, exact match)
- Benchmarking multiple OCR engines
- Generating evaluation reports
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import Levenshtein

from app.core.logging import get_logger
from app.ocr.extraction.base import MathVisionEngine

logger = get_logger("app.ocr.extraction.evaluation")


@dataclass
class OCRMetrics:
    """Metrics for evaluating OCR performance."""

    exact_match: bool
    character_error_rate: float  # CER: edit distance / reference length
    word_error_rate: float  # WER: word-level edit distance
    confidence_score: float
    processing_time_ms: float
    detected_text: str | None
    reference_text: str
    error_message: str | None = None


class OCREvaluator:
    """Evaluates OCR engine performance against ground truth."""

    @staticmethod
    def calculate_cer(reference: str, hypothesis: str) -> float:
        """
        Calculate Character Error Rate (CER).

        CER = (insertions + deletions + substitutions) / len(reference)
        """
        if not reference:
            return 0.0 if not hypothesis else 1.0

        distance = Levenshtein.distance(reference, hypothesis)
        return distance / len(reference)

    @staticmethod
    def calculate_wer(reference: str, hypothesis: str) -> float:
        """
        Calculate Word Error Rate (WER).

        WER = word_edit_distance / number_of_words_in_reference
        """
        ref_words = reference.split()
        hyp_words = hypothesis.split()

        if not ref_words:
            return 0.0 if not hyp_words else 1.0

        distance = Levenshtein.distance(ref_words, hyp_words)
        return distance / len(ref_words)

    @staticmethod
    def evaluate_single(
        engine: MathVisionEngine,
        image_bytes: bytes,
        ground_truth: str,
    ) -> OCRMetrics:
        """
        Evaluate OCR engine on a single image.

        Args:
            engine: OCR engine to evaluate
            image_bytes: Image data
            ground_truth: Expected text output

        Returns:
            OCRMetrics with performance metrics
        """
        # Time the detection
        start_time = time.time()

        try:
            result = engine.detect(image_bytes)
            processing_time = (time.time() - start_time) * 1000  # milliseconds

            if result.error_message or not result.detected_text:
                return OCRMetrics(
                    exact_match=False,
                    character_error_rate=1.0,
                    word_error_rate=1.0,
                    confidence_score=0.0,
                    processing_time_ms=processing_time,
                    detected_text=result.detected_text,
                    reference_text=ground_truth,
                    error_message=result.error_message,
                )

            # Calculate metrics
            detected = result.detected_text.strip()
            reference = ground_truth.strip()

            exact_match = detected == reference
            cer = OCREvaluator.calculate_cer(reference, detected)
            wer = OCREvaluator.calculate_wer(reference, detected)

            return OCRMetrics(
                exact_match=exact_match,
                character_error_rate=cer,
                word_error_rate=wer,
                confidence_score=result.confidence,
                processing_time_ms=processing_time,
                detected_text=detected,
                reference_text=reference,
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"OCR evaluation failed: {e}")

            return OCRMetrics(
                exact_match=False,
                character_error_rate=1.0,
                word_error_rate=1.0,
                confidence_score=0.0,
                processing_time_ms=processing_time,
                detected_text=None,
                reference_text=ground_truth,
                error_message=str(e),
            )

    @staticmethod
    def evaluate_dataset(
        engine: MathVisionEngine,
        test_cases: list[tuple[bytes, str]],
    ) -> dict[str, Any]:
        """
        Evaluate OCR engine on a dataset of test cases.

        Args:
            engine: OCR engine to evaluate
            test_cases: List of (image_bytes, ground_truth) tuples

        Returns:
            Dictionary with aggregate metrics and per-sample results
        """
        results = []

        for i, (image_bytes, ground_truth) in enumerate(test_cases):
            logger.info(f"Evaluating test case {i + 1}/{len(test_cases)}")
            metrics = OCREvaluator.evaluate_single(engine, image_bytes, ground_truth)
            results.append(metrics)

        # Calculate aggregate metrics
        total_samples = len(results)
        exact_matches = sum(1 for r in results if r.exact_match)

        avg_cer = sum(r.character_error_rate for r in results) / total_samples
        avg_wer = sum(r.word_error_rate for r in results) / total_samples
        avg_confidence = sum(r.confidence_score for r in results) / total_samples
        avg_time = sum(r.processing_time_ms for r in results) / total_samples

        errors = [r for r in results if r.error_message]

        return {
            "total_samples": total_samples,
            "exact_matches": exact_matches,
            "accuracy": exact_matches / total_samples if total_samples > 0 else 0.0,
            "average_cer": avg_cer,
            "average_wer": avg_wer,
            "average_confidence": avg_confidence,
            "average_processing_time_ms": avg_time,
            "error_count": len(errors),
            "error_rate": len(errors) / total_samples if total_samples > 0 else 0.0,
            "results": results,
        }


class OCRBenchmark:
    """Benchmark multiple OCR engines on the same dataset."""

    @staticmethod
    def compare_engines(
        engines: dict[str, MathVisionEngine],
        test_cases: list[tuple[bytes, str]],
    ) -> dict[str, Any]:
        """
        Compare multiple OCR engines on the same test dataset.

        Args:
            engines: Dict mapping engine names to engine instances
            test_cases: List of (image_bytes, ground_truth) tuples

        Returns:
            Comparison report with metrics for each engine
        """
        comparison = {}

        for engine_name, engine in engines.items():
            logger.info(f"Benchmarking engine: {engine_name}")

            eval_results = OCREvaluator.evaluate_dataset(engine, test_cases)
            comparison[engine_name] = eval_results

        # Generate summary
        summary = {
            "engines_tested": list(engines.keys()),
            "total_test_cases": len(test_cases),
            "results_by_engine": comparison,
        }

        # Find best engine for each metric
        if comparison:
            best_accuracy = max(comparison.items(), key=lambda x: x[1]["accuracy"])
            best_cer = min(comparison.items(), key=lambda x: x[1]["average_cer"])
            best_speed = min(comparison.items(), key=lambda x: x[1]["average_processing_time_ms"])

            summary["best_accuracy"] = {
                "engine": best_accuracy[0],
                "accuracy": best_accuracy[1]["accuracy"],
            }
            summary["best_cer"] = {
                "engine": best_cer[0],
                "cer": best_cer[1]["average_cer"],
            }
            summary["best_speed"] = {
                "engine": best_speed[0],
                "time_ms": best_speed[1]["average_processing_time_ms"],
            }

        return summary

    @staticmethod
    def generate_report(comparison: dict[str, Any]) -> str:
        """
        Generate a human-readable benchmark report.

        Args:
            comparison: Results from compare_engines()

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("OCR ENGINE BENCHMARK REPORT")
        lines.append("=" * 80)
        lines.append(f"Engines tested: {', '.join(comparison['engines_tested'])}")
        lines.append(f"Total test cases: {comparison['total_test_cases']}")
        lines.append("")

        # Engine comparison table
        lines.append("PERFORMANCE COMPARISON:")
        lines.append("-" * 80)
        lines.append(
            f"{'Engine':<20} {'Accuracy':<12} {'Avg CER':<12} {'Avg WER':<12} {'Avg Time (ms)':<15}"
        )
        lines.append("-" * 80)

        for engine_name, results in comparison["results_by_engine"].items():
            lines.append(
                f"{engine_name:<20} "
                f"{results['accuracy']:>10.2%}  "
                f"{results['average_cer']:>10.4f}  "
                f"{results['average_wer']:>10.4f}  "
                f"{results['average_processing_time_ms']:>13.2f}"
            )

        lines.append("-" * 80)
        lines.append("")

        # Best performers
        lines.append("BEST PERFORMERS:")
        lines.append(
            f"  Best Accuracy: {comparison['best_accuracy']['engine']} "
            f"({comparison['best_accuracy']['accuracy']:.2%})"
        )
        lines.append(
            f"  Best CER: {comparison['best_cer']['engine']} ({comparison['best_cer']['cer']:.4f})"
        )
        lines.append(
            f"  Fastest: {comparison['best_speed']['engine']} "
            f"({comparison['best_speed']['time_ms']:.2f} ms)"
        )
        lines.append("")

        # Error analysis
        lines.append("ERROR ANALYSIS:")
        for engine_name, results in comparison["results_by_engine"].items():
            lines.append(
                f"  {engine_name}: {results['error_count']} errors ({results['error_rate']:.2%})"
            )

        lines.append("=" * 80)

        return "\n".join(lines)


def load_test_cases_from_directory(directory: Path) -> list[tuple[bytes, str]]:
    """
    Load test cases from a directory structure.

    Expected structure:
        test_data/
            001.png
            001.txt  (ground truth)
            002.jpg
            002.txt
            ...

    Args:
        directory: Path to test data directory

    Returns:
        List of (image_bytes, ground_truth) tuples
    """
    test_cases = []

    # Find all image files
    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    image_files = [f for f in directory.iterdir() if f.suffix.lower() in image_extensions]

    for image_file in sorted(image_files):
        # Look for corresponding .txt file
        txt_file = image_file.with_suffix(".txt")

        if not txt_file.exists():
            logger.warning(f"No ground truth found for {image_file.name}, skipping")
            continue

        try:
            # Read image bytes
            image_bytes = image_file.read_bytes()

            # Read ground truth text
            ground_truth = txt_file.read_text(encoding="utf-8").strip()

            test_cases.append((image_bytes, ground_truth))
            logger.debug(f"Loaded test case: {image_file.name}")

        except Exception as e:
            logger.error(f"Failed to load test case {image_file.name}: {e}")
            continue

    logger.info(f"Loaded {len(test_cases)} test cases from {directory}")
    return test_cases
