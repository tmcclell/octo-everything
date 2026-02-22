"""
Validation script to verify test suite completeness.

Run this to check that all test files are properly structured.
"""

import os
import ast
from pathlib import Path


def count_test_functions(filepath):
    """Count test functions in a Python file."""
    with open(filepath, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    test_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            test_count += 1
    
    return test_count


def validate_test_suite():
    """Validate test suite structure and completeness."""
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob('test_*.py'))
    
    print("=" * 60)
    print("DevMetrics Test Suite Validation")
    print("=" * 60)
    
    total_tests = 0
    
    for test_file in sorted(test_files):
        test_count = count_test_functions(test_file)
        total_tests += test_count
        status = "✓" if test_count > 0 else "✗"
        print(f"{status} {test_file.name:30s} {test_count:3d} tests")
    
    print("=" * 60)
    print(f"Total: {len(test_files)} test files, {total_tests} test functions")
    print("=" * 60)
    
    # Check for required files
    required_files = [
        'test_github_client.py',
        'test_space_collector.py',
        'test_copilot_collector.py',
        'test_dummy_data_generator.py',
        'test_json_store.py'
    ]
    
    print("\nRequired Test Files:")
    missing = []
    for req_file in required_files:
        exists = (test_dir / req_file).exists()
        status = "✓" if exists else "✗ MISSING"
        print(f"{status} {req_file}")
        if not exists:
            missing.append(req_file)
    
    # Check for test configuration
    print("\nConfiguration Files:")
    config_files = [
        ('pytest.ini', test_dir.parent.parent / 'pytest.ini'),
        ('requirements-test.txt', test_dir.parent.parent / 'requirements-test.txt'),
        ('README.md', test_dir / 'README.md')
    ]
    
    for name, path in config_files:
        exists = path.exists()
        status = "✓" if exists else "✗ MISSING"
        print(f"{status} {name}")
    
    print("\n" + "=" * 60)
    
    if missing:
        print(f"⚠ WARNING: {len(missing)} required test files missing")
        return False
    elif total_tests < 50:
        print(f"⚠ WARNING: Only {total_tests} tests (expected 50+)")
        return False
    else:
        print("✓ Test suite validation PASSED")
        return True


if __name__ == '__main__':
    success = validate_test_suite()
    exit(0 if success else 1)
