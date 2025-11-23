"""
Run All Unit Tests
Comprehensive test suite for Cyber Mirage
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests(verbose=True):
    """
    Run all unit tests with coverage reporting
    
    Args:
        verbose: Whether to show detailed output
    """
    print("\n" + "="*70)
    print("🎯 CYBER MIRAGE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("="*70 + "\n")
    
    # Test arguments
    args = [
        'tests/',
        '-v' if verbose else '',
        '--tb=short',
        '--color=yes',
        '-p', 'no:warnings'
    ]
    
    # Remove empty strings
    args = [arg for arg in args if arg]
    
    # Run tests
    result = pytest.main(args)
    
    # Summary
    print("\n" + "="*70)
    if result == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  SOME TESTS FAILED (exit code: {result})")
    print("="*70 + "\n")
    
    return result


def run_specific_tests(test_pattern):
    """
    Run specific tests matching a pattern
    
    Args:
        test_pattern: Pattern to match (e.g., 'test_neural*')
    """
    print(f"\n🎯 Running tests matching: {test_pattern}\n")
    
    args = [
        'tests/',
        '-k', test_pattern,
        '-v',
        '--tb=short'
    ]
    
    return pytest.main(args)


def run_test_file(file_path):
    """
    Run a specific test file
    
    Args:
        file_path: Path to test file
    """
    print(f"\n🎯 Running: {file_path}\n")
    
    args = [
        file_path,
        '-v',
        '--tb=short'
    ]
    
    return pytest.main(args)


def list_all_tests():
    """List all available tests"""
    print("\n" + "="*70)
    print("📋 AVAILABLE TESTS")
    print("="*70 + "\n")
    
    pytest.main(['tests/', '--collect-only', '-q'])
    
    print("\n" + "="*70)
    print("\n💡 Run tests with: python tests/run_all_tests.py")
    print("   Or: pytest tests/ -v\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Cyber Mirage Test Runner')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List all tests')
    parser.add_argument('-k', '--keyword', type=str,
                       help='Run tests matching keyword')
    parser.add_argument('-f', '--file', type=str,
                       help='Run specific test file')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (less verbose)')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_tests()
    elif args.keyword:
        run_specific_tests(args.keyword)
    elif args.file:
        run_test_file(args.file)
    else:
        run_all_tests(verbose=not args.quiet)
