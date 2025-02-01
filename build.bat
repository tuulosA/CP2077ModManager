@echo off
cd /d "%~dp0"
echo Building CP2077 Mod Manager Executable...

:: Activate virtual environment
if not exist ".venv" (
    echo Virtual environment not found! Creating one...
    py -3.12 -m venv .venv
)

echo Activating Virtual Environment...
call .venv\Scripts\activate

:: Ensure PyInstaller is installed
pip show pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Run PyInstaller to create the executable
echo Packaging CP2077ModManager.exe...
pyinstaller --onefile --noconsole --name CP2077ModManager --add-data "json;json" --add-data "nexus_api_key.txt;." src/main.py

:: Move the built EXE to the project root (optional)
if exist "dist\CP2077ModManager.exe" (
    move "dist\CP2077ModManager.exe" "."
    echo Build complete! Executable created: CP2077ModManager.exe
) else (
    echo Build failed! Check for errors above.
)

echo Press any key to exit...
pause
