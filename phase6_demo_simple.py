"""
PHASE 6 DEMONSTRATION - SIMPLE VERSION

This script demonstrates Phase 6 functionality with sample data.
"""

from monitoring.notification_manager import NotificationManager
from monitoring.change_detector import ChangeDetector
import sys
from datetime import datetime
from pathlib import Path

# Add project to path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))


def main():
    """Run Phase 6 demo"""
    print("\n" + "="*80)
    print("PHASE 6: INTEGRATED CHANGE MONITORING SYSTEM - DEMO")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # 1. CHANGE DETECTION
        print("[1] CHANGE DETECTION\n")
        detector = ChangeDetector()

        previous = {
            "GDPR-1": "Organizations must implement data protection",
            "GDPR-2": "Data subjects have right to erasure"
        }

        current = {
            "GDPR-1": "Organizations must implement advanced data protection",
            "GDPR-2": "Data subjects have right to erasure",
            "GDPR-4": "Mandatory Data Protection Impact Assessment",
            "GDPR-5": "Annual compliance audits required"
        }

        result = detector.analyze_changes("GDPR", previous, current)

        print(f"Total Changes: {result.total_changes}")
        print(f"  Critical: {result.critical_changes}")
        print(f"  High: {result.high_changes}")
        print(f"  Medium: {result.medium_changes}")
        print(f"  Low: {result.low_changes}\n")

        for change in result.changes:
            print(f"  - {change.change_type.value}: {change.requirement_id}")
            print(f"    Severity: {change.severity.value}")
            print(f"    Hours: {change.estimated_remediation_hours}")
            print()

        # 2. NOTIFICATIONS
        print("[2] NOTIFICATIONS\n")
        manager = NotificationManager()

        notifications = manager.create_change_notification(
            change_id="CHG-001",
            change_type="NEW_REQUIREMENT",
            severity="CRITICAL",
            regulation="GDPR",
            requirement_id="GDPR-4",
            affected_systems=["Data Storage"],
            description="Mandatory DPIA",
            recipients=["compliance@company.com"]
        )

        print(f"Notifications Created: {len(notifications)}")
        for n in notifications:
            print(f"  - {n.channel.value}: {n.priority.value}")
        print()

        results = manager.send_notifications(notifications)
        print(f"Send Results:")
        print(f"  Sent: {results['sent']}")
        print(f"  Delivered: {results['delivered']}")
        print(f"  Failed: {results['failed']}\n")

        print("="*80)
        print("STATUS: PHASE 6 COMPLETE AND WORKING")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
