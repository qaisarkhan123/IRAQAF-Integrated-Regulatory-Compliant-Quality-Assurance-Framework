"""
UX Enhancements Module for IRAQAF Dashboard
Features: Dark Mode, Loading Animations, Keyboard Shortcuts, Session Info
"""

import streamlit as st
from datetime import datetime
from typing import Callable, Optional

# ============================================================================
# 🎨 DARK MODE & THEME MANAGEMENT
# ============================================================================

def init_theme_state():
    """Initialize theme state in session"""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "theme_applied" not in st.session_state:
        st.session_state.theme_applied = False


def get_theme_css(dark_mode: bool) -> str:
    """Generate CSS for current theme"""
    if dark_mode:
        return """
        <style>
        /* Dark Mode */
        .stApp {
            background-color: #0e1117;
            color: #e6edf3;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #161b22;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f6feb;
        }
        .streamlit-expanderHeader {
            background-color: #21262d;
        }
        .element-container {
            background-color: transparent;
        }
        [data-testid="stMetric"] {
            background-color: #161b22;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
        """
    else:
        return """
        <style>
        /* Light Mode (Default) */
        .stApp {
            background-color: #ffffff;
            color: #262730;
        }
        [data-testid="stMetric"] {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
        """


def render_theme_toggle():
    """Render theme toggle button"""
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🌓 Toggle Dark Mode", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    with col2:
        theme_text = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"
        st.markdown(f"**Current: {theme_text}**")


# ============================================================================
# ⚡ LOADING ANIMATIONS
# ============================================================================

def show_loading_spinner(message: str = "Loading..."):
    """Show a loading spinner with message"""
    with st.spinner(message):
        return True


def render_progress_bar(current: int, total: int, label: str = "Progress"):
    """Render a progress bar"""
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{label}: {current}/{total}")


def animate_metric_change(old_value: float, new_value: float, label: str = "Value"):
    """Animate metric change with visual indicator"""
    delta = new_value - old_value
    delta_color = "green" if delta > 0 else "red" if delta < 0 else "gray"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label, f"{new_value:.2f}")
    with col2:
        st.metric("Change", f"{delta:+.2f}")
    with col3:
        st.metric("% Change", f"{(delta/old_value)*100:+.1f}%" if old_value != 0 else "N/A")


# ============================================================================
# ⌨️ KEYBOARD SHORTCUTS
# ============================================================================

def get_keyboard_shortcuts() -> dict:
    """Return dictionary of keyboard shortcuts"""
    return {
        "Ctrl+E": "Quick Export",
        "Ctrl+U": "Upload Evidence",
        "Ctrl+S": "Save Session",
        "Ctrl+/": "Search Evidence",
        "Alt+D": "Toggle Dark Mode",
        "Esc": "Close Sidebar",
        "?": "Show Help",
    }


def render_keyboard_shortcuts():
    """Render keyboard shortcuts help panel"""
    shortcuts = get_keyboard_shortcuts()
    
    st.markdown("### ⌨️ Keyboard Shortcuts")
    
    cols = st.columns(2)
    for idx, (shortcut, action) in enumerate(shortcuts.items()):
        with cols[idx % 2]:
            st.markdown(f"**{shortcut}** → {action}")
    
    st.markdown("---")
    st.info("💡 Tip: Press `?` to show this help panel anytime")


# ============================================================================
# 👤 SESSION & USER INFO
# ============================================================================

def init_session_state():
    """Initialize session state tracking"""
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()
    if "actions_count" not in st.session_state:
        st.session_state.actions_count = 0


def get_session_duration() -> str:
    """Get formatted session duration"""
    if "session_start" not in st.session_state:
        return "Unknown"
    
    duration = datetime.now() - st.session_state.session_start
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {duration.seconds % 60}s"


