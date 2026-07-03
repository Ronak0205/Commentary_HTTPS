import os
import sys

from pipeline.pipeline import process_pdf, PipelineError


def run():
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

        print(f"\n=== Processing PDF: {pdf_name} ===")

        try:
            result = process_pdf(pdf_path, pdf_name)
        except PipelineError as e:
            print(f"[error] {e}")
            sys.exit(1)

        for name, path in result["section_output_paths"].items():
            print(f"[{pdf_name}][{name}] commentary saved: {path}")

        print(f"[{pdf_name}][ceo_report] commentary saved: {result['ceo_output']}")
        print(f"[{pdf_name}][action_recommended] commentary saved: {result['action_output']}")
        print(f"[{pdf_name}][final_output] merged JSON saved: {result['final_output_path']}")

        print(f"=== Completed PDF: {pdf_name} ===")


if __name__ == "__main__":
    run()