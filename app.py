import streamlit as st
import requests
import json
from PIL import Image, UnidentifiedImageError

st.set_page_config(page_title="Image to JSON Extractor with OCR.space", layout="centered")

st.title("🧠 Image to JSON Extractor with OCR.space API")
st.write("Upload an image and get back OCR data in JSON format using OCR.space API.")

# Load your OCR.space API key securely from Streamlit secrets
OCR_SPACE_API_KEY = st.secrets["OCR_SPACE_API_KEY"]

def ocr_space_api(image_bytes):
    payload = {
        'apikey': OCR_SPACE_API_KEY,
        'language': 'eng',
        'isOverlayRequired': True,  # This gives positional data if you want it
        'OCREngine': 2,  # Use OCR Engine 2 (LSTM) for better accuracy
    }
    files = {'file': image_bytes}
    response = requests.post('https://api.ocr.space/parse/image', data=payload, files=files)
    result = response.json()
    return result

uploaded_file = st.file_uploader("📤 Choose an image", type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Uploaded Image", use_container_width=True)
    except UnidentifiedImageError:
        st.error("❌ The uploaded file is not a valid image. Please upload a PNG, JPG, or BMP file.")
        st.stop()

    if st.button("🧠 Extract Text Layout"):
        with st.spinner("Running OCR..."):
            ocr_result = ocr_space_api(uploaded_file.getvalue())

            # Show full raw JSON result from OCR.space
            st.subheader("Raw OCR JSON Result")
            st.json(ocr_result)

            # Extract parsed text lines with position if available
            parsed_results = ocr_result.get("ParsedResults", [])
            if parsed_results:
                parsed_text = parsed_results[0].get("ParsedText", "")
                st.subheader("Extracted Text")
                st.text_area("Text from image:", parsed_text, height=200)

                # Optional: return OCR overlay info (bounding boxes etc.)
                # You can customize how to transform this into JSON for Elementor here

            else:
                st.error("❌ No parsed OCR results found.")

