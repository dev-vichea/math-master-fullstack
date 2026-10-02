# Math Vision OCR Setup Guide

This guide explains how to set up and configure different OCR providers for the Math Vision feature.

## Overview

The Khmer Math Lab backend supports multiple OCR providers through a pluggable architecture with advanced features:

- **Multiple OCR Engines**: Tesseract, Kiri OCR, Google Vision, Mathpix, Gemini Vision, Pix2Tex
- **Intelligent Routing**: Automatic engine selection based on image analysis
- **Multi-Engine Ensemble**: Combine multiple engines with voting or fallback
- **Advanced Preprocessing**: Auto-deskew, perspective correction, adaptive binarization
- **Enhanced Postprocessing**: LaTeX normalization, OCR error correction, math notation fixes
- **Result Caching**: SHA-256 based caching for improved performance
- **Evaluation Tools**: CER/WER metrics, benchmarking, and comparison reports

You can easily switch between providers or enable advanced features by setting environment variables.

## Available Providers

| Provider | Cost | Accuracy | Khmer Support | Math Support | Setup Difficulty |
|----------|------|----------|---------------|--------------|------------------|
| **Stub** (default) | Free | N/A | N/A | N/A | None |
| **Kiri OCR** (`kiri`, `khmer_ocr`) | Free (Offline) | High | 🇰🇭 Native/Excellent | ✅ Good | Easy (`pip install`) |
| **Tesseract** (`tesseract`) | Free (Offline) | High (with CLAHE) | ✅ Good | ✅ Good (with Sanitizer) | Medium (needs brew) |
| **Gemini Vision** (`gemini`) | Free tier + paid | Superior (SOTA) | 🇰🇭 Native/Exceptional | 🧮 SOTA | Easy (`GEMINI_API_KEY`) |
| **Google Vision** (`google`) | Free tier + paid | High | ✅ Excellent | ⚠️ Good | Medium (GCP account) |
| **Mathpix** (`mathpix`) | Paid | Excellent | ✅ Good | ✅ Excellent | Easy (API keys) |
| **Intelligent Router** (`smart`) | Varies | Adaptive | ✅ Auto-detects | ✅ Auto-detects | Easy (auto-config) |
| **Ensemble** (`ensemble:*`) | Varies | High (voting) | ✅ Combined | ✅ Combined | Medium (multi-engine) |

## Advanced Features

### 🎯 Intelligent Routing (Recommended)

Automatically analyzes images and routes to the best OCR engine:

```bash
# Enable intelligent routing
VISION_PROVIDER=smart
```

**What it does:**
- Detects Khmer script → Routes to Kiri OCR or Gemini
- Detects complex math notation → Routes to Mathpix or Gemini  
- Detects handwriting → Routes to Gemini
- Detects low quality → Uses ensemble with voting
- Default cases → Routes to Tesseract (fast & free)

**Benefits:**
- No manual configuration needed
- Optimal accuracy for each image type
- Automatic fallback on errors
- Cost-effective (uses free engines when possible)

### 🔄 Multi-Engine Ensemble

Combine multiple OCR engines for improved accuracy:

```bash
# Voting strategy: run all engines, select most common result
VISION_PROVIDER=ensemble:voting:kiri,tesseract,gemini

# Confidence strategy: select highest confidence result
VISION_PROVIDER=ensemble:confidence:kiri,mathpix

# Fallback strategy: try engines sequentially
VISION_PROVIDER=ensemble:fallback:kiri,tesseract

# Best-of-N: voting among successful results
VISION_PROVIDER=ensemble:best_of_n:kiri,tesseract,gemini
```

**Strategies:**
- `fallback`: Sequential (fast, cost-effective)
- `voting`: Democratic consensus (most accurate)
- `confidence`: Trust score-based (balanced)
- `best_of_n`: Confidence + voting (robust)

### 🖼️ Advanced Image Preprocessing

Enhanced preprocessing options for better OCR accuracy:

```python
from app.core.vision.preprocessor import preprocess_image

# Auto-deskew tilted images
processed = preprocess_image(
    image_bytes,
    mode="enhanced_grayscale",
    auto_deskew=True,          # Automatically straighten text
    auto_perspective=True,      # Fix angled camera shots
    binarization_method="sauvola"  # Best for handwriting
)

# Adaptive binarization methods
processed = preprocess_image(
    image_bytes,
    mode="adaptive_binary",
    binarization_method="gaussian"  # or "otsu", "sauvola"
)
```

