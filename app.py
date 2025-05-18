import streamlit as st
from PIL import Image, UnidentifiedImageError
import pytesseract
import json

st.set_page_config(page_title="Image to JSON Extractor", layout="centered")

st.title("🧠 Image to JSON Extractor")
st.write("Upload an image and get back OCR data in JSON format.")

uploaded_file = st.file_uploader("📤 Choose an image", type=["png", "jpg", "jpeg", "bmp"])

image = None

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Uploaded Image", use_column_width=True)
    except UnidentifiedImageError:
        st.error("❌ The uploaded file is not a valid image. Please upload a PNG, JPG, or BMP file.")
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")

if image is not None:
    if st.button("🧠 Extract Text Layout"):
        with st.spinner("Running OCR..."):
            # Run pytesseract on the image
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            elements = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                # Filter out empty strings and low confidence texts
                if text and int(data['conf'][i]) > 60:
                    elements.append({
                        "text": text,
                        "left": data['left'][i],
                        "top": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i],
                        "confidence": int(data['conf'][i])
                    })

            result = {
                "image": uploaded_file.name,
                "elements": elements
            }
            json_data = json.dumps(result, indent=2)
            st.success("✅ Text layout extracted!")

            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=uploaded_file.name.rsplit('.', 1)[0] + "_layout.json",
                mime="application/json"
            )
            st.code(json_data, language="json")
