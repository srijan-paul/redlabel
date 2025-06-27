@echo off
REM Build script for creating standalone Windows executable
REM This batch file can be double-clicked on Windows

echo Building RedLabel Windows Executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install PyInstaller if not available
echo Checking for PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install dependencies if needed
echo Installing dependencies...
python -m pip install PyQt5>=5.14.0 lxml>=4.6.0

REM Build the executable
echo.
echo Building executable with PyInstaller...
pyinstaller redlabel.spec

if errorlevel 1 (
    echo.
    echo Error: Build failed!
    pause
    exit /b 1
)

REM Create distribution folder
set VERSION=1.8.6
set DIST_FOLDER=RedLabel-%VERSION%-Windows

echo.
echo Creating distribution folder: %DIST_FOLDER%

if exist "%DIST_FOLDER%" rmdir /s /q "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%"

REM Copy files
copy "dist\RedLabel.exe" "%DIST_FOLDER%\"
if exist "README.md" copy "README.md" "%DIST_FOLDER%\"
if exist "LICENSE" copy "LICENSE" "%DIST_FOLDER%\"

echo.
echo ================================
echo Build completed successfully!
echo ================================
echo.
echo Executable location: %DIST_FOLDER%\RedLabel.exe
echo.
echo You can now distribute the '%DIST_FOLDER%' folder.
echo Users can double-click RedLabel.exe to run the application.
echo.
pause
