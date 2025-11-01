@echo off
echo ================================
echo Sales Analytics Chat Assistant
echo ================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create a .env file based on .env.example:
    echo   1. Copy .env.example to .env
    echo   2. Add your database credentials
    echo   3. Add your OpenAI or Anthropic API key
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Python dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [2/3] Installing Python dependencies...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [3/3] Starting backend server...
echo.
echo ================================
echo Backend API running at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo ================================
echo.
echo Press Ctrl+C to stop the server
echo.

python src/main.py

pause
