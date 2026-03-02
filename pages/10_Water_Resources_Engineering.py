import streamlit as st
from theme import apply_theme
apply_theme("Water Resources Engineering")
def app():
  
    
    st.title("🚧 Module Under Construction")
    st.markdown("---")

    col1, col2 = st.columns([1, 2])
    
        
    st.info("Expected Release: Fall 2026")
    st.progress(0.1, text="Coding in progress...")

if __name__ == "__main__":
    app()
