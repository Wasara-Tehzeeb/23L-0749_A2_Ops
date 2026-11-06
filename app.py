import base64
from io import BytesIO

import uuid
import os
import requests
from pathlib import Path

from PIL import Image
from flask import Flask, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from src.inference import predict_image, MODEL_URI
from src.database import init_db, save_prediction, get_predictions

BASE_DIR = Path(__file__).resolve().parent

CLOUD_API_URL = os.environ.get(
    "VISIONGUARD_CLOUD_API_URL",
    "https://except-surfing-opening-percentage.trycloudflare.com/api/predict"
)

CLOUD_API_KEY = os.environ.get("VISIONGUARD_API_KEY")

app = Flask(__name__)
init_db()

UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "application": "VisionGuard",
        "message": "Flask application is running"
    }, 200

@app.route("/history")
def history():
    records = get_predictions()
    return render_template("history.html", records=records)

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return render_template(
            "error.html",
            message="Please select an image before submitting."
        ), 400

    file = request.files["image"]

    if not file.filename or not allowed_file(file.filename):
        return render_template(
            "error.html",
            message="Unsupported file type. Please upload a JPG, PNG, GIF, or WebP image."
        ), 400

    filename = uuid.uuid4().hex + "_" + secure_filename(file.filename)

    try:
        with Image.open(file.stream) as image:
            image.load()
            if not CLOUD_API_KEY:
                raise RuntimeError("VISIONGUARD_API_KEY is not configured")

            buffer_api = BytesIO()
            image.convert("RGB").save(buffer_api, format="JPEG")
            buffer_api.seek(0)

            response = requests.post(
                CLOUD_API_URL,
                headers={"X-API-Key": CLOUD_API_KEY},
                files={"image": ("upload.jpg", buffer_api, "image/jpeg")},
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            # Create an image preview entirely in memory
            buffer = BytesIO()
            image.convert("RGB").save(buffer, format="JPEG")

            encoded_image = base64.b64encode(
            buffer.getvalue()
            ).decode("utf-8")

            image_url = "data:image/jpeg;base64," + encoded_image

    except (OSError, ValueError):
        return render_template(
            "error.html",
            message="This image could not be opened. Please upload a valid, uncorrupted image."
        ), 400

    save_prediction(
        filename=secure_filename(file.filename),
        prediction=result["label"],
        confidence=result["confidence"],
        model_name=MODEL_URI
    )

    return render_template(
        "result.html",
        image_url=image_url,
        prediction=result["label"],
        probability=result["ai_probability"],
        confidence=result["confidence"]
    )

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error):
    return render_template(
        "error.html",
        message="File is too large. Maximum allowed size is 10 MB."
    ), 413

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
        use_reloader=False
    )
