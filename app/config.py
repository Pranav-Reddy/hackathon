import os

class Config:
    BUCKET_NAME = os.getenv("GCS_BUCKET", "your-default-bucket-name")
