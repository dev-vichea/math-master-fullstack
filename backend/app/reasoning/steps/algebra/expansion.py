"""
Step-by-step derivation for polynomial expansion, products of factors, and factorization.

Follows the standard Cambodian high school curriculum pedagogy:
Example: A = (k + 4)(k² - 4k + 1)
  Step 1: Original expression: A = (k + 4)(k² - 4k + 1)
  Step 2: Apply distributive property: = k(k² - 4k + 1) + 4(k² - 4k + 1)
  Step 3: Multiply and expand each term: = k³ - 4k² + k + 4k² - 16k + 4
  Step 4: Combine like terms to get final result: = k³ - 15k + 4
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Add, Mul, Pow, Symbol, expand, factor, latex

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import StepGenerator


class ExpansionStepGenerator(StepGenerator):
    """Generates step-by-step textbook solutions for polynomial expansion and factorization."""

    problem_type = "factored_expression"

    def generate(self, expr: Any, symbol: Symbol | None = None, raw_text: str = "") -> list[SolutionStep]:
        """Generate pedagogical step-by-step expansion matching Khmer textbook standards."""
        steps: list[SolutionStep] = []
        order = 1

        # Check for assignment name (e.g. A = ..., B = ...)
        prefix = ""
        if raw_text and "=" in raw_text:
            parts = raw_text.split("=", 1)
            candidate = parts[0].strip()
            # If candidate is a single variable or function name like A, B, C, P
            if len(candidate) <= 2 and candidate.replace("(", "").replace(")", "").isalpha():
                prefix = f"{candidate} = "

        # Case 1: Product of factors (Mul)
        if isinstance(expr, Mul):
            factors = list(expr.args)
            poly_factors = [f for f in factors if not f.is_Number]
            constant = Mul(*[f for f in factors if f.is_Number]) if any(f.is_Number for f in factors) else None

            if len(poly_factors) >= 2:
                # Two or more polynomial factors: (P1)(P2)
                f1, f2 = poly_factors[0], poly_factors[1]
                if not isinstance(f1, Add) and isinstance(f2, Add):
                    f1, f2 = f2, f1

                # Sort terms of first factor so variables precede constants, and positive precedes negative (e.g. a then -b, k then 4)
                raw_terms = f1.args if isinstance(f1, Add) else (f1,)
                terms_f1 = sorted(
                    raw_terms,
                    key=lambda t: (
                        1 if t.is_Number else 0,
                        1 if str(t).strip().startswith("-") else 0,
                        -len(t.free_symbols),
                        str(t),
                    ),
                )

                # Step 1: Original expression
                orig_latex = latex(expr)
                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="កន្សោមដើម",
                        title_en="Original Expression",
                        rationale_km="កត់សម្គាល់កន្សោមដើមដែលជាផលគុណរវាងពហុធានិងពហុធា។",
                        rationale_en="Identify the original expression as a product of polynomials.",
                        description_km="កន្សោមដើម៖",
                        description_en="Original expression:",
                        expression=f"{prefix}{orig_latex}",
                        is_verification=False,
                    )
                )
                order += 1

                # Step 2: Distributive property (លក្ខណៈបំបែក)
                dist_parts: list[str] = []
                f2_latex = latex(f2)
                for i, t in enumerate(terms_f1):
                    t_latex = latex(t)
                    if i == 0:
                        dist_parts.append(rf"{t_latex}\left({f2_latex}\right)")
                    else:
                        if str(t).startswith("-"):
                            abs_t_latex = latex(-t)
                            dist_parts.append(rf"- {abs_t_latex}\left({f2_latex}\right)")
                        else:
                            dist_parts.append(rf"+ {t_latex}\left({f2_latex}\right)")

                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="អនុវត្តលក្ខណៈបំបែកនៃផលគុណ",
                        title_en="Apply Distributive Property",
                        rationale_km="គុណតួនីមួយៗនៃកត្តាទី១ ជាមួយនឹងកត្តាទី២ តាមរូបមន្ត (A + B)C = AC + BC។",
                        rationale_en="Multiply each term of the first factor by the second factor using (A + B)C = AC + BC.",
                        description_km="អនុវត្តលក្ខណៈបំបែក (គុណតួនីមួយៗនៃកត្តាទី១ នឹងកត្តាទី២)៖",
                        description_en="Apply the distributive property (multiply each term of 1st factor by 2nd factor):",
                        expression=f"= {' '.join(dist_parts)}",
                        rule_formula=r"(A + B)C = AC + BC",
                        is_verification=False,
                    )
                )
                order += 1

                # Step 3: Expand each distributed term
                expanded_parts: list[str] = []
                for i, t in enumerate(terms_f1):
                    exp_t = expand(t * f2)
                    sub_terms = exp_t.as_ordered_terms() if isinstance(exp_t, Add) else [exp_t]
                    for j, st in enumerate(sub_terms):
                        st_latex = latex(st)
                        if i == 0 and j == 0:
                            expanded_parts.append(st_latex)
                        else:
                            coeff = st.as_coeff_Mul()[0]
                            if coeff < 0:
                                pos_st = latex(-st)
                                expanded_parts.append(f"- {pos_st}")
                            else:
                                expanded_parts.append(f"+ {st_latex}")

                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="គុណពន្លាតតួនីមួយៗចូលក្នុងវង់ក្រចក",
                        title_en="Multiply Terms Inside Parentheses",
                        rationale_km="គុណមេគុណលេខ និងបូកស្វ័យគុណនៃអថេរដូចគ្នា ដើម្បីបំប្លែងទៅជាតួទោល។",
                        rationale_en="Multiply coefficients and add exponents of identical variables into individual terms.",
                        description_km="គុណពន្លាតតួនីមួយៗចូលក្នុងវង់ក្រចក៖",
                        description_en="Multiply each term inside parentheses:",
                        expression=f"= {' '.join(expanded_parts)}",
                        is_verification=False,
                    )
                )
                order += 1

                # Step 4: Combine like terms for final result
                final_expr = expand(expr)
                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="បង្រួមតួដូចគ្នា និងរៀបតាមស្វ័យគុណចុះ",
                        title_en="Combine Like Terms",
                        rationale_km="បូកដកតួដែលមានអថេរ និងស្វ័យគុណដូចគ្នា ដើម្បីទទួលបានទម្រង់ពហុធាសាមញ្ញបំផុត។",
                        rationale_en="Add or subtract like terms to obtain the simplest polynomial form.",
                        description_km="បង្រួមតួដូចគ្នាដើម្បីទទួលបានលទ្ធផលចុងក្រោយ៖",
                        description_en="Combine like terms to get final result:",
                        expression=f"= {latex(final_expr)}",
                        is_verification=False,
                    )
                )
                order += 1
                return steps

            elif len(poly_factors) == 1 and constant is not None:
                # Constant * Polynomial, e.g. 4(k² - 4k + 1)
                f = poly_factors[0]
                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="កន្សោមដើម",
                        title_en="Original Expression",
                        rationale_km="កត់សម្គាល់កន្សោមផលគុណរវាងមេគុណលេខ និងពហុធា។",
                        rationale_en="Identify the expression as a constant multiplied by a polynomial.",
                        description_km="កន្សោមដើម៖",
                        description_en="Original expression:",
                        expression=f"{prefix}{latex(expr)}",
                        is_verification=False,
                    )
                )
                order += 1

                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="គុណមេគុណចូលគ្រប់តួក្នុងវង់ក្រចក",
                        title_en="Distribute Constant to All Terms",
                        rationale_km="គុណមេគុណលេខចូលគ្រប់តួនីមួយៗក្នុងវង់ក្រចកតាមលក្ខណៈបំបែក k(a + b) = ka + kb។",
                        rationale_en="Multiply the constant factor into each term inside parentheses using k(a + b) = ka + kb.",
                        description_km="គុណមេគុណចូលគ្រប់តួក្នុងវង់ក្រចក៖",
                        description_en="Multiply coefficient with every term inside parentheses:",
                        expression=f"= {latex(expand(expr))}",
                        rule_formula=r"k(a + b) = ka + kb",
                        is_verification=False,
                    )
                )
                order += 1
                return steps

        # Case 2: Powers of a sum/difference: (a + b)²
        elif isinstance(expr, Pow):
            base, exp = expr.args
            if exp == 2 and isinstance(base, Add):
                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="កន្សោមដើម",
                        title_en="Original Expression",
                        rationale_km="កត់សម្គាល់ទម្រង់ការេនៃទ្វេធា (a ± b)²។",
                        rationale_en="Recognize the square of a binomial form (a ± b)².",
                        description_km="កន្សោមដើម៖",
                        description_en="Original expression:",
                        expression=f"{prefix}{latex(expr)}",
                        is_verification=False,
                    )
                )
                order += 1

                steps.append(
                    SolutionStep(
                        order=order,
                        title_km="អនុវត្តរូបមន្តស្វ័យគុណទ្វេធា",
                        title_en="Apply Binomial Square Identity",
                        rationale_km="ប្រើរូបមន្តស្មើភាពសំខាន់ (a ± b)² = a² ± 2ab + b²។",
                        rationale_en="Apply the standard algebraic identity (a ± b)² = a² ± 2ab + b².",
                        description_km="អនុវត្តរូបមន្តស្វ័យគុណ (a ± b)² = a² ± 2ab + b²៖",
                        description_en="Apply identity (a ± b)² = a² ± 2ab + b²:",
                        expression=f"= {latex(expand(expr))}",
                        rule_formula=r"(a \pm b)^2 = a^2 \pm 2ab + b^2",
                        is_verification=False,
                    )
                )
                order += 1
                return steps

        # Fallback expansion step
        final_exp = expand(expr)
        steps.append(
            SolutionStep(
                order=1,
                title_km="កន្សោមដើម",
                title_en="Original Expression",
                rationale_km="កន្សោមដើមដែលត្រូវពន្លាត។",
                rationale_en="Original expression to be expanded.",
                description_km="កន្សោមដើម៖",
                description_en="Original expression:",
                expression=f"{prefix}{latex(expr)}",
                is_verification=False,
            )
        )
        steps.append(
            SolutionStep(
                order=2,
                title_km="គណនាពន្លាតកន្សោម",
                title_en="Expand Expression",
                rationale_km="អនុវត្តការគុណពន្លាតដើម្បីទទួលបានពហុធាសាមញ្ញ។",
                rationale_en="Perform polynomial expansion to reach simplified polynomial form.",
                description_km="គណនាពន្លាតកន្សោម៖",
                description_en="Expand the expression:",
                expression=f"= {latex(final_exp)}",
                is_verification=False,
            )
        )
        return steps
