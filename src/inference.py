import os
from pathlib import Path

import mlflow
import mlflow.keras
import numpy as np
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Configure model source
MODEL_URI = os.getenv(
    "MODEL_URI",
    "models:/VisionGuard_MobileNetV2@champion"
)

LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH")

if LOCAL_MODEL_PATH:
    print("Loading local VisionGuard model...")
    model = mlflow.keras.load_model(LOCAL_MODEL_PATH)
else:
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    print("Loading VisionGuard champion model from DagsHub...")
    model = mlflow.keras.load_model(MODEL_URI)

print("Champion model loaded successfully.")

def predict_image(image):
    """
    Accepts a PIL image and returns a prediction
    label and confidence score.
    """

    # Match training preprocessing
    image = image.convert("RGB")
    image = image.resize((224, 224))

    image_array = np.asarray(
        image, dtype=np.float32
    ) / 255.0

    image_array = np.expand_dims(
        image_array, axis=0
    )

    # Generate prediction
    ai_probability = float(
        model.predict(image_array, verbose=0)[0][0]
    )

    # Label mapping: 0 = Real, 1 = AI-generated
    if ai_probability >= 0.5:
        label = "AI-generated"
        confidence = ai_probability
    else:
        label = "Real"
        confidence = 1 - ai_probability

    return {
        "label": label,
        "confidence": round(confidence * 100, 2),
        "ai_probability": round(ai_probability * 100, 2)
    }
