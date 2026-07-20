"""
Inspection Report Parser

Usage:
    python parser.py inspection_report.txt

Output:

output/
    json/
    markdown/
    raw/
    summary.json
    summary.md
"""

import re
import json
import os
import sys
from pathlib import Path

# ============================================================
# Output folders
# ============================================================

OUTPUT_DIR = Path("output")
JSON_DIR = OUTPUT_DIR / "json"
MD_DIR = OUTPUT_DIR / "markdown"
RAW_DIR = OUTPUT_DIR / "raw"

JSON_DIR.mkdir(parents=True, exist_ok=True)
MD_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Regex
# ============================================================

SECTION_REGEX = re.compile(
    r"SECTION:\s*([A-Za-z0-9_]+)",
    re.IGNORECASE,
)

STATUS_REGEX = re.compile(
    r"status:\s*(.+)",
    re.IGNORECASE,
)

FLAGS_REGEX = re.compile(
    r"flags:\s*(.+)",
    re.IGNORECASE,
)

# ============================================================
# Helpers
# ============================================================

def clean_value(value):
    """
    Convert text to proper python types.
    """

    value = value.strip()

    if value.lower() == "none":
        return None

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    # integer

    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except:
            pass

    # float

    if re.fullmatch(r"-?\d+\.\d+", value):
        try:
            return float(value)
        except:
            pass

    return value


def indentation(line):
    """
    Count leading spaces.
    """

    return len(line) - len(line.lstrip())


# ============================================================
# Split report into sections
# ============================================================

def split_sections(report_text):
    """
    Returns

    [
        ("balance_sheet", text),
        ("earning", text),
        ...
    ]
    """

    matches = list(SECTION_REGEX.finditer(report_text))

    sections = []

    for i, match in enumerate(matches):

        name = match.group(1).strip()

        start = match.start()

        if i == len(matches) - 1:
            end = len(report_text)
        else:
            end = matches[i + 1].start()

        block = report_text[start:end]

        sections.append((name, block))

    return sections


# ============================================================
# Extract raw OCR text
# ============================================================

def extract_raw_text(section_text):

    start = section_text.find("--- RAW extract_text() PER PAGE ---")

    if start == -1:
        return ""

    end = section_text.find(
        "--- PARSED RESULT ---",
        start,
    )

    if end == -1:
        return section_text[start:]

    return section_text[start:end].strip()


# ============================================================
# Status
# ============================================================

def extract_status(section_text):

    m = STATUS_REGEX.search(section_text)

    if m:
        return m.group(1).strip()

    return None


# ============================================================
# Flags
# ============================================================

def extract_flags(section_text):
    """
    Returns a list of flag reason strings, or None if the section reported
    no flags.

    inspect_extraction.py writes flags as either:
        flags: none
    or, when validate_section() found one or more issues:
        flags:
          - reason one
          - reason two

    The previous single-line regex only ever captured the first bullet
    after "flags:", silently dropping every additional DATA_CHECK reason
    once a section had more than one. That was tolerable for a debug
    report a human skims, but this file's JSON output can now feed
    directly into commentary generation -- a dropped flag there means a
    real, unreconciled figure reaches the model with no DATA CHECK
    protection at all.
    """
    m = re.search(r"^\s*flags:[ \t]*(.*)$", section_text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return None

    same_line_value = m.group(1).strip()
    if same_line_value.lower() == "none":
        return None

    reasons = []
    for line in section_text[m.end():].splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            reasons.append(stripped[2:].strip())
        elif stripped == "":
            continue
        else:
            break  # first non-bullet, non-blank line ends the flags block

    return reasons or None


# ============================================================
# Locate parsed data block
# ============================================================

def get_parsed_data_text(section_text):

    marker = "parsed data:"

    pos = section_text.find(marker)

    if pos == -1:
        return ""

    return section_text[pos + len(marker):].rstrip()


# ============================================================
# Parse indentation-based structure
# ============================================================

def parse_block(text):
    """
    Converts

        total_assets:
            amount: 123
            pct: 10

    into nested dict/list.

    Implemented in Part 2.
    """
    raise NotImplementedError


# ============================================================
# JSON writer
# ============================================================

def save_json(path, data):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )


# ============================================================
# Markdown writer
# ============================================================

def markdown_from_object(obj, level=1):
    """
    Implemented in Part 2
    """
    raise NotImplementedError


def save_markdown(path, text):

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ============================================================
# Parse indentation-based structure
# ============================================================

