from google.cloud import storage
from app.config import Config

def download_blob(filename, override_bucket=None):
    bucket_name = override_bucket or Config.BUCKET_NAME
    destination_path = f"/tmp/{filename}"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.download_to_filename(destination_path)

    return f"Downloaded {filename} to {destination_path} from {bucket_name}"