**Preprocessing modes:**
- `enhanced_grayscale`: CLAHE contrast + denoising (recommended)
- `binary`: Otsu thresholding (printed text)
- `adaptive_binary`: Advanced adaptive methods (handwriting)
- `standard`: Basic RGB with contrast boost

**Binarization methods:**
- `otsu`: Global threshold (fast, good for clean images)
- `gaussian`: Adaptive local threshold (varying lighting)
- `sauvola`: Local adaptive (best for handwriting)

### 📝 Enhanced Postprocessing

Automatic correction of OCR errors:

```python
from app.core.vision.postprocessor import sanitize_ocr_math_text

# Automatic corrections:
text = sanitize_ocr_math_text(raw_ocr_output)
```

**What it fixes:**
- LaTeX commands: `\times` → `*`, `\frac{a}{b}` → `(a)/(b)`
- Character confusions: `O`→`0`, `l`→`1`, `S`→`5`, `B`→`8`, `Z`→`2`
- Collapsed exponents: `x2` → `x^2`
- Fragmented numbers: `1 5` → `15`
- Coefficient spacing: `2 x` → `2x`
- Fraction formats: `3 over 4` → `3/4`
- Exponent spacing: `x^ 2` → `x^2`
- Parenthesis balancing: auto-closes unmatched `(`
- Equation spacing: `2x=10` → `2x = 10`

### 💾 Result Caching

Cache OCR results for repeated images:

```python
from app.core.vision.cache import create_cached_engine
from app.core.vision.factory import create_vision_engine

# Wrap any engine with caching
engine = create_vision_engine("tesseract")
cached_engine = create_cached_engine(
    engine,
    cache_size=1000,      # Max entries in memory
    ttl_seconds=3600,     # 1 hour TTL
    persistent=True       # Enable file cache
)

# Use cached engine
result = cached_engine.detect(image_bytes)

# Check cache performance
stats = cached_engine.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

**Benefits:**
- Avoid reprocessing identical images
- SHA-256 image hashing
- In-memory LRU cache + optional persistent cache
- Configurable TTL and size limits

### 📊 Evaluation & Benchmarking

Compare OCR engines on your dataset:

```python
from app.core.vision.evaluation import OCREvaluator, OCRBenchmark
from app.core.vision.factory import create_vision_engine

# Load test cases
test_cases = [
    (image1_bytes, "expected text 1"),
    (image2_bytes, "expected text 2"),
]

# Evaluate single engine
engine = create_vision_engine("kiri")
results = OCREvaluator.evaluate_dataset(engine, test_cases)
print(f"Accuracy: {results['accuracy']:.2%}")
print(f"Average CER: {results['average_cer']:.4f}")

# Compare multiple engines
engines = {
    "kiri": create_vision_engine("kiri"),
    "tesseract": create_vision_engine("tesseract"),
    "gemini": create_vision_engine("gemini"),
}
comparison = OCRBenchmark.compare_engines(engines, test_cases)
report = OCRBenchmark.generate_report(comparison)
print(report)
```

**Metrics provided:**
- Exact match accuracy
- Character Error Rate (CER)
- Word Error Rate (WER)
- Confidence scores
- Processing time
- Error analysis

## Quick Start

### Easiest: Intelligent Routing (Recommended for Production)

Automatically selects the best OCR engine for each image:

```bash
# In .env file
VISION_PROVIDER=smart

# Test via API
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@math_problem.jpg"
```

**Requires:** At least 2 OCR engines installed (e.g., `pip install kiri-ocr` + Tesseract)

### Simple: Single Engine

The easiest way to get started with **native Khmer OCR** is with **Kiri OCR** (Python library, free, offline):

```bash
# 1. Install Kiri OCR
pip install kiri-ocr

# 2. Set environment variable in .env
VISION_PROVIDER=kiri  # or khmer_ocr

