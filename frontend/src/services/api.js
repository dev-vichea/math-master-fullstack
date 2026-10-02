/**
 * API service for communicating with the Khmer Math Lab FastAPI backend.
 */

const API_BASE = '/api/v1';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return { online: false, error: `HTTP ${res.status}` };
    const data = await res.json();
    return { online: true, ...data };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

export async function solveMath(question, language = 'km') {
  const res = await fetch(`${API_BASE}/math/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, language }),
  });

  const payload = await res.json();
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || `Error solving problem (${res.status})`);
  }
  return payload.data;
}

export async function solveVision(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);

  const res = await fetch(`${API_BASE}/math/vision`, {
    method: 'POST',
    body: formData,
  });

  const payload = await res.json();
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || `Error processing vision OCR (${res.status})`);
  }
  return payload.data;
}

export async function processWorksheet(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);

  const res = await fetch(`${API_BASE}/worksheets/process`, {
    method: 'POST',
    body: formData,
  });

  const payload = await res.json();
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || `Error analyzing worksheet (${res.status})`);
  }
  return payload.data;
}

export async function fetchGlossaryTerms(query = '', category = '') {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (category) params.append('category', category);

  const res = await fetch(`${API_BASE}/glossary?${params.toString()}`);
  const payload = await res.json();
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || 'Failed to fetch glossary terms');
  }
  return payload.data;
}

export async function fetchGlossaryCategories() {
  const res = await fetch(`${API_BASE}/glossary/categories`);
  const payload = await res.json();
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || 'Failed to fetch categories');
  }
  return payload.data?.categories || [];
}

export async function fetchGlossaryExamples() {
  const res = await fetch(`${API_BASE}/glossary/examples`);
  const payload = await res.json();
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || 'Failed to fetch glossary examples');
  }
  return payload.data?.examples || [];
}

