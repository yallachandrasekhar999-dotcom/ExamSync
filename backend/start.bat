@echo off
echo Starting Exam Sync Backend Server...
echo.

if not exist venv (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python run.py
