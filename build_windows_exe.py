#!/usr/bin/env python3
"""
Build script to create standalone Windows executable using PyInstaller.
Run this on Windows or in a Windows environment.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    """Build standalone Windows executable using PyInstaller."""
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("redlabel.spec"):
        os.remove("redlabel.spec")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=RedLabel",              # Output name
        "--icon=resources/icons/app.ico",  # App icon (if exists)
        "--add-data=data;data",         # Include data folder
        "--add-data=resources;resources", # Include resources
        "--hidden-import=xml",
        "--hidden-import=xml.etree",
        "--hidden-import=xml.etree.ElementTree",
        "--hidden-import=lxml.etree",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui", 
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=libs.canvas",
        "--hidden-import=libs.colorDialog",
        "--hidden-import=libs.labelDialog",
        "--hidden-import=libs.toolBar",
        "--hidden-import=libs.pascal_voc_io",
        "--hidden-import=libs.yolo_io",
        "--hidden-import=libs.create_ml_io",
        "redlabel.py"
    ]
    
    print("Building Windows executable...")
    print("Command:", " ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ Build successful!")
        print(f"Executable created: {os.path.abspath('dist/RedLabel.exe')}")
        
        # Create distribution folder
        version = "1.8.6"  # From pyproject.toml
        dist_folder = f"RedLabel-{version}-Windows"
        
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        os.makedirs(dist_folder)
        
        # Copy executable
        shutil.copy2("dist/RedLabel.exe", dist_folder)
        
        # Copy additional files
        if os.path.exists("README.md"):
            shutil.copy2("README.md", dist_folder)
        if os.path.exists("LICENSE"):
            shutil.copy2("LICENSE", dist_folder)
            
        print(f"\n✓ Distribution folder created: {dist_folder}")
        print(f"You can now distribute the '{dist_folder}' folder.")
        print("Users can double-click RedLabel.exe to run the application.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if sys.platform != "win32":
        print("Warning: This script should be run on Windows for best results.")
        print("Cross-compilation may not work properly.")
    
    success = build_executable()
    if success:
        print("\n🎉 Windows executable build complete!")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)
