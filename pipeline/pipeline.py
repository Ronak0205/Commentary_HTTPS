import json
import os
from datetime import date

from config.config import EXTRACTED_IMG_DIR, DATA_DIR, SECTIONS
from services.pdf import extract_page_images
from services.commentary import generate_commentary
from services.summary_commentary import generate_ceo_and_action_commentary

from config.extraction_config import EXTRACTION_CONFIG
from services.pdf_extract import PARSERS, extract_section_data, extract_institution_name, extract_report_date
from pipeline.validate import validate_section, validate_cross_source


class PipelineError(Exception):
    """Raised when a stage of the pipeline fails to produce output."""


def process_pdf(pdf_path, pdf_name, extracted_img_dir=None, data_dir=None):
    extracted_img_dir = extracted_img_dir or EXTRACTED_IMG_DIR
    data_dir = data_dir or DATA_DIR

    os.makedirs(extracted_img_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    pdf_data_dir = os.path.join(data_dir, pdf_name)
    os.makedirs(pdf_data_dir, exist_ok=True)

    section_output_paths = {}
    extracted_payloads = {}
    
    institution_name = extract_institution_name(pdf_path)
    report_date = extract_report_date(pdf_path, page_number=SECTIONS[0]["pages"][0] - 1)
    
    for section in SECTIONS:
        name = section["name"]
        pages = section["pages"]
        page_numbers = [p - 1 for p in pages]

        cfg = EXTRACTION_CONFIG.get(name, {})
        extracted_payload = None

        if cfg.get("extractable"):
            raw = extract_section_data(pdf_path, name, page_numbers)
            validated = validate_section(name, raw)
            if validated:
                extracted_payload = validated

        extracted_payloads[name] = extracted_payload
        if extracted_payload:
              extracted_payload["data"]["institution_name"] = institution_name
              extracted_payload["data"]["report_date"] = report_date
    # ------------------------------------------------------------------
    # Cross-section reconciliation: Shares table total vs Balance Sheet's
    # Shares/Deposits control total. Runs once, here, before any section
    # is written to disk or handed to the model.
    # ------------------------------------------------------------------
    share_extracted = extracted_payloads.get("share")
    balance_extracted = extracted_payloads.get("balance_sheet")

    if share_extracted and balance_extracted:
        control_value = (balance_extracted.get("data", {})
                          .get("shares_deposits", {}) or {}).get("amount")
        other_value = share_extracted.get("data", {}).get("total_shares")

        cross_flag = validate_cross_source(
            control_value=control_value,
            other_value=other_value,
            control_label="Balance Sheet shares/deposits",
            other_label="Shares section total",
        )

        if cross_flag["status"] == "DATA_CHECK":
            # Resolve to the control total and attach the flag so it's
            # visible to whoever reviews this run, and so the commentary
            # generation step below sees the corrected figure, not the
            # unreconciled one.
            share_extracted["data"]["total_shares"] = cross_flag["value"]
            share_extracted.setdefault("flags", []).append(cross_flag)

    # ------------------------------------------------------------------
    # PHASE 2: Generate commentary for each section, now that every
    # extracted_payload (including the cross-source-corrected share data)
    # is finalized.
    # ------------------------------------------------------------------
    for section in SECTIONS:
        name = section["name"]
        pages = section["pages"]
        module = section["module"]
        system_prompt_var = section["system_prompt_var"]
        user_prompt_var = section["user_prompt_var"]

        page_numbers = [p - 1 for p in pages]
        cfg = EXTRACTION_CONFIG.get(name, {})

        extracted_payload = extracted_payloads.get(name)

        needs_image = (not cfg.get("extractable")) or cfg.get("hybrid", False)
        
        if cfg.get("extractable") and not extracted_payload:
          needs_image = True

        img_paths = (
            extract_page_images(pdf_path, extracted_img_dir, f"{pdf_name}_{name}", page_numbers)
            if needs_image else []
        )

        json_path = os.path.join(
            pdf_data_dir,
            f"{pdf_name}_{name}_commentary_{date.today().strftime('%d-%m-%Y_%H-%M-%S')}.json",
        )

        result = generate_commentary(
            img_paths, json_path, module, system_prompt_var, user_prompt_var,
            extracted_data=extracted_payload,
            needs_image=needs_image,
        )

        if not result:
            raise PipelineError(f"[{pdf_name}][{name}] no JSON found, stopping at module: {name}")

        section_output_paths[name] = json_path

    ceo_output, action_output = generate_ceo_and_action_commentary(
        pdf_name, pdf_data_dir, section_output_paths
    )
    if not ceo_output:
        raise PipelineError(f"[{pdf_name}][ceo_report] no JSON found, stopping run")
    if not action_output:
        raise PipelineError(f"[{pdf_name}][action_recommended] no JSON found, stopping run")

    final_output_path = _merge_outputs(
        pdf_name, pdf_data_dir, section_output_paths, ceo_output, action_output
    )

    return {
        "pdf_name": pdf_name,
        "section_output_paths": section_output_paths,
        "ceo_output": ceo_output,
        "action_output": action_output,
        "final_output_path": final_output_path,
    }

def _merge_outputs(pdf_name, pdf_data_dir, section_output_paths, ceo_output, action_output):
    merged = {
        "pdf_name": pdf_name,
        "report_date": date.today().isoformat(),
        "sections": {},
        "ceo_summary": None,
        "action_recommended": None,
    }

    for section_name, path in section_output_paths.items():
        with open(path, "r", encoding="utf-8") as f:
            merged["sections"][section_name] = json.load(f)

    with open(ceo_output, "r", encoding="utf-8") as f:
        merged["ceo_summary"] = json.load(f)

    with open(action_output, "r", encoding="utf-8") as f:
        merged["action_recommended"] = json.load(f)

    final_path = os.path.join(pdf_data_dir, f"{pdf_name}_final_output.json")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)

    return final_path