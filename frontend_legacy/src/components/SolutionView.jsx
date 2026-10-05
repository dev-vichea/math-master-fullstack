import React, { useEffect, useState } from 'react';
import MathView from './MathView';
import RichMathText from './RichMathText';
import confetti from 'canvas-confetti';
import {
  CheckCircle2,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Award,
  Sparkles,
  HelpCircle,
} from 'lucide-react';

export default function SolutionView({ solution, lang = 'km' }) {
  const [copied, setCopied] = useState(false);
  const [openSteps, setOpenSteps] = useState({});

  useEffect(() => {
    if (solution?.is_verified) {
      try {
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.6 },
          colors: ['#10b981', '#06b6d4', '#6366f1', '#f59e0b'],
        });
      } catch {
        // Confetti optional
      }
    }

    // Default: all steps open
    if (solution?.steps) {
      const initial = {};
      solution.steps.forEach((_, idx) => {
        initial[idx] = true;
      });
      setOpenSteps(initial);
    }
  }, [solution]);

  if (!solution) return null;

  const toggleStep = (idx) => {
    setOpenSteps((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const toggleAll = (open) => {
    if (!solution.steps) return;
    const update = {};
    solution.steps.forEach((_, idx) => {
      update[idx] = open;
    });
    setOpenSteps(update);
  };

  const handleCopyAnswer = () => {
    const textToCopy = solution.answer || solution.normalized_expression || '';
    navigator.clipboard?.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lesson = solution.lesson_info;

  return (
    <div className="solution-view">
      {/* Hero Answer Banner */}
      <div className="hero-answer-card">
        <div className="hero-top-meta">
          <span className="badge badge-type">{solution.problem_type || 'Math Problem'}</span>
          {solution.is_verified && (
            <span className="badge badge-verified">
              <CheckCircle2 size={14} />
              <span>ផ្ទៀងផ្ទាត់ត្រឹមត្រូវ (Verified by SymPy)</span>
            </span>
          )}
        </div>

        <div className="hero-main-answer">
          <span className="hero-label">
            {lang === 'km' ? 'ចម្លើយចុងក្រោយ (Final Answer):' : 'Final Answer:'}
          </span>
          <div className="hero-expression">
            {solution.variable && <span className="var-tag">{solution.variable} = </span>}
            <MathView math={solution.answer || '✓ ដោះស្រាយរួចរាល់'} block={false} className="answer-math" />
          </div>
        </div>

        <div className="hero-bottom-actions">
          <span className="normalized-expression-text">
            <span>សមីការដើម: </span>
            <MathView math={solution.normalized_expression || solution.original_question} />
          </span>
          <button type="button" className="btn-copy" onClick={handleCopyAnswer}>
            {copied ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
            <span>{copied ? 'ចម្លងរួច' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Curriculum Lesson Banner */}
      {lesson && (
        <div className="curriculum-banner">
          <div className="curriculum-header">
            <div className="curriculum-tag">
              <BookOpen size={16} />
              <span>កម្មវិធីសិក្សាថ្នាក់ទី១២ (Curriculum Standard)</span>
            </div>
            {lesson.rule_formula && (
              <div className="rule-pill">
                <span className="rule-label">រូបមន្តគន្លឹះ:</span>
                <MathView math={lesson.rule_formula} />
              </div>
            )}
          </div>
          <div className="curriculum-breadcrumbs">
            {(lesson.chapter_km || lesson.chapter_title_km) && (
              <span className="crumb crumb-chapter">{lesson.chapter_km || lesson.chapter_title_km}</span>
            )}
            {(lesson.lesson_km || lesson.lesson_title_km) && (
              <>
                <span className="crumb-separator">›</span>
                <span className="crumb crumb-lesson">{lesson.lesson_km || lesson.lesson_title_km}</span>
              </>
            )}
            {(lesson.method_km || lesson.curriculum_method) && (
              <>
                <span className="crumb-separator">›</span>
                <span className="crumb crumb-method">{lesson.method_km || lesson.curriculum_method}</span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Steps List */}
      {solution.steps && solution.steps.length > 0 && (
        <div className="steps-container">
          <div className="steps-header">
            <div className="steps-title">
              <Sparkles size={18} className="text-indigo" />
              <h3>
                {lang === 'km'
                  ? 'ដំណាក់កាលដោះស្រាយ (Step-by-Step Solution)'
                  : 'Step-by-Step Pedagogical Solution'}
              </h3>
            </div>
            <div className="steps-controls">
              <button type="button" className="btn-text-action" onClick={() => toggleAll(true)}>
                ពន្លាតទាំងអស់ (Expand)
              </button>
              <span className="control-divider">|</span>
              <button type="button" className="btn-text-action" onClick={() => toggleAll(false)}>
                បង្រួម (Collapse)
              </button>
            </div>
          </div>

          <div className="steps-list">
            {solution.steps.map((step, idx) => {
              const isOpen = openSteps[idx] ?? true;
              const stepTitle =
                lang === 'km'
                  ? step.title_km || step.description_km
                  : step.title_en || step.description_en || step.description_km;
              const stepDesc = lang === 'km' ? step.description_km : step.description_en || step.description_km;
              const rationale = lang === 'km' ? step.rationale_km : step.rationale_en || step.rationale_km;

              return (
                <div key={idx} className={`step-card ${isOpen ? 'open' : 'closed'} ${step.is_verification ? 'verification-step' : ''}`}>
                  <div className="step-card-header" onClick={() => toggleStep(idx)}>
                    <div className="step-order-badge">{step.order || idx + 1}</div>
                    <div className="step-header-text">
                      <span className="step-title">
                        <RichMathText text={stepTitle} />
                      </span>
                      {step.rule_formula && (
                        <span className="step-formula-mini">
                          <MathView math={step.rule_formula} />
                        </span>
                      )}
                    </div>
                    <button type="button" className="step-toggle-btn">
                      {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </button>
                  </div>

                  {isOpen && (
                    <div className="step-card-body">
                      {step.expression && (
                        <div className="step-math-box">
                          <MathView math={step.expression} block />
                        </div>
                      )}
                      {stepDesc && (
                        <p className="step-description">
                          <RichMathText text={stepDesc} />
                        </p>
                      )}

                      {rationale && (
                        <div className="step-rationale-box">
                          <HelpCircle size={14} className="rationale-icon" />
                          <div className="rationale-text">
                            <strong>ហេតុអ្វី: </strong>
                            <span>
                              <RichMathText text={rationale} />
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
