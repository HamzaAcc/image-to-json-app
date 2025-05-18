import streamlit as st
import requests
from PIL import Image, UnidentifiedImageError
import json
import base64
import io

st.set_page_config(page_title="🧠 Image to Elementor JSON", layout="centered")

st.title("🧠 Image to Elementor JSON Generator")
st.write("Upload a screenshot of a website layout to generate Elementor-compatible JSON.")

# Load API key from Streamlit secrets
OCR_KEY = st.secrets["OCR_SPACE_API_KEY"]

uploaded_file = st.file_uploader("📤 Choose an image", type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Uploaded Image", use_container_width=True)
    except UnidentifiedImageError:
        st.error("❌ Invalid image format.")
        st.stop()

    if st.button("🔍 Scan and Generate JSON"):
        with st.spinner("Sending image to OCR.space..."):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            url = "https://api.ocr.space/parse/image"
            headers = {'apikey': OCR_KEY}
            payload = {
                'base64Image': f'data:image/png;base64,{img_base64}',
                'language': 'eng',
                'OCREngine': '2'
            }

            response = requests.post(url, data=payload, headers=headers)
            result = response.json()

            try:
                parsed_text = result['ParsedResults'][0]['ParsedText']
            except (KeyError, IndexError):
                st.error("❌ OCR failed or no text found.")
                st.stop()

        st.success("✅ OCR Completed!")
        st.text_area("📝 Extracted Text", parsed_text, height=200)

        # Simple conversion to Elementor section (basic)
        elementor_json = {
            "version": "1.0",
            "title": uploaded_file.name,
            "content": [
                {
                    "type": "section",
                    "elements": [
                        {
                            "type": "widget",
                            "widgetType": "text-editor",
                            "settings": {
                                "editor": parsed_text
                            }
                        }
                    ]
                }
            ]
        }

        json_str = json.dumps(elementor_json, indent=2)
        st.download_button("📥 Download Elementor JSON", data=json_str,
                           file_name="elementor_layout.json", mime="application/json")
        st.code(json_str, language="json")
