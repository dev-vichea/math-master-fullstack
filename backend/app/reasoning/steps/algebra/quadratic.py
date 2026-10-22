"""
Step-by-step derivation for quadratic equations (ax² + bx + c = 0).

The algorithm:
  1. Show the original equation.
  2. If not in standard form, rearrange to ax² + bx + c = 0.
  3. Identify coefficients a, b, and c.
  4. Calculate and display the discriminant (Δ = b² - 4ac).
  5. Apply the quadratic formula based on the discriminant:
     - Δ > 0: Two distinct real roots
     - Δ = 0: One repeated root
     - Δ < 0: No real roots (complex roots)
  6. Show the final solution(s).

Every arithmetic operation is done by SymPy, and the final value is
substituted back and checked by verification.verify_solution before it is
ever returned to the API layer — the steps shown here are a *description*
of a computation SymPy already did, not a separate, potentially-wrong,
free-form explanation.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Symbol, expand, nsimplify, sqrt

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import CalculationBuilder, StepGenerator, create_solution_step


def _format_number(value: sympy.Expr) -> str:
    """Render a number the way a textbook would: no '.0', fractions kept as
    fractions rather than decimals."""
    if value == sympy.floor(value):
        try:
            return str(int(value))
        except TypeError:
            pass
    return str(value)


class QuadraticStepGenerator(StepGenerator):
    problem_type = "quadratic_equation"

    def generate(self, eq: Eq, symbol: Symbol) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        order = 1

        lhs = expand(eq.lhs)
        rhs = expand(eq.rhs)

        calc_init = CalculationBuilder(f"{sympy.latex(lhs)} = {sympy.latex(rhs)}")
        steps.append(
            create_solution_step(
                order=order,
                title_km="កំណត់សមីការដើម",
                title_en="Original Equation",
                description_km="សមីការដើម៖",
                description_en="Original equation:",
                calc=calc_init,
                teacher_note="ដើម្បីដោះស្រាយសមីការដឺក្រេទី ២ (សមីការក្វាដ្រាទិក) ត្រូវតម្រៀបវាឱ្យចូលទម្រង់ស្តង់ដារ ax² + bx + c = 0 ជាមុនសិន។",
            )
        )
        order += 1

        # Move everything to the left side to get standard form: ax² + bx + c = 0
        standard_lhs = expand(lhs - rhs)
        if standard_lhs != lhs or rhs != 0:
            calc_std = CalculationBuilder(f"{sympy.latex(lhs)} = {sympy.latex(rhs)}")
            calc_std.add_step("ផ្លាស់ទីគ្រប់តួមកអង្គខាងឆ្វេង", f"{sympy.latex(standard_lhs)} = 0")
            steps.append(
                create_solution_step(
                    order=order,
                    title_km="រៀបចំឱ្យចូលទម្រង់ស្តង់ដារ",
                    title_en="Standard Form",
                    description_km="ផ្លាស់ទីទាំងអស់មកខាងឆ្វេងដើម្បីទទួលបានទម្រង់ស្តង់ដារ៖",
                    description_en="Move all terms to the left to get standard form:",
                    calc=calc_std,
                    teacher_note="ផ្លាស់ទីគ្រប់តួទាំងអស់មកអង្គខាងឆ្វេង ដើម្បីឱ្យអង្គខាងស្តាំស្មើសូន្យ (ax² + bx + c = 0)៖",
                )
            )
            order += 1

        # Extract coefficients: a, b, c from ax² + bx + c = 0
        a = standard_lhs.coeff(symbol, 2)
        b = standard_lhs.coeff(symbol, 1)
        c = standard_lhs.coeff(symbol, 0)

        # Check special case: difference of squares (b == 0 and -c/a > 0)
        if b == 0 and a != 0:
            val_k = -c / a
            sqrt_k = sympy.sqrt(val_k)
            if sqrt_k.is_integer and sqrt_k > 0:
                k_int = int(sqrt_k)
                calc_diff = CalculationBuilder(f"{sympy.latex(standard_lhs)} = 0")
                calc_diff.add_step("ដាក់ជាផលគុណកត្តាផលដកពីរការ៉េ", f"({symbol} - {k_int})({symbol} + {k_int}) = 0")
                steps.append(
                    create_solution_step(
                        order=order,
                        title_km="ប្រើរូបមន្តផលដកពីរការ៉េ (Factoring)",
                        title_en="Factor as Difference of Squares",
                        description_km="ដាក់ជាផលគុណកត្តាផលដកពីរការ៉េ៖",
                        description_en="Factor as difference of two squares:",
                        calc=calc_diff,
                        rule_formula=r"a^2 - b^2 = (a - b)(a + b)",
                        teacher_note=f"សមីការនេះគ្មានតួ {symbol} (គឺ b = 0) អាចប្រើរូបមន្តផលដកពីរការ៉េ៖\n"
                        r"$a^2 - b^2 = (a - b)(a + b)$"
                        + "\n"
                        + f"ដូចនេះ៖ ${symbol}^2 - {k_int}^2 = ({symbol} - {k_int})({symbol} + {k_int}) = 0$",
                        important_note="ចំណាំ៖ ផលគុណស្មើសូន្យ A × B = 0 លុះត្រាតែ A = 0 ឬ B = 0។",
                    )
                )
                order += 1

                calc_fac = CalculationBuilder()
                calc_fac.add_step(f"ឱ្យកត្តាទី ១ ស្មើសូន្យ៖ {symbol} - {k_int} = 0", f"{symbol} = {k_int}")
                calc_fac.add_step(f"ឱ្យកត្តាទី ២ ស្មើសូន្យ៖ {symbol} + {k_int} = 0", f"{symbol} = -{k_int}")
                steps.append(
                    create_solution_step(
                        order=order,
                        title_km="រកឫសនៃកត្តានីមួយៗ",
                        title_en="Solve Each Factor",
                        description_km="ឱ្យកត្តានីមួយៗស្មើសូន្យ រួចទាញរកចម្លើយ៖",
                        description_en="Set each factor to zero and solve:",
                        calc=calc_fac,
                        teacher_note=f"ឱ្យកត្តានីមួយៗស្មើសូន្យ៖\n"
                        f"• ${symbol} - {k_int} = 0 \\implies {symbol} = {k_int}$\n"
                        f"• ${symbol} + {k_int} = 0 \\implies {symbol} = -{k_int}$",
                    )
                )
                order += 1

                calc_ans = CalculationBuilder(f"{symbol} = {k_int}, \\quad {symbol} = -{k_int}")
                steps.append(
                    create_solution_step(
                        order=order,
                        title_km="ចម្លើយចុងក្រោយ",
                        title_en="Final Answer",
                        description_km=f"ចម្លើយ៖ {symbol} = {k_int} ឬ {symbol} = -{k_int}",
                        description_en=f"Answer: {symbol} = {k_int} or {symbol} = -{k_int}",
                        calc=calc_ans,
                        teacher_note=f"សមីការមានឫសពីរគឺ {symbol} = {k_int} និង {symbol} = -{k_int}។ ផ្ទៀងផ្ទាត់ដោយជំនួសចូលសមីការដើម។",
                    )
                )
                return steps

        # General case with discriminant
        calc_coeff = CalculationBuilder(
            f"a = {_format_number(a)}, \\quad b = {_format_number(b)}, \\quad c = {_format_number(c)}"
        )
        steps.append(
            create_solution_step(
                order=order,
                title_km="កំណត់មេគុណ a, b, c",
                title_en="Identify Coefficients",
                description_km=f"កំណត់​មេគុណ៖ a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}",
                description_en=f"Identify coefficients: a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}",
                calc=calc_coeff,
                teacher_note=f"ស្រង់តម្លៃមេគុណពីសមីការស្តង់ដារ៖ a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}។",
            )
        )
        order += 1

        # Calculate discriminant: Δ = b² - 4ac
        discriminant = nsimplify(b**2 - 4 * a * c)
        if discriminant > 0:
            delta_note = "ចំណាំ៖ ដោយសារ Δ > 0 សមីការមានឫសពីរផ្សេងគ្នាជាចំនួនពិត!"
        elif discriminant == 0:
            delta_note = "ចំណាំ៖ ដោយសារ Δ = 0 សមីការមានឫសឌុប (ឫសឡើងវិញ)!"
        else:
            delta_note = "ចំណាំ៖ ដោយសារ Δ < 0 សមីការគ្មានឫសក្នុងសំណុំចំនួនពិត ℝ ទេ (មានឫសកុំផ្លិច)!"

        calc_delta = CalculationBuilder()
        calc_delta.add_initial(r"\Delta = b^2 - 4ac")
        calc_delta.add_step(
            "ជំនួសតម្លៃមេគុណ a, b, c",
            f"\\Delta = ({_format_number(b)})^2 - 4({_format_number(a)})({_format_number(c)})",
        )
        calc_delta.add_step("គណនាតម្លៃឌីស្ក្រីមីណង់", f"\\Delta = {_format_number(discriminant)}")

        steps.append(
            create_solution_step(
                order=order,
                title_km="គណនាឌីស្ក្រីមីណង់ (Delta)",
                title_en="Calculate Discriminant",
                description_km="គណនាឌីស្ក្រីមីណង់ Δ = b² - 4ac:",
                description_en="Calculate discriminant Δ = b² - 4ac:",
                calc=calc_delta,
                rule_formula=r"\Delta = b^2 - 4ac",
                teacher_note="ប្រើរូបមន្តឌីស្ក្រីមីណង់ Δ = b² - 4ac ដើម្បីពិនិត្យចំនួនឫសនៃសមីការ៖",
                important_note=delta_note,
            )
        )
        order += 1

        # Apply quadratic formula based on discriminant value
        if discriminant > 0:
            # Two distinct real roots
            sqrt_discriminant = sqrt(discriminant)
            root1 = nsimplify((-b + sqrt_discriminant) / (2 * a))
            root2 = nsimplify((-b - sqrt_discriminant) / (2 * a))

            calc_quad = CalculationBuilder()
            calc_quad.add_initial(rf"{symbol} = \frac{{-b \pm \sqrt{{\Delta}}}}{{2a}}")
            calc_quad.add_step(
                "ជំនួសតម្លៃចូលក្នុងរូបមន្ត",
                f"{symbol} = \\frac{{-({_format_number(b)}) \\pm \\sqrt{{{_format_number(discriminant)}}}}}{{2({_format_number(a)})}}",
            )
            calc_quad.add_step(
                "គណនាឫសទីមួយ និងទីពីរ",
                f"{symbol}_1 = {_format_number(root1)}, \\quad {symbol}_2 = {_format_number(root2)}",
            )

            steps.append(
                create_solution_step(
                    order=order,
                    title_km="អនុវត្តរូបមន្តក្វាដ្រាទិក",
                    title_en="Apply Quadratic Formula",
                    description_km="ដោយសារ Δ > 0, មានដំណោះស្រាយពីរផ្សេងគ្នា។ ប្រើរូបមន្តក្វាដ្រាទិក៖",
                    description_en="Since Δ > 0, there are two distinct real solutions. Using the quadratic formula:",
                    calc=calc_quad,
                    rule_formula=rf"{symbol} = \frac{{-b \pm \sqrt{{\Delta}}}}{{2a}}",
                    teacher_note="ជំនួសតម្លៃមេគុណ a, b និង Δ ចូលក្នុងរូបមន្តក្វាដ្រាទិក៖",
                )
            )
            order += 1

            calc_ans = CalculationBuilder(
                f"{symbol} = {_format_number(root1)}, \\quad {symbol} = {_format_number(root2)}"
            )
            steps.append(
                create_solution_step(
                    order=order,
                    title_km="ចម្លើយចុងក្រោយ",
                    title_en="Final Answer",
                    description_km=f"ចម្លើយ៖ {symbol} = {_format_number(root1)} ឬ {symbol} = {_format_number(root2)}",
                    description_en=f"Answer: {symbol} = {_format_number(root1)} or {symbol} = {_format_number(root2)}",
                    calc=calc_ans,
                    teacher_note=f"ឫសទាំងពីរនៃសមីការគឺ៖ {symbol} = {_format_number(root1)} ឬ {symbol} = {_format_number(root2)}។",
                )
            )

        elif discriminant == 0:
            root = nsimplify(-b / (2 * a))
            calc_quad = CalculationBuilder()
            calc_quad.add_initial(rf"{symbol} = -\frac{{b}}{{2a}}")
            calc_quad.add_step(
                "ជំនួសតម្លៃមេគុណ a, b",
                f"{symbol} = -\\frac{{{_format_number(b)}}}{{2({_format_number(a)})}}",
            )
            calc_quad.add_step("គណនាឫសឌុប", f"{symbol} = {_format_number(root)}")

            steps.append(
                create_solution_step(
                    order=order,
                    title_km="អនុវត្តរូបមន្តក្វាដ្រាទិក (ឫសឌុប)",
                    title_en="Apply Quadratic Formula (Repeated Root)",
                    description_km="ដោយសារ Δ = 0, មានដំណោះស្រាយតែមួយ (ឫសឌុប ឬឫសឡើងវិញ)។ ប្រើរូបមន្តក្វាដ្រាទិក៖",
                    description_en="Since Δ = 0, there is one repeated solution. Using the quadratic formula:",
                    calc=calc_quad,
                    rule_formula=rf"{symbol} = -\frac{{b}}{{2a}}",
                    teacher_note=f"ដោយសារ Δ = 0 សមីការមានឫសឌុប (ឫសឡើងវិញ) {symbol} = -b / 2a៖",
                )
            )
            order += 1

            calc_ans = CalculationBuilder(f"{symbol} = {_format_number(root)}")
            steps.append(
                create_solution_step(
                    order=order,
                    title_km="ចម្លើយចុងក្រោយ",
                    title_en="Final Answer",
                    description_km=f"ចម្លើយ៖ {symbol} = {_format_number(root)}",
                    description_en=f"Answer: {symbol} = {_format_number(root)}",
                    calc=calc_ans,
                    teacher_note=f"ដូចនេះ សមីការមានឫសឌុប {symbol} = {_format_number(root)}។",
                )
            )

        else:  # discriminant < 0
            sqrt_neg_discriminant = sqrt(-discriminant)
            real_part = nsimplify(-b / (2 * a))
            imag_part = nsimplify(sqrt_neg_discriminant / (2 * a))

            calc_neg = CalculationBuilder(r"\Delta < 0 \implies x \notin \mathbb{R}")
            steps.append(
                create_solution_step(
                    order=order,
                    title_km="សន្និដ្ឋានលើចំនួនឫសពិត",
                    title_en="Check Real Solutions",
                    description_km="ដោយសារ Δ < 0, គ្មានដំណោះស្រាយជាលេខពិតទេ (មានតែដំណោះស្រាយស្មុគស្មាញ)។",
                    description_en="Since Δ < 0, there are no real solutions (only complex solutions).",
                    calc=calc_neg,
                    teacher_note="ដោយសារឌីស្គ្រីមីណង់អវិជ្ជមាន (Δ < 0) មិនអាចបញ្ចេញឫសការ៉េនៃចំនួនអវិជ្ជមានក្នុងសំណុំចំនួនពិត ℝ បានទេ ដូច្នេះសមីការគ្មានឫសពិតទេ។",
                    important_note="ចំណាំ៖ សមីការក្វាដ្រាទិកដែលមាន Δ < 0 គ្មានឫសក្នុង ℝ តែមានឫសឆ្លាស់ពីរក្នុងសំណុំចំនួនកុំផ្លិច ℂ។",
                )
            )
            order += 1

            calc_cplx = CalculationBuilder(
                f"{symbol} = {_format_number(real_part)} + {_format_number(imag_part)}i, \\quad {symbol} = {_format_number(real_part)} - {_format_number(imag_part)}i"
            )
            steps.append(
                create_solution_step(
                    order=order,
                    title_km="ចម្លើយក្នុងសំណុំចំនួនកុំផ្លិច",
                    title_en="Complex Solutions",
                    description_km=f"ចម្លើយស្មុគស្មាញ៖ {symbol} = {_format_number(real_part)} ± {_format_number(imag_part)}i",
                    description_en=f"Complex solutions: {symbol} = {_format_number(real_part)} ± {_format_number(imag_part)}i",
                    calc=calc_cplx,
                    teacher_note=f"ក្នុងសំណុំចំនួនកុំផ្លិច ℂ សមីការមានឫសពីរគឺ {symbol} = {_format_number(real_part)} ± {_format_number(imag_part)}i។",
                )
            )

        return steps