def render_session_info():
    """Render session information widget"""
    st.markdown("### 📊 Session Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Session Duration",
            get_session_duration(),
            help="Time since dashboard opened"
        )
    
    with col2:
        st.metric(
            "Actions Performed",
            st.session_state.get("actions_count", 0),
            help="Number of actions in this session"
        )
    
    with col3:
        last_activity = st.session_state.get("last_activity", datetime.now())
        time_since_activity = datetime.now() - last_activity
        st.metric(
            "Last Activity",
            f"{int(time_since_activity.total_seconds())}s ago",
            help="Time since last user action"
        )
    
    st.divider()


def increment_action_count():
    """Increment action counter"""
    if "actions_count" not in st.session_state:
        st.session_state.actions_count = 0
    st.session_state.actions_count += 1
    st.session_state.last_activity = datetime.now()


# ============================================================================
# 🎯 ENHANCED METRICS & DASHBOARD COMPONENTS
# ============================================================================

def render_quick_stats(stats: dict):
    """Render quick statistics dashboard"""
    st.markdown("### 📈 Quick Stats")
    
    cols = st.columns(len(stats))
    for idx, (label, (value, delta, icon)) in enumerate(stats.items()):
        with cols[idx]:
            st.metric(label, value, delta=delta, help=f"{icon} {label}")


def render_action_buttons(actions: dict[str, Callable]):
    """Render action buttons in a organized layout"""
    cols = st.columns(len(actions))
    results = {}
    
    for idx, (label, callback) in enumerate(actions.items()):
        with cols[idx]:
            if st.button(label, use_container_width=True):
                results[label] = callback()
                st.success(f"✅ {label} completed!")
                increment_action_count()
    
    return results


def render_info_cards(cards: dict[str, dict]):
    """Render information cards with icons and descriptions"""
    cols = st.columns(min(3, len(cards)))
    
    for idx, (title, card_data) in enumerate(cards.items()):
        with cols[idx % len(cols)]:
            icon = card_data.get("icon", "📌")
            description = card_data.get("description", "")
            color = card_data.get("color", "info")
            
            if color == "success":
                st.success(f"{icon} **{title}**\n{description}")
            elif color == "warning":
                st.warning(f"{icon} **{title}**\n{description}")
            elif color == "error":
                st.error(f"{icon} **{title}**\n{description}")
            else:
                st.info(f"{icon} **{title}**\n{description}")


# ============================================================================
# 🎨 CUSTOM STYLING HELPERS
# ============================================================================

def inject_custom_css():
    """Inject custom CSS for enhanced styling"""
    custom_css = """
    <style>
    /* Smooth transitions */
    * {
        transition: all 0.3s ease-in-out;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Enhanced cards */
    .stCard {
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 1.5rem;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Enhanced metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Smooth expandable sections */
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .badge-success {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .badge-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .badge-info {
        background-color: #dbeafe;
        color: #0c4a6e;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ============================================================================
# 🔧 INITIALIZATION
# ============================================================================

def initialize_ux_enhancements():
    """Initialize all UX enhancements"""
    init_theme_state()
    init_session_state()
    inject_custom_css()
    
    # Apply theme CSS
    if st.session_state.dark_mode:
        st.markdown(get_theme_css(True), unsafe_allow_html=True)
    
    return True


# ============================================================================
# 📋 HELPFUL UTILITIES
# ============================================================================

def render_toast_notification(message: str, notification_type: str = "info"):
    """Render a toast-like notification"""
    if notification_type == "success":
        st.success(f"✅ {message}")
    elif notification_type == "error":
        st.error(f"❌ {message}")
    elif notification_type == "warning":
        st.warning(f"⚠️ {message}")
    else:
        st.info(f"ℹ️ {message}")


def copy_to_clipboard(text: str):
    """Copy text to clipboard (Streamlit compatible)"""
    st.write(text)
    st.info("📋 Text ready to copy from console output")


def render_command_palette_hint():
    """Render hint about keyboard shortcuts"""
    st.markdown(
        '<div style="text-align: center; color: #888; font-size: 0.85rem;">'
        'Press <code>?</code> to see keyboard shortcuts'
        '</div>',
        unsafe_allow_html=True
    )
