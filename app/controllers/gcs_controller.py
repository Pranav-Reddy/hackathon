from flask import Blueprint, request, jsonify
from app.services.gcs_service import download_blob
from app.services.gcs_service import get_records_from_bq
from flask import Blueprint, request, jsonify
from app.services.vision_service import analyze_image
from app.services.gcs_service import get_user_context
from app.services.gemini_service import generate_answer

gcs_bp = Blueprint('gcs', __name__)
bq_bp = Blueprint("bq_bp", __name__)
image_qna_bp = Blueprint("image_qna_bp", __name__)

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

@image_qna_bp.route("/image-qna/<user_id>", methods=["POST"])
def image_qna(user_id):
    try:
        if "image" not in request.files:
            return jsonify({"error": "Missing image"}), 400

        image_file = request.files["image"]
        image_bytes = image_file.read()

        ocr_text, labels = analyze_image(image_bytes)
        user_context = get_user_context(user_id)
        response_text = generate_answer(ocr_text, labels, user_context)

        return jsonify({"answer": response_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500