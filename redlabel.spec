# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Get the directory of this spec file
spec_root = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Collect all submodules from libs
libs_imports = collect_submodules('libs')

a = Analysis(
    ['redlabel.py'],
    pathex=[spec_root],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('resources', 'resources'),
        ('libs', 'libs'),
    ],
    hiddenimports=libs_imports + [
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        'lxml.etree',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtOpenGL',
        'libs.canvas',
        'libs.colorDialog',
        'libs.labelDialog',
        'libs.toolBar',
        'libs.pascal_voc_io',
        'libs.yolo_io',
        'libs.create_ml_io',
        'libs.settings',
        'libs.utils',
        'libs.constants',
        'libs.ustr',
        'libs.stringBundle',
        'libs.hashableQListWidgetItem',
        'libs.combobox',
        'libs.resources',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RedLabel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico' if os.path.exists('resources/icons/app.ico') else None,
)
