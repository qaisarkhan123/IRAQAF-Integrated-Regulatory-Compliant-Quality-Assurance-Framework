"""
Multi-Factor Authentication (MFA) Enforcement Module
Implements MFA requirements for sensitive operations
Supports TOTP (Time-based One-Time Passwords) and backup codes
"""

import os
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
import hmac
import hashlib
import base64
import secrets
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class MFAConfig:
    """MFA configuration for a user"""
    user_id: str
    secret_key: str  # Base32 encoded TOTP secret
    backup_codes: List[str] = field(default_factory=list)
    enabled: bool = False
    created_at: str = ""
    last_used: str = ""
    recovery_codes_generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MFAAttempt:
    """Record of MFA authentication attempt"""
    user_id: str
    timestamp: str
    method: str  # "totp", "backup_code"
    success: bool
    ip_address: str = ""
    device_info: str = ""


class TOTPGenerator:
    """Time-based One-Time Password (TOTP) generator"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret key (Base32 encoded)"""
        return base64.b32encode(os.urandom(20)).decode('utf-8')

    @staticmethod
    def generate_totp(secret: str, time_step: int = 30) -> str:
        """
        Generate current TOTP code.

        Args:
            secret: Base32 encoded TOTP secret
            time_step: Time step in seconds (default 30)

        Returns:
            6-digit TOTP code
        """
        try:
            # Decode the secret
            secret_bytes = base64.b32decode(secret)

            # Calculate counter (number of time steps since epoch)
            counter = int(time.time() // time_step)

            # Generate HMAC
            message = counter.to_bytes(8, byteorder='big')
            hmac_hash = hmac.new(secret_bytes, message, hashlib.sha1).digest()

            # Extract 4-byte dynamic binary code
            offset = hmac_hash[-1] & 0x0f
            code = hmac_hash[offset:offset + 4]
            code_int = int.from_bytes(code, byteorder='big') & 0x7fffffff

            # Generate 6-digit code
            totp_code = str(code_int % 1000000).zfill(6)
            return totp_code

        except Exception as e:
            logger.error(f"Error generating TOTP: {e}")
            return ""

    @staticmethod
    def verify_totp(secret: str, code: str, time_step: int = 30, window: int = 1) -> bool:
        """
        Verify TOTP code.

        Args:
            secret: Base32 encoded TOTP secret
            code: 6-digit code to verify
            time_step: Time step in seconds
            window: Number of time steps to check before/after current time

        Returns:
            True if code is valid, False otherwise
        """
        try:
            current_time = int(time.time())

            # Check current and adjacent time steps
            for offset in range(-window, window + 1):
                check_time = current_time + (offset * time_step)
                check_counter = check_time // time_step

                # Generate HMAC for this time step
                secret_bytes = base64.b32decode(secret)
                message = check_counter.to_bytes(8, byteorder='big')
                hmac_hash = hmac.new(secret_bytes, message,
                                     hashlib.sha1).digest()

                offset_val = hmac_hash[-1] & 0x0f
                code_bytes = hmac_hash[offset_val:offset_val + 4]
                code_int = int.from_bytes(
                    code_bytes, byteorder='big') & 0x7fffffff
                totp_code = str(code_int % 1000000).zfill(6)

                if totp_code == code:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error verifying TOTP: {e}")
            return False

    @staticmethod
    def generate_qr_code(secret: str, user_id: str, issuer: str = "IRAQAF") -> bytes:
        """
        Generate QR code for TOTP setup.

        Args:
            secret: Base32 encoded TOTP secret
            user_id: User identifier
            issuer: Issuer name (appears in authenticator app)

        Returns:
            PNG image bytes of QR code
        """
        try:
            # Format: otpauth://totp/ISSUER:user_id?secret=SECRET&issuer=ISSUER
            otpauth_uri = f"otpauth://totp/{issuer}:{user_id}?secret={secret}&issuer={issuer}"

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(otpauth_uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()

        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return b""


class BackupCodeGenerator:
    """Generates and manages backup codes for MFA recovery"""

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.

        Args:
            count: Number of codes to generate

        Returns:
            List of backup codes (format: XXXX-XXXX-XXXX)
        """
        codes = []
        for _ in range(count):
            # Generate 12 random hex characters
            code = secrets.token_hex(6).upper()
            # Format as XXXX-XXXX-XXXX
            formatted = f"{code[0:4]}-{code[4:8]}-{code[8:12]}"
            codes.append(formatted)
        return codes

    @staticmethod
    def verify_backup_code(code: str, stored_codes: List[str]) -> Tuple[bool, str]:
        """
        Verify and consume a backup code.

        Args:
            code: Backup code to verify
            stored_codes: List of stored backup codes

        Returns:
            Tuple of (is_valid, remaining_codes_as_json_string)
        """
        # Normalize the code (remove dashes, convert to uppercase)
        normalized_code = code.replace("-", "").replace(" ", "").upper()

        for i, stored in enumerate(stored_codes):
            stored_normalized = stored.replace("-", "").upper()
            if normalized_code == stored_normalized:
                # Code is valid, remove it from the list
                stored_codes.pop(i)
                return True, str(len(stored_codes))

        return False, str(len(stored_codes))


class MFAManager:
    """Manages MFA for users"""

    def __init__(self, mfa_dir: str = "data/mfa", attempts_log: str = None):
        self.mfa_dir = mfa_dir
        self.attempts_log_path = attempts_log or f"{mfa_dir}/attempts.json"

        # Create directories
        os.makedirs(mfa_dir, exist_ok=True)
        os.makedirs(f"{mfa_dir}/configs", exist_ok=True)

        # Load attempt logs
        self.attempt_logs = self._load_attempt_logs()

    def _load_attempt_logs(self) -> List[Dict[str, Any]]:
        """Load MFA attempt logs"""
        if os.path.exists(self.attempts_log_path):
            try:
                import json
                with open(self.attempts_log_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading attempt logs: {e}")
                return []
        return []

    def _save_attempt_logs(self):
        """Save MFA attempt logs"""
        try:
            import json
            with open(self.attempts_log_path, "w") as f:
                json.dump(self.attempt_logs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving attempt logs: {e}")

    def _get_config_path(self, user_id: str) -> str:
        """Get path to user's MFA config file"""
        return f"{self.mfa_dir}/configs/{user_id}_mfa.json"

    def setup_mfa(self, user_id: str) -> Tuple[str, List[str], bytes]:
        """
        Set up MFA for a user.

        Returns:
            Tuple of (secret_key, backup_codes, qr_code_image_bytes)
        """
        try:
            # Generate TOTP secret
            totp_generator = TOTPGenerator()
            secret = totp_generator.generate_secret()

            # Generate backup codes
            backup_codes = BackupCodeGenerator.generate_backup_codes()

            # Generate QR code
            qr_code = totp_generator.generate_qr_code(secret, user_id)

            # Store configuration (but don't enable yet)
            mfa_config = MFAConfig(
                user_id=user_id,
                secret_key=secret,
                backup_codes=backup_codes,
                enabled=False,
                created_at=datetime.now().isoformat(),
                recovery_codes_generated_at=datetime.now().isoformat()
            )

            # Save config
            config_path = self._get_config_path(user_id)
            import json
            with open(config_path, "w") as f:
                json.dump(mfa_config.to_dict(), f, indent=2)

            logger.info(f"MFA setup initiated for user: {user_id}")

            return secret, backup_codes, qr_code

        except Exception as e:
            logger.error(f"Error setting up MFA: {e}")
            return "", [], b""

    def verify_and_enable_mfa(self, user_id: str, totp_code: str) -> Tuple[bool, str]:
        """
        Verify TOTP code and enable MFA for user.

        Args:
            user_id: User identifier
            totp_code: 6-digit TOTP code to verify

        Returns:
            Tuple of (success, message)
        """
        try:
            config_path = self._get_config_path(user_id)

            if not os.path.exists(config_path):
                return False, "MFA not set up for this user"

            import json
            with open(config_path, "r") as f:
                config_data = json.load(f)

            mfa_config = MFAConfig(**config_data)

            # Verify TOTP code
            totp_generator = TOTPGenerator()
            if not totp_generator.verify_totp(mfa_config.secret_key, totp_code):
                return False, "Invalid TOTP code"

            # Enable MFA
            mfa_config.enabled = True
            with open(config_path, "w") as f:
                json.dump(mfa_config.to_dict(), f, indent=2)

            logger.info(f"MFA enabled for user: {user_id}")
            return True, "MFA successfully enabled"

        except Exception as e:
            logger.error(f"Error enabling MFA: {e}")
            return False, f"Error: {str(e)}"

    def authenticate_with_mfa(self, user_id: str, totp_code: str, ip_address: str = "",
                              device_info: str = "") -> Tuple[bool, str]:
        """
        Authenticate user with MFA.

        Args:
            user_id: User identifier
            totp_code: 6-digit TOTP code or backup code
            ip_address: User's IP address
            device_info: Device information string

        Returns:
            Tuple of (success, message)
        """
        try:
            config_path = self._get_config_path(user_id)

            if not os.path.exists(config_path):
                self._log_attempt(MFAAttempt(
                    user_id=user_id,
                    timestamp=datetime.now().isoformat(),
                    method="unknown",
                    success=False,
                    ip_address=ip_address,
                    device_info=device_info
                ))
                return False, "MFA not configured"

            import json
            with open(config_path, "r") as f:
                config_data = json.load(f)

            mfa_config = MFAConfig(**config_data)

            if not mfa_config.enabled:
                return False, "MFA not enabled for this user"

            # Try TOTP verification first
            totp_generator = TOTPGenerator()
            if totp_generator.verify_totp(mfa_config.secret_key, totp_code):
                mfa_config.last_used = datetime.now().isoformat()
                with open(config_path, "w") as f:
                    json.dump(mfa_config.to_dict(), f, indent=2)

                self._log_attempt(MFAAttempt(
                    user_id=user_id,
                    timestamp=datetime.now().isoformat(),
                    method="totp",
                    success=True,
                    ip_address=ip_address,
                    device_info=device_info
                ))

                logger.info(
                    f"MFA authentication successful for user: {user_id}")
                return True, "Authentication successful"

            # Try backup code
            is_valid, remaining = BackupCodeGenerator.verify_backup_code(
                totp_code, mfa_config.backup_codes)
            if is_valid:
                mfa_config.last_used = datetime.now().isoformat()
                with open(config_path, "w") as f:
                    json.dump(mfa_config.to_dict(), f, indent=2)

                self._log_attempt(MFAAttempt(
                    user_id=user_id,
                    timestamp=datetime.now().isoformat(),
                    method="backup_code",
                    success=True,
                    ip_address=ip_address,
                    device_info=device_info
                ))

                logger.warning(
                    f"Backup code used by {user_id} - {remaining} codes remaining")
                return True, "Authentication successful (backup code used)"

            # Both TOTP and backup code failed
            self._log_attempt(MFAAttempt(
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
                method="totp",
                success=False,
                ip_address=ip_address,
                device_info=device_info
            ))

            return False, "Invalid authentication code"

        except Exception as e:
            logger.error(f"Error during MFA authentication: {e}")
            return False, f"Authentication error: {str(e)}"

    def disable_mfa(self, user_id: str) -> Tuple[bool, str]:
        """
        Disable MFA for a user.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (success, message)
        """
        try:
            config_path = self._get_config_path(user_id)

            if not os.path.exists(config_path):
                return False, "MFA not configured"

            os.remove(config_path)
            logger.info(f"MFA disabled for user: {user_id}")
            return True, "MFA successfully disabled"

        except Exception as e:
            logger.error(f"Error disabling MFA: {e}")
            return False, f"Error: {str(e)}"

    def regenerate_backup_codes(self, user_id: str) -> Tuple[bool, List[str], str]:
        """
        Generate new backup codes for a user.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (success, new_backup_codes, message)
        """
        try:
            config_path = self._get_config_path(user_id)

            if not os.path.exists(config_path):
                return False, [], "MFA not configured"

            import json
            with open(config_path, "r") as f:
                config_data = json.load(f)

            mfa_config = MFAConfig(**config_data)

            # Generate new backup codes
            new_codes = BackupCodeGenerator.generate_backup_codes()
            mfa_config.backup_codes = new_codes
            mfa_config.recovery_codes_generated_at = datetime.now().isoformat()

            # Save updated config
            with open(config_path, "w") as f:
                json.dump(mfa_config.to_dict(), f, indent=2)

            logger.info(f"Backup codes regenerated for user: {user_id}")
            return True, new_codes, "Backup codes successfully regenerated"

        except Exception as e:
            logger.error(f"Error regenerating backup codes: {e}")
            return False, [], f"Error: {str(e)}"

    def is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for a user"""
        try:
            config_path = self._get_config_path(user_id)

            if not os.path.exists(config_path):
                return False

            import json
            with open(config_path, "r") as f:
                config_data = json.load(f)

            return config_data.get("enabled", False)

        except Exception as e:
            logger.error(f"Error checking MFA status: {e}")
            return False

    def _log_attempt(self, attempt: MFAAttempt):
        """Log MFA authentication attempt"""
        self.attempt_logs.append(asdict(attempt))
        self._save_attempt_logs()

    def get_failed_attempts(self, user_id: str, hours: int = 24) -> int:
        """
        Get number of failed MFA attempts for a user in the last N hours.

        Args:
            user_id: User identifier
            hours: Number of hours to look back

        Returns:
            Number of failed attempts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        failed_count = 0
        for log in self.attempt_logs:
            if log.get("user_id") == user_id and not log.get("success", False):
                try:
                    log_time = datetime.fromisoformat(log.get("timestamp", ""))
                    if log_time > cutoff_time:
                        failed_count += 1
                except:
                    pass

        return failed_count

    def is_account_locked(self, user_id: str, max_attempts: int = 5, lockout_hours: int = 1) -> bool:
        """
        Check if account is locked due to too many failed attempts.

        Args:
            user_id: User identifier
            max_attempts: Maximum allowed failed attempts
            lockout_hours: Lockout duration in hours

        Returns:
            True if account is locked, False otherwise
        """
        failed_attempts = self.get_failed_attempts(
            user_id, hours=lockout_hours)
        return failed_attempts >= max_attempts

    def generate_mfa_report(self) -> str:
        """Generate MFA audit report"""
        report = f"""
MFA (Multi-Factor Authentication) Audit Report
{'='*60}
Generated: {datetime.now().isoformat()}

Summary:
{'-'*60}
Total Authentication Attempts: {len(self.attempt_logs)}

Successful Attempts: {sum(1 for log in self.attempt_logs if log.get('success', False))}
Failed Attempts: {sum(1 for log in self.attempt_logs if not log.get('success', False))}

Authentication Methods Used:
"""

        totp_count = sum(
            1 for log in self.attempt_logs if log.get("method") == "totp")
        backup_count = sum(1 for log in self.attempt_logs if log.get(
            "method") == "backup_code")

        report += f"""
  - TOTP: {totp_count}
  - Backup Codes: {backup_count}

Recent Attempts (Last 10):
{'-'*60}
"""

        for log in self.attempt_logs[-10:]:
            status = "✓" if log.get("success") else "✗"
            report += f"{status} {log.get('timestamp')}: {log.get('method')} ({log.get('user_id')})\n"

        report += f"""
Recommendations:
{'-'*60}
✓ Monitor failed MFA attempts regularly
✓ Implement account lockout after N failed attempts
✓ Regenerate backup codes periodically
✓ Encourage users to enable MFA
✓ Audit access from unusual locations/devices
"""

        return report
