from io import BytesIO
import docx
from .ocr import ocr_pdf_to_pages

def extract_pdf_text(pdf_bytes: bytes) -> list[dict]:
    pages = ocr_pdf_to_pages(pdf_bytes)
    total = sum(len(p.get("text","")) for p in pages)
    print(f"OCR used: pages={len(pages)} total_chars={total}")
    return pages

def extract_docx_text(docx_bytes: bytes) -> list[dict]:
    d = docx.Document(BytesIO(docx_bytes))
    parts = [p.text.strip() for p in d.paragraphs if p.text and p.text.strip()]
    text = "\n\n".join(parts)
    return [{"page": 1, "text": text}]
