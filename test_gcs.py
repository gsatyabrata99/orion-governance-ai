import os
import sys
from google.cloud import storage

BUCKET = os.environ.get("GCS_BUCKET")  # set this before running
TEST_PATH = "audit/smoke_test.txt"

def main():
    print("Starting GCS test...", flush=True)
    if not BUCKET:
        raise ValueError("GCS_BUCKET env var not set. Example: export GCS_BUCKET=orion-governance-data")

    client = storage.Client()
    bucket = client.bucket(BUCKET)

    blob = bucket.blob(TEST_PATH)
    blob.upload_from_string("OK - GCS write works.\n", content_type="text/plain")

    data = blob.download_as_text()
    print("GCS READBACK:", data.strip(), flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", repr(e), file=sys.stderr, flush=True)
        raise
