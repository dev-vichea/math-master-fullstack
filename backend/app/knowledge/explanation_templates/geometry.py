"""
Geometry Explanation Templates (Vectors & Spatial Analytic Geometry).
"""

from __future__ import annotations

from app.knowledge.models import ExplanationStepTemplate, ExplanationTemplate

# Template: Dot Product of Spatial Vectors
template_vector_dot_product = ExplanationTemplate(
    id="tmpl_vector_dot_product",
    method_id="method_vector_dot_product",
    name_km="ផលគុណស្កាលែនៃពីរវ៉ិចទ័រក្នុងលំហ",
    name_en="Dot Product of Spatial Vectors",
    verification_strategy="none",
    pedagogical_notes_km="គណនាផលគុណស្កាលែដោយប្រើរូបមន្ត u·v = x1*x2 + y1*y2 + z1*z2។",
    pedagogical_notes_en="Compute dot product using coordinate formula u·v = x1*x2 + y1*y2 + z1*z2.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_coordinates",
            title_km="កំណត់កូអរដោនេនៃវ៉ិចទ័រ",
            title_en="Identify Vector Coordinates",
            rationale_template_km="ស្រង់កូអរដោនេនៃវ៉ិចទ័រ u(x1, y1, z1) និង v(x2, y2, z2)។",
            rationale_template_en="Extract coordinates of vectors u(x1, y1, z1) and v(x2, y2, z2).",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="apply_dot_product_formula",
            title_km="អនុវត្តរូបមន្តផលគុណស្កាលែ",
            title_en="Apply Coordinate Dot Product Formula",
            rationale_template_km="ជំនួសកូអរដោនេចូលក្នុងរូបមន្ត u·v = x1*x2 + y1*y2 + z1*z2។",
            rationale_template_en="Substitute coordinates into u·v = x1*x2 + y1*y2 + z1*z2.",
            rule_reference="\\vec{u} \\cdot \\vec{v} = x_1 x_2 + y_1 y_2 + z_1 z_2",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="compute_scalar_result",
            title_km="គណនាតម្លៃលេខចុងក្រោយ",
            title_en="Compute Scalar Result",
            rationale_template_km="បូកផលគុណនៃសមាសភាគដើម្បីទទួលបានចំនួនពិតមួយ។",
            rationale_template_en="Sum the coordinate products to get a scalar value.",
        ),
    ],
)
