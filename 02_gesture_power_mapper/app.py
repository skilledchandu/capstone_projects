"""
Gesture to Power Mapper
Build the Magic Gesture Recognizer

Streamlit app:
- capture from webcam or upload a hand photo
- recognise a gesture (Teachable Machine model if present, otherwise a built-in demo classifier)
- map the gesture to a game power

Drop an exported Teachable Machine Keras model at:
    model/keras_model.h5
and labels at:
    model/labels.txt
"""

from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

try:
    import tensorflow as tf
except ImportError:  # app still runs with the demo classifier
    tf = None


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model" / "keras_model.h5"
LABELS_PATH = ROOT / "model" / "labels.txt"

POWERS = {
    "open_palm": {
        "name": "Shield Bloom",
        "element": "Light",
        "effect": "Raises a bright barrier for 3 seconds.",
        "color": (86, 168, 255),
    },
    "fist": {
        "name": "Stone Pulse",
        "element": "Earth",
        "effect": "Sends a short ground shock in front of you.",
        "color": (196, 140, 74),
    },
    "peace": {
        "name": "Twin Spark",
        "element": "Lightning",
        "effect": "Fires two small sparks that chain once.",
        "color": (255, 214, 64),
    },
    "point": {
        "name": "Arrow Gleam",
        "element": "Wind",
        "effect": "Aims a fast wind dart at the nearest target.",
        "color": (120, 220, 160),
    },
    "unknown": {
        "name": "Calm Aura",
        "element": "Neutral",
        "effect": "No special move yet. Try a clearer hand shape.",
        "color": (160, 160, 170),
    },
}


@st.cache_resource
def load_model():
    if tf is None or not MODEL_PATH.exists():
        return None, None
    model = tf.keras.models.load_model(str(MODEL_PATH))
    labels = []
    if LABELS_PATH.exists():
        for line in LABELS_PATH.read_text(encoding="utf-8").splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            # Teachable Machine labels look like "0 Open Palm"
            parts = cleaned.split(" ", 1)
            labels.append(parts[1].strip().lower().replace(" ", "_") if len(parts) == 2 else cleaned.lower())
    return model, labels


def demo_classify(image: Image.Image) -> tuple[str, float]:
    """Small built-in classifier so the project runs before a model is trained.

    It looks at how much of the frame is skin-toned and how wide that region is.
    Replace this with the Teachable Machine model for the real assignment.
    """
    rgb = np.asarray(image.convert("RGB").resize((160, 120)))
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    skin = (r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b) & ((r.astype(int) - g.astype(int)) > 15)
    ratio = float(skin.mean())
    if ratio < 0.04:
        return "unknown", 0.42
    cols = skin.any(axis=0)
    rows = skin.any(axis=1)
    width = int(cols.sum()) / max(1, cols.shape[0])
    height = int(rows.sum()) / max(1, rows.shape[0])
    if width > 0.45 and height > 0.45:
        return "open_palm", min(0.95, 0.55 + ratio)
    if width < 0.28 and height > 0.35:
        return "point", min(0.9, 0.5 + ratio)
    if width < 0.36:
        return "fist", min(0.9, 0.5 + ratio)
    return "peace", min(0.88, 0.5 + ratio)


def predict(image: Image.Image) -> tuple[str, float]:
    model, labels = load_model()
    if model is None:
        return demo_classify(image)
    arr = np.asarray(image.convert("RGB").resize((224, 224)), dtype=np.float32)
    arr = (arr / 127.5) - 1.0
    arr = np.expand_dims(arr, axis=0)
    probs = model.predict(arr, verbose=0)[0]
    index = int(np.argmax(probs))
    label = labels[index] if labels and index < len(labels) else list(POWERS.keys())[min(index, 3)]
    key = label if label in POWERS else "unknown"
    return key, float(probs[index])


def make_card(power: dict, confidence: float) -> Image.Image:
    card = Image.new("RGB", (720, 360), (18, 24, 38))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((24, 24, 696, 336), radius=24, fill=power["color"])
    draw.rounded_rectangle((40, 40, 680, 320), radius=18, fill=(255, 255, 255))
    draw.text((64, 70), power["name"], fill=(20, 24, 36))
    draw.text((64, 130), f"Element: {power['element']}", fill=(40, 48, 70))
    draw.text((64, 180), power["effect"], fill=(40, 48, 70))
    draw.text((64, 240), f"Confidence: {confidence:.0%}", fill=(40, 48, 70))
    return card


st.set_page_config(page_title="Gesture to Power Mapper", page_icon="✨", layout="wide")
st.title("Gesture to Power Mapper")
st.caption("Magic Gesture Recognizer — webcam or upload, then map the hand shape to a power.")

left, right = st.columns(2)
with left:
    st.subheader("Input")
    source = st.radio("Source", ["Webcam", "Upload"], horizontal=True)
    image = None
    if source == "Webcam":
        shot = st.camera_input("Show a hand gesture")
        if shot is not None:
            image = Image.open(shot)
    else:
        upload = st.file_uploader("Upload a hand photo", type=["png", "jpg", "jpeg"])
        if upload is not None:
            image = Image.open(upload)
    if image is not None:
        st.image(image, caption="Captured gesture", use_container_width=True)

with right:
    st.subheader("Unlocked power")
    if image is None:
        st.info("Capture or upload a gesture to begin.")
    else:
        key, confidence = predict(image)
        power = POWERS[key]
        st.metric("Move", power["name"])
        st.write(f"**Element:** {power['element']}")
        st.write(power["effect"])
        st.progress(min(1.0, confidence))
        st.image(make_card(power, confidence), caption="Power card", use_container_width=True)
        if load_model()[0] is None:
            st.warning("Demo classifier is active. Add model/keras_model.h5 for Teachable Machine predictions.")
