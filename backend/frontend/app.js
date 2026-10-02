// -------------------------------------------------------------
// Khmer Math Lab — Client Application Logic (KaTeX & LaTeX First)
// -------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // Elements: Tabs
  const tabTypingBtn = document.getElementById('tab-typing-btn');
  const tabVisionBtn = document.getElementById('tab-vision-btn');
  const tabWorksheetBtn = document.getElementById('tab-worksheet-btn');
  const tabTyping = document.getElementById('tab-typing');
  const tabVision = document.getElementById('tab-vision');
  const tabWorksheet = document.getElementById('tab-worksheet');
  const btnGotoWorksheet = document.getElementById('btn-goto-worksheet');

  // Solution View Containers (Single Formula vs Full Worksheet)
  const singleSolutionView = document.getElementById('single-solution-view');
  const worksheetSolutionView = document.getElementById('worksheet-solution-view');

  // Elements: Worksheet Pipeline Dropzone & Controls
  const worksheetDropzone = document.getElementById('worksheet-dropzone');
  const worksheetFileInput = document.getElementById('worksheet-file-input');
  const worksheetDropzoneEmpty = document.getElementById('worksheet-dropzone-empty');
  const worksheetDropzonePreview = document.getElementById('worksheet-dropzone-preview');
  const worksheetPreviewImage = document.getElementById('worksheet-preview-image');
  const worksheetRemoveBtn = document.getElementById('worksheet-remove-btn');
  const worksheetAnalyzeBtn = document.getElementById('worksheet-analyze-btn');
  const worksheetSampleButtons = document.querySelectorAll('[data-worksheet-sample]');

  // Elements: Worksheet Solution View
  const wsBadgeStatus = document.getElementById('ws-badge-status');
  const wsBadgeTotal = document.getElementById('ws-badge-total');
  const wsBadgeSolved = document.getElementById('ws-badge-solved');
  const wsBadgeConf = document.getElementById('ws-badge-conf');
  const wsInstructionCard = document.getElementById('ws-instruction-card');
  const wsInstructionText = document.getElementById('ws-instruction-text');
  const wsInstructionType = document.getElementById('ws-instruction-type');
  const wsContextCard = document.getElementById('ws-context-card');
  const wsContextVariables = document.getElementById('ws-context-variables');
  const wsProblemsCount = document.getElementById('ws-problems-count');
  const wsProblemsContainer = document.getElementById('ws-problems-container');
  const wsRawOcrText = document.getElementById('ws-raw-ocr-text');

  // State: Worksheet Image File
  let worksheetImageFile = null;

  // Elements: Typing Tab & Live Math Preview
  const questionInput = document.getElementById('question-input');
  const charCounter = document.getElementById('char-counter');
  const solveBtn = document.getElementById('solve-btn');
  const liveMathPreviewCard = document.getElementById('live-math-preview-card');
  const liveMathPreviewContent = document.getElementById('live-math-preview-content');

  // Elements: Vision Dropzone & Cropping
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const dropzoneEmpty = document.getElementById('dropzone-empty');
  const dropzonePreview = document.getElementById('dropzone-preview');
  const previewImage = document.getElementById('preview-image');
  const cropCanvas = document.getElementById('crop-canvas');
  const btnCropFormula = document.getElementById('btn-crop-formula');
  const btnResetCrop = document.getElementById('btn-reset-crop');
  const removeImageBtn = document.getElementById('remove-image-btn');
  const visionSolveBtn = document.getElementById('vision-solve-btn');

  // Elements: OCR LaTeX Card & Inline Editor
  const ocrLatexCard = document.getElementById('ocr-latex-card');
  const ocrLatexInput = document.getElementById('ocr-latex-input');
  const btnCopyLatex = document.getElementById('btn-copy-latex');
  const btnSolveEditedLatex = document.getElementById('btn-solve-edited-latex');

  // Elements: Solution Section
  const solutionEmpty = document.getElementById('solution-empty');
  const solutionLoading = document.getElementById('solution-loading');
  const solutionError = document.getElementById('solution-error');
  const errorMessage = document.getElementById('error-message');
  const errorActions = document.getElementById('error-actions');
  const btnErrorSwitchManual = document.getElementById('btn-error-switch-manual');
  const solutionContent = document.getElementById('solution-content');

  let pendingFallbackMath = '\\lim_{x \\to 0} \\frac{\\sin^2 x}{1 - \\cos^4 x}';

  const badgeProblemType = document.getElementById('badge-problem-type');
  const badgeVerified = document.getElementById('badge-verified');
  const heroVar = document.getElementById('hero-var');
  const heroAnswer = document.getElementById('hero-answer');
  const stepsList = document.getElementById('steps-list');

  // Lesson Curriculum Banner elements
  const lessonCurriculumBanner = document.getElementById('lesson-curriculum-banner');
  const lessonChapterBadge = document.getElementById('lesson-chapter-badge');
  const lessonNameBadge = document.getElementById('lesson-name-badge');
  const lessonMethodBadge = document.getElementById('lesson-method-badge');
  const lessonFormulaPill = document.getElementById('lesson-formula-pill');
  const lessonFormulaContent = document.getElementById('lesson-formula-content');

  // OCR Info Banner elements
  const ocrInfoBanner = document.getElementById('ocr-info-banner');
  const ocrDetectedText = document.getElementById('ocr-detected-text');
  const ocrExerciseHeaderRow = document.getElementById('ocr-exercise-header-row');
  const ocrExerciseBadge = document.getElementById('ocr-exercise-badge');
  const ocrInstructionBadge = document.getElementById('ocr-instruction-badge');
  const ocrCleanedRow = document.getElementById('ocr-cleaned-row');
  const ocrCleanedText = document.getElementById('ocr-cleaned-text');
  const ocrConfFill = document.getElementById('ocr-conf-fill');
  const ocrConfVal = document.getElementById('ocr-conf-val');

  // History elements
  const historyToggleBtn = document.getElementById('history-toggle-btn');
  const historyDrawer = document.getElementById('history-drawer');
  const closeHistoryBtn = document.getElementById('close-history-btn');
  const historyList = document.getElementById('history-list');
  const historyEmpty = document.getElementById('history-empty');
  const historyCount = document.getElementById('history-count');
  const clearHistoryBtn = document.getElementById('clear-history-btn');
  const apiStatus = document.getElementById('api-status');

  // State: Images & Crop
  let originalImageFile = null;
  let originalDataUrl = null;
  let currentImageFile = null;
  let cropRect = null; // { x, y, w, h }
  let isDraggingCrop = false;
  let cropStartX = 0;
  let cropStartY = 0;

  // ---------------- KaTeX Formatting & Rendering Helpers ----------------
  function formatMathForKaTeX(raw) {
    if (raw === undefined || raw === null) return '';
    let s = String(raw).trim();
    if (!s) return '';

    // Strip enclosing math delimiters if present
    if (s.startsWith('$$') && s.endsWith('$$')) {
      s = s.slice(2, -2).trim();
    } else if (s.startsWith('$') && s.endsWith('$')) {
      s = s.slice(1, -1).trim();
    }

    // 1. Simplify SymPy interval representations
    // (-oo < x) & (x < 5) -> x < 5
    s = s.replace(/\(-oo\s*<\s*([a-zA-Z])\)\s*&\s*\(\1\s*<\s*([^)]+)\)/g, '$1 < $2');
    // (a < x) & (x < oo) -> a < x
    s = s.replace(/\(([^)]+)\s*<\s*([a-zA-Z])\)\s*&\s*\(\2\s*<\s*oo\)/g, '$1 < $2');
    // (a < x) & (x < b) -> a < x < b
    s = s.replace(/\(([^)]+)\s*<\s*([a-zA-Z])\)\s*&\s*\(\2\s*<\s*([^)]+)\)/g, '$1 < $2 < $3');

    // Replace infinity and logical operators
    s = s.replace(/-oo\b/g, '-\\infty');
    s = s.replace(/\boo\b/g, '\\infty');
    s = s.replace(/\s*&\s*/g, ' \\text{ and } ');
    s = s.replace(/\s*\|\s*/g, ' \\text{ or } ');

    // 2. Simple numeric fractions like -1/4 or 5/4
    s = s.replace(/^-(\d+)\/(\d+)$/, '-\\frac{$1}{$2}');
    s = s.replace(/^(\d+)\/(\d+)$/, '\\frac{$1}{$2}');

    // 3. Powers: replace ** with ^{...}
    let prev;
    let iterations = 0;
    while (s.includes('**') && iterations < 10) {
      iterations++;
      prev = s;
      s = s.replace(/(\((?:[^()]+|\([^()]*\))*\)|[a-zA-Z0-9_\\]+|\{[^{}]+\})\s*\*\*\s*(\((?:[^()]+|\([^()]*\))*\)|-?[a-zA-Z0-9_\\]+|\{[^{}]+\})/g, (match, base, exp) => {
        let cleanExp = exp;
        if (cleanExp.startsWith('(') && cleanExp.endsWith(')')) {
          cleanExp = cleanExp.slice(1, -1).trim();
        }
        return `${base}^{${cleanExp}}`;
      });
      if (s === prev) break;
    }

    // 4. Square roots: sqrt(...) -> \sqrt{...}
    while (/\\?sqrt\(([^()]+)\)/.test(s)) {
      s = s.replace(/\\?sqrt\(([^()]+)\)/g, '\\sqrt{$1}');
    }

    // 5. Clean up redundant coefficients like -1*4*k or 1*4*k
    s = s.replace(/(^|[^a-zA-Z0-9_])1\s*\*\s*([a-zA-Z0-9_\\(])/g, '$1$2');

    // 6. Multiplication cleanup (replacing * with implicit or LaTeX multiplication)
    // Parentheses product: (...) * (...) -> (...)(...)
    s = s.replace(/\)\s*\*\s*\(/g, ')(');

    // Number * variable: 15*k -> 15k, 4*x -> 4x
    s = s.replace(/(\d+)\s*\*\s*([a-zA-Z])/g, '$1$2');

    // Number * paren: 4*(...) -> 4(...)
    s = s.replace(/(\d+)\s*\*\s*\(/g, '$1(');

    // Paren * var/number: (...)*x -> (...)x
    s = s.replace(/\)\s*\*\s*([a-zA-Z\d])/g, ')$1');

    // Var * paren: x*(...) -> x(...)
    s = s.replace(/([a-zA-Z])\s*\*\s*\(/g, '$1(');

    // Var * var: x*y -> xy
    s = s.replace(/([a-zA-Z])\s*\*\s*([a-zA-Z])/g, '$1$2');

    // Number * sqrt: 3*\sqrt{2} -> 3\sqrt{2}
    s = s.replace(/(\d+)\s*\*\s*(\\sqrt)/g, '$1$2');

    // Number * number: 4*5 -> 4 \cdot 5
    s = s.replace(/(\d+)\s*\*\s*(\d+)/g, '$1 \\cdot $2');

    // Any remaining standalone * -> \cdot
    s = s.replace(/\s*\*\s*/g, ' \\cdot ');

    // 7. Relational operators
    s = s.replace(/<=/g, ' \\le ');
    s = s.replace(/>=/g, ' \\ge ');
    s = s.replace(/!=/g, ' \\ne ');

    // 8. Comma-separated lists of roots: e.g. 2, 3 -> 2, \; 3
    s = s.replace(/,\s*/g, ', \\; ');

    // 9. Arrow operators
    s = s.replace(/\s*->\s*/g, ' \\rightarrow ');
    s = s.replace(/\s*→\s*/g, ' \\rightarrow ');

    return s;
  }

  function renderKaTeX(element, latexStr, displayMode = false) {
    if (!element || latexStr === undefined || latexStr === null) return;
    const clean = formatMathForKaTeX(latexStr);
    if (!clean) {
      element.innerHTML = '';
      return;
    }

    if (window.katex) {
      try {
        window.katex.render(clean, element, {
          throwOnError: false,
          displayMode: displayMode,
          trust: true,
        });
        return;
      } catch (e) {
        console.warn('KaTeX rendering error:', e);
      }
    }
    element.textContent = clean;
  }

  function renderMathIn(container) {
    if (!container || !window.renderMathInElement) return;
    try {
      window.renderMathInElement(container, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true },
        ],
        throwOnError: false,
      });
    } catch (e) {
      console.warn('renderMathInElement error:', e);
    }
  }

  // ---------------- Health Check ----------------
  async function checkHealth() {
    try {
      const res = await fetch('/api/v1/health');
      if (res.ok) {
        apiStatus.innerHTML = `
          <span class="status-dot"></span>
          <span class="status-text">API Live (v0.1.0)</span>
        `;
      }
    } catch {
      apiStatus.innerHTML = `
        <span class="status-dot" style="background:#f43f5e;box-shadow:0 0 8px #f43f5e"></span>
        <span class="status-text" style="color:#fda4af">API Offline</span>
      `;
    }
  }
  checkHealth();

  // ---------------- Tab Switching ----------------
  function switchTab(activeTab) {
    [tabTypingBtn, tabVisionBtn, tabWorksheetBtn].forEach((btn) => {
      if (btn) btn.classList.remove('active');
    });
    [tabTyping, tabVision, tabWorksheet].forEach((tab) => {
      if (tab) tab.classList.remove('active');
    });

    if (activeTab === 'typing') {
      if (tabTypingBtn) tabTypingBtn.classList.add('active');
      if (tabTyping) tabTyping.classList.add('active');
    } else if (activeTab === 'vision') {
      if (tabVisionBtn) tabVisionBtn.classList.add('active');
      if (tabVision) tabVision.classList.add('active');
      setTimeout(syncCropCanvas, 150);
    } else if (activeTab === 'worksheet') {
      if (tabWorksheetBtn) tabWorksheetBtn.classList.add('active');
      if (tabWorksheet) tabWorksheet.classList.add('active');
    }
  }

  if (tabTypingBtn) tabTypingBtn.addEventListener('click', () => switchTab('typing'));
  if (tabVisionBtn) tabVisionBtn.addEventListener('click', () => switchTab('vision'));
  if (tabWorksheetBtn) tabWorksheetBtn.addEventListener('click', () => switchTab('worksheet'));
  if (btnGotoWorksheet) btnGotoWorksheet.addEventListener('click', () => switchTab('worksheet'));

  // ---------------- Live Math Preview & Typing ----------------
  function updateLivePreview() {
    charCounter.textContent = questionInput.value.length;
    const raw = questionInput.value.trim();
    if (!raw) {
      if (liveMathPreviewCard) liveMathPreviewCard.classList.add('hidden');
      return;
    }

    // Detect if input has LaTeX or mathematical symbols
    const hasMath = /[\\^_{}]|lim|frac|sqrt|sin|cos|tan|\d+\s*[\+\-\*\/=]|\d+[a-zA-Z]/i.test(raw);
    if (!hasMath) {
      if (liveMathPreviewCard) liveMathPreviewCard.classList.add('hidden');
      return;
    }

    // Clean instructions and sub-problem labels for KaTeX math preview
    let formula = raw;
    formula = formula.replace(/^(?:លំហាត់ទី|លំហាត់|សំណួរទី|សំណួរ|វិញ្ញាសាទី|វិញ្ញាសា|ឧទាហរណ៍ទី|ឧទាហរណ៍|Exercise|Problem|Task|Question|Example|Ex|Q)\s*[:.-]?\s*[0-9\u17e0-\u17e9]*[:.-]?\s*/i, '');
    formula = formula.replace(/^(?:(?:ចូរ)?(?:គណនា|រក|ដោះស្រាយ)(?:នូវ)?(?:តម្លៃ)?(?:នៃ)?លីមីត(?:នៃអនុគមន៍)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?|ដោះស្រាយសមីការ(?:ខាងក្រោម)?|ចូរដោះស្រាយសមីការ|ចូរដោះស្រាយ|ដោះស្រាយ|រកតម្លៃនៃ\s*[a-zA-Z]?|រកតម្លៃ\s*[a-zA-Z]?|រក\s*[a-zA-Z]?|ចូររកតម្លៃ|គណនាតម្លៃនៃ\s*[a-zA-Z]?|គណនាតម្លៃ|គណនាកន្សោម(?:ខាងក្រោម)?|គណនាប្រភាគ|គណនា|ចូរគណនា|ធ្វើឲ្យសាមញ្ញ(?:នូវកន្សោម)?(?:ខាងក្រោម)?|ចូរធ្វើឲ្យសាមញ្ញ|បង្រួមកន្សោម(?:ខាងក្រោម)?|Find\s+(?:the\s+)?value\s+of\s+[a-zA-Z]?|Solve\s+for\s+[a-zA-Z]?|Solve\s+the\s+equation|Find\s+[a-zA-Z]|(?:Find|Calculate|Evaluate|Compute|Solve)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?limits?(?:\s+of)?(?:\s+the\s+following)?|Calculate|Evaluate|Simplify|Compute)[:៖\s]*/i, '');
    // Clean sub-item label like 'ខ.', 'ក.', '1.', '2.', 'a.', '(a)', '(1)', '\mathcal{Q}.'
    formula = formula.replace(/^(?:\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?|(?:\\(?:mathcal|mathbf|mathrm|text)\{[a-zA-Z0-9\u1780-\u17a2]+\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d))\s*/i, '');

    // Format ASCII limits and sqrt for smooth KaTeX display
    formula = formula.replace(/(?:\\)?sqrt\(([^)]+)\)/gi, '\\sqrt{$1}');
    formula = formula.replace(/(?:\\\\|\\|\/)*lim(?:it)?\s*(?:_\{?|\s+)\s*([a-zA-Z])\s*(?:->|\\\\rightarrow|\\rightarrow|\\\\to|\\to|\bto\b)\s*([0-9+\-a-zA-Z]+|\\[a-zA-Z]+)\}?/gi, '\\lim_{$1 \\to $2} ');

    formula = formula.trim();
    if (!formula) {
      if (liveMathPreviewCard) liveMathPreviewCard.classList.add('hidden');
      return;
    }

    if (liveMathPreviewCard && liveMathPreviewContent) {
      liveMathPreviewCard.classList.remove('hidden');
      renderKaTeX(liveMathPreviewContent, formula, true);
    }
  }

  questionInput.addEventListener('input', updateLivePreview);

  // Shortcut Chips Insertion
  document.querySelectorAll('.btn-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const insertText = chip.getAttribute('data-insert');
      if (!insertText) return;
      insertAtCursor(questionInput, insertText);
      updateLivePreview();
      questionInput.focus();
    });
  });

  function insertAtCursor(input, textToInsert) {
    const start = input.selectionStart || 0;
    const end = input.selectionEnd || 0;
    const text = input.value;
    input.value = text.substring(0, start) + textToInsert + text.substring(end);
    input.selectionStart = input.selectionEnd = start + textToInsert.length;
  }

  // Example Presets
  document.querySelectorAll('.preset-pill').forEach((pill) => {
    pill.addEventListener('click', () => {
      const exampleText = pill.getAttribute('data-example');
      questionInput.value = exampleText;
      updateLivePreview();
      solveManualMath();
    });
  });

  // ---------------- Solve Manual Math ----------------
  solveBtn.addEventListener('click', solveManualMath);
  questionInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      solveManualMath();
    }
  });

  async function solveManualMath() {
    const question = questionInput.value.trim();
    if (!question) {
      showError('សូមបញ្ចូលលំហាត់គណិតវិទ្យា (Please enter a math expression).');
      return;
    }

    showLoading();

    try {
      const response = await fetch('/api/v1/math/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'km', question: question }),
      });

      const result = await response.json();

      if (result.success && result.data) {
        renderSolution(result.data, false);
        loadHistory();
      } else {
        showError(result.error || 'មិនអាចដោះស្រាយលំហាត់នេះបានទេ');
      }
    } catch (err) {
      showError('កំហុសក្នុងការតភ្ជាប់ទៅកាន់ Server: ' + err.message);
    }
  }

  // ---------------- File Dropzone & Image Handling ----------------
  dropzone.addEventListener('click', (e) => {
    if (e.target !== removeImageBtn && e.target !== btnCropFormula && e.target !== btnResetCrop) {
      fileInput.click();
    }
  });

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      handleImageSelected(fileInput.files[0]);
    }
  });

  function handleImageSelected(file) {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (PNG, JPG, WebP)');
      return;
    }

    originalImageFile = file;
    currentImageFile = file;
    cropRect = null;
    if (btnResetCrop) btnResetCrop.classList.add('hidden');
    if (ocrLatexCard) ocrLatexCard.classList.add('hidden');

    const reader = new FileReader();
    reader.onload = (e) => {
      originalDataUrl = e.target.result;
      previewImage.src = originalDataUrl;
      dropzoneEmpty.classList.add('hidden');
      dropzonePreview.classList.remove('hidden');
      visionSolveBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  previewImage.addEventListener('load', () => {
    syncCropCanvas();
  });

  window.addEventListener('resize', () => {
    syncCropCanvas();
  });

  function syncCropCanvas() {
    if (!previewImage.complete || !previewImage.naturalWidth || !cropCanvas) return;
    cropCanvas.width = previewImage.clientWidth;
    cropCanvas.height = previewImage.clientHeight;
    drawCropOverlay();
  }

  // Crop Drag Events
  if (cropCanvas) {
    cropCanvas.addEventListener('mousedown', (e) => {
      const rect = cropCanvas.getBoundingClientRect();
      cropStartX = e.clientX - rect.left;
      cropStartY = e.clientY - rect.top;
      isDraggingCrop = true;
      cropRect = null;
    });

    cropCanvas.addEventListener('mousemove', (e) => {
      if (!isDraggingCrop) return;
      const rect = cropCanvas.getBoundingClientRect();
      const currX = e.clientX - rect.left;
      const currY = e.clientY - rect.top;
      const x = Math.min(cropStartX, currX);
      const y = Math.min(cropStartY, currY);
      const w = Math.abs(currX - cropStartX);
      const h = Math.abs(currY - cropStartY);
      cropRect = { x, y, w, h };
      drawCropOverlay();
    });

    window.addEventListener('mouseup', () => {
      if (isDraggingCrop) {
        isDraggingCrop = false;
        if (cropRect && (cropRect.w < 15 || cropRect.h < 15)) {
          cropRect = null;
          drawCropOverlay();
        }
      }
    });
  }

  function drawCropOverlay() {
    if (!cropCanvas) return;
    const ctx = cropCanvas.getContext('2d');
    ctx.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
    if (!cropRect || cropRect.w === 0 || cropRect.h === 0) return;

    // Dim mask over image
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(0, 0, cropCanvas.width, cropCanvas.height);

    // Clear selected rectangle
    ctx.clearRect(cropRect.x, cropRect.y, cropRect.w, cropRect.h);

    // Cyan glowing border
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 2]);
    ctx.strokeRect(cropRect.x, cropRect.y, cropRect.w, cropRect.h);

    // Handles
    ctx.setLineDash([]);
    ctx.fillStyle = '#38bdf8';
    const hSize = 6;
    const corners = [
      [cropRect.x, cropRect.y],
      [cropRect.x + cropRect.w, cropRect.y],
      [cropRect.x, cropRect.y + cropRect.h],
      [cropRect.x + cropRect.w, cropRect.y + cropRect.h],
    ];
    corners.forEach(([cx, cy]) => {
      ctx.fillRect(cx - hSize / 2, cy - hSize / 2, hSize, hSize);
    });
  }

  // Crop Button
  if (btnCropFormula) {
    btnCropFormula.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!cropRect || cropRect.w < 15 || cropRect.h < 15) {
        alert('សូមគូសប្រអប់ជុំវិញរូបមន្តដែលអ្នកចង់កាត់ជាមុនសិន (Drag a box on the image to crop first).');
        return;
      }

      const scaleX = previewImage.naturalWidth / previewImage.clientWidth;
      const scaleY = previewImage.naturalHeight / previewImage.clientHeight;

      const sx = Math.round(cropRect.x * scaleX);
      const sy = Math.round(cropRect.y * scaleY);
      const sw = Math.round(cropRect.w * scaleX);
      const sh = Math.round(cropRect.h * scaleY);

      const offscreen = document.createElement('canvas');
      offscreen.width = sw;
      offscreen.height = sh;
      const ctx = offscreen.getContext('2d');
      ctx.drawImage(previewImage, sx, sy, sw, sh, 0, 0, sw, sh);

      offscreen.toBlob((blob) => {
        if (!blob) return;
        currentImageFile = new File([blob], 'cropped_formula.png', { type: 'image/png' });
        previewImage.src = URL.createObjectURL(blob);
        if (btnResetCrop) btnResetCrop.classList.remove('hidden');
        cropRect = null;
        const cctx = cropCanvas.getContext('2d');
        cctx.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
      }, 'image/png');
    });
  }

  // Reset Crop Button
  if (btnResetCrop) {
    btnResetCrop.addEventListener('click', (e) => {
      e.stopPropagation();
      if (originalDataUrl && originalImageFile) {
        currentImageFile = originalImageFile;
        previewImage.src = originalDataUrl;
        btnResetCrop.classList.add('hidden');
        cropRect = null;
        setTimeout(syncCropCanvas, 100);
      }
    });
  }

  // Remove Image Button
  removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    originalImageFile = null;
    currentImageFile = null;
    originalDataUrl = null;
    cropRect = null;
    fileInput.value = '';
    previewImage.src = '';
    dropzoneEmpty.classList.remove('hidden');
    dropzonePreview.classList.add('hidden');
    visionSolveBtn.disabled = true;
    if (btnResetCrop) btnResetCrop.classList.add('hidden');
    if (ocrLatexCard) ocrLatexCard.classList.add('hidden');
  });

  // Sample Image Shortcuts
  document.querySelectorAll('.btn-sample').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const samplePath = btn.getAttribute('data-sample');
      try {
        const res = await fetch(samplePath);
        const blob = await res.blob();
        const file = new File([blob], 'sample.png', { type: blob.type || 'image/png' });
        handleImageSelected(file);
      } catch (err) {
        console.error('Failed to load sample image:', err);
      }
    });
  });

  // ---------------- Solve Image Vision ----------------
  visionSolveBtn.addEventListener('click', solveVisionMath);

  async function solveVisionMath() {
    if (!currentImageFile) return;

    showLoading();

    const formData = new FormData();
    formData.append('image', currentImageFile);

    try {
      const response = await fetch('/api/v1/math/vision', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success && result.data) {
        renderSolution(result.data, true);
        loadHistory();
      } else {
        let errorMsg = result.error || 'No mathematical text recognized in image.';
        let isStub = errorMsg.includes('stub') || errorMsg.includes('not implemented yet');
        if (isStub) {
          errorMsg = `⚠️ ប្រព័ន្ធ OCR (Math Vision) កំពុងស្ថិតក្នុងដំណាក់កាលទាញយកកញ្ចប់ម៉ូឌែលនៅក្នុង Background។\n\n💡 ប៉ុន្តែប្រព័ន្ធគណិតវិទ្យា (Math Engine) អាចដោះស្រាយលំហាត់នេះបានភ្លាមៗ!`;
          pendingFallbackMath = (result.data && result.data.ocr_detected_text) ? result.data.ocr_detected_text : '4/3 + 2/4';
          showError(errorMsg, true);
        } else {
          // Extract detected text if available from API response
          const detectedMatch = errorMsg.match(/OCR detected '([^']+)'/);
          const extractedLatex = result.data?.ocr_detected_text || (detectedMatch ? detectedMatch[1] : '');

          if (extractedLatex) {
            pendingFallbackMath = extractedLatex;
            if (ocrLatexCard && ocrLatexInput) {
              ocrLatexCard.classList.remove('hidden');
              ocrLatexInput.value = extractedLatex;
            }
            errorMsg = `⚠️ មិនអាចបម្លែង ឬគណនារូបមន្តដោយស្វ័យប្រវត្តបានទេ\n\n` +
                       `🔍 អត្ថបទ LaTeX ស្រង់បាន៖ ${extractedLatex}\n\n` +
                       `💡 សម្គាល់៖ ម៉ូឌែល Pix2Tex ត្រូវបានបង្វឹកលើរូបមន្តពុម្ពកុំព្យូទ័រ (Printed LaTeX) ដូច្នេះអក្សរសរសេរដោយដៃ (Handwritten Math) អាចបង្កឱ្យមាននិមិត្តសញ្ញាខុសឆ្គង។\n\n` +
                       `👉 អ្នកអាចកែសម្រួលរូបមន្តនៅក្នុងប្រអប់ខាងលើ រួចចុច "ដោះស្រាយ" ឬចុចប៊ូតុងខាងក្រោមដើម្បីផ្ទេរទៅផ្ទាំងសរសេរដោយដៃ (Manual Typing)។`;
            showError(errorMsg, true);
          } else {
            showError(errorMsg, false);
          }
        }
      }
    } catch (err) {
      showError('កំហុសក្នុងការតភ្ជាប់ OCR: ' + err.message, false);
    }
  }

  // ---------------- OCR LaTeX Box Actions ----------------
  if (btnCopyLatex) {
    btnCopyLatex.addEventListener('click', () => {
      if (!ocrLatexInput || !ocrLatexInput.value) return;
      navigator.clipboard.writeText(ocrLatexInput.value).then(() => {
        const orig = btnCopyLatex.textContent;
        btnCopyLatex.textContent = '✅ បានចម្លង!';
        setTimeout(() => {
          btnCopyLatex.textContent = orig;
        }, 1500);
      });
    });
  }

  if (btnSolveEditedLatex) {
    btnSolveEditedLatex.addEventListener('click', async () => {
      if (!ocrLatexInput || !ocrLatexInput.value.trim()) return;
      const editedVal = ocrLatexInput.value.trim();
      switchTab('typing');
      questionInput.value = editedVal;
      updateLivePreview();
      await solveManualMath();
    });
  }

  // Action button to switch directly to manual solve
  if (btnErrorSwitchManual) {
    btnErrorSwitchManual.addEventListener('click', () => {
      switchTab('typing');
      if (pendingFallbackMath) {
        questionInput.value = pendingFallbackMath;
        updateLivePreview();
      }
    });
  }

  // ---------------- Worksheet Upload & Handling ----------------
  function setWorksheetImage(file) {
    if (!file || !file.type.startsWith('image/')) return;
    worksheetImageFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      if (worksheetPreviewImage) worksheetPreviewImage.src = e.target.result;
      if (worksheetDropzoneEmpty) worksheetDropzoneEmpty.classList.add('hidden');
      if (worksheetDropzonePreview) worksheetDropzonePreview.classList.remove('hidden');
      if (worksheetAnalyzeBtn) worksheetAnalyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  function resetWorksheetImage() {
    worksheetImageFile = null;
    if (worksheetFileInput) worksheetFileInput.value = '';
    if (worksheetPreviewImage) worksheetPreviewImage.src = '';
    if (worksheetDropzonePreview) worksheetDropzonePreview.classList.add('hidden');
    if (worksheetDropzoneEmpty) worksheetDropzoneEmpty.classList.remove('hidden');
    if (worksheetAnalyzeBtn) worksheetAnalyzeBtn.disabled = true;
  }

  if (worksheetDropzone) {
    worksheetDropzone.addEventListener('click', (e) => {
      if (e.target !== worksheetRemoveBtn && !worksheetRemoveBtn.contains(e.target)) {
        if (worksheetFileInput) worksheetFileInput.click();
      }
    });

    worksheetDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      worksheetDropzone.classList.add('dragover');
    });

    worksheetDropzone.addEventListener('dragleave', () => {
      worksheetDropzone.classList.remove('dragover');
    });

    worksheetDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      worksheetDropzone.classList.remove('dragover');
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        setWorksheetImage(files[0]);
      }
    });
  }

  if (worksheetFileInput) {
    worksheetFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        setWorksheetImage(e.target.files[0]);
      }
    });
  }

  if (worksheetRemoveBtn) {
    worksheetRemoveBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      resetWorksheetImage();
    });
  }

  worksheetSampleButtons.forEach((btn) => {
    btn.addEventListener('click', async () => {
      const samplePath = btn.dataset.worksheetSample;
      if (!samplePath) return;
      try {
        const res = await fetch(samplePath);
        const blob = await res.blob();
        const filename = samplePath.split('/').pop() || 'worksheet_sample.png';
        const file = new File([blob], filename, { type: blob.type || 'image/png' });
        setWorksheetImage(file);
      } catch (err) {
        console.error('Failed to load sample worksheet:', err);
      }
    });
  });

  if (worksheetAnalyzeBtn) {
    worksheetAnalyzeBtn.addEventListener('click', analyzeWorksheet);
  }

  // ---------------- Process Full Worksheet ----------------
  async function analyzeWorksheet() {
    if (!worksheetImageFile) return;

    showLoading(
      'កំពុងដំណើរការវិភាគសន្លឹកកិច្ចការពេញលេញ...',
      'Kiri OCR → Exercise Structure → Context Propagation → SymPy Solving'
    );

    const formData = new FormData();
    formData.append('image', worksheetImageFile, worksheetImageFile.name || 'worksheet.png');

    try {
      const response = await fetch('/api/v1/worksheets/process', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success && result.data) {
        renderWorksheetSolution(result.data);
        loadHistory();
      } else {
        const errorMsg = result.error || 'បរាជ័យក្នុងការវិភាគសន្លឹកកិច្ចការ (Worksheet processing failed)';
        showError(errorMsg, false);
      }
    } catch (err) {
      showError('កំហុសក្នុងការតភ្ជាប់ Worksheet API: ' + err.message, false);
    }
  }

  // ---------------- Render Full Worksheet Solution ----------------
  function renderWorksheetSolution(data) {
    solutionEmpty.classList.add('hidden');
    solutionLoading.classList.add('hidden');
    solutionError.classList.add('hidden');
    solutionContent.classList.remove('hidden');

    if (singleSolutionView) singleSolutionView.classList.add('hidden');
    if (worksheetSolutionView) worksheetSolutionView.classList.remove('hidden');

    const solutions = data.solutions || [];
    const sections = (data.exercise && data.exercise.sections) ? data.exercise.sections : [];
    const primarySection = sections.length > 0 ? sections[0] : null;

    // Header Statistics
    const totalCount = (data.statistics && data.statistics.total_problems) || solutions.length;
    const solvedCount = solutions.filter(s => s.answer !== null && s.answer !== undefined).length;
    const confVal = Math.round(((data.ocr && data.ocr.confidence) || 0.95) * 100);

    if (wsBadgeTotal) wsBadgeTotal.textContent = `${totalCount} លំហាត់ (${totalCount} Problems)`;
    if (wsBadgeSolved) wsBadgeSolved.textContent = `${solvedCount} បានដោះស្រាយ (${solvedCount} Solved)`;
    if (wsBadgeConf) wsBadgeConf.textContent = `Confidence: ${confVal}%`;

    // 1. Detected Instruction Card
    const instructionObj = primarySection ? primarySection.instruction : null;
    if (instructionObj && instructionObj.text) {
      if (wsInstructionCard) wsInstructionCard.classList.remove('hidden');
      if (wsInstructionText) {
        wsInstructionText.innerHTML = '';
        const textSpan = document.createElement('span');
        textSpan.textContent = instructionObj.text;
        wsInstructionText.appendChild(textSpan);
        renderMathIn(wsInstructionText);
      }
      const action = instructionObj.type || 'calculate';
      if (wsInstructionType) wsInstructionType.textContent = action.toUpperCase();
    } else {
      if (wsInstructionCard) wsInstructionCard.classList.add('hidden');
    }

    // 2. Given Context Card (Shared Variables e.g. x = 2 - √3, y = 3 + √3)
    const givenVars = primarySection ? (primarySection.given_variables || {}) : {};
    const varKeys = Object.keys(givenVars);

    if (varKeys.length > 0) {
      if (wsContextCard) wsContextCard.classList.remove('hidden');
      if (wsContextVariables) {
        wsContextVariables.innerHTML = '';
        varKeys.forEach((v) => {
          const val = givenVars[v];
          const pill = document.createElement('div');
          pill.className = 'ws-context-pill';

          const varLabel = document.createElement('span');
          varLabel.className = 'ws-context-var';
          varLabel.textContent = `${v} =`;

          const valSpan = document.createElement('span');
          valSpan.className = 'ws-context-val';
          renderKaTeX(valSpan, String(val), false);

          pill.appendChild(varLabel);
          pill.appendChild(valSpan);
          wsContextVariables.appendChild(pill);
        });
      }
    } else {
      if (wsContextCard) wsContextCard.classList.add('hidden');
    }

    // 3. Problems and Solutions List
    if (wsProblemsCount) wsProblemsCount.textContent = `${solutions.length} Problems`;
    if (wsProblemsContainer) {
      wsProblemsContainer.innerHTML = '';

      if (solutions.length === 0) {
        wsProblemsContainer.innerHTML = `
          <div class="empty-state" style="padding: 2rem;">
            <p>រកមិនឃើញលំហាត់នៅក្នុងសន្លឹកកិច្ចការនេះទេ</p>
          </div>
        `;
      } else {
        solutions.forEach((prob, index) => {
          const card = document.createElement('div');
          card.className = 'ws-problem-card';

          // Header: Label + Badges
          const header = document.createElement('div');
          header.className = 'ws-problem-header';

          const labelBadge = document.createElement('span');
          labelBadge.className = 'ws-problem-label-badge';
          labelBadge.textContent = prob.label || `លំហាត់ ${index + 1}`;

          const badgesGroup = document.createElement('div');
          badgesGroup.className = 'ws-problem-badges';

          const typeBadge = document.createElement('span');
          typeBadge.className = 'badge badge-primary';
          typeBadge.textContent = (prob.problem_type || 'Problem')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
          badgesGroup.appendChild(typeBadge);

          if (prob.is_verified) {
            const verifiedBadge = document.createElement('span');
            verifiedBadge.className = 'badge badge-success';
            verifiedBadge.innerHTML = `✓ ផ្ទៀងផ្ទាត់ (Verified)`;
            badgesGroup.appendChild(verifiedBadge);
          }

          header.appendChild(labelBadge);
          header.appendChild(badgesGroup);
          card.appendChild(header);

          // Expression Box (KaTeX)
          const exprBox = document.createElement('div');
          exprBox.className = 'ws-problem-expr-box';
          const exprMath = document.createElement('div');
          renderKaTeX(exprMath, prob.expression || '', true);
          exprBox.appendChild(exprMath);
          card.appendChild(exprBox);

          // Problem Relationships (e.g. Depends on given values: x, y)
          const rels = prob.relationships || [];
          if (rels.length > 0) {
            rels.forEach((rel) => {
              const relBanner = document.createElement('div');
              relBanner.className = 'ws-relationship-banner';
              relBanner.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                <span>${escapeHtml(rel)}</span>
              `;
              card.appendChild(relBanner);
            });
          }

          // Solution Hero Box
          const solutionBox = document.createElement('div');
          solutionBox.className = 'ws-solution-box';

          const solLeft = document.createElement('div');
          solLeft.className = 'ws-solution-left';

          const solTag = document.createElement('span');
          solTag.className = 'ws-solution-tag';
          solTag.textContent = 'ចម្លើយចុងក្រោយ (Final Answer):';

          const solAnswer = document.createElement('div');
          solAnswer.className = 'ws-solution-answer';
          if (prob.answer) {
            renderKaTeX(solAnswer, String(prob.answer), false);
          } else if (prob.error) {
            solAnswer.style.color = '#fda4af';
            solAnswer.style.fontSize = '0.95rem';
            solAnswer.textContent = prob.error;
          } else {
            solAnswer.style.color = '#94a3b8';
            solAnswer.style.fontSize = '0.95rem';
            solAnswer.textContent = 'មិនមានចម្លើយ (Unsolved)';
          }

          solLeft.appendChild(solTag);
          solLeft.appendChild(solAnswer);
          solutionBox.appendChild(solLeft);

          // Steps Toggle & Steps
          const steps = prob.steps || [];
          if (steps.length > 0) {
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'ws-steps-toggle';
            toggleBtn.innerHTML = `<span>ដំណាក់កាល (${steps.length} Steps)</span> ▾`;

            const stepsWrapper = document.createElement('div');
            stepsWrapper.className = 'ws-problem-steps';

            steps.forEach((st) => {
              const stepRow = document.createElement('div');
              stepRow.className = 'ws-step-row';

              const stepNum = document.createElement('div');
              stepNum.className = 'ws-step-num';
              stepNum.textContent = st.order || '•';

              const stepBody = document.createElement('div');
              stepBody.className = 'ws-step-body';

              const stepDesc = document.createElement('div');
              stepDesc.className = 'ws-step-desc';
              stepDesc.textContent = st.description_km || st.description_en || '';
              stepBody.appendChild(stepDesc);

              if (st.expression) {
                const stepExpr = document.createElement('div');
                stepExpr.className = 'ws-step-expr';
                renderKaTeX(stepExpr, st.expression, true);
                stepBody.appendChild(stepExpr);
              }

              stepRow.appendChild(stepNum);
              stepRow.appendChild(stepBody);
              stepsWrapper.appendChild(stepRow);
            });

            toggleBtn.addEventListener('click', () => {
              stepsWrapper.classList.toggle('hidden');
              const isHidden = stepsWrapper.classList.contains('hidden');
              toggleBtn.innerHTML = `<span>ដំណាក់កាល (${steps.length} Steps)</span> ${isHidden ? '▾' : '▴'}`;
            });

            solutionBox.appendChild(toggleBtn);
            card.appendChild(solutionBox);
            card.appendChild(stepsWrapper);
          } else {
            card.appendChild(solutionBox);
          }

          wsProblemsContainer.appendChild(card);
        });
      }
    }

    // 4. Raw Kiri OCR Text
    if (wsRawOcrText) {
      wsRawOcrText.textContent = (data.ocr && data.ocr.detected_text) || 'No text detected';
    }
  }

  // ---------------- Render Solution States ----------------
  function showLoading(title, subtitle) {
    solutionEmpty.classList.add('hidden');
    solutionError.classList.add('hidden');
    solutionContent.classList.add('hidden');
    if (errorActions) errorActions.classList.add('hidden');
    solutionLoading.classList.remove('hidden');

    const loadingTitle = document.querySelector('.loading-title');
    const loadingSub = document.querySelector('.loading-subtitle');
    if (loadingTitle) {
      loadingTitle.textContent = title || 'កំពុងដំណើរការគណនា និងផ្ទៀងផ្ទាត់...';
    }
    if (loadingSub) {
      loadingSub.textContent = subtitle || 'Solving symbolically with SymPy & verifying accuracy';
    }
  }

  function showError(msg, showAction = false) {
    solutionEmpty.classList.add('hidden');
    solutionLoading.classList.add('hidden');
    solutionContent.classList.add('hidden');
    solutionError.classList.remove('hidden');
    errorMessage.textContent = msg;

    if (errorActions) {
      if (showAction) {
        errorActions.classList.remove('hidden');
      } else {
        errorActions.classList.add('hidden');
      }
    }
  }

  function renderSolution(data, isFromVision) {
    solutionEmpty.classList.add('hidden');
    solutionLoading.classList.add('hidden');
    solutionError.classList.add('hidden');
    solutionContent.classList.remove('hidden');

    // Ensure single solution view is visible and worksheet view is hidden
    if (singleSolutionView) singleSolutionView.classList.remove('hidden');
    if (worksheetSolutionView) worksheetSolutionView.classList.add('hidden');

    // Format Problem Type label
    const typeLabel = (data.problem_type || 'math_problem')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());
    badgeProblemType.textContent = typeLabel;

    // Verified badge
    if (data.is_verified) {
      badgeVerified.className = 'badge badge-success';
      badgeVerified.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <span>ផ្ទៀងផ្ទាត់ត្រឹមត្រូវ (Verified)</span>
      `;
    } else {
      badgeVerified.className = 'badge badge-primary';
      badgeVerified.textContent = 'ដំណោះស្រាយ (Solution)';
    }

    // Hero variable and answer (Rendered with KaTeX)
    if (data.variable) {
      const ansTrim = String(data.answer || '').trim();
      if (!ansTrim.startsWith(`${data.variable} =`) && !ansTrim.startsWith(`${data.variable}=`)) {
        heroVar.textContent = `${data.variable} = `;
      } else {
        heroVar.textContent = '';
      }
    } else {
      heroVar.textContent = '';
    }
    heroAnswer.innerHTML = '';
    renderKaTeX(heroAnswer, String(data.answer ?? 'N/A'), false);

    // OCR Info Banner & LaTeX Card
    if (isFromVision && (data.ocr_detected_text || data.cleaned_math_expression)) {
      const bestLatex = data.cleaned_math_expression || data.ocr_detected_text;
      ocrInfoBanner.classList.remove('hidden');
      ocrDetectedText.textContent = data.ocr_detected_text || '';
      const conf = Math.round((data.ocr_confidence || 0.95) * 100);
      ocrConfVal.textContent = `${conf}%`;
      ocrConfFill.style.width = `${conf}%`;

      // Populate editable LaTeX card
      if (ocrLatexCard && ocrLatexInput) {
        ocrLatexCard.classList.remove('hidden');
        ocrLatexInput.value = bestLatex;
      }

      // Exercise title and instruction badges
      if (data.exercise_title || data.instruction) {
        ocrExerciseHeaderRow.classList.remove('hidden');
        if (data.exercise_title) {
          ocrExerciseBadge.textContent = data.exercise_title;
          ocrExerciseBadge.classList.remove('hidden');
        } else {
          ocrExerciseBadge.classList.add('hidden');
        }
        if (data.instruction) {
          ocrInstructionBadge.textContent = data.instruction;
          ocrInstructionBadge.classList.remove('hidden');
        } else {
          ocrInstructionBadge.classList.add('hidden');
        }
      } else {
        ocrExerciseHeaderRow.classList.add('hidden');
      }

      // Extracted math expression display
      if (data.cleaned_math_expression && data.cleaned_math_expression !== data.ocr_detected_text) {
        ocrCleanedRow.classList.remove('hidden');
        ocrCleanedText.textContent = data.cleaned_math_expression;
      } else {
        ocrCleanedRow.classList.add('hidden');
      }
    } else {
      ocrInfoBanner.classList.add('hidden');
    }

    // Render Lesson Curriculum Banner
    if (lessonCurriculumBanner) {
      if (data.lesson_info) {
        lessonCurriculumBanner.classList.remove('hidden');
        if (lessonChapterBadge) {
          lessonChapterBadge.textContent = `${data.lesson_info.chapter_km} (${data.lesson_info.chapter_en})`;
        }
        if (lessonNameBadge) {
          lessonNameBadge.textContent = data.lesson_info.lesson_km || '';
        }
        if (lessonMethodBadge) {
          lessonMethodBadge.textContent = data.lesson_info.method_km || '';
        }
        if (lessonFormulaPill && lessonFormulaContent) {
          if (data.lesson_info.rule_formula) {
            lessonFormulaPill.classList.remove('hidden');
            lessonFormulaContent.innerHTML = '';
            renderKaTeX(lessonFormulaContent, data.lesson_info.rule_formula, false);
          } else {
            lessonFormulaPill.classList.add('hidden');
          }
        }
      } else {
        lessonCurriculumBanner.classList.add('hidden');
      }
    }

    // Steps list with KaTeX rendering & pedagogical annotations
    stepsList.innerHTML = '';
    if (data.steps && data.steps.length > 0) {
      data.steps.forEach((step) => {
        const stepCard = document.createElement('div');
        stepCard.className = step.is_verification ? 'step-card step-card-verification' : 'step-card';

        const stepNumber = document.createElement('div');
        stepNumber.className = 'step-number';
        stepNumber.textContent = step.order || '•';

        const stepContent = document.createElement('div');
        stepContent.className = 'step-content';

        // Step Header Row (Title + Verification Badge)
        const headerRow = document.createElement('div');
        headerRow.className = 'step-header-row';

        const titleKm = document.createElement('div');
        titleKm.className = 'step-title-km';
        titleKm.textContent = step.title_km || step.description_km || '';
        headerRow.appendChild(titleKm);

        if (step.is_verification) {
          const verifTag = document.createElement('span');
          verifTag.className = 'step-verification-tag';
          verifTag.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span>ផ្ទៀងផ្ទាត់ (Verification)</span>
          `;
          headerRow.appendChild(verifTag);
        }
        stepContent.appendChild(headerRow);

        // English Title / Description
        const engText = step.title_en || step.description_en;
        if (engText) {
          const titleEn = document.createElement('div');
          titleEn.className = 'step-title-en';
          titleEn.textContent = engText;
          stepContent.appendChild(titleEn);
        }

        // Pedagogical Rationale ("Why" this step is performed)
        if (step.rationale_km) {
          const whyBox = document.createElement('div');
          whyBox.className = 'step-why-box';
          whyBox.innerHTML = `
            <div>
              <span class="step-why-label">💡 ហេតុអ្វី (Why):</span>
              <span class="step-why-text">${escapeHtml(step.rationale_km)}</span>
            </div>
            ${step.rationale_en ? `<div class="step-why-en">${escapeHtml(step.rationale_en)}</div>` : ''}
          `;
          stepContent.appendChild(whyBox);
        }

        // Specific Formula/Rule for this step
        if (step.rule_formula) {
          const rulePill = document.createElement('div');
          rulePill.className = 'step-rule-pill';
          const ruleIcon = document.createElement('span');
          ruleIcon.textContent = '📌 រូបមន្ត: ';
          const ruleMath = document.createElement('span');
          renderKaTeX(ruleMath, step.rule_formula, false);
          rulePill.appendChild(ruleIcon);
          rulePill.appendChild(ruleMath);
          stepContent.appendChild(rulePill);
        }

        // Mathematical Expression
        if (step.expression) {
          const exprBox = document.createElement('div');
          exprBox.className = 'step-expression';
          renderKaTeX(exprBox, step.expression, true);
          stepContent.appendChild(exprBox);
        }

        renderMathIn(stepContent);

        stepCard.appendChild(stepNumber);
        stepCard.appendChild(stepContent);
        stepsList.appendChild(stepCard);
      });
    } else {
      stepsList.innerHTML = `
        <div class="step-card">
          <div class="step-content">
            <div class="step-title-km">ចម្លើយគណនាដោយ SymPy ៖ ${escapeHtml(String(data.answer))}</div>
          </div>
        </div>
      `;
    }
  }

  // ---------------- History Drawer ----------------
  historyToggleBtn.addEventListener('click', () => {
    historyDrawer.classList.toggle('hidden');
    if (!historyDrawer.classList.contains('hidden')) {
      loadHistory();
    }
  });

  closeHistoryBtn.addEventListener('click', () => {
    historyDrawer.classList.add('hidden');
  });

  async function loadHistory() {
    try {
      const res = await fetch('/api/v1/math/history?limit=30');
      const json = await res.json();

      if (json.success && json.data && json.data.items) {
        const items = json.data.items;
        historyCount.textContent = `${items.length} problems`;

        if (items.length === 0) {
          historyEmpty.classList.remove('hidden');
          historyList.innerHTML = '';
          return;
        }

        historyEmpty.classList.add('hidden');
        historyList.innerHTML = '';

        items.forEach((item) => {
          const card = document.createElement('div');
          card.className = 'history-item';

          const timeFormatted = new Date(item.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });

          card.innerHTML = `
            <div class="history-meta">
              <span class="history-type">${item.problem_type.replace(/_/g, ' ')}</span>
              <span class="history-time">${timeFormatted}</span>
            </div>
            <div class="history-q">${escapeHtml(item.question)}</div>
            <div class="history-ans">Answer: ${escapeHtml(item.answer || '')}</div>
          `;

          card.addEventListener('click', () => {
            renderSolution(
              {
                problem_type: item.problem_type,
                original_question: item.question,
                answer: item.answer,
                is_verified: item.is_verified,
                steps: item.steps || [],
              },
              false
            );
            questionInput.value = item.question;
            updateLivePreview();
            historyDrawer.classList.add('hidden');
          });

          historyList.appendChild(card);
        });
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }

  clearHistoryBtn.addEventListener('click', async () => {
    if (confirm('តើអ្នកពិតជាចង់លុបប្រវត្តិទាំងអស់មែនទេ? (Clear all history?)')) {
      try {
        await fetch('/api/v1/math/history', { method: 'DELETE' });
        loadHistory();
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  });

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
});
