from pathlib import Path
from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine
from app.ocr.quality import MathOcrQualityPipeline
from app.parser.exercise_parser.exercise_parser import parse_exercise

dir_path = Path("training/test_exercises/limit")
images = sorted(list(dir_path.glob("*.png")) + list(dir_path.glob("*.jpg")))

engine = Pix2TexVisionEngine()
pipeline = MathOcrQualityPipeline(formula_engine=engine)

results = []
for p in images:
    with open(p, "rb") as f:
        b = f.read()
    res = pipeline.process_image(b)
    c = res.selected_candidate
    meta = c.exercise_metadata or {}
    parsed_ex = parse_exercise(c.normalized_math_text or c.raw_ocr_text)

    cond = parsed_ex.condition or (meta.get("condition") if isinstance(meta.get("condition"), str) else (meta.get("condition") or {}).get("normalized_condition"))
    clean_expr = meta.get("primary_expression") or parsed_ex.primary_expression or c.normalized_math_text

    item = {
        "file": p.name,
        "raw": c.raw_ocr_text,
        "clean": clean_expr,
        "label": c.detected_prefix or parsed_ex.exercise_title,
        "condition": cond,
        "intent": parsed_ex.detected_intent,
        "status": c.status.value,
        "score": c.score,
        "issues": c.validation_issues,
    }
    results.append(item)
    print("=" * 60)
    print("FILE:       ", item["file"])
    print("RAW OCR:    ", item["raw"])
    print("CLEAN EXPR: ", item["clean"])
    print("LABEL:      ", item["label"])
    print("CONDITION:  ", item["condition"])
    print("INTENT:     ", item["intent"])
    print(f"STATUS:      {item['status']} (score={item['score']:.2f})")
    if item["issues"]:
        print("ISSUES:     ", item["issues"])

print("\n" + "#" * 60)
verified_count = sum(1 for r in results if r["status"].upper() == "VERIFIED")
print(f"SUMMARY: {verified_count}/{len(results)} VERIFIED")
