"""
Two-Factor Authentication Setup Component
Provides UI for setting up and managing 2FA
"""

import streamlit as st
import time
from authentication_enhanced import EnhancedAuthenticationManager, TwoFactorAuth

def render_2fa_setup_page():
    """Render 2FA setup page for authenticated users"""
    
    if not st.session_state.get('authenticated', False):
        st.error("Please log in to access 2FA settings")
        return
    
    user = st.session_state.get('current_user', {})
    username = user.get('username', '')
    
    st.markdown("""
    <style>
    .twofa-container {
        max-width: 600px;
        margin: 20px auto;
        padding: 30px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .twofa-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .twofa-header h2 {
        color: #1e293b;
        font-size: 28px;
        margin: 0 0 10px 0;
        font-weight: 700;
    }
    
    .security-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    
    .step-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 15px;
    }
    
    .backup-codes {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    
    .backup-code {
        font-family: 'Courier New', monospace;
        background: white;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 5px;
        display: inline-block;
        font-weight: 600;
        border: 1px solid #d1d5db;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class='twofa-container'>
        <div class='twofa-header'>
            <h2>🔐 Two-Factor Authentication</h2>
            <div class='security-badge'>Enhanced Security</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check current 2FA status
    auth_manager = EnhancedAuthenticationManager()
    user_info = auth_manager.get_user_info(username)
    
    if not user_info:
        st.error("User information not found")
        return
    
    two_fa_enabled = user_info.get('two_fa_enabled', False)
    
    if two_fa_enabled:
        render_2fa_management(username, auth_manager)
    else:
        render_2fa_setup(username, auth_manager)

def render_2fa_setup(username: str, auth_manager: EnhancedAuthenticationManager):
    """Render 2FA setup process"""
    
    st.markdown("### 🚀 Enable Two-Factor Authentication")
    
    st.markdown("""
    <div class='step-card'>
        <div style='display: flex; align-items: center; margin-bottom: 15px;'>
            <div class='step-number'>1</div>
            <h4 style='margin: 0; color: #1e293b;'>Install Authenticator App</h4>
        </div>
        <p style='margin: 0; color: #64748b;'>
            Download an authenticator app like Google Authenticator, Authy, or Microsoft Authenticator on your phone.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Setup button
    if st.button("🔧 Start 2FA Setup", type="primary", use_container_width=True):
        st.session_state.setup_2fa_step = 2
    
    # Step 2: QR Code
    if st.session_state.get('setup_2fa_step', 1) >= 2:
        success, setup_data = auth_manager.setup_2fa(username)
        
        if success:
            st.markdown("""
            <div class='step-card'>
                <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                    <div class='step-number'>2</div>
                    <h4 style='margin: 0; color: #1e293b;'>Scan QR Code</h4>
                </div>
                <p style='margin: 0 0 15px 0; color: #64748b;'>
                    Scan this QR code with your authenticator app:
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display QR code
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: white; border-radius: 12px; border: 2px solid #e2e8f0;'>
                    <img src='{setup_data["qr_code"]}' style='max-width: 250px; width: 100%;'>
                </div>
                """, unsafe_allow_html=True)
            
            # Manual entry option
            with st.expander("📝 Manual Entry (if QR code doesn't work)"):
                st.code(setup_data["secret"], language="text")
                st.info("Enter this secret key manually in your authenticator app")
            
            # Step 3: Verification
            st.markdown("""
            <div class='step-card'>
                <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                    <div class='step-number'>3</div>
                    <h4 style='margin: 0; color: #1e293b;'>Verify Setup</h4>
                </div>
                <p style='margin: 0 0 15px 0; color: #64748b;'>
                    Enter the 6-digit code from your authenticator app to complete setup:
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("verify_2fa_setup"):
                verification_code = st.text_input(
                    "Verification Code",
                    placeholder="Enter 6-digit code",
                    max_chars=6,
                    key="2fa_verification_code"
                )
                
                col_verify, col_cancel = st.columns([1, 1])
                
                with col_verify:
                    verify_button = st.form_submit_button(
                        "✅ Enable 2FA",
                        type="primary",
                        use_container_width=True
                    )
                
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.setup_2fa_step = 1
                        st.rerun()
                
                if verify_button:
                    if not verification_code or len(verification_code) != 6:
                        st.error("Please enter a 6-digit verification code")
                    else:
                        success, message = auth_manager.enable_2fa(username, verification_code)
                        
                        if success:
                            st.success("🎉 Two-Factor Authentication enabled successfully!")
                            
                            # Show backup codes
                            st.markdown("""
                            <div class='backup-codes'>
                                <h4 style='margin: 0 0 10px 0; color: #92400e;'>⚠️ Important: Save Your Backup Codes</h4>
                                <p style='margin: 0 0 15px 0; color: #92400e; font-size: 14px;'>
                                    Store these backup codes in a safe place. You can use them to access your account if you lose your phone.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display backup codes
                            backup_codes = setup_data.get("backup_codes", [])
                            codes_html = ""
                            for i, code in enumerate(backup_codes):
                                codes_html += f"<span class='backup-code'>{code}</span>"
                                if (i + 1) % 2 == 0:
                                    codes_html += "<br>"
                            
                            st.markdown(f"""
                            <div style='text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 15px 0;'>
                                {codes_html}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download backup codes
                            backup_text = "\n".join([f"{i+1}. {code}" for i, code in enumerate(backup_codes)])
                            st.download_button(
                                "💾 Download Backup Codes",
                                backup_text,
                                file_name=f"iraqaf_backup_codes_{username}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                            time.sleep(2)
                            st.session_state.setup_2fa_step = 1
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

def render_2fa_management(username: str, auth_manager: EnhancedAuthenticationManager):
    """Render 2FA management for users with 2FA enabled"""
    
    st.success("✅ Two-Factor Authentication is **ENABLED**")
    
    st.markdown("""
    ### 🛡️ 2FA Management
    
    Your account is protected with two-factor authentication. You'll need to enter a code from your authenticator app each time you log in.
    """)
    
    # Security status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Security Level", "High", "🔐")
    
    with col2:
        st.metric("2FA Status", "Active", "✅")
    
    with col3:
        st.metric("Backup Codes", "Available", "💾")
    
    st.markdown("---")
    
    # Management options
    st.markdown("### ⚙️ Management Options")
    
    col_disable, col_regenerate = st.columns(2)
    
    with col_disable:
        st.markdown("#### 🔓 Disable 2FA")
        st.warning("This will reduce your account security")
        
        if st.button("Disable 2FA", type="secondary", use_container_width=True):
            st.session_state.show_disable_2fa = True
    
    with col_regenerate:
        st.markdown("#### 🔄 Regenerate Backup Codes")
        st.info("Generate new backup codes if needed")
        
        if st.button("Regenerate Codes", use_container_width=True):
            st.session_state.show_regenerate_codes = True
    
    # Disable 2FA confirmation
    if st.session_state.get('show_disable_2fa', False):
        st.markdown("---")
        st.markdown("### ⚠️ Confirm 2FA Disable")
        
        with st.form("disable_2fa_form"):
            st.warning("Enter your password to confirm disabling 2FA:")
            
            password = st.text_input(
                "Current Password",
                type="password",
                placeholder="Enter your password"
            )
            
            col_confirm, col_cancel = st.columns([1, 1])
            
            with col_confirm:
                disable_confirm = st.form_submit_button(
                    "🔓 Confirm Disable",
                    type="primary"
                )
            
            with col_cancel:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_disable_2fa = False
                    st.rerun()
            
            if disable_confirm:
                if not password:
                    st.error("Please enter your password")
                else:
                    success, message = auth_manager.disable_2fa(username, password)
                    
                    if success:
                        st.success("✅ 2FA disabled successfully")
                        st.session_state.show_disable_2fa = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

def render_2fa_login_form(username: str):
    """Render 2FA code input during login"""
    
    st.markdown("### 🔐 Two-Factor Authentication Required")
    st.info(f"Please enter the 6-digit code from your authenticator app for **{username}**")
    
    with st.form("2fa_login_form"):
        two_fa_code = st.text_input(
            "Authentication Code",
            placeholder="Enter 6-digit code",
            max_chars=6,
            key="2fa_login_code"
        )
        
        col_verify, col_backup = st.columns([2, 1])
        
        with col_verify:
            verify_2fa = st.form_submit_button(
                "🔓 Verify & Login",
                type="primary",
                use_container_width=True
            )
        
        with col_backup:
            use_backup = st.form_submit_button(
                "🔑 Use Backup Code",
                use_container_width=True
            )
        
        if verify_2fa:
            if not two_fa_code or len(two_fa_code) != 6:
                st.error("Please enter a 6-digit code")
                return None
            
            return {"type": "totp", "code": two_fa_code}
        
        if use_backup:
            st.session_state.show_backup_login = True
            st.rerun()
    
    # Backup code login
    if st.session_state.get('show_backup_login', False):
        st.markdown("---")
        st.markdown("### 🔑 Backup Code Login")
        
        with st.form("backup_code_form"):
            backup_code = st.text_input(
                "Backup Code",
                placeholder="Enter backup code",
                key="backup_login_code"
            )
            
            col_verify_backup, col_back = st.columns([1, 1])
            
            with col_verify_backup:
                verify_backup = st.form_submit_button(
                    "✅ Verify Backup Code",
                    type="primary"
                )
            
            with col_back:
                if st.form_submit_button("← Back to 2FA"):
                    st.session_state.show_backup_login = False
                    st.rerun()
            
            if verify_backup:
                if not backup_code:
                    st.error("Please enter a backup code")
                    return None
                
                return {"type": "backup", "code": backup_code}
    
    return None
