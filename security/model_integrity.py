"""
Model Integrity & Tamper Detection Module
Verifies model file integrity using checksums
Detects unauthorized model modifications
Maintains model versioning and provenance
"""

import hashlib
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelChecksum:
    """Represents a model file checksum"""
    file_path: str
    checksum_sha256: str
    file_size: int
    timestamp: str
    algorithm: str = "sha256"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelVersion:
    """Represents a model version"""
    version_id: str
    model_path: str
    checksum: str
    timestamp: str
    author: str
    description: str
    parent_version: Optional[str] = None
    integrity_verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModelIntegrityValidator:
    """Validates model file integrity"""

    CHECKSUM_FILE_SUFFIX = ".sha256"
    METADATA_FILE_SUFFIX = ".metadata.json"

    @staticmethod
    def calculate_file_checksum(file_path: str, algorithm: str = "sha256") -> str:
        """
        Calculate checksum for file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('sha256', 'sha512', 'md5')

        Returns:
            Hex-encoded checksum
        """
        if algorithm == "sha256":
            hash_obj = hashlib.sha256()
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512()
        elif algorithm == "md5":
            hash_obj = hashlib.md5()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    @staticmethod
    def generate_model_checksum(model_path: str) -> ModelChecksum:
        """
        Generate checksum for model file.

        Args:
            model_path: Path to model file

        Returns:
            ModelChecksum object
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        checksum = ModelIntegrityValidator.calculate_file_checksum(model_path)
        file_size = os.path.getsize(model_path)

        return ModelChecksum(
            file_path=str(model_path),
            checksum_sha256=checksum,
            file_size=file_size,
            timestamp=datetime.now().isoformat()
        )

    @staticmethod
    def save_checksum(model_path: str, checksum: ModelChecksum) -> str:
        """
        Save checksum to file.

        Args:
            model_path: Path to model file
            checksum: ModelChecksum object

        Returns:
            Path to checksum file
        """
        checksum_path = model_path + ModelIntegrityValidator.CHECKSUM_FILE_SUFFIX

        with open(checksum_path, "w") as f:
            json.dump(checksum.to_dict(), f, indent=2)

        logger.info(f"Checksum saved: {checksum_path}")
        return checksum_path

    @staticmethod
    def load_checksum(model_path: str) -> Optional[ModelChecksum]:
        """
        Load checksum from file.

        Args:
            model_path: Path to model file

        Returns:
            ModelChecksum or None if not found
        """
        checksum_path = model_path + ModelIntegrityValidator.CHECKSUM_FILE_SUFFIX

        if not os.path.exists(checksum_path):
            return None

        try:
            with open(checksum_path, "r") as f:
                data = json.load(f)
                return ModelChecksum(**data)
        except Exception as e:
            logger.error(f"Error loading checksum: {e}")
            return None

    @staticmethod
    def verify_model_integrity(model_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify model integrity by comparing checksums.

        Args:
            model_path: Path to model file

        Returns:
            Tuple of (is_valid, details)
        """
        stored_checksum = ModelIntegrityValidator.load_checksum(model_path)

        if stored_checksum is None:
            return False, {
                "status": "error",
                "message": "No checksum file found",
                "model": model_path
            }

        current_checksum = ModelIntegrityValidator.generate_model_checksum(model_path)

        if stored_checksum.checksum_sha256 == current_checksum.checksum_sha256:
            return True, {
                "status": "valid",
                "message": "Model integrity verified",
                "model": model_path,
                "checksum": current_checksum.checksum_sha256,
                "stored_timestamp": stored_checksum.timestamp,
                "verify_timestamp": datetime.now().isoformat()
            }
        else:
            return False, {
                "status": "invalid",
                "message": "Model has been modified (checksum mismatch)",
                "model": model_path,
                "expected_checksum": stored_checksum.checksum_sha256,
                "actual_checksum": current_checksum.checksum_sha256,
                "stored_size": stored_checksum.file_size,
                "actual_size": current_checksum.file_size,
                "warning": "⚠️ POTENTIAL TAMPERING DETECTED"
            }

    @staticmethod
    def create_model_with_integrity(model_path: str, author: str = "system",
                                   description: str = "") -> Tuple[bool, str]:
        """
        Create model with integrity protection.

        Args:
            model_path: Path to model file
            author: Author/creator of model
            description: Model description

        Returns:
            Tuple of (success, message)
        """
        try:
            checksum = ModelIntegrityValidator.generate_model_checksum(model_path)
            checksum_file = ModelIntegrityValidator.save_checksum(model_path, checksum)

            # Create metadata file
            metadata = {
                "model_path": model_path,
                "checksum": checksum.checksum_sha256,
                "file_size": checksum.file_size,
                "timestamp": checksum.timestamp,
                "author": author,
                "description": description,
                "integrity_verified": True
            }

            metadata_path = model_path + ModelIntegrityValidator.METADATA_FILE_SUFFIX
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Model protected: {model_path}")
            return True, f"Model integrity protection created: {checksum_file}"

        except Exception as e:
            logger.error(f"Error creating model integrity: {e}")
            return False, f"Error: {str(e)}"


