"""
Instruction detector for mathematical instructions.

Detects and parses mathematical instructions from text,
identifying the action, target objects, and constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.document import Instruction, InstructionType
from app.parser.instruction_parser.vocabulary import KhmerMathVocabulary, MathAction


@dataclass
class ParsedInstruction:
    """Result of instruction parsing."""

    text: str  # Original instruction text
    action: MathAction  # Detected action
    language: str  # "km" or "en"
    confidence: float  # Detection confidence (0.0 to 1.0)

    # Detected components
    target_objects: list[str] = field(default_factory=list)  # e.g., ["equation", "polynomial"]
    modifiers: list[str] = field(default_factory=list)  # e.g., ["following", "completely"]
    matched_keywords: list[str] = field(default_factory=list)  # Keywords that matched

    def to_instruction(self) -> Instruction:
        """Convert to Instruction model."""
        # Map MathAction to InstructionType
        action_to_type = {
            MathAction.SOLVE: InstructionType.SOLVE,
            MathAction.FACTOR: InstructionType.FACTOR,
            MathAction.SIMPLIFY: InstructionType.SIMPLIFY,
            MathAction.EXPAND: InstructionType.EXPAND,
            MathAction.EVALUATE: InstructionType.EVALUATE,
            MathAction.CALCULATE: InstructionType.EVALUATE,
            MathAction.FIND: InstructionType.FIND,
            MathAction.PROVE: InstructionType.PROVE,
            MathAction.COMPARE: InstructionType.COMPARE,
            MathAction.GRAPH: InstructionType.GRAPH,
            MathAction.DETERMINE: InstructionType.FIND,
            MathAction.VERIFY: InstructionType.PROVE,
            MathAction.SHOW: InstructionType.PROVE,
            MathAction.DERIVE: InstructionType.DERIVATIVE,
            MathAction.TRANSFORM: InstructionType.SIMPLIFY,
        }

        instruction_type = action_to_type.get(self.action, InstructionType.UNKNOWN)

        # Calculus instruction refinement (integrals, derivatives, differential equations)
        if any(k in self.text.lower() for k in ("ឌីផេរ៉ង់ស្យែល", "differential")):
            instruction_type = InstructionType.DIFFERENTIAL_EQUATION
        elif any(k in self.text.lower() for k in ("អាំងតេក្រាល", "ព្រីមីទីវ", "integral", "antiderivative")):
            instruction_type = InstructionType.INTEGRAL
        elif any(k in self.text.lower() for k in ("ដេរីវេ", "derivative", "differentiate")):
            instruction_type = InstructionType.DERIVATIVE

        # Sequence-specific instruction refinement
        if "sequence" in self.target_objects:
            if any(k in self.text for k in ("រួម", "រីក", "convergen")):
                instruction_type = InstructionType.CONVERGENCE
            elif instruction_type in (InstructionType.FIND, InstructionType.UNKNOWN):
                instruction_type = InstructionType.SEQUENCE

        return Instruction(
            text=self.text,
            language=self.language,
            instruction_type=instruction_type,
            confidence=self.confidence,
            detected_keywords=self.matched_keywords,
        )



class InstructionDetector:
    """
    Detect and parse mathematical instructions.

    Uses the Khmer math vocabulary knowledge base to identify
    mathematical actions, target objects, and modifiers.
    """

    def __init__(self):
        """Initialize instruction detector."""
        self.vocab = KhmerMathVocabulary()

    def detect(self, text: str, language: str | None = None) -> ParsedInstruction | None:
        """
        Detect and parse mathematical instruction from text.

        Args:
            text: Instruction text to parse
            language: Language hint ("km" or "en"), auto-detected if None

        Returns:
            ParsedInstruction if detected, None otherwise
        """
        if not text or not text.strip():
            return None

        text = text.strip()

        # Auto-detect language if not provided
        if language is None:
            language = self._detect_language(text)

        # Get patterns for language
        patterns = self.vocab.get_patterns_by_language(language)

        # Try to match patterns
        best_match = None
        best_score = 0.0

        for pattern in patterns:
            score, matched_keywords = self._score_pattern(text, pattern)
            if score > best_score:
                best_score = score
                best_match = (pattern, matched_keywords)

        if best_match is None or best_score < 0.3:
            return None

        pattern, matched_keywords = best_match

        # Extract target objects and modifiers
        target_objects = self._extract_objects(text, language)
        modifiers = self._extract_modifiers(text, language)

        return ParsedInstruction(
            text=text,
            action=pattern.action,
            language=language,
            confidence=min(best_score, 1.0),
            target_objects=target_objects,
            modifiers=modifiers,
            matched_keywords=matched_keywords,
        )

    def _detect_language(self, text: str) -> str:
        """Auto-detect language from text."""
        # Count Khmer characters
        khmer_chars = sum(1 for c in text if "\u1780" <= c <= "\u17FF")
        total_chars = len(text.replace(" ", ""))

        if total_chars == 0:
            return "en"

        # If more than 30% Khmer characters, consider it Khmer
        ratio = khmer_chars / total_chars
        return "km" if ratio > 0.3 else "en"

    def _score_pattern(self, text: str, pattern) -> tuple[float, list[str]]:
        """
        Score how well a pattern matches the text.

        Uses exact matching + fuzzy matching for OCR error tolerance.

        Returns:
            Tuple of (score, matched_keywords)
        """
        text_lower = text.lower()
        score = 0.0
        matched_keywords = []

        # Check primary keywords (exact + fuzzy)
        for keyword in pattern.keywords:
            # Exact match
            if keyword.lower() in text_lower or keyword in text:
                score += 1.0
                matched_keywords.append(keyword)
            # Fuzzy match (for OCR errors)
            elif self._fuzzy_contains(text, keyword):
                score += 0.8  # Slightly lower score for fuzzy match
                matched_keywords.append(keyword)

        # Check synonyms (worth less than primary keywords)
        if pattern.synonyms:
            for synonym in pattern.synonyms:
                if synonym.lower() in text_lower or synonym in text:
                    score += 0.5
                    matched_keywords.append(synonym)
                elif self._fuzzy_contains(text, synonym):
                    score += 0.4
                    matched_keywords.append(synonym)

        # Check context words (boost score)
        if pattern.context_words:
            for context_word in pattern.context_words:
                if context_word.lower() in text_lower or context_word in text:
                    score += 0.2

        return score, matched_keywords

    def _fuzzy_contains(self, text: str, keyword: str, threshold: float = 0.75) -> bool:
        """
        Check if keyword is contained in text with fuzzy matching.

        Uses character-level similarity to handle OCR errors.
        Sliding window approach to find best match.

        Args:
            text: Text to search in
            keyword: Keyword to find
            threshold: Minimum similarity ratio (0.0 to 1.0)

        Returns:
            True if fuzzy match found above threshold
        """
        if not keyword or not text:
            return False

        keyword_len = len(keyword)
        text_len = len(text)

        if keyword_len > text_len:
            return False

        # Try all windows of size keyword_len in text
        best_similarity = 0.0

        for i in range(text_len - keyword_len + 1):
            window = text[i : i + keyword_len]
            similarity = self._character_similarity(window, keyword)
            best_similarity = max(best_similarity, similarity)

            if best_similarity >= threshold:
                return True

        return False

    def _character_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate character-level similarity between two strings.

        Uses a simple character overlap ratio.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        # Normalize to lowercase for comparison
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        if s1_lower == s2_lower:
            return 1.0

        # Count matching characters in order
        matches = 0
        max_len = max(len(s1), len(s2))

        for i in range(min(len(s1), len(s2))):
            if s1_lower[i] == s2_lower[i]:
                matches += 1

        # Penalize length difference
        len_diff_penalty = abs(len(s1) - len(s2)) / max_len

        return (matches / max_len) * (1.0 - len_diff_penalty * 0.5)

    def _extract_objects(self, text: str, language: str) -> list[str]:
        """Extract mathematical objects mentioned in the text."""
        objects = []
        text_lower = text.lower()

        # Get object dictionary for language
        if language == "km":
            object_dict = self.vocab.MATH_OBJECTS_KM
        else:
            object_dict = self.vocab.MATH_OBJECTS_EN

        # Check for each object type
        for obj_type, keywords in object_dict.items():
            for keyword in keywords:
                if keyword.lower() in text_lower or keyword in text:
                    objects.append(obj_type)
                    break

        return objects

    def _extract_modifiers(self, text: str, language: str) -> list[str]:
        """Extract modifier words from the text."""
        modifiers = []
        text_lower = text.lower()

        # Get modifier dictionary for language
        if language == "km":
            modifier_dict = self.vocab.MODIFIERS_KM
        else:
            modifier_dict = self.vocab.MODIFIERS_EN

        # Check for each modifier type
        for mod_type, keywords in modifier_dict.items():
            for keyword in keywords:
                if keyword.lower() in text_lower or keyword in text:
                    modifiers.append(mod_type)
                    break

        return modifiers

    def detect_all(self, texts: list[str], language: str | None = None) -> list[ParsedInstruction]:
        """
        Detect instructions from multiple texts.

        Args:
            texts: List of instruction texts
            language: Language hint, auto-detected if None

        Returns:
            List of ParsedInstruction (only successful detections)
        """
        results = []
        for text in texts:
            parsed = self.detect(text, language)
            if parsed:
                results.append(parsed)
        return results

    def is_instruction(self, text: str, language: str | None = None) -> bool:
        """
        Check if text contains a mathematical instruction.

        Args:
            text: Text to check
            language: Language hint

        Returns:
            True if instruction detected
        """
        parsed = self.detect(text, language)
        return parsed is not None and parsed.confidence >= 0.5
