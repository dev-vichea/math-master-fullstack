/**
 * Mathematical LaTeX formatting utilities.
 * Converts Python / SymPy mathematical string representations (e.g. x**2, Eq(...), sqrt(...))
 * into clean, valid LaTeX for KaTeX rendering.
 */

export function formatMathToLatex(expr) {
  if (expr === null || expr === undefined) return '';
  let s = String(expr).trim();
  if (!s) return '';

  // 1. Strip wrapping math delimiters ($$...$$, $...$, \(...\)) if already present
  if ((s.startsWith('$$') && s.endsWith('$$')) || (s.startsWith('$') && s.endsWith('$'))) {
    s = s.replace(/^\$\$|\$\$$|^\\\$|\\\$|\$$/g, '').trim();
  }
  if (s.startsWith('\\(') && s.endsWith('\\)')) {
    s = s.slice(2, -2).trim();
  }

  // 2. Convert SymPy Eq(lhs, rhs) -> lhs = rhs
  s = s.replace(/^Eq\s*\(\s*(.*?)\s*,\s*(.*?)\s*\)$/g, '$1 = $2');
  s = s.replace(/\bEq\s*\(\s*(.*?)\s*,\s*(.*?)\s*\)/g, '$1 = $2');

  // 3. Convert Unicode superscripts to LaTeX ^n
  const supMap = {
    '⁰': '^0',
    '¹': '^1',
    '²': '^2',
    '³': '^3',
    '⁴': '^4',
    '⁵': '^5',
    '⁶': '^6',
    '⁷': '^7',
    '⁸': '^8',
    '⁹': '^9',
    'ⁿ': '^n',
    '⁺': '^+',
    '⁻': '^-',
  };
  for (const [k, v] of Object.entries(supMap)) {
    s = s.replaceAll(k, v);
  }

  // 4. Convert Python power ** to LaTeX ^
  // Multi-pass to handle nested or parenthesized expressions: e.g. (x**2 + 1)**3
  for (let pass = 0; pass < 4; pass++) {
    // Parenthesized or bracketed base with parenthesized exponent: (...)...**(...)
    s = s.replace(
      /(\([^\(\)]+\)|\[[^\[\]]+\]|[a-zA-Z0-9_\\]+)\s*\*\*\s*\(([^\(\)]+)\)/g,
      '$1^{$2}'
    );
    // Curly braced exponent: base**{...}
    s = s.replace(
      /(\([^\(\)]+\)|\[[^\[\]]+\]|[a-zA-Z0-9_\\]+)\s*\*\*\s*\{([^}]+)\}/g,
      '$1^{$2}'
    );
    // Base with simple exponent (digits, letters, negative numbers): base**-?123 or base**n
    s = s.replace(
      /(\([^\(\)]+\)|\[[^\[\]]+\]|[a-zA-Z0-9_\\]+)\s*\*\*\s*(-?[a-zA-Z0-9_]+)/g,
      '$1^{$2}'
    );
    // Any remaining ** alone
    s = s.replace(/\s*\*\*\s*/g, '^');
  }

  // 5. Convert sqrt(...) to \sqrt{...}
  for (let pass = 0; pass < 3; pass++) {
    s = s.replace(/(?<!\\)\bsqrt\s*\(([^()]+)\)/g, '\\sqrt{$1}');
  }

  // 6. Greek letters and common mathematical symbols
  s = s.replace(/(?<!\\)\bDelta\b|Δ/g, '\\Delta ');
  s = s.replace(/(?<!\\)\bpi\b|π/g, '\\pi ');
  s = s.replace(/(?<!\\)\btheta\b|θ/g, '\\theta ');
  s = s.replace(/(?<!\\)\bomega\b|ω/g, '\\omega ');
  s = s.replace(/(?<!\\)\balpha\b|α/g, '\\alpha ');
  s = s.replace(/(?<!\\)\bbeta\b|β/g, '\\beta ');
  s = s.replace(/(?<!\\)\bgamma\b|γ/g, '\\gamma ');
  s = s.replace(/-\s*(?<!\\)\boo\b/g, '-\\infty ');
  s = s.replace(/(?<!\\)\boo\b/g, '\\infty ');
  s = s.replace(/±/g, '\\pm ');
  s = s.replace(/≠|!=/g, '\\neq ');
  s = s.replace(/≤|<=/g, '\\le ');
  s = s.replace(/≥|>=/g, '\\ge ');
  s = s.replace(/<==>|<=>/g, '\\iff ');
  s = s.replace(/==>|=>/g, '\\implies ');
  s = s.replace(/-->|->/g, '\\to ');

  // 7. Clean up Python multiplication asterisks
  // Number * variable: 25*x -> 25x, 2*x -> 2x
  s = s.replace(/([0-9]+)\s*\*\s*([a-zA-Z])/g, '$1$2');
  // Variable * variable: x*y -> xy, a*b -> ab
  s = s.replace(/([a-zA-Z])\s*\*\s*([a-zA-Z])/g, '$1$2');
  // Multiplications involving parentheses: 4*(a) -> 4(a), (x+1)*(x-1) -> (x+1)(x-1)
  s = s.replace(/(\)|[0-9a-zA-Z])\s*\*\s*(\()/g, '$1$2');
  s = s.replace(/(\))\s*\*\s*([0-9a-zA-Z])/g, '$1$2');
  // Any leftover standalone * between symbols/numbers -> \cdot
  s = s.replace(/\s*\*\s*/g, ' \\cdot ');

  // 8. Standalone simple fractions: e.g. 25/2 -> \frac{25}{2}, \sqrt{565}/2 -> \frac{\sqrt{565}}{2}
  s = s.replace(/(?<![\\a-zA-Z0-9])([0-9]+)\s*\/\s*([0-9]+)(?![\\a-zA-Z0-9])/g, '\\frac{$1}{$2}');
  s = s.replace(/(\\sqrt\{[^{}]+\})\s*\/\s*([0-9]+)/g, '\\frac{$1}{$2}');

  return s;
}
