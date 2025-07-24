import os

class Config:
    BUCKET_NAME = os.getenv("bucket", "hack-team-eclipse-test-bucket")
    PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
