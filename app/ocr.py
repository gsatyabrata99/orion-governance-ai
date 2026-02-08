import os
from google.cloud import documentai_v1 as documentai

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DOCAI_LOCATION = os.getenv("DOCAI_LOCATION", "us")
DOCAI_PROCESSOR_ID = os.getenv("DOCAI_PROCESSOR_ID")

def _text_from_anchor(full_text: str, anchor) -> str:
    if not anchor or not anchor.text_segments:
        return ""
    out = []
    for seg in anchor.text_segments:
        start = int(seg.start_index or 0)
        end = int(seg.end_index or 0)
        out.append(full_text[start:end])
    return "".join(out)

def ocr_pdf_to_pages(pdf_bytes: bytes) -> list[dict]:
    if not PROJECT_ID:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not set")
    if not DOCAI_PROCESSOR_ID:
        raise RuntimeError("DOCAI_PROCESSOR_ID not set")
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR_ID)

    raw_document = documentai.RawDocument(content=pdf_bytes, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    doc = result.document

    full_text = doc.text or ""
    pages = []
    if doc.pages:
        for i, page in enumerate(doc.pages, start=1):
            page_text = _text_from_anchor(full_text, page.layout.text_anchor).strip()
            pages.append({"page": i, "text": page_text})
    else:
        pages = [{"page": 1, "text": full_text.strip()}]
    return pages
