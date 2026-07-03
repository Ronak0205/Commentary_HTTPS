# import json
# import os
# import re
# import importlib
# from datetime import date
# from ollama_client import chat
# from general import JSON_WRAP_RULE


# def _load_commentary_file(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)


# def _load_json_with_cleanup(candidate):
#     try:
#         return json.loads(candidate)
#     except json.JSONDecodeError:
#         # Tolerate common model mistake: trailing commas before ] or }.
#         cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
#         try:
#             return json.loads(cleaned)
#         except json.JSONDecodeError:
#             return None


# def _salvage_title_content_json(raw_text):
#     """
#     Recover a minimal valid payload when the model breaks JSON by splitting
#     "content" into multiple quoted chunks outside the object.
#     """
#     title_match = re.search(
#         r'"title"\s*:\s*("(?:\\.|[^"\\])*")', raw_text, re.DOTALL
#     )
#     content_match = re.search(
#         r'"content"\s*:\s*("(?:\\.|[^"\\])*")', raw_text, re.DOTALL
#     )
#     if not title_match or not content_match:
#         return None

#     try:
#         title = json.loads(title_match.group(1))
#         first_content_chunk = json.loads(content_match.group(1))
#     except json.JSONDecodeError:
#         return None

#     tail = raw_text[content_match.end() :]

#     extra_chunks = []
#     for token in re.findall(r'("(?:\\.|[^"\\])*")', tail, re.DOTALL):
#         try:
#             decoded = json.loads(token).strip()
#         except json.JSONDecodeError:
#             continue
#         if decoded:
#             extra_chunks.append(decoded)

#     trailing_bullets = []
#     for line in tail.splitlines():
#         stripped = line.strip()
#         if stripped.startswith("- "):
#             trailing_bullets.append(stripped.rstrip('"').strip())

#     content_parts = [first_content_chunk.strip()]
#     content_parts.extend(extra_chunks)
#     content_parts.extend(trailing_bullets)

#     merged_content = "\n\n".join([part for part in content_parts if part])
#     if not merged_content:
#         return None

#     return {"title": title, "content": merged_content}


# def _extract_json_from_response(raw_text):
#     candidates = []

#     fenced = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL | re.IGNORECASE)
#     if fenced:
#         candidates.append(fenced.group(1))

#     first_last = re.search(r"\{.*\}", raw_text, re.DOTALL)
#     if first_last:
#         candidates.append(first_last.group())

#     for candidate in candidates:
#         parsed = _load_json_with_cleanup(candidate)
#         if parsed is not None:
#             return parsed

#     salvaged = _salvage_title_content_json(raw_text)
#     if salvaged is not None:
#         return salvaged

#     return None


# def _build_user_prompt(prompt_template, payload_obj):
#     payload_text = json.dumps(payload_obj, indent=2, ensure_ascii=False)
#     return prompt_template.format(all_sections_json=payload_text)


# def _generate_from_prompt(module_name, user_payload, output_json_path):
#     prompt_module = importlib.import_module(f"prompts.{module_name}")
#     system_prompt = getattr(prompt_module, "SYSTEM_PROMPT") + JSON_WRAP_RULE
#     user_prompt_template = getattr(prompt_module, "USER_PROMPT")
#     user_prompt = _build_user_prompt(user_prompt_template, user_payload)

#     response = chat(
#         model="qwen3.5:9b",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         think=False,
#         options={"temperature": 0.2, "num_ctx": 16384},
#     )

#     raw_output = response.message.content
#     parsed = _extract_json_from_response(raw_output)
#     if parsed and (
#         not isinstance(parsed, dict)
#         or "title" not in parsed
#         or "content" not in parsed
#     ):
#         parsed = None

#     if not parsed:
#         failed_path = os.path.join(
#             os.path.dirname(output_json_path),
#             f"failed_{module_name}_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.txt",
#         )
#         with open(failed_path, "w", encoding="utf-8") as f:
#             f.write(raw_output)
#         return None

#     with open(output_json_path, "w", encoding="utf-8") as f:
#         json.dump(parsed, f, indent=4, ensure_ascii=False)

#     return output_json_path


# def generate_ceo_and_action_commentary(pdf_name, pdf_data_dir, section_output_paths):
#     section_payload = {
#         "report_date": date.today().isoformat(),
#         "pdf_name": pdf_name,
#         "sections": {},
#     }

#     for section_name, path in section_output_paths.items():
#         section_payload["sections"][section_name] = _load_commentary_file(path)

#     ceo_output_path = os.path.join(
#         pdf_data_dir,
#         f"{pdf_name}_ceo_report_commentary_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.json",
#     )
#     ceo_result = _generate_from_prompt("ceo_report", section_payload, ceo_output_path)
#     if not ceo_result:
#         return None, None

#     action_payload = {
#         "report_date": section_payload["report_date"],
#         "pdf_name": pdf_name,
#         "sections": section_payload["sections"],
#         "ceo_summary": _load_commentary_file(ceo_result),
#     }

#     action_output_path = os.path.join(
#         pdf_data_dir,
#         f"{pdf_name}_action_recommended_commentary_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.json",
#     )
#     action_result = _generate_from_prompt(
#         "action_recommended", action_payload, action_output_path
#     )
#     if not action_result:
#         return ceo_result, None

#     return ceo_result, action_result

import json
import os
import re
import importlib
from datetime import date
from client.ollama_client import chat
from prompts.general import JSON_WRAP_RULE


def _load_commentary_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_json_with_cleanup(candidate):
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None


def _salvage_title_content_json(raw_text):
    """
    Recover a minimal valid payload when the model breaks JSON by splitting
    "content" into multiple quoted chunks outside the object.
    """
    title_match = re.search(
        r'"title"\s*:\s*("(?:\\.|[^"\\])*")', raw_text, re.DOTALL
    )
    content_match = re.search(
        r'"content"\s*:\s*("(?:\\.|[^"\\])*")', raw_text, re.DOTALL
    )
    if not title_match or not content_match:
        return None

    try:
        title = json.loads(title_match.group(1))
        first_content_chunk = json.loads(content_match.group(1))
    except json.JSONDecodeError:
        return None

    tail = raw_text[content_match.end():]

    extra_chunks = []
    for token in re.findall(r'("(?:\\.|[^"\\])*")', tail, re.DOTALL):
        try:
            decoded = json.loads(token).strip()
        except json.JSONDecodeError:
            continue
        if decoded:
            extra_chunks.append(decoded)

    trailing_bullets = []
    for line in tail.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            trailing_bullets.append(stripped.rstrip('"').strip())

    content_parts = [first_content_chunk.strip()]
    content_parts.extend(extra_chunks)
    content_parts.extend(trailing_bullets)

    merged_content = "\n\n".join([part for part in content_parts if part])
    if not merged_content:
        return None

    return {"title": title, "content": merged_content}


def _extract_json_from_response(raw_text):
    candidates = []

    fenced = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.append(fenced.group(1))

    first_last = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if first_last:
        candidates.append(first_last.group())

    for candidate in candidates:
        parsed = _load_json_with_cleanup(candidate)
        if parsed is not None:
            return parsed

    salvaged = _salvage_title_content_json(raw_text)
    if salvaged is not None:
        return salvaged

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

    raw_output = response["message"]["content"]
    parsed = _extract_json_from_response(raw_output)
    if parsed and (
        not isinstance(parsed, dict)
        or "title" not in parsed
        or "content" not in parsed
    ):
        parsed = None

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