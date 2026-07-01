import json
import os
import re
import importlib
from datetime import date

from ollama import chat

from general import JSON_WRAP_RULE


def _load_commentary_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_json_from_response(raw_text):
    candidates = []

    fenced = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.append(fenced.group(1))

    first_last = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if first_last:
        candidates.append(first_last.group())

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Tolerate common model mistake: trailing commas before ] or }.
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    return None


def _build_user_prompt(prompt_template, payload_obj):
    payload_text = json.dumps(payload_obj, indent=2, ensure_ascii=False)
    return prompt_template.format(all_sections_json=payload_text)


def _generate_from_prompt(module_name, user_payload, output_json_path):
    prompt_module = importlib.import_module(f"prompts.{module_name}")
    system_prompt = getattr(prompt_module, "SYSTEM_PROMPT") + JSON_WRAP_RULE
    user_prompt_template = getattr(prompt_module, "USER_PROMPT")
    user_prompt = _build_user_prompt(user_prompt_template, user_payload)

    response = chat(
        model="qwen3.5:9b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        think=False,
        options={"temperature": 0.2, "num_ctx": 16384},
    )

    raw_output = response.message.content
    parsed = _extract_json_from_response(raw_output)
    if not parsed:
        failed_path = os.path.join(
            os.path.dirname(output_json_path),
            f"failed_{module_name}_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.txt",
        )
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(raw_output)
        return None

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=4, ensure_ascii=False)

    return output_json_path


def generate_ceo_and_action_commentary(pdf_name, pdf_data_dir, section_output_paths):
    section_payload = {
        "report_date": date.today().isoformat(),
        "pdf_name": pdf_name,
        "sections": {},
    }

    for section_name, path in section_output_paths.items():
        section_payload["sections"][section_name] = _load_commentary_file(path)

    ceo_output_path = os.path.join(
        pdf_data_dir,
        f"{pdf_name}_ceo_report_commentary_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.json",
    )
    ceo_result = _generate_from_prompt("ceo_report", section_payload, ceo_output_path)
    if not ceo_result:
        return None, None

    action_payload = {
        "report_date": section_payload["report_date"],
        "pdf_name": pdf_name,
        "sections": section_payload["sections"],
        "ceo_summary": _load_commentary_file(ceo_result),
    }

    action_output_path = os.path.join(
        pdf_data_dir,
        f"{pdf_name}_action_recommended_commentary_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.json",
    )
    action_result = _generate_from_prompt(
        "action_recommended", action_payload, action_output_path
    )
    if not action_result:
        return ceo_result, None

    return ceo_result, action_result