class ModelVersioning:
    """Manages model versions and provenance"""

    def __init__(self, version_registry_path: str = "data/model_versions.json"):
        self.registry_path = Path(version_registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.versions = self._load_registry()

    def _load_registry(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load model version registry"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading registry: {e}")
                return {}
        return {}

    def _save_registry(self):
        """Save model version registry"""
        try:
            with open(self.registry_path, "w") as f:
                json.dump(self.versions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def register_model_version(self, model_name: str, model_path: str,
                              author: str, description: str,
                              parent_version: Optional[str] = None) -> str:
        """
        Register a new model version.

        Args:
            model_name: Name/identifier for model
            model_path: Path to model file
            author: Author of this version
            description: Version description
            parent_version: ID of parent version (for lineage)

        Returns:
            Version ID
        """
        # Calculate checksum
        checksum = ModelIntegrityValidator.calculate_file_checksum(model_path)

        # Generate version ID
        version_id = f"{model_name}_v{len(self.versions.get(model_name, [])) + 1}"

        # Create version entry
        version = ModelVersion(
            version_id=version_id,
            model_path=str(model_path),
            checksum=checksum,
            timestamp=datetime.now().isoformat(),
            author=author,
            description=description,
            parent_version=parent_version,
            integrity_verified=True
        )

        # Store in registry
        if model_name not in self.versions:
            self.versions[model_name] = []

        self.versions[model_name].append(version.to_dict())
        self._save_registry()

        logger.info(f"Model version registered: {version_id}")
        return version_id

    def get_model_history(self, model_name: str) -> List[Dict[str, Any]]:
        """Get version history for model"""
        return self.versions.get(model_name, [])

    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get specific version details"""
        for model_versions in self.versions.values():
            for version in model_versions:
                if version["version_id"] == version_id:
                    return version
        return None

    def verify_version_integrity(self, version_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Verify integrity of specific version"""
        version = self.get_version(version_id)

        if version is None:
            return False, {"error": "Version not found"}

        model_path = version["model_path"]
        is_valid, details = ModelIntegrityValidator.verify_model_integrity(model_path)

        return is_valid, {
            **details,
            "version_id": version_id,
            "registered_checksum": version["checksum"],
            "file_checksum": version["checksum"]
        }

    def generate_provenance_report(self, model_name: str) -> str:
        """Generate model provenance report"""
        history = self.get_model_history(model_name)

        report = f"""
Model Provenance Report
{'='*60}
Model: {model_name}
Total Versions: {len(history)}

Version History:
{'-'*60}
"""

        for version in history:
            report += f"""
Version ID: {version['version_id']}
  Author: {version['author']}
  Created: {version['timestamp']}
  Description: {version['description']}
  Parent: {version.get('parent_version', 'None')}
  Checksum: {version['checksum'][:16]}...
  Integrity: {'✓ Verified' if version.get('integrity_verified') else '✗ Not Verified'}
"""

        return report

    def get_model_lineage(self, version_id: str) -> List[str]:
        """Get full lineage/ancestry of a model version"""
        lineage = [version_id]
        version = self.get_version(version_id)

        while version and version.get("parent_version"):
            parent_id = version["parent_version"]
            lineage.append(parent_id)
            version = self.get_version(parent_id)

        return lineage


class TamperDetection:
    """Detects and logs model tampering attempts"""

    def __init__(self, log_path: str = "data/tamper_attempts.json"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.attempts = self._load_log()

    def _load_log(self) -> List[Dict[str, Any]]:
        """Load tamper attempt log"""
        if self.log_path.exists():
            try:
                with open(self.log_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tamper log: {e}")
                return []
        return []

    def _save_log(self):
        """Save tamper attempt log"""
        try:
            with open(self.log_path, "w") as f:
                json.dump(self.attempts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tamper log: {e}")

    def log_tamper_attempt(self, model_path: str, expected_checksum: str,
                          actual_checksum: str, severity: str = "critical"):
        """
        Log a detected tampering attempt.

        Args:
            model_path: Path to tampered model
            expected_checksum: Expected checksum
            actual_checksum: Actual checksum
            severity: 'critical', 'high', 'medium'
        """
        attempt = {
            "timestamp": datetime.now().isoformat(),
            "model_path": model_path,
            "expected_checksum": expected_checksum,
            "actual_checksum": actual_checksum,
            "severity": severity,
            "detected": True
        }

        self.attempts.append(attempt)
        self._save_log()

        logger.warning(f"TAMPER ATTEMPT DETECTED: {model_path}")
        logger.warning(f"  Expected: {expected_checksum}")
        logger.warning(f"  Actual: {actual_checksum}")

    def get_tamper_attempts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get tamper attempts from last N hours"""
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            attempt for attempt in self.attempts
            if datetime.fromisoformat(attempt["timestamp"]) > cutoff_time
        ]

    def get_tamper_report(self) -> str:
        """Generate tamper detection report"""
        report = f"""
Model Tampering Detection Report
{'='*60}
Generated: {datetime.now().isoformat()}

Total Attempts Detected: {len(self.attempts)}

Recent Attempts (Last 24 Hours):
{'-'*60}
"""

        recent = self.get_tamper_attempts(hours=24)
        if recent:
            for attempt in recent:
                report += f"""
  Model: {attempt['model_path']}
  Time: {attempt['timestamp']}
  Severity: {attempt['severity']}
  Expected Hash: {attempt['expected_checksum'][:16]}...
  Actual Hash: {attempt['actual_checksum'][:16]}...
"""
        else:
            report += "No tampering attempts detected in last 24 hours.\n"

        if len(self.attempts) > len(recent):
            report += f"""

Older Attempts: {len(self.attempts) - len(recent)} detected
"""

        return report
