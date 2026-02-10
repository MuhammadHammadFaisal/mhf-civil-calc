import streamlit as st
from PIL import Image
import base64
from io import BytesIO

# =========================================================
# Load favicon
# =========================================================
def prepare_icon(im_path, final_size=64):
    im = Image.open(im_path).convert("RGBA")
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0,0,0,0))
    new_im.paste(im, ((size-x)//2, (size-y)//2))
    new_im = new_im.resize((final_size, final_size), Image.LANCZOS)
    return new_im

try:
    icon_img = prepare_icon("assets/Sticker.png", 64)
except:
    icon_img = ""

# =========================================================
# Embed background as Base64
# =========================================================
def get_base64_image(path, max_size=(1920,1080)):
    img = Image.open(path)
    img.thumbnail(max_size, Image.LANCZOS)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode()

bg_base64 = get_base64_image("assets/blueprint.png")

# =========================================================
# App Config
# =========================================================
st.set_page_config(page_title="MHF Civil Calc", layout="wide", page_icon=icon_img)

# =========================================================
# CSS with embedded background
# =========================================================
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(rgba(26,58,90,0.3), rgba(26,58,90,0.3)),
                url("data:image/png;base64,{bg_base64}") no-repeat center center fixed;
    background-size: cover;
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# Minimal content to test
# =========================================================
st.title("MHF Civil Calc")
st.write("Background should now display correctly behind gradient!")
