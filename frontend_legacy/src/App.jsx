import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ManualSolver from './components/ManualSolver';
import VisionSolver from './components/VisionSolver';
import WorksheetSolver from './components/WorksheetSolver';
import SolutionView from './components/SolutionView';
import WorksheetResultView from './components/WorksheetResultView';
import BilingualGlossaryModal from './components/BilingualGlossaryModal';
import { solveMath, solveVision, processWorksheet } from './services/api';
import {
  PenTool,
  Camera,
  FileSpreadsheet,
  AlertCircle,
  Lightbulb,
  Cpu,
  BookOpen,
} from 'lucide-react';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('manual'); // 'manual' | 'vision' | 'worksheet'
  const [lang, setLang] = useState('km');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('mathlab-theme') || 'light';
  });
  const [solution, setSolution] = useState(null);
  const [worksheetData, setWorksheetData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pastedVisionFile, setPastedVisionFile] = useState(null);
  const [pastedWorksheetFile, setPastedWorksheetFile] = useState(null);
  const [isGlossaryOpen, setIsGlossaryOpen] = useState(false);
  const [glossaryPrompt, setGlossaryPrompt] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('mathlab-theme', theme);
  }, [theme]);

  // Global clipboard screenshot paste handler (Cmd+V / Ctrl+V)
  useEffect(() => {
    const handleGlobalPaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith('image/')) {
          e.preventDefault();
          const file = items[i].getAsFile();
          if (file) {
            if (activeTab === 'worksheet') {
              setPastedWorksheetFile(file);
            } else {
              setActiveTab('vision');
              setPastedVisionFile(file);
            }
          }
          break;
        }
      }
    };

    window.addEventListener('paste', handleGlobalPaste);
    return () => window.removeEventListener('paste', handleGlobalPaste);
  }, [activeTab]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const handleManualSolve = async (question) => {
    setLoading(true);
    setError(null);
    setWorksheetData(null);
    try {
      const data = await solveMath(question, lang);
      setSolution(data);
    } catch (err) {
      setError(err.message || 'បរាជ័យក្នុងការដោះស្រាយ។ សូមពិនិត្យទម្រង់សំណួរឡើងវិញ។');
      setSolution(null);
    } finally {
      setLoading(false);
    }
  };

  const handleVisionSolve = async (file) => {
    setLoading(true);
    setError(null);
    setWorksheetData(null);
    try {
      const data = await solveVision(file);
      setSolution(data);
    } catch (err) {
      setError(err.message || 'មិនអាចស្កេនរូបភាពរូបមន្តបានទេ។ សូមសាកល្បងម្ដងទៀត។');
      setSolution(null);
    } finally {
      setLoading(false);
    }
  };

  const handleWorksheetSolve = async (file) => {
    setLoading(true);
    setError(null);
    setSolution(null);
    try {
      const data = await processWorksheet(file);
      setWorksheetData(data);
    } catch (err) {
      setError(err.message || 'មិនអាចវិភាគសន្លឹកកិច្ចការបានទេ។');
      setWorksheetData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <Header
        lang={lang}
        setLang={setLang}
        theme={theme}
        toggleTheme={toggleTheme}
        onOpenGlossary={() => setIsGlossaryOpen(true)}
      />

      <main className="main-content">
        <div className="content-grid">
          {/* Left Column: Input Panels */}
          <section className="card card-input">
            {/* Tabs */}
            <div className="tabs-header">
              <button
                type="button"
                className={`tab-btn ${activeTab === 'manual' ? 'active' : ''}`}
                onClick={() => setActiveTab('manual')}
              >
                <PenTool size={16} />
                <span>សរសេរលំហាត់ (Manual / MathLive)</span>
              </button>
              <button
                type="button"
                className={`tab-btn ${activeTab === 'vision' ? 'active' : ''}`}
                onClick={() => setActiveTab('vision')}
              >
                <Camera size={16} />
                <span>រូបមន្តទោល (Vision OCR)</span>
              </button>
              <button
                type="button"
                className={`tab-btn ${activeTab === 'worksheet' ? 'active' : ''}`}
                onClick={() => setActiveTab('worksheet')}
              >
                <FileSpreadsheet size={16} />
                <span>សន្លឹកកិច្ចការ (Full Worksheet)</span>
              </button>
            </div>

            <div className="tab-body">
              {activeTab === 'manual' && (
                <ManualSolver
                  onSolve={handleManualSolve}
                  loading={loading}
                  externalQuestion={glossaryPrompt}
                />
              )}
              {activeTab === 'vision' && (
                <VisionSolver
                  onVisionSolve={handleVisionSolve}
                  loading={loading}
                  externalFile={pastedVisionFile}
                />
              )}
              {activeTab === 'worksheet' && (
                <WorksheetSolver
                  onWorksheetSolve={handleWorksheetSolve}
                  loading={loading}
                  externalFile={pastedWorksheetFile}
                />
              )}
            </div>
          </section>

          {/* Right Column: Results */}
          <section className="card card-output">
            {/* Loading State */}
            {loading && (
              <div className="state-box state-loading">
                <div className="spinner"></div>
                <h3 className="state-title">កំពុងដំណើរការគណនា និងផ្ទៀងផ្ទាត់...</h3>
                <p className="state-subtitle">
                  Solving symbolically with SymPy & generating pedagogical steps
                </p>
              </div>
            )}

            {/* Error State */}
            {!loading && error && (
              <div className="state-box state-error">
                <div className="error-icon-box">
                  <AlertCircle size={36} />
                </div>
                <h3 className="error-title">មិនអាចដោះស្រាយបានទេ (Solving Error)</h3>
                <p className="error-desc">{error}</p>
                <button
                  type="button"
                  className="btn-retry"
                  onClick={() => {
                    setError(null);
                    setActiveTab('manual');
                  }}
                >
                  សាកល្បងម្ដងទៀត (Try Again)
                </button>
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && !solution && !worksheetData && (
              <div className="state-box state-empty">
                <div className="empty-icon-box">
                  <Lightbulb size={40} />
                </div>
                <h3 className="empty-title">លទ្ធផលដំណោះស្រាយនឹងបង្ហាញនៅទីនេះ</h3>
                <p className="empty-desc">
                  ជ្រើសរើសលំហាត់គំរូ ឬវាយបញ្ចូលលំហាត់គណិតវិទ្យាថ្នាក់ទី១២
                  (លីមីត, ស្វ៊ីត, ដេរីវេ, អាំងតេក្រាល, លោការីត...) ដើម្បីទទួលបានដំណោះស្រាយជាជំហានៗ។
                </p>
                <div className="empty-hints">
                  <span className="hint-pill">✨ SymPy Verified</span>
                  <span className="hint-pill">🇰🇭 Khmer Pedagogical Steps</span>
                  <span className="hint-pill">📖 BacII Standard</span>
                </div>
              </div>
            )}

            {/* Solution State */}
            {!loading && !error && solution && (
              <SolutionView solution={solution} lang={lang} />
            )}

            {/* Worksheet Result State */}
            {!loading && !error && worksheetData && (
              <WorksheetResultView data={worksheetData} lang={lang} />
            )}
          </section>
        </div>
      </main>

      {/* Bilingual Math Glossary Modal */}
      <BilingualGlossaryModal
        isOpen={isGlossaryOpen}
        onClose={() => setIsGlossaryOpen(false)}
        onSelectExample={(prompt) => {
          setActiveTab('manual');
          setGlossaryPrompt(prompt);
        }}
      />

      {/* Footer */}
      <footer className="footer">
        <p>
          Khmer Math Lab — កម្មវិធីជំនួយដោះស្រាយគណិតវិទ្យាថ្នាក់ទី១២ ស្របតាមកម្មវិធីសិក្សាជាតិ
        </p>
      </footer>
    </div>
  );
}
