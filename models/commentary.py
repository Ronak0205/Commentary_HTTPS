import json
import re
from ollama import chat
from general import JSON_WRAP_RULE
# from prompts.loan import SYSTEM_PROMPT,USER_PROMPT

# system_prompt =  SYSTEM_PROMPT + JSON_WRAP_RULE

def save_failed_output(output, filename="failed_output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Raw output saved to: {filename}")


response = chat(
    model='qwen3.5:9b',
    messages=[
        {"role": "system", "content": "understand both graph properly and extract the values carefully"},
        {
            'role': 'user',
            'content': 'generate insight from the graph ',
            'images': [
                'C:/Users/ronak.chaturvedi/Documents/ollam/img/page_20.png',
            ]
        }
    ],
    think=False,
    options={"temperature": 0.2,
             }
)

result = response.message.content
match = re.search(r"\{.*\}", result, re.DOTALL)
if match:
    try:
        data = json.loads(match.group())

        with open("balance_commentary.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("✅ JSON parsed successfully")

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        save_failed_output(result)

else:
    print("❌ No JSON found")
    save_failed_output(result)

# import json
# import re
# import importlibþ
# from ollama import chat
# from general import JSON_WRAP_RULE


# def generate_commentary(image_paths, output_json_path, module, system_prompt_var, user_prompt_var):
#     prompt_module = importlib.import_module(f"prompts.{module}")
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

#     result = response.message.content
#     match = re.search(r"\{.*\}", result, re.DOTALL)
#     if match:
#         data = json.loads(match.group())
#         with open(output_json_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         return output_json_path
#     else:
#         return None