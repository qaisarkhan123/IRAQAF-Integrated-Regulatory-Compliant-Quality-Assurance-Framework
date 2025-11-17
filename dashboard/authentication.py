"""
Authentication and role-based access control (RBAC) system.
Manages user sessions, credentials, and permissions.
"""

import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import streamlit as st

logger = logging.getLogger(__name__)


class User:
    """Represents a system user with roles and permissions."""
    
    # Role definitions with permissions
    ROLE_DEFINITIONS = {
        "admin": {
            "display_name": "Administrator",
            "permissions": [
                "view_all_reports",
                "export_data",
                "create_alerts",
                "manage_users",
                "manage_settings",
                "manage_compliance_rules",
                "access_audit_logs"
            ]
        },
        "analyst": {
            "display_name": "Compliance Analyst",
            "permissions": [
                "view_all_reports",
                "export_data",
                "create_alerts",
                "view_audit_logs",
                "access_regulatory_data"
            ]
        },
        "viewer": {
            "display_name": "Viewer",
            "permissions": [
                "view_dashboards",
                "view_reports",
                "access_regulatory_data"
            ]
        }
    }
    
    def __init__(self, username: str, role: str = "viewer", domain: str = None):
        """
        Initialize a user.
        
        Args:
            username: Username
            role: User role (admin, analyst, viewer)
            domain: Optional domain restriction (e.g., FDA, EPA)
        """
        self.username = username
        self.role = role
        self.domain = domain
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        if self.role not in self.ROLE_DEFINITIONS:
            return False
        permissions = self.ROLE_DEFINITIONS[self.role]["permissions"]
        return permission in permissions
    
    def get_role_display_name(self) -> str:
        """Get human-readable role name."""
        return self.ROLE_DEFINITIONS.get(self.role, {}).get("display_name", self.role)
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            "username": self.username,
            "role": self.role,
            "domain": self.domain,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active
        }


class AuthenticationManager:
    """Manages user authentication and session management."""
    
    def __init__(self, auth_dir: Path = None):
        """Initialize authentication manager."""
        if auth_dir is None:
            auth_dir = Path.cwd() / "data" / "auth"
        self.auth_dir = auth_dir
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.auth_dir / "users.json"
        self.sessions_file = self.auth_dir / "sessions.json"
        self._load_users()
        self._load_sessions()
        self._create_default_user()
    
    def _load_users(self) -> None:
        """Load users from storage."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    self.users = {
                        username: {
                            **user_data,
                            "password_hash": user_data.get("password_hash", "")
                        }
                        for username, user_data in data.items()
                    }
            else:
                self.users = {}
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            self.users = {}
    
    def _save_users(self) -> None:
        """Persist users to storage."""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
    
    def _load_sessions(self) -> None:
        """Load active sessions."""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
            else:
                self.sessions = {}
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.sessions = {}
    
    def _save_sessions(self) -> None:
        """Persist sessions to storage."""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def _create_default_user(self) -> None:
        """Create default admin user if none exists."""
        if not self.users:
            self.create_user(
                username="admin",
                password="admin_default_123",
                role="admin",
                display_name="Administrator"
            )
            logger.info("Created default admin user")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self,
                   username: str,
                   password: str,
                   role: str = "viewer",
                   display_name: str = None,
                   domain: str = None) -> bool:
        """
        Create a new user.
        
        Args:
            username: Username
            password: User password
            role: User role (admin, analyst, viewer)
            display_name: User's display name
            domain: Optional domain restriction
            
        Returns:
            True if successful, False if user already exists
        """
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return False
        
        self.users[username] = {
            "username": username,
            "password_hash": self._hash_password(password),
            "role": role,
            "display_name": display_name or username,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        self._save_users()
        logger.info(f"Created user {username} with role {role}")
        return True
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, user_data)
        """
        if username not in self.users:
            logger.warning(f"Authentication failed for non-existent user {username}")
            return False, None
        
        user = self.users[username]
        if not user.get("is_active", False):
            logger.warning(f"Authentication failed for inactive user {username}")
            return False, None
        
        password_hash = self._hash_password(password)
        if user.get("password_hash") != password_hash:
            logger.warning(f"Authentication failed for user {username} - invalid password")
            return False, None
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        self._save_users()
        
        logger.info(f"User {username} authenticated successfully")
        return True, user
    
    def create_session(self, username: str, session_id: str = None) -> str:
        """
        Create a user session.
        
        Args:
            username: Username
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = hashlib.sha256(
                f"{username}{datetime.now().timestamp()}".encode()
            ).hexdigest()
        
        self.sessions[session_id] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        self._save_sessions()
        return session_id
    
    def validate_session(self, session_id: str, timeout_minutes: int = 480) -> bool:
        """
        Validate a session.
        
        Args:
            session_id: Session ID
            timeout_minutes: Session timeout in minutes (default 8 hours)
            
        Returns:
            True if session is valid
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        last_activity = datetime.fromisoformat(session["last_activity"])
        
        if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
            del self.sessions[session_id]
            self._save_sessions()
            return False
        
        # Update last activity
        session["last_activity"] = datetime.now().isoformat()
        self._save_sessions()
        return True
    
    def get_session_user(self, session_id: str) -> Optional[Dict]:
        """Get user data from session."""
        if not self.validate_session(session_id):
            return None
        
        username = self.sessions[session_id]["username"]
        return self.users.get(username)
    
    def end_session(self, session_id: str) -> bool:
        """End a user session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            return True
        return False
    
    def list_users(self) -> List[Dict]:
        """List all users."""
        return list(self.users.values())
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account."""
        if username in self.users:
            self.users[username]["is_active"] = False
            self._save_users()
            return True
        return False
    
    def update_user_role(self, username: str, new_role: str) -> bool:
        """Update a user's role."""
        if username in self.users and new_role in User.ROLE_DEFINITIONS:
            self.users[username]["role"] = new_role
            self._save_users()
            return True
        return False


def render_login_form() -> Optional[Tuple[str, str]]:
    """Render login form and return (username, password) if submitted."""
    st.title("🔐 IRAQAF Dashboard Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            return username, password
    
    return None


def check_authentication() -> bool:
    """Check if user is authenticated. Returns True if authenticated."""
    if "session_id" not in st.session_state:
        return False
    
    auth_manager = AuthenticationManager()
    user = auth_manager.get_session_user(st.session_state.session_id)
    return user is not None


def require_permission(permission: str) -> bool:
    """Check if current user has a specific permission."""
    if "session_id" not in st.session_state:
        return False
    
    auth_manager = AuthenticationManager()
    user = auth_manager.get_session_user(st.session_state.session_id)
    
    if not user:
        return False
    
    role = user.get("role", "viewer")
    permissions = User.ROLE_DEFINITIONS.get(role, {}).get("permissions", [])
    return permission in permissions
