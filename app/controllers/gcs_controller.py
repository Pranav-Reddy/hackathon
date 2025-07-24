from flask import Blueprint, request, jsonify
from app.services.gcs_service import download_blob
from app.services.gcs_service import get_records_from_bq

gcs_bp = Blueprint('gcs', __name__)
bq_bp = Blueprint("bq_bp", __name__)

@gcs_bp.route("/download/<filename>", methods=["GET"])
def download(filename):
    bucket = request.args.get("bucket")
    try:
        return download_blob(filename, bucket)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bq_bp.route("/records", methods=["GET"])
def get_records():
    try:
        records = get_records_from_bq()
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
