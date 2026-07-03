
# import json
# import re
# import importlib
# from ollama_client import chat
# from general import JSON_WRAP_RULE


# def generate_commentary(image_paths, output_json_path, module, system_prompt_var, user_prompt_var):
#     prompt_module = importlib.import_module(f"prompts_v1.{module}")
#     system_prompt_text = getattr(prompt_module, system_prompt_var)
#     user_prompt_text = getattr(prompt_module, user_prompt_var)

#     system_prompt = system_prompt_text + JSON_WRAP_RULE

#     response = chat(
#         model='qwen3.5:9b',
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 'role': 'user',
#                 'content': user_prompt_text,
#                 'images': image_paths
#             }
#         ],
#         think=False,
#         options={
#             "temperature": 0.2,
#             "num_ctx": 16384 
#         }
#     )

#     result = response["message"]["content"]
#     match = re.search(r"\{.*\}", result, re.DOTALL)
#     if match:
#         data = json.loads(match.group())
#         with open(output_json_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         return output_json_path
#     else:
#         return None

import json
import re
import importlib
from client.ollama_client import chat
from prompts.general import JSON_WRAP_RULE


def generate_commentary(image_paths, output_json_path, module, system_prompt_var, user_prompt_var):
    prompt_module = importlib.import_module(f"prompts.{module}")
    system_prompt_text = getattr(prompt_module, system_prompt_var)
    user_prompt_text = getattr(prompt_module, user_prompt_var)

    system_prompt = system_prompt_text + JSON_WRAP_RULE

    response = chat(
        model='qwen3.5:9b',
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                'role': 'user',
                'content': user_prompt_text,
                'images': image_paths
            }
        ],
        think=False,
        options={
            "temperature": 0.2,
            "num_ctx": 16384
        }
    )

    result = response["message"]["content"]
    match = re.search(r"\{.*\}", result, re.DOTALL)
    if match:
        data = json.loads(match.group())
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return output_json_path
    else:
        return None