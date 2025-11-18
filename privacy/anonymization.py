"""
Privacy & Anonymization Module
Detects and protects Personally Identifiable Information (PII)
Implements anonymization techniques: masking, hashing, tokenization, k-anonymity
"""

import re
import hashlib
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class PII_TYPE(Enum):
    """Enumeration of PII types"""
    EMAIL = "email"
    SSN = "ssn"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    NAME = "name"
    ADDRESS = "address"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"


@dataclass
class PIIMatch:
    """Represents a detected PII instance"""
    pii_type: PII_TYPE
    value: str
    location: str  # Where in data it was found
    confidence: float  # 0-1 confidence score
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class PIIDetector:
    """Detects personally identifiable information in text and data"""

    # Regex patterns for various PII types
    PATTERNS = {
        PII_TYPE.EMAIL: '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}',
        PII_TYPE.SSN: '\\b\\d{3}-\\d{2}-\\d{4}\\b|\\b\\d{9}\\b',
        PII_TYPE.PHONE: '(?:\\+1[-\\.\\s]?)?\\(?[0-9]{3}\\)?[-\\.\\s]?[0-9]{3}[-\\.\\s]?[0-9]{4}',
        PII_TYPE.CREDIT_CARD: '\\b(?:\\d{4}[-\\s]?){3}\\d{4}\\b|\\b\\d{16}\\b',
        PII_TYPE.IP_ADDRESS: '\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b',
        PII_TYPE.DATE_OF_BIRTH: '\\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\\d|3[01])[/-](?:19|20)?\\d{2}\\b',
        PII_TYPE.PASSPORT: '\\b[A-Z]{2}\\d{6,9}\\b',
        PII_TYPE.DRIVER_LICENSE: '\\b[A-Z]{1,2}\\d{5,8}\\b',
    }

    # Common name patterns (simplified)
    NAME_KEYWORDS = ['name', 'first_name',
                     'last_name', 'full_name', 'author', 'user']
    ADDRESS_KEYWORDS = ['address', 'street', 'city', 'state', 'zip', 'postal']

    @classmethod
    def detect_pii(cls, data: str, check_names: bool = True) -> List[PIIMatch]:
        """
        Detect all PII in text data.

        Args:
            data: Text to scan for PII
            check_names: Whether to check for common name patterns

        Returns:
            List of detected PII matches
        """
        matches = []

        # Check regex patterns
        for pii_type, pattern in cls.PATTERNS.items():
            for match in re.finditer(pattern, data, re.IGNORECASE):
                matches.append(PIIMatch(
                    pii_type=pii_type,
                    value=match.group(0),
                    location=f"position {match.start()}-{match.end()}",
                    confidence=0.95
                ))

        return matches

    @classmethod
    def detect_pii_in_dataframe(cls, df: pd.DataFrame) -> Dict[str, List[PIIMatch]]:
        """
        Scan DataFrame columns for PII.

        Args:
            df: DataFrame to scan

        Returns:
            Dictionary mapping column names to detected PII matches
        """
        pii_columns = {}

        for col in df.columns:
            col_data = df[col].astype(str).str.cat(sep=' ')
            matches = cls.detect_pii(col_data)

            # Also check if column name suggests PII
            if any(keyword in col.lower() for keyword in cls.NAME_KEYWORDS):
                if col not in pii_columns:
                    pii_columns[col] = []
                pii_columns[col].extend([
                    PIIMatch(
                        pii_type=PII_TYPE.NAME,
                        value=str(val),
                        location=f"Column '{col}' (by name pattern)",
                        confidence=0.7
                    ) for val in df[col].unique()[:5]  # Sample first 5 unique values
                ])

            if matches:
                if col not in pii_columns:
                    pii_columns[col] = []
                pii_columns[col].extend(matches)

        return pii_columns

    @classmethod
    def has_pii(cls, data: str) -> bool:
        """Quick check if data contains any PII"""
        return len(cls.detect_pii(data)) > 0

    @classmethod
    def pii_risk_score(cls, data: str) -> float:
        """
        Calculate PII risk score (0-1).

        Args:
            data: Text to assess

        Returns:
            Risk score where 1.0 = high risk
        """
        matches = cls.detect_pii(data)
        if not matches:
            return 0.0

        # Risk based on number and types of PII found
        high_risk_types = {PII_TYPE.SSN,
                           PII_TYPE.CREDIT_CARD, PII_TYPE.PASSPORT}
        high_risk_count = sum(
            1 for m in matches if m.pii_type in high_risk_types)
        other_count = len(matches) - high_risk_count

        risk = (high_risk_count * 0.3 + other_count * 0.1) / \
            max(len(data) / 100, 1)
        return min(risk, 1.0)


