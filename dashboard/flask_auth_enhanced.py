"""
Flask Enhanced Authentication Manager
Advanced security features including 2FA, session management, and audit logging
Adapted for Flask from the Streamlit version
"""

import json
import logging
import hashlib
import hmac
import secrets
import pyotp
import qrcode
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from flask import session, request, redirect, url_for, render_template
from io import BytesIO
import base64
from functools import wraps

logger = logging.getLogger(__name__)

class EnhancedUser:
    """Enhanced user class with additional security features"""
    
    ROLE_DEFINITIONS = {
        "admin": {
            "display_name": "Administrator",
            "permissions": [
                "view_all_reports", "export_data", "create_alerts",
                "manage_users", "manage_settings", "manage_compliance_rules",
                "access_audit_logs", "manage_2fa", "view_security_logs"
            ]
        },
        "analyst": {
            "display_name": "Compliance Analyst", 
            "permissions": [
                "view_all_reports", "export_data", "create_alerts",
                "view_audit_logs", "access_regulatory_data", "manage_own_2fa"
            ]
        },
        "viewer": {
            "display_name": "Viewer",
            "permissions": [
                "view_dashboards", "view_reports", "access_regulatory_data", "manage_own_2fa"
            ]
        }
    }
    
    def __init__(self, username: str, email: str, role: str = "viewer", 
                 password_hash: str = "", salt: str = "", created_at: str = None,
                 last_login: str = None, failed_attempts: int = 0, 
                 account_locked: bool = False, two_fa_enabled: bool = False,
                 two_fa_secret: str = "", backup_codes: List[str] = None):
        
        self.username = username
        self.email = email
        self.role = role.lower()
        self.password_hash = password_hash
        self.salt = salt
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login
        self.failed_attempts = failed_attempts
        self.account_locked = account_locked
        self.two_fa_enabled = two_fa_enabled
        self.two_fa_secret = two_fa_secret
        self.backup_codes = backup_codes or []
        
    def get_permissions(self) -> List[str]:
        """Get user permissions based on role"""
        return self.ROLE_DEFINITIONS.get(self.role, {}).get("permissions", [])
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.get_permissions()
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for storage"""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "password_hash": self.password_hash,
            "salt": self.salt,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "failed_attempts": self.failed_attempts,
            "account_locked": self.account_locked,
            "two_fa_enabled": self.two_fa_enabled,
            "two_fa_secret": self.two_fa_secret,
            "backup_codes": self.backup_codes,
            "permissions": self.get_permissions()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EnhancedUser':
        """Create user from dictionary"""
        return cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            role=data.get("role", "viewer"),
            password_hash=data.get("password_hash", ""),
            salt=data.get("salt", ""),
            created_at=data.get("created_at"),
            last_login=data.get("last_login"),
            failed_attempts=data.get("failed_attempts", 0),
            account_locked=data.get("account_locked", False),
            two_fa_enabled=data.get("two_fa_enabled", False),
            two_fa_secret=data.get("two_fa_secret", ""),
            backup_codes=data.get("backup_codes", [])
        )

class SecurityAuditLogger:
    """Security audit logging system"""
    
    def __init__(self, log_file: str = "data/auth/security_audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event_type: str, username: str, details: Dict = None, 
                  ip_address: str = None, user_agent: str = None):
        """Log security event"""
        
        # Get IP and user agent from Flask request if available
        if ip_address is None:
            ip_address = request.remote_addr if request else "unknown"
        if user_agent is None:
            user_agent = request.headers.get('User-Agent', 'unknown') if request else "unknown"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "session_id": session.get("session_id", "unknown") if session else "unknown"
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_recent_events(self, hours: int = 24, username: str = None) -> List[Dict]:
        """Get recent security events"""
        
        if not self.log_file.exists():
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        events = []
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event["timestamp"])
                        
                        if event_time >= cutoff_time:
                            if username is None or event["username"] == username:
                                events.append(event)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)

class TwoFactorAuth:
    """Two-Factor Authentication manager"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate new 2FA secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(username: str, secret: str, issuer: str = "IRAQAF") -> str:
        """Generate QR code for 2FA setup"""
        
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Convert to base64 image
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify 2FA token"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # Allow 30s window
        except Exception:
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes for 2FA recovery"""
        return [secrets.token_hex(4).upper() for _ in range(count)]

class FlaskAuthenticationManager:
    """Flask Enhanced authentication manager with advanced security features"""
    
    def __init__(self, users_file: str = "data/auth/users_enhanced.json"):
        self.users_file = Path(users_file)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.audit_logger = SecurityAuditLogger()
        self._ensure_default_users()
    
    def _ensure_default_users(self):
        """Ensure default admin user exists"""
        
        if not self.users_file.exists():
            # Create default admin user
            admin_user = EnhancedUser(
                username="admin",
                email="admin@iraqaf.com",
                role="admin"
            )
            
            # Set default password
            salt = secrets.token_hex(32)
            password_hash = self._hash_password("admin123", salt)
            admin_user.salt = salt
            admin_user.password_hash = password_hash
            
            # Save user
            users_data = {"admin": admin_user.to_dict()}
            self._save_users(users_data)
            
            logger.info("Created default admin user (admin/admin123)")
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using PBKDF2"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000   # iterations
        ).hex()
    
    def _load_users(self) -> Dict[str, Dict]:
        """Load users from file"""
        
        if not self.users_file.exists():
            return {}
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return {}
    
    def _save_users(self, users_data: Dict[str, Dict]):
        """Save users to file"""
        
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
    
    def authenticate(self, username: str, password: str, 
                    two_fa_token: str = None) -> Tuple[bool, Optional[Dict]]:
        """Enhanced authentication with 2FA support"""
        
        users_data = self._load_users()
        
        if username not in users_data:
            self.audit_logger.log_event("LOGIN_FAILED", username, 
                                      {"reason": "user_not_found"})
            return False, None
        
        user_data = users_data[username]
        user = EnhancedUser.from_dict(user_data)
        
        # Check if account is locked
        if user.account_locked:
            self.audit_logger.log_event("LOGIN_BLOCKED", username, 
                                      {"reason": "account_locked"})
            return False, None
        
        # Verify password
        password_hash = self._hash_password(password, user.salt)
        if password_hash != user.password_hash:
            # Increment failed attempts
            user.failed_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_attempts >= 5:
                user.account_locked = True
                self.audit_logger.log_event("ACCOUNT_LOCKED", username, 
                                          {"failed_attempts": user.failed_attempts})
            
            # Update user data
            users_data[username] = user.to_dict()
            self._save_users(users_data)
            
            self.audit_logger.log_event("LOGIN_FAILED", username, 
                                      {"reason": "invalid_password", 
                                       "failed_attempts": user.failed_attempts})
            return False, None
        
        # Check 2FA if enabled
        if user.two_fa_enabled:
            if not two_fa_token:
                self.audit_logger.log_event("LOGIN_2FA_REQUIRED", username)
                return False, {"requires_2fa": True, "user": user.to_dict()}
            
            if not TwoFactorAuth.verify_token(user.two_fa_secret, two_fa_token):
                self.audit_logger.log_event("LOGIN_2FA_FAILED", username)
                return False, None
        
        # Successful login - reset failed attempts
        user.failed_attempts = 0
        user.last_login = datetime.now().isoformat()
        users_data[username] = user.to_dict()
        self._save_users(users_data)
        
        self.audit_logger.log_event("LOGIN_SUCCESS", username, 
                                  {"2fa_used": user.two_fa_enabled})
        
        return True, user.to_dict()
    
    def create_user(self, username: str, password: str, email: str, 
                   role: str = "viewer") -> Tuple[bool, str]:
        """Create new user with enhanced validation"""
        
        users_data = self._load_users()
        
        # Check if user already exists
        if username in users_data:
            return False, "Username already exists"
        
        # Check if email already exists
        for existing_user in users_data.values():
            if existing_user.get("email") == email:
                return False, "Email already registered"
        
        # Validate password strength
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        # Create new user
        user = EnhancedUser(username=username, email=email, role=role)
        
        # Hash password
        salt = secrets.token_hex(32)
        password_hash = self._hash_password(password, salt)
        user.salt = salt
        user.password_hash = password_hash
        
        # Save user
        users_data[username] = user.to_dict()
        self._save_users(users_data)
        
        self.audit_logger.log_event("USER_CREATED", username, 
                                  {"role": role, "email": email})
        
        return True, "User created successfully"
    
    def setup_2fa(self, username: str) -> Tuple[bool, Dict]:
        """Setup 2FA for user"""
        
        users_data = self._load_users()
        
        if username not in users_data:
            return False, {"error": "User not found"}
        
        user_data = users_data[username]
        user = EnhancedUser.from_dict(user_data)
        
        # Generate 2FA secret and backup codes
        secret = TwoFactorAuth.generate_secret()
        backup_codes = TwoFactorAuth.generate_backup_codes()
        qr_code = TwoFactorAuth.generate_qr_code(username, secret)
        
        # Store secret (not enabled yet)
        user.two_fa_secret = secret
        user.backup_codes = backup_codes
        
        users_data[username] = user.to_dict()
        self._save_users(users_data)
        
        self.audit_logger.log_event("2FA_SETUP_INITIATED", username)
        
        return True, {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes
        }
    
    def enable_2fa(self, username: str, verification_token: str) -> Tuple[bool, str]:
        """Enable 2FA after verification"""
        
        users_data = self._load_users()
        
        if username not in users_data:
            return False, "User not found"
        
        user_data = users_data[username]
        user = EnhancedUser.from_dict(user_data)
        
        # Verify token
        if not TwoFactorAuth.verify_token(user.two_fa_secret, verification_token):
            return False, "Invalid verification token"
        
        # Enable 2FA
        user.two_fa_enabled = True
        users_data[username] = user.to_dict()
        self._save_users(users_data)
        
        self.audit_logger.log_event("2FA_ENABLED", username)
        
        return True, "2FA enabled successfully"
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        
        users_data = self._load_users()
        
        if username not in users_data:
            return None
        
        user_data = users_data[username]
        user = EnhancedUser.from_dict(user_data)
        
        # Remove sensitive data
        safe_data = user.to_dict()
        safe_data.pop("password_hash", None)
        safe_data.pop("salt", None)
        safe_data.pop("two_fa_secret", None)
        safe_data.pop("backup_codes", None)
        
        return safe_data

# Flask decorators
def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated') or not session.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission: str):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('authenticated'):
                return redirect(url_for('login'))
            
            user_permissions = session.get('permissions', [])
            if permission not in user_permissions:
                return render_template('error.html', 
                                     error_code=403, 
                                     error_message="Access denied - insufficient permissions"), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            return render_template('error.html', 
                                 error_code=403, 
                                 error_message="Access denied - admin role required"), 403
        return f(*args, **kwargs)
    return decorated_function
