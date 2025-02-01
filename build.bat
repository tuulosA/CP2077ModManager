@echo off
cd /d "%~dp0"
echo Building AllusModManager Executable...

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
echo Packaging AllusModManager.exe...
pyinstaller --onefile --noconsole --name AllusModManager --add-data "json;json" --add-data "nexus_api_key.txt;." src/main.py

:: Move the built EXE to the project root (optional)
if exist "dist\AllusModManager.exe" (
    move "dist\AllusModManager.exe" "."
    echo Build complete! Executable created: AllusModManager.exe
) else (
    echo Build failed! Check for errors above.
)

echo Press any key to exit...
pause
