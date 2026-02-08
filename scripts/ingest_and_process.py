import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

import os
import mimetypes
from pathlib import Path

ACL = {
  "Board_Minutes_Jan_2026.pdf": ["Janish Kumar", "Ganesh Satyabrata"],
  "Board_Minutes_Feb_2026.pdf": ["Janish Kumar", "Ganesh Satyabrata"],
  "Board_Minutes_Mar_2026.pdf": ["Janish Kumar", "Ganesh Satyabrata"],

  "COI_Disclosure_Register_v2.pdf": ["Janish Kumar", "Ganesh Satyabrata", "Kamal Dhakal"],
  "COI_Disclosure_Register_v1.docx": ["Janish Kumar", "Ganesh Satyabrata", "Kamal Dhakal"],

  "Corporate Governance Reference Framework.pdf": ["Janish Kumar", "Ganesh Satyabrata", "Kamal Dhakal", "Vyanktesh Arali", "Devansh Agarwal"],
  "Code of Conduct.pdf": ["Janish Kumar", "Ganesh Satyabrata", "Kamal Dhakal", "Vyanktesh Arali", "Devansh Agarwal"],
}

from app.storage import upload_bytes
from app.db import create_document_record, update_document_record, write_chunks
from app.extract import extract_pdf_text, extract_docx_text
from app.chunk import chunk_pages

PROJECT_ID = os.getenv("PROJECT_ID", "orion")
DATA_DIR = Path("data")

def detect_type(path: Path) -> str:
    mt, _ = mimetypes.guess_type(str(path))
    return mt or "application/octet-stream"

def main():
    DATA_DIR.mkdir(exist_ok=True)
    files = [p for p in DATA_DIR.glob("*") if p.is_file() and not p.name.startswith(".")]

    if not files:
        print("No files in ./data")
        return

    for f in files:
        content_type = detect_type(f)
        raw_bytes = f.read_bytes()

            # --- metadata (define BEFORE creating doc_id) ---
        import time
        timestamp = int(__import__("time").time())
        doc_type = "minutes" if "Board_Minutes" in f.name else ("coi" if "COI" in f.name else "policy")
        allowed_users = ACL.get(f.name, ["Janish Kumar"])  # default minimal access

        doc = {
            "source_filename": f.name,
            "ingested_at": timestamp,
            "doc_type": doc_type,
            "allowed_users": allowed_users,
            "status": "NEW",
        }

        # create Firestore doc_id
        doc_id = create_document_record(PROJECT_ID, doc)

        # now that doc_id exists, store it back (optional but nice)
        update_document_record(PROJECT_ID, doc_id, {"doc_id": doc_id})

        # store raw file in GCS
        gcs_path = f"raw/{doc_id}/{f.name}"
        gcs_uri = upload_bytes(gcs_path, raw_bytes, content_type)

        update_document_record(PROJECT_ID, doc_id, {
            "gcs_uri": gcs_uri,
            "status": "STORED"
        })

        # extract text (OCR already happens inside extract_pdf_text)
        if f.suffix.lower() == ".pdf":
            pages = extract_pdf_text(raw_bytes)
        elif f.suffix.lower() == ".docx":
            pages = extract_docx_text(raw_bytes)
        else:
            pages = [{"page": 1, "text": raw_bytes.decode("utf-8", errors="ignore")}]

        update_document_record(PROJECT_ID, doc_id, {
            "status": "EXTRACTED",
            "page_count": len(pages)
        })

        # chunk
        chunks = chunk_pages(doc_id, pages)

        # enrich chunks with metadata + ACL
        for c in chunks:
            c["doc_id"] = doc_id
            c["project_id"] = PROJECT_ID
            c["allowed_users"] = allowed_users
            c["source_filename"] = f.name
            c["source"] = {"filename": f.name, "gcs_uri": gcs_uri}

        write_chunks(PROJECT_ID, doc_id, chunks)

        update_document_record(PROJECT_ID, doc_id, {
            "status": "CHUNKED",
            "chunk_count": len(chunks)
        })

        print(f"Ingested {f.name} -> {len(chunks)} chunks")



if __name__ == "__main__":
    main()
