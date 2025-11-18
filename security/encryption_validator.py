"""
Encryption & TLS Validation Module
Verifies system encryption configuration meets security standards
Checks for AES-256, TLS 1.2+, key management policies
"""

import re
import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import yaml
import json
import logging
from datetime import datetime
import ssl
import socket

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256 = "aes-256"
    AES_192 = "aes-192"
    AES_128 = "aes-128"
    CHACHA20 = "chacha20"
    UNKNOWN = "unknown"
    WEAK = "weak"


class TLSVersion(Enum):
    """TLS versions"""
    TLS_1_3 = "1.3"
    TLS_1_2 = "1.2"
    TLS_1_1 = "1.1"
    TLS_1_0 = "1.0"
    UNKNOWN = "unknown"


@dataclass
class EncryptionConfig:
    """Encryption configuration details"""
    algorithm: EncryptionAlgorithm
    key_length: int
    mode: str  # CBC, GCM, ECB, etc.
    tls_version: TLSVersion
    key_rotation_days: int
    location: str  # Where in config this was found
    score: float  # 0-1 compliance score
    issues: List[str]  # Any identified issues
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class EncryptionValidator:
    """Validates encryption configuration"""

    # Security standards
    REQUIRED_ALGORITHM = EncryptionAlgorithm.AES_256
    REQUIRED_KEY_LENGTH = 256
    REQUIRED_TLS_VERSION = TLSVersion.TLS_1_2
    RECOMMENDED_KEY_ROTATION_DAYS = 90
    MAX_KEY_ROTATION_DAYS = 365

    # Weak algorithms to flag
    WEAK_ALGORITHMS = {
        'des', 'md5', 'rc4', 'md4', 'sha1', 'aes-128', 'aes-192', 'ecb'
    }

    @staticmethod
    def parse_encryption_config(config: Dict[str, Any]) -> Optional[EncryptionConfig]:
        """
        Parse encryption configuration from system config.

        Args:
            config: Configuration dictionary

        Returns:
            EncryptionConfig or None if not found
        """
        issues = []
        algorithm = EncryptionAlgorithm.UNKNOWN
        key_length = 0
        mode = "unknown"
        tls_version = TLSVersion.UNKNOWN
        key_rotation = 365

        # Search for encryption settings (common paths)
        search_keys = [
            'encryption', 'security', 'crypto', 'tls', 'ssl',
            'database', 'storage', 'auth'
        ]

        for key in search_keys:
            if key in config:
                section = config[key]
                if isinstance(section, dict):
                    # Look for algorithm
                    for algo_key in ['algorithm', 'cipher', 'method', 'type']:
                        if algo_key in section:
                            algo_val = str(section[algo_key]).lower()
                            algorithm = EncryptionValidator._parse_algorithm(algo_val)

                    # Look for key length
                    for length_key in ['key_length', 'key_size', 'bits']:
                        if length_key in section:
                            try:
                                key_length = int(section[length_key])
                            except (ValueError, TypeError):
                                pass

                    # Look for mode
                    for mode_key in ['mode', 'cipher_mode']:
                        if mode_key in section:
                            mode = str(section[mode_key]).upper()

                    # Look for TLS version
                    for tls_key in ['tls_version', 'min_tls_version', 'ssl_version']:
                        if tls_key in section:
                            tls_val = str(section[tls_key]).lower()
                            tls_version = EncryptionValidator._parse_tls_version(tls_val)

                    # Look for key rotation
                    for rotation_key in ['key_rotation_days', 'rotation_period']:
                        if rotation_key in section:
                            try:
                                key_rotation = int(section[rotation_key])
                            except (ValueError, TypeError):
                                pass

        # Validate and score
        if algorithm == EncryptionAlgorithm.UNKNOWN:
            issues.append("Encryption algorithm not specified in configuration")

        if key_length < 256:
            issues.append(f"Key length {key_length} is below required 256-bit")

        if tls_version in [TLSVersion.UNKNOWN, TLSVersion.TLS_1_0, TLSVersion.TLS_1_1]:
            issues.append(f"TLS version {tls_version.value} is outdated or not found")

        if key_rotation > EncryptionValidator.RECOMMENDED_KEY_ROTATION_DAYS:
            issues.append(f"Key rotation period {key_rotation} days exceeds recommendation ({EncryptionValidator.RECOMMENDED_KEY_ROTATION_DAYS} days)")

        # Calculate score
        score = EncryptionValidator._calculate_score(algorithm, key_length, tls_version, issues)

        return EncryptionConfig(
            algorithm=algorithm,
            key_length=key_length,
            mode=mode,
            tls_version=tls_version,
            key_rotation_days=key_rotation,
            location="system configuration",
            score=score,
            issues=issues
        )

    @staticmethod
    def _parse_algorithm(algo_str: str) -> EncryptionAlgorithm:
        """Parse algorithm string to EncryptionAlgorithm"""
        algo_lower = algo_str.lower().strip()

        if 'aes' in algo_lower and '256' in algo_lower:
            return EncryptionAlgorithm.AES_256
        elif 'aes' in algo_lower and '192' in algo_lower:
            return EncryptionAlgorithm.AES_192
        elif 'aes' in algo_lower and '128' in algo_lower:
            return EncryptionAlgorithm.AES_128
        elif 'chacha' in algo_lower:
            return EncryptionAlgorithm.CHACHA20
        elif any(weak in algo_lower for weak in EncryptionValidator.WEAK_ALGORITHMS):
            return EncryptionAlgorithm.WEAK
        else:
            return EncryptionAlgorithm.UNKNOWN

    @staticmethod
    def _parse_tls_version(tls_str: str) -> TLSVersion:
        """Parse TLS version string"""
        tls_lower = tls_str.lower().strip()

        if '1.3' in tls_lower or '13' in tls_lower:
            return TLSVersion.TLS_1_3
        elif '1.2' in tls_lower or '12' in tls_lower:
            return TLSVersion.TLS_1_2
        elif '1.1' in tls_lower or '11' in tls_lower:
            return TLSVersion.TLS_1_1
        elif '1.0' in tls_lower or '10' in tls_lower or 'tls' in tls_lower:
            return TLSVersion.TLS_1_0
        else:
            return TLSVersion.UNKNOWN

    @staticmethod
    def _calculate_score(algorithm: EncryptionAlgorithm, key_length: int,
                         tls_version: TLSVersion, issues: List[str]) -> float:
        """Calculate compliance score (0-1)"""
        score = 1.0

        # Algorithm scoring
        if algorithm == EncryptionAlgorithm.AES_256:
            score *= 1.0
        elif algorithm == EncryptionAlgorithm.AES_192:
            score *= 0.9
        elif algorithm == EncryptionAlgorithm.AES_128:
            score *= 0.7
        elif algorithm == EncryptionAlgorithm.CHACHA20:
            score *= 0.95
        elif algorithm == EncryptionAlgorithm.WEAK:
            score *= 0.2
        else:
            score *= 0.0

        # Key length scoring
        if key_length >= 256:
            score *= 1.0
        elif key_length >= 192:
            score *= 0.9
        elif key_length >= 128:
            score *= 0.7
        elif key_length > 0:
            score *= 0.3
        else:
            score *= 0.0

        # TLS scoring
        if tls_version == TLSVersion.TLS_1_3:
            score *= 1.0
        elif tls_version == TLSVersion.TLS_1_2:
            score *= 0.95
        elif tls_version == TLSVersion.TLS_1_1:
            score *= 0.5
        elif tls_version == TLSVersion.TLS_1_0:
            score *= 0.1
        else:
            score *= 0.0

        # Issue penalty
        score *= max(0.0, 1.0 - (len(issues) * 0.1))

        return max(0.0, min(1.0, score))

    @staticmethod
    def validate_encryption_config(config: Dict[str, Any]) -> Tuple[bool, EncryptionConfig, List[str]]:
        """
        Validate encryption meets standards.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_compliant, config_details, detailed_messages)
        """
        enc_config = EncryptionValidator.parse_encryption_config(config)

        if enc_config is None:
            return False, None, ["No encryption configuration found"]

        messages = []

        # Check algorithm
        if enc_config.algorithm != EncryptionAlgorithm.AES_256:
            messages.append(f"⚠️ Algorithm: {enc_config.algorithm.value} (required: AES-256)")
        else:
            messages.append(f"✓ Algorithm: {enc_config.algorithm.value}")

        # Check key length
        if enc_config.key_length < 256:
            messages.append(f"⚠️ Key length: {enc_config.key_length}-bit (required: 256-bit)")
        else:
            messages.append(f"✓ Key length: {enc_config.key_length}-bit")

        # Check TLS version
        if enc_config.tls_version not in [TLSVersion.TLS_1_3, TLSVersion.TLS_1_2]:
            messages.append(f"⚠️ TLS version: {enc_config.tls_version.value} (required: 1.2+)")
        else:
            messages.append(f"✓ TLS version: {enc_config.tls_version.value}")

        # Check key rotation
        if enc_config.key_rotation_days > EncryptionValidator.RECOMMENDED_KEY_ROTATION_DAYS:
            messages.append(f"⚠️ Key rotation: {enc_config.key_rotation_days} days (recommended: {EncryptionValidator.RECOMMENDED_KEY_ROTATION_DAYS} days)")
        else:
            messages.append(f"✓ Key rotation: {enc_config.key_rotation_days} days")

        # Add any additional issues
        messages.extend(enc_config.issues)

        is_compliant = (
            enc_config.algorithm == EncryptionAlgorithm.AES_256 and
            enc_config.key_length >= 256 and
            enc_config.tls_version in [TLSVersion.TLS_1_3, TLSVersion.TLS_1_2]
        )

        return is_compliant, enc_config, messages

    @staticmethod
    def check_tls_certificate(hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Check TLS certificate for hostname.

        Args:
            hostname: Server hostname
            port: Port to check (default 443)

        Returns:
            Certificate details
        """
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()

                    return {
                        "hostname": hostname,
                        "port": port,
                        "connected": True,
                        "cert": cert,
                        "cipher": cipher,
                        "protocol": ssock.version()
                    }
        except Exception as e:
            return {
                "hostname": hostname,
                "port": port,
                "connected": False,
                "error": str(e)
            }

    @staticmethod
    def generate_encryption_report(config: Dict[str, Any]) -> str:
        """Generate human-readable encryption audit report"""
        is_compliant, enc_config, messages = EncryptionValidator.validate_encryption_config(config)

        report = f"""
Encryption Configuration Audit Report
{'='*60}
Timestamp: {datetime.now().isoformat()}
Compliance Status: {'✓ COMPLIANT' if is_compliant else '✗ NON-COMPLIANT'}

Configuration Details:
{'-'*60}
Algorithm: {enc_config.algorithm.value if enc_config else 'Not found'}
Key Length: {enc_config.key_length}-bit{' (✓ meets requirement)' if enc_config and enc_config.key_length >= 256 else ' (⚠ below requirement)' if enc_config else ''}
TLS Version: {enc_config.tls_version.value if enc_config else 'Not found'}
Key Rotation: {enc_config.key_rotation_days} days{' (✓ recommended)' if enc_config and enc_config.key_rotation_days <= 90 else ' (⚠ exceeds recommendation)' if enc_config else ''}
Compliance Score: {enc_config.score:.1%}

Validation Results:
{'-'*60}
"""

        for msg in messages:
            report += f"{msg}\n"

        report += f"""
Recommendations:
{'-'*60}
"""
        if not is_compliant:
            report += "- Implement AES-256 encryption for data at rest\n"
            report += "- Enable TLS 1.2 or higher for data in transit\n"
            report += "- Establish 90-day key rotation policy\n"
            report += "- Document key management procedures\n"

        return report
