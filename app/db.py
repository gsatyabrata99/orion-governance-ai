from google.cloud import firestore

db = firestore.Client()

def create_document_record(project_id: str, doc: dict) -> str:
    ref = db.collection("projects").document(project_id).collection("documents").document()
    ref.set(doc)
    return ref.id

def update_document_record(project_id: str, doc_id: str, patch: dict):
    ref = db.collection("projects").document(project_id).collection("documents").document(doc_id)
    ref.set(patch, merge=True)

def write_chunks(project_id: str, doc_id: str, chunks: list[dict]):
    col = (
        db.collection("projects")
        .document(project_id)
        .collection("documents")
        .document(doc_id)
        .collection("chunks")
    )
    batch = db.batch()
    for c in chunks:
        ref = col.document(c["chunk_id"])
        batch.set(ref, c)
    batch.commit()
