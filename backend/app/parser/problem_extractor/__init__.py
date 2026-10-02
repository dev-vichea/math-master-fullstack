"""
Problem extractor module for detecting and extracting problems from text.

Identifies problem labels (a), b), ក., ខ., etc.) and their associated
mathematical expressions, building structured Problem objects.
"""

from app.parser.problem_extractor.problem_extractor import ProblemExtractor

__all__ = [
    "ProblemExtractor",
]
