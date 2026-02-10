import streamlit as st

st.set_page_config(
    page_title="MHF Civil Calc",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- CSS (SAFE + FIXED) --------------------
st.markdown("""
<style>

/* Apply background ONLY to app body */
.stApp {
    background:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,0.08), transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(255,255,255,0.06), transparent 40%),
        linear-gradient(
            rgba(255,255,255,0.08) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,0.08) 1px,
            transparent 1px
        ),
        linear-gradient(135deg, #0b2d4f, #061b33);
    background-size:
        auto,
        auto,
        40px 40px,
        40px 40px,
        cover;
}

/* Keep Streamlit default UI SAFE */
header, footer, .stToolbar {
    background: transparent !important;
}

/* Force white text ONLY inside main app content */
main, main * {
    color: #ffffff !important;
}

/* Buttons */
.stButton>button {
    background-color: rgba(255,255,255,0.9);
    color: #0b2d4f !important;
    border-radius: 12px;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    border: none;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 2rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.35);
}

</style>
""", unsafe_allow_html=True)

# -------------------- HERO SECTION --------------------
col1, col2 = st.columns([1.2, 2])

with col1:
    st.image("mhf_logo.png", width=280)  # keep same logo

with col2:
    st.markdown("## **MHF Civil Calc**")
    st.markdown(
        "Verified numerical solvers aligned with standard undergraduate civil engineering coursework."
    )

st.markdown("---")

# -------------------- COURSE MODULES --------------------
st.markdown("### **Course Modules**")

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class="card">
        <h4>Reinforced Concrete Fundamentals</h4>
        <p>Design-oriented solvers with transparent assumptions and step-by-step logic.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
        <h4>Soil Mechanics</h4>
        <p>Bearing capacity, settlement, and stress distribution tools.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------- PURPOSE --------------------
st.markdown("### **Purpose**")
st.markdown(
    "MHF Civil Calc provides transparent numerical solutions to standard civil engineering problems. "
    "Each module follows established theory, clearly states assumptions, and presents intermediate steps "
    "to support learning, verification, and exam preparation."
)

st.markdown("---")

# -------------------- FEEDBACK --------------------
st.markdown("### **Feedback**")
st.markdown(
    "If you identify an incorrect result, unclear assumption, or missing topic, your feedback helps "
    "improve the reliability of this platform."
)
