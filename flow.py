from datetime import date
import os
import sys
from config import PDF_PATH, PDF_NAME, EXTRACTED_IMG_DIR, DATA_DIR, SECTIONS
from models.pdf import extract_page_images
from models.commentary import generate_commentary


def run():
    os.makedirs(EXTRACTED_IMG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    for section in SECTIONS:
        name = section["name"]
        pages = section["pages"]
        module = section["module"]
        system_prompt_var = section["system_prompt_var"]
        user_prompt_var = section["user_prompt_var"]

        page_numbers = [p - 1 for p in pages]

        img_paths = extract_page_images(
            PDF_PATH, EXTRACTED_IMG_DIR, f"{PDF_NAME}_{name}", page_numbers
        )
        print(f"[{name}] images extracted: {img_paths}")

        json_path = os.path.join(DATA_DIR, f"{PDF_NAME}_{name}_commentary_{date.today().strftime('%Y-%m-%d-%H-%M-%S')}.json")

        result = generate_commentary(
            img_paths, json_path, module, system_prompt_var, user_prompt_var
        )

        if result:
            print(f"[{name}] commentary saved: {json_path}")
        else:
            print(f"[{name}] no JSON found, stopping at module: {name}")
            sys.exit(1)


if __name__ == "__main__":
    run()