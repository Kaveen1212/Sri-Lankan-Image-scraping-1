@echo off
echo Sri Lankan Image Downloader - High Quality Unlimited
echo ===================================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check for requirements.txt and install dependencies
if exist requirements.txt (
    echo Installing required packages...
    python -m pip install -r requirements.txt
) else (
    echo Warning: requirements.txt not found.
)

echo.
echo Installing required Python packages...
python -m pip install requests beautifulsoup4 pillow

echo.
echo Choose which version to run:
echo 1) Regular version (direct_image_downloader.py) - uses multiple sources
echo 2) Simplified version (simplified_downloader.py) - optimized for reliability
echo.
set /p choice="Enter your choice (1 or 2): "

echo.
echo Press any key to start downloading high-quality images or Ctrl+C to cancel...
pause >nul

echo.
echo Starting unlimited high-quality image downloader...
echo (Press Ctrl+C at any time to stop the script)
echo.

if "%choice%"=="2" (
    python simplified_downloader.py
) else (
    python direct_image_downloader.py
)

echo.
echo Script finished. Press any key to exit...
pause >nul
