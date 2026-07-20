import os
import json
from datetime import date
from services.clean_section_data import clean_section
from config.config import EXTRACTED_IMG_DIR, DATA_DIR, SECTIONS
from config.extraction_config import EXTRACTION_CONFIG
from services.pdf import extract_page_images
from services.commentary import generate_commentary
from services.pdf_extract import extract_institution_name, extract_report_date

# ============================================================
# HARDCODE WHAT YOU'RE TESTING HERE. Change and re-run.
# ============================================================
SECTION_NAME = "earning"
PDF_PATH = "pdf/BOPTI_Board_Report_May26.pdf"
PDF_NAME = "BOPTI_Board_Report_May26"

# Where parser.py writes its per-section JSON (output/json/<section>.json).
# Run inspect_extraction.py against this PDF, then parser.py against the
# resulting inspection report, BEFORE running this file -- there is no
# staleness check here, so if the PDF changed since your last parser.py
# run, this will silently hand the model last run's numbers.
PARSED_JSON_DIR = "output/json"
# ============================================================


def _load_parsed_section_json(section_name, json_dir=PARSED_JSON_DIR):
    path = os.path.join(json_dir, f"{section_name}.json")
    if not os.path.isfile(path):
        print(f"[warn] no parsed JSON found at {path} -- run parser.py first")
        return None

    with open(path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    cleaned = clean_section(parsed)          # <-- new
    if not cleaned["data"]:
        return None

    return {"status": cleaned["status"], "data": cleaned["data"],
            "flags": [{"reason": r} for r in cleaned["flags"]]}


def run_single_section(section_name=SECTION_NAME, pdf_path=PDF_PATH, pdf_name=PDF_NAME):
    section = next((s for s in SECTIONS if s["name"] == section_name), None)
    if not section:
        raise ValueError(f"'{section_name}' not found in SECTIONS (config.py)")

    pages = section["pages"]
    module = section["module"]
    system_prompt_var = section["system_prompt_var"]
    user_prompt_var = section["user_prompt_var"]
    page_numbers = [p - 1 for p in pages]

    os.makedirs(EXTRACTED_IMG_DIR, exist_ok=True)
    pdf_data_dir = os.path.join(DATA_DIR, pdf_name)
    os.makedirs(pdf_data_dir, exist_ok=True)

    institution_name = extract_institution_name(pdf_path)
    report_date = extract_report_date(pdf_path, page_number=SECTIONS[0]["pages"][0] - 1)

    cfg = EXTRACTION_CONFIG.get(section_name, {})
    extracted_payload = None

    if cfg.get("extractable"):
        # Data source swap: pull from parser.py's already-generated JSON
        # (output/json/<section>.json) instead of re-running
        # extract_section_data()/validate_section() live against the PDF.
        validated = _load_parsed_section_json(section_name)
        if validated:
            extracted_payload = validated
            extracted_payload["data"]["institution_name"] = institution_name
            extracted_payload["data"]["report_date"] = report_date

            print("--- EXTRACTED / VALIDATED DATA (from parser.py output) ---")
            print(extracted_payload)
            print()

    # Unchanged: hybrid sections still get both the JSON above *and* the
    # page image, for chart/donut-only figures the code extraction can't
    # reach. Non-hybrid extractable sections stay JSON-only. Membership
    # (not extractable) stays image-only. Only extracted_payload's SOURCE
    # changed above -- this logic is identical to the live-extraction
    # version.
    needs_image = (not cfg.get("extractable")) or cfg.get("hybrid", False)
    if cfg.get("extractable") and not extracted_payload:
        needs_image = True

    img_paths = (
        extract_page_images(
            pdf_path, EXTRACTED_IMG_DIR, f"{pdf_name}_{section_name}_TEST", page_numbers
        )
        if needs_image
        else []
    )

    json_path = os.path.join(
        pdf_data_dir,
        f"{pdf_name}_{section_name}_TEST_{date.today().strftime('%d-%m-%Y_%H-%M-%S')}.json",
    )

    result = generate_commentary(
        img_paths,
        json_path,
        module,
        system_prompt_var,
        user_prompt_var,
        extracted_data=extracted_payload,
        needs_image=needs_image,
    )

    if not result:
        print(f"[FAILED] no JSON parsed for section: {section_name}")
        return None

    print(f"[OK] {section_name} commentary saved: {result}")
    if extracted_payload and extracted_payload.get("flags"):
        print("flags:")
        for f in extracted_payload["flags"]:
            print(f"  - {f.get('reason', f)}")

    with open(result, "r", encoding="utf-8") as f:
        print("\n--- COMMENTARY OUTPUT ---")
        print(f.read())

    return result


if __name__ == "__main__":
    run_single_section()