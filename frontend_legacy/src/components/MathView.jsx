import React, { useMemo } from 'react';
import katex from 'katex';
import { formatMathToLatex } from '../utils/mathFormatter';

/**
 * Safely renders mathematical expressions with KaTeX.
 * Automatically converts Python / SymPy formatting (e.g. x**2, Eq(...), sqrt(...))
 * into clean standard LaTeX.
 * Supports inline or displayMode (block).
 */
export default function MathView({ math, block = false, className = '' }) {
  const html = useMemo(() => {
    if (!math) return '';
    const latexExpr = formatMathToLatex(math);
    try {
      return katex.renderToString(latexExpr, {
        displayMode: block,
        throwOnError: false,
        strict: false,
      });
    } catch {
      // Fallback: render without crashing
      try {
        return katex.renderToString(`\\text{${latexExpr}}`, {
          displayMode: block,
          throwOnError: false,
        });
      } catch {
        return latexExpr;
      }
    }
  }, [math, block]);

  if (!math) return null;

  return (
    <span
      className={`katex-wrapper ${block ? 'katex-block' : 'katex-inline'} ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
