from google.cloud import storage
from .config import BUCKET

_client = storage.Client()

def upload_bytes(path: str, data: bytes, content_type: str):
    bucket = _client.bucket(BUCKET)
    blob = bucket.blob(path)
    blob.upload_from_string(data, content_type=content_type)
    return f"gs://{BUCKET}/{path}"

def download_bytes(path: str) -> bytes:
    bucket = _client.bucket(BUCKET)
    blob = bucket.blob(path)
    return blob.download_as_bytes()
