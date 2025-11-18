"""
GDPR Data Subject Rights Module
Implements Right to Erasure (Right to be Forgotten)
Implements Right to Access (Data Portability)
Implements Right to Withdraw Consent
"""

import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataSubjectRequest:
    """Represents a GDPR data subject request"""
    request_id: str
    user_id: str
    request_type: str  # "access", "erasure", "withdraw_consent"
    status: str  # "pending", "processing", "completed", "denied"
    timestamp: str
    completion_timestamp: Optional[str] = None
    reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserData:
    """Represents user personal data"""
    user_id: str
    data_categories: Dict[str, Any]  # All user data organized by category
    consent_status: Dict[str, bool]  # Tracking consent for each data use
    created_at: str
    last_modified: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GDPRRightsManager:
    """Manages GDPR data subject rights"""

    def __init__(self, data_dir: str = "data/gdpr", request_log_path: str = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.request_log_path = Path(
            request_log_path or f"{data_dir}/requests.json")
        self.requests = self._load_requests()

        # User data directory
        self.user_data_dir = self.data_dir / "user_data"
        self.user_data_dir.mkdir(exist_ok=True)

        # Erasure log (audit trail)
        self.erasure_log_path = self.data_dir / "erasures.json"
        self.erasures = self._load_erasures()

    def _load_requests(self) -> List[Dict[str, Any]]:
        """Load request log"""
        if self.request_log_path.exists():
            try:
                with open(self.request_log_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading requests: {e}")
                return []
        return []

    def _save_requests(self):
        """Save request log"""
        try:
            with open(self.request_log_path, "w") as f:
                json.dump(self.requests, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving requests: {e}")

    def _load_erasures(self) -> List[Dict[str, Any]]:
        """Load erasure audit log"""
        if self.erasure_log_path.exists():
            try:
                with open(self.erasure_log_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading erasures: {e}")
                return []
        return []

    def _save_erasures(self):
        """Save erasure audit log"""
        try:
            with open(self.erasure_log_path, "w") as f:
                json.dump(self.erasures, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving erasures: {e}")

    def get_user_data_file(self, user_id: str) -> Path:
        """Get path to user data file"""
        return self.user_data_dir / f"{user_id}.json"

    def store_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Store user personal data.

        Args:
            user_id: User identifier
            data: User data to store

        Returns:
            Success status
        """
        try:
            user_data = UserData(
                user_id=user_id,
                data_categories=data,
                consent_status={},
                created_at=datetime.now().isoformat(),
                last_modified=datetime.now().isoformat()
            )

            data_file = self.get_user_data_file(user_id)
            with open(data_file, "w") as f:
                json.dump(user_data.to_dict(), f, indent=2)

            logger.info(f"User data stored: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing user data: {e}")
            return False

    def get_user_data(self, user_id: str) -> Optional[UserData]:
        """
        Retrieve user personal data.

        Args:
            user_id: User identifier

        Returns:
            UserData or None
        """
        try:
            data_file = self.get_user_data_file(user_id)

            if not data_file.exists():
                logger.warning(f"No data found for user: {user_id}")
                return None

            with open(data_file, "r") as f:
                data = json.load(f)

            return UserData(**data)

        except Exception as e:
            logger.error(f"Error retrieving user data: {e}")
            return None

    def right_to_access(self, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Implement Right to Access (GDPR Article 15).

        User can request all their personal data in portable format.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (success, user_data)
        """
        logger.info(f"Right to Access request: {user_id}")

        request_id = f"ACCESS_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="access",
            status="processing",
            timestamp=datetime.now().isoformat()
        )

        self.requests.append(request.to_dict())
        self._save_requests()

        # Retrieve all user data
        user_data = self.get_user_data(user_id)

        if user_data is None:
            request["status"] = "completed"
            request["notes"] = "No data found for user"
            self._save_requests()
            return False, None

        # Mark as completed
        request["status"] = "completed"
        request["completion_timestamp"] = datetime.now().isoformat()
        self._save_requests()

        logger.info(f"Right to Access completed: {request_id}")

        return True, user_data.to_dict()

    def right_to_erasure(self, user_id: str, reason: str = "") -> Tuple[bool, str]:
        """
        Implement Right to Erasure (GDPR Article 17 - Right to be Forgotten).

        User can request deletion of all personal data.

        Args:
            user_id: User identifier
            reason: Reason for erasure request

        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Right to Erasure request: {user_id} (reason: {reason})")

        request_id = f"ERASE_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="erasure",
            status="processing",
            timestamp=datetime.now().isoformat(),
            reason=reason
        )

        self.requests.append(request.to_dict())
        self._save_requests()

        try:
            # Step 1: Delete from primary storage
            data_file = self.get_user_data_file(user_id)
            if data_file.exists():
                os.remove(data_file)
                logger.info(f"User data file deleted: {data_file}")

            # Step 2: Log the erasure (for audit)
            erasure_record = {
                "request_id": request_id,
                "user_id": user_id,
                "erasure_timestamp": datetime.now().isoformat(),
                "reason": reason,
                "status": "completed"
            }

            self.erasures.append(erasure_record)
            self._save_erasures()

            # Step 3: Update request status
            for req in self.requests:
                if req["request_id"] == request_id:
                    req["status"] = "completed"
                    req["completion_timestamp"] = datetime.now().isoformat()
                    req["notes"] = "All user data successfully deleted"

            self._save_requests()

            logger.info(f"Right to Erasure completed: {request_id}")
            return True, f"User data for {user_id} has been permanently deleted"

        except Exception as e:
            logger.error(f"Error during erasure: {e}")

            # Update request to failed
            for req in self.requests:
                if req["request_id"] == request_id:
                    req["status"] = "denied"
                    req["notes"] = f"Deletion failed: {str(e)}"

            self._save_requests()

            return False, f"Erasure failed: {str(e)}"

    def right_to_rectification(self, user_id: str, updated_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Implement Right to Rectification (GDPR Article 16).

        User can request correction of inaccurate personal data.

        Args:
            user_id: User identifier
            updated_data: Corrected data

        Returns:
            Tuple of (success, message)
        """
        try:
            user_data = self.get_user_data(user_id)

            if user_data is None:
                return False, f"No data found for user {user_id}"

            # Update data
            user_data.data_categories.update(updated_data)
            user_data.last_modified = datetime.now().isoformat()

            # Save updated data
            data_file = self.get_user_data_file(user_id)
            with open(data_file, "w") as f:
                json.dump(user_data.to_dict(), f, indent=2)

            logger.info(f"User data rectified: {user_id}")
            return True, "User data has been updated"

        except Exception as e:
            logger.error(f"Error during rectification: {e}")
            return False, f"Rectification failed: {str(e)}"

    def withdraw_consent(self, user_id: str, data_category: str = "all") -> Tuple[bool, str]:
        """
        Implement Right to Withdraw Consent (GDPR Article 7).

        User can revoke consent for data processing.

        Args:
            user_id: User identifier
            data_category: Category of data (or "all" for everything)

        Returns:
            Tuple of (success, message)
        """
        request_id = f"CONSENT_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="withdraw_consent",
            status="processing",
            timestamp=datetime.now().isoformat(),
            reason=f"Consent withdrawn for: {data_category}"
        )

        self.requests.append(request.to_dict())

        try:
            user_data = self.get_user_data(user_id)

            if user_data is None:
                return False, f"No data found for user {user_id}"

            # Update consent status
            if data_category == "all":
                user_data.consent_status = {
                    k: False for k in user_data.consent_status}
            else:
                user_data.consent_status[data_category] = False

            user_data.last_modified = datetime.now().isoformat()

            # Save updated data
            data_file = self.get_user_data_file(user_id)
            with open(data_file, "w") as f:
                json.dump(user_data.to_dict(), f, indent=2)

            # Update request status
            for req in self.requests:
                if req["request_id"] == request_id:
                    req["status"] = "completed"
                    req["completion_timestamp"] = datetime.now().isoformat()

            self._save_requests()

            logger.info(f"Consent withdrawn for {user_id}: {data_category}")
            return True, f"Consent withdrawn for {data_category}"

        except Exception as e:
            logger.error(f"Error withdrawing consent: {e}")
            return False, f"Error: {str(e)}"

    def data_portability_export(self, user_id: str, format: str = "json") -> Tuple[bool, Optional[str]]:
        """
        Implement Right to Data Portability (GDPR Article 20).

        User can export data in machine-readable format.

        Args:
            user_id: User identifier
            format: Export format ('json', 'csv')

        Returns:
            Tuple of (success, file_path)
        """
        try:
            user_data = self.get_user_data(user_id)

            if user_data is None:
                return False, None

            export_dir = self.data_dir / "exports"
            export_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = export_dir / f"{user_id}_export_{timestamp}.{format}"

            if format == "json":
                with open(export_file, "w") as f:
                    json.dump(user_data.to_dict(), f, indent=2)

            elif format == "csv":
                import csv
                with open(export_file, "w", newline='') as f:
                    writer = csv.writer(f)
                    # Write headers
                    writer.writerow(["Category", "Value"])
                    # Write data
                    for category, value in user_data.data_categories.items():
                        writer.writerow([category, str(value)])

            logger.info(f"Data exported for {user_id}: {export_file}")
            return True, str(export_file)

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False, None

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of data subject request"""
        for req in self.requests:
            if req["request_id"] == request_id:
                return req
        return None

    def get_user_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all requests for a user"""
        return [req for req in self.requests if req["user_id"] == user_id]

    def generate_compliance_report(self) -> str:
        """Generate GDPR compliance report"""
        report = f"""
GDPR Data Subject Rights Compliance Report
{'='*60}
Generated: {datetime.now().isoformat()}

Summary:
{'-'*60}
Total Requests: {len(self.requests)}
Total Erasures: {len(self.erasures)}

Request Types:
"""

        access_count = sum(
            1 for r in self.requests if r["request_type"] == "access")
        erasure_count = sum(
            1 for r in self.requests if r["request_type"] == "erasure")
        consent_count = sum(
            1 for r in self.requests if r["request_type"] == "withdraw_consent")

        report += f"""
  - Right to Access: {access_count}
  - Right to Erasure: {erasure_count}
  - Withdraw Consent: {consent_count}

Request Status:
"""

        pending = sum(1 for r in self.requests if r["status"] == "pending")
        processing = sum(
            1 for r in self.requests if r["status"] == "processing")
        completed = sum(1 for r in self.requests if r["status"] == "completed")

        report += f"""
  - Pending: {pending}
  - Processing: {processing}
  - Completed: {completed}

Recommendations:
{'-'*60}
✓ Ensure all requests are handled within 30 days (GDPR requirement)
✓ Maintain audit trail of all deletions (data subjects' right to know)
✓ Document legal basis for any denied requests
✓ Implement automated deletion where possible
"""

        return report
