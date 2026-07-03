

import json
import os
from datetime import date

from config import EXTRACTED_IMG_DIR, DATA_DIR, SECTIONS
from services.pdf import extract_page_images
from services.commentary import generate_commentary
from services.summary_commentary import generate_ceo_and_action_commentary


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

    for section in SECTIONS:
        name = section["name"]
        pages = section["pages"]
        module = section["module"]
        system_prompt_var = section["system_prompt_var"]
        user_prompt_var = section["user_prompt_var"]

        page_numbers = [p - 1 for p in pages]

        img_paths = extract_page_images(
            pdf_path, extracted_img_dir, f"{pdf_name}_{name}", page_numbers
        )

        json_path = os.path.join(
            pdf_data_dir,
            f"{pdf_name}_{name}_commentary_{date.today().strftime('%d-%m-%Y_%H-%M-%S')}.json",
        )

        result = generate_commentary(
            img_paths, json_path, module, system_prompt_var, user_prompt_var
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