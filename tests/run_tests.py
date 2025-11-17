"""
Test Runner and Configuration
Orchestrates running all test suites with comprehensive reporting
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Manages test execution and reporting"""
    
    def __init__(self, test_dir="tests"):
        self.test_dir = Path(test_dir)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "categories": {}
        }
    
    def run_unit_tests(self, verbose=True):
        """Run unit tests"""
        print("\n" + "="*70)
        print("UNIT TESTS")
        print("="*70)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_regulatory_monitor.py"),
            str(self.test_dir / "test_nlp_change_detector.py"),
            "-v" if verbose else "",
            "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.results["categories"]["unit"] = result.returncode == 0
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_integration_tests(self, verbose=True):
        """Run integration tests"""
        print("\n" + "="*70)
        print("INTEGRATION TESTS")
        print("="*70)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_integration*.py"),
            "-v" if verbose else "",
            "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.results["categories"]["integration"] = result.returncode == 0
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_e2e_tests(self, verbose=True):
        """Run end-to-end tests"""
        print("\n" + "="*70)
        print("END-TO-END TESTS")
        print("="*70)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_e2e*.py"),
            "-v" if verbose else "",
            "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.results["categories"]["e2e"] = result.returncode == 0
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_performance_tests(self, verbose=True):
        """Run performance tests"""
        print("\n" + "="*70)
        print("PERFORMANCE TESTS")
        print("="*70)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_performance*.py"),
            "-v" if verbose else "",
            "-s",  # Show print statements
            "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.results["categories"]["performance"] = result.returncode == 0
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_coverage(self):
        """Run tests with coverage reporting"""
        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--cov=scripts",
            "--cov-report=term-missing",
            "--cov-report=html"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_all_tests(self, coverage=False):
        """Run all test suites"""
        print("\n" + "="*70)
        print("REGULATORY MONITORING - COMPREHENSIVE TEST SUITE")
        print("="*70 + "\n")
        
        all_passed = True
        
        # Run all test categories
        all_passed &= self.run_unit_tests()
        all_passed &= self.run_integration_tests()
        all_passed &= self.run_e2e_tests()
        all_passed &= self.run_performance_tests()
        
        if coverage:
            self.run_coverage()
        
        # Print summary
        self.print_summary(all_passed)
        
        return all_passed
    
    def print_summary(self, all_passed):
        """Print test execution summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        print("\nResults by Category:")
        for category, passed in self.results["categories"].items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"  {category:20s} {status}")
        
        overall = all(self.results["categories"].values())
        print(f"\nOverall Status: {'✓ ALL TESTS PASSED' if overall else '✗ SOME TESTS FAILED'}")
        print(f"Timestamp: {self.results['timestamp']}")
        print("="*70 + "\n")


def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Regulatory Monitoring Tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Determine what to run
    if not any([args.unit, args.integration, args.e2e, args.performance, args.coverage]):
        # Default: run all
        return runner.run_all_tests(coverage=False)
    
    all_passed = True
    
    if args.unit:
        all_passed &= runner.run_unit_tests()
    
    if args.integration:
        all_passed &= runner.run_integration_tests()
    
    if args.e2e:
        all_passed &= runner.run_e2e_tests()
    
    if args.performance:
        all_passed &= runner.run_performance_tests()
    
    if args.coverage:
        all_passed &= runner.run_coverage()
    
    runner.print_summary(all_passed)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
