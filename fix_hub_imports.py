#!/usr/bin/env python3
"""
Fix the privacy_security_hub.py imports to be optional
"""

# Read the file
with open('dashboard/privacy_security_hub.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the problematic imports section
old_imports = """# Import security modules
try:
    from privacy.anonymization import detect_pii, anonymize_data
    from security.encryption_validator import EncryptionValidator
    from security.model_integrity import ModelIntegrityChecker
    from security.adversarial_tests import AdversarialTester
    from compliance.gdpr_rights import GDPRRightsManager
    from security.l2_evaluator import L2Evaluator
    from security.mfa_manager import MFAManager
    from data.retention_manager import DataRetentionManager
    MODULES_AVAILABLE = True
except:
    MODULES_AVAILABLE = False"""

new_imports = """# Import security modules - gracefully handle missing imports
MODULES_AVAILABLE = True
try:
    try:
        from privacy.anonymization import detect_pii, anonymize_data
    except ImportError:
        detect_pii = None
        anonymize_data = None
    
    try:
        from security.encryption_validator import EncryptionValidator
    except ImportError:
        EncryptionValidator = None
    
    try:
        from security.model_integrity import ModelIntegrityChecker
    except ImportError:
        ModelIntegrityChecker = None
    
    try:
        from security.adversarial_tests import AdversarialTester
    except ImportError:
        AdversarialTester = None
    
    try:
        from compliance.gdpr_rights import GDPRRightsManager
    except ImportError:
        GDPRRightsManager = None
    
    try:
        from security.l2_evaluator import L2Evaluator
    except ImportError:
        L2Evaluator = None
    
    try:
        from security.mfa_manager import MFAManager
    except ImportError:
        MFAManager = None
    
    try:
        from data.retention_manager import DataRetentionManager
    except ImportError:
        DataRetentionManager = None
except Exception:
    MODULES_AVAILABLE = False"""

if old_imports in content:
    content = content.replace(old_imports, new_imports)
    with open('dashboard/privacy_security_hub.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed imports in privacy_security_hub.py")
else:
    print("⚠️  Could not find exact import section to replace")
    print("Looking for imports...")
    if "# Import security modules" in content:
        print("Found '# Import security modules' - checking structure...")
