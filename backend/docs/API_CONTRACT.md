# Khmer Math Lab — API Contract (v1)

This is the contract the Flutter app builds against. It will grow (new
fields, new endpoints) but existing fields will not be renamed or removed
without bumping the version prefix (`/api/v2/...`).

Base URL (local dev): `http://<your-mac-ip>:8000/api/v1`
Interactive docs (Swagger UI): `http://<your-mac-ip>:8000/docs`

> Use your Mac's LAN IP, not `127.0.0.1`, if the Flutter app runs on a
> physical phone or a different simulator/emulator network namespace.
> Android emulators specifically should use `10.0.2.2` to reach the host
> Mac's `localhost`.

Every endpoint returns the same envelope:

```json
{
  "success": true,
  "data": { "...": "..." },
  "error": null
}
```

On failure, `success` is `false`, `data` is `null`, and `error` is a
human-readable string. **A validation/parsing failure (bad input) is still
an HTTP 200** with `success: false` — only genuine server bugs return a
5xx. Design the Flutter error handling around the `success` field, not the
HTTP status code, except for network-level failures.

---

## `GET /health`

Liveness check.

**Response `data`:**
```json
{ "status": "ok", "app_name": "Khmer Math Lab API", "version": "0.1.0" }
```

---

## `POST /math/solve`

The main endpoint. Send a raw question (Khmer or English); get back the
fully solved, step-by-step, Khmer-explained answer.

**Request:**
```json
{
  "language": "km",
  "question": "ដោះស្រាយ 2x + 5 = 15"
}
```
`language` is `"km"` or `"en"`. It's currently informational — the pipeline
auto-detects Khmer vs. Latin text either way — but send it so the response
can be localized further later (e.g. `description_en` becoming primary for
`"en"`).

**Response `data`:**
```json
{
  "problem_type": "linear_equation",
  "original_question": "ដោះស្រាយ 2x + 5 = 15",
  "detected_intent": "solve_equation",
  "normalized_expression": "Eq(2*x + 5, 15)",
  "variable": "x",
  "answer": "5",
  "is_verified": true,
  "steps": [
    {
      "order": 1,
      "description_km": "សមីការដើម៖",
      "description_en": "Original equation:",
      "expression": "2*x + 5 = 15"
    },
    {
      "order": 2,
      "description_km": "ដក 5 ពីភាគីទាំងពីរ៖",
      "description_en": "Subtract 5 from both sides:",
      "expression": "2*x = 10"
    },
    {
      "order": 3,
      "description_km": "ចែកភាគីទាំងពីរដោយ 2៖",
      "description_en": "Divide both sides by 2:",
      "expression": "x = 5"
    },
    {
      "order": 4,
      "description_km": "ចម្លើយ៖ x = 5",
      "description_en": "Answer: x = 5",
      "expression": "x = 5"
    }
  ]
}
```

**`problem_type` values you may see:**
- ✅ `linear_equation` - Single variable, degree 1 (e.g., 2x + 5 = 15)
- ✅ `quadratic_equation` - Degree 2 with discriminant method (e.g., x² - 5x + 6 = 0)
- ✅ **NEW** `polynomial_equation` - Degree 3+ (cubic, quartic, quintic)
- ✅ **NEW** `linear_inequality` - Inequalities with <, >, ≤, ≥ (e.g., 2x + 5 < 15)
- ✅ `arithmetic_expression` - Pure computation (e.g., 5 + 3 * 2)
- ✅ `algebraic_expression` - Variables but no equation (e.g., 2x + 3y)
- ✅ `numeric_equation` - No variables (e.g., 5 = 5 → true/false)
- ✅ `multivariate_equation` - Multiple variables (future: systems of equations)
- 🔄 `system_of_equations` - Planned: 2x2, 3x3 systems
- ❓ `unknown_equation` - Couldn't classify

All equation types (linear, quadratic, polynomial, inequality) now have **full step-by-step explanations**.
Expressions return computed answers. Design the UI to gracefully render 1 step or many.

**`is_verified`**: always trust this over just displaying `answer` — it
means the answer was substituted back into the original equation and
checked, not just "SymPy said so".

**Failure example** (unrecognized input):
```json
{ "success": false, "data": null, "error": "Could not detect a math request in the given text." }
```

---

## `POST /math/parse`

Same input shape as `/math/solve`, but only normalizes + classifies —
doesn't solve. Useful for an "Is this the equation you meant?" confirmation
screen before committing to solve.

**Response `data`:**
```json
{
  "detected_intent": "solve_equation",
  "raw_expression": "2x+5=15",
  "normalized_expression": "Eq(2*x + 5, 15)",
  "problem_type": "linear_equation"
}
```

