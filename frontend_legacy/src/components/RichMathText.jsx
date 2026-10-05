import React from 'react';
import MathView from './MathView';

/**
 * RichMathText parses text that may contain:
 * - Markdown bold: **bold text** -> <strong>bold text</strong>
 * - Inline math: $math$ or \(math\) -> <MathView math={math} />
 * - Block math: $$math$$ -> <MathView math={math} block />
 * - Plain text
 *
 * This ensures that descriptions or explanations containing ** never display
 * raw asterisks, but are cleanly rendered as formatted typography or math.
 */
export default function RichMathText({ text, className = '' }) {
  if (!text) return null;
  const str = String(text);

  // Tokenize by math delimiters ($$...$$, $...$, \(...\)) and markdown bold (**...**)
  const regex = /(\$\$[\s\S]*?\$\$|\$[^$\n]+\$|\\\(.+?\\\)|\*\*[^\*\n]+?\*\*)/g;
  const elements = [];
  let lastIdx = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(str)) !== null) {
    if (match.index > lastIdx) {
      elements.push(
        <span key={`txt-${key++}`}>
          {str.slice(lastIdx, match.index)}
        </span>
      );
    }

    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**') && token.length >= 4) {
      const inner = token.slice(2, -2);
      // If inner text looks like a formula (e.g. x**2 or Δ = b² - 4ac)
      if (inner.includes('**') || inner.includes('^') || inner.includes('=')) {
        elements.push(
          <strong key={`bold-${key++}`} className="rich-bold">
            <MathView math={inner} />
          </strong>
        );
      } else {
        elements.push(
          <strong key={`bold-${key++}`} className="rich-bold">
            {inner}
          </strong>
        );
      }
    } else if (token.startsWith('$$') && token.endsWith('$$')) {
      elements.push(
        <MathView key={`math-block-${key++}`} math={token.slice(2, -2)} block />
      );
    } else if (token.startsWith('$') && token.endsWith('$')) {
      elements.push(
        <MathView key={`math-inline-${key++}`} math={token.slice(1, -1)} />
      );
    } else if (token.startsWith('\\(') && token.endsWith('\\)')) {
      elements.push(
        <MathView key={`math-inline-${key++}`} math={token.slice(2, -2)} />
      );
    }

    lastIdx = regex.lastIndex;
  }

  if (lastIdx < str.length) {
    elements.push(
      <span key={`txt-${key++}`}>
        {str.slice(lastIdx)}
      </span>
    );
  }

  return <span className={`rich-math-text ${className}`}>{elements}</span>;
}
