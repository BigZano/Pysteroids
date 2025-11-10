# PowerShell script to setup and run Pysteroids from source
# This script creates a virtual environment, installs dependencies, and runs the game

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Pysteroids - Setup and Run" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or later from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "env")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error creating virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "env\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install/upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not upgrade pip" -ForegroundColor Yellow
}
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install requirements
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error installing dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Run the game
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting Pysteroids..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
python main.py

# Deactivate on exit
deactivate

Write-Host ""
Write-Host "Game closed. Press Enter to exit..." -ForegroundColor Yellow
Read-Host
