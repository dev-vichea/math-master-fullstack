import React from "react";
import katex from "katex";

interface MathViewProps {
  math: string;
  displayMode?: boolean;
  className?: string;
}

export function sanitizeExplanationText(text: string): string {
  if (!text) return "";
  return text
    .replace(/ពីលោកគ្រូ/g, "")
    .replace(/លោកគ្រូ/g, "")
    .replace(/កូនត្រូវចាំ/g, "ត្រូវចាំ")
    .replace(/កូនត្រូវ/g, "ត្រូវ")
    .replace(/កូនអាច/g, "អាច")
    .replace(/កូនសង្កេតឃើញ/g, "សង្កេតឃើញ")
    .replace(/កូនសង្កេតមើល/g, "សង្កេតមើល")
    .replace(/កូនកុំភ្លេច/g, "កុំភ្លេច")
    .replace(/កូនបោះ/g, "បោះ")
    .replace(/កូនបំពាក់/g, "បំពាក់")
    .replace(/កូនគណនា/g, "គណនា")
    .replace(/កូនផ្លាស់ទី/g, "ផ្លាស់ទី")
    .replace(/កូនដាក់/g, "ដាក់")
    .replace(/កូនឱ្យ/g, "ឱ្យ")
    .replace(/កូនស្រង់/g, "ស្រង់")
    .replace(/កូនជំនួស/g, "ជំនួស")
    .replace(/កូនធ្វើការ/g, "ធ្វើការ")
    .replace(/កូនប្រយ័ត្ន/g, "ប្រយ័ត្ន")
    .replace(/ពេលកូន/g, "ពេល")
    .replace(/ដើម្បីឱ្យកូន/g, "ដើម្បី")
    .replace(/សម្រាប់កូន/g, "សម្រាប់")
    .replace(/កូន/g, "")
    .replace(/របស់យើង/g, "")
    .replace(/ឱ្យយើង/g, "ឱ្យ")
    .replace(/យើងត្រូវ/g, "ត្រូវ")
    .replace(/យើងអាច/g, "អាច")
    .replace(/យើងប្រើ/g, "ប្រើ")
    .replace(/យើងមាន/g, "មាន")
    .replace(/យើងទទួលបាន/g, "ទទួលបាន")
    .replace(/យើងបាន/g, "បាន")
    .replace(/យើងទាញបាន/g, "ទាញបាន")
    .replace(/យើង/g, "");
}

