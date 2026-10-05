# Math OCR API Documentation

## Overview

The Math OCR API provides three endpoints for processing mathematical content from images:

1. **`/api/v1/math/ocr`** - Fast OCR with quality validation (no solving)
2. **`/api/v1/math/vision`** - Complete workflow: OCR → Parse → Solve
3. **`/api/v1/math/vision/batch`** - Multi-problem extraction and structured output

**New in Phase 1**: All endpoints now use the **MathDocumentPipeline** for document-aware processing with automatic fallback to legacy pipeline.

## Architecture

### Processing Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ Image Upload                                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ MathDocumentPipeline (Document-Aware Processing)        │
│  1. Document OCR (Tesseract/Kiri) - Extract layout     │
│  2. Region Classification - Headers, instructions, math │
│  3. Selective Formula OCR - High-quality math regions   │
│  4. Text + Formula Merge - Combine results             │
│  5. Document Structure Parsing - Exercise hierarchy     │
│  6. OCR Quality Validation - Confidence checks          │
│  7. Normalization - Clean expressions                   │
│  8. Context Propagation - Link instructions→problems    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├─ Success ──> Return structured result
                 │
                 └─ Failure/No problems ──> Fallback ─────┐
                                                           │
                                                           ▼
                 ┌─────────────────────────────────────────┐
                 │ Legacy Quality Pipeline (Backward Compat)│
                 │  • Formula-first OCR                     │
                 │  • Quality validation                    │
                 │  • Exercise parsing                      │
                 └──────────────┬──────────────────────────┘
                                │
                                ▼
                          Return result
```

### Fallback Behavior

The document pipeline automatically falls back to the legacy pipeline when:
- Image format cannot be parsed (e.g., corrupted files)
- No text blocks detected by document OCR
- No mathematical problems extracted
- Any processing exception occurs

**Important**: Fallback is transparent to clients - all endpoints return 200 OK with valid responses.

---

## Endpoint Reference

### 1. POST /api/v1/math/ocr

**Purpose**: Fast OCR with quality validation, returns detected math without solving.

**Use Case**: 
- Preview OCR results before solving
- Validate OCR quality
- Extract raw mathematical expressions

#### Request

```http
POST /api/v1/math/ocr HTTP/1.1
Content-Type: multipart/form-data

image: <file>
```

**Parameters:**
- `image` (file, required): Image file (PNG, JPG, JPEG)
  - Max size: 10MB
  - Recommended: 800x600 to 1920x1080 pixels
  - Supported formats: PNG, JPG, JPEG

#### Response

**Success (200 OK)**

```json
{
  "success": true,
  "data": {
    "detected_text": "3x - 9 = 0",
    "expression": "3x-9=0",
    "status": "valid",
    "confidence": 0.95,
    "score": 8.5,
    "suspicious_tokens": [],
    "validation_issues": [],
    "detected_prefix": null,
    "detected_suffix": null,
    "exercise_title": "Exercise 1",
    "instruction": "Solve for x",
    "sub_exercises": [],
    "candidates": [
      {
        "raw_text": "3x - 9 = 0",
        "normalized": "3x-9=0",
        "status": "valid",
        "confidence": 0.95,
        "score": 8.5,
        "variant": "original"
      }
    ]
  },
  "error": null
}
```

**Fields:**
- `detected_text`: Raw OCR output
- `expression`: Normalized mathematical expression
- `status`: One of `valid`, `needs_review`, `invalid`
- `confidence`: OCR confidence score (0.0 to 1.0)
- `score`: Overall quality score
- `suspicious_tokens`: Potentially misrecognized characters
- `validation_issues`: Array of validation warnings
- `exercise_title`: Detected exercise title (if any)
- `instruction`: Detected instruction text (if any)
- `sub_exercises`: Array of sub-problems (a, b, c, etc.)
- `candidates`: Alternative OCR interpretations

**Error Response**

```json
{
  "success": false,
  "data": null,
  "error": "OCR failed: No mathematical text detected"
}
```

---

### 2. POST /api/v1/math/vision

**Purpose**: Complete math vision workflow - OCR → Parse → Solve → Steps

**Use Case**:
- Solve single math problems from images
- Get step-by-step solutions
- Educational applications

#### Request

```http
POST /api/v1/math/vision HTTP/1.1
Content-Type: multipart/form-data

