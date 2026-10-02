"""
Complex Numbers Explanation Templates (Grade 12 BacII Focus).
"""

from __future__ import annotations

from app.knowledge.models import ExplanationStepTemplate, ExplanationTemplate

# Template: Basic Arithmetic of Complex Numbers (z = a + bi)
template_complex_arithmetic = ExplanationTemplate(
    id="tmpl_complex_arithmetic",
    method_id="method_complex_arithmetic",
    name_km="ប្រមាណវិធីលើចំនួនកុំផ្លិច (ទម្រង់ពីជគណិត)",
    name_en="Algebraic Form Operations for Complex Numbers",
    verification_strategy="none",
    pedagogical_notes_km="បូក ដក ឬគុណចំនួនកុំផ្លិចដោយគិតផ្នែកពិតដោយឡែក និងផ្នែកនិម្មិតដោយឡែក (ដោយប្រើ i² = -1)។",
    pedagogical_notes_en="Add, subtract, or multiply complex numbers grouping real and imaginary parts (using i² = -1).",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_complex_parts",
            title_km="កំណត់ផ្នែកពិត និងផ្នែកនិម្មិត",
            title_en="Identify Real & Imaginary Parts",
            rationale_template_km="កត់សម្គាល់ផ្នែកពិត Re(z) និងផ្នែកនិម្មិត Im(z) នៃចំនួនកុំផ្លិចនីមួយៗ។",
            rationale_template_en="Identify real part Re(z) and imaginary part Im(z) for each operand.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="apply_operation",
            title_km="អនុវត្តប្រមាណវិធី",
            title_en="Perform Complex Operation",
            rationale_template_km="អនុវត្តការបូក ដក ឬគុណតាមវិធាននៃចំនួនកុំផ្លិច។",
            rationale_template_en="Apply operations grouping like real and imaginary components.",
            rule_reference="(a + bi) \\pm (c + di) = (a \\pm c) + (b \\pm d)i",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="standard_form",
            title_km="សរសេរជាទម្រង់ស្តង់ដារ a + bi",
            title_en="Write in Standard Form a + bi",
            rationale_template_km="បង្រួមលទ្ធផលចុងក្រោយជាទម្រង់ពីជគណិតស្តង់ដារ a + bi។",
            rationale_template_en="Express final simplified result in standard form a + bi.",
        ),
    ],
)
