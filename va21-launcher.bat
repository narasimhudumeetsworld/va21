@echo off
cd /d "%~dp0"
echo 🔒 Starting VA21 Omni Agent - Digital Fortress...
echo Guardian AI security system: ACTIVE
echo Air gap protection: ENABLED
echo Access the interface at: http://localhost:5000
echo.

REM Check if we have a Python virtual environment
if exist "%~dp0python-env\Scripts\activate.bat" (
    echo Activating portable Python environment...
    call "%~dp0python-env\Scripts\activate.bat"
)

cd va21-omni-agent\backend
python va21_server.py
pause