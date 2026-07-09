import json
import importlib
import re
from prompts.general import JSON_WRAP_RULE, EXTRACTED_DATA_RULE, DATA_CHECK_CONTAINMENT_RULE
from client.ollama_client import chat

def generate_commentary(image_paths, output_json_path, module, system_prompt_var,
                         user_prompt_var, extracted_data=None, needs_image=True):
    prompt_module = importlib.import_module(f"prompts.{module}")
    system_prompt_text = getattr(prompt_module, system_prompt_var)
    user_prompt_text = getattr(prompt_module, user_prompt_var)

    system_prompt = system_prompt_text + JSON_WRAP_RULE + DATA_CHECK_CONTAINMENT_RULE
    user_content = user_prompt_text

    if extracted_data:
        system_prompt = system_prompt_text + EXTRACTED_DATA_RULE + JSON_WRAP_RULE + DATA_CHECK_CONTAINMENT_RULE
        user_content += (
            "\n\nValidated extracted data for this section (authoritative for "
            "all numbers):\n" + json.dumps(extracted_data, indent=2, ensure_ascii=False)
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