export function MathView({ math, displayMode = false, className = "" }: MathViewProps) {
  if (!math) return null;

  let raw = math.trim();
  let isBlock = displayMode;

  // 1. Strip outer enclosing delimiters ($$, \[, $, \() FIRST
  if (raw.startsWith("$$") && raw.endsWith("$$") && raw.length >= 4) {
    raw = raw.slice(2, -2).trim();
    isBlock = true;
  } else if (raw.startsWith("\\[") && raw.endsWith("\\]") && raw.length >= 4) {
    raw = raw.slice(2, -2).trim();
    isBlock = true;
  } else if (raw.startsWith("$") && raw.endsWith("$") && raw.length >= 2) {
    raw = raw.slice(1, -1).trim();
  } else if (raw.startsWith("\\(") && raw.endsWith("\\)") && raw.length >= 4) {
    raw = raw.slice(2, -2).trim();
  }

  // Normalize escaped \n, \newline, and \\ into real newlines if not inside LaTeX array/matrix
  if (!raw.includes("\\begin{")) {
    raw = raw
      .replace(/\\newline\b/g, "\n")
      .replace(/\\n\b/g, "\n")
      .replace(/\\\\/g, "\n");
  }

  // 2. Multi-line math: split by newline (\n) to render vertically enter-line, centered
  const newlineLines = raw.split(/\r?\n+/).map((l) => l.trim()).filter(Boolean);
  if (newlineLines.length > 1) {
    return (
      <div className={`flex flex-col items-center justify-center space-y-2 text-center w-full my-1.5 ${className}`}>
        {newlineLines.map((line, idx) => (
          <MathView key={idx} math={line} displayMode={true} />
        ))}
      </div>
    );
  }

  try {
    const html = katex.renderToString(raw, {
      displayMode: isBlock,
      throwOnError: false,
      output: "htmlAndMathml",
    });

    if (!isBlock) {
      return (
        <span
          className={`inline-block font-sans ${className}`}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    }

    return (
      <div
        className={`w-full flex items-center justify-center text-center overflow-x-auto py-1 font-display ${className}`}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  } catch {
    return <span className={`font-mono ${className}`}>{raw}</span>;
  }
}

export function RichMathText({ text, className = "" }: { text: string; className?: string }) {
  if (!text) return null;

  // Sanitize text to remove "កូន", "ពីលោកគ្រូ", "លោកគ្រូ", "យើង"
  const clean = sanitizeExplanationText(text);
  const lines = clean.split("\n");

  return (
    <div className={`space-y-1.5 ${className}`}>
      {lines.map((line, lIdx) => {
        let trimmed = line.trim();
        if (!trimmed) return <div key={lIdx} className="h-1.5" />;

        // Clean out labels like ភាគយក៖, ភាគបែង៖, Numerator:, Denominator:
        const isFracLabel = /^(ភាគយក|ភាគបែង|Numerator|Denominator)[៖:]\s*/i.test(trimmed);
        if (isFracLabel) {
          trimmed = trimmed.replace(/^(ភាគយក|ភាគបែង|Numerator|Denominator)[៖:]\s*/i, "").trim();
        }
        if (!trimmed) return null;

        // If line was ភាគយក/ភាគបែង or is a single math expression wrapped in $, render centered math
        if (isFracLabel || /^\$\$?([^$]+)\$\$?$/.test(trimmed)) {
          const inner = trimmed.replace(/^\$\$?|\$\$?$/g, "").trim();
          return (
            <div key={lIdx} className="my-1 flex justify-center text-center w-full">
              <MathView math={inner} displayMode={true} />
            </div>
          );
        }

        // 1. Text with explicit $...$ or $$...$$ delimiters
        if (trimmed.includes("$")) {
          const parts = trimmed.split(/(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)/g);
          return (
            <p key={lIdx} className="leading-relaxed">
              {parts.map((part, pIdx) => {
                if (part.startsWith("$$") && part.endsWith("$$")) {
                  return <MathView key={pIdx} math={part.slice(2, -2)} displayMode={true} />;
                }
                if (part.startsWith("$") && part.endsWith("$")) {
                  return <MathView key={pIdx} math={part.slice(1, -1)} />;
                }
                return <span key={pIdx}>{part}</span>;
              })}
            </p>
          );
        }

        // 2. Line with a label prefix followed by LaTeX
        const labelColonMatch = trimmed.match(/^([^៖:\n]+[៖:])\s*(.+)$/);
        if (labelColonMatch) {
          const label = labelColonMatch[1];
          const rest = labelColonMatch[2];
          const looksLikeMath = /[\^\\_{}=]|\d+\s*[-+*/]/.test(rest);
          if (looksLikeMath) {
            return (
              <p key={lIdx} className="leading-relaxed flex items-baseline flex-wrap gap-x-1.5">
                <span className="font-semibold opacity-90">{label}</span>
                <MathView math={rest} />
              </p>
            );
          }
        }

        // 3. Pure math expression without delimiters (e.g. "2x = 11 - 3" or "a^2 - b^2 = (a-b)(a+b)")
        const isPureMath =
          (/^(\\[a-zA-Z]+|[a-zA-Z0-9^_{}()=+\-*/\s\\]+)$/.test(trimmed) && /[\^\\_{}=]/.test(trimmed)) ||
          /^(\d+[a-zA-Z]?|[a-zA-Z])\s*[-+*/=]/.test(trimmed);
        if (isPureMath) {
          return (
            <div key={lIdx} className="my-1.5 flex justify-center text-center w-full">
              <MathView math={trimmed} displayMode={true} />
            </div>
          );
        }

        // 4. Regular text line
        return (
          <p key={lIdx} className="leading-relaxed">
            {trimmed}
          </p>
        );
      })}
    </div>
  );
}
