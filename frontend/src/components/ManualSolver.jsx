import React, { useState } from 'react';
import MathView from './MathView';
import MathLiveInput from './MathLiveInput';
import { Sparkles, Send, RotateCcw, Keyboard, AlignLeft } from 'lucide-react';

const PRESETS = [
  {
    category: 'ស្វ៊ីត (Sequence)',
    label: 'លីមីតស្វ៊ីត BacII',
    text: 'គណនាលីមីតស្វ៊ីត u_n = \\frac{3n^2 - 2}{5n^2 + 7n + 1}',
    preview: '\\lim_{n \\to +\\infty} \\frac{3n^2 - 2}{5n^2 + 7n + 1}',
  },
  {
    category: 'ស្វ៊ីត (Sequence)',
    label: 'ស្វ៊ីតកំណត់ដោយទំនាក់ទំនង',
    text: 'រកតួទូទៅ a_1 = 2, a_{n+1} = \\frac{1}{2}a_n + 3',
    preview: 'a_1 = 2, \\, a_{n+1} = \\frac{1}{2}a_n + 3',
  },
  {
    category: 'លីមីត (Limit)',
    label: 'លីមីតត្រីកោណមាត្រ BacII C',
    text: '\\lim_{x \\to 0} \\frac{\\sin^2 x}{1 - \\cos^4 x}',
    preview: '\\lim_{x \\to 0} \\frac{\\sin^2 x}{1 - \\cos^4 x}',
  },
  {
    category: 'លីមីត (Limit)',
    label: 'លីមីតកន្សោមរ៉ាឌីកាល់ BacII',
    text: '\\lim_{x \\to 2} \\frac{4(\\sqrt{x+2} - 2)}{4 - x^2}',
    preview: '\\lim_{x \\to 2} \\frac{4(\\sqrt{x+2} - 2)}{4 - x^2}',
  },
  {
    category: 'អាំងតេក្រាល (Integral)',
    label: 'អាំងតេក្រាលកំណត់',
    text: '\\int_{0}^{\\pi} \\sin(x) dx',
    preview: '\\int_{0}^{\\pi} \\sin(x) dx',
  },
  {
    category: 'លោការីត (Logarithm)',
    label: 'សមីការលោការីតនេពែ',
    text: 'ដោះស្រាយ \\ln(x^2 - 1) = \\ln(3)',
    preview: '\\ln(x^2 - 1) = \\ln(3)',
  },
  {
    category: 'ពិជគណិត (Algebra)',
    label: 'សមីការដឺក្រេទី២',
    text: 'ដោះស្រាយ x^2 - 5x + 6 = 0',
    preview: 'x^2 - 5x + 6 = 0',
  },
];

export default function ManualSolver({ onSolve, loading, externalQuestion }) {
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'mathfield'
  const [question, setQuestion] = useState('គណនាលីមីតស្វ៊ីត u_n = \\frac{3n^2 - 2}{5n^2 + 7n + 1}');

  React.useEffect(() => {
    if (externalQuestion) {
      setQuestion(externalQuestion);
      onSolve(externalQuestion);
    }
  }, [externalQuestion]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!question.trim() || loading) return;
    onSolve(question.trim());
  };

  const handleInsertPrefix = (prefix) => {
    setQuestion((prev) => `${prefix}${prev}`);
  };

  const handleSelectPreset = (preset) => {
    setQuestion(preset.text);
    onSolve(preset.text);
  };

  return (
    <div className="solver-panel">
      <div className="solver-mode-selector">
        <button
          type="button"
          className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
          onClick={() => setInputMode('text')}
        >
          <AlignLeft size={16} />
          <span>អត្ថបទខ្មែរ + រូបមន្ត (Text & LaTeX)</span>
        </button>
        <button
          type="button"
          className={`mode-btn ${inputMode === 'mathfield' ? 'active' : ''}`}
          onClick={() => setInputMode('mathfield')}
        >
          <Keyboard size={16} />
          <span>ក្ដារចុចគណិត (Visual MathLive)</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="solver-form">
        {/* Intent Shortcuts */}
        <div className="intent-chips">
          <span className="chips-title">បញ្ជា (Intents):</span>
          <button type="button" className="chip" onClick={() => handleInsertPrefix('ដោះស្រាយ ')}>
            ដោះស្រាយ (Solve)
          </button>
          <button type="button" className="chip" onClick={() => handleInsertPrefix('គណនា ')}>
            គណនា (Calculate)
          </button>
          <button type="button" className="chip" onClick={() => handleInsertPrefix('គណនាលីមីតស្វ៊ីត ')}>
            លីមីតស្វ៊ីត (Seq Limit)
          </button>
          <button type="button" className="chip" onClick={() => handleInsertPrefix('រកដេរីវេ ')}>
            ដេរីវេ (Derivative)
          </button>
          <button type="button" className="chip" onClick={() => handleInsertPrefix('គណនាអាំងតេក្រាល ')}>
            អាំងតេក្រាល (Integral)
          </button>
        </div>

        {/* Input Field */}
        <div className="input-container">
          {inputMode === 'text' ? (
            <div className="textarea-wrapper">
              <textarea
                className="math-textarea"
                rows={3}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="បញ្ចូលសំណួរជាភាសាខ្មែរ ឬរូបមន្ត LaTeX (ឧ. ដោះស្រាយ 2x + 5 = 15 ឬ \lim_{x \to 0} ...)"
              />
              <div className="textarea-footer">
                <span className="char-count">{question.length}/500</span>
                {question && (
                  <button
                    type="button"
                    className="btn-clear"
                    onClick={() => setQuestion('')}
                    title="Clear input"
                  >
                    <RotateCcw size={14} />
                    <span>Clear</span>
                  </button>
                )}
              </div>
            </div>
          ) : (
            <MathLiveInput value={question} onChange={setQuestion} />
          )}
        </div>

        {/* Live KaTeX Preview */}
        {question && (
          <div className="live-preview-box">
            <div className="preview-label">
              <span className="pulse-indicator"></span>
              <span>ទិដ្ឋភាពរូបមន្តផ្ទាល់ (Live KaTeX Preview)</span>
            </div>
            <div className="preview-content">
              <MathView math={question} block />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="submit-row">
          <button
            type="submit"
            className="btn-solve-primary"
            disabled={loading || !question.trim()}
          >
            {loading ? (
              <>
                <span className="btn-spinner"></span>
                <span>កំពុងគណនាដោយ SymPy...</span>
              </>
            ) : (
              <>
                <Send size={18} />
                <span>ដោះស្រាយលំហាត់ (Solve Problem)</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Curriculum Quick Presets */}
      <div className="presets-box">
        <div className="presets-header">
          <Sparkles size={16} className="sparkle-icon" />
          <span>លំហាត់គំរូបាក់ឌុប (BacII Grade 12 Presets):</span>
        </div>
        <div className="presets-grid">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-card"
              onClick={() => handleSelectPreset(p)}
            >
              <div className="preset-meta">
                <span className="preset-category">{p.category}</span>
                <span className="preset-label">{p.label}</span>
              </div>
              <div className="preset-math">
                <MathView math={p.preview} />
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
