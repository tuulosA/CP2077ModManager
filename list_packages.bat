@echo off
cd /d "%~dp0"

echo Activating Virtual Environment...
call .venv\Scripts\activate

echo Listing installed packages...
pip list

echo.
echo Press any key to exit...
pause
