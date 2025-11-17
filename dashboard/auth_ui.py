"""
Beautiful Authentication UI Module
Provides a pretty login page and authentication interface
"""

import streamlit as st
import time
from authentication import AuthenticationManager


def render_login_page():
    """Render a beautiful login page"""
    # Custom CSS for better styling
    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .login-container {
        max-width: 450px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .login-header h1 {
        color: #333;
        font-size: 28px;
        margin: 0;
        margin-bottom: 10px;
    }
    .login-header p {
        color: #666;
        font-size: 14px;
        margin: 0;
    }
    .divider {
        height: 1px;
        background: #eee;
        margin: 20px 0;
    }
    .demo-creds {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 12px;
        border-radius: 4px;
        font-size: 13px;
        margin-top: 20px;
    }
    .demo-creds code {
        background: #e0e5ff;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create centered layout
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        # Header
        st.markdown("""
        <div class='login-container'>
            <div class='login-header'>
                <h1>🔐 IRAQAF Dashboard</h1>
                <p>Integrated Regulatory & Compliance Quality Assurance Framework</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Login Form
        st.markdown("<div class='login-container' style='margin-top: -20px; padding-top: 20px;'>", 
                    unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 👤 Login")

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            col_login, col_space = st.columns([1, 1])

            with col_login:
                submit_button = st.form_submit_button(
                    "🔓 Login",
                    use_container_width=True,
                    type="primary"
                )

            if submit_button:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    # Authenticate
                    auth_manager = AuthenticationManager()
                    success, user = auth_manager.authenticate(username, password)

                    if success:
                        # Store user in session
                        st.session_state['authenticated'] = True
                        st.session_state['current_user'] = user
                        st.session_state['username'] = username

                        # Show success and reload
                        st.success(f"✅ Welcome, {user['username']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")

            # Demo Credentials
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            with st.expander("📋 Demo Credentials"):
                st.markdown("""
                **Admin Account:**
                - Username: `admin`
                - Password: `admin_default_123`

                **Create new accounts:**
                You can create new user accounts from the Settings page after logging in.
                """)

            st.markdown("</div>", unsafe_allow_html=True)


def render_logout_button():
    """Render logout button in sidebar"""
    if st.session_state.get('authenticated', False):
        user = st.session_state.get('current_user', {})
        username = user.get('username', 'User')

        st.sidebar.markdown(f"👤 **Logged in as:** {username}")

        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state['current_user'] = None
            st.session_state['username'] = None
            st.success("✅ Logged out successfully!")
            time.sleep(1)
            st.rerun()


def render_user_info():
    """Display user information in sidebar"""
    if st.session_state.get('authenticated', False):
        user = st.session_state.get('current_user', {})

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Information")

        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            st.metric("Role", user.get('role', 'N/A').title())
        with col2:
            permissions = user.get('permissions', [])
            st.metric("Permissions", len(permissions))

        if st.sidebar.checkbox("👥 View Details"):
            st.sidebar.markdown(f"**Username:** {user.get('username', 'N/A')}")
            st.sidebar.markdown(f"**Email:** {user.get('email', 'N/A')}")
            st.sidebar.markdown(f"**Role:** {user.get('role', 'N/A')}")
            st.sidebar.markdown(f"**Permissions:** {', '.join(permissions) if permissions else 'None'}")


def check_authentication():
    """Check if user is authenticated, show login if not"""
    if not st.session_state.get('authenticated', False):
        render_login_page()
        return False
    return True