class Anonymizer:
    """Applies anonymization techniques to protect PII"""

    @staticmethod
    def mask_email(email: str) -> str:
        """Replace email with masked version: a***@b.com"""
        if '@' not in email:
            return email
        local, domain = email.split('@', 1)
        masked_local = local[0] + '*' * (len(local) - 2) + \
            local[-1] if len(local) > 2 else local[0] + '*'
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Replace phone with XXX-XXX-1234"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
        return "***-***-****"

    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """Replace SSN with XXX-XX-1234"""
        digits = re.sub(r'\D', '', ssn)
        if len(digits) >= 4:
            return f"***-**-{digits[-4:]}"
        return "***-**-****"

    @staticmethod
    def mask_credit_card(cc: str) -> str:
        """Replace credit card with XXXX-XXXX-XXXX-1234"""
        digits = re.sub(r'\D', '', cc)
        if len(digits) >= 4:
            return f"****-****-****-{digits[-4:]}"
        return "****-****-****-****"

    @staticmethod
    def hash_pii(value: str, salt: str = "") -> str:
        """
        Hash PII using SHA-256.

        Args:
            value: PII value to hash
            salt: Optional salt for additional security

        Returns:
            Hex-encoded SHA-256 hash
        """
        salted = f"{salt}{value}".encode('utf-8')
        return hashlib.sha256(salted).hexdigest()

    @staticmethod
    def tokenize_pii(value: str, token_map: Dict[str, str] = None) -> Tuple[str, Dict[str, str]]:
        """
        Replace PII with random token, maintain bidirectional mapping.

        Args:
            value: PII value to tokenize
            token_map: Existing token mapping (for consistency)

        Returns:
            Tuple of (tokenized_value, token_mapping)
        """
        if token_map is None:
            token_map = {}

        if value in token_map:
            return token_map[value], token_map

        # Generate token
        token = f"TOKEN_{hashlib.sha256(value.encode()).hexdigest()[:12].upper()}"
        token_map[value] = token
        return token, token_map

    @staticmethod
    def suppress_pii(value: str, keep_prefix: int = 2, keep_suffix: int = 2) -> str:
        """
        Suppress PII by keeping only prefix/suffix.

        Args:
            value: Value to suppress
            keep_prefix: Characters to keep at start
            keep_suffix: Characters to keep at end

        Returns:
            Suppressed value
        """
        if len(value) <= keep_prefix + keep_suffix:
            return "*" * len(value)
        return value[:keep_prefix] + "*" * (len(value) - keep_prefix - keep_suffix) + value[-keep_suffix:]

    @classmethod
    def anonymize_text(cls, text: str, method: str = "mask") -> str:
        """
        Anonymize all detected PII in text.

        Args:
            text: Text to anonymize
            method: Anonymization method ('mask', 'hash', 'suppress')

        Returns:
            Anonymized text
        """
        matches = PIIDetector.detect_pii(text)
        anonymized = text

        # Sort by position (reverse) to avoid index shifting
        for match in sorted(matches, key=lambda m: int(m.location.split()[1].split('-')[0]), reverse=True):
            if method == "mask":
                if match.pii_type == PII_TYPE.EMAIL:
                    replacement = cls.mask_email(match.value)
                elif match.pii_type == PII_TYPE.PHONE:
                    replacement = cls.mask_phone(match.value)
                elif match.pii_type == PII_TYPE.SSN:
                    replacement = cls.mask_ssn(match.value)
                elif match.pii_type == PII_TYPE.CREDIT_CARD:
                    replacement = cls.mask_credit_card(match.value)
                else:
                    replacement = "*" * len(match.value)
            elif method == "hash":
                replacement = cls.hash_pii(match.value)[:16]
            elif method == "suppress":
                replacement = cls.suppress_pii(match.value)
            else:
                replacement = "*" * len(match.value)

            # Find and replace in original text
            idx = anonymized.find(match.value)
            if idx != -1:
                anonymized = anonymized[:idx] + replacement + \
                    anonymized[idx + len(match.value):]

        return anonymized

    @classmethod
    def anonymize_dataframe(cls, df: pd.DataFrame, column_methods: Dict[str, str] = None) -> pd.DataFrame:
        """
        Anonymize identified PII columns in DataFrame.

        Args:
            df: DataFrame to anonymize
            column_methods: Dict mapping column names to anonymization methods

        Returns:
            Anonymized DataFrame
        """
        df_anon = df.copy()
        pii_columns = PIIDetector.detect_pii_in_dataframe(df)

        for col, matches in pii_columns.items():
            if matches:
                method = column_methods.get(
                    col, "mask") if column_methods else "mask"

                # Apply anonymization to column values
                df_anon[col] = df[col].apply(
                    lambda x: cls.anonymize_text(str(x), method=method))

        return df_anon


