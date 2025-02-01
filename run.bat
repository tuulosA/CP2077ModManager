@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Virtual environment not found! Creating one...
    py -3.12 -m venv .venv
)

echo Activating Virtual Environment...
call .venv\Scripts\activate

if not exist ".venv\Scripts\pip.exe" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Running Mod Manager...
set PYTHONPATH=%CD%
python src\main.py

echo Program exited. Press any key to close.
pause
