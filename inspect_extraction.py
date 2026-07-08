

import os
import sys
import pdfplumber

from config.config import SECTIONS 
from config.extraction_config import EXTRACTION_CONFIG
from services.pdf_extract import extract_section_data
from pipeline.validate import validate_section


def _get_raw_page_text(pdf_path, page_numbers):
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in page_numbers:
            if 0 <= page_number < len(pdf.pages):
                text = pdf.pages[page_number].extract_text()
                texts.append((page_number + 1, text or "(no text extracted on this page)"))
            else:
                texts.append((page_number + 1, "(page number out of range)"))
    return texts


def _format_value(v, indent=4):
    pad = " " * indent
    if isinstance(v, dict):
        lines = []
        for k, val in v.items():
            if isinstance(val, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_format_value(val, indent + 2))
            else:
                lines.append(f"{pad}{k}: {val}")
        return "\n".join(lines)
    if isinstance(v, list):
        lines = []
        for i, item in enumerate(v):
            lines.append(f"{pad}[{i}]")
            lines.append(_format_value(item, indent + 2))
        return "\n".join(lines)
    return f"{pad}{v}"


def inspect_pdf(pdf_path, output_dir="inspection_output"):
    os.makedirs(output_dir, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f"{pdf_name}_inspection_report.txt")

    lines = []
    lines.append("=" * 90)
    lines.append(f"EXTRACTION INSPECTION REPORT")
    lines.append(f"PDF: {pdf_path}")
    lines.append("=" * 90)

    for section in SECTIONS:
        name = section["name"]
        pages = section["pages"]
        page_numbers = [p - 1 for p in pages]

        lines.append("\n")
        lines.append("#" * 90)
        lines.append(f"SECTION: {name}   (config pages: {pages})")
        lines.append("#" * 90)

        # --- raw page text, always shown regardless of extractable flag ---
        lines.append("\n--- RAW extract_text() PER PAGE ---")
        for page_num_1indexed, text in _get_raw_page_text(pdf_path, page_numbers):
            lines.append(f"\n[Page {page_num_1indexed}]")
            lines.append(text)

        cfg = EXTRACTION_CONFIG.get(name, {})
        if not cfg.get("extractable"):
            lines.append("\n--- PARSED RESULT ---")
            lines.append("SKIPPED -- not configured as extractable in extraction_config.py")
            continue

        raw = extract_section_data(pdf_path, name, page_numbers)

        lines.append("\n--- PARSED RESULT ---")
        if raw is None:
            lines.append("NOTHING EXTRACTED -- parser ran but found no usable data")
            continue

        validated = validate_section(name, raw)
        status = validated["status"] if validated else "OK"
        flags = validated["flags"] if validated else []
        data = validated["data"] if validated else raw

        lines.append(f"status: {status}")
        if flags:
            lines.append("flags:")
            for f in flags:
                lines.append(f"  - {f.get('reason', f)}")
        else:
            lines.append("flags: none")

        lines.append("\nparsed data:")
        lines.append(_format_value(data))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Full inspection report written to: {output_path}")
    print(f"({len(lines)} lines)")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_extraction.py path/to/report.pdf")
        sys.exit(1)

    inspect_pdf(sys.argv[1])