---

## `POST /math/vision`

**Now implemented with multiple OCR providers!** Send a `multipart/form-data` request with an `image` file.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@math_problem.jpg"
```

**Configuration:**
Set `VISION_PROVIDER` in `.env` to choose OCR provider:
- `stub` - Default, returns "not implemented" error
- `tesseract` - Free, offline OCR (requires local installation)
- `google` - Google Cloud Vision (best for Khmer, requires credentials)
- `mathpix` - Specialized math OCR (best for complex equations, requires API key)

See `docs/VISION_OCR_SETUP.md` for detailed setup instructions.

**Response `data` (when OCR succeeds):**
```json
{
  "problem_type": "linear_equation",
  "original_question": "2x + 5 = 15",
  "detected_intent": "solve_equation",
  "normalized_expression": "Eq(2*x + 5, 15)",
  "variable": "x",
  "answer": "5",
  "is_verified": true,
  "steps": [ /* same as /math/solve */ ],
  "ocr_detected_text": "2x + 5 = 15",
  "ocr_confidence": 0.95
}
```

**Additional fields:**
- `ocr_detected_text` - Raw text extracted from image
- `ocr_confidence` - OCR confidence score (0.0 to 1.0)

**Failure scenarios:**
1. OCR failed: `{"success": false, "error": "No mathematical text detected in image"}`
2. OCR succeeded but parsing failed: Returns `ocr_detected_text` in data, error explains parsing failure
3. Provider not configured: Returns error message about setup

---

## `GET /math/history` (Enhanced)

**NEW: Supports pagination, filtering, and search!**

Returns solved questions history with advanced filtering options.

**Query Parameters:**
- `limit` - Max entries to return (default: 50, max: 100)
- `offset` - Skip N entries for pagination (default: 0)
- `problem_type` - Filter by type (e.g., "linear_equation", "polynomial_equation")
- `date_from` - Filter entries after this datetime (ISO 8601 format)
- `date_to` - Filter entries before this datetime (ISO 8601 format)
- `search` - Search in question text (case-insensitive)

**Examples:**
```bash
# Get first 10 entries
GET /math/history?limit=10

# Get next 10 entries (pagination)
GET /math/history?limit=10&offset=10

# Filter by problem type
GET /math/history?problem_type=polynomial_equation

# Search for specific content
GET /math/history?search=polynomial

# Date range filter
GET /math/history?date_from=2024-01-01T00:00:00Z&date_to=2024-12-31T23:59:59Z

# Combined filters
GET /math/history?limit=20&problem_type=linear_equation&search=2x
```

**Response `data`:**
```json
{
  "items": [
    {
      "id": 1,
      "question": "ដោះស្រាយ 2x + 5 = 15",
      "problem_type": "linear_equation",
      "normalized_expression": "Eq(2*x + 5, 15)",
      "answer": "5",
      "is_verified": true,
      "steps": [ /* ... */ ],
      "created_at": "2026-09-16T10:00:00+00:00"
    }
    /* ... more items ... */
  ],
  "pagination": {
    "total_count": 150,
    "limit": 50,
    "offset": 0,
    "returned_count": 50,
    "has_more": true
  }
}
```

**Pagination metadata:**
- `total_count` - Total matching entries (considering filters)
- `limit` - Requested limit
- `offset` - Current offset
- `returned_count` - Actual items in this response
- `has_more` - True if more entries available

---

## `GET /math/history/stats` (New)

Get statistics about history entries.

**Response `data`:**
```json
{
  "total_count": 150,
  "by_problem_type": {
    "linear_equation": 50,
    "quadratic_equation": 30,
    "polynomial_equation": 20,
    "arithmetic_expression": 40,
    "linear_inequality": 10
  }
}
```

---

## `DELETE /math/history/{entry_id}` (New)

Delete a specific history entry by ID.

**Response `data`:**
```json
{ "deleted_id": 123 }
```

**Failure (not found):**
```json
{ "success": false, "error": "History entry with ID 123 not found" }
```

---

## `DELETE /math/history` (New)

**WARNING:** Deletes ALL history entries permanently.

**Response `data`:**
```json
{ "deleted_count": 150 }
```

---

## Things that will change without breaking you

- New `problem_type` values as new math topics are added (quadratic
  step-by-step, word problems, geometry, ...).
- New optional fields on `SolveData` (additive only).
- Real answers from `/math/vision` once OCR lands (same response shape).

## Things that won't change silently

- The top-level `{success, data, error}` envelope.
- Existing field names/types on `SolveData` and `SolutionStep`.
- Endpoint paths and methods listed above.