def parse_block(text):
    """
    Parse the 'parsed data:' section into nested Python dicts/lists.
    """

    lines = [l.rstrip() for l in text.splitlines() if l.strip()]

    if not lines:
        return {}

    root = {}
    stack = [(-1, root)]

    for line in lines:

        indent = indentation(line)
        line = line.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]

        # ---------------------------------------------------
        # List index
        # ---------------------------------------------------

        m = re.match(r"\[(\d+)\]\s*$", line)

        if m:

            idx = int(m.group(1))

            if not isinstance(parent, list):

                if len(stack) < 2:
                    # No enclosing dict key to attach a list to. This shows
                    # up when a wrapped PDF table cell embeds a literal
                    # newline (e.g. a policy metric label split across two
                    # lines by pdfplumber) -- the continuation line lands
                    # at root indentation in the report text and, if it
                    # happens to look like "[N]", there is no parent key
                    # left on the stack to attach a list to. Skip this one
                    # malformed line rather than crashing the whole run --
                    # every other line/section still needs to parse.
                    continue

                new_list = []

                # attach to previous dict key

                prev_indent, prev_parent = stack[-2]

                if isinstance(prev_parent, dict):
                    last_key = list(prev_parent.keys())[-1]
                    prev_parent[last_key] = new_list

                parent = new_list
                stack[-1] = (stack[-1][0], parent)

            while len(parent) <= idx:
                parent.append({})

            stack.append((indent, parent[idx]))
            continue

        # ---------------------------------------------------
        # key: value
        # ---------------------------------------------------

        if ":" in line:

            key, value = line.split(":", 1)

            key = key.strip()
            value = value.strip()

            # empty value -> nested dict

            if value == "":

                obj = {}

                if isinstance(parent, dict):
                    parent[key] = obj

                elif isinstance(parent, list):
                    parent.append(obj)

                stack.append((indent, obj))

            else:

                value = clean_value(value)

                if isinstance(parent, dict):
                    parent[key] = value

                elif isinstance(parent, list):
                    parent.append({key: value})

    return root


# ============================================================
# Markdown
# ============================================================

def markdown_from_object(obj, level=1):

    md = ""

    if isinstance(obj, dict):

        for key, value in obj.items():

            if isinstance(value, dict):

                md += "#" * level + f" {key}\n\n"
                md += markdown_from_object(value, level + 1)

            elif isinstance(value, list):

                md += "#" * level + f" {key}\n\n"

                for i, item in enumerate(value):

                    md += f"### Item {i+1}\n\n"
                    md += markdown_from_object(item, level + 1)

            else:

                md += f"- **{key}**: {value}\n"

        md += "\n"

    elif isinstance(obj, list):

        for item in obj:

            md += markdown_from_object(item, level)

    return md


# ============================================================
# Convert one section
# ============================================================

def process_section(name, block):

    status = extract_status(block)
    flags = extract_flags(block)

    raw = extract_raw_text(block)

    parsed_text = get_parsed_data_text(block)

    parsed = {}

    if parsed_text.strip():
        parsed = parse_block(parsed_text)

    result = {
        "section": name,
        "status": status,
        "flags": flags,
        "raw_extract_text": raw,
        "parsed_data": parsed,
    }

    return result


# ============================================================
# Driver: read an inspection report, process every section,
# write per-section outputs + a run summary.
# ============================================================

DEFAULT_REPORT_PATH = os.path.join(
    "inspection_output", "BOPTI_Board_Report_May26_inspection_report.txt"
)


def load_report(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _flags_display(flags):
    """Render a flags list (or None) as one readable line."""
    if not flags:
        return ""
    if isinstance(flags, list):
        return "; ".join(flags)
    return str(flags)


def run(path=DEFAULT_REPORT_PATH):
    report_text = load_report(path)
    sections = split_sections(report_text)

    if not sections:
        print(f"[warn] no 'SECTION:' markers found in {path}")
        return

    summary_rows = []

    for name, block in sections:
        try:
            result = process_section(name, block)
        except Exception as exc:
            print(f"[error] {name}: failed to parse -- {exc!r}")
            summary_rows.append({
                "section": name,
                "status": "PARSE_ERROR",
                "flags": str(exc),
            })
            continue

        json_path = JSON_DIR / f"{name}.json"
        save_json(json_path, result)

        md_lines = [f"# {name}", "", f"**status:** {result['status']}"]
        if result["flags"]:
            md_lines.append(f"**flags:** {_flags_display(result['flags'])}")
        md_lines.append("")
        md_lines.append(markdown_from_object(result["parsed_data"]))
        save_markdown(MD_DIR / f"{name}.md", "\n".join(md_lines))

        save_markdown(RAW_DIR / f"{name}.txt", result["raw_extract_text"])

        summary_rows.append({
            "section": name,
            "status": result["status"],
            "flags": result["flags"],
        })

        print(f"[ok] {name}: status={result['status']}")

    save_json(OUTPUT_DIR / "summary.json", summary_rows)

    md_summary = ["# Inspection Report Summary", "", f"Source: `{path}`", ""]
    md_summary.append("| Section | Status | Flags |")
    md_summary.append("|---|---|---|")
    for row in summary_rows:
        md_summary.append(f"| {row['section']} | {row['status']} | {_flags_display(row['flags'])} |")
    save_markdown(OUTPUT_DIR / "summary.md", "\n".join(md_summary))

    print(f"\nDone. {len(summary_rows)} sections written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    report_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPORT_PATH
    if not os.path.isfile(report_path):
        print(f"[error] report file not found: {report_path}")
        sys.exit(1)
    run(report_path)