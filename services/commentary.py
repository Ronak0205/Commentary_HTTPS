import json
import importlib
import re
from prompts.general import BENCHMARK_TONE_RULE, JSON_WRAP_RULE, EXTRACTED_DATA_RULE, DATA_CHECK_CONTAINMENT_RULE, NUMERIC_INTEGRITY_RULE
from client.ollama_client import chat

# Keys that exist purely for internal pipeline bookkeeping / developer
# debugging and must NEVER be serialized into the model's context. These
# fields contain phrasing like "chart callout", "JSON payload", "not in
# this payload", etc. -- language the model has previously echoed
# verbatim into board-facing commentary once it saw it in context.
# Anything pipeline-internal gets added here, not passed through raw.
_PIPELINE_INTERNAL_KEYS = {"note", "raw_rows"}


def _sanitize_extracted_data(extracted_data):
    """Return a copy of extracted_data with pipeline-internal keys removed,
    recursively (in case a nested dict/list also carries a 'note' field)."""
    if isinstance(extracted_data, dict):
        return {
            k: _sanitize_extracted_data(v)
            for k, v in extracted_data.items()
            if k not in _PIPELINE_INTERNAL_KEYS
        }
    if isinstance(extracted_data, list):
        return [_sanitize_extracted_data(v) for v in extracted_data]
    return extracted_data


def generate_commentary(image_paths, output_json_path, module, system_prompt_var,
                         user_prompt_var, extracted_data=None, needs_image=True):
    prompt_module = importlib.import_module(f"prompts.{module}")
    system_prompt_text = getattr(prompt_module, system_prompt_var)
    user_prompt_text = getattr(prompt_module, user_prompt_var)

    system_prompt = system_prompt_text + JSON_WRAP_RULE + DATA_CHECK_CONTAINMENT_RULE + BENCHMARK_TONE_RULE + NUMERIC_INTEGRITY_RULE
    user_content = user_prompt_text

    if extracted_data:
        safe_extracted_data = _sanitize_extracted_data(extracted_data)
        system_prompt = system_prompt_text + EXTRACTED_DATA_RULE + JSON_WRAP_RULE + DATA_CHECK_CONTAINMENT_RULE + BENCHMARK_TONE_RULE + NUMERIC_INTEGRITY_RULE
        user_content += (
            "\n\nValidated extracted data for this section (authoritative for "
            "all numbers):\n" + json.dumps(safe_extracted_data, indent=2, ensure_ascii=False)
        )

    message = {"role": "user", "content": user_content}
    if needs_image and image_paths:
        message["images"] = image_paths
    response = chat(model='qwen3.5:9b', messages=[
        {"role": "system", "content": system_prompt}, message,
    ],
        think=False,
        options={"temperature": 0.2, "num_ctx": 16384},
    )

    result = response["message"]["content"]
    match = re.search(r"\{.*\}", result, re.DOTALL)
    if match:
        raw_json = match.group()
        data = json.loads(raw_json, strict=False)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return output_json_path
    else:
        return None