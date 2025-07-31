#!/usr/bin/env python3
"""
Package validation script for ProstScratch ROS2 implementation
This script validates the package structure without requiring ROS2 to be installed
"""

import sys
import os
import ast


def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (missing)")
        return False


def check_python_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {filepath}: {e}")
        return False


def main():
    print("=== ProstScratch ROS2 Package Validation ===\n")
    
    # Check essential files
    essential_files = [
        ("setup.py", "ROS2 Python package setup"),
        ("package.xml", "ROS2 package manifest"),
        ("resource/prost_scratch", "ROS2 resource marker"),
        ("prost_scratch/__init__.py", "Python package init"),
    ]
    
    all_files_exist = True
    for filepath, description in essential_files:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    print()
    
    # Check Python modules
    python_modules = [
        "prost_scratch/prost_scratch_ros2_connector.py",
        "prost_scratch/prost_scratch_ros2_controller.py", 
        "prost_scratch/test_prost_scratch_ros2.py"
    ]
    
    print("=== Python Module Syntax Check ===")
    syntax_ok = True
    for module in python_modules:
        if os.path.exists(module):
            if check_python_syntax(module):
                print(f"✓ {module} syntax valid")
            else:
                syntax_ok = False
        else:
            print(f"✗ {module} not found")
            syntax_ok = False
    
    print()
    
    # Check launch files
    launch_files = [
        "launch/prost_scratch_ros2.launch.py",
        "launch/turtlebot2_minimal_ros2.launch.py"
    ]
    
    print("=== Launch Files Check ===")
    launch_ok = True
    for launch_file in launch_files:
        if check_file_exists(launch_file, "Launch file"):
            if check_python_syntax(launch_file):
                print(f"✓ {launch_file} syntax valid")
            else:
                launch_ok = False
        else:
            launch_ok = False
    
    print()
    
    # Check documentation
    doc_files = [
        "README_ROS2.md",
        "MIGRATION_GUIDE.md"
    ]
    
    print("=== Documentation Check ===")
    doc_ok = True
    for doc_file in doc_files:
        if not check_file_exists(doc_file, "Documentation"):
            doc_ok = False
    
    print()
    
    # Final summary
    print("=== Validation Summary ===")
    if all_files_exist:
        print("✓ All essential files present")
    else:
        print("✗ Some essential files missing")
        
    if syntax_ok:
        print("✓ All Python modules have valid syntax")
    else:
        print("✗ Some Python modules have syntax errors")
        
    if launch_ok:
        print("✓ All launch files valid")
    else:
        print("✗ Some launch files have issues")
        
    if doc_ok:
        print("✓ Documentation files present")
    else:
        print("✗ Some documentation missing")
    
    overall_success = all_files_exist and syntax_ok and launch_ok and doc_ok
    
    if overall_success:
        print("\n🎉 Package validation PASSED - Ready for ROS2 deployment!")
        return 0
    else:
        print("\n❌ Package validation FAILED - Please fix issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())