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
    .features-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 20px;
    }
    .feature-card {
        background: #f8f9ff;
        border: 1px solid #e5e7ff;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-size: 13px;
    }
    .feature-icon {
        font-size: 24px;
        margin-bottom: 5px;
    }
    .security-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        margin-top: 15px;
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

        # Key Features Section
        st.markdown("""
        <div class='login-container' style='margin-top: 15px; padding: 20px; background: #f8f9ff; border: 1px solid #e5e7ff;'>
            <h3 style='text-align: center; color: #333; margin-top: 0; margin-bottom: 15px;'>✨ Key Features</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards using Streamlit columns
        feat_col1, feat_col2 = st.columns(2)
        with feat_col1:
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 10px;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>📊</div>
                <strong style='font-size: 14px;'>11-Category Assessment</strong>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #666;'>Comprehensive security scoring</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>📈</div>
                <strong style='font-size: 14px;'>Real-Time Monitoring</strong>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #666;'>Live security metrics</p>
            </div>
            """, unsafe_allow_html=True)
        
        with feat_col2:
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 10px;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>🔒</div>
                <strong style='font-size: 14px;'>Role-Based Access</strong>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #666;'>Admin, Analyst, Viewer roles</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>🛡️</div>
                <strong style='font-size: 14px;'>L2 Privacy Monitor</strong>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #666;'>Advanced threat detection</p>
            </div>
            """, unsafe_allow_html=True)

        # Login Form
        st.markdown("<div class='login-container' style='margin-top: 20px; padding-top: 20px;'>",
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
                    success, user = auth_manager.authenticate(
                        username, password)

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
                        st.error(
                            "❌ Invalid username or password. Please try again.")

            # Demo Credentials
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            with st.expander("📋 Demo Credentials & Info"):
                st.markdown("""
                ### 🎯 Quick Start
                
                **Admin Account (Full Access):**
                ```
                Username: admin
                Password: admin_default_123
                ```
                
                **Features Available:**
                - 📊 View 11-category security assessment
                - 📈 Analyze 30-day trends & metrics
                - 🛡️ Monitor real-time alerts
                - 📋 Compliance framework tracking (GDPR, HIPAA, PCI-DSS, ISO 27001, NIST CSF)
                - 🔐 L2 Privacy/Security Monitor
                - 👥 Role-based access control
                
                **Role Permissions:**
                - **Admin:** Full access to all features and settings
                - **Analyst:** Full access to monitoring and reporting
                - **Viewer:** Read-only access to reports and metrics
                
                **💡 Tip:** Create additional user accounts from the Settings page after logging in.
                """)

            # Security Badge
            st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <div class='security-badge'>🔐 Enterprise-Grade Security</div>
            </div>
            """, unsafe_allow_html=True)

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
            st.sidebar.markdown(
                f"**Permissions:** {', '.join(permissions) if permissions else 'None'}")


def check_authentication():
    """Check if user is authenticated, show login if not"""
    if not st.session_state.get('authenticated', False):
        render_login_page()
        return False
    return True
