import streamlit as st
import requests
import openai
import json
from PIL import Image, UnidentifiedImageError

st.set_page_config(page_title="Image to Elementor JSON", layout="centered")

st.title("📷 ➜ 🧠 ➜ 🌐 Image to Elementor JSON")
st.write("Upload a screenshot of a website. We'll OCR the text and generate Elementor-compatible JSON.")

# Load secrets
OCR_KEY = st.secrets["OCR_SPACE_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

def run_ocr_space(image_bytes):
    payload = {
        'apikey': OCR_KEY,
        'language': 'eng',
        'isOverlayRequired': False,
    }
    files = {'file': image_bytes}
    response = requests.post('https://api.ocr.space/parse/image', data=payload, files=files)
    return response.json()

def generate_elementor_json(ocr_text):
    prompt = f"""
You are a web design assistant. Given this website text:

\"\"\"{ocr_text}\"\"\"

Generate a basic Elementor JSON layout compatible with WordPress. Use heading, paragraph, and button widgets appropriately. Only output clean JSON.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in Elementor and WordPress JSON layouts."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']

uploaded_file = st.file_uploader("📤 Upload website screenshot", type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
    except UnidentifiedImageError:
        st.error("Invalid image format.")
        st.stop()

    if st.button("🧠 Scan & Build Elementor JSON"):
        with st.spinner("Running OCR..."):
            ocr_result = run_ocr_space(uploaded_file.getvalue())
            parsed = ocr_result.get("ParsedResults", [])
            if not parsed:
                st.error("OCR failed or returned no results.")
                st.stop()
            ocr_text = parsed[0].get("ParsedText", "")
            st.subheader("📄 Extracted Text")
            st.text_area("OCR Result", ocr_text, height=200)

        with st.spinner("Generating Elementor JSON..."):
            elementor_json = generate_elementor_json(ocr_text)
            st.subheader("🌐 Elementor Layout (JSON)")
            st.code(elementor_json, language="json")

            st.download_button(
                label="📥 Download Elementor JSON",
                data=elementor_json,
                file_name="elementor_layout.json",
                mime="application/json"
            )
