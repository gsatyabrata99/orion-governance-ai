import os
from google import genai

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "orion-group-486700")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")  # keep the region that worked

def main():
    print("Starting Vertex AI test (new SDK)...")

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

    model_id = "gemini-2.0-flash"  # confirmed working model

    resp = client.models.generate_content(
        model=model_id,
        contents="Reply with exactly: OK - Vertex AI works.",
    )

    print("MODEL RESPONSE:", resp.text.strip())

if __name__ == "__main__":
    main()
