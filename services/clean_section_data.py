import json
import os
from pathlib import Path

# Fields that represent a section's own as-of date, in priority order.
# The first one present wins. Anything else falls back to the report's
# general cover date, passed in by the caller.
_AS_OF_DATE_KEYS = ("schedule_as_of_date", "report_date")

# Debug/internal fields that are never real business values -- e.g.
# raw_rows (pdfplumber's row-per-line dump, kept only for troubleshooting
# extraction) and note (free-text pipeline instructions that previously
# leaked into commentary verbatim). commentary.py used to strip these
# downstream via its own _PIPELINE_INTERNAL_KEYS; stripping them here
# instead means every downstream consumer gets clean data by default.
_DROP_KEYS = {"raw_rows", "note"}


def _drop_internal_keys(data):
    if isinstance(data, dict):
        return {k: _drop_internal_keys(v) for k, v in data.items() if k not in _DROP_KEYS}
    if isinstance(data, list):
        return [_drop_internal_keys(v) for v in data]
    return data


def remove_nulls(data):
    """
    Recursively strip None values and empty dict/list containers.
    A field that was extracted as null (nothing on the source) simply
    disappears instead of showing up as `"reserves": null` for every
    downstream consumer to check for.
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned_value = remove_nulls(value)
            if cleaned_value is None:
                continue
            if isinstance(cleaned_value, (dict, list)) and len(cleaned_value) == 0:
                continue
            cleaned[key] = cleaned_value
        return cleaned

    if isinstance(data, list):
        cleaned_list = [remove_nulls(item) for item in data]
        cleaned_list = [
            item for item in cleaned_list
            if item is not None and not (isinstance(item, (dict, list)) and len(item) == 0)
        ]
        return cleaned_list

    return data


def clean_section(section_json, institution_name=None, report_date=None):
    """
    section_json: the dict already loaded from output/json/<section>.json
    (parser.py's shape: {"section","status","flags","raw_extract_text",
    "parsed_data"}).

    Returns:
        {
            "section": "loan_continue",
            "status": "OK",
            "flags": [...],                 # always a list, never None
            "as_of_date": "03-31-2026",      # section's own date if present,
                                             # else the report's cover date
            "institution_name": "Bopti Federal Credit Union",
            "data": { ...nulls stripped... },
        }
    """
    parsed_data = section_json.get("parsed_data") or {}
    parsed_data = _drop_internal_keys(parsed_data)
    cleaned_data = remove_nulls(parsed_data)

    as_of_date = report_date
    for key in _AS_OF_DATE_KEYS:
        if key in cleaned_data:
            as_of_date = cleaned_data.pop(key)
            break

    raw_flags = section_json.get("flags")
    flags = raw_flags if isinstance(raw_flags, list) else ([raw_flags] if raw_flags else [])

    return {
        "section": section_json.get("section"),
        "status": section_json.get("status") or "OK",
        "flags": flags,
        "as_of_date": as_of_date,
        "institution_name": institution_name,
        "data": cleaned_data,
    }


def clean_section_file(path, institution_name=None, report_date=None):
    """Load one output/json/<section>.json file and return its cleaned form."""
    with open(path, "r", encoding="utf-8") as f:
        section_json = json.load(f)
    return clean_section(section_json, institution_name=institution_name, report_date=report_date)


def clean_all_sections(json_dir="output/json", out_dir="output/clean",
                        institution_name=None, report_date=None):
    """
    Clean every <section>.json in json_dir and write the result to
    out_dir/<section>.json. Returns {section_name: cleaned_dict}.
    """
    os.makedirs(out_dir, exist_ok=True)
    results = {}

    for file_path in sorted(Path(json_dir).glob("*.json")):
        section_name = file_path.stem
        cleaned = clean_section_file(
            file_path, institution_name=institution_name, report_date=report_date
        )
        results[section_name] = cleaned

        out_path = Path(out_dir) / f"{section_name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=4, ensure_ascii=False)

    return results


if __name__ == "__main__":
    import sys
    json_dir = sys.argv[1] if len(sys.argv) > 1 else "output/json"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output/clean"
    results = clean_all_sections(json_dir, out_dir)
    for name, cleaned in results.items():
        print(f"[ok] {name}: status={cleaned['status']}, as_of_date={cleaned['as_of_date']}, "
              f"fields={len(cleaned['data'])}")