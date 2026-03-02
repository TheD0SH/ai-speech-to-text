@echo off
echo Building VoiceType v2.0.0...
echo.

:: Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Build the full version
echo Building VoiceType.exe (Full Version)...
pyinstaller --clean VoiceType.spec

:: Build the lite version
echo Building VoiceTypeLite.exe (Lite Version)...
pyinstaller --clean VoiceTypeLite.spec

echo.
echo Build complete!
echo.
echo Output files:
echo   dist\VoiceType.exe
echo   dist\VoiceTypeLite.exe
echo.
pause
