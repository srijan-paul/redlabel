#!/usr/bin/env python3
"""
Build script to generate resources.py from resources.qrc
This ensures the resources are available before package installation
"""
import os
import subprocess
import sys
import shutil


def find_pyrcc5():
    """Find pyrcc5 executable."""
    # Try common locations
    candidates = [
        ['pyrcc5'],
        ['uv', 'run', 'pyrcc5'],
        ['python', '-m', 'PyQt5.pyrcc_main'],
    ]
    
    for cmd in candidates:
        try:
            # pyrcc5 doesn't support --help, so try -help instead
            result = subprocess.run(cmd + ['-help'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 or 'pyrcc5' in result.stderr:
                return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None


def build_resources():
    """Generate libs/resources.py from resources.qrc."""
    if not os.path.exists('resources.qrc'):
        print("Error: resources.qrc not found")
        return False
    
    # Find pyrcc5
    pyrcc5_cmd = find_pyrcc5()
    if not pyrcc5_cmd:
        print("Error: pyrcc5 not found. Please install PyQt5 development tools.")
        return False
    
    # Create libs directory if it doesn't exist
    os.makedirs('libs', exist_ok=True)
    
    # Generate resources.py
    cmd = pyrcc5_cmd + ['-o', 'libs/resources.py', 'resources.qrc']
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Successfully generated libs/resources.py")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating resources: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


if __name__ == '__main__':
    success = build_resources()
    sys.exit(0 if success else 1)
