@echo off
REM Batch script to setup and run Pysteroids from source
REM This script creates a virtual environment, installs dependencies, and runs the game

echo =========================================
echo Pysteroids - Setup and Run
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or later from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "env\" (
    echo Creating virtual environment...
    python -m venv env
    if errorlevel 1 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call env\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo pip upgraded
echo.

REM Install requirements
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Run the game
echo =========================================
echo Starting Pysteroids...
echo =========================================
echo.
python main.py

REM Deactivate on exit
call env\Scripts\deactivate.bat

echo.
pause
