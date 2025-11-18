"""
Data Retention & Automated Deletion Manager
Implements scheduled data retention policies
Ensures compliance with data minimization principles
"""

import os
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
import sqlite3

logger = logging.getLogger(__name__)


@dataclass
class RetentionPolicy:
    """Data retention policy configuration"""
    name: str
    data_type: str  # "user_data", "logs", "temp", "audit", "backups"
    retention_days: int  # 0 = permanent
    archive_after_days: int = 0  # 0 = no archive
    purge_on_deletion: bool = True  # Automatically delete when account deleted
    description: str = ""
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def should_retain(self, created_date: datetime) -> bool:
        """Check if data should still be retained"""
        if self.retention_days == 0:
            return True
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        return created_date > cutoff_date

    def should_archive(self, created_date: datetime) -> bool:
        """Check if data should be archived"""
        if self.archive_after_days == 0:
            return False
        cutoff_date = datetime.now() - timedelta(days=self.archive_after_days)
        return created_date < cutoff_date


@dataclass
class DeletionRecord:
    """Record of data deletion"""
    deletion_id: str
    data_type: str
    record_count: int
    deletion_timestamp: str
    deletion_reason: str  # "retention_expired", "user_requested", "policy_enforced"
    details: str = ""
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RetentionPolicyManager:
    """Manages data retention policies"""

    # Default retention policies
    DEFAULT_POLICIES = [
        RetentionPolicy(
            name="User Account Data",
            data_type="user_data",
            retention_days=0,  # Permanent until deletion request
            purge_on_deletion=True,
            description="Core user account information"
        ),
        RetentionPolicy(
            name="Activity Logs",
            data_type="logs",
            retention_days=90,  # 3 months
            archive_after_days=30,
            purge_on_deletion=True,
            description="User activity and system logs"
        ),
        RetentionPolicy(
            name="Audit Logs",
            data_type="audit",
            retention_days=365,  # 1 year (regulatory requirement)
            archive_after_days=180,
            purge_on_deletion=False,  # Keep for compliance
            description="Security and compliance audit trails"
        ),
        RetentionPolicy(
            name="Temporary Data",
            data_type="temp",
            retention_days=7,  # 1 week
            archive_after_days=0,
            purge_on_deletion=True,
            description="Temporary files and cache"
        ),
        RetentionPolicy(
            name="Database Backups",
            data_type="backups",
            retention_days=30,  # 1 month
            archive_after_days=14,
            purge_on_deletion=True,
            description="Automatic database backups"
        ),
    ]

    def __init__(self, policies_file: str = "data/retention_policies.json"):
        self.policies_file = policies_file
        os.makedirs(os.path.dirname(policies_file), exist_ok=True)
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, RetentionPolicy]:
        """Load retention policies from file"""
        if os.path.exists(self.policies_file):
            try:
                with open(self.policies_file, "r") as f:
                    data = json.load(f)
                    return {
                        name: RetentionPolicy(**policy)
                        for name, policy in data.items()
                    }
            except Exception as e:
                logger.error(f"Error loading policies: {e}")
                return {}

        # If no file, initialize with defaults
        policies = {p.name: p for p in self.DEFAULT_POLICIES}
        self._save_policies(policies)
        return policies

    def _save_policies(self, policies: Dict[str, RetentionPolicy]):
        """Save retention policies to file"""
        try:
            data = {name: policy.to_dict()
                    for name, policy in policies.items()}
            with open(self.policies_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving policies: {e}")

    def get_policy(self, data_type: str) -> Optional[RetentionPolicy]:
        """Get policy for data type"""
        for policy in self.policies.values():
            if policy.data_type == data_type:
                return policy
        return None

    def add_policy(self, policy: RetentionPolicy) -> bool:
        """Add or update a retention policy"""
        try:
            policy.created_at = datetime.now().isoformat()
            self.policies[policy.name] = policy
            self._save_policies(self.policies)
            logger.info(f"Policy added: {policy.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding policy: {e}")
            return False

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a retention policy"""
        try:
            if policy_name in self.policies:
                del self.policies[policy_name]
                self._save_policies(self.policies)
                logger.info(f"Policy removed: {policy_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing policy: {e}")
            return False


class DataRetentionManager:
    """Manages data retention and automated deletion"""

    def __init__(self, data_dir: str = "data", database_path: str = None,
                 deletion_log_path: str = None):
        self.data_dir = data_dir
        self.database_path = database_path or f"{data_dir}/iraqaf_compliance.db"
        self.deletion_log_path = deletion_log_path or f"{data_dir}/deletion_log.json"

        os.makedirs(data_dir, exist_ok=True)

        self.policy_manager = RetentionPolicyManager(
            f"{data_dir}/retention_policies.json")
        self.deletion_log = self._load_deletion_log()

    def _load_deletion_log(self) -> List[Dict[str, Any]]:
        """Load deletion audit log"""
        if os.path.exists(self.deletion_log_path):
            try:
                with open(self.deletion_log_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading deletion log: {e}")
                return []
        return []

    def _save_deletion_log(self):
        """Save deletion audit log"""
        try:
            with open(self.deletion_log_path, "w") as f:
                json.dump(self.deletion_log, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving deletion log: {e}")

    def _log_deletion(self, record: DeletionRecord):
        """Log data deletion"""
        self.deletion_log.append(record.to_dict())
        self._save_deletion_log()

    def purge_expired_logs(self) -> Tuple[int, str]:
        """
        Purge logs based on retention policy.

        Returns:
            Tuple of (records_deleted, message)
        """
        try:
            policy = self.policy_manager.get_policy("logs")
            if not policy:
                return 0, "No retention policy for logs"

            if not os.path.exists(self.database_path):
                return 0, "Database not found"

            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=policy.retention_days)

            # Delete logs older than policy
            cursor.execute("""
                DELETE FROM activity_logs
                WHERE created_at < ?
            """, (cutoff_date.isoformat(),))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            # Log deletion
            deletion_record = DeletionRecord(
                deletion_id=f"DEL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                data_type="logs",
                record_count=deleted_count,
                deletion_timestamp=datetime.now().isoformat(),
                deletion_reason="retention_expired",
                details=f"Deleted logs older than {cutoff_date.date()}"
            )
            self._log_deletion(deletion_record)

            logger.info(f"Purged {deleted_count} expired logs")
            return deleted_count, f"Deleted {deleted_count} expired log records"

        except Exception as e:
            logger.error(f"Error purging logs: {e}")
            return 0, f"Error: {str(e)}"

    def purge_temporary_data(self) -> Tuple[int, str]:
        """
        Purge temporary data based on retention policy.

        Returns:
            Tuple of (files_deleted, message)
        """
        try:
            policy = self.policy_manager.get_policy("temp")
            if not policy:
                return 0, "No retention policy for temp data"

            temp_dir = f"{self.data_dir}/temp"
            if not os.path.exists(temp_dir):
                return 0, "Temp directory not found"

            cutoff_time = datetime.now() - timedelta(days=policy.retention_days)

            deleted_count = 0
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)

                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(
                        os.path.getmtime(filepath))

                    if file_mtime < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1

            # Log deletion
            if deleted_count > 0:
                deletion_record = DeletionRecord(
                    deletion_id=f"DEL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    data_type="temp",
                    record_count=deleted_count,
                    deletion_timestamp=datetime.now().isoformat(),
                    deletion_reason="retention_expired",
                    details=f"Deleted temp files older than {cutoff_time.date()}"
                )
                self._log_deletion(deletion_record)

            logger.info(f"Purged {deleted_count} temporary files")
            return deleted_count, f"Deleted {deleted_count} temporary files"

        except Exception as e:
            logger.error(f"Error purging temporary data: {e}")
            return 0, f"Error: {str(e)}"

    def archive_old_data(self, data_type: str) -> Tuple[int, str]:
        """
        Archive data based on retention policy.

        Returns:
            Tuple of (records_archived, message)
        """
        try:
            policy = self.policy_manager.get_policy(data_type)
            if not policy or policy.archive_after_days == 0:
                return 0, "No archival policy configured"

            if not os.path.exists(self.database_path):
                return 0, "Database not found"

            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=policy.archive_after_days)

            # Archive logs (move to archive table)
            cursor.execute("""
                INSERT INTO activity_logs_archive
                SELECT * FROM activity_logs
                WHERE created_at < ? AND status != 'archived'
            """, (cutoff_date.isoformat(),))

            archived_count = cursor.rowcount

            # Mark as archived
            if archived_count > 0:
                cursor.execute("""
                    UPDATE activity_logs
                    SET status = 'archived'
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))

            conn.commit()
            conn.close()

            logger.info(f"Archived {archived_count} {data_type} records")
            return archived_count, f"Archived {archived_count} records"

        except Exception as e:
            logger.error(f"Error archiving data: {e}")
            return 0, f"Error: {str(e)}"

    def delete_user_data(self, user_id: str, reason: str = "user_requested") -> Tuple[bool, str]:
        """
        Delete all data for a user.

        Args:
            user_id: User identifier
            reason: Reason for deletion

        Returns:
            Tuple of (success, message)
        """
        try:
            if not os.path.exists(self.database_path):
                return False, "Database not found"

            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # Get count of records to delete
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))
            user_exists = cursor.fetchone()[0] > 0

            if not user_exists:
                return False, f"User {user_id} not found"

            # Delete user records from all relevant tables
            tables_to_clean = ["activity_logs", "audit_logs", "gdpr_requests"]
            total_deleted = 0

            for table in tables_to_clean:
                try:
                    cursor.execute(
                        f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
                    total_deleted += cursor.rowcount
                except sqlite3.OperationalError:
                    # Table might not exist
                    pass

            # Finally delete user account
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            total_deleted += cursor.rowcount

            conn.commit()
            conn.close()

            # Log deletion
            deletion_record = DeletionRecord(
                deletion_id=f"DEL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                data_type="user_data",
                record_count=total_deleted,
                deletion_timestamp=datetime.now().isoformat(),
                deletion_reason=reason,
                user_id=user_id,
                details=f"Complete user data deletion for {user_id}"
            )
            self._log_deletion(deletion_record)

            logger.info(
                f"Deleted all data for user: {user_id} ({total_deleted} records)")
            return True, f"User data deleted ({total_deleted} records removed)"

        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False, f"Error: {str(e)}"

    def schedule_retention_job(self) -> Dict[str, Any]:
        """
        Execute scheduled retention jobs.

        Returns:
            Dictionary with job results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "jobs_executed": [],
            "total_records_deleted": 0,
            "errors": []
        }

        try:
            # Purge expired logs
            log_count, log_msg = self.purge_expired_logs()
            results["jobs_executed"].append({
                "job": "purge_logs",
                "records": log_count,
                "message": log_msg
            })
            results["total_records_deleted"] += log_count

        except Exception as e:
            results["errors"].append(f"Log purge failed: {str(e)}")

        try:
            # Purge temporary data
            temp_count, temp_msg = self.purge_temporary_data()
            results["jobs_executed"].append({
                "job": "purge_temp",
                "records": temp_count,
                "message": temp_msg
            })
            results["total_records_deleted"] += temp_count

        except Exception as e:
            results["errors"].append(f"Temp purge failed: {str(e)}")

        try:
            # Archive old data
            arch_count, arch_msg = self.archive_old_data("logs")
            results["jobs_executed"].append({
                "job": "archive_logs",
                "records": arch_count,
                "message": arch_msg
            })

        except Exception as e:
            results["errors"].append(f"Archive failed: {str(e)}")

        logger.info(
            f"Retention job completed: {results['total_records_deleted']} records processed")
        return results

    def generate_retention_report(self) -> str:
        """Generate data retention audit report"""
        report = f"""
Data Retention & Deletion Audit Report
{'='*70}
Generated: {datetime.now().isoformat()}

Retention Policies:
{'-'*70}
"""

        for policy in self.policy_manager.policies.values():
            report += f"""
  Name: {policy.name}
  Type: {policy.data_type}
  Retention Period: {policy.retention_days} days
  Archive After: {policy.archive_after_days} days
  Auto-purge on Deletion: {policy.purge_on_deletion}
  Description: {policy.description}
"""

        report += f"""
Deletion History:
{'-'*70}
Total Deletions: {len(self.deletion_log)}
"""

        if self.deletion_log:
            # Show recent deletions
            report += "\nRecent Deletions (Last 10):\n"
            for record in self.deletion_log[-10:]:
                report += f"""
  ID: {record.get('deletion_id')}
  Type: {record.get('data_type')}
  Records: {record.get('record_count')}
  Reason: {record.get('deletion_reason')}
  Time: {record.get('deletion_timestamp')}
"""

        report += f"""
Compliance Notes:
{'-'*70}
✓ Audit logs retained for {self.policy_manager.get_policy('audit').retention_days if self.policy_manager.get_policy('audit') else 'N/A'} days (regulatory requirement)
✓ User data retained until deletion request (GDPR compliance)
✓ Temporary data cleaned automatically after retention period
✓ All deletions logged for audit trail

Recommendations:
{'-'*70}
✓ Review and adjust retention policies quarterly
✓ Run retention jobs on a scheduled basis (daily/weekly)
✓ Monitor deletion logs for unexpected data loss
✓ Archive old data before permanent deletion
✓ Maintain backup copies of archived data
"""

        return report
