# Math Master Fullstack (Khmer Math Lab)

A modern fullstack AI-powered mathematics solver and learning lab designed specifically for Khmer and English mathematical expressions, BacII preparation (Grade 12), and interactive step-by-step problem solving.

---

## 🚀 Features Overview

- **Deterministic Solver Engine**: Uses SymPy for rigorous mathematical correctness—no hallucinated arithmetic.
- **Khmer & English Language Support**: Understands natural Khmer keywords (ដោះស្រាយ, គណនា, រក, etc.), Khmer numerals (០-៩), and provides explanations in Khmer.
- **BacII Math Curriculum**:
  - Linear, quadratic, and higher-degree polynomial equations & inequalities
  - Real sequences (ស្វ៊ីតចំនួនពិត) — arithmetic, geometric, general terms, limits, and sums
  - Natural logarithms & exponentials
  - Primitives and definite integrals
- **Math Vision / OCR Integration**:
  - Multi-provider OCR architecture supporting native Khmer OCR, Pix2Tex, Tesseract, Mathpix, Google Cloud Vision, and Gemini Vision
  - Intelligent routing and preprocessing (perspective correction, deskew, binarization)
- **Interactive Web Interface**:
  - Built with React, Vite, and modern UI components
  - Formula rendering, step-by-step reasoning view, bilingual glossaries, and math keyboard
- **RESTful API**:
  - FastAPI backend with async database support, Swagger/OpenAPI documentation, and request tracking

---

## 📁 Repository Structure

```
math-master-fullstack/
├── frontend/               # React + Vite web application
│   ├── src/                # UI components, pages, state, and styling
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies & scripts
│   └── vite.config.js      # Vite build configuration
│
├── backend/                # FastAPI Python backend
│   ├── app/                # Application modules
│   │   ├── api/            # API endpoints & routing (v1)
│   │   ├── core/           # Mathematical engines, parsers, and solvers
│   │   ├── models/         # Pydantic schemas and ORM models
│   │   ├── services/       # Business logic & OCR orchestration
│   │   └── db/             # Database session management
│   ├── tests/              # Pytest test suite
│   ├── training/           # OCR models, datasets, and scripts
│   ├── Dockerfile          # Backend container specification
│   ├── docker-compose.yml  # Docker compose configuration
│   └── requirements.txt    # Python dependencies
│
└── README.md
```

---

## 🛠️ Quick Start

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations / init & start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
source .venv/bin/activate
pytest -v
```

---

## 📜 License

MIT License.
