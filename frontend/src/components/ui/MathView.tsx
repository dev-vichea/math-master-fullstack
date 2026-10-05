import React from "react";
import katex from "katex";

interface MathViewProps {
  math: string;
  displayMode?: boolean;
  className?: string;
}

export function MathView({ math, displayMode = false, className = "" }: MathViewProps) {
  if (!math) return null;

  try {
    // Clean up typical delimiters if present
    let raw = math.trim();
    if (raw.startsWith("$$") && raw.endsWith("$$")) {
      raw = raw.slice(2, -2).trim();
      displayMode = true;
    } else if (raw.startsWith("$") && raw.endsWith("$")) {
      raw = raw.slice(1, -1).trim();
    } else if (raw.startsWith("\\[") && raw.endsWith("\\]")) {
      raw = raw.slice(2, -2).trim();
      displayMode = true;
    } else if (raw.startsWith("\\(") && raw.endsWith("\\)")) {
      raw = raw.slice(2, -2).trim();
    }

    const html = katex.renderToString(raw, {
      displayMode,
      throwOnError: false,
      output: "htmlAndMathml",
    });

    return (
      <span
        className={`inline-block font-sans ${className}`}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  } catch {
    return <span className={`font-mono ${className}`}>{math}</span>;
  }
}
