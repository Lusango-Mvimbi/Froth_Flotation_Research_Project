#!/usr/bin/env python3
"""
Test Runner Script for Froth Flotation System
Runs all tests and provides a summary
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def run_comprehensive_tests():
    """Run the comprehensive test suite"""
    print("🧪 Running Comprehensive System Tests...")
    
    try:
        from tests.test_system_comprehensive import ComprehensiveSystemTest
        
        test_suite = ComprehensiveSystemTest()
        success = test_suite.run_all_tests()
        
        return success
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False

def run_system_functionality_tests():
    """Run the system functionality tests"""
    print("🧪 Running System Functionality Tests...")
    
    try:
        from tests.test_system_functionality import test_system_functionality
        
        success = test_system_functionality()
        return success
    except Exception as e:
        print(f"❌ Error running system functionality tests: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 FROTH FLOTATION SYSTEM TEST RUNNER")
    print("=" * 50)
    
    # Run comprehensive tests
    comprehensive_success = run_comprehensive_tests()
    
    print("\n" + "=" * 50)
    
    # Run system functionality tests
    functionality_success = run_system_functionality_tests()
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 50)
    
    if comprehensive_success and functionality_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is ready for production deployment")
        return 0
    else:
        print("⚠️  Some tests failed")
        if not comprehensive_success:
            print("❌ Comprehensive tests failed")
        if not functionality_success:
            print("❌ System functionality tests failed")
        return 1

if __name__ == "__main__":
    exit(main())


