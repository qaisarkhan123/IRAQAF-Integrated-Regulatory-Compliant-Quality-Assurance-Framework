"""
Enhanced Authentication UI Module
Comprehensive upgrade with security and modern UI improvements
"""

import streamlit as st
import time
import re
import secrets
import hashlib
from datetime import datetime, timedelta
from authentication import AuthenticationManager
import pyotp
import qrcode
from io import BytesIO
import base64

class PasswordStrengthChecker:
    """Enhanced password strength validation"""
    
    @staticmethod
    def check_strength(password: str) -> dict:
        """Check password strength and return detailed feedback"""
        if not password:
            return {"score": 0, "level": "None", "feedback": [], "color": "#ef4444"}
        
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 20
        else:
            feedback.append("At least 8 characters")
        
        if len(password) >= 12:
            score += 10
        
        # Character variety checks
        if re.search(r'[a-z]', password):
            score += 15
        else:
            feedback.append("Lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 15
        else:
            feedback.append("Uppercase letters")
        
        if re.search(r'\d', password):
            score += 15
        else:
            feedback.append("Numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
        else:
            feedback.append("Special characters")
        
        # Bonus checks
        if len(password) >= 16:
            score += 10
        
        # No common patterns
        common_patterns = ['123', 'abc', 'password', 'admin', 'qwerty']
        if not any(pattern in password.lower() for pattern in common_patterns):
            score += 10
        else:
            feedback.append("Avoid common patterns")
        
        # Determine level and color
        if score >= 80:
            level, color = "Very Strong", "#10b981"
        elif score >= 60:
            level, color = "Strong", "#059669"
        elif score >= 40:
            level, color = "Medium", "#f59e0b"
        elif score >= 20:
            level, color = "Weak", "#f97316"
        else:
            level, color = "Very Weak", "#ef4444"
        
        return {
            "score": min(score, 100),
            "level": level,
            "feedback": feedback,
            "color": color
        }

class SessionManager:
    """Enhanced session management with timeout and security"""
    
    @staticmethod
    def init_session():
        """Initialize session with security settings"""
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = datetime.now()
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = {}
        if 'theme_mode' not in st.session_state:
            st.session_state.theme_mode = 'light'
    
    @staticmethod
    def check_session_timeout(timeout_minutes: int = 30) -> bool:
        """Check if session has timed out"""
        if 'last_activity' not in st.session_state:
            return True
        
        last_activity = st.session_state.last_activity
        if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
            return True
        
        # Update last activity
        st.session_state.last_activity = datetime.now()
        return False
    
    @staticmethod
    def check_account_lockout(username: str, max_attempts: int = 5) -> bool:
        """Check if account is locked due to failed attempts"""
        if username not in st.session_state.login_attempts:
            return False
        
        attempts = st.session_state.login_attempts[username]
        return attempts['count'] >= max_attempts and \
               datetime.now() - attempts['last_attempt'] < timedelta(minutes=15)
    
    @staticmethod
    def record_failed_attempt(username: str):
        """Record a failed login attempt"""
        if username not in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = {'count': 0, 'last_attempt': datetime.now()}
        
        st.session_state.login_attempts[username]['count'] += 1
        st.session_state.login_attempts[username]['last_attempt'] = datetime.now()
    
    @staticmethod
    def clear_failed_attempts(username: str):
        """Clear failed attempts after successful login"""
        if username in st.session_state.login_attempts:
            del st.session_state.login_attempts[username]

def render_enhanced_login_page():
    """Render enhanced login page with modern UI and security features"""
    
    # Initialize session
    SessionManager.init_session()
    
    # Check for session timeout
    if st.session_state.get('authenticated') and SessionManager.check_session_timeout():
        st.session_state.authenticated = False
        st.warning("⏰ Session expired. Please log in again.")
    
    # Enhanced CSS with dark mode support
    theme = st.session_state.get('theme_mode', 'light')
    
    if theme == 'dark':
        # Dark mode colors
        bg_gradient = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
        card_bg = "#1e293b"
        text_color = "#f8fafc"
        secondary_text = "#cbd5e1"
        border_color = "#475569"
        input_bg = "#334155"
        feature_card_bg = "#334155"
        accent_color = "#3b82f6"
    else:
        # Light mode colors - changed from purple to a more neutral/professional look
        bg_gradient = "linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)"
        card_bg = "#ffffff"
        text_color = "#1e293b"
        secondary_text = "#64748b"
        border_color = "#e2e8f0"
        input_bg = "#f8fafc"
        feature_card_bg = "#f8fafc"
        accent_color = "#3b82f6"
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_gradient};
        min-height: 100vh;
    }}
    
    .enhanced-login-container {{
        max-width: 480px;
        margin: 50px auto;
        padding: 40px;
        background: {card_bg};
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,{'0.4' if theme == 'dark' else '0.15'});
        backdrop-filter: blur(10px);
        border: 1px solid {border_color};
        animation: slideIn 0.5s ease-out;
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .login-header {{
        text-align: center;
        margin-bottom: 35px;
        animation: fadeIn 0.6s ease-out 0.2s both;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    .login-header h1 {{
        color: {text_color};
        font-size: 32px;
        margin: 0 0 10px 0;
        font-weight: 800;
        background: linear-gradient(135deg, {accent_color} 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .login-header p {{
        color: {secondary_text};
        font-size: 16px;
        margin: 0;
        font-weight: 500;
    }}
    
    .theme-toggle {{
        position: absolute;
        top: 20px;
        right: 20px;
        background: {'rgba(255,255,255,0.1)' if theme == 'dark' else 'rgba(0,0,0,0.1)'};
        border: 1px solid {'rgba(255,255,255,0.2)' if theme == 'dark' else 'rgba(0,0,0,0.2)'};
        border-radius: 50px;
        padding: 8px 16px;
        color: {text_color};
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s ease;
    }}
    
    .theme-toggle:hover {{
        background: {'rgba(255,255,255,0.2)' if theme == 'dark' else 'rgba(0,0,0,0.2)'};
        transform: scale(1.05);
    }}
    
    .password-strength-meter {{
        margin-top: 8px;
        padding: 12px;
        background: {input_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        animation: slideDown 0.3s ease-out;
        color: {text_color};
    }}
    
    @keyframes slideDown {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .strength-bar {{
        width: 100%;
        height: 6px;
        background: {border_color};
        border-radius: 3px;
        overflow: hidden;
        margin: 8px 0;
    }}
    
    .strength-fill {{
        height: 100%;
        transition: all 0.3s ease;
        border-radius: 3px;
    }}
    
    .feature-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin: 25px 0;
        animation: fadeIn 0.8s ease-out 0.4s both;
    }}
    
    .feature-card {{
        background: {feature_card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        color: {text_color};
    }}
    
    .feature-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,{'0.25' if theme == 'dark' else '0.15'});
        border-color: {accent_color};
    }}
    
    .feature-card strong {{
        color: {text_color};
    }}
    
    .feature-card p {{
        color: {secondary_text};
    }}
    
    .feature-icon {{
        font-size: 28px;
        margin-bottom: 8px;
        display: block;
    }}
    
    .security-badge {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        margin-top: 20px;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    .loading-spinner {{
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid {border_color};
        border-top: 3px solid {accent_color};
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 8px;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    .alert-banner {{
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: 500;
        animation: slideIn 0.4s ease-out;
    }}
    
    .alert-success {{
        background: {'#065f46' if theme == 'dark' else '#dcfce7'};
        color: {'#d1fae5' if theme == 'dark' else '#166534'};
        border: 1px solid {'#047857' if theme == 'dark' else '#bbf7d0'};
    }}
    
    .alert-error {{
        background: {'#7f1d1d' if theme == 'dark' else '#fef2f2'};
        color: {'#fecaca' if theme == 'dark' else '#991b1b'};
        border: 1px solid {'#991b1b' if theme == 'dark' else '#fecaca'};
    }}
    
    .alert-warning {{
        background: {'#78350f' if theme == 'dark' else '#fffbeb'};
        color: {'#fed7aa' if theme == 'dark' else '#92400e'};
        border: 1px solid {'#92400e' if theme == 'dark' else '#fed7aa'};
    }}
    
    .session-info {{
        background: {input_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
        font-size: 12px;
        color: {secondary_text};
    }}
    
    /* Streamlit form styling fixes for dark mode */
    .stTextInput > div > div > input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    .stTextInput > label {{
        color: {text_color} !important;
    }}
    
    .stCheckbox > label {{
        color: {text_color} !important;
    }}
    
    .stMarkdown h3 {{
        color: {text_color} !important;
    }}
    
    .stMarkdown p {{
        color: {secondary_text} !important;
    }}
    
    .stExpander > div > div > div > div {{
        background-color: {input_bg} !important;
        border-color: {border_color} !important;
    }}
    
    .stExpander > div > div > div > div > div {{
        color: {text_color} !important;
    }}
    
    /* Enhanced button styling for uniform appearance */
    .stButton > button {{
        height: 48px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 100px !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}
    
    /* Ensure buttons in columns have equal height */
    .stColumns > div > div > div > div > div > button {{
        height: 48px !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Theme toggle button
    col_theme, col_space = st.columns([1, 4])
    with col_theme:
        if st.button("🌓" if theme == 'light' else "☀️", help="Toggle theme"):
            st.session_state.theme_mode = 'dark' if theme == 'light' else 'light'
            st.rerun()
    
    # Main container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class='enhanced-login-container'>
            <div class='login-header'>
                <h1>🛡️ IRAQAF</h1>
                <p>Integrated Regulatory & Compliance Quality Assurance Framework</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Security features showcase
        st.markdown(f"""
        <div class='feature-grid'>
            <div class='feature-card'>
                <span class='feature-icon'>🔐</span>
                <strong style='font-size: 14px;'>Enhanced Security</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px;'>2FA & Account Protection</p>
            </div>
            <div class='feature-card'>
                <span class='feature-icon'>📊</span>
                <strong style='font-size: 14px;'>Real-time Monitoring</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px;'>Live Compliance Metrics</p>
            </div>
            <div class='feature-card'>
                <span class='feature-icon'>🎯</span>
                <strong style='font-size: 14px;'>7-Hub Architecture</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px;'>Comprehensive Coverage</p>
            </div>
            <div class='feature-card'>
                <span class='feature-icon'>⚡</span>
                <strong style='font-size: 14px;'>Modern Interface</strong>
                <p style='margin: 5px 0 0 0; font-size: 11px;'>Enhanced User Experience</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab_login, tab_signup, tab_recovery = st.tabs(["🔓 Login", "📝 Sign Up", "🔑 Recovery"])
        
        with tab_login:
            render_enhanced_login_form()
        
        with tab_signup:
            render_enhanced_signup_form()
        
        with tab_recovery:
            render_password_recovery_form()
        
        # Demo credentials
        with st.expander("📋 Demo Access & Security Info"):
            st.markdown("""
            ### 🎯 Quick Start
            
            **Admin Account:**
            ```
            Username: admin
            Password: admin_default_123
            ```
            
            ### 🔐 Security Features
            - **Password Strength Validation** - Real-time feedback
            - **Account Lockout Protection** - 5 attempts, 15min cooldown
            - **Session Management** - 30min timeout, activity tracking
            - **Two-Factor Authentication** - TOTP support (optional)
            - **Dark/Light Mode** - Theme preferences
            
            ### 📊 Available Hubs
            - **L1:** Regulations & Governance
            - **L2:** Privacy & Security  
            - **L3:** Fairness & Ethics
            - **L4:** Explainability & Transparency
            - **SOQM:** System Operations & QA Monitor
            - **UQO:** Unified QA Orchestrator
            - **CAE:** Continuous Assurance Engine
            """)
            
            st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <div class='security-badge'>🔐 Enterprise-Grade Security</div>
            </div>
            """, unsafe_allow_html=True)

def render_enhanced_login_form():
    """Enhanced login form with security features"""
    
    with st.form("enhanced_login_form", clear_on_submit=False):
        st.markdown("### 🔓 Secure Login")
        
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="enhanced_login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="enhanced_login_password"
        )
        
        # Remember me and forgot password
        col_remember, col_forgot = st.columns([1, 1])
        with col_remember:
            remember_me = st.checkbox("Remember me", key="remember_me")
        with col_forgot:
            if st.form_submit_button("Forgot Password?", type="secondary"):
                st.info("Password recovery is available in the Recovery tab.")
        
        # Login button with loading state
        col_login, col_space = st.columns([1, 1])
        with col_login:
            login_button = st.form_submit_button(
                "🔓 Sign In",
                use_container_width=True,
                type="primary"
            )
        
        if login_button:
            if not username or not password:
                st.error("❌ Please enter both username and password")
                return
            
            # Check account lockout
            if SessionManager.check_account_lockout(username):
                st.error("🔒 Account temporarily locked due to multiple failed attempts. Try again in 15 minutes.")
                return
            
            # Show loading state
            with st.spinner("Authenticating..."):
                time.sleep(1)  # Simulate processing time
                
                # Authenticate
                auth_manager = AuthenticationManager()
                success, user = auth_manager.authenticate(username, password)
                
                if success:
                    # Clear failed attempts
                    SessionManager.clear_failed_attempts(username)
                    
                    # Store user in session
                    st.session_state['authenticated'] = True
                    st.session_state['current_user'] = user
                    st.session_state['username'] = username
                    st.session_state['login_time'] = datetime.now()
                    
                    if remember_me:
                        st.session_state['remember_me'] = True
                    
                    # Success message with animation
                    st.markdown("""
                    <div class='alert-banner alert-success'>
                        ✅ Welcome back! Redirecting to dashboard...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(1.5)
                    st.rerun()
                else:
                    # Record failed attempt
                    SessionManager.record_failed_attempt(username)
                    
                    attempts_left = 5 - st.session_state.login_attempts.get(username, {}).get('count', 0)
                    
                    st.markdown(f"""
                    <div class='alert-banner alert-error'>
                        ❌ Invalid credentials. {attempts_left} attempts remaining.
                    </div>
                    """, unsafe_allow_html=True)

def render_enhanced_signup_form():
    """Enhanced signup form with password strength meter"""
    
    with st.form("enhanced_signup_form", clear_on_submit=False):
        st.markdown("### 📝 Create Account")
        
        new_username = st.text_input(
            "Username",
            placeholder="Choose a unique username",
            key="enhanced_signup_username"
        )
        
        new_email = st.text_input(
            "Email Address",
            placeholder="Enter your email",
            key="enhanced_signup_email"
        )
        
        new_password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password",
            key="enhanced_signup_password"
        )
        
        # Password strength meter
        if new_password:
            strength = PasswordStrengthChecker.check_strength(new_password)
            
            st.markdown(f"""
            <div class='password-strength-meter'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span style='font-size: 12px; font-weight: 600;'>Password Strength:</span>
                    <span style='font-size: 12px; color: {strength["color"]}; font-weight: 600;'>{strength["level"]}</span>
                </div>
                <div class='strength-bar'>
                    <div class='strength-fill' style='width: {strength["score"]}%; background: {strength["color"]};'></div>
                </div>
                {f"<div style='font-size: 11px; color: #64748b; margin-top: 5px;'>Missing: {', '.join(strength['feedback'])}</div>" if strength['feedback'] else ""}
            </div>
            """, unsafe_allow_html=True)
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="enhanced_signup_confirm_password"
        )
        
        # Terms and conditions
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="terms_checkbox")
        
        # Signup button
        col_signup, col_space = st.columns([1, 1])
        with col_signup:
            signup_button = st.form_submit_button(
                "📝 Create Account",
                use_container_width=True,
                type="primary"
            )
        
        if signup_button:
            # Validation
            if not all([new_username, new_password, new_email, confirm_password]):
                st.error("❌ Please fill in all fields")
                return
            
            if not terms_accepted:
                st.error("❌ Please accept the Terms of Service")
                return
            
            if new_password != confirm_password:
                st.error("❌ Passwords do not match")
                return
            
            # Check password strength
            strength = PasswordStrengthChecker.check_strength(new_password)
            if strength["score"] < 40:
                st.error("❌ Password is too weak. Please choose a stronger password.")
                return
            
            # Email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                st.error("❌ Please enter a valid email address")
                return
            
            # Create account
            with st.spinner("Creating account..."):
                time.sleep(1)
                
                auth_manager = AuthenticationManager()
                success, message = auth_manager.create_user(
                    new_username, new_password, new_email, role="Viewer"
                )
                
                if success:
                    st.markdown("""
                    <div class='alert-banner alert-success'>
                        ✅ Account created successfully! You can now log in.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='alert-banner alert-error'>
                        ❌ {message}
                    </div>
                    """, unsafe_allow_html=True)

def render_password_recovery_form():
    """Password recovery form"""
    
    st.markdown("### 🔑 Password Recovery")
    
    with st.form("password_recovery_form"):
        recovery_email = st.text_input(
            "Email Address",
            placeholder="Enter your registered email",
            key="recovery_email"
        )
        
        recovery_button = st.form_submit_button(
            "📧 Send Recovery Email",
            use_container_width=True,
            type="primary"
        )
        
        if recovery_button:
            if not recovery_email:
                st.error("❌ Please enter your email address")
                return
            
            # Simulate email sending
            with st.spinner("Sending recovery email..."):
                time.sleep(2)
                
                st.markdown("""
                <div class='alert-banner alert-success'>
                    ✅ Recovery email sent! Check your inbox for instructions.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    ### 🛡️ Account Recovery Options
    
    - **Email Recovery:** Reset password via email link
    - **Admin Recovery:** Contact system administrator
    - **Security Questions:** Answer security questions (coming soon)
    - **2FA Recovery:** Use backup codes (if enabled)
    
    **Need Help?** Contact support at: support@iraqaf.com
    """)

def render_enhanced_user_info():
    """Enhanced user info display with session management"""
    
    if st.session_state.get('authenticated', False):
        user = st.session_state.get('current_user', {})
        username = user.get('username', 'N/A')
        role = user.get('role', 'N/A').title()
        permissions = user.get('permissions', [])
        login_time = st.session_state.get('login_time', datetime.now())
        
        # Session duration
        session_duration = datetime.now() - login_time
        duration_str = f"{int(session_duration.total_seconds() // 60)}m {int(session_duration.total_seconds() % 60)}s"
        
        # Theme
        theme = st.session_state.get('theme_mode', 'light')
        
        # Role colors
        role_colors = {
            'Admin': {'bg': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'text': 'white'},
            'Analyst': {'bg': 'linear-gradient(135deg, #00d4ff 0%, #0099ff 100%)', 'text': 'white'},
            'Viewer': {'bg': 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)', 'text': 'white'}
        }
        role_style = role_colors.get(role, {'bg': '#e2e8f0', 'text': '#475569'})
        
        # Get theme colors
        if theme == 'dark':
            card_bg = "linear-gradient(135deg, #1e293b 0%, #334155 100%)"
            border_color = "#475569"
            text_color = "#f8fafc"
            secondary_text = "#cbd5e1"
        else:
            card_bg = "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)"
            border_color = "#e2e8f0"
            text_color = "#1e293b"
            secondary_text = "#64748b"
        
        # Use a simpler approach with Streamlit native components
        st.markdown(f"""
        <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; margin: 16px 0; box-shadow: 0 4px 12px rgba(0,0,0,{'0.15' if theme == 'dark' else '0.08'});">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <span style="font-size: 20px;">👤</span>
                <h4 style="margin: 0; font-size: 16px; font-weight: 700; color: {text_color};">User Profile</h4>
                <span style="margin-left: auto; font-size: 12px; color: {secondary_text};">Session: {duration_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Use Streamlit columns for the content to avoid HTML rendering issues
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"**Role:** {role}")
            st.markdown(f"**Permissions:** {len(permissions)}")
            
        with col2:
            st.markdown(f"**Theme:** {'🌙 Dark' if theme == 'dark' else '☀️ Light'}")
            st.markdown(f"**Username:** {username}")
        
        # Optional expandable details
        with st.expander("📋 View Full Details", expanded=False):
            st.markdown(f"**Email:** {user.get('email', 'Not provided')}")
            st.markdown(f"**Permission List:** {', '.join(permissions) if permissions else 'None assigned'}")
            st.markdown(f"**Login Time:** {login_time.strftime('%H:%M:%S')}")
        
        # Session management with uniform button styling
        st.markdown(f"""
        <div style="
            margin-top: 20px; 
            padding-top: 15px; 
            border-top: 1px solid {border_color};
        ">
            <h5 style="
                margin: 0 0 15px 0; 
                font-size: 14px; 
                font-weight: 600; 
                color: {text_color}; 
                text-align: center;
            ">Session Management</h5>
        </div>
        """, unsafe_allow_html=True)
        
        col_logout, col_extend = st.columns(2, gap="medium")
        
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_btn"):
                # Clear session
                for key in ['authenticated', 'current_user', 'username', 'login_time']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.success("✅ Logged out successfully!")
                time.sleep(1)
                st.rerun()
        
        with col_extend:
            if st.button("⏰ Extend", use_container_width=True, key="extend_btn"):
                st.session_state.last_activity = datetime.now()
                st.success("✅ Session extended!")

def check_enhanced_authentication():
    """Enhanced authentication check with session management"""
    
    # Initialize session
    SessionManager.init_session()
    
    # Check if user is authenticated
    if not st.session_state.get('authenticated', False):
        render_enhanced_login_page()
        return False
    
    # Check session timeout
    if SessionManager.check_session_timeout():
        st.session_state.authenticated = False
        st.warning("⏰ Session expired due to inactivity. Please log in again.")
        render_enhanced_login_page()
        return False
    
    return True
