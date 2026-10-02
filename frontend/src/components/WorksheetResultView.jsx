import React, { useState } from 'react';
import MathView from './MathView';
import SolutionView from './SolutionView';
import { FileText, CheckCircle, ListOrdered, ChevronRight } from 'lucide-react';

export default function WorksheetResultView({ data, lang = 'km' }) {
  const [activeProblemIdx, setActiveProblemIdx] = useState(0);

  if (!data) return null;

  const exercise = data.exercise || {};
  const solutions = data.solutions || [];
  const statistics = data.statistics || {};

  const currentSolution = solutions[activeProblemIdx]?.solution_data || solutions[activeProblemIdx];

  return (
    <div className="worksheet-result-container">
      {/* Top Summary Banner */}
      <div className="ws-summary-card">
        <div className="ws-summary-title-row">
          <div className="ws-badge-group">
            <FileText size={18} className="text-cyan" />
            <h3>លទ្ធផលវិភាគសន្លឹកកិច្ចការ (Worksheet Analysis)</h3>
          </div>
          <span className="badge badge-verified">
            <CheckCircle size={14} />
            <span>វិភាគបាន {solutions.length} លំហាត់</span>
          </span>
        </div>

        {exercise.instruction && (
          <div className="ws-instruction-box">
            <span className="ws-inst-label">ការណែនាំ (Instruction):</span>
            <span className="ws-inst-text">{exercise.instruction}</span>
          </div>
        )}

        {exercise.shared_context && Object.keys(exercise.shared_context).length > 0 && (
          <div className="ws-context-box">
            <span className="ws-context-label">អថេររួម (Shared Variables):</span>
            <div className="ws-context-vars">
              {Object.entries(exercise.shared_context).map(([k, v], idx) => (
                <span key={idx} className="var-chip">
                  <MathView math={`${k} = ${v}`} />
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Problem Selector Bar */}
      {solutions.length > 0 && (
        <div className="ws-problem-nav">
          <span className="nav-label">បញ្ជីលំហាត់ (Problems):</span>
          <div className="nav-buttons">
            {solutions.map((item, idx) => {
              const label = item.label || item.problem_id || `${idx + 1}`;
              const isSelected = idx === activeProblemIdx;
              return (
                <button
                  key={idx}
                  type="button"
                  className={`ws-prob-btn ${isSelected ? 'active' : ''}`}
                  onClick={() => setActiveProblemIdx(idx)}
                >
                  <span className="prob-label">{label}</span>
                  {item.expression && (
                    <span className="prob-math-preview">
                      <MathView math={item.expression} />
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Selected Problem Solution */}
      {currentSolution ? (
        <SolutionView solution={currentSolution} lang={lang} />
      ) : (
        <div className="empty-selection">
          <p>ជ្រើសរើសលំហាត់មួយខាងលើដើម្បីមើលដំណោះស្រាយលម្អិត</p>
        </div>
      )}
    </div>
  );
}