# 3. Test it via API
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@math_problem.jpg"
```

---

## Provider Setup Details

### 1. Stub (Default - No OCR)

**When to use:** API development, testing mobile app integration without OCR.

**Setup:**
```bash
export VISION_PROVIDER=stub
```

No additional configuration needed. Returns "not implemented" message.

---

### 2. Kiri OCR (Recommended for Native Khmer OCR, Free & Offline)

**When to use:** Local, high-accuracy Khmer & English OCR without cloud API fees or system binary installations.

**Pros:**
- ✅ Native Khmer script recognition (consonants, subscripts, vowels, numerals)
- ✅ Free, open-source, runs offline
- ✅ Transformer architecture with CTC + attention decoder
- ✅ Pure Python package (`pip install kiri-ocr`)
- ✅ No cloud API account or internet required during inference

**Cons:**
- ⚠️ Model weights (~150MB) downloaded on first execution
- ⚠️ Uses PyTorch for inference

**Setup:**
```bash
pip install kiri-ocr
export VISION_PROVIDER=kiri
```

---

### 3. Gemini Vision (Recommended for Complex Multimodal Worksheets)

**When to use:** Production, state-of-the-art accuracy on handwritten math, complex textbook worksheets, and mixed Khmer/English exercises.

**Pros:**
- ✅ State-of-the-art multimodal understanding for Khmer script and handwriting
- ✅ Automatically isolates exercise titles ("លំហាត់ទី 1"), instructions, and math expressions
- ✅ Understands complex mathematical formulas, fractions, radicals, and systems
- ✅ Fast response times with `gemini-2.5-flash`

**Cons:**
- ⚠️ Requires internet connection and `GEMINI_API_KEY` (free tier available at AI Studio)

**Setup:**
1. Get an API key from [Google AI Studio](https://aistudio.google.com/)
2. In `.env`:
```bash
VISION_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
```

---

### 4. Tesseract (Traditional Open-Source OCR)

**When to use:** Free development, offline usage, privacy-sensitive applications.

**Pros:**
- ✅ Free and open-source
- ✅ Works offline
- ✅ Supports Khmer language
- ✅ No API limits

**Cons:**
- ⚠️ Less accurate for handwriting
- ⚠️ Struggles with complex math notation

**Setup:**

#### Step 1: Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-khm
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

#### Step 2: Install Python Libraries
```bash
pip install pytesseract pillow
```

#### Step 3: Verify Installation
```bash
tesseract --version
tesseract --list-langs  # Should show 'khm' if Khmer is installed
```

#### Step 4: Configure
```bash
# Add to .env file
VISION_PROVIDER=tesseract
```

#### Step 5: (Optional) Install Khmer Language Data
If Khmer isn't in the `--list-langs` output:
```bash
# Download khm.traineddata from:
# https://github.com/tesseract-ocr/tessdata/raw/main/khm.traineddata

# Copy to Tesseract data directory:
# macOS: /usr/local/share/tessdata/
# Linux: /usr/share/tesseract-ocr/4.00/tessdata/
```

---

### 4. Google Cloud Vision (Recommended for Production)

**When to use:** Production use with good Khmer support, affordable pricing.

**Pros:**
- ✅ Excellent Khmer recognition
- ✅ Good for printed/typed math
- ✅ Affordable ($1.50 per 1000 images after free tier)
- ✅ Free tier: 1000 requests/month

**Cons:**
- ⚠️ Less specialized for handwritten math notation
- ⚠️ Requires Google Cloud account

**Setup:**

#### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Cloud Vision API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

#### Step 2: Create Service Account
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: "khmer-math-ocr"
4. Grant role: "Cloud Vision" → "Cloud Vision User"
5. Click "Create Key" → JSON
6. Download the JSON file

#### Step 3: Install Python Library
```bash
pip install google-cloud-vision
```

#### Step 4: Configure
```bash
# Add to .env file
VISION_PROVIDER=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Security Note:** Never commit the service account JSON file to git!

---

### 5. Mathpix (Best for Complex Math)

**When to use:** Handwritten complex equations, matrices, advanced notation.

**Pros:**
- ✅ Best-in-class for mathematical notation
- ✅ Handles complex equations, matrices, calculus
- ✅ Fast and reliable

**Cons:**
- ⚠️ Paid service (free tier: 1000 requests/month)
- ⚠️ Most expensive option

**Setup:**

#### Step 1: Sign Up
1. Go to https://mathpix.com/
2. Sign up for an account
3. Choose a plan:
   - **Free Tier:** 1000 requests/month
   - **Paid Plans:** Starting at $4.99/month

#### Step 2: Get API Credentials
1. Go to https://accounts.mathpix.com/
2. Navigate to "OCR API"
3. Copy your `APP_ID` and `APP_KEY`

#### Step 3: Install Python Library
```bash
pip install requests
```

#### Step 4: Configure
```bash
# Add to .env file
VISION_PROVIDER=mathpix
MATHPIX_APP_ID=your_app_id_here
MATHPIX_APP_KEY=your_app_key_here
```

---

## Testing Your Setup

### Check Available Providers

```python
from app.core.vision.factory import list_available_providers

providers = list_available_providers()
for name, available in providers.items():
    status = "✓ Available" if available else "✗ Not Available"
    print(f"{name}: {status}")
```

### Test OCR with Sample Image

```bash
# Test the /math/vision endpoint
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@test_math.jpg" \
  -F "language=km"
```