image: <file>
```

**Parameters:**
- `image` (file, required): Image containing math problem

#### Response

**Success - Single Problem (200 OK)**

```json
{
  "success": true,
  "data": {
    "problem_type": "linear_equation",
    "answer": "3",
    "is_verified": true,
    "steps": [
      {
        "step_number": 1,
        "operation": "simplify",
        "description": "Simplify the equation",
        "expression": "3x - 9 = 0",
        "result": "3x = 9"
      },
      {
        "step_number": 2,
        "operation": "divide",
        "description": "Divide both sides by 3",
        "expression": "3x = 9",
        "result": "x = 3"
      }
    ],
    "ocr_detected_text": "3x - 9 = 0",
    "ocr_confidence": 0.95,
    "ocr_status": "success",
    "exercise_title": "Exercise 1",
    "instruction": "Solve for x",
    "cleaned_math_expression": "3x-9=0",
    "document_structure": {
      "sections": 1,
      "total_problems": 1
    },
    "warnings": [],
    "processing_time": 0.45
  },
  "error": null
}
```

**Success - Multiple Problems Detected (200 OK)**

When the document pipeline detects multiple problems, it returns structure information:

```json
{
  "success": true,
  "data": {
    "exercise": {
      "title": "លំហាត់ទី 1",
      "sections": [
        {
          "section_number": 1,
          "instruction": {
            "text": "រកចម្លើយ",
            "type": "solve"
          },
          "problems": [
            {
              "problem": {
                "problem_id": "uuid-1",
                "raw_input": "2x + 4 = 12"
              }
            },
            {
              "problem": {
                "problem_id": "uuid-2",
                "raw_input": "3x - 9 = 0"
              }
            }
          ]
        }
      ],
      "total_problems": 2
    },
    "status": "success",
    "warnings": [],
    "message": "Detected 2 problems. Use /math/vision/batch for multi-problem solving."
  },
  "error": null
}
```

**New Fields (Phase 1)**:
- `document_structure`: Section and problem count from document pipeline
- `warnings`: Array of processing warnings
- `processing_time`: Total pipeline execution time (seconds)
- `message`: Guidance message when multiple problems detected

**Error Response - OCR Failed**

```json
{
  "success": false,
  "data": null,
  "error": "No mathematical text detected in image"
}
```

**Error Response - Parsing Failed**

```json
{
  "success": false,
  "data": {
    "ocr_detected_text": "invalid text ~~~",
    "ocr_confidence": 0.45,
    "ocr_status": "invalid",
    "exercise_title": null,
    "instruction": null,
    "cleaned_math_expression": null
  },
  "error": "OCR detected 'invalid text ~~~' but failed to solve: Invalid mathematical syntax"
}
```

---

### 3. POST /api/v1/math/vision/batch

**Purpose**: Extract and structure multiple problems from a single image

**Use Case**:
- Process worksheets with multiple exercises
- Batch problem extraction
- Structured problem sets

#### Request

```http
POST /api/v1/math/vision/batch HTTP/1.1
Content-Type: multipart/form-data

image: <file>
```

**Parameters:**
- `image` (file, required): Image containing multiple problems

#### Response

**Success (200 OK)**

```json
{
  "success": true,
  "data": {
    "exercise_title": "លំហាត់ទី 1",
    "instruction": "រកចម្លើយ",
    "problems": [
      {
        "problem_id": "550e8400-e29b-41d4-a716-446655440000",
        "source": "ocr",
        "language": "km",
        "raw_input": "2x + 4 = 12",
        "ocr_confidence": 0.92,
        "metadata": {
          "sub_exercise_label": "ក",
          "sub_exercise_raw_text": "ក. 2x + 4 = 12",
          "detected_intent": "solve_equation"
        },
        "warnings": []
      },
      {
        "problem_id": "550e8400-e29b-41d4-a716-446655440001",
        "source": "ocr",
        "language": "km",
        "raw_input": "3x - 9 = 0",
        "ocr_confidence": 0.89,
        "metadata": {
          "sub_exercise_label": "ខ",
          "sub_exercise_raw_text": "ខ. 3x - 9 = 0",
          "detected_intent": "solve_equation"
        },
        "warnings": []
      }
    ],
    "problem_count": 2,
    "source_metadata": {
      "ocr_engine": "MathDocumentPipeline",
      "ocr_confidence": 0.905,
      "processing_status": "success",
      "sections": 1,
      "processing_time": 1.23
    }
  },
  "error": null
}
```

**New Fields (Phase 1)**:
- `source_metadata.ocr_engine`: Always "MathDocumentPipeline" (or legacy engine name)
- `source_metadata.processing_status`: `success`, `partial`, `needs_review`, or `failed`
- `source_metadata.sections`: Number of document sections detected
- `source_metadata.processing_time`: Pipeline execution time

**Error Response**

```json
{
  "success": false,
  "data": null,
  "error": "OCR detected text but could not extract any mathematical expressions"
}
```

---

## Processing Status Codes

The document pipeline returns one of four status codes:

| Status | Meaning | Action |
|--------|---------|--------|
| `success` | All stages completed successfully | Use results as-is |
| `partial` | Some problems extracted, some failed | Review warnings, use valid problems |
| `needs_review` | Low OCR confidence or validation issues | Manual review recommended |
| `failed` | No problems extracted or critical error | Falls back to legacy pipeline |

---

## Error Handling

### Client-Side Error Handling

```javascript
const formData = new FormData();
formData.append('image', imageFile);

