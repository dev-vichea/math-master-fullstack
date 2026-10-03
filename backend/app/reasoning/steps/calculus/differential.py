"""
Step-by-step reasoning generator for Differential Equations (Grade 12 BacII Mathematics).

Supports:
1. First-Order Linear Homogeneous ODEs: y' + ay = 0 -> y = A * e^{-ax} (A in R)
2. First-Order Linear Homogeneous with Cauchy Initial Condition: y(x0) = y0
3. Direct Integration: y' = f(x) -> y = int f(x) dx + C
4. Separable ODEs: y'/y = f(x) -> ln|y| = F(x) + c -> y = e^{F(x) + c}
5. Solution Verification: Show that y = f(x) satisfies F(x, y, y') = 0
"""

from __future__ import annotations

import re
from typing import Any

import sympy
from sympy import Derivative, Eq, Function, Symbol, exp, factor, integrate, latex, log, simplify

from app.api.schemas.responses import SolutionStep
from app.knowledge.lessons.differentials import detect_differential_method
from app.reasoning.steps.base import StepGenerator


def _to_latex(expr_or_str: Any) -> str:
    """Format mathematical expression to clean LaTeX using standard BacII notation."""
    if isinstance(expr_or_str, str):
        text = expr_or_str
    else:
        try:
            text = latex(expr_or_str, ln_notation=True)
        except Exception:
            text = latex(expr_or_str)
    # Ensure standard ln notation
    text = re.sub(r"\\log\b", r"\\ln", text)
    # Clean redundant multiplication
    text = re.sub(r"\b1\s*\\cdot\s*", "", text)
    text = re.sub(r"(?<![0-9a-zA-Z])1\s*\\frac", r"\\frac", text)
    text = re.sub(r"\\left\(-1\\right\)\s*(\d+)", r"-\1", text)
    text = re.sub(r"\(-1\)\s*(\d+)", r"-\1", text)
    return text