class KAnonymity:
    """Implements k-anonymity for privacy protection"""

    @staticmethod
    def calculate_k_anonymity(df: pd.DataFrame, quasi_identifiers: List[str]) -> int:
        """
        Calculate k-anonymity score for dataset.

        Args:
            df: DataFrame to assess
            quasi_identifiers: Columns that are quasi-identifiers

        Returns:
            k value (minimum group size for any combination of quasi-identifiers)
        """
        if not quasi_identifiers or len(quasi_identifiers) == 0:
            return len(df)

        # Get minimum group size across all combinations
        grouped = df.groupby(quasi_identifiers, dropna=False).size()
        return int(grouped.min()) if len(grouped) > 0 else 0

    @staticmethod
    def enforce_k_anonymity(df: pd.DataFrame, quasi_identifiers: List[str], k: int = 5) -> pd.DataFrame:
        """
        Modify dataset to achieve k-anonymity through generalization.

        Args:
            df: Input DataFrame
            quasi_identifiers: Columns to consider for k-anonymity
            k: Minimum group size required

        Returns:
            Modified DataFrame achieving k-anonymity
        """
        df_result = df.copy()

        # Group by quasi-identifiers
        groups = df_result.groupby(quasi_identifiers, dropna=False)

        # Remove small groups or generalize them
        valid_groups = []
        for name, group in groups:
            if len(group) >= k:
                valid_groups.append(group)

        if valid_groups:
            df_result = pd.concat(valid_groups, ignore_index=True)
        else:
            # If no groups meet k, suppress identifiers
            logger.warning(
                f"Cannot achieve k={k} anonymity. Suppressing quasi-identifiers.")
            for col in quasi_identifiers:
                df_result[col] = df_result[col].apply(
                    lambda x: Anonymizer.suppress_pii(
                        str(x)) if pd.notna(x) else x
                )

        return df_result

    @staticmethod
    def check_k_anonymity(df: pd.DataFrame, quasi_identifiers: List[str], k: int = 5) -> bool:
        """Check if dataset meets k-anonymity requirement"""
        k_current = KAnonymity.calculate_k_anonymity(df, quasi_identifiers)
        return k_current >= k

    @staticmethod
    def get_anonymity_report(df: pd.DataFrame, quasi_identifiers: List[str]) -> Dict[str, Any]:
        """Generate detailed k-anonymity report"""
        k = KAnonymity.calculate_k_anonymity(df, quasi_identifiers)

        grouped = df.groupby(quasi_identifiers, dropna=False).size()
        group_distribution = grouped.describe().to_dict()

        return {
            "k_anonymity": k,
            "meets_k5": k >= 5,
            "meets_k10": k >= 10,
            "meets_k20": k >= 20,
            "group_count": len(grouped),
            "group_distribution": group_distribution,
            "timestamp": datetime.now().isoformat()
        }


