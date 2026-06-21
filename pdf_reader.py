import PyPDF2

def read_pdf(pdf_path):
    """
    Takes a PDF path.
    Returns a list of strings, one per page.
    Example: ["page 1 text...", "page 2 text...", ...]
    """
    reader = PyPDF2.PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    print(f"Read {len(pages)} pages from {pdf_path}")
    return pages