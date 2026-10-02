"""
Instruction parser module for mathematical instructions.

Parses and understands mathematical instructions in Khmer and English,
extracting intent, target objects, and constraints.
"""

from app.parser.instruction_parser.instruction_detector import InstructionDetector
from app.parser.instruction_parser.vocabulary import KhmerMathVocabulary

__all__ = [
    "InstructionDetector",
    "KhmerMathVocabulary",
]
