# import json
# import re
# from ollama import chat
# from general import JSON_WRAP_RULE
# from prompts.balance import SYSTEM_PROMPT,USER_PROMPT

# system_prompt =  SYSTEM_PROMPT + JSON_WRAP_RULE

# def save_failed_output(output, filename="failed_output.txt"):
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(output)
#     print(f"Raw output saved to: {filename}")


# response = chat(
#     model='qwen3.5:9b',
#     messages=[
#         {"role": "system", "content": system_prompt},
#         {
#             'role': 'user',
#             'content': USER_PROMPT,
#             'images': [
#                 'C:/Users/ronak.chaturvedi/Documents/ollam/img/7.png',
#             ]
#         }
#     ],
#     think=False,
#     options={"temperature": 0.2,
#              "num_ctx": 16384 
#              }
# )

# result = response.message.content
# match = re.search(r"\{.*\}", result, re.DOTALL)
# if match:
#     try:
#         data = json.loads(match.group())

#         with open("example.json", "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)

#         print("✅ JSON parsed successfully")

#     except json.JSONDecodeError as e:
#         print(f"❌ Invalid JSON: {e}")
#         save_failed_output(result)

# else:
#     print("❌ No JSON found")
#     save_failed_output(result)

import json
import re
import importlib
from ollama import chat
from general import JSON_WRAP_RULE


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

    result = response.message.content
    match = re.search(r"\{.*\}", result, re.DOTALL)
    if match:
        data = json.loads(match.group())
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return output_json_path
    else:
        return None