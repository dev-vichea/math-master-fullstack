import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Play, Layers, ClipboardCheck } from 'lucide-react';

const WORKSHEET_SAMPLES = [
  {
    label: 'គណនាអាំងតេក្រាល (Definite Integrals: ∫₀² 3x dx, ...)',
    path: '/samples/worksheet_integrals.png',
  },
  {
    label: 'លំហាត់អថេររួម (Shared Context: x = 2 - √3, y = 3 + √3)',
    path: '/samples/worksheet_shared_context.png',
  },
  {
    label: 'ដាក់ជាផលគុណកត្តា (Factorization Sheet)',
    path: '/samples/worksheet_factorization.jpg',
  },
];

export default function WorksheetSolver({ onWorksheetSolve, loading, externalFile }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [pastedNotice, setPastedNotice] = useState(false);

  const handleFileChange = (file) => {
    if (!file) return;
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  // Sync external file if passed from App paste listener
  useEffect(() => {
    if (externalFile) {
      handleFileChange(externalFile);
      setPastedNotice(true);
      const timer = setTimeout(() => setPastedNotice(false), 3500);
      return () => clearTimeout(timer);
    }
  }, [externalFile]);

  // Direct paste listener (Cmd+V or Ctrl+V)
  useEffect(() => {
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith('image/')) {
          e.preventDefault();
          const file = items[i].getAsFile();
          if (file) {
            handleFileChange(file);
            setPastedNotice(true);
            const timer = setTimeout(() => setPastedNotice(false), 3500);
            return () => clearTimeout(timer);
          }
          break;
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSampleClick = async (samplePath) => {
    try {
      const response = await fetch(samplePath);
      const blob = await response.blob();
      const file = new File([blob], samplePath.split('/').pop(), { type: blob.type || 'image/png' });
      handleFileChange(file);
      onWorksheetSolve(file);
    } catch (err) {
      console.error('Failed to load sample worksheet:', err);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setPastedNotice(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile || loading) return;
    onWorksheetSolve(selectedFile);
  };

  return (
    <div className="worksheet-panel">
      {/* Pipeline flow header */}
      <div className="pipeline-flow-card">
        <div className="pipeline-header">
          <div className="pipeline-badge">
            <Layers size={16} />
            <span>Full Worksheet End-to-End Pipeline</span>
          </div>
          <span className="no-crop-badge">✨ មិនបាច់កាត់រូបភាព (No crop required)</span>
        </div>
        <div className="pipeline-steps">
          <span className="step-node">Worksheet Image</span>
          <span className="step-arrow">→</span>
          <span className="step-node highlight-cyan">Kiri Khmer OCR</span>
          <span className="step-arrow">→</span>
          <span className="step-node">Exercise Structure</span>
          <span className="step-arrow">→</span>
          <span className="step-node highlight-emerald">Context Propagation</span>
          <span className="step-arrow">→</span>
          <span className="step-node highlight-indigo">SymPy Engine</span>
        </div>
      </div>

      {pastedNotice && (
        <div className="pasted-banner">
          <ClipboardCheck size={18} />
          <span>បានបិទភ្ជាប់រូបភាពសន្លឹកកិច្ចការពី Clipboard រួចរាល់! (Pasted via ⌘V)</span>
        </div>
      )}

      {/* Dropzone */}
      <div
        className={`dropzone worksheet-dropzone ${dragOver ? 'drag-over' : ''} ${
          previewUrl ? 'has-preview' : ''
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="worksheet-file-input"
          accept="image/*"
          className="file-input-hidden"
          onChange={(e) => handleFileChange(e.target.files[0])}
        />

        {previewUrl ? (
          <div className="image-preview-wrapper worksheet-preview-wrapper" onClick={(e) => e.stopPropagation()}>
            <img src={previewUrl} alt="Worksheet preview" className="preview-image" />
            <button
              type="button"
              className="btn-remove-preview"
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
              title="Remove image"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ) : (
          <label htmlFor="worksheet-file-input" className="dropzone-label">
            <FileText size={48} className="upload-icon text-cyan" />
            <span className="dropzone-primary-text">អូសទម្លាក់សន្លឹកកិច្ចការពេញលេញនៅទីនេះ</span>
            <div className="dropzone-shortcut-badge">
              <span className="kbd-shortcut">⌘V</span> / <span className="kbd-shortcut">Ctrl+V</span>
              <span>បិទភ្ជាប់រូបភាព Screenshot ពី Clipboard</span>
            </div>
            <span className="dropzone-secondary-text">
              Recognizes Khmer titles, exercise sections, and variables across entire pages
            </span>
          </label>
        )}
      </div>

      {/* Sample Worksheets */}
      <div className="sample-bar">
        <span className="sample-title">សន្លឹកកិច្ចការគំរូពិតប្រាកដ (Real Worksheets):</span>
        <div className="sample-btn-group vertical">
          {WORKSHEET_SAMPLES.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-btn-ws"
              onClick={() => handleSampleClick(sample.path)}
            >
              <FileText size={16} />
              <span>{sample.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <div className="worksheet-action-row">
        <button
          type="button"
          className="btn-solve-primary btn-worksheet"
          disabled={!selectedFile || loading}
          onClick={handleSubmit}
        >
          {loading ? (
            <>
              <span className="btn-spinner"></span>
              <span>កំពុងវិភាគសន្លឹកកិច្ចការទាំងមូល...</span>
            </>
          ) : (
            <>
              <Play size={18} />
              <span>វិភាគសន្លឹកកិច្ចការ (Analyze & Solve Worksheet)</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
