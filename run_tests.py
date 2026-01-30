#!/usr/bin/env python3
"""
Quick test runner script.
"""
import sys
import subprocess

def run_tests():
    """Run pytest with common options."""
    print("=" * 60)
    print("Running PDF-Insight Test Suite")
    print("=" * 60)
    print()
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    result = subprocess.run(cmd)
    
    print()
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. See output above.")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
