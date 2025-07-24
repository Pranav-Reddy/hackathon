from flask import Blueprint, request, jsonify
from app.services.gcs_service import download_blob

gcs_bp = Blueprint('gcs', __name__)

@gcs_bp.route("/download/<filename>", methods=["GET"])
def download(filename):
    bucket = request.args.get("bucket")
    try:
        message = download_blob(filename, bucket)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
