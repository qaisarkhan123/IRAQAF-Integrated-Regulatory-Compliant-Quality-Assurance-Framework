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
    """Render theme toggle button with improved styling"""
    # Create compact horizontal layout
    col1, col2, col3 = st.columns([0.8, 1.2, 1])
    
    with col1:
        theme_icon = "🌙" if st.session_state.dark_mode else "☀️"
        if st.button(f"{theme_icon}", help="Toggle dark mode", use_container_width=True, key="theme_toggle_btn"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    with col2:
        theme_text = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
        st.markdown(f"<div style='padding: 0.5rem; text-align: center;'><small><b>{theme_text}</b></small></div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("")  # Spacer


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
        st.metric(
            "% Change", f"{(delta/old_value)*100:+.1f}%" if old_value != 0 else "N/A")


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
    """Render compact session information widget with modern styling"""
    duration = get_session_duration()
    actions = st.session_state.get("actions_count", 0)
    last_activity = st.session_state.get("last_activity", datetime.now())
    time_since_activity = datetime.now() - last_activity
    time_str = f"{int(time_since_activity.total_seconds())}s" if time_since_activity.total_seconds() < 60 else "Active"
    
    # CSS Styles
    st.markdown("""
    <style>
        .session-info-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 18px;
            margin: 16px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        
        .session-info-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .session-info-header h5 {
            margin: 0;
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: 0.5px;
        }
        
        .session-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
        }
        
        .session-info-item {
            text-align: center;
            padding: 12px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease;
        }
        
        .session-info-item:hover {
            border-color: #667eea;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }
        
        .session-info-label {
            font-size: 10px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        
        .session-info-value {
            font-size: 18px;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.2;
        }
        
        .session-info-duration {
            color: #667eea;
        }
        
        .session-info-actions {
            color: #10b981;
        }
        
        .session-info-activity {
            color: #f59e0b;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML Content
    html_content = f"""
    <div class="session-info-card">
        <div class="session-info-header">
            <span style="font-size: 18px;">📊</span>
            <h5>Session Info</h5>
        </div>
        <div class="session-info-grid">
            <div class="session-info-item">
                <div class="session-info-label">Duration</div>
                <div class="session-info-value session-info-duration">{duration}</div>
            </div>
            <div class="session-info-item">
                <div class="session-info-label">Actions</div>
                <div class="session-info-value session-info-actions">{actions}</div>
            </div>
            <div class="session-info-item">
                <div class="session-info-label">Last Activity</div>
                <div class="session-info-value session-info-activity">{time_str}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
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
    
    /* Enhanced buttons - compact and pretty */
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 0.5rem 1rem;
        font-size: 0.95rem;
        height: auto;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Compact button for theme toggle */
    [key="theme_toggle_btn"] {
        font-size: 1.2rem !important;
        padding: 0.4rem !important;
        height: 2.5rem !important;
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
        padding: 0.75rem 1.5rem;
    }
    
    /* Enhanced metrics - compact version */
    [data-testid="stMetric"] {
        padding: 0.75rem 0.5rem;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Smooth expandable sections */
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-weight: 500;
        padding: 1rem;
    }
    
    /* Divider styling */
    hr {
        margin: 0.5rem 0;
        border: none;
        border-top: 1px solid #e5e5e5;
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
