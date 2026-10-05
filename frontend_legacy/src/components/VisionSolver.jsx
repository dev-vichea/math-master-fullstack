import React, { useState, useEffect } from 'react';
import { UploadCloud, Image as ImageIcon, Camera, Trash2, Zap, ClipboardCheck } from 'lucide-react';

const SAMPLES = [
  { label: 'អាំងតេក្រាល: ∫₂⁴ 4x dx', path: '/samples/integral_kha.png' },
  { label: 'ឌីផេរ៉ង់ស្យែល: y\' = 2x² - x + 1', path: '/samples/differential_ex1.png' },
  { label: 'ឌីផេរ៉ង់ស្យែលលំដាប់២: y\'\' - 3y\' + 2y = 0', path: '/samples/differential_ex7.png' },
  { label: 'ស្វ៊ីត Squeeze: lim (n²+sin n)/(5n²+cos πn)', path: '/samples/sequence_ex2.png' },
];

export default function VisionSolver({ onVisionSolve, loading, externalFile }) {
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
      onVisionSolve(file);
    } catch (err) {
      console.error('Failed to load sample image:', err);
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
    onVisionSolve(selectedFile);
  };

  return (
    <div className="vision-panel">
      <div className="vision-banner">
        <div className="vision-badge">
          <Camera size={16} />
          <span>ស្កេនរូបមន្តទោល (Single Formula Vision OCR)</span>
        </div>
        <p className="vision-desc">
          ស្កេនរូបភាពរូបមន្តគណិតវិទ្យាដែលបានបោះពុម្ព ឬសរសេរដៃ ដើម្បីស្រង់យកកូដ LaTeX និងដោះស្រាយដោយស្វ័យប្រវត្តិ។
        </p>
      </div>

      {pastedNotice && (
        <div className="pasted-banner">
          <ClipboardCheck size={18} />
          <span>បានបិទភ្ជាប់រូបភាពពី Clipboard រួចរាល់! (Screenshot pasted via ⌘V)</span>
        </div>
      )}

      {/* Dropzone */}
      <div
        className={`dropzone ${dragOver ? 'drag-over' : ''} ${previewUrl ? 'has-preview' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="vision-file-input"
          accept="image/*"
          className="file-input-hidden"
          onChange={(e) => handleFileChange(e.target.files[0])}
        />

        {previewUrl ? (
          <div className="image-preview-wrapper" onClick={(e) => e.stopPropagation()}>
            <img src={previewUrl} alt="Math upload preview" className="preview-image" />
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
          <label htmlFor="vision-file-input" className="dropzone-label">
            <UploadCloud size={48} className="upload-icon" />
            <span className="dropzone-primary-text">អូសទម្លាក់រូបភាពនៅទីនេះ ឬចុចដើម្បីជ្រើសរើស</span>
            <div className="dropzone-shortcut-badge">
              <span className="kbd-shortcut">⌘V</span> / <span className="kbd-shortcut">Ctrl+V</span>
              <span>បិទភ្ជាប់រូបភាព Screenshot ពី Clipboard</span>
            </div>
            <span className="dropzone-secondary-text">Supports PNG, JPG, WEBP (Single formula)</span>
          </label>
        )}
      </div>

      {/* Samples */}
      <div className="sample-bar">
        <span className="sample-title">រូបភាពគំរូ (Quick Test Samples):</span>
        <div className="sample-btn-group">
          {SAMPLES.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-btn"
              onClick={() => handleSampleClick(sample.path)}
            >
              <ImageIcon size={14} />
              <span>{sample.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <div className="vision-action-row">
        <button
          type="button"
          className="btn-solve-primary"
          disabled={!selectedFile || loading}
          onClick={handleSubmit}
        >
          {loading ? (
            <>
              <span className="btn-spinner"></span>
              <span>កំពុងស្កេន OCR & ដោះស្រាយ...</span>
            </>
          ) : (
            <>
              <Zap size={18} />
              <span>ស្កេន និង ដោះស្រាយ (Scan & Solve Formula)</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
