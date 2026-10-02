import React, { useMemo } from 'react';
import katex from 'katex';

/**
 * Safely renders LaTeX mathematical expressions with KaTeX.
 * Supports inline or displayMode (block).
 */
export default function MathView({ math, block = false, className = '' }) {
  const html = useMemo(() => {
    if (!math) return '';
    const cleanMath = String(math).trim();
    try {
      return katex.renderToString(cleanMath, {
        displayMode: block,
        throwOnError: false,
        strict: false,
      });
    } catch {
      return cleanMath;
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
