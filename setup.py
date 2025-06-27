#!/usr/bin/env python3
"""
Setup script for RedLabel with automatic resource generation
"""
import os
import sys
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess


class BuildResourcesCommand:
    """Mixin class to add resource building to setup commands."""
    
    def build_resources(self):
        """Generate libs/resources.py from resources.qrc."""
        if not os.path.exists('resources.qrc'):
            print("Warning: resources.qrc not found, skipping resource generation")
            return
        
        # Try to find pyrcc5
        for cmd in ['pyrcc5', 'python -m PyQt5.pyrcc_main']:
            try:
                subprocess.run([cmd, '--help'], capture_output=True, check=True)
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        else:
            print("Warning: pyrcc5 not found, resources.py may not be updated")
            return
        
        # Create libs directory
        os.makedirs('libs', exist_ok=True)
        
        # Generate resources.py
        try:
            if cmd == 'pyrcc5':
                subprocess.run([cmd, '-o', 'libs/resources.py', 'resources.qrc'], check=True)
            else:
                subprocess.run([cmd, 'resources.qrc', '-o', 'libs/resources.py'], check=True)
            print("Successfully generated libs/resources.py")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to generate resources.py: {e}")


class CustomBuildPy(build_py, BuildResourcesCommand):
    def run(self):
        self.build_resources()
        super().run()


class CustomDevelop(develop, BuildResourcesCommand):
    def run(self):
        self.build_resources()
        super().run()


class CustomInstall(install, BuildResourcesCommand):
    def run(self):
        self.build_resources()
        super().run()


if __name__ == '__main__':
    setup(
        cmdclass={
            'build_py': CustomBuildPy,
            'develop': CustomDevelop,
            'install': CustomInstall,
        }
    )
