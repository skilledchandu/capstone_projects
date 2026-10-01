"""
AI Battle Gesture Arena
Connect Gestures to AI Magic

Left panel: webcam or upload, gesture prediction, mapped battle move.
Right panel: unlocked move, AI move description (Groq if GROQ_API_KEY is set),
and a matching action image (Hugging Face if HF_TOKEN is set, otherwise a drawn card).
"""

import os
from pathlib import Path

import numpy as np
import requests
import streamlit as st
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model" / "keras_model.h5"
LABELS_PATH = ROOT / "model" / "labels.txt"

MOVES = {
    "open_palm": ("Aegis Wall", "a glowing shield snapping open in a stone arena"),
    "fist": ("Quake Jab", "a fighter punching the ground and sending a ripple of dust"),
    "peace": ("Dual Flash", "two bright sparks crossing in front of a young hero"),
    "point": ("Line Shot", "a focused beam of light leaving a pointed fingertip"),
    "unknown": ("Ready Stance", "a hero standing calmly in a temple arena"),
}


def demo_classify(image: Image.Image) -> tuple[str, float]:
    rgb = np.asarray(image.convert("RGB").resize((160, 120)))
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    skin = (r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b)
    ratio = float(skin.mean())
    if ratio < 0.04:
        return "unknown", 0.4
    width = skin.any(axis=0).mean()
    height = skin.any(axis=1).mean()
    if width > 0.45 and height > 0.4:
        return "open_palm", 0.8
    if width < 0.28:
        return "point", 0.74
    if width < 0.36:
        return "fist", 0.76
    return "peace", 0.72


def predict(image: Image.Image) -> tuple[str, float]:
    try:
        import tensorflow as tf
        if MODEL_PATH.exists():
            model = tf.keras.models.load_model(str(MODEL_PATH))
            arr = np.asarray(image.convert("RGB").resize((224, 224)), dtype=np.float32)
            arr = np.expand_dims((arr / 127.5) - 1.0, 0)
            probs = model.predict(arr, verbose=0)[0]
            labels = []
            if LABELS_PATH.exists():
                labels = [ln.split(" ", 1)[-1].strip().lower().replace(" ", "_") for ln in LABELS_PATH.read_text().splitlines() if ln.strip()]
            index = int(np.argmax(probs))
            label = labels[index] if index < len(labels) else "unknown"
            return (label if label in MOVES else "unknown"), float(probs[index])
    except Exception:
        pass
    return demo_classify(image)


def describe_move(move: str, prompt_scene: str) -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    prompt = (
        f"Write 2 short family-friendly sentences describing the battle move '{move}': {prompt_scene}. "
        "No violence details. Suitable for students."
    )
    if not api_key:
        return f"{move}: the hero uses a clean, bright technique. {prompt_scene.capitalize()}."
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 120,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        return f"{move}: the hero uses a clean, bright technique. (AI fallback: {exc})"


def action_image(move: str, scene: str) -> Image.Image:
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        try:
            response = requests.post(
                "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0",
                headers={"Authorization": f"Bearer {token}"},
                json={"inputs": f"family-friendly game art, {move}, {scene}, bright colors, no text"},
                timeout=60,
            )
            if response.ok and response.headers.get("content-type", "").startswith("image"):
                from io import BytesIO
                return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception:
            pass
    card = Image.new("RGB", (768, 432), (24, 32, 54))
    draw = ImageDraw.Draw(card)
    draw.ellipse((80, 60, 320, 300), fill=(255, 206, 84))
    draw.rectangle((140, 250, 250, 400), fill=(64, 110, 190))
    draw.text((360, 160), move, fill=(255, 255, 255))
    draw.text((360, 210), "Action art", fill=(200, 220, 255))
    return card


st.set_page_config(page_title="AI Battle Gesture Arena", layout="wide")
st.title("AI Battle Gesture Arena")
st.caption("Left: gesture capture. Right: unlocked move, AI description, battle art.")

left, right = st.columns(2)
with left:
    st.subheader("Gesture capture")
    source = st.radio("Source", ["Webcam", "Upload"], horizontal=True)
    image = None
    if source == "Webcam":
        shot = st.camera_input("Show your battle gesture")
        if shot:
            image = Image.open(shot)
    else:
        upload = st.file_uploader("Upload a gesture", type=["png", "jpg", "jpeg"])
        if upload:
            image = Image.open(upload)
    if image:
        st.image(image, use_container_width=True)
        key, conf = predict(image)
        st.session_state["result"] = (key, conf)

with right:
    st.subheader("Unlocked move")
    if "result" not in st.session_state:
        st.info("Capture a gesture on the left.")
    else:
        key, conf = st.session_state["result"]
        move, scene = MOVES[key]
        st.metric("Move", move, f"{conf:.0%} confidence")
        st.write(describe_move(move, scene))
        st.image(action_image(move, scene), caption="Generated battle art", use_container_width=True)
        st.caption("Set GROQ_API_KEY and HF_TOKEN to use live Groq text and Hugging Face images.")
