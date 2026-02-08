import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "orion-group-486700")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-east1")

BUCKET = os.getenv("GCS_BUCKET")
if not BUCKET:
    raise RuntimeError("GCS_BUCKET env var not set")