class DifferentialStepGenerator(StepGenerator):
    """Generates pedagogical step-by-step solutions for first-order differential equations."""

    problem_type = "calculus_differential_equation"

    def generate(
        self,
        eq: sympy.Eq,
        symbol: sympy.Symbol,
        solution: Any = None,
        parsed: Any | None = None,
    ) -> list[SolutionStep]:
        """Implement StepGenerator abstract method."""
        return self.generate_steps(eq, symbol, solution=solution, parsed=parsed)

    def generate_steps(
        self,
        equation: Eq,
        symbol: Symbol,
        solution: Any = None,
        parsed: Any | None = None,
    ) -> list[SolutionStep]:
        """Generate comprehensive bilingual steps for differential equation."""
        metadata = getattr(parsed, "metadata", {}) or {}

        # Case 5: Solution Verification
        if metadata.get("is_verification"):
            return self._generate_verification_steps(equation, symbol, parsed)

        # Classify ODE type
        ode_type = self._classify_ode_type(equation, symbol)

        if ode_type == "linear_homogeneous":
            return self._generate_linear_homogeneous_steps(equation, symbol, parsed)
        elif ode_type == "separable":
            return self._generate_separable_steps(equation, symbol, parsed)
        else:
            return self._generate_direct_integration_steps(equation, symbol, parsed)

    def _classify_ode_type(self, equation: Eq, symbol: Symbol) -> str:
        """Classify the differential equation into linear_homogeneous, separable, or direct."""
        lhs = equation.lhs
        rhs = equation.rhs
        diff = simplify(lhs - rhs)

        y_fn = Function("y")(symbol)
        dy = Derivative(y_fn, symbol)

        # Check if separable form: y'/y = f(x) or y'/g(x) = const
        if isinstance(lhs, sympy.Mul) or isinstance(lhs, sympy.Pow) or "/" in str(lhs):
            # Check for y'/y
            if lhs == dy / y_fn or lhs == dy / symbol:
                return "separable"

        # Check if linear homogeneous in y: A(x)*y' + B(x)*y = 0
        # When expanded, diff has only terms with y or y' and no constant term free of y
        try:
            poly_y = sympy.Poly(diff, [dy, y_fn])
            if poly_y.degree() == 1 and poly_y.EC == 0:
                # Coefficients must not have y
                return "linear_homogeneous"
        except Exception:
            pass

        # Check if diff is A*y' + B*y
        coeff_dy = diff.coeff(dy)
        coeff_y = diff.coeff(y_fn)
        rem = simplify(diff - (coeff_dy * dy + coeff_y * y_fn))
        if coeff_dy != 0 and coeff_y != 0 and rem == 0:
            return "linear_homogeneous"

        return "direct_integration"

    def _generate_linear_homogeneous_steps(
        self, equation: Eq, symbol: Symbol, parsed: Any | None
    ) -> list[SolutionStep]:
        """
        Steps for y' + ay = 0 (and Ay' + By = 0), with or without initial condition:
        Standard form: y' + ay = 0 -> y = A * e^{-ax} (A in R).
        """
        metadata = getattr(parsed, "metadata", {}) or {}
        ics = metadata.get("initial_condition")

        y_fn = Function("y")(symbol)
        dy = Derivative(y_fn, symbol)

        diff = equation.lhs - equation.rhs
        coeff_dy = diff.coeff(dy)
        coeff_y = diff.coeff(y_fn)

        if coeff_dy == 0:
            coeff_dy = sympy.Integer(1)

        # Standard form: y' + a*y = 0 => a = coeff_y / coeff_dy
        a_val = simplify(coeff_y / coeff_dy)
        neg_a = simplify(-a_val)

        steps: list[SolutionStep] = []
        step_order = 1

        # Step 1: Standardize Equation
        orig_latex = _to_latex(equation).replace(r"\frac{d}{d x} y{\left(x \right)}", "y'")
        orig_latex = re.sub(r"\\frac\{d\}\{d [a-zA-Z]\}\s*y(?:\{\\left\([a-zA-Z]\\right\)\})?", "y'", orig_latex)
        orig_latex = orig_latex.replace(r"y{\left(x \right)}", "y").replace(r"y{\left(t \right)}", "y")

        if coeff_dy != 1:
            std_eq_latex = f"y' + {_to_latex(a_val)}y = 0"
            if a_val < 0:
                std_eq_latex = f"y' - {_to_latex(-a_val)}y = 0"
            desc_km = f"សមីការដើម៖ ${orig_latex}$ ឬបម្លែងទៅជាទម្រង់ស្តង់ដារ៖ ${std_eq_latex}$"
            desc_en = f"Original equation: ${orig_latex}$ or transform to standard form: ${std_eq_latex}$"
            expr_step1 = f"{orig_latex} \\iff {std_eq_latex}"
        else:
            desc_km = f"សមីការមានទម្រង់ស្តង់ដារស្រាប់៖ ${orig_latex}$"
            desc_en = f"Equation is already in standard form: ${orig_latex}$"
            expr_step1 = orig_latex

        steps.append(
            SolutionStep(
                order=step_order,
                title_km="សរសេរសមីការក្នុងទម្រង់ស្តង់ដារ",
                title_en="Write in Standard Form",
                description_km=desc_km,
                description_en=desc_en,
                expression=expr_step1,
            )
        )
        step_order += 1

        # Step 2: Identify coefficient a and state general solution formula
        a_str = _to_latex(a_val)
        neg_a_str = _to_latex(neg_a)
        if neg_a == 1:
            exp_power = f"{symbol}"
        elif neg_a == -1:
            exp_power = f"-{symbol}"
        elif ("+" in neg_a_str or "-" in neg_a_str[1:]):
            exp_power = f"({neg_a_str}){symbol}"
        else:
            exp_power = f"{neg_a_str} {symbol}".strip()

        general_sol_latex = f"y = A \\cdot e^{{{exp_power}}}"

        steps.append(
            SolutionStep(
                order=step_order,
                title_km="កំណត់មេគុណ a និងសរសេរចម្លើយទូទៅ",
                title_en="Identify Coefficient a and State General Solution",
                description_km=(
                    f"ដោយ $a = {a_str}$ នោះតាមរូបមន្តចម្លើយទូទៅរបស់សមីការ $y' + ay = 0$ គឺ៖\n"
                    f"${general_sol_latex}$ ដែល $A$ ជាចំនួនថេរ ។"
                ),
                description_en=(
                    f"With $a = {a_str}$, according to the general solution formula for $y' + ay = 0$:\n"
                    f"${general_sol_latex}$, where $A$ is an arbitrary constant."
                ),
                expression=f"a = {a_str} \\implies {general_sol_latex} \\quad (A \\in \\mathbb{{R}})",
            )
        )
        step_order += 1

        # Step 3: Handle Initial Condition if given
        if ics:
            x0_val, y0_val = ics
            x0_str = _to_latex(x0_val)
            y0_str = _to_latex(y0_val)

            # Substitute x0 into general solution: A * e^{neg_a * x0} = y0 => A = y0 / e^{neg_a * x0}
            exp_val_at_x0 = simplify(exp(neg_a * x0_val))
            a_const_val = simplify(y0_val / exp_val_at_x0)
            a_const_str = _to_latex(a_const_val)

            # Particular solution
            particular_sol = simplify(a_const_val * exp(neg_a * symbol))
            part_latex = f"y = {_to_latex(particular_sol)}"

            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="ជំនួសលក្ខខណ្ឌដើមដើម្បីរកថេរ A",
                    title_en="Apply Initial Condition to Find Constant A",
                    description_km=(
                        f"តាមលក្ខខណ្ឌដែលឲ្យ ចំពោះ $x = {x0_str}$ គេបាន៖\n"
                        f"$y({x0_str}) = A \\cdot e^{{{_to_latex(simplify(neg_a * x0_val))}}} = {y0_str}$\n"
                        f"នាំឲ្យ $A = {a_const_str}$ ។"
                    ),
                    description_en=(
                        f"From the given condition, for $x = {x0_str}$ we have:\n"
                        f"$y({x0_str}) = A \\cdot e^{{{_to_latex(simplify(neg_a * x0_val))}}} = {y0_str}$\n"
                        f"which yields $A = {a_const_str}$."
                    ),
                    expression=f"y({x0_str}) = {y0_str} \\implies A = {a_const_str}",
                )
            )
            step_order += 1

            # Final Step
            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="សន្និដ្ឋានចម្លើយពិសេស",
                    title_en="State Final Particular Solution",
                    description_km=f"ដូចនេះ ចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែលដែលផ្ទៀងផ្ទាត់លក្ខខណ្ឌដើមគឺ៖\n${part_latex}$",
                    description_en=f"Therefore, the solution satisfying the initial condition is:\n${part_latex}$",
                    expression=part_latex,
                )
            )
        else:
            # Final conclusion general solution
            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="សន្និដ្ឋានចម្លើយទូទៅ",
                    title_en="State Final General Solution",
                    description_km=f"ដូចនេះ ចម្លើយទូទៅរបស់សមីការគឺ៖\n${general_sol_latex}$ ដែល $A$ ជាចំនួនថេរ ។",
                    description_en=f"Therefore, the general solution of the equation is:\n${general_sol_latex}$ (where $A$ is an arbitrary constant).",
                    expression=f"{general_sol_latex} \\quad (A \\in \\mathbb{{R}})",
                )
            )

        return steps

    def _generate_direct_integration_steps(
        self, equation: Eq, symbol: Symbol, parsed: Any | None
    ) -> list[SolutionStep]:
        """
        Steps for direct integration y' = f(x) or g(x)y' = f(x):
        y = int f(x) dx + C.
        """
        metadata = getattr(parsed, "metadata", {}) or {}
        ics = metadata.get("initial_condition")
        domain = metadata.get("domain")

        y_fn = Function("y")(symbol)
        dy = Derivative(y_fn, symbol)

        diff = equation.lhs - equation.rhs
        # Solve for dy: coeff_dy * dy + rem = 0 => dy = -rem / coeff_dy
        coeff_dy = diff.coeff(dy)
        rem = simplify(diff - coeff_dy * dy)

        if coeff_dy == 0:
            coeff_dy = sympy.Integer(1)

        f_x = simplify(-rem / coeff_dy)
        f_x_latex = _to_latex(f_x)

        steps: list[SolutionStep] = []
        step_order = 1

        # Step 1: Express as indefinite integral
        int_expr_latex = f"y = \\int {f_x_latex}\\,d{symbol}"
        domain_note_km = f" (កំណត់លើ ${domain}$)" if domain else ""
        domain_note_en = f" (defined on ${domain}$)" if domain else ""

        steps.append(
            SolutionStep(
                order=step_order,
                title_km="បម្លែងជាទម្រង់អាំងតេក្រាល",
                title_en="Express as Indefinite Integral",
                description_km=f"គេមានសមីការ $y' = {f_x_latex}${domain_note_km} នាំឲ្យ៖\n${int_expr_latex}$",
                description_en=f"Given equation $y' = {f_x_latex}${domain_note_en}, we have:\n${int_expr_latex}$",
                expression=int_expr_latex,
            )
        )
        step_order += 1

        # Step 2: Compute indefinite integral
        try:
            raw_antideriv = integrate(f_x, symbol)
            antideriv = simplify(raw_antideriv)
        except Exception:
            antideriv = raw_antideriv

        antideriv_latex = _to_latex(antideriv)
        general_sol_latex = f"y = {antideriv_latex} + C"

        steps.append(
            SolutionStep(
                order=step_order,
                title_km="គណនាអាំងតេក្រាល",
                title_en="Compute Antiderivative",
                description_km=(
                    f"គណនាអាំងតេក្រាល $\\int {f_x_latex}\\,d{symbol}$ គេបាន៖\n"
                    f"${general_sol_latex}$ ដែល $C$ ជាចំនួនថេរ ។"
                ),
                description_en=(
                    f"Evaluating the integral $\\int {f_x_latex}\\,d{symbol}$ yields:\n"
                    f"${general_sol_latex}$, where $C$ is an arbitrary constant."
                ),
                expression=f"\\int {f_x_latex}\\,d{symbol} = {antideriv_latex} + C",
            )
        )
        step_order += 1

        # Step 3: Handle Initial Condition if given
        if ics:
            x0_val, y0_val = ics
            x0_str = _to_latex(x0_val)
            y0_str = _to_latex(y0_val)

            # Substitute x0 into antiderivative: antideriv(x0) + C = y0 => C = y0 - antideriv(x0)
            val_at_x0 = simplify(antideriv.subs(symbol, x0_val))
            c_val = simplify(y0_val - val_at_x0)
            c_str = _to_latex(c_val)

            part_sol = simplify(antideriv + c_val)
            part_latex = f"y = {_to_latex(part_sol)}"

            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="ជំនួសលក្ខខណ្ឌដើមដើម្បីរកថេរ C",
                    title_en="Apply Initial Condition to Find Constant C",
                    description_km=(
                        f"តាមលក្ខខណ្ឌដើម ចំពោះ $x = {x0_str}$ គេបាន៖\n"
                        f"$y({x0_str}) = {_to_latex(val_at_x0)} + C = {y0_str}$\n"
                        f"នាំឲ្យ $C = {c_str}$ ។"
                    ),
                    description_en=(
                        f"From the initial condition, for $x = {x0_str}$ we have:\n"
                        f"$y({x0_str}) = {_to_latex(val_at_x0)} + C = {y0_str}$\n"
                        f"which yields $C = {c_str}$."
                    ),
                    expression=f"y({x0_str}) = {y0_str} \\implies C = {c_str}",
                )
            )
            step_order += 1

            # Final Particular Solution
            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="សន្និដ្ឋានចម្លើយពិសេស",
                    title_en="State Final Particular Solution",
                    description_km=f"ដូចនេះ ចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែលគឺ៖\n${part_latex}$",
                    description_en=f"Therefore, the solution of the differential equation is:\n${part_latex}$",
                    expression=part_latex,
                )
            )
        else:
            # Final General Solution
            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="សន្និដ្ឋានចម្លើយទូទៅ",
                    title_en="State Final General Solution",
                    description_km=f"ដូចនេះ ចម្លើយទូទៅនៃសមីការគឺ៖\n${general_sol_latex}$ ដែល $C$ ជាចំនួនថេរ ។",
                    description_en=f"Therefore, the general solution is:\n${general_sol_latex}$ (where $C$ is a constant).",
                    expression=f"{general_sol_latex} \\quad (C \\in \\mathbb{{R}})",
                )
            )

        return steps

    def _generate_separable_steps(
        self, equation: Eq, symbol: Symbol, parsed: Any | None
    ) -> list[SolutionStep]:
        """
        Steps for separable equations like y'/y = cos(x) or y'/tan(x) = 1:
        int (y'/y) dx = int f(x) dx -> ln|y| = F(x) + c -> y = e^{F(x) + c}.
        """
        metadata = getattr(parsed, "metadata", {}) or {}
        ics = metadata.get("initial_condition")

        y_fn = Function("y")(symbol)
        dy = Derivative(y_fn, symbol)

        # Typical case: y'/y = f(x)
        # or y'/g(x) = 1 => y' = g(x)
        lhs = equation.lhs
        rhs = equation.rhs

        steps: list[SolutionStep] = []
        step_order = 1

        # Check if lhs is dy / y_fn
        if lhs == dy / y_fn:
            f_x = rhs
            f_x_latex = _to_latex(f_x)

            # Step 1: Integrate both sides
            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="ធ្វើអាំងតេក្រាលអង្គសងខាង",
                    title_en="Integrate Both Sides",
                    description_km=f"គេមានសមីការ $\\frac{{y'}}{{y}} = {f_x_latex}$ ធ្វើអាំងតេក្រាលអង្គសងខាងធៀបនឹង ${symbol}$៖\n$\\int \\frac{{y'}}{{y}}\\,d{symbol} = \\int {f_x_latex}\\,d{symbol}$",
                    description_en=f"Given equation $\\frac{{y'}}{{y}} = {f_x_latex}$, integrate both sides with respect to ${symbol}$:\n$\\int \\frac{{y'}}{{y}}\\,d{symbol} = \\int {f_x_latex}\\,d{symbol}$",
                    expression=f"\\int \\frac{{y'}}{{y}}\\,d{symbol} = \\int {f_x_latex}\\,d{symbol}",
                )
            )
            step_order += 1

            # Step 2: Compute integrals
            f_integral = integrate(f_x, symbol)
            f_int_latex = _to_latex(f_integral)

            steps.append(
                SolutionStep(
                    order=step_order,
                    title_km="ដោះស្រាយរកអនុគមន៍ y",
                    title_en="Solve for Function y",
                    description_km=(
                        f"គេបាន $\\ln|y| = {f_int_latex} + c$\n"
                        f"នាំឲ្យ $y = e^{{{f_int_latex} + c}}$"
                    ),
                    description_en=(
                        f"We obtain $\\ln|y| = {f_int_latex} + c$\n"
                        f"which gives $y = e^{{{f_int_latex} + c}}$"
                    ),
                    expression=f"\\ln|y| = {f_int_latex} + c \\implies y = e^{{{f_int_latex} + c}}",
                )
            )
            step_order += 1

            # Step 3: Cauchy condition
            if ics:
                x0_val, y0_val = ics
                x0_str = _to_latex(x0_val)
                y0_str = _to_latex(y0_val)

                val_f_x0 = simplify(f_integral.subs(symbol, x0_val))
                # y(x0) = e^{val_f_x0 + c} = y0 => val_f_x0 + c = ln(y0) => c = ln(y0) - val_f_x0
                try:
                    c_val = simplify(log(y0_val) - val_f_x0)
                except Exception:
                    c_val = sympy.Integer(0)

                final_y = simplify(exp(f_integral + c_val))
                final_y_latex = f"y = {_to_latex(final_y)}"

                steps.append(
                    SolutionStep(
                        order=step_order,
                        title_km="ជំនួសលក្ខខណ្ឌដើមដើម្បីរកថេរ c",
                        title_en="Apply Initial Condition to Find Constant c",
                        description_km=(
                            f"ចំពោះ $x = {x0_str}$ គេបាន៖\n"
                            f"$y({x0_str}) = e^{{{_to_latex(val_f_x0)} + c}} = {y0_str}$\n"
                            f"នាំឲ្យ $c = {_to_latex(c_val)}$ ។"
                        ),
                        description_en=(
                            f"For $x = {x0_str}$, we have:\n"
                            f"$y({x0_str}) = e^{{{_to_latex(val_f_x0)} + c}} = {y0_str}$\n"
                            f"which implies $c = {_to_latex(c_val)}$."
                        ),
                        expression=f"y({x0_str}) = {y0_str} \\implies c = {_to_latex(c_val)}",
                    )
                )
                step_order += 1

                steps.append(
                    SolutionStep(
                        order=step_order,
                        title_km="សន្និដ្ឋានចម្លើយពិសេស",
                        title_en="State Final Particular Solution",
                        description_km=f"ដូចនេះ ចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែលគឺ៖\n${final_y_latex}$",
                        description_en=f"Therefore, the particular solution is:\n${final_y_latex}$",
                        expression=final_y_latex,
                    )
                )
            else:
                steps.append(
                    SolutionStep(
                        order=step_order,
                        title_km="សន្និដ្ឋានចម្លើយទូទៅ",
                        title_en="State Final General Solution",
                        description_km=f"ដូចនេះ ចម្លើយទូទៅគឺ $y = e^{{{f_int_latex} + c}} = A \\cdot e^{{{f_int_latex}}}$ ដែល $A$ ជាចំនួនថេរ ។",
                        description_en=f"Therefore, the general solution is $y = A \\cdot e^{{{f_int_latex}}}$ (where $A$ is a constant).",
                        expression=f"y = A \\cdot e^{{{f_int_latex}}} \\quad (A \\in \\mathbb{{R}})",
                    )
                )
            return steps

        # Fallback to direct integration if separable in other ways (e.g. y' / tan(x) = 1)
        return self._generate_direct_integration_steps(equation, symbol, parsed)

    def _generate_verification_steps(
        self, equation: Eq, symbol: Symbol, parsed: Any
    ) -> list[SolutionStep]:
        """
        Steps for showing that y = f(x) satisfies a given differential equation F(x, y, y') = 0.
        """
        metadata = getattr(parsed, "metadata", {}) or {}
        vfunc = metadata.get("verification_func")
        if vfunc is None:
            vfunc = symbol

        y_fn = Function("y")(symbol)
        dy = Derivative(y_fn, symbol)

        vfunc_latex = _to_latex(vfunc)
        ode_latex = _to_latex(equation).replace(r"\frac{d}{d x} y{\left(x \right)}", "y'")
        ode_latex = ode_latex.replace(r"y{\left(x \right)}", "y")

        steps: list[SolutionStep] = []

        # Step 1: Compute derivative of given function
        y_prime_val = simplify(sympy.diff(vfunc, symbol))
        y_prime_latex = _to_latex(y_prime_val)

        steps.append(
            SolutionStep(
                order=1,
                title_km="គណនាដេរីវេនៃអនុគមន៍ដែលឲ្យ",
                title_en="Compute Derivative of Given Function",
                description_km=(
                    f"គេមានអនុគមន៍ $y = {vfunc_latex}$\n"
                    f"គណនាដេរីវេទី១ គេបាន៖\n"
                    f"$y' = ({vfunc_latex})' = {y_prime_latex}$"
                ),
                description_en=(
                    f"Given function $y = {vfunc_latex}$\n"
                    f"Computing first derivative:\n"
                    f"$y' = ({vfunc_latex})' = {y_prime_latex}$"
                ),
                expression=f"y' = {y_prime_latex}",
            )
        )

        # Step 2: Substitute into LHS of ODE
        sub_dict = {dy: y_prime_val, y_fn: vfunc}
        lhs_val = simplify(equation.lhs.subs(sub_dict))
        rhs_val = simplify(equation.rhs.subs(sub_dict))
        is_valid = simplify(lhs_val - rhs_val) == 0

        lhs_expr_latex = _to_latex(equation.lhs).replace(r"\frac{d}{d x} y{\left(x \right)}", "y'").replace(r"y{\left(x \right)}", "y")
        lhs_val_latex = _to_latex(lhs_val)
        rhs_val_latex = _to_latex(rhs_val)

        steps.append(
            SolutionStep(
                order=2,
                title_km="ជំនួស y និង y' ចូលក្នុងអង្គខាងឆ្វេងនៃសមីការ",
                title_en="Substitute y and y' into LHS of Differential Equation",
                description_km=(
                    f"ជំនួស $y = {vfunc_latex}$ និង $y' = {y_prime_latex}$ ទៅក្នុងអង្គខាងឆ្វេង (LHS)៖\n"
                    f"${lhs_expr_latex} = {lhs_val_latex}$"
                ),
                description_en=(
                    f"Substituting $y = {vfunc_latex}$ and $y' = {y_prime_latex}$ into the left-hand side (LHS):\n"
                    f"${lhs_expr_latex} = {lhs_val_latex}$"
                ),
                expression=f"{lhs_expr_latex} = {lhs_val_latex}",
            )
        )

        # Step 3: Compare and conclude
        if is_valid:
            conclusion_km = (
                f"ឃើញថាអង្គខាងឆ្វេងស្មើនឹងអង្គខាងស្តាំ (${lhs_val_latex} = {rhs_val_latex}$) ។\n"
                f"ដូចនេះ អនុគមន៍ $y = {vfunc_latex}$ ពិតជាចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែល ${ode_latex}$ ។"
            )
            conclusion_en = (
                f"The left-hand side equals the right-hand side (${lhs_val_latex} = {rhs_val_latex}$).\n"
                f"Therefore, the function $y = {vfunc_latex}$ is indeed a solution to the differential equation ${ode_latex}$."
            )
            verif_expr = f"{lhs_val_latex} = {rhs_val_latex} \\quad (\\text{{ពិត / Verified}})"
        else:
            conclusion_km = f"អង្គខាងឆ្វេងមិនស្មើនឹងអង្គខាងស្តាំ (${lhs_val_latex} \\ne {rhs_val_latex}$) ។ ដូចនេះ អនុគមន៍មិនមែនជាចម្លើយទេ។"
            conclusion_en = f"The left-hand side does not equal the right-hand side. Therefore, the function is not a solution."
            verif_expr = f"{lhs_val_latex} \\ne {rhs_val_latex}"

        steps.append(
            SolutionStep(
                order=3,
                title_km="សន្និដ្ឋានការផ្ទៀងផ្ទាត់",
                title_en="Conclude Verification",
                description_km=conclusion_km,
                description_en=conclusion_en,
                expression=verif_expr,
            )
        )

        return steps
