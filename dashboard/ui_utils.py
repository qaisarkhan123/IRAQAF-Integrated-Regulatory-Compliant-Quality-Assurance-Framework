"""
UI utility functions for better user experience.
"""

import streamlit as st
from typing import Optional
import time


def show_toast(message: str, icon: str = "ℹ️", duration: int = 3):
    """
    Show a temporary toast notification.

    Args:
        message: Message to display
        icon: Emoji icon
        duration: Seconds to display (simulation only)
    """
    # Streamlit doesn't have native toasts yet, so we use a temporary container
    toast_container = st.empty()

    toast_container.markdown(
        f"""
        <div style='
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        '>
            <span style='font-size: 1.2rem; margin-right: 8px;'>{icon}</span>
            <span>{message}</span>
        </div>
        <style>
        @keyframes slideIn {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Note: In a real app, you'd use JavaScript or st.experimental_rerun
    # For now, this is a visual indicator
    time.sleep(duration)
    toast_container.empty()


def show_success(message: str):
    """Show success message with icon."""
    st.success(f"✅ {message}")


def show_error(message: str, details: Optional[str] = None):
    """Show error message with optional details."""
    st.error(f"❌ {message}")
    if details:
        with st.expander("🔍 Error Details"):
            st.code(details, language="text")


def show_warning(message: str):
    """Show warning message with icon."""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Show info message with icon."""
    st.info(f"ℹ️ {message}")


def confirm_action(message: str, key: str) -> bool:
    """
    Show a confirmation dialog.

    Args:
        message: Confirmation message
        key: Unique key for the dialog

    Returns:
        True if confirmed, False otherwise
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.warning(message)

    with col2:
        if st.button("✓ Confirm", key=f"{key}_confirm"):
            return True
        if st.button("✗ Cancel", key=f"{key}_cancel"):
            return False

    return False
