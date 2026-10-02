"""
Bilingual Khmer-English Mathematical Glossary (ពាក្យគន្លឹះគណិតវិទ្យា)
Curated from Cambodian High School Grade 12 BacII & CSCA standards (by CHEANG SOKKONG / EDU-IKH).

Used across the Math Lab pipeline:
- Exercise Parsing & Intent Classification
- Pedagogical Step Explanations (What & Why rationales)
- Bilingual Khmer/English toggles in the frontend
- Logical Connectives for verified step-by-step reasoning
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class GlossaryEntry:
    english: str
    khmer: str
    category: str
    explanation: Optional[str] = None
    symbol: Optional[str] = None
    synonyms: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "english": self.english,
            "khmer": self.khmer,
            "category": self.category,
            "explanation": self.explanation,
            "symbol": self.symbol,
            "synonyms": self.synonyms or [],
        }


# 1. Command Words (ពាក្យបញ្ជាក្នុងប្រធានលំហាត់)
COMMAND_WORDS: Dict[str, str] = {
    "calculate": "គណនា",
    "compute": "គណនា",
    "evaluate": "គណនាតម្លៃ",
    "simplify": "សម្រួល",
    "solve": "ដោះស្រាយ",
    "prove": "ស្រាយបំភ្លឺថា",
    "show that": "បង្ហាញថា",
    "determine": "កំណត់",
    "factor": "ដាក់ជាផលគុណកត្តា",
    "factorise": "ដាក់ជាផលគុណកត្តា",
    "expand": "ពន្លាត",
    "sketch": "សង់រូប / គូសក្រាប",
    "plot": "ដៅចំណុច និងគូសក្រាប",
    "derive": "ទាញរករូបមន្ត / រកដេរីវេ",
    "find the value of": "រកតម្លៃនៃ",
    "express in terms of": "សរសេរជាអនុគមន៍នៃ",
    "verify": "ផ្ទៀងផ្ទាត់",
    "justify": "ផ្តល់ហេតុផល",
    "deduce": "ទាញរក",
    "classify": "ចាត់ថ្នាក់",
    "interpret": "បកស្រាយ",
}

# 2. Logical Connectives (ពាក្យភ្ជាប់ហេតុផលក្នុងដំណោះស្រាយ)
LOGICAL_CONNECTIVES: Dict[str, str] = {
    "let": "តាង",
    "let ... be ...": "តាង ... ជា ...",
    "given that": "គេឱ្យ / ដោយដឹងថា",
    "since": "ដោយសារ",
    "because": "ព្រោះ",
    "therefore": "ដូចនេះ",
    "thus": "ដូចនេះ",
    "hence": "ហេតុនេះ",
    "implies that": "នាំឱ្យ",
    "if and only if": "លុះត្រាតែ",
    "for all": "ចំពោះគ្រប់",
    "for every": "ចំពោះគ្រប់",
    "there exists": "មាន",
    "assume that": "សន្មតថា",
    "substitute": "ជំនួស",
    "compare": "ប្រៀបធៀប",
    "conclusion": "សន្និដ្ឋាន",
}

# 3. Numbers & Fractions (លេខ និង ប្រភាគ)
NUMBERS_GLOSSARY: Dict[str, str] = {
    "integer": "ចំនួនគត់",
    "even number": "ចំនួនគូ",
    "odd number": "ចំនួនសេស",
    "prime number": "ចំនួនបឋម",
    "consecutive numbers": "ចំនួនតគ្នានៃ",
    "fraction": "ប្រភាគ",
    "numerator": "ភាគយក",
    "denominator": "ភាគបែង",
    "decimal": "ចំនួនទសភាគ",
    "percentage": "ភាគរយ",
    "reciprocal": "ចម្រាស់",
    "significant figures": "លេខមានន័យ",
    "round off": "បង្គត់លេខ",
}

# 4. Algebra (ពិជគណិត)
ALGEBRA_GLOSSARY: Dict[str, str] = {
    "sum": "ផលបូក",
    "difference": "ផលដក",
    "product": "ផលគុណ",
    "quotient": "ផលចែក",
    "remainder": "សំណល់",
    "equation": "សមីការ",
    "inequality": "វិសមីការ",
    "variable": "អថេរ",
    "unknown": "អញ្ញាត",
    "coefficient": "មេគុណ",
    "constant": "ចំនួនថេរ",
    "term": "តួ",
    "expression": "កន្សោម",
    "polynomial": "ពហុធា",
    "root": "ឬស",
    "solution": "ចម្លើយ",
    "quadratic": "ដឺក្រេទី ២ (ការ៉េ)",
    "discriminant": "ឌីសគ្រីមីណង់ (Δ)",
    "simultaneous equations": "ប្រព័ន្ធសមីការ",
    "subject of the formula": "អថេរគោល",
    "inverse function": "អនុគមន៍ច្រាស់",
    "composite function": "អនុគមន៍បណ្តាក់",
    "asymptote": "អាស៊ីមតូត",
}

# 5. Geometry (ធរណីមាត្រ)
GEOMETRY_GLOSSARY: Dict[str, str] = {
    "angle": "មុំ",
    "right angle": "មុំកែង",
    "acute angle": "មុំស្រួច",
    "obtuse angle": "មុំទាល",
    "reflex angle": "មុំផ្លាត",
    "vertically opposite angles": "មុំទល់កំពូល",
    "corresponding angles": "មុំត្រូវគ្នា",
    "alternate angles": "មុំឆ្លាស់",
    "triangle": "ត្រីកោណ",
    "isosceles triangle": "ត្រីកោណសមបាត",
    "equilateral triangle": "ត្រីកោណសម័ង្ស",
    "right-angled triangle": "ត្រីកោណកែង",
    "hypotenuse": "អ៊ីប៉ូតេនុស",
    "adjacent side": "ជ្រុងជាប់",
    "opposite side": "ជ្រុងឈម",
    "parallel": "ស្រប",
    "perpendicular": "កែង",
    "perimeter": "បរិមាត្រ",
    "area": "ផ្ទៃក្រឡា",
    "bisector": "កន្លះបន្ទាត់ពុះមុំ / មេដ្យាទ័រ",
    "congruent": "ប៉ុនគ្នា",
    "similar": "ដូចគ្នា",
}

# 6. Shapes & Solids (រូបធរណីមាត្រ និង សូលីដ)
SHAPES_GLOSSARY: Dict[str, str] = {
    "quadrilateral": "ចតុកោណ",
    "parallelogram": "ប្រលេឡូក្រាម",
    "rhombus": "ស្វាយ (ចតុកោណស្មើ)",
    "trapezium": "ចតុកោណព្នាយ",
    "trapezoid": "ចតុកោណព្នាយ",
    "kite": "ចតុកោណខ្លែង",
    "polygon": "ពហុកោណ",
    "hexagon": "ឆកោណ",
    "octagon": "អដ្ឋកោណ",
    "circle": "រង្វង់",
    "radius": "កាំ",
    "diameter": "អង្កត់ផ្ចិត",
    "chord": "អង្កត់ធ្នូ",
    "tangent": "បន្ទាត់ប៉ះ",
    "arc": "ធ្នូ",
    "sector": "ចម្រៀករង្វង់",
    "prism": "ព្រីស",
    "pyramid": "ពីរ៉ាមីត",
    "cylinder": "ស៊ីឡាំង",
    "cone": "កូន",
    "sphere": "ស្វ៊ែរ",
    "volume": "មាឌ",
    "surface area": "ផ្ទៃក្រឡាខាងក្រៅ",
}

# 7. Calculus (គណនា - វិភាគគណិត)
CALCULUS_GLOSSARY: Dict[str, str] = {
    "function": "អនុគមន៍",
    "domain": "ដែនកំណត់",
    "range": "សំណុំរូបភាព",
    "limit": "លីមីត",
    "approaches": "ខិតជិតទៅរក",
    "derivative": "ដេរីវេ",
    "differentiation": "ការរកដេរីវេ",
    "rate of change": "អត្រាបម្រែបម្រួល",
    "chain rule": "រូបមន្តបណ្តាក់",
    "product rule": "រូបមន្តផលគុណ",
    "quotient rule": "រូបមន្តផលចែក",
    "tangent line": "បន្ទាត់ប៉ះ",
    "normal line": "បន្ទាត់កែង",
    "integral": "អាំងតេក្រាល",
    "integration": "ការគណនាអាំងតេក្រាល",
    "definite": "កំណត់",
    "indefinite": "មិនកំណត់",
    "maximum": "អតិបរមា",
    "minimum": "អប្បបរមា",
    "turning point": "ចំណុចបត់",
    "stationary point": "ចំណុចមានដេរីវេស្មើសូន្យ",
    "inflection point": "ចំណុចរបត់",
    "concave up": "ផតអ៊ុតទៅលើ",
    "concave down": "ផតអ៊ុតទៅក្រោម",
}

# 8. Sequences (ស្វ៊ីត - MoEYS Grade 12 BacII)
SEQUENCES_GLOSSARY: Dict[str, str] = {
    "sequence": "ស្វ៊ីត",
    "arithmetic sequence": "ស្វ៊ីតនព្វន្ត",
    "geometric sequence": "ស្វ៊ីតធរណីមាត្រ",
    "common difference": "ផលសងរួម",
    "common ratio": "ផលធៀបរួម",
    "general term": "តួទូទៅ",
    "first term": "តួទីមួយ",
    "recurrence relation": "ទំនាក់ទំនងកំណត់ដោយកំឡើត",
    "convergent sequence": "ស្វ៊ីតរួម",
    "divergent sequence": "ស្វ៊ីតរីក",
    "bounded sequence": "ស្វ៊ីតទាល់",
    "bounded above": "ទាល់លើ",
    "bounded below": "ទាល់ក្រោម",
    "increasing sequence": "ស្វ៊ីតកើន",
    "decreasing sequence": "ស្វ៊ីតចុះ",
    "squeeze theorem": "ទ្រឹស្តីបទញှៀប",
    "sum of n terms": "ផលបូក n តួដំបូង",
}

# 9. Statistics & Probability (ស្ថិតិ និង ប្រូបាប)
STATISTICS_GLOSSARY: Dict[str, str] = {
    "data": "ទិន្នន័យ",
    "mean": "មធ្យម",
    "average": "មធ្យម",
    "median": "មេដ្យាន",
    "mode": "ម៉ូត",
    "range": "គំលាត",
    "frequency": "ប្រេកង់",
    "cumulative frequency": "ប្រេកង់កើន",
    "standard deviation": "គំលាតស្តង់ដា",
    "variance": "វ៉ារ្យង់",
    "probability": "ប្រូបាប",
    "outcome": "លទ្ធផល",
    "event": "ព្រឹត្តិការណ៍",
    "mutually exclusive": "ព្រឹត្តិការណ៍ដាច់ដោយឡែក",
    "independent events": "ព្រឹត្តិការណ៍មិនទាក់ទងគ្នា",
}

# 10. Matrices & Vectors (ម៉ាទ្រីស និង វ៉ិចទ័រ)
MATRICES_GLOSSARY: Dict[str, str] = {
    "matrix": "ម៉ាទ្រីស",
    "row": "ជួរដេក",
    "column": "ជួរឈរ",
    "order": "លំដាប់",
    "dimension": "វិមាត្រ",
    "determinant": "ដេអ៊ែរមីណង់",
    "inverse matrix": "ម៉ាទ្រីសច្រាស់",
    "identity matrix": "ម៉ាទ្រីសឯកតា",
    "vector": "វ៉ិចទ័រ",
    "magnitude": "ម៉ូឌុល",
    "direction": "ទិសដៅ",
    "scalar": "ស្កាលែ",
    "resultant vector": "វ៉ិចទ័រផលបូក",
    "collinear": "កូលីនេអ៊ែរ",
    "dot product": "ផលគុណស្កាលែ",
}

# 11. Sets (សំណុំ)
SETS_GLOSSARY: Dict[str, str] = {
    "set": "សំណុំ",
    "element": "ធាតុ",
    "member": "ធាតុ",
    "subset": "សំណុំរង",
    "universal set": "សំណុំសកល",
    "empty set": "សំណុំទទេ",
    "null set": "សំណុំទទេ",
    "union": "ប្រជុំ",
    "intersection": "ប្រសព្វ",
    "complement": "បំពេញ",
}

# Master Unified Dictionary
ALL_MATH_TERMS: Dict[str, str] = {
    **COMMAND_WORDS,
    **LOGICAL_CONNECTIVES,
    **NUMBERS_GLOSSARY,
    **ALGEBRA_GLOSSARY,
    **GEOMETRY_GLOSSARY,
    **SHAPES_GLOSSARY,
    **CALCULUS_GLOSSARY,
    **SEQUENCES_GLOSSARY,
    **STATISTICS_GLOSSARY,
    **MATRICES_GLOSSARY,
    **SETS_GLOSSARY,
}

# Comprehensive Structured Database with Metadata, Symbols & Context
STRUCTURED_ENTRIES: List[GlossaryEntry] = [
    # 1. Command Words
    GlossaryEntry("Calculate", "គណនា", "Command Words", "Compute numerically or symbolically"),
    GlossaryEntry("Compute", "គណនា", "Command Words", "Compute numerical result"),
    GlossaryEntry("Evaluate", "គណនាតម្លៃ", "Command Words", "Find the numerical value of an expression"),
    GlossaryEntry("Simplify", "សម្រួល", "Command Words", "Reduce an expression to its simplest form"),
    GlossaryEntry("Solve", "ដោះស្រាយ", "Command Words", "Find roots or unknowns satisfying an equation"),
    GlossaryEntry("Prove", "ស្រាយបំភ្លឺថា", "Command Words", "Establish validity through mathematical steps"),
    GlossaryEntry("Show that", "បង្ហាញថា", "Command Words", "Demonstrate truth of a proposition"),
    GlossaryEntry("Determine", "កំណត់", "Command Words", "Find an exact value or condition logically"),
    GlossaryEntry("Factor / Factorise", "ដាក់ជាផលគុណកត្តា", "Command Words", "Write an expression as a product of factors"),
    GlossaryEntry("Expand", "ពន្លាត", "Command Words", "Multiply out brackets / terms"),
    GlossaryEntry("Sketch", "សង់រូប / គូសក្រាប", "Command Words", "Rough diagram showing key features (asymptotes, intercepts)"),
    GlossaryEntry("Plot", "ដៅចំណុច និងគូសក្រាប", "Command Words", "Accurately plot points and graph"),
    GlossaryEntry("Derive", "ទាញរករូបមន្ត / រកដេរីវេ", "Command Words", "Deduce formula or calculate derivative"),
    GlossaryEntry("Find the value of", "រកតម្លៃនៃ", "Command Words", "Compute the exact value of variable or term"),
    GlossaryEntry("Express in terms of", "សរសេរជាអនុគមន៍នៃ", "Command Words", "Rewrite variable as function of another"),
    GlossaryEntry("Verify", "ផ្ទៀងផ្ទាត់", "Command Words", "Check whether a given solution is correct"),
    GlossaryEntry("Justify", "ផ្តល់ហេតុផល", "Command Words", "Provide mathematical reasoning / grounds"),
    GlossaryEntry("Deduce", "ទាញរក", "Command Words", "Derive a result using previous answers"),
    GlossaryEntry("Classify", "ចាត់ថ្នាក់", "Command Words", "Categorize into defined types or sets"),
    GlossaryEntry("Interpret", "បកស្រាយ", "Command Words", "Explain real-world or geometric meaning"),

    # 2. Logical Connectives
    GlossaryEntry("Let ... be ...", "តាង ... ជា ...", "Logical Connectives", "Introduce a variable or assumption"),
    GlossaryEntry("Given that", "គេឱ្យ / ដោយដឹងថា", "Logical Connectives", "Stating problem premises or hypotheses"),
    GlossaryEntry("Since / Because", "ដោយសារ / ព្រោះ", "Logical Connectives", "Reasoning leading into inference"),
    GlossaryEntry("Therefore / Thus / Hence", "ដូចនេះ / ហេតុនេះ", "Logical Connectives", "Logical deduction marker"),
    GlossaryEntry("Implies that", "នាំឱ្យ", "Logical Connectives", "Implication arrow", symbol="⇒"),
    GlossaryEntry("If and only if", "លុះត្រាតែ", "Logical Connectives", "Biconditional equivalence", symbol="⇔"),
    GlossaryEntry("For all / For every", "ចំពោះគ្រប់", "Logical Connectives", "Universal quantifier", symbol="∀"),
    GlossaryEntry("There exists", "មាន", "Logical Connectives", "Existential quantifier", symbol="∃"),
    GlossaryEntry("Assume that", "សន្មតថា", "Logical Connectives", "Hypothesis in proof by contradiction or induction"),
    GlossaryEntry("Substitute", "ជំនួស", "Logical Connectives", "Replace variable by value or expression"),
    GlossaryEntry("Compare", "ប្រៀបធៀប", "Logical Connectives", "Examine similarities or magnitude (<, =, >)"),
    GlossaryEntry("Conclusion", "សន្និដ្ឋាន", "Logical Connectives", "Final summary statement"),

    # 3. Numbers & Fractions
    GlossaryEntry("Integer", "ចំនួនគត់", "Numbers & Fractions", "Whole number positive, zero, or negative", symbol="ℤ"),
    GlossaryEntry("Even number", "ចំនួនគូ", "Numbers & Fractions", "Divisible by 2 (2k)"),
    GlossaryEntry("Odd number", "ចំនួនសេស", "Numbers & Fractions", "Not divisible by 2 (2k+1)"),
    GlossaryEntry("Prime number", "ចំនួនបឋម", "Numbers & Fractions", "Greater than 1 with only factors 1 and itself"),
    GlossaryEntry("Consecutive numbers", "ចំនួនតគ្នានៃ", "Numbers & Fractions", "Numbers following in order (n, n+1, ...)"),
    GlossaryEntry("Fraction", "ប្រភាគ", "Numbers & Fractions", "Rational representation a/b"),
    GlossaryEntry("Numerator", "ភាគយក", "Numbers & Fractions", "Top number in a fraction"),
    GlossaryEntry("Denominator", "ភាគបែង", "Numbers & Fractions", "Bottom number in a fraction"),
    GlossaryEntry("Decimal", "ចំនួនទសភាគ", "Numbers & Fractions", "Number with decimal point"),
    GlossaryEntry("Percentage", "ភាគរយ", "Numbers & Fractions", "Per hundred", symbol="%"),
    GlossaryEntry("Reciprocal", "ចម្រាស់", "Numbers & Fractions", "Multiplicative inverse (1/x)"),
    GlossaryEntry("Significant figures", "លេខមានន័យ", "Numbers & Fractions", "Digits carrying meaningful resolution"),
    GlossaryEntry("Round off", "បង្គត់លេខ", "Numbers & Fractions", "Approximating to nearest decimal or sig fig"),

    # 4. Algebra
    GlossaryEntry("Sum / Total", "ផលបូក", "Algebra", "Result of addition (+)"),
    GlossaryEntry("Difference", "ផលដក", "Algebra", "Result of subtraction (-)"),
    GlossaryEntry("Product", "ផលគុណ", "Algebra", "Result of multiplication (×)"),
    GlossaryEntry("Quotient", "ផលចែក", "Algebra", "Result of division (÷)"),
    GlossaryEntry("Remainder", "សំណល់", "Algebra", "Amount left over after division"),
    GlossaryEntry("Equation", "សមីការ", "Algebra", "Mathematical statement of equality (=)"),
    GlossaryEntry("Inequality", "វិសមីការ", "Algebra", "Relation with <, >, ≤, or ≥"),
    GlossaryEntry("Variable / Unknown", "អថេរ / អញ្ញាត", "Algebra", "Letter representing changing or unknown value"),
    GlossaryEntry("Coefficient", "មេគុណ", "Algebra", "Numerical factor multiplying a variable"),
    GlossaryEntry("Constant", "ចំនួនថេរ", "Algebra", "Fixed numerical value"),
    GlossaryEntry("Term", "តួ", "Algebra", "Single component in a sum or sequence"),
    GlossaryEntry("Expression", "កន្សោម", "Algebra", "Combination of symbols without equality sign"),
    GlossaryEntry("Polynomial", "ពហុធា", "Algebra", "Sum of terms with non-negative integer powers"),
    GlossaryEntry("Root / Solution", "ឬស / ចម្លើយ", "Algebra", "Value satisfying an equation"),
    GlossaryEntry("Quadratic", "ដឺក្រេទី ២ (ការ៉េ)", "Algebra", "Degree 2 polynomial ax² + bx + c"),
    GlossaryEntry("Discriminant", "ឌីសគ្រីមីណង់", "Algebra", "Δ = b² - 4ac determines root nature", symbol="Δ"),
    GlossaryEntry("Simultaneous equations", "ប្រព័ន្ធសមីការ", "Algebra", "System of multiple equations solved together"),
    GlossaryEntry("Subject of formula", "អថេរគោល", "Algebra", "Variable isolated on one side of '='"),
    GlossaryEntry("Inverse function", "អនុគមន៍ច្រាស់", "Algebra", "f⁻¹(x) reversing the action of f(x)", symbol="f⁻¹"),
    GlossaryEntry("Composite function", "អនុគមន៍បណ្តាក់", "Algebra", "fg(x) = f(g(x)) applying g then f", symbol="f ∘ g"),
    GlossaryEntry("Asymptote", "អាស៊ីមតូត", "Algebra", "Line approached arbitrarily closely by curve"),

    # 5. Geometry
    GlossaryEntry("Angle", "មុំ", "Geometry", "Figure formed by two rays sharing vertex"),
    GlossaryEntry("Right angle", "មុំកែង", "Geometry", "Angle of exactly 90 degrees", symbol="90°"),
    GlossaryEntry("Acute angle", "មុំស្រួច", "Geometry", "Angle strictly between 0° and 90°"),
    GlossaryEntry("Obtuse angle", "មុំទាល", "Geometry", "Angle strictly between 90° and 180°"),
    GlossaryEntry("Reflex angle", "មុំផ្លាត", "Geometry", "Angle strictly greater than 180° and < 360°"),
    GlossaryEntry("Vertically opposite", "មុំទល់កំពូល", "Geometry", "Opposite angles formed by two intersecting lines"),
    GlossaryEntry("Corresponding angles", "មុំត្រូវគ្នា", "Geometry", "Matching angles along transversal"),
    GlossaryEntry("Alternate angles", "មុំឆ្លាស់", "Geometry", "Interior angles on alternate sides of transversal"),
    GlossaryEntry("Triangle", "ត្រីកោណ", "Geometry", "3-sided polygon"),
    GlossaryEntry("Isosceles triangle", "ត្រីកោណសមបាត", "Geometry", "Triangle with 2 equal sides"),
    GlossaryEntry("Equilateral triangle", "ត្រីកោណសម័ង្ស", "Geometry", "Triangle with 3 equal sides and 60° angles"),
    GlossaryEntry("Right-angled triangle", "ត្រីកោណកែង", "Geometry", "Triangle containing one 90° right angle"),
    GlossaryEntry("Hypotenuse", "អ៊ីប៉ូតេនុស", "Geometry", "Longest side of right triangle opposite 90°"),
    GlossaryEntry("Adjacent side", "ជ្រុងជាប់", "Geometry", "Side next to the reference angle"),
    GlossaryEntry("Opposite side", "ជ្រុងឈម", "Geometry", "Side facing the reference angle"),
    GlossaryEntry("Parallel", "ស្រប", "Geometry", "Lines in same plane that never intersect", symbol="∥"),
    GlossaryEntry("Perpendicular", "កែង", "Geometry", "Lines intersecting at 90° right angle", symbol="⊥"),
    GlossaryEntry("Perimeter", "បរិមាត្រ", "Geometry", "Total distance around boundary"),
    GlossaryEntry("Area", "ផ្ទៃក្រឡា", "Geometry", "Measure of two-dimensional surface"),
    GlossaryEntry("Bisector", "កន្លះបន្ទាត់ពុះមុំ / មេដ្យាទ័រ", "Geometry", "Line dividing angle or segment into two halves"),
    GlossaryEntry("Congruent", "ប៉ុនគ្នា", "Geometry", "Identical in shape and size", symbol="≅"),
    GlossaryEntry("Similar", "ដូចគ្នា", "Geometry", "Identical in shape with proportional sides", symbol="∼"),

    # 6. Shapes & Solids
    GlossaryEntry("Quadrilateral", "ចតុកោណ", "Shapes & Solids", "4-sided polygon"),
    GlossaryEntry("Parallelogram", "ប្រលេឡូក្រាម", "Shapes & Solids", "Opposite sides parallel and equal"),
    GlossaryEntry("Rhombus", "ស្វាយ (ចតុកោណស្មើ)", "Shapes & Solids", "Parallelogram with 4 equal sides"),
    GlossaryEntry("Trapezium / Trapezoid", "ចតុកោណព្នាយ", "Shapes & Solids", "Quadrilateral with at least one pair of parallel sides"),
    GlossaryEntry("Kite", "ចតុកោណខ្លែង", "Shapes & Solids", "Quadrilateral with two pairs of equal adjacent sides"),
    GlossaryEntry("Polygon", "ពហុកោណ", "Shapes & Solids", "Closed 2D figure with straight sides"),
    GlossaryEntry("Hexagon / Octagon", "ឆកោណ / អដ្ឋកោណ", "Shapes & Solids", "6-sided and 8-sided polygons"),
    GlossaryEntry("Circle", "រង្វង់", "Shapes & Solids", "Points equidistant from center"),
    GlossaryEntry("Radius / Diameter", "កាំ / អង្កត់ផ្ចិត", "Shapes & Solids", "r and d = 2r"),
    GlossaryEntry("Chord", "អង្កត់ធ្នូ", "Shapes & Solids", "Segment joining two points on circle"),
    GlossaryEntry("Tangent", "បន្ទាត់ប៉ះ", "Shapes & Solids", "Line touching circle at exactly one point"),
    GlossaryEntry("Arc / Sector", "ធ្នូ / ចម្រៀករង្វង់", "Shapes & Solids", "Curve portion and pie slice of circle"),
    GlossaryEntry("Prism", "ព្រីស", "Shapes & Solids", "Polyhedron with identical parallel bases"),
    GlossaryEntry("Pyramid", "ពីរ៉ាមីត", "Shapes & Solids", "Solid with polygonal base and triangular faces meeting at apex"),
    GlossaryEntry("Cylinder", "ស៊ីឡាំង", "Shapes & Solids", "3D solid with circular bases and curved surface"),
    GlossaryEntry("Cone", "កូន", "Shapes & Solids", "3D solid tapering smoothly from flat circular base to apex"),
    GlossaryEntry("Sphere", "ស្វ៊ែរ", "Shapes & Solids", "Perfect 3D round object"),
    GlossaryEntry("Volume", "មាឌ", "Shapes & Solids", "Amount of 3D space enclosed"),
    GlossaryEntry("Surface area", "ផ្ទៃក្រឡាខាងក្រៅ", "Shapes & Solids", "Total area of outer surface"),

    # 7. Calculus
    GlossaryEntry("Function", "អនុគមន៍", "Calculus", "Mapping from domain to range", symbol="f(x)"),
    GlossaryEntry("Domain", "ដែនកំណត់", "Calculus", "Set of allowed input values", symbol="D"),
    GlossaryEntry("Range", "សំណុំរូបភាព", "Calculus", "Set of output values y = f(x)"),
    GlossaryEntry("Limit", "លីមីត", "Calculus", "Value approached by function", symbol="lim"),
    GlossaryEntry("Approaches", "ខិតជិតទៅរក", "Calculus", "Tending towards", symbol="→"),
    GlossaryEntry("Derivative", "ដេរីវេ", "Calculus", "Instantaneous rate of change", symbol="f'(x)"),
    GlossaryEntry("Differentiation", "ការរកដេរីវេ", "Calculus", "Process of finding derivative"),
    GlossaryEntry("Rate of change", "អត្រាបម្រែបម្រួល", "Calculus", "Change in y relative to change in x"),
    GlossaryEntry("Chain rule", "រូបមន្តបណ្តាក់", "Calculus", "dy/dx = (dy/du)(du/dx)"),
    GlossaryEntry("Product rule", "រូបមន្តផលគុណ", "Calculus", "(uv)' = u'v + uv'"),
    GlossaryEntry("Quotient rule", "រូបមន្តផលចែក", "Calculus", "(u/v)' = (u'v - uv') / v²"),
    GlossaryEntry("Tangent line", "បន្ទាត់ប៉ះ", "Calculus", "Line touching curve with slope f'(x₀)"),
    GlossaryEntry("Normal line", "បន្ទាត់កែង", "Calculus", "Line perpendicular to tangent line with slope -1/f'(x₀)"),
    GlossaryEntry("Integral", "អាំងតេក្រាល", "Calculus", "Antiderivative or area under curve", symbol="∫"),
    GlossaryEntry("Integration", "ការគណនាអាំងតេក្រាល", "Calculus", "Process of integrating"),
    GlossaryEntry("Definite integral", "អាំងតេក្រាលកំណត់", "Calculus", "Integral evaluated between bounds [a, b]", symbol="∫_a^b"),
    GlossaryEntry("Indefinite integral", "អាំងតេក្រាលមិនកំណត់", "Calculus", "General antiderivative with + C", symbol="∫ f(x)dx"),
    GlossaryEntry("Maximum / Minimum", "អតិបរមា / អប្បបរមា", "Calculus", "Local/global peak and trough"),
    GlossaryEntry("Turning point", "ចំណុចបត់", "Calculus", "Point where f'(x) = 0 and curve changes direction"),
    GlossaryEntry("Stationary point", "ចំណុចមានដេរីវេស្មើសូន្យ", "Calculus", "Point where tangent is horizontal (f'=0)"),
    GlossaryEntry("Inflection point", "ចំណុចរបត់", "Calculus", "Point where concavity changes (f'' = 0)"),
    GlossaryEntry("Concave up", "ផតអ៊ុតទៅលើ", "Calculus", "Curving upwards like cup (f'' > 0)"),
    GlossaryEntry("Concave down", "ផតអ៊ុតទៅក្រោម", "Calculus", "Curving downwards like cap (f'' < 0)"),

    # 8. Sequences (BacII Grade 12 Focus)
    GlossaryEntry("Sequence", "ស្វ៊ីត", "Sequences", "Ordered list of mathematical elements", symbol="(uₙ)"),
    GlossaryEntry("Arithmetic sequence", "ស្វ៊ីតនព្វន្ត", "Sequences", "Sequence with constant difference u_{n+1} - u_n = d"),
    GlossaryEntry("Geometric sequence", "ស្វ៊ីតធរណីមាត្រ", "Sequences", "Sequence with constant ratio u_{n+1} / u_n = q"),
    GlossaryEntry("Common difference", "ផលសងរួម", "Sequences", "Step size in arithmetic progression", symbol="d"),
    GlossaryEntry("Common ratio", "ផលធៀបរួម", "Sequences", "Multiplier in geometric progression", symbol="q"),
    GlossaryEntry("General term", "តួទូទៅ", "Sequences", "Formula for nth element", symbol="u_n"),
    GlossaryEntry("First term", "តួទីមួយ", "Sequences", "Starting element of sequence", symbol="u₁"),
    GlossaryEntry("Recurrence relation", "ទំនាក់ទំនងកំណត់ដោយកំឡើត", "Sequences", "Defines u_{n+1} in terms of previous terms"),
    GlossaryEntry("Convergent sequence", "ស្វ៊ីតរួម", "Sequences", "Has a finite limit as n → +∞"),
    GlossaryEntry("Divergent sequence", "ស្វ៊ីតរីក", "Sequences", "No finite limit or limit is ±∞"),
    GlossaryEntry("Bounded sequence", "ស្វ៊ីតទាល់", "Sequences", "Bounded both above and below (m ≤ u_n ≤ M)"),
    GlossaryEntry("Bounded above", "ទាល់លើ", "Sequences", "u_n ≤ M for all n"),
    GlossaryEntry("Bounded below", "ទាល់ក្រោម", "Sequences", "u_n ≥ m for all n"),
    GlossaryEntry("Increasing sequence", "ស្វ៊ីតកើន", "Sequences", "u_{n+1} ≥ u_n for all n"),
    GlossaryEntry("Decreasing sequence", "ស្វ៊ីតចុះ", "Sequences", "u_{n+1} ≤ u_n for all n"),
    GlossaryEntry("Squeeze theorem", "ទ្រឹស្តីបទញှៀប", "Sequences", "Sandwich theorem for limits of bounded sequences"),
    GlossaryEntry("Sum of n terms", "ផលបូក n តួដំបូង", "Sequences", "Sum u₁ + u₂ + ... + u_n", symbol="S_n"),

    # 9. Statistics & Probability
    GlossaryEntry("Data", "ទិន្នន័យ", "Statistics & Probability", "Collected facts or numerical measurements"),
    GlossaryEntry("Mean / Average", "មធ្យម", "Statistics & Probability", "Sum of values divided by count", symbol="x̄"),
    GlossaryEntry("Median", "មេដ្យាន", "Statistics & Probability", "Middle value in sorted dataset"),
    GlossaryEntry("Mode", "ម៉ូត", "Statistics & Probability", "Most frequently occurring value"),
    GlossaryEntry("Range", "គំលាត", "Statistics & Probability", "Max value minus Min value"),
    GlossaryEntry("Frequency", "ប្រេកង់", "Statistics & Probability", "Number of occurrences of a data item", symbol="f"),
    GlossaryEntry("Cumulative frequency", "ប្រេកង់កើន", "Statistics & Probability", "Running sum of frequencies"),
    GlossaryEntry("Standard deviation", "គំលាតស្តង់ដា", "Statistics & Probability", "Measure of dispersion around the mean", symbol="σ"),
    GlossaryEntry("Variance", "វ៉ារ្យង់", "Statistics & Probability", "Square of standard deviation", symbol="σ²"),
    GlossaryEntry("Probability", "ប្រូបាប", "Statistics & Probability", "Likelihood of an event occurring", symbol="P(A)"),
    GlossaryEntry("Outcome", "លទ្ធផល", "Statistics & Probability", "Possible result of experiment"),
    GlossaryEntry("Event", "ព្រឹត្តិការណ៍", "Statistics & Probability", "Subset of sample space"),
    GlossaryEntry("Mutually exclusive", "ព្រឹត្តិការណ៍ដាច់ដោយឡែក", "Statistics & Probability", "Events that cannot happen simultaneously"),
    GlossaryEntry("Independent events", "ព្រឹត្តិការណ៍មិនទាក់ទងគ្នា", "Statistics & Probability", "P(A ∩ B) = P(A) · P(B)"),

    # 10. Matrices & Vectors
    GlossaryEntry("Matrix", "ម៉ាទ្រីស", "Matrices & Vectors", "Rectangular array of numbers"),
    GlossaryEntry("Row / Column", "ជួរដេក / ជួរឈរ", "Matrices & Vectors", "Horizontal and vertical rows"),
    GlossaryEntry("Order / Dimension", "លំដាប់ / វិមាត្រ", "Matrices & Vectors", "m × n size of matrix"),
    GlossaryEntry("Determinant", "ដេអ៊ែរមីណង់", "Matrices & Vectors", "Scalar value computed from square matrix", symbol="det(A)"),
    GlossaryEntry("Inverse matrix", "ម៉ាទ្រីសច្រាស់", "Matrices & Vectors", "A⁻¹ such that A · A⁻¹ = I", symbol="A⁻¹"),
    GlossaryEntry("Identity matrix", "ម៉ាទ្រីសឯកតា", "Matrices & Vectors", "Square matrix with 1s on main diagonal and 0s elsewhere", symbol="I"),
    GlossaryEntry("Vector", "វ៉ិចទ័រ", "Matrices & Vectors", "Quantity with magnitude and direction", symbol="v⃗"),
    GlossaryEntry("Magnitude", "ម៉ូឌុល", "Matrices & Vectors", "Length of vector", symbol="‖v⃗‖"),
    GlossaryEntry("Direction", "ទិសដៅ", "Matrices & Vectors", "Orientation along line of action"),
    GlossaryEntry("Scalar", "ស្កាលែ", "Matrices & Vectors", "Real number multiplier without direction"),
    GlossaryEntry("Resultant vector", "វ៉ិចទ័រផលបូក", "Matrices & Vectors", "Vector sum of multiple vectors"),
    GlossaryEntry("Collinear", "កូលីនេអ៊ែរ", "Matrices & Vectors", "Lying on the same straight line"),
    GlossaryEntry("Dot product", "ផលគុណស្កាលែ", "Matrices & Vectors", "Scalar product u⃗ · v⃗ = ‖u⃗‖ ‖v⃗‖ cos θ", symbol="·"),

    # 11. Sets
    GlossaryEntry("Set", "សំណុំ", "Sets", "Well-defined collection of objects"),
    GlossaryEntry("Element / Member", "ធាតុ", "Sets", "Object belonging to a set", symbol="∈"),
    GlossaryEntry("Subset", "សំណុំរង", "Sets", "Set contained entirely inside another", symbol="⊆"),
    GlossaryEntry("Universal set", "សំណុំសកល", "Sets", "Totality of elements under consideration", symbol="ξ ឬ U"),
    GlossaryEntry("Empty / Null set", "សំណុំទទេ", "Sets", "Set containing no elements", symbol="∅"),
    GlossaryEntry("Union", "ប្រជុំ", "Sets", "Combination of elements in either set", symbol="∪"),
    GlossaryEntry("Intersection", "ប្រសព្វ", "Sets", "Elements common to both sets", symbol="∩"),
    GlossaryEntry("Complement", "បំពេញ", "Sets", "Elements not in given set", symbol="A'"),
]


# Bilingual Example Usages (ឧទាហរណ៍ជាក់ស្តែង)
EXAMPLE_USAGES = [
    {
        "english": "Find the derivative of f(x) with respect to x.",
        "khmer": "រកដេរីវេនៃ f(x) ធៀបនឹង x។",
        "topic": "Calculus",
    },
    {
        "english": "Let x be the length of the rectangle.",
        "khmer": "តាង x ជាបណ្តោយនៃចតុកោណកែង។",
        "topic": "Algebra",
    },
    {
        "english": "Determine the coordinates of the turning points.",
        "khmer": "កំណត់កូអរដោនេនៃចំណុចបត់។",
        "topic": "Calculus",
    },
    {
        "english": "Given that triangle ABC is equilateral, find angle A.",
        "khmer": "ដោយដឹងថាត្រីកោណ ABC ជាត្រីកោណសម័ង្ស, ចូររកមុំ A។",
        "topic": "Geometry",
    },
    {
        "english": "Calculate the limit of sequence (u_n) as n approaches infinity.",
        "khmer": "គណនាលីមីតនៃស្វ៊ីត (u_n) កាលណា n ខិតជិត +∞។",
        "topic": "Sequences",
    },
    {
        "english": "Express the general term u_n in terms of n.",
        "khmer": "សរសេរតួទូទៅ u_n ជាអនុគមន៍នៃ n។",
        "topic": "Sequences",
    },
]


def get_all_categories() -> List[str]:
    """Returns unique list of categories in the glossary."""
    cats = []
    seen = set()
    for entry in STRUCTURED_ENTRIES:
        if entry.category not in seen:
            seen.add(entry.category)
            cats.append(entry.category)
    return cats


def search_glossary(query: str, category: Optional[str] = None) -> List[GlossaryEntry]:
    """
    Search glossary across both English and Khmer names, explanations, and symbols.
    """
    if not query and not category:
        return STRUCTURED_ENTRIES

    q = (query or "").strip().lower()
    results: List[GlossaryEntry] = []

    for entry in STRUCTURED_ENTRIES:
        if category and entry.category.lower() != category.strip().lower():
            continue

        if not q:
            results.append(entry)
            continue

        en_match = q in entry.english.lower()
        km_match = q in entry.khmer.lower()
        sym_match = bool(entry.symbol and q in entry.symbol.lower())
        exp_match = bool(entry.explanation and q in entry.explanation.lower())

        if en_match or km_match or sym_match or exp_match:
            results.append(entry)

    return results


def lookup_khmer(english_term: str) -> Optional[str]:
    """Lookup standard Khmer translation for an English math term."""
    clean = english_term.strip().lower()
    return ALL_MATH_TERMS.get(clean)


def lookup_english(khmer_term: str) -> Optional[str]:
    """Lookup standard English translation for a Khmer math term."""
    clean = khmer_term.strip()
    for en, km in ALL_MATH_TERMS.items():
        if clean in km or km in clean:
            return en
    return None