try {
  const response = await fetch('/api/v1/math/vision', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.success) {
    // Check for multiple problems
    if (result.data.message && result.data.message.includes('Use /math/vision/batch')) {
      console.log('Multiple problems detected, use batch endpoint');
      // Redirect to batch processing
    } else {
      // Single problem solved
      displaySolution(result.data);
    }
  } else {
    // Handle error
    console.error(result.error);
    displayError(result.error);
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### Common Error Scenarios

1. **No Text Detected**
   - **Cause**: Blank image, pure whitespace, or unrecognizable content
   - **Response**: `{ "success": false, "error": "No mathematical text detected" }`
   - **Recommendation**: Ask user to capture clearer image

2. **Low OCR Confidence**
   - **Cause**: Blurry image, poor lighting, handwriting
   - **Response**: `{ "success": true, "data": {..., "ocr_status": "needs_review", "warnings": [...]} }`
   - **Recommendation**: Display confidence warning, allow user to retry

3. **Invalid Mathematical Syntax**
   - **Cause**: OCR misrecognition, non-mathematical text
   - **Response**: `{ "success": false, "error": "Invalid mathematical syntax", "data": {...} }`
   - **Recommendation**: Show detected text, allow manual correction

4. **Unsupported Problem Type**
   - **Cause**: Advanced math beyond solver capabilities
   - **Response**: `{ "success": false, "error": "Problem type not supported" }`
   - **Recommendation**: Inform user of supported types

---

## Best Practices

### Image Quality

**Recommended**:
- ✅ Clear, well-lit images
- ✅ High contrast (dark text on light background)
- ✅ Straight-on angle (minimal perspective distortion)
- ✅ Resolution: 800x600 to 1920x1080 pixels
- ✅ Format: PNG or JPG

**Avoid**:
- ❌ Blurry or out-of-focus images
- ❌ Extreme angles or rotations
- ❌ Low contrast or poor lighting
- ❌ Images smaller than 400x300 pixels
- ❌ Images larger than 4000x4000 pixels (slow processing)

### Performance Optimization

1. **Resize large images client-side** before upload
   ```javascript
   // Resize to max 1920x1080 before upload
   const maxWidth = 1920;
   const maxHeight = 1080;
   ```

2. **Use `/math/ocr` for preview** before solving
   - Faster than full `/math/vision` endpoint
   - Validate OCR quality first
   - Solve only if confidence is acceptable

3. **Cache results** by image hash
   - Avoid re-processing same image
   - Store OCR results locally

### Multi-Problem Workflows

**Recommended Flow**:
1. User uploads image
2. Call `/math/vision`
3. If response contains `message` about multiple problems:
   - Call `/math/vision/batch` to get structured problems
   - Display problem list to user
   - Solve each problem individually via `/math/solve` endpoint

**Example**:
```javascript
// Step 1: Initial detection
const visionResult = await callVisionAPI(image);

if (visionResult.data.exercise && visionResult.data.exercise.total_problems > 1) {
  // Step 2: Get structured problems
  const batchResult = await callBatchAPI(image);
  
  // Step 3: Solve each problem
  for (const problem of batchResult.data.problems) {
    const solution = await solveProblem(problem.problem_id);
    displaySolution(solution);
  }
}
```

---

## Rate Limiting

- **Rate limit**: 100 requests per minute per IP
- **Burst**: Up to 10 concurrent requests
- **Headers**:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**429 Too Many Requests Response**:
```json
{
  "success": false,
  "error": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Supported Problem Types

The solver supports:
- ✅ Linear equations: `2x + 3 = 7`
- ✅ Quadratic equations: `x^2 - 5x + 6 = 0`
- ✅ Systems of equations: `2x + y = 5; x - y = 1`
- ✅ Polynomial simplification: `(x+2)(x-3)`
- ✅ Inequalities: `2x + 3 > 7`
- ✅ Factoring: `x^2 - 9`

**Coming soon**:
- 🔜 Calculus (derivatives, integrals)
- 🔜 Trigonometry
- 🔜 Matrices

---

## Changelog

### Phase 1 (2026-10-05)

**New Features**:
- ✨ Document-aware processing pipeline
- ✨ Automatic section and problem detection
- ✨ Multi-problem extraction from single image
- ✨ Context propagation (instructions → problems)
- ✨ Graceful fallback to legacy pipeline

**Improvements**:
- 📈 Better handling of mixed Khmer/English text
- 📈 Improved OCR confidence tracking
- 📈 Enhanced error messages with processing status
- 📈 Processing time metrics

**Breaking Changes**:
- None - Full backward compatibility maintained

---

## Support

For issues or questions:
- **Documentation**: https://github.com/your-org/math-ocr/wiki
- **Issues**: https://github.com/your-org/math-ocr/issues
- **Email**: support@example.com

---

## Testing

### cURL Examples

**Test OCR endpoint**:
```bash
curl -X POST http://localhost:8000/api/v1/math/ocr \
  -F "image=@test_image.png"
```

**Test Vision endpoint**:
```bash
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@test_image.png"
```

**Test Batch endpoint**:
```bash
curl -X POST http://localhost:8000/api/v1/math/vision/batch \
  -F "image=@worksheet.png"
```

### Python Example

```python
import requests

with open('math_problem.png', 'rb') as f:
    files = {'image': f}
    response = requests.post(
        'http://localhost:8000/api/v1/math/vision',
        files=files
    )
    
result = response.json()
if result['success']:
    print(f"Answer: {result['data']['answer']}")
    print(f"Steps: {len(result['data']['steps'])}")
else:
    print(f"Error: {result['error']}")
```
