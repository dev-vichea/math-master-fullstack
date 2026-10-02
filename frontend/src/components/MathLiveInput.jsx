import React, { useEffect, useRef } from 'react';
import 'mathlive';

export default function MathLiveInput({ value, onChange, placeholder = 'វាយរូបមន្តគណិតវិទ្យាទីនេះ (Type math here)...' }) {
  const mfRef = useRef(null);

  useEffect(() => {
    const mf = mfRef.current;
    if (!mf) return;

    // Set initial value
    if (value !== undefined && mf.value !== value) {
      mf.value = value;
    }

    const handleInput = () => {
      if (onChange) {
        onChange(mf.value);
      }
    };

    mf.addEventListener('input', handleInput);
    return () => {
      mf.removeEventListener('input', handleInput);
    };
  }, [onChange, value]);

  const insertSymbol = (latex) => {
    if (mfRef.current) {
      mfRef.current.executeCommand(['insert', latex]);
      mfRef.current.focus();
    }
  };

  return (
    <div className="mathlive-container">
      <div className="mathlive-field-wrapper">
        <math-field
          ref={mfRef}
          style={{
            display: 'block',
            width: '100%',
            padding: '12px 16px',
            fontSize: '1.25rem',
            borderRadius: '10px',
            background: 'var(--color-surface-elevated)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-border)',
            outline: 'none',
          }}
        >
          {value}
        </math-field>
      </div>

      {/* Quick math symbol toolbar */}
      <div className="mathlive-toolbar">
        <span className="toolbar-label">និមិត្តសញ្ញារហ័ស (Quick Symbols):</span>
        <div className="toolbar-buttons">
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\frac{#@}{#?}')}>
            \frac{a}{b}
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\sqrt{#@}')}>
            \sqrt{x}
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('^{2}')}>
            x²
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('^{#?}')}>
            xⁿ
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\lim_{x \\to 0} ')}>
            lim x→0
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\lim_{x \\to +\\infty} ')}>
            lim x→+∞
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\lim_{n \\to +\\infty} ')}>
            lim n→+∞
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\int_{#?}^{#?} #@ \\, dx')}>
            \int_a^b
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\ln(#@)')}>
            \ln(x)
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('u_{n+1}')}>
            u_{'{n+1}'}
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\sin(#@)')}>
            \sin
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\cos(#@)')}>
            \cos
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\le ')}>
            ≤
          </button>
          <button type="button" className="sym-btn" onClick={() => insertSymbol('\\ge ')}>
            ≥
          </button>
        </div>
      </div>
    </div>
  );
}
