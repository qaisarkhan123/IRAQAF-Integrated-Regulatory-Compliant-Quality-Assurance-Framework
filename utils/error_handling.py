"""
File: utils/error_handling.py
Centralized error handling and user-friendly error messages
"""

import logging
import traceback
import streamlit as st
from datetime import datetime

logger = logging.getLogger(__name__)


def show_error_inline(e: Exception, context: str, show_recovery_tips: bool = True):
    """
    Display user-friendly error message with recovery tips.
    
    Args:
        e: The exception that occurred
        context: User-friendly description of what failed
        show_recovery_tips: Whether to show recovery suggestions
    """
    error_id = f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    tb = "".join(traceback.format_exception_only(type(e), e)).strip()
    
    logger.error(f"{error_id} | {context}: {e}", exc_info=True)
    
    st.error(f"❌ **{context}**")
    
    with st.expander("🔍 Error Details & Recovery Tips", expanded=False):
        st.code(tb, language="text")
        
        if show_recovery_tips:
            error_type = type(e).__name__
            
            if error_type == "FileNotFoundError":
                st.info("""
                **Recovery Tips:**
                - ✅ Verify the file exists in the expected location
                - ✅ Check file permissions (read access required)
                - ✅ Re-run evaluation to regenerate missing files
                - ✅ Check the path for typos
                """)
                
            elif error_type == "JSONDecodeError":
                st.info("""
                **Recovery Tips:**
                - ✅ File may be corrupted - try regenerating it
                - ✅ Check for manual edits that broke JSON syntax
                - ✅ Use a JSON validator (https://jsonlint.com)
                - ✅ Look for missing commas, brackets, or quotes
                """)
                
            elif error_type == "PermissionError":
                st.info("""
                **Recovery Tips:**
                - ✅ Close programs that might be using the file
                - ✅ Run with administrator privileges
                - ✅ Check folder permissions
                """)
                
            else:
                st.info("""
                **Recovery Tips:**
                - ✅ Check logs/dashboard.log for details
                - ✅ Try refreshing the page
                - ✅ Contact support with Error ID below
                """)
        
        st.caption(f"**Error ID:** `{error_id}` • **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")