### Python Test Script

```python
from app.core.vision.factory import create_vision_engine

# Create engine
engine = create_vision_engine("tesseract")  # or "google", "mathpix"

# Read test image
with open("test_math.jpg", "rb") as f:
    image_bytes = f.read()

# Detect
result = engine.detect(image_bytes)

print(f"Detected: {result.detected_text}")
print(f"Confidence: {result.confidence:.2%}")
if result.error_message:
    print(f"Error: {result.error_message}")
```

---

## Choosing the Right Provider

### For Development/Testing
**Use: Tesseract**
- Free, offline, good for testing the integration

### For Production (Budget-Friendly)
**Use: Google Cloud Vision**
- Good balance of cost, Khmer support, and accuracy

### For Production (Best Math Accuracy)
**Use: Mathpix**
- Best for complex handwritten equations
- More expensive but worth it for advanced math

### Hybrid Approach (Recommended)
Use different providers for different scenarios:
```python
# In your code, you can dynamically choose:
if is_complex_math:
    engine = create_vision_engine("mathpix")
else:
    engine = create_vision_engine("google")
```

---

## Cost Comparison

| Provider | Free Tier | After Free Tier | Est. Cost for 10,000 images |
|----------|-----------|-----------------|------------------------------|
| Tesseract | Unlimited | N/A (free) | **$0** |
| Google Vision | 1,000/month | $1.50 per 1,000 | **$13.50** |
| Mathpix | 1,000/month | ~$0.04 per image | **$360** |

---

## Troubleshooting

### Tesseract: "TesseractNotFoundError"
```bash
# Verify installation
which tesseract
tesseract --version

# macOS: Reinstall
brew reinstall tesseract

# Linux: Reinstall
sudo apt-get install --reinstall tesseract-ocr
```

### Tesseract: Khmer Not Detected
```bash
# Check available languages
tesseract --list-langs

# If 'khm' missing, install it:
# Ubuntu
sudo apt-get install tesseract-ocr-khm

# macOS
brew install tesseract-lang
```

### Google Vision: Authentication Error
```bash
# Verify credentials file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
python -c "from google.cloud import vision; client = vision.ImageAnnotatorClient(); print('✓ Auth works')"
```

### Mathpix: Invalid Credentials
```bash
# Verify environment variables are set
echo $MATHPIX_APP_ID
echo $MATHPIX_APP_KEY

# Test API connection
curl -X POST https://api.mathpix.com/v3/text \
  -H "app_id: $MATHPIX_APP_ID" \
  -H "app_key: $MATHPIX_APP_KEY" \
  -d '{"src": "data:image/jpeg;base64,..."}'
```

---

## Best Practices

### Choosing the Right Configuration

**For Development:**
```bash
VISION_PROVIDER=tesseract  # Fast, free, good enough for testing
```

**For Production (Balanced):**
```bash
VISION_PROVIDER=smart  # Intelligent routing with automatic fallback
```

**For Production (Maximum Accuracy):**
```bash
VISION_PROVIDER=ensemble:voting:kiri,gemini,mathpix  # Multiple engines with voting
```

**For Production (Cost-Effective):**
```bash
VISION_PROVIDER=ensemble:fallback:kiri,tesseract  # Free engines with fallback
```

### Image Quality Guidelines

For best OCR results, ensure:

✅ **Good:**
- Adequate lighting (no harsh shadows)
- Text is horizontal (or use auto-deskew)
- Minimum 800px on shortest side
- Sharp focus (not blurry)
- High contrast between text and background

❌ **Avoid:**
- Very low resolution (<400px)
- Extreme angles (>30° rotation)
- Severe motion blur
- Heavy shadows or glare
- Compressed/lossy formats (prefer PNG over JPEG)

### Performance Optimization

**1. Enable Caching for Repeated Images:**
```python
from app.core.vision.cache import create_cached_engine

cached = create_cached_engine(
    engine,
    cache_size=1000,
    ttl_seconds=3600,
    persistent=True
)
```

**2. Use Appropriate Preprocessing:**
- Clean scanned documents → `mode="binary"`, `binarization_method="otsu"`
- Phone camera photos → `mode="enhanced_grayscale"`, `auto_deskew=True`
- Handwritten notes → `mode="adaptive_binary"`, `binarization_method="sauvola"`

**3. Choose Efficient Ensemble Strategy:**
- Development → `fallback` (fastest)
- Production → `best_of_n` (balanced)
- Critical accuracy → `voting` (most accurate)

### Security Considerations

