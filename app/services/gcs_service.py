from flask import Response
from google.cloud import bigquery
from google.cloud import storage
from app.config import Config

def download_blob(filename, override_bucket=None):
    client = storage.Client(project="hackathon-470421")
    bucket_name = override_bucket or Config.BUCKET_NAME
    print(bucket_name)
    destination_path = f"/tmp/{filename}"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    data = blob.download_as_bytes()
    mimetype = blob.content_type or 'application/octet-stream'
    return Response(
        data,
        mimetype=mimetype,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

def download_withkey():
    SERVICE_ACCOUNT_KEY_PATH = "C:\\Users\\prana\\Documents\\hackathon\\keyfile.json"
    BUCKET_NAME = "hack-team-eclipse-test-bucket"
    BLOB_NAME = "test.txt"
    client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_KEY_PATH)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    content = blob.download_as_text()
    print("File contents:")
    print(content)
def get_records_from_bq():
    client = bigquery.Client()

    query = """
        SELECT
          ID,
          data.name AS name,
          data.age AS age
        FROM `hack-team-eclipse.eclipse.ecilipse-test`
        LIMIT 10
    """

    results = client.query(query).result()

    return [
        {"id": row.ID, "name": row.name, "age": row.age}
        for row in results
    ]

def get_user_context(user_id: str) -> dict:
    client = bigquery.Client()

    query = """
        SELECT data
        FROM `hack-team-eclipse.eclipse.ecilipse-test`
        WHERE ID = @user_id
        LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    rows = list(query_job.result())

    if not rows:
        return {}

    row = rows[0]
    # The `data` field is expected to be a JSON object
    return dict(row["data"])