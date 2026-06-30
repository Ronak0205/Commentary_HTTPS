from datetime import date
import os
import sys
from config import EXTRACTED_IMG_DIR, DATA_DIR, SECTIONS
from models.pdf import extract_page_images
from models.commentary import generate_commentary


def run():
    os.makedirs(EXTRACTED_IMG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    pdf_dir = "pdf"
    if not os.path.isdir(pdf_dir):
        print(f"[error] PDF directory not found: {pdf_dir}")
        sys.exit(1)

    pdf_files = sorted(
        [
            f
            for f in os.listdir(pdf_dir)
            if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(pdf_dir, f))
        ]
    )

    if not pdf_files:
        print(f"[error] No PDF files found in: {pdf_dir}")
        sys.exit(1)

    for pdf_file in pdf_files:
        pdf_name = os.path.splitext(pdf_file)[0]
        pdf_path = os.path.join(pdf_dir, pdf_file)
        pdf_data_dir = os.path.join(DATA_DIR, pdf_name)
        os.makedirs(pdf_data_dir, exist_ok=True)

        print(f"\n=== Processing PDF: {pdf_name} ===")

        for section in SECTIONS:
            name = section["name"]
            pages = section["pages"]
            module = section["module"]
            system_prompt_var = section["system_prompt_var"]
            user_prompt_var = section["user_prompt_var"]

            page_numbers = [p - 1 for p in pages]

            img_paths = extract_page_images(
                pdf_path, EXTRACTED_IMG_DIR, f"{pdf_name}_{name}", page_numbers
            )
            print(f"[{pdf_name}][{name}] images extracted: {img_paths}")

            json_path = os.path.join(
                pdf_data_dir,
                f"{pdf_name}_{name}_commentary_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.json",
            )

            result = generate_commentary(
                img_paths, json_path, module, system_prompt_var, user_prompt_var
            )

            if result:
                print(f"[{pdf_name}][{name}] commentary saved: {json_path}")
            else:
                print(
                    f"[{pdf_name}][{name}] no JSON found, stopping at module: {name}"
                )
                sys.exit(1)

        print(f"=== Completed PDF: {pdf_name} ===")


if __name__ == "__main__":
    run()