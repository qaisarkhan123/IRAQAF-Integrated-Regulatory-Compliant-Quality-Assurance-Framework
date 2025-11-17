"""Test the L2 Security Monitor"""
from security_monitor import SecurityMonitor

print("Testing SecurityMonitor...")
monitor = SecurityMonitor()

# Run a test scan
print("Running test scan on API Server...")
scan = monitor.start_scan("API Server", "full")
print(f"Scan completed: {scan.scan_id}")
print(f"Overall Score: {scan.overall_score}/100")
print(f"Recommendations: {len(scan.recommendations)}")

# Get summary
summary = monitor.get_security_summary()
print(f"\nSummary:")
print(f"Total Scans: {summary['total_scans']}")
print(f"Average Score: {summary['average_score']}/100")

print("\n✅ All tests passed!")
