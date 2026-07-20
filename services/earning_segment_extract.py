
import json
import re
from prompts.earning_extract import SYSTEM_PROMPT, USER_PROMPT
from client.ollama_client import chat


def extract_earning_segments(image_paths):
    """
    Returns:
        {
            "non_interest_income_segments": [{"label": ..., "amount": ...}, ...],
            "non_interest_expense_segments": [{"label": ..., "amount": ...}, ...],
        }
        or None if no image was available or the model's output could not
        be parsed as valid JSON. Callers must treat None as a soft failure
        and fall back to existing (image-only hybrid) behavior -- never
        raise on a failed extraction here.
    """
    if not image_paths:
        return None

    message = {"role": "user", "content": USER_PROMPT, "images": image_paths}

    response = chat(
        model='qwen3.5:9b',
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            message,
        ],
        think=False,
        options={"temperature": 0.2, "num_ctx": 16384},
    )

    result = response["message"]["content"]
    match = re.search(r"\{.*\}", result, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(), strict=False)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    return {
        "non_interest_income_segments": data.get("non_interest_income_segments") or [],
        "non_interest_expense_segments": data.get("non_interest_expense_segments") or [],
    }