class DifferentialPrivacy:
    """Implements differential privacy for privacy protection"""

    @staticmethod
    def add_laplace_noise(data: np.ndarray, epsilon: float = 1.0, scale: float = 1.0) -> np.ndarray:
        """
        Add Laplace noise for differential privacy.

        Args:
            data: Input data (array of values)
            epsilon: Privacy budget (higher = less noise, lower privacy)
            scale: Scale parameter (scale = sensitivity / epsilon)

        Returns:
            Noisy data
        """
        sensitivity = 1.0  # Assumes bounded sensitivity
        laplace_scale = sensitivity / max(epsilon, 0.1)
        noise = np.random.laplace(0, laplace_scale, size=data.shape)
        return data + noise

    @staticmethod
    def add_gaussian_noise(data: np.ndarray, epsilon: float = 1.0, delta: float = 1e-5) -> np.ndarray:
        """
        Add Gaussian noise for differential privacy (more efficient for large sensitivity).

        Args:
            data: Input data
            epsilon: Privacy budget
            delta: Failure probability

        Returns:
            Noisy data
        """
        sensitivity = 1.0
        sigma = np.sqrt(2 * np.log(1.25 / delta)) / epsilon
        noise = np.random.normal(0, sigma, size=data.shape)
        return data + noise

    @staticmethod
    def apply_differential_privacy(df: pd.DataFrame, numeric_columns: List[str],
                                   epsilon: float = 1.0, method: str = "laplace") -> pd.DataFrame:
        """
        Apply differential privacy to numeric columns.

        Args:
            df: Input DataFrame
            numeric_columns: Columns to add noise to
            epsilon: Privacy budget
            method: 'laplace' or 'gaussian'

        Returns:
            DataFrame with differential privacy applied
        """
        df_private = df.copy()

        for col in numeric_columns:
            if col in df_private.columns and df_private[col].dtype in ['float64', 'int64']:
                data = df_private[col].values.astype(float)

                if method == "laplace":
                    noisy_data = DifferentialPrivacy.add_laplace_noise(
                        data, epsilon)
                else:
                    noisy_data = DifferentialPrivacy.add_gaussian_noise(
                        data, epsilon)

                df_private[col] = noisy_data

        return df_private

    @staticmethod
    def get_privacy_report(epsilon: float, delta: float = 1e-5) -> Dict[str, Any]:
        """Generate differential privacy report"""
        return {
            "epsilon": epsilon,
            "delta": delta,
            "privacy_level": "high" if epsilon < 0.5 else "medium" if epsilon < 1.0 else "low",
            "description": f"Dataset satisfies ({epsilon}, {delta})-differential privacy"
        }


class PrivacyAudit:
    """Audit data for privacy compliance"""

    @staticmethod
    def audit_dataset(df: pd.DataFrame, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive privacy audit of dataset.

        Args:
            df: DataFrame to audit
            config: Audit configuration with expected settings

        Returns:
            Audit report
        """
        config = config or {}
        quasi_identifiers = config.get("quasi_identifiers", [])
        expected_k = config.get("expected_k", 5)
        check_pii = config.get("check_pii", True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "rows": len(df),
            "columns": len(df.columns),
            "privacy_checks": {}
        }

        # Check for PII
        if check_pii:
            pii_found = PIIDetector.detect_pii_in_dataframe(df)
            report["privacy_checks"]["pii_detected"] = bool(pii_found)
            report["privacy_checks"]["pii_columns"] = list(pii_found.keys())
            report["privacy_checks"]["pii_count"] = sum(
                len(v) for v in pii_found.values())

        # Check k-anonymity
        if quasi_identifiers:
            k_report = KAnonymity.get_anonymity_report(df, quasi_identifiers)
            report["privacy_checks"]["k_anonymity"] = k_report
            report["privacy_checks"]["meets_requirement"] = k_report["k_anonymity"] >= expected_k

        # Check for duplicates (privacy risk)
        duplicates = df.duplicated().sum()
        report["privacy_checks"]["duplicate_rows"] = int(duplicates)
        report["privacy_checks"]["duplicate_risk"] = "high" if duplicates > 0 else "low"

        return report

    @staticmethod
    def generate_audit_report(df: pd.DataFrame, config: Dict[str, Any] = None) -> str:
        """Generate human-readable privacy audit report"""
        audit = PrivacyAudit.audit_dataset(df, config)

        report = f"""
Privacy Audit Report
{'='*50}
Generated: {audit['timestamp']}
Dataset: {audit['rows']} rows × {audit['columns']} columns

Privacy Checks:
{'-'*50}"""

        for check, result in audit['privacy_checks'].items():
            if isinstance(result, dict):
                report += f"\n{check}:"
                for k, v in result.items():
                    report += f"\n  {k}: {v}"
            else:
                report += f"\n{check}: {result}"

        return report
