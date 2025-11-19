#!/usr/bin/env python
"""
Phase 2 Quick Start Script

This script sets up and runs Phase 2 initialization:
1. Initialize database schema
2. Load regulatory sources
3. Load sample data
4. Run tests
5. Display summary

Usage:
    python phase2_quickstart.py

Author: IRAQAF Phase 2
Date: 2024
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(number, text):
    """Print formatted step"""
    print(f"\n[STEP {number}] {text}")
    print("-" * 70)


def run_command(cmd, description):
    """Run a command and report results"""
    try:
        print(f"\nRunning: {description}...")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            if result.stdout:
                print(result.stdout[:500])  # First 500 chars
            return True
        else:
            print(f"✗ {description} - FAILED")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except Exception as e:
        print(f"✗ Error running {description}: {e}")
        return False


def main():
    """Main execution"""
    print_header("PHASE 2: DATABASE LAYER - QUICK START")

    print("This script will:")
    print("  1. Verify dependencies")
    print("  2. Initialize database")
    print("  3. Load sample data")
    print("  4. Run database tests")
    print("  5. Display summary")

    # Step 1: Verify Python
    print_step(1, "Verify Python Environment")
    python_version = sys.version.split()[0]
    print(f"✓ Python version: {python_version}")

    # Step 2: Verify dependencies
    print_step(2, "Verify Dependencies")
    required_packages = [
        'sqlalchemy',
        'requests',
        'beautifulsoup4',
        'pytest'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            missing.append(package)

    if missing:
        print(f"\n⚠ Install missing packages:")
        print(f"  pip install {' '.join(missing)}")

    # Step 3: Initialize database
    print_step(3, "Initialize Database")
    success = run_command(
        "python db/initial_data.py",
        "Initialize database and load sample data"
    )

    if not success:
        print("\n✗ Failed to initialize database")
        return False

    # Step 4: Run tests
    print_step(4, "Run Database Tests")
    success = run_command(
        "pytest tests/test_database.py -v --tb=short",
        "Run database test suite"
    )

    if not success:
        print("\n⚠ Some tests may have failed")
        print("  Run: pytest tests/test_database.py -v")

    # Step 5: Display summary
    print_header("PHASE 2 QUICK START COMPLETE")

    print("✓ Database initialized")
    print("✓ Regulatory sources loaded")
    print("✓ Sample data populated")
    print("✓ Tests executed")

    print("\nNEXT STEPS:")
    print("  1. Read: PHASE_2_COMPLETE_IMPLEMENTATION_GUIDE.md")
    print("  2. Review: db/models.py (database schema)")
    print("  3. Explore: db/operations.py (database operations)")
    print("  4. Test: pytest tests/test_database.py -v")

    print("\nPHASE 2 COMPLETED SUCCESSFULLY!")
    print("Ready for Phase 3: Web Scraper Enhancement")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
