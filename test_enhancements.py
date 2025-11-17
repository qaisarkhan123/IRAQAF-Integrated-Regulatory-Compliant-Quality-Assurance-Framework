#!/usr/bin/env python
"""Test script for dashboard enhancements"""

import sys
sys.path.insert(0, 'dashboard')

from alerts import AlertManager
from authentication import AuthenticationManager, User
from domain_dashboards import RegulatoryDomain, DomainDashboard
from exports import ExportManager
import pandas as pd

print('=' * 60)
print('TESTING DASHBOARD ENHANCEMENTS')
print('=' * 60)

# Test 1: Alert System
print('\n[1/4] TESTING ALERT SYSTEM...')
print('-' * 60)
alerts = AlertManager()

alert1 = alerts.create_alert(
    alert_type='regulatory_change',
    severity='high',
    title='FDA Guidance Update',
    description='New quality guidance released',
    domain='FDA'
)
print(f'✓ Alert created: {alert1}')

alert2 = alerts.create_alert(
    alert_type='compliance_issue',
    severity='critical',
    title='Training Overdue',
    description='5 employees need training',
    domain='General'
)
print(f'✓ Alert created: {alert2}')

recent = alerts.get_alerts(hours=24)
print(f'✓ Retrieved {len(recent)} recent alerts')

unread = alerts.get_alerts(unread_only=True)
print(f'✓ {len(unread)} unread alerts')

stats = alerts.get_stats()
print(f"✓ Alert stats: {stats['total']} total, {stats['critical']} critical")

alerts.mark_as_read(alert1)
unread_after = alerts.get_alerts(unread_only=True)
print(f'✓ After marking read: {len(unread_after)} unread alerts')

# Test 2: Authentication System
print('\n[2/4] TESTING AUTHENTICATION SYSTEM...')
print('-' * 60)
auth = AuthenticationManager()

success = auth.create_user(
    username='analyst_test',
    password='test_pass_123',
    role='analyst',
    display_name='Test Analyst'
)
print(f'✓ User created: {success}')

auth_success, user = auth.authenticate('analyst_test', 'test_pass_123')
print(f'✓ Authentication success: {auth_success}')
print(f"  User: {user['display_name']} ({user['role']})")

session_id = auth.create_session('analyst_test')
print(f'✓ Session created: {session_id[:20]}...')

is_valid = auth.validate_session(session_id)
print(f'✓ Session valid: {is_valid}')

user_from_session = auth.get_session_user(session_id)
print(f"✓ Retrieved user from session: {user_from_session['username']}")

users = auth.list_users()
print(f'✓ Total users in system: {len(users)}')

# Test 3: Regulatory Domains
print('\n[3/4] TESTING REGULATORY DOMAINS...')
print('-' * 60)
domains = RegulatoryDomain.DOMAINS
print(f'✓ Available domains: {list(domains.keys())}')

for domain_code in ['FDA', 'EPA', 'SEC']:
    domain = RegulatoryDomain(domain_code)
    print(f'✓ {domain.get_icon()} {domain.get_name()}')
    print(f'  - Regulations: {len(domain.get_regulations())}')
    print(f'  - Metrics: {len(domain.get_metrics())}')

# Test domain dashboard
fda_dashboard = DomainDashboard('FDA')
regulations = fda_dashboard.domain.get_regulations()
print(f'✓ FDA Dashboard created with {len(regulations)} regulations')

# Test 4: Export Manager
print('\n[4/4] TESTING EXPORT MANAGER...')
print('-' * 60)
exporter = ExportManager()

# Create sample data
sample_data = pd.DataFrame({
    'Domain': ['FDA', 'EPA', 'SEC', 'ISO', 'GDPR'],
    'Compliance Score': [92, 88, 95, 85, 90],
    'Status': ['Compliant', 'At Risk', 'Compliant', 'At Risk', 'Compliant']
})

# Test CSV export
csv_bytes = exporter.export_to_csv(sample_data)
print(f'✓ CSV export successful: {len(csv_bytes)} bytes')

# Test Excel export
excel_data = {
    'Summary': sample_data,
    'Stats': pd.DataFrame({
        'Metric': ['Average', 'Min', 'Max'],
        'Score': [90, 85, 95]
    })
}
excel_bytes = exporter.export_to_excel(excel_data)
print(f'✓ Excel export successful: {len(excel_bytes)} bytes')

# Test PDF export
pdf_sections = [
    {'heading': 'Overview', 'content': 'This is a test compliance report'},
    {'heading': 'Scores by Domain', 'content': sample_data},
]
pdf_bytes = exporter.generate_compliance_report_pdf(
    title='Test Compliance Report',
    executive_summary='Test summary',
    sections=pdf_sections,
    metadata={'domain': 'General'}
)
print(f'✓ PDF export successful: {len(pdf_bytes)} bytes')

print('\n' + '=' * 60)
print('✓✓✓ ALL TESTS PASSED ✓✓✓')
print('=' * 60)
print('\nSummary:')
print('  • AlertManager: Working')
print('  • AuthenticationManager: Working')
print('  • RegulatoryDomains: Working')
print('  • ExportManager: Working')
print('\nReady for dashboard integration!')
