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

        # Features Section Header
        st.markdown("<div style='text-align: center; margin: 20px 0 15px 0; padding-top: 15px; border-top: 1px solid #eee;'><h3 style='color: #333;'>✨ Key Features</h3></div>", unsafe_allow_html=True)

        # Feature cards using Streamlit columns
        feat_col1, feat_col2 = st.columns(2)
        with feat_col1:
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>📊</div>
                <strong style='font-size: 13px; color: #333;'>11-Category Assessment</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px; color: #666;'>Comprehensive security scoring</p>
            </div>
            """, unsafe_allow_html=True)
        with feat_col2:
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>🔒</div>
                <strong style='font-size: 13px; color: #333;'>Role-Based Access</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px; color: #666;'>Admin, Analyst, Viewer roles</p>
            </div>
            """, unsafe_allow_html=True)

        feat_col3, feat_col4 = st.columns(2)
        with feat_col3:
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>📈</div>
                <strong style='font-size: 13px; color: #333;'>Real-Time Monitoring</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px; color: #666;'>Live security metrics</p>
            </div>
            """, unsafe_allow_html=True)
        with feat_col4:
            st.markdown("""
            <div style='background: #f8f9ff; border: 1px solid #e5e7ff; border-radius: 8px; padding: 12px; text-align: center;'>
                <div style='font-size: 24px; margin-bottom: 5px;'>🛡️</div>
                <strong style='font-size: 13px; color: #333;'>L2 Privacy Monitor</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px; color: #666;'>Advanced threat detection</p>
            </div>
            """, unsafe_allow_html=True)

        # Login Form Container
        st.markdown("<div style='margin-top: 25px;'>", unsafe_allow_html=True)

        # Login / Sign Up Tabs
        tab_login, tab_signup = st.tabs(["🔓 Login", "📝 Sign Up"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### Login to Dashboard")

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

        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("### Create New Account")

                new_username = st.text_input(
                    "Choose Username",
                    placeholder="Enter desired username",
                    key="signup_username"
                )

                new_email = st.text_input(
                    "Email Address",
                    placeholder="Enter your email",
                    key="signup_email"
                )

                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter a strong password",
                    key="signup_password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="signup_confirm_password"
                )

                col_signup, col_space = st.columns([1, 1])

                with col_signup:
                    signup_button = st.form_submit_button(
                        "📝 Create Account",
                        use_container_width=True,
                        type="primary"
                    )

                if signup_button:
                    if not new_username or not new_password or not new_email:
                        st.error("❌ Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        # Create new user
                        auth_manager = AuthenticationManager()
                        success, message = auth_manager.create_user(
                            new_username, new_password, new_email, role="Viewer")

                        if success:
                            st.success(f"✅ {message} You can now login!")
                            st.info(
                                "Account created successfully. Please login with your credentials.")
                        else:
                            st.error(f"❌ {message}")

            # Demo Credentials
            st.markdown(
                "<div class='divider' style='margin-top: 20px;'></div>", unsafe_allow_html=True)

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
            
            **💡 Tip:** After signing up with Viewer role, an Admin can upgrade your role to Analyst or Admin.
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
    """Display user information in sidebar with modern styling"""
    if st.session_state.get('authenticated', False):
        user = st.session_state.get('current_user', {})
        permissions = user.get('permissions', [])
        role = user.get('role', 'N/A').title()
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        
        # Role badge colors
        role_colors = {
            'Admin': {'bg': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'text': 'white'},
            'Analyst': {'bg': 'linear-gradient(135deg, #00d4ff 0%, #0099ff 100%)', 'text': 'white'},
            'Viewer': {'bg': 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)', 'text': 'white'}
        }
        role_style = role_colors.get(role, {'bg': '#e2e8f0', 'text': '#475569'})
        
        # CSS Styles
        st.markdown("""
        <style>
            .user-info-card {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 18px;
                margin: 16px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }
            
            .user-info-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 2px solid #e2e8f0;
            }
            
            .user-info-header h4 {
                margin: 0;
                font-size: 14px;
                font-weight: 700;
                color: #1e293b;
                letter-spacing: 0.5px;
            }
            
            .user-info-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #f1f5f9;
            }
            
            .user-info-row:last-child {
                border-bottom: none;
            }
            
            .user-info-label {
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .role-badge {
                display: inline-block;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .permissions-badge {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 32px;
                height: 24px;
                padding: 0 10px;
                border-radius: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 12px;
                font-weight: 700;
                box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # HTML Content
        html_content = f"""
        <div class="user-info-card">
            <div class="user-info-header">
                <span style="font-size: 18px;">👤</span>
                <h4>User Information</h4>
            </div>
            <div class="user-info-row">
                <span class="user-info-label">Role</span>
                <span class="role-badge" style="background: {role_style['bg']}; color: {role_style['text']};">
                    {role}
                </span>
            </div>
            <div class="user-info-row">
                <span class="user-info-label">Permissions</span>
                <span class="permissions-badge">{len(permissions)}</span>
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Optional expandable details
        with st.sidebar.expander("📋 View Full Details", expanded=False):
            st.markdown(f"""
                <div style="padding: 8px 0;">
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase;">Username:</span><br>
                        <span style="font-size: 13px; color: #1e293b; font-weight: 600;">{username}</span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase;">Email:</span><br>
                        <span style="font-size: 13px; color: #1e293b; font-weight: 600;">{email if email != 'N/A' else 'Not provided'}</span>
                    </div>
                    <div>
                        <span style="font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase;">Permission List:</span><br>
                        <span style="font-size: 12px; color: #475569;">{', '.join(permissions) if permissions else 'None assigned'}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def check_authentication():
    """Check if user is authenticated, show login if not"""
    if not st.session_state.get('authenticated', False):
        render_login_page()
        return False
    return True