- Never commit API keys (use `.env` file)
- Set appropriate cache TTL for sensitive content
- Use local engines (Tesseract, Kiri) for private data
- Validate image file sizes (prevent DOS)
- Sanitize OCR output before using in queries

### Monitoring & Debugging

**Enable detailed logging:**
```bash
LOG_LEVEL=DEBUG
```

**Check cache performance:**
```python
stats = cached_engine.get_cache_stats()
if stats['hit_rate'] < 0.3:
    print("Low cache hit rate - consider increasing cache_size")
```

**Benchmark your engines:**
```python
# Compare accuracy on your specific dataset
comparison = OCRBenchmark.compare_engines(engines, test_cases)
print(OCRBenchmark.generate_report(comparison))
```

### Troubleshooting

**Problem: OCR returns empty/wrong results**
- ✓ Try preprocessing: `auto_deskew=True`, `auto_perspective=True`
- ✓ Use intelligent routing: `VISION_PROVIDER=smart`
- ✓ Enable ensemble: `ensemble:voting:kiri,tesseract,gemini`

**Problem: Slow OCR performance**
- ✓ Enable caching: `create_cached_engine(..., persistent=True)`
- ✓ Use faster engine: `tesseract` instead of `gemini`
- ✓ Reduce image size: Resize to 1200px max before OCR

**Problem: Poor accuracy on Khmer text**
- ✓ Use Kiri OCR: `VISION_PROVIDER=kiri`
- ✓ Or Gemini: `VISION_PROVIDER=gemini`
- ✓ Or ensemble: `ensemble:voting:kiri,gemini`

**Problem: Poor accuracy on handwriting**
- ✓ Use Gemini: `VISION_PROVIDER=gemini`
- ✓ Preprocess: `binarization_method="sauvola"`
- ✓ Ensure high image quality (1200px+)

**Problem: Math notation errors**
- ✓ Postprocessing handles most issues automatically
- ✓ Use Mathpix for complex math: `VISION_PROVIDER=mathpix`
- ✓ Or Gemini: `VISION_PROVIDER=gemini`

---

## Configuration Reference

### Complete .env Example

```bash
# OCR Provider Configuration
VISION_PROVIDER=smart                    # Options: stub, tesseract, kiri, gemini, mathpix, google, smart, or ensemble:*

# Intelligent Router (if VISION_PROVIDER=smart)
# No additional config needed - automatically selects best engine

# Ensemble Configuration (if VISION_PROVIDER=ensemble:*)
# Format: ensemble:strategy:provider1,provider2,provider3
# Example: ensemble:voting:kiri,tesseract,gemini

# Kiri OCR (if using kiri or khmer_ocr)
# No config needed - models download automatically

# Tesseract (if using tesseract)
# No config needed - uses system installation

# Gemini Vision (if using gemini or in ensemble)
GEMINI_API_KEY=your_gemini_api_key_here

# Mathpix (if using mathpix or in ensemble)
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key

# Google Cloud Vision (if using google or in ensemble)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Logging
LOG_LEVEL=INFO                           # DEBUG for detailed OCR logs
```

### Provider Quick Reference

| Configuration | Use Case | Cost | Accuracy |
|--------------|----------|------|----------|
| `stub` | Testing without OCR | Free | N/A |
| `tesseract` | Development, simple cases | Free | Good |
| `kiri` | Khmer text (offline) | Free | Excellent (Khmer) |
| `gemini` | Complex math + Khmer | Paid | Excellent |
| `mathpix` | Advanced math notation | Paid | Excellent (Math) |
| `google` | General purpose (cloud) | Paid | Good |
| `smart` | **Production (recommended)** | Mixed | Adaptive |
| `ensemble:voting:*` | Maximum accuracy | Mixed | Highest |
| `ensemble:fallback:*` | Cost-effective fallback | Mixed | Good |

---

## Next Steps

1. **Choose and set up an OCR provider** (start with `smart` for automatic)
2. **Test with sample images** containing Khmer math
3. **Benchmark on your dataset** using evaluation tools
4. **Enable caching** for production deployment
5. **Monitor performance** and adjust configuration as needed
6. **Integrate with Flutter** mobile app camera flow

For questions or issues, refer to the main README.md or the provider's documentation.

## Additional Resources

- **Main Documentation**: `README.md`
- **API Reference**: `docs/API_CONTRACT.md`
- **Code Examples**: `tests/test_vision_*.py`
- **Evaluation Scripts**: `app/core/vision/evaluation.py`
- **Caching Guide**: `app/core/vision/cache.py`

---

**Last Updated**: October 2026
**Version**: 2.0 (Enhanced OCR Capabilities)
