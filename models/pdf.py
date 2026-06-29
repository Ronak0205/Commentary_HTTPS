import fitz


def extract_page_images(pdf_path, output_dir, pdf_name, page_numbers, dpi=300):
    doc = fitz.open(pdf_path)
    output_paths = []

    for page_number in page_numbers:
        page = doc[page_number]
        pix = page.get_pixmap(dpi=dpi)
        output_path = f"{output_dir}/{pdf_name}_page{page_number + 1}.png"
        pix.save(output_path)
        output_paths.append(output_path)

    doc.close()
    return output_paths

# import fitz

# doc = fitz.open("pdf/01_Board_Report_Quaterly_WithoutCommentary.pdf")
# page = doc[19]  # page 7
# pix = page.get_pixmap()
# pix.save("page_20.png")