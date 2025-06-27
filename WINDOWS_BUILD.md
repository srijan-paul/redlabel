# Building RedLabel for Windows

This guide explains how to create a standalone Windows executable that users can double-click to run without installing Python or any dependencies.

## Quick Start (Windows Users)

1. **Double-click `build_windows.bat`** - This will automatically:
   - Install PyInstaller if needed
   - Install required dependencies
   - Build the standalone executable
   - Create a distribution folder

2. **Find your executable** in the `RedLabel-1.8.6-Windows` folder

3. **Distribute the entire folder** - Users can then double-click `RedLabel.exe` to run

## Alternative Methods

### Method 1: Python Script
```bash
# Run the build script directly
python build_windows_exe.py
```

### Method 2: PyInstaller Directly
```bash
# Install PyInstaller
pip install pyinstaller

# Build using the spec file
pyinstaller redlabel.spec
```

### Method 3: Manual PyInstaller
```bash
pyinstaller --onefile --windowed --name=RedLabel \
    --add-data="data;data" --add-data="resources;resources" \
    redlabel.py
```

## Requirements for Building

- Python 3.8+
- PyQt5 5.14.0+
- lxml 4.6.0+
- PyInstaller (auto-installed by build scripts)

## Output

The build process creates:
- `RedLabel.exe` - Standalone executable (no Python required)
- `RedLabel-X.X.X-Windows/` - Distribution folder with executable and docs

## Distribution

Users only need the `.exe` file, but it's recommended to distribute the entire folder which includes:
- `RedLabel.exe` - The main application
- `README.md` - Documentation
- `LICENSE` - License information

## Troubleshooting

**Build fails with "PyQt5 not found":**
```bash
pip install PyQt5>=5.14.0
```

**Missing icon error:**
- Create `resources/icons/app.ico` or remove icon reference from spec file

**Console window appears:**
- Change `console=False` to `console=True` in `redlabel.spec` for debugging
- Change back to `False` for release builds

**Large executable size:**
- The standalone executable includes Python runtime and all dependencies (~100MB+)
- This is normal for PyInstaller builds
- Alternative: Use `--onedir` instead of `--onefile` for faster startup
