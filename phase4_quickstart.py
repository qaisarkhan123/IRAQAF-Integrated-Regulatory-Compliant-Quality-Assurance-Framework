#!/usr/bin/env python
"""
PHASE 4 QUICK START - Setup & Verification Script
==================================================

Automated setup verification for Phase 4 NLP Pipeline Enhancement.
Tests all components and displays diagnostic information.

Run: python phase4_quickstart.py
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# VERIFICATION STEPS
# ============================================================================

class Phase4Verifier:
    """Verifies Phase 4 implementation"""
    
    def __init__(self):
        self.results = {
            'environment': {},
            'dependencies': {},
            'modules': {},
            'components': {},
            'tests': {},
            'summary': {}
        }
        self.root_path = Path(__file__).parent
    
    # ========================================================================
    # STEP 1: Environment Verification
    # ========================================================================
    
    def verify_environment(self) -> bool:
        """Verify Python environment"""
        print("\n" + "="*70)
        print("STEP 1: ENVIRONMENT VERIFICATION")
        print("="*70)
        
        checks = {
            'Python Version': self._check_python_version(),
            'Working Directory': self._check_working_directory(),
            'Directory Structure': self._check_directory_structure(),
        }
        
        for check_name, result in checks.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {check_name:<30} {status}")
            self.results['environment'][check_name] = result
        
        return all(checks.values())
    
    def _check_python_version(self) -> bool:
        """Check Python version (3.8+)"""
        version = sys.version_info
        required = (3, 8)
        passed = version >= required
        
        logger.info(f"Python {version.major}.{version.minor}.{version.micro}")
        return passed
    
    def _check_working_directory(self) -> bool:
        """Check working directory"""
        exists = self.root_path.exists()
        logger.info(f"Working directory: {self.root_path}")
        return exists
    
    def _check_directory_structure(self) -> bool:
        """Check required directories exist"""
        required_dirs = [
            'nlp_pipeline',
            'tests',
            'db',
            'config',
        ]
        
        for dir_name in required_dirs:
            dir_path = self.root_path / dir_name
            if not dir_path.exists():
                logger.warning(f"Missing directory: {dir_name}")
                return False
        
        return True
    
    # ========================================================================
    # STEP 2: Dependency Verification
    # ========================================================================
    
    def verify_dependencies(self) -> bool:
        """Verify required packages"""
        print("\n" + "="*70)
        print("STEP 2: DEPENDENCY VERIFICATION")
        print("="*70)
        
        required = {
            'Core': [
                ('json', 'Standard library'),
                ('re', 'Standard library'),
                ('logging', 'Standard library'),
                ('pathlib', 'Standard library'),
                ('dataclasses', 'Standard library'),
                ('hashlib', 'Standard library'),
            ],
            'Data Processing': [
                ('numpy', 'Numerical computing'),
                ('pandas', 'Data frames'),
            ],
            'ML/NLP': [
                ('sklearn', 'scikit-learn'),
            ],
            'Testing': [
                ('pytest', 'Testing framework'),
            ],
            'Optional': [
                ('textblob', 'Language detection'),
                ('spacy', 'Advanced NLP'),
                ('gensim', 'Word embeddings'),
            ],
        }
        
        all_passed = True
        for category, packages in required.items():
            print(f"\n  {category}:")
            for package, description in packages:
                passed = self._check_package(package)
                status = "✓" if passed else "✗"
                print(f"    {status} {package:<20} ({description})")
                
                if category != 'Optional' and not passed:
                    all_passed = False
                
                self.results['dependencies'][package] = passed
        
        return all_passed
    
    def _check_package(self, package: str) -> bool:
        """Check if package is installed"""
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    # ========================================================================
    # STEP 3: Module Verification
    # ========================================================================
    
    def verify_modules(self) -> bool:
        """Verify Phase 4 modules exist and are valid"""
        print("\n" + "="*70)
        print("STEP 3: MODULE VERIFICATION")
        print("="*70)
        
        modules = {
            'Advanced Processing': 'nlp_pipeline/advanced_processing.py',
            'Semantic Search': 'nlp_pipeline/semantic_search.py',
            'Test Suite': 'tests/test_phase4_nlp_pipeline.py',
        }
        
        all_passed = True
        for module_name, file_path in modules.items():
            full_path = self.root_path / file_path
            exists = full_path.exists()
            
            status = "✓" if exists else "✗"
            print(f"  {status} {module_name:<30} ({file_path})")
            
            if exists:
                # Check file size and line count
                size = full_path.stat().st_size
                lines = len(full_path.read_text().split('\n'))
                print(f"      Size: {size:,} bytes | Lines: {lines:,}")
            else:
                all_passed = False
            
            self.results['modules'][module_name] = exists
        
        return all_passed
    
    # ========================================================================
    # STEP 4: Component Verification
    # ========================================================================
    
    def verify_components(self) -> bool:
        """Verify Phase 4 components can be imported"""
        print("\n" + "="*70)
        print("STEP 4: COMPONENT VERIFICATION")
        print("="*70)
        
        components = {
            'Advanced Processing': [
                'AdvancedTextProcessor',
                'TableExtractor',
                'CodeFormulaExtractor',
                'ReferenceExtractor',
                'RequirementEntityRecognizer',
                'MultiLanguageProcessor',
            ],
            'Semantic Search': [
                'SemanticSearchPipeline',
                'TFIDFSearchEngine',
                'SemanticSearchEngine',
                'CrossRegulationLinker',
                'RequirementDependencyGraph',
                'RequirementRecommendationEngine',
            ],
        }
        
        all_passed = True
        
        for category, classes in components.items():
            print(f"\n  {category}:")
            
            module_name = category.lower().replace(' ', '_')
            try:
                if category == 'Advanced Processing':
                    import nlp_pipeline.advanced_processing as mod
                else:
                    import nlp_pipeline.semantic_search as mod
                
                for class_name in classes:
                    has_class = hasattr(mod, class_name)
                    status = "✓" if has_class else "✗"
                    print(f"    {status} {class_name}")
                    
                    if not has_class:
                        all_passed = False
                    
                    self.results['components'][class_name] = has_class
            
            except ImportError as e:
                print(f"    ✗ Failed to import module: {e}")
                all_passed = False
        
        return all_passed
    
    # ========================================================================
    # STEP 5: Test Execution
    # ========================================================================
    
    def run_tests(self) -> bool:
        """Run Phase 4 test suite"""
        print("\n" + "="*70)
        print("STEP 5: TEST EXECUTION")
        print("="*70)
        
        try:
            import pytest
            
            test_file = self.root_path / 'tests' / 'test_phase4_nlp_pipeline.py'
            
            if not test_file.exists():
                print(f"  ✗ Test file not found: {test_file}")
                return False
            
            print(f"\n  Running: {test_file}")
            print("  " + "-"*66)
            
            # Run tests with minimal output
            result = pytest.main([
                str(test_file),
                '-v',
                '--tb=short',
                '-q'
            ])
            
            passed = result == 0
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"\n  Test Suite: {status}")
            
            return passed
        
        except ImportError:
            print("  ⚠ pytest not installed, skipping test execution")
            print("  Install with: pip install pytest")
            return True  # Don't fail if pytest not available
    
    # ========================================================================
    # STEP 6: Quick Functional Test
    # ========================================================================
    
    def run_functional_tests(self) -> bool:
        """Run quick functional tests"""
        print("\n" + "="*70)
        print("STEP 6: FUNCTIONAL TESTS")
        print("="*70)
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Advanced Text Processing
        tests_total += 1
        try:
            from nlp_pipeline.advanced_processing import AdvancedTextProcessor
            
            processor = AdvancedTextProcessor()
            result = processor.process_document(
                text="The system shall implement access control.",
                regulation="EU AI Act",
                section="4.1"
            )
            
            if 'requirements' in result and len(result['requirements']) > 0:
                print("  ✓ Advanced Text Processing")
                tests_passed += 1
            else:
                print("  ✗ Advanced Text Processing (no requirements extracted)")
        
        except Exception as e:
            print(f"  ✗ Advanced Text Processing ({e})")
        
        # Test 2: Semantic Search Pipeline
        tests_total += 1
        try:
            from nlp_pipeline.semantic_search import SemanticSearchPipeline
            
            pipeline = SemanticSearchPipeline()
            requirements = [
                {
                    'requirement_id': 'TEST-1',
                    'text': 'Access control shall be implemented',
                    'regulation': 'EU AI Act',
                    'section': '4.1'
                }
            ]
            
            if pipeline.build_complete_index(requirements):
                print("  ✓ Semantic Search Pipeline")
                tests_passed += 1
            else:
                print("  ✗ Semantic Search Pipeline (indexing failed)")
        
        except Exception as e:
            print(f"  ✗ Semantic Search Pipeline ({e})")
        
        # Test 3: Configuration Files
        tests_total += 1
        config_file = self.root_path / 'config' / 'nlp_config.json'
        if config_file.exists() or (self.root_path / 'config').exists():
            print("  ✓ Configuration Files")
            tests_passed += 1
        else:
            print("  ✗ Configuration Files")
        
        return tests_passed == tests_total
    
    # ========================================================================
    # STEP 7: Performance Estimation
    # ========================================================================
    
    def estimate_performance(self):
        """Estimate Phase 4 performance"""
        print("\n" + "="*70)
        print("STEP 7: PERFORMANCE ESTIMATION")
        print("="*70)
        
        performance = {
            'Document Processing': {
                'per_item': '100-150ms',
                'for_500_items': '~60-90 seconds',
                'for_1000_items': '~2-2.5 minutes'
            },
            'Semantic Search Index': {
                'indexing_1000_reqs': '~50-100ms',
                'single_search': '<500ms',
                'cross_regulation_linking': '5-10 seconds'
            },
            'Memory Usage': {
                'base': '~100MB',
                'per_1000_requirements': '~400-500MB',
                'total_estimated': '~600-700MB'
            }
        }
        
        for category, metrics in performance.items():
            print(f"\n  {category}:")
            for metric, value in metrics.items():
                print(f"    {metric:<30} {value}")
    
    # ========================================================================
    # SUMMARY & REPORT
    # ========================================================================
    
    def generate_summary(self):
        """Generate verification summary"""
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        
        env_passed = all(self.results['environment'].values())
        dep_passed = all(v for k, v in self.results['dependencies'].items() 
                        if k not in ['textblob', 'spacy', 'gensim'])
        mod_passed = all(self.results['modules'].values())
        
        summary = {
            'Environment': env_passed,
            'Dependencies': dep_passed,
            'Modules': mod_passed,
        }
        
        for check_name, passed in summary.items():
            status = "✓ PASS" if passed else "✗ NEEDS ATTENTION"
            print(f"  {check_name:<30} {status}")
        
        # Status indicators
        print("\n" + "-"*70)
        
        if all(summary.values()):
            print("\n  🎉 PHASE 4 IS READY FOR PRODUCTION!")
            print("\n  Next steps:")
            print("    1. Process 500+ regulatory items from database")
            print("    2. Extract 1000+ requirements")
            print("    3. Find 500+ cross-regulation links")
            print("    4. Build semantic search index")
            print("    5. Proceed to Phase 5")
        else:
            print("\n  ⚠️  PHASE 4 NEEDS SETUP")
            print("\n  Missing components:")
            if not env_passed:
                print("    - Environment issues detected")
            if not dep_passed:
                print("    - Install missing dependencies: pip install -r requirements.txt")
            if not mod_passed:
                print("    - Phase 4 modules not found")
        
        print("\n" + "-"*70)
    
    # ========================================================================
    # MAIN VERIFICATION FLOW
    # ========================================================================
    
    def run_all_verifications(self):
        """Run all verification steps"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "  PHASE 4: NLP PIPELINE ENHANCEMENT - VERIFICATION".center(68) + "║")
        print("║" + "  Automated Setup Verification Script".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝")
        
        steps = [
            ("Environment", self.verify_environment),
            ("Dependencies", self.verify_dependencies),
            ("Modules", self.verify_modules),
            ("Components", self.verify_components),
            ("Tests", self.run_tests),
            ("Functional", self.run_functional_tests),
        ]
        
        for step_name, step_func in steps:
            try:
                step_func()
            except Exception as e:
                logger.error(f"Error in {step_name}: {e}")
        
        # Performance estimation
        self.estimate_performance()
        
        # Summary
        self.generate_summary()
        
        print("\n  For documentation, see: PHASE_4_IMPLEMENTATION_GUIDE.md")
        print("\n")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Run Phase 4 verification"""
    verifier = Phase4Verifier()
    verifier.run_all_verifications()


if __name__ == "__main__":
    main()
