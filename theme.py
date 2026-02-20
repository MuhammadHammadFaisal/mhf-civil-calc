# theme.py
import streamlit as st
from PIL import Image
import os

def prepare_icon(im, final_size=64):
    """Makes the image square and resizes it for the favicon."""
    x, y = im.size
    size = max(x, y)
    new_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    return new_im.resize((final_size, final_size), Image.LANCZOS)

def load_icon():
    """Loads the MHF Civil Calc sticker as the favicon."""
    try:
        icon_path = os.path.join("assets", "Sticker.png")
        icon_img = Image.open(icon_path).convert("RGBA")
        return prepare_icon(icon_img, 64)
    except:
        return "🛠️"

def apply_theme(page_title="MHF Civil Calc"):
    """Injects the global CSS and sets the page config. Call this first on main pages."""
    st.set_page_config(page_title=page_title, layout="wide", page_icon=load_icon())

    st.markdown("""
    <style>
    /* Blueprint Background */
    [data-testid="stAppViewContainer"] {
        background-color: #031126;
        background-image: 
            linear-gradient(to bottom, #031126 0%, #031126 40px, rgba(255,255,255,0.5) 40px, rgba(255,255,255,0.5) 42px, transparent 42px),
            radial-gradient(circle at 50% 40vh, rgba(20, 75, 150, 0.4) 0%, transparent 70%),
            linear-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
            linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            radial-gradient(circle at 100% 0%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
            radial-gradient(circle at 100% 0%, transparent 220px, rgba(255,255,255,0.05) 221px, transparent 222px),
            radial-gradient(circle at 0% 100%, transparent 250px, rgba(255,255,255,0.1) 251px, transparent 253px),
            radial-gradient(circle at 0% 100%, transparent 50px, rgba(255,255,255,0.15) 51px, transparent 53px);
        background-size: 100% 100%, 100% 100%, 75px 75px, 75px 75px, 15px 15px, 15px 15px, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        background-repeat: no-repeat, no-repeat, repeat, repeat, repeat, repeat, no-repeat, no-repeat, no-repeat, no-repeat;
        background-attachment: local;
    }

    /* Sidebar and Global Text */
    [data-testid="stSidebar"] {
        background-color: #031126;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3, h4, p, li, .stMarkdown {
        color: #E2E8F0 !important;
    }

    /* Glassy Cards and Links */
    [data-testid="stPageLink-NavLink"] {
        background-color: rgba(255,255,255,0.85) !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        padding: 18px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stPageLink-NavLink"] p {
        color: #212529 !important; 
        font-size: 17px !important;
        font-weight: 600 !important;
        text-align: center !important;
        width: 100% !important;
    }
    [data-testid="stPageLink-NavLink"] svg, [data-testid="stHeaderAction"] {
        display: none !important;
    }
    
    /* Buttons */
    [data-testid="stLinkButton"] > a {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #1a3a5a !important; 
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_page_header(title):
    """Standardizes the large header with the logo across all pages."""
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")
    with col_logo:
        try:
            st.image(os.path.join("assets", "Sticker.png"))
        except:
            pass # Fails gracefully if image isn't found
    with col_text:
        st.markdown(
            f"""
            <div style="padding-left: 15px;">
                <h1 style='font-size: 55px; margin: 0; line-height: 1.0; font-weight: 700;'>{title}</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

TEXT_STYLES = {
    "section_heading": {
        "size": "24px",
        "weight": "700",
        "color": "#aad4ff", # A nice light blue to stand out from the white text
        "margin": "20px 0px 10px 0px"
    },
    "subheading": {
        "size": "18px",
        "weight": "600",
        "color": "#E2E8F0",
        "margin": "15px 0px 5px 0px"
    },
    "working": {
        "size": "15px",
        "weight": "400",
        "color": "#CBD5E1", # Slightly dimmer for calculation logs/working
        "margin": "5px 0px"
    }
}

def write_text(text_type, content):
    """Pulls the style from TEXT_STYLES and renders it in Streamlit."""
    style = TEXT_STYLES.get(text_type, TEXT_STYLES["working"]) # Defaults to 'working'
    
    html = f"""
    <div style="
        font-size: {style['size']}; 
        font-weight: {style['weight']}; 
        color: {style['color']}; 
        margin: {style['margin']};
    ">
        {content}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
