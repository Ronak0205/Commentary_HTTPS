import base64
import json
import os
import re
import ollama

from prompts.graph import BOTH_PROMPT, PIE_CHART_PROMPT, GRAPH_PROMPT, TABLE_PROMPT, CLASSIFY_PROMPT

MODEL = "qwen3.5:9b"
INPUT_DIR = "img"
OUTPUT_DIR = "json"

img = {}


def load_images(input_dir):
    image_extensions = (".png", ".jpg", ".jpeg")
    for filename in sorted(os.listdir(input_dir)):
        if filename.lower().endswith(image_extensions):
            path = os.path.join(input_dir, filename)
            with open(path, "rb") as f:
                img[filename] = base64.b64encode(f.read()).decode("utf-8")


def call_vision_model(image_b64, prompt, force_json=True):
    kwargs = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        "think": False,
        "options": {
            "temperature": 0,
        },
    }
    if force_json:
        kwargs["format"] = "json"

    response = ollama.chat(**kwargs)
    return response["message"]["content"]


def classify_image(image_b64):
    text = call_vision_model(image_b64, CLASSIFY_PROMPT, force_json=False)
    text = text.strip().upper()
    found = set()
    for label in ["TABLE", "BAR_CHART", "PIE_CHART", "LINE_CHART"]:
        if label in text:
            found.add(label)
    if not found:
        found.add("NONE")
    return found


def strip_code_fences(text):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def extract_first_json_object(text):
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def fix_bad_numeric_tokens(text):
    text = re.sub(r"(\d+(\.\d+)?)\s*%\s*\([\d\+\-\*/\.\s]+\)", r'"\1%"', text)
    text = re.sub(r'(?<!")(\d+(\.\d+)?)\s*%(?!")', r'"\1%"', text)
    text = re.sub(r"(\d+(\.\d+)?e[+-]?\d+)\s*/\s*\d+(\.\d+)?(\s*\*\s*\d+(\.\d+)?\*?)?", r'"\1"', text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def safe_parse_json(raw_text):
    cleaned = strip_code_fences(raw_text)
    candidate = extract_first_json_object(cleaned) or cleaned

    try:
        return json.loads(candidate), False
    except json.JSONDecodeError:
        pass

    repaired = fix_bad_numeric_tokens(candidate)
    try:
        return json.loads(repaired), False
    except json.JSONDecodeError as e:
        return {"raw_response": raw_text, "error_detail": str(e)}, True


def names_match(series_name, table_name):
    series_name = series_name.strip()
    table_name = table_name.strip()
    if series_name == table_name:
        return True
    if series_name.endswith("..."):
        prefix = series_name.rstrip(". ").strip()
        return bool(prefix) and table_name.startswith(prefix)
    return False


def backfill_charts_from_table(parsed, name_column=None):
    table = parsed.get("table")
    charts = parsed.get("charts")
    if not table or not charts:
        return parsed

    for chart in charts:
        if chart.get("x_axis_type") != "category":
            continue

        value_column = chart.get("source_table_column")
        if not value_column:
            continue

        col_name_column = name_column or guess_name_column(table)
        if not col_name_column:
            continue

        table_lookup = {}
        for row in table:
            name = (row.get(col_name_column) or "").strip().upper()
            if name and value_column in row and row[value_column] is not None:
                table_lookup[name] = row[value_column]

        for series in chart.get("series", []):
            if series.get("values") not in (None, "", []):
                continue
            series_name = (series.get("name") or "").strip().upper()
            matches = [(t, v) for t, v in table_lookup.items() if names_match(series_name, t)]
            if len(matches) == 1:
                series["values"] = matches[0][1]
            elif len(matches) > 1:
                series["match_ambiguous"] = [m[0] for m in matches]

    return parsed


def guess_name_column(table):
    if not table:
        return None
    sample = table[0]
    for key, val in sample.items():
        if isinstance(val, str):
            return key
    return None


def extract_from_image(image_b64):
    content_types = classify_image(image_b64)

    if content_types == {"NONE"}:
        return {"content_types": ["NONE"], "table": None, "charts": None, "pie_charts": None, "parse_error": False}

    result = {"content_types": sorted(content_types)}
    any_parse_error = False

    if "TABLE" in content_types and "BAR_CHART" in content_types:
        raw = call_vision_model(image_b64, BOTH_PROMPT)
        parsed, parse_error = safe_parse_json(raw)
        any_parse_error = any_parse_error or parse_error
        if not parse_error:
            parsed = backfill_charts_from_table(parsed)
        result["table"] = parsed.get("table")
        result["charts"] = parsed.get("charts")
        if parse_error:
            result["raw_output"] = parsed.get("raw_response")
    else:
        if "TABLE" in content_types:
            raw = call_vision_model(image_b64, TABLE_PROMPT)
            parsed, parse_error = safe_parse_json(raw)
            any_parse_error = any_parse_error or parse_error
            result["table"] = parsed.get("table")
            if parse_error:
                result["raw_output"] = parsed.get("raw_response")

        if "BAR_CHART" in content_types or "LINE_CHART" in content_types:
            raw = call_vision_model(image_b64, GRAPH_PROMPT)
            parsed, parse_error = safe_parse_json(raw)
            any_parse_error = any_parse_error or parse_error
            result["charts"] = parsed.get("charts")
            if parse_error:
                result["raw_output"] = parsed.get("raw_response")

    if "PIE_CHART" in content_types:
        raw = call_vision_model(image_b64, PIE_CHART_PROMPT)
        parsed, parse_error = safe_parse_json(raw)
        any_parse_error = any_parse_error or parse_error
        result["pie_charts"] = parsed.get("pie_charts")
        if parse_error:
            result["raw_output"] = parsed.get("raw_response")

    result["parse_error"] = any_parse_error
    return result


def save_json(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_txt(text, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def run():
    load_images(INPUT_DIR)

    if not img:
        print(f"No images found in {INPUT_DIR}")
        return

    for filename, image_b64 in img.items():
        base_name = os.path.splitext(filename)[0]
        print(f"Processing {filename} ...")

        try:
            result = extract_from_image(image_b64)
        except Exception as e:
            save_txt(f"extraction failed: {e}", os.path.join(OUTPUT_DIR, f"{base_name}.txt"))
            print(f"  failed, saved error to {base_name}.txt")
            continue

        if result.get("parse_error"):
            raw_text = result.get("raw_output") or json.dumps(result, indent=2)
            save_txt(raw_text, os.path.join(OUTPUT_DIR, f"{base_name}.txt"))
            print(f"  parse_error, saved raw output to {base_name}.txt")
        else:
            save_json(result, os.path.join(OUTPUT_DIR, f"{base_name}.json"))
            print(f"  saved clean json to {base_name}.json")


if __name__ == "__main__":
    run()