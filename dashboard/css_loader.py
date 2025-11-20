"""
CSS Loader Utility for IRAQAF Dashboard
Loads and injects CSS files into Streamlit
"""

import streamlit as st
from pathlib import Path


def load_css_file(css_file: str) -> None:
    """
    Load and inject a CSS file into the Streamlit app.
    
    Args:
        css_file: Path to the CSS file relative to dashboard directory
    """
    css_path = Path(__file__).parent / css_file
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {css_file}")


def load_main_styles() -> None:
    """Load the main stylesheet"""
    load_css_file('styles.css')

