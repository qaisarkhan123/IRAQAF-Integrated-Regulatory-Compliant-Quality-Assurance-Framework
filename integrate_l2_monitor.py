#!/usr/bin/env python3
"""
Integration Script: Add L2 Privacy/Security Monitor content to app.py
This script integrates the L2 monitor functions into app.py as a new page
while keeping l2_privacy_security_monitor.py as a backup
"""

import os
from pathlib import Path

# Paths
dashboard_dir = Path("dashboard")
app_py = dashboard_dir / "app.py"
l2_integration = dashboard_dir / "l2_monitor_integration.py"

# Read app.py
print("Reading app.py...")
with open(app_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if L2 integration already imported
if "from l2_monitor_integration import" in content:
    print("✅ L2 monitor already integrated!")
else:
    # Find a good place to add the import (after other imports from dashboard modules)
    import_marker = "try:\n    from ui_utils import"
    if import_marker in content:
        # Add import before the try/except block
        new_import = f"from l2_monitor_integration import show_l2_privacy_security_monitor\n\n{import_marker}"
        content = content.replace(import_marker, new_import)
        print("✅ Added L2 monitor import")
    else:
        # Find where other imports from dashboard are
        print("⚠️ Could not find standard import location, adding at end of imports section...")

# Check if L2 monitor is added to page selection
if "L2 Privacy/Security Monitor" not in content and "show_l2_privacy_security_monitor" in content:
    print("✅ L2 monitor page selector needs to be added to navigation")
    # This will need to be done manually or with more context
    print("   📝 Note: Add '\"L2 Privacy/Security Monitor\": show_l2_privacy_security_monitor' to page selector")

# Write updated app.py
print("Writing updated app.py...")
with open(app_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Integration complete!")
print("📝 Next steps:")
print("   1. Restart the Streamlit app")
print("   2. Look for 'L2 Privacy/Security Monitor' in the sidebar/page selector")
print("   3. The L2 monitor content will appear after login")
print("\n💾 Backup file: dashboard/l2_privacy_security_monitor.py.backup")
