import json
import os
from datetime import date
from pipeline.guardrails import apply_guardrails
from config.config import EXTRACTED_IMG_DIR, DATA_DIR, SECTIONS
from services.pdf import extract_page_images
from services.commentary import generate_commentary
from services.summary_commentary import generate_ceo_and_action_commentary
from services.earning_segment_extract import extract_earning_segments
from config.extraction_config import EXTRACTION_CONFIG
from services.pdf_extract import PARSERS, extract_section_data, extract_institution_name, extract_report_date
from pipeline.validate import validate_section


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

    # ------------------------------------------------------------------
    # PHASE 1: per-section deterministic extraction + validation.
    # ------------------------------------------------------------------
    for section in SECTIONS:
        name = section["name"]
        pages = section["pages"]
        page_numbers = [p - 1 for p in pages]

        cfg = EXTRACTION_CONFIG.get(name, {})
        extracted_payload = None

        if cfg.get("extractable"):
            raw = extract_section_data(pdf_path, name, page_numbers)
            validated = validate_section(name, raw)
            if name == "earning" and raw is not None:
                earning_img_paths = extract_page_images(
                    pdf_path, extracted_img_dir, f"{pdf_name}_{name}_segments", page_numbers
                )
                segment_data = extract_earning_segments(earning_img_paths)
                if segment_data:
                    raw["non_interest_income_segments"] = segment_data["non_interest_income_segments"]
                    raw["non_interest_expense_segments"] = segment_data["non_interest_expense_segments"]

            validated = validate_section(name, raw)
            if validated:
                extracted_payload = validated

        extracted_payloads[name] = extracted_payload
        if extracted_payload:
            extracted_payload["data"]["institution_name"] = institution_name
            extracted_payload["data"]["report_date"] = report_date
            if validated:
                extracted_payload = validated

    # ------------------------------------------------------------------
    # PHASE 1.5: cross-source conflict guardrails. Runs once, here,
    # before any section is written to disk or handed to the model.
    # Supersedes the old inline Shares-vs-Balance-Sheet check (which only
    # reconciled the dollar total, not the paired % change) -- do not
    # re-add that block alongside this one, the two would silently mask
    # each other depending on execution order.
    # ------------------------------------------------------------------
    context = {
        "balance_sheet": (extracted_payloads.get("balance_sheet") or {}).get("data"),
        # "external_non_interest_expense": <wire this up once/if a second
        #  source document is ever ingested -- omitted entirely today>
    }

    blocked_sections = set()
    for section in SECTIONS:
        name = section["name"]
        payload = extracted_payloads.get(name)
        if not payload:
            continue
        payload["data"], guard_flags, blocked = apply_guardrails(
            name, payload["data"], context=context
        )
        payload.setdefault("flags", []).extend(guard_flags)
        if blocked:
            blocked_sections.add(name)
            print(f"[BLOCKED] {name}: unresolved cross-source conflict, requires manual confirmation")

    # ------------------------------------------------------------------
    # PHASE 2: generate commentary for each section, now that every
    # extracted_payload (including any guardrail-corrected data) is
    # finalized. Blocked sections are skipped entirely -- no commentary
    # is generated until a human resolves the conflict.
    # ------------------------------------------------------------------
    for section in SECTIONS:
        name = section["name"]
        if name in blocked_sections:
            continue

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