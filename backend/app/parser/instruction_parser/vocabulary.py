"""
Khmer mathematical vocabulary knowledge base.

Comprehensive dictionary of Khmer mathematical terms, instructions,
and their English equivalents with variations and synonyms.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MathAction(str, Enum):
    """Mathematical actions/instructions."""

    SOLVE = "solve"  # Find solution to equation/system
    FACTOR = "factor"  # Factor expression into products
    SIMPLIFY = "simplify"  # Simplify/reduce expression
    EXPAND = "expand"  # Expand expression
    EVALUATE = "evaluate"  # Calculate numerical value
    FIND = "find"  # Find specific value/quantity
    PROVE = "prove"  # Prove/demonstrate statement
    COMPARE = "compare"  # Compare expressions/values
    GRAPH = "graph"  # Draw graph/plot
    CALCULATE = "calculate"  # Perform calculation
    DETERMINE = "determine"  # Determine value/property
    VERIFY = "verify"  # Check/verify result
    SHOW = "show"  # Show/demonstrate
    DERIVE = "derive"  # Derive formula/expression
    TRANSFORM = "transform"  # Transform expression


@dataclass
class InstructionPattern:
    """Pattern for matching mathematical instructions."""

    keywords: list[str]  # Primary keywords
    action: MathAction  # Mathematical action
    language: str  # "km" or "en"
    synonyms: list[str] | None = None  # Alternative keywords
    context_words: list[str] | None = None  # Words that strengthen match


class KhmerMathVocabulary:
    """
    Comprehensive Khmer mathematical vocabulary knowledge base.

    Contains patterns for:
    - Instructions (solve, factor, simplify, etc.)
    - Mathematical objects (equation, polynomial, expression, etc.)
    - Mathematical operations and concepts
    - Common modifiers and constraints
    """

    # Instruction patterns (Khmer)
    INSTRUCTION_PATTERNS_KM = [
        # Solve (ដោះស្រាយ, រក)
        InstructionPattern(
            keywords=["ដោះស្រាយ"],
            action=MathAction.SOLVE,
            language="km",
            synonyms=["ស្វែងរក", "ស្វែងយក"],
            context_words=["សមីការ", "ប្រព័ន្ធ", "អញ្ញាត"],
        ),
        InstructionPattern(
            keywords=["រក"],
            action=MathAction.FIND,
            language="km",
            synonyms=["រកតម្លៃ", "រកចម្លើយ"],
            context_words=["តម្លៃ", "ចម្លើយ", "លទ្ធផល"],
        ),
        # Factor (ដាក់ជាកត្តាកត់)
        InstructionPattern(
            keywords=["ដាក់ជាកត្តាកត់"],
            action=MathAction.FACTOR,
            language="km",
            synonyms=["កត្តាកត់", "បំបែកជាកត្តា", "ដាក់កត្តា", "ដាក់ជាផលគុណកត្តា", "ដាក់ជាផលគណកតា"],
            context_words=["ពហុធា", "កន្សោម", "រូបមន្ត", "ផលគុណ"],
        ),
        # Simplify (សង្ខេប, សង្រួត)
        InstructionPattern(
            keywords=["សង្ខេប"],
            action=MathAction.SIMPLIFY,
            language="km",
            synonyms=["សង្រួត", "សាមញ្ញ", "កាត់បន្ថយ"],
            context_words=["កន្សោម", "ប្រភាគ", "រូបមន្ត"],
        ),
        # Expand (បង្ហាញ, ពន្លា)
        InstructionPattern(
            keywords=["បង្ហាញ"],
            action=MathAction.EXPAND,
            language="km",
            synonyms=["ពន្លា", "បង្កើត"],
            context_words=["កន្សោម", "ពហុធា"],
        ),
        InstructionPattern(
            keywords=["ពន្លា"],
            action=MathAction.EXPAND,
            language="km",
            synonyms=["បង្ហាញ", "ពង្រីក"],
        ),
        # Calculate/Evaluate (គណនា, គិត)
        InstructionPattern(
            keywords=["គណនា"],
            action=MathAction.CALCULATE,
            language="km",
            synonyms=["គិត", "គណនី"],
            context_words=["តម្លៃ", "លទ្ធផល", "ចម្លើយ"],
        ),
        InstructionPattern(
            keywords=["គិត"],
            action=MathAction.CALCULATE,
            language="km",
            synonyms=["គណនា", "បូក", "គុណ"],
        ),
        # Prove (បង្ហាញថា, បញ្ជាក់)
        InstructionPattern(
            keywords=["បង្ហាញថា"],
            action=MathAction.PROVE,
            language="km",
            synonyms=["បញ្ជាក់", "ប្រាប់"],
            context_words=["ថា", "គឺ", "ស្មើ"],
        ),
        InstructionPattern(
            keywords=["បញ្ជាក់"],
            action=MathAction.PROVE,
            language="km",
            synonyms=["បង្ហាញថា", "ពន្យល់"],
        ),
        # Compare (ប្រៀបធៀប)
        InstructionPattern(
            keywords=["ប្រៀបធៀប"],
            action=MathAction.COMPARE,
            language="km",
            synonyms=["ធៀប"],
            context_words=["និង", "ជាមួយ", "ឬ"],
        ),
        # Graph (គូរ, គូរក្រាប)
        InstructionPattern(
            keywords=["គូរក្រាប"],
            action=MathAction.GRAPH,
            language="km",
            synonyms=["គូរ", "ពណ៌នា"],
            context_words=["ក្រាប", "អ័ក្ស", "កូអរដោណេ"],
        ),
        InstructionPattern(
            keywords=["គូរ"],
            action=MathAction.GRAPH,
            language="km",
            context_words=["ក្រាប", "គំនូស", "ផ្ទាំង"],
        ),
        # Determine (កំណត់)
        InstructionPattern(
            keywords=["កំណត់"],
            action=MathAction.DETERMINE,
            language="km",
            synonyms=["ស្វែងរក"],
            context_words=["តម្លៃ", "លក្ខណៈ"],
        ),
        # Verify (ពិនិត្យ)
        InstructionPattern(
            keywords=["ពិនិត្យ"],
            action=MathAction.VERIFY,
            language="km",
            synonyms=["ត្រួតពិនិត្យ", "ពិនិត្យមើល"],
            context_words=["ថា", "ចម្លើយ", "លទ្ធផល"],
        ),
        # Derivative (គណនាដេរីវេ, រកដេរីវេ, ដេរីវេ)
        InstructionPattern(
            keywords=["ដេរីវេ"],
            action=MathAction.DERIVE,
            language="km",
            synonyms=["គណនាដេរីវេ", "រកដេរីវេ", "ដេរីវេនៃអនុគមន៍", "គណនាដេរីវេនៃអនុគមន៍"],
            context_words=["អនុគមន៍", "កន្សោម", "ខាងក្រោម"],
        ),
        # Sequence & Convergence (ស្វ៊ីត, សិក្សាភាពរួម ឬរីក)
        InstructionPattern(
            keywords=["ស្វ៊ីត"],
            action=MathAction.DETERMINE,
            language="km",
            synonyms=["ស្វិត", "ភាពរួម", "ស្វ៊ីតរួម", "ស្វ៊ីតរីក", "រួម ឬរីក", "រួមឬរីក"],
            context_words=["តួទូទៅ", "ខាងក្រោម", "កំណត់", "លីមីត"],
        ),
    ]

    # Instruction patterns (English)
    INSTRUCTION_PATTERNS_EN = [

        InstructionPattern(
            keywords=["solve"],
            action=MathAction.SOLVE,
            language="en",
            synonyms=["find the solution", "determine the solution"],
            context_words=["equation", "system", "for"],
        ),
        InstructionPattern(
            keywords=["factor"],
            action=MathAction.FACTOR,
            language="en",
            synonyms=["factorize", "factorise"],
            context_words=["polynomial", "expression", "completely"],
        ),
        InstructionPattern(
            keywords=["simplify"],
            action=MathAction.SIMPLIFY,
            language="en",
            synonyms=["reduce", "simplify fully"],
            context_words=["expression", "fraction", "radical"],
        ),
        InstructionPattern(
            keywords=["expand"],
            action=MathAction.EXPAND,
            language="en",
            synonyms=["multiply out", "expand fully"],
            context_words=["expression", "polynomial", "brackets"],
        ),
        InstructionPattern(
            keywords=["evaluate"],
            action=MathAction.EVALUATE,
            language="en",
            synonyms=["calculate", "compute", "find the value"],
            context_words=["value", "when", "for"],
        ),
        InstructionPattern(
            keywords=["calculate"],
            action=MathAction.CALCULATE,
            language="en",
            synonyms=["compute", "work out"],
            context_words=["value", "result", "answer"],
        ),
        InstructionPattern(
            keywords=["find"],
            action=MathAction.FIND,
            language="en",
            synonyms=["determine", "obtain"],
            context_words=["value", "solution", "answer"],
        ),
        InstructionPattern(
            keywords=["prove"],
            action=MathAction.PROVE,
            language="en",
            synonyms=["show that", "demonstrate", "verify"],
            context_words=["that", "is", "equals"],
        ),
        InstructionPattern(
            keywords=["compare"],
            action=MathAction.COMPARE,
            language="en",
            synonyms=["contrast"],
            context_words=["with", "and", "or"],
        ),
        InstructionPattern(
            keywords=["graph"],
            action=MathAction.GRAPH,
            language="en",
            synonyms=["plot", "draw", "sketch"],
            context_words=["function", "equation", "curve"],
        ),
        InstructionPattern(
            keywords=["determine"],
            action=MathAction.DETERMINE,
            language="en",
            synonyms=["find", "establish"],
            context_words=["value", "nature", "type"],
        ),
        InstructionPattern(
            keywords=["verify"],
            action=MathAction.VERIFY,
            language="en",
            synonyms=["check", "confirm"],
            context_words=["that", "whether", "solution"],
        ),
        InstructionPattern(
            keywords=["show"],
            action=MathAction.SHOW,
            language="en",
            synonyms=["demonstrate", "prove"],
            context_words=["that", "how", "why"],
        ),
        InstructionPattern(
            keywords=["derive"],
            action=MathAction.DERIVE,
            language="en",
            synonyms=["obtain", "deduce"],
            context_words=["formula", "expression", "equation"],
        ),
        InstructionPattern(
            keywords=["differentiate", "derivative"],
            action=MathAction.DERIVE,
            language="en",
            synonyms=["find the derivative", "calculate the derivative", "compute the derivative", "take derivative"],
            context_words=["function", "expression", "with respect to", "following"],
        ),
    ]

    # Mathematical objects (Khmer)
    MATH_OBJECTS_KM = {
        "equation": ["សមីការ", "សមីការណ៍"],
        "polynomial": ["ពហុធា", "ពហុនាម"],
        "expression": ["កន្សោម", "រូបមន្ត"],
        "system": ["ប្រព័ន្ធ", "ប្រព័ន្ធសមីការ"],
        "fraction": ["ប្រភាគ", "ប្រភាគសន្ទស្ស"],
        "function": ["អនុគមន៍", "អនុគមន៍"],
        "inequality": ["វីសមភាព", "វិសមភាព"],
        "limit": ["លីមីត", "កំណត់"],
        "derivative": ["ដេរីវេ", "អនុគមន៍"],
        "integral": ["អាំងតេក្រាល", "សមាមាត្រ"],
        "sequence": ["ស្វ៊ីត", "ស្វិត", "ស្វ៊ីតចំនួនពិត"],
        "recurrence": ["ទំនាក់ទំនងដំណាល", "ដំណាល"],
        "matrix": ["ម៉ាទ្រីស", "តារាង"],
        "vector": ["វ៉ិចទ័រ", "វ៉ិចទ័រ"],
        "variable": ["អញ្ញាត", "តម្រូវ"],
        "coefficient": ["មេគុណ", "ធានាគុណ"],
        "constant": ["អថេរ", "ថេរ"],
    }

    # Mathematical objects (English)
    MATH_OBJECTS_EN = {
        "equation": ["equation", "equations"],
        "polynomial": ["polynomial", "polynomials"],
        "expression": ["expression", "expressions"],
        "system": ["system", "systems"],
        "fraction": ["fraction", "fractions"],
        "function": ["function", "functions"],
        "inequality": ["inequality", "inequalities"],
        "limit": ["limit", "limits"],
        "derivative": ["derivative", "derivatives"],
        "integral": ["integral", "integrals"],
        "sequence": ["sequence", "sequences"],
        "recurrence": ["recurrence", "recurrence relation"],
        "matrix": ["matrix", "matrices"],
        "vector": ["vector", "vectors"],
        "variable": ["variable", "variables", "unknown", "unknowns"],
        "coefficient": ["coefficient", "coefficients"],
        "constant": ["constant", "constants"],
    }


    # Modifier words (Khmer)
    MODIFIERS_KM = {
        "following": ["ខាងក្រោម", "ដូចខាងក្រោម", "ដែលតទៅ"],
        "given": ["ដែលបានឲ្យ", "ដែលកំណត់", "ដែលមាន"],
        "each": ["នីមួយៗ", "នីមួយ", "ទាំងអស់"],
        "all": ["ទាំងអស់", "គ្រប់", "ទាំងមូល"],
        "complete": ["ពេញលេញ", "ទាំងស្រុង", "គ្រប់ផ្នែក"],
        "fully": ["ពេញលេញ", "ទាំងស្រុង"],
        "below": ["ខាងក្រោម", "ក្រោម"],
        "above": ["ខាងលើ", "លើ"],
    }

    # Modifier words (English)
    MODIFIERS_EN = {
        "following": ["following", "below", "given below"],
        "given": ["given", "provided", "shown"],
        "each": ["each", "every", "all"],
        "all": ["all", "every"],
        "complete": ["complete", "completely", "full", "fully"],
        "fully": ["fully", "completely", "entirely"],
        "below": ["below", "following"],
        "above": ["above", "preceding"],
    }

    @classmethod
    def get_all_patterns(cls) -> list[InstructionPattern]:
        """Get all instruction patterns (Khmer and English)."""
        return cls.INSTRUCTION_PATTERNS_KM + cls.INSTRUCTION_PATTERNS_EN

    @classmethod
    def get_patterns_by_language(cls, language: str) -> list[InstructionPattern]:
        """Get instruction patterns for specific language."""
        if language == "km":
            return cls.INSTRUCTION_PATTERNS_KM
        elif language == "en":
            return cls.INSTRUCTION_PATTERNS_EN
        else:
            return cls.get_all_patterns()

    @classmethod
    def get_patterns_by_action(cls, action: MathAction) -> list[InstructionPattern]:
        """Get all patterns for a specific action."""
        return [p for p in cls.get_all_patterns() if p.action == action]
