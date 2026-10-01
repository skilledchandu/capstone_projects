"""
AI Combo Card Generator
Develop the Complete Gesture-to-Magic Studio

Left panel: webcam or upload.
Right panel: combo name, AI narration, scene image, and a final card made with PIL.
"""

import os
from io import BytesIO

import numpy as np
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

COMBOS = {
    "open_palm": ("Dawn Guard Combo", "open palms lifting a ring of light over a quiet courtyard"),
    "fist": ("Mountain Meter Combo", "a steady fist planting a glowing marker on stone tiles"),
    "peace": ("Twin Star Combo", "two fingers tracing a small star in the evening sky"),
    "point": ("Pathfinder Combo", "a pointed finger drawing a bright trail across a map"),
    "unknown": ("Practice Combo", "a student reviewing hand shapes in a bright studio"),
}


def demo_classify(image: Image.Image) -> str:
    rgb = np.asarray(image.convert("RGB").resize((160, 120)))
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    skin = (r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b)
    if float(skin.mean()) < 0.04:
        return "unknown"
    width = float(skin.any(axis=0).mean())
    if width > 0.45:
        return "open_palm"
    if width < 0.28:
        return "point"
    if width < 0.36:
        return "fist"
    return "peace"


def narrate(combo: str, scene: str) -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    fallback = f"{combo} begins. {scene.capitalize()}. The studio light settles, and the combo card is ready."
    if not key:
        return fallback
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{
                    "role": "user",
                    "content": f"Write 2 family-friendly sentences of narration for '{combo}': {scene}.",
                }],
                "max_tokens": 100,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return fallback


def scene_image(combo: str) -> Image.Image:
    img = Image.new("RGB", (640, 360), (32, 48, 82))
    draw = ImageDraw.Draw(img)
    draw.ellipse((40, 40, 220, 220), fill=(255, 214, 92))
    draw.polygon([(80, 300), (180, 160), (300, 300)], fill=(72, 120, 86))
    draw.rectangle((360, 80, 600, 280), outline=(255, 255, 255), width=4)
    draw.text((380, 150), combo, fill=(255, 255, 255))
    return img


def build_card(combo: str, narration: str, scene: Image.Image) -> Image.Image:
    card = Image.new("RGB", (900, 1200), (245, 238, 220))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((30, 30, 870, 1170), radius=28, outline=(40, 40, 50), width=6)
    draw.rectangle((60, 70, 840, 150), fill=(28, 42, 74))
    draw.text((80, 95), combo, fill=(255, 248, 220))
    scene_fit = scene.resize((780, 420))
    card.paste(scene_fit, (60, 180))
    draw.multiline_text((80, 640), narration[:280], fill=(30, 30, 40), spacing=8)
    draw.text((80, 1080), "Gesture-to-Magic Studio", fill=(90, 70, 40))
    return card


st.set_page_config(page_title="AI Combo Card Generator", layout="wide")
st.title("AI Combo Card Generator")
st.caption("Gesture in, combo card out.")

left, right = st.columns(2)
with left:
    st.subheader("Input")
    mode = st.radio("Source", ["Webcam", "Upload"], horizontal=True)
    image = None
    if mode == "Webcam":
        shot = st.camera_input("Capture a gesture")
        if shot:
            image = Image.open(shot)
    else:
        upload = st.file_uploader("Upload", type=["png", "jpg", "jpeg"])
        if upload:
            image = Image.open(upload)
    if image:
        st.image(image, use_container_width=True)

with right:
    st.subheader("Combo studio")
    if not image:
        st.info("Add a gesture on the left.")
    else:
        key = demo_classify(image)
        combo, scene = COMBOS[key]
        text = narrate(combo, scene)
        art = scene_image(combo)
        card = build_card(combo, text, art)
        st.write(f"**Combo name:** {combo}")
        st.write(text)
        st.image(art, caption="AI scene image", use_container_width=True)
        st.image(card, caption="Final PIL combo card", use_container_width=True)
        buffer = BytesIO()
        card.save(buffer, format="PNG")
        st.download_button("Download card", buffer.getvalue(), file_name="combo_card.png", mime="